from typing import List, Optional
from fastapi import HTTPException, status
from app.database import get_db
from app.database.models.user import (
    Admin, AdminInfo, AdminStatus, User, UserRole
)

# ===========================================
# ADMIN OPERATIONS (Updated - without create)
# ===========================================

def get_admin_by_id_db(admin_id: int) -> Admin:
    """Получение администратора по ID"""
    with next(get_db()) as db:
        admin = db.query(Admin).filter_by(admin_id=admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Администратор не найден"
            )
        return admin

def update_admin_db(admin_id: int, schedule: Optional[str] = None,
                   admin_status: Optional[AdminStatus] = None) -> Admin:
    """Обновление данных администратора"""
    with next(get_db()) as db:
        admin = db.query(Admin).filter_by(admin_id=admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Администратор не найден"
            )

        if schedule is not None:
            admin.schedule = schedule
        if admin_status is not None:
            admin.admin_status = admin_status

        db.commit()
        db.refresh(admin)
        return admin

def delete_admin_db(admin_id: int) -> dict:
    """Удаление администратора"""
    with next(get_db()) as db:
        admin = db.query(Admin).filter_by(admin_id=admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Администратор не найден"
            )
        db.delete(admin)
        db.commit()
        return {"status": "Удален"}

# ===========================================
# ADMIN INFO OPERATIONS
# ===========================================

def create_admin_info_db(admin_id: int, admin_number: Optional[str] = None,
                        employment: Optional[str] = None, admin_hobby: Optional[str] = None) -> AdminInfo:
    """Создание дополнительной информации об администраторе"""
    with next(get_db()) as db:
        # Проверяем, что администратор существует
        admin = db.query(Admin).filter_by(admin_id=admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Администратор не найден"
            )

        # Проверяем, что информация еще не создана
        existing_info = db.query(AdminInfo).filter_by(admin_id=admin_id).first()
        if existing_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Информация об администраторе уже существует"
            )

        admin_info = AdminInfo(
            admin_id=admin_id,
            admin_number=admin_number,
            employment=employment,
            admin_hobby=admin_hobby
        )
        db.add(admin_info)
        db.commit()
        db.refresh(admin_info)
        return admin_info

def get_admin_info_db(admin_id: int) -> AdminInfo:
    """Получение дополнительной информации об администраторе"""
    with next(get_db()) as db:
        admin_info = db.query(AdminInfo).filter_by(admin_id=admin_id).first()
        if not admin_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Информация об администраторе не найдена"
            )
        return admin_info

def update_admin_info_db(admin_id: int, admin_number: Optional[str] = None,
                        employment: Optional[str] = None, admin_hobby: Optional[str] = None) -> AdminInfo:
    """Обновление дополнительной информации об администраторе"""
    with next(get_db()) as db:
        admin_info = db.query(AdminInfo).filter_by(admin_id=admin_id).first()
        if not admin_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Информация об администраторе не найдена"
            )

        if admin_number is not None:
            admin_info.admin_number = admin_number
        if employment is not None:
            admin_info.employment = employment
        if admin_hobby is not None:
            admin_info.admin_hobby = admin_hobby

        db.commit()
        db.refresh(admin_info)
        return admin_info

def delete_admin_info_db(admin_id: int) -> dict:
    """Удаление дополнительной информации об администраторе"""
    with next(get_db()) as db:
        admin_info = db.query(AdminInfo).filter_by(admin_id=admin_id).first()
        if not admin_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Информация об администраторе не найдена"
            )
        db.delete(admin_info)
        db.commit()
        return {"status": "Удалена"}

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_all_admins_db() -> List[Admin]:
    """Получение всех администраторов"""
    with next(get_db()) as db:
        admins = db.query(Admin).all()
        return admins

def get_active_admins_db() -> List[Admin]:
    """Получение всех активных администраторов"""
    with next(get_db()) as db:
        admins = db.query(Admin).filter_by(admin_status=AdminStatus.ACTIVE).all()
        return admins

def get_inactive_admins_db() -> List[Admin]:
    """Получение всех неактивных администраторов"""
    with next(get_db()) as db:
        admins = db.query(Admin).filter_by(admin_status=AdminStatus.INACTIVE).all()
        return admins

def activate_admin_db(admin_id: int) -> Admin:
    """Активация администратора"""
    with next(get_db()) as db:
        admin = db.query(Admin).filter_by(admin_id=admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Администратор не найден"
            )
        
        admin.admin_status = AdminStatus.ACTIVE
        db.commit()
        db.refresh(admin)
        return admin

def deactivate_admin_db(admin_id: int) -> Admin:
    """Деактивация администратора"""
    with next(get_db()) as db:
        admin = db.query(Admin).filter_by(admin_id=admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Администратор не найден"
            )
        
        admin.admin_status = AdminStatus.INACTIVE
        db.commit()
        db.refresh(admin)
        return admin

def get_admin_statistics_db() -> dict:
    """Получение статистики администраторов"""
    with next(get_db()) as db:
        total_admins = db.query(Admin).count()
        active_admins = db.query(Admin).filter_by(admin_status=AdminStatus.ACTIVE).count()
        inactive_admins = db.query(Admin).filter_by(admin_status=AdminStatus.INACTIVE).count()
        
        return {
            "total_admins": total_admins,
            "active_admins": active_admins,
            "inactive_admins": inactive_admins
        }