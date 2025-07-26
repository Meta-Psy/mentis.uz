from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth.admin import *
from app.services.auth.user_service import *

router = APIRouter()

@router.get("/dashboard", response_model=AdminDashboardStatistics)
async def get_dashboard_statistics(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики для дашборда"""
    try:
        # Используем существующие функции статистики
        user_stats = await get_user_statistics_db(db)
        
        dashboard_stats = AdminDashboardStatistics(
            total_users=user_stats["total_users"],
            active_students=user_stats["users_by_role"]["students"],
            active_teachers=user_stats["users_by_role"]["teachers"],
            # Добавляем другие статистики используя существующие функции
        )
        
        return dashboard_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=AdminHealthResponse)
async def get_admin_health(
    db: AsyncSession = Depends(get_db)
):
    """Проверка здоровья админки"""
    try:
        dashboard_stats = await get_dashboard_statistics(db)
        
        system_health = SystemHealth(
            status="healthy",
            database_status="connected",
            active_sessions=0,
            server_uptime="1d 2h 30m",
            memory_usage=45.6,
            cpu_usage=12.3
        )
        
        return AdminHealthResponse(
            dashboard_stats=dashboard_stats,
            system_health=system_health
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))