# app/schemas/auth.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

class UserRoleEnum(str, Enum):
    STUDENT = "student"
    PARENT = "parent" 
    TEACHER = "teacher"
    ADMIN = "admin"

class LoginRequest(BaseModel):
    """Запрос первого этапа авторизации"""
    phone: str = Field(..., description="Номер телефона")
    password: str = Field(..., min_length=6, description="Основной пароль")

class RoleAccessRequest(BaseModel):
    """Запрос второго этапа - выбор роли"""
    phone: str = Field(..., description="Номер телефона")
    primary_password: str = Field(..., description="Основной пароль")
    selected_role: UserRoleEnum = Field(..., description="Выбранная роль")
    role_password: str = Field(..., min_length=4, description="Пароль роли")

class AvailableRolesResponse(BaseModel):
    """Ответ с доступными ролями"""
    user_id: int
    name: str
    surname: str
    available_roles: List[UserRoleEnum]
    message: str = "Выберите роль для входа"

class LoginResponse(BaseModel):
    """Ответ успешной авторизации"""
    access_token: str
    token_type: str = "bearer"
    user_data: Dict[str, Any]
    expires_in: int = 3600

class TokenData(BaseModel):
    """Данные из токена"""
    user_id: int
    phone: str
    name: str
    surname: str
    primary_role: str
    active_role: str
    role_id: int
    role_data: Dict[str, Any]

class CurrentUser(BaseModel):
    """Текущий пользователь"""
    user_id: int
    name: str
    surname: str
    phone: str
    primary_role: str
    active_role: str
    role_id: int
    role_data: Dict[str, Any]
    
    class Config:
        from_attributes = True