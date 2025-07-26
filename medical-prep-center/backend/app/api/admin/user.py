from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.schemas.auth.admin import *
from app.services.auth.user_service import *
from app.services.auth.student_service import *
from app.services.auth.teacher_service import *
from app.services.auth.admin_service import *

router = APIRouter()

@router.get("/", response_model=AdminUsersListResponse)
async def get_users(
    role: Optional[UserRoleEnum] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка пользователей с фильтрами"""
    try:
        # Используем существующие функции
        if role:
            users = await get_users_by_role_db(db, role)
        elif is_active is not None:
            if is_active:
                users = await get_active_users_db(db)
            else:
                users = await get_inactive_users_db(db)
        elif search:
            users = await search_users_db(db, search)
        else:
            users = await get_all_users_db(db)
        
        # Пагинация
        total = len(users)
        paginated_users = users[offset:offset + limit]
        
        # Получаем роль-специфичную информацию
        enriched_users = []
        for user in paginated_users:
            user_data = AdminUserResponse.from_orm(user)
            
            # Добавляем роль-специфичную информацию
            if user.role == UserRoleEnum.STUDENT.value and user.student:
                user_data.role_info = {
                    "direction": user.student.direction,
                    "group_id": user.student.group_id,
                    "goal": user.student.goal,
                    "status": user.student.student_status.value
                }
            elif user.role == UserRoleEnum.TEACHER and user.teacher:
                user_data.role_info = {
                    "schedule": user.teacher.teacher_schedule,
                    "status": user.teacher.teacher_status.value,
                    "subjects_count": len(user.teacher.subjects)
                }
            elif user.role == UserRoleEnum.ADMIN and user.admin:
                user_data.role_info = {
                    "schedule": user.admin.schedule,
                    "status": user.admin.admin_status.value
                }
            
            enriched_users.append(user_data)
        
        return AdminUsersListResponse(
            items=enriched_users,
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=AdminUserResponse)
async def create_user(
    user_data: CreateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового пользователя"""
    try:
        # Используем существующую функцию create_user_db
        new_user = await create_user_db(
            db=db,
            name=user_data.name,
            surname=user_data.surname,
            phone=user_data.phone,
            password=user_data.password,
            role=user_data.role,
            email=user_data.email,
            photo=user_data.photo,
            direction=user_data.direction,
            group_id=user_data.group_id,
            goal=user_data.goal,
            teacher_schedule=user_data.teacher_schedule,
            admin_schedule=user_data.admin_schedule
        )
        
        return AdminUserResponse.from_orm(new_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение пользователя по ID"""
    try:
        user = await get_user_by_id_db(db, user_id)
        return AdminUserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: int,
    user_data: UpdateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление пользователя"""
    try:
        updated_user = await update_user_db(
            db=db,
            user_id=user_id,
            name=user_data.name,
            surname=user_data.surname,
            phone=user_data.phone,
            email=user_data.email,
            password=user_data.password,
            photo=user_data.photo,
            is_active=user_data.is_active
        )
        
        return AdminUserResponse.from_orm(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление пользователя"""
    try:
        return await delete_user_db(db, user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-action")
async def bulk_user_action(
    action_data: BulkActionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Массовые действия с пользователями"""
    try:
        results = []
        for user_id in action_data.item_ids:
            if action_data.action == "activate":
                result = await activate_user_db(db, user_id)
                results.append(result)
            elif action_data.action == "deactivate":
                result = await deactivate_user_db(db, user_id)
                results.append(result)
            elif action_data.action == "delete":
                result = await delete_user_db(db, user_id)
                results.append(result)
        
        return {"message": f"Bulk action {action_data.action} completed", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))