from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth.user_service import *
from app.schemas.auth import UserCreate, UserResponse, Token, UserLogin
from app.core.security import create_access_token, verify_password, get_password_hash
from datetime import timedelta

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    try:
        # Хешируем пароль
        hashed_password = get_password_hash(user_data.password)
        
        # Создаем пользователя через сервис
        new_user = create_user_db(
            name=user_data.name,
            surname=user_data.surname,
            phone=user_data.phone,
            password=hashed_password,
            role=user_data.role,
            email=user_data.email,
            photo=user_data.photo,
            # Дополнительные параметры в зависимости от роли
            direction=user_data.direction if user_data.role == UserRole.STUDENT else None,
            group_id=user_data.group_id if user_data.role == UserRole.STUDENT else None,
            goal=user_data.goal if user_data.role == UserRole.STUDENT else None,
            teacher_schedule=user_data.teacher_schedule if user_data.role == UserRole.TEACHER else None,
            admin_schedule=user_data.admin_schedule if user_data.role == UserRole.ADMIN else None
        )
        
        return UserResponse.from_orm(new_user)
    except HTTPException as e:
        raise e
    except Exception as e:
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
        user = get_user_by_phone_db(form_data.username)
        
        # Проверяем пароль
        if not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный номер телефона или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Обновляем время последнего входа
        update_last_login_time_db(user.user_id)
        
        # Создаем токен
        access_token_expires = timedelta(days=30)
        access_token = create_access_token(
            data={"sub": str(user.user_id), "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            role=user.role.value
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при авторизации"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Получение информации о текущем пользователе"""
    return UserResponse.from_orm(current_user)

@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    current_user: User = Depends(get_current_user_dependency)
):
    """Обновление токена доступа"""
    access_token_expires = timedelta(days=30)
    access_token = create_access_token(
        data={"sub": str(current_user.user_id), "role": current_user.role.value},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=current_user.user_id,
        role=current_user.role.value
    )

@router.post("/logout")
async def logout():
    """Выход из системы"""
    # В случае с JWT токенами, выход происходит на клиенте
    # Можно добавить blacklist токенов если необходимо
    return {"message": "Успешный выход из системы"}