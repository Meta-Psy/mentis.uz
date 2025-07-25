# app/services/auth/auth_service.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
import jwt
from app.database.models.user import User, Student, ParentInfo, UserRole
from app.config.database import settings
from app.database import get_db
from fastapi.security import OAuth2PasswordBearer
from app.database.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class AuthService:
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Создание JWT токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    async def authenticate_primary_user(db: AsyncSession, phone: str, password: str) -> Optional[User]:
        """Первичная аутентификация по основному паролю пользователя"""
        result = await db.execute(select(User).filter(User.phone == phone))
        user = result.scalar_one_or_none()
        
        if not user or not AuthService.verify_password(password, user.password):
            return None
        return user
    
    @staticmethod
    async def authenticate_role_access(
        db: AsyncSession, 
        user_id: int, 
        role: UserRole, 
        role_password: str
    ) -> Optional[Dict[str, Any]]:
        """Аутентификация доступа к роли"""
        
        if role == UserRole.STUDENT:
            result = await db.execute(
                select(Student).filter(Student.student_id == user_id)
            )
            student = result.scalar_one_or_none()
            if not student:
                return None
            
            # Проверяем пароль студента (можно хранить в отдельном поле)
            # Для примера используем хеш от user_id + "student"
            expected_hash = AuthService.get_password_hash(f"{user_id}student")
            if not AuthService.verify_password(role_password, expected_hash):
                return None
            
            return {
                "role_id": student.student_id,
                "role_data": {
                    "direction": student.direction,
                    "group_id": student.group_id,
                    "status": student.student_status.value
                }
            }
        
        elif role == UserRole.PARENT:
            result = await db.execute(
                select(ParentInfo).filter(ParentInfo.parent_id == user_id)
            )
            parent = result.scalar_one_or_none()
            if not parent:
                return None
            
            # Проверяем пароль родителя
            expected_hash = AuthService.get_password_hash(f"{user_id}parent")
            if not AuthService.verify_password(role_password, expected_hash):
                return None
            
            return {
                "role_id": parent.parent_id,
                "role_data": {
                    "profession": parent.profession,
                    "workplace": parent.workplace
                }
            }
        
        return None
    
    @staticmethod
    async def login_two_step(
        db: AsyncSession,
        phone: str,
        primary_password: str,
        selected_role: UserRole,
        role_password: str
    ) -> Dict[str, Any]:
        """Двухэтапная авторизация"""
        
        # Шаг 1: Проверяем основного пользователя
        user = await AuthService.authenticate_primary_user(db, phone, primary_password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль"
            )
        
        # Шаг 2: Проверяем доступ к роли
        role_data = await AuthService.authenticate_role_access(
            db, user.user_id, selected_role, role_password
        )
        if not role_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный пароль для выбранной роли"
            )
        
        # Создаем токен с полной информацией
        token_data = {
            "sub": str(user.user_id),
            "phone": user.phone,
            "name": user.name,
            "surname": user.surname,
            "primary_role": user.role.value,
            "active_role": selected_role.value,
            "role_id": role_data["role_id"],
            "role_data": role_data["role_data"]
        }
        
        access_token = AuthService.create_access_token(data=token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_data": {
                "user_id": user.user_id,
                "name": user.name,
                "surname": user.surname,
                "phone": user.phone,
                "primary_role": user.role.value,
                "active_role": selected_role.value,
                "role_id": role_data["role_id"],
                "role_data": role_data["role_data"]
            }
        }
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Декодирование JWT токена"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен"
            )
            
    @staticmethod
    def get_current_user_dependency(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """Получение текущего пользователя из JWT токена"""
        try:
            payload = AuthService.decode_token(token)
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный токен: отсутствует user_id"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невозможно декодировать токен"
            )

        user = db.query(User).filter(User.user_id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )

        return user