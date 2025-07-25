from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models.user import Admin, AdminInfo, AdminStatus, User, UserRole

# ===========================================
# ADMIN OPERATIONS (Updated - without create)
# ===========================================


async def get_admin_by_id_db(db: AsyncSession, admin_id: int) -> Admin:
    """Получение администратора по ID"""

    result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )
    return admin


async def update_admin_db(
    db: AsyncSession,
    admin_id: int,
    schedule: Optional[str] = None,
    admin_status: Optional[AdminStatus] = None,
) -> Admin:
    """Обновление данных администратора"""

    result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )

    if schedule is not None:
        admin.schedule = schedule
    if admin_status is not None:
        admin.admin_status = admin_status

    await db.commit()
    await db.refresh(admin)
    return admin


async def delete_admin_db(db: AsyncSession, admin_id: int) -> dict:
    """Удаление администратора"""

    result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )
    await db.delete(admin)
    await db.commit()
    return {"status": "Удален"}


# ===========================================
# ADMIN INFO OPERATIONS
# ===========================================


async def create_admin_info_db(
    db: AsyncSession,
    admin_id: int,
    admin_number: Optional[str] = None,
    employment: Optional[str] = None,
    admin_hobby: Optional[str] = None,
) -> AdminInfo:
    """Создание дополнительной информации об администраторе"""

    # Проверяем, что администратор существует
    admin_result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = admin_result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )

    # Проверяем, что информация еще не создана
    existing_info_result = await db.execute(
        select(AdminInfo).filter(AdminInfo.admin_id == admin_id)
    )
    existing_info = existing_info_result.scalar_one_or_none()
    if existing_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Информация об администраторе уже существует",
        )

    admin_info = AdminInfo(
        admin_id=admin_id,
        admin_number=admin_number,
        employment=employment,
        admin_hobby=admin_hobby,
    )
    db.add(admin_info)
    await db.commit()
    await db.refresh(admin_info)
    return admin_info


async def get_admin_info_db(db: AsyncSession, admin_id: int) -> AdminInfo:
    """Получение дополнительной информации об администраторе"""

    result = await db.execute(select(AdminInfo).filter(AdminInfo.admin_id == admin_id))
    admin_info = result.scalar_one_or_none()
    if not admin_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об администраторе не найдена",
        )
    return admin_info


async def update_admin_info_db(
    db: AsyncSession,
    admin_id: int,
    admin_number: Optional[str] = None,
    employment: Optional[str] = None,
    admin_hobby: Optional[str] = None,
) -> AdminInfo:
    """Обновление дополнительной информации об администраторе"""

    result = await db.execute(select(AdminInfo).filter(AdminInfo.admin_id == admin_id))
    admin_info = result.scalar_one_or_none()
    if not admin_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об администраторе не найдена",
        )

    if admin_number is not None:
        admin_info.admin_number = admin_number
    if employment is not None:
        admin_info.employment = employment
    if admin_hobby is not None:
        admin_info.admin_hobby = admin_hobby

    await db.commit()
    await db.refresh(admin_info)
    return admin_info


async def delete_admin_info_db(db: AsyncSession, admin_id: int) -> dict:
    """Удаление дополнительной информации об администраторе"""

    result = await db.execute(select(AdminInfo).filter(AdminInfo.admin_id == admin_id))
    admin_info = result.scalar_one_or_none()
    if not admin_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об администраторе не найдена",
        )
    await db.delete(admin_info)
    await db.commit()
    return {"status": "Удалена"}


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_all_admins_db(db: AsyncSession) -> List[Admin]:
    """Получение всех администраторов"""

    result = await db.execute(select(Admin))
    admins = result.scalars().all()
    return admins


async def get_active_admins_db(db: AsyncSession) -> List[Admin]:
    """Получение всех активных администраторов"""

    result = await db.execute(
        select(Admin).filter(Admin.admin_status == AdminStatus.ACTIVE)
    )
    admins = result.scalars().all()
    return admins


async def get_inactive_admins_db(db: AsyncSession) -> List[Admin]:
    """Получение всех неактивных администраторов"""

    result = await db.execute(
        select(Admin).filter(Admin.admin_status == AdminStatus.INACTIVE)
    )
    admins = result.scalars().all()
    return admins


async def activate_admin_db(db: AsyncSession, admin_id: int) -> Admin:
    """Активация администратора"""

    result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )

    admin.admin_status = AdminStatus.ACTIVE
    await db.commit()
    await db.refresh(admin)
    return admin


async def deactivate_admin_db(db: AsyncSession, admin_id: int) -> Admin:
    """Деактивация администратора"""

    result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )

    admin.admin_status = AdminStatus.INACTIVE
    await db.commit()
    await db.refresh(admin)
    return admin


async def get_admin_statistics_db(db: AsyncSession) -> dict:
    """Получение статистики администраторов"""

    total_admins_result = await db.execute(select(func.count(Admin.admin_id)))
    total_admins = total_admins_result.scalar()

    active_admins_result = await db.execute(
        select(func.count(Admin.admin_id)).filter(
            Admin.admin_status == AdminStatus.ACTIVE
        )
    )
    active_admins = active_admins_result.scalar()

    inactive_admins_result = await db.execute(
        select(func.count(Admin.admin_id)).filter(
            Admin.admin_status == AdminStatus.INACTIVE
        )
    )
    inactive_admins = inactive_admins_result.scalar()

    return {
        "total_admins": total_admins,
        "active_admins": active_admins,
        "inactive_admins": inactive_admins,
    }
