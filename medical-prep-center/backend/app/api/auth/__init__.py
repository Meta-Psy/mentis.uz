from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth.user_service import *
from app.schemas.base import UserCreate, UserResponse, Token
from app.services.auth.auth_service import AuthService
from datetime import timedelta
import traceback
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    try:
        # Хешируем пароль
        hashed_password = AuthService.get_password_hash(user_data.password)
        
        # Создаем пользователя через сервис
        new_user = await create_user_db(
            db=db,
            name=user_data.name,
            surname=user_data.surname,
            phone=user_data.phone,
            password=hashed_password,
            role=user_data.role,
            email=user_data.email,
            photo=user_data.photo,
            # Дополнительные параметры в зависимости от роли
            direction=user_data.direction if user_data.role == "student" else None,
            group_id=user_data.group_id if user_data.role == "student" else None,
            goal=user_data.goal if user_data.role == "student" else None,
            teacher_schedule=user_data.teacher_schedule if user_data.role == "teacher" else None,
            admin_schedule=user_data.admin_schedule if user_data.role == "admin" else None
        )
        
        return UserResponse.from_orm(new_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger = logging.getLogger("main")
        logger.error("❌ Ошибка при регистрации пользователя:\n%s", traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании пользователя"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Авторизация пользователя"""
    try:
        # Ищем пользователя по телефону (username в форме)
        user = await get_user_by_phone_db(db, form_data.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный номер телефона",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Проверяем пароль
        if not AuthService.verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Обновляем время последнего входа
        await update_last_login_time_db(db, user.user_id)
        
        # Создаем токен
        access_token_expires = timedelta(days=30)
        access_token = AuthService.create_access_token(
            data={"sub": str(user.user_id), "role": user.role.value if hasattr(user.role, 'value') else str(user.role)},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            role=user.role.value if hasattr(user.role, 'value') else str(user.role)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger = logging.getLogger("main")
        logger.error("❌ Ошибка при авторизации:\n%s", traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при авторизации"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user = Depends(AuthService.get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Получение информации о текущем пользователе"""
    return UserResponse.from_orm(current_user)

@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    current_user = Depends(AuthService.get_current_user_dependency)
):
    """Обновление токена доступа"""
    access_token_expires = timedelta(days=30)
    access_token = AuthService.create_access_token(
        data={"sub": str(current_user.user_id), "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=current_user.user_id,
        role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    )

@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    current_user: User = Depends(AuthService.get_current_user_dependency)
):
    """Обновление токена доступа"""
    access_token_expires = timedelta(days=30)
    access_token = AuthService.create_access_token(
        data={"sub": str(current_user.user_id), "role": current_user.role.value},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=current_user.user_id,
        role=current_user.role
    )

@router.post("/logout")
async def logout():
    """Выход из системы"""
    # В случае с JWT токенами, выход происходит на клиенте
    # Можно добавить blacklist токенов если необходимо
    return {"message": "Успешный выход из системы"}