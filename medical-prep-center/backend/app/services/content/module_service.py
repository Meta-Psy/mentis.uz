from typing import List, Optional
from fastapi import HTTPException, status
from app.database import get_db
from app.database.models.academic import Moduls

# ===========================================
# EXISTING MODULE OPERATIONS (Updated)
# ===========================================

def add_modul_db(start_topic_chem: int, start_topic_bio: int, end_topic_chem: int,
                 end_topic_bio: int, order_number: Optional[int] = None,
                 name: Optional[str] = None) -> Moduls:
    """Добавление нового модуля"""
    with next(get_db()) as db:
        new_modul = Moduls(
            start_topic_chem=start_topic_chem,
            start_topic_bio=start_topic_bio,
            end_topic_chem=end_topic_chem,
            end_topic_bio=end_topic_bio,
            order_number=order_number,
            name=name
        )
        db.add(new_modul)
        db.commit()
        db.refresh(new_modul)
        return new_modul

def delete_modul_db(modul_id: int) -> dict:
    """Удаление модуля"""
    with next(get_db()) as db:
        modul = db.query(Moduls).filter_by(modul_id=modul_id).first()
        if not modul:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Модуль не найден"
            )
        db.delete(modul)
        db.commit()
        return {"status": "Удалён"}

def find_modul_db(modul_id: int) -> Moduls:
    """Поиск модуля по ID"""
    with next(get_db()) as db:
        modul = db.query(Moduls).filter_by(modul_id=modul_id).first()
        if not modul:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Модуль не найден"
            )
        return modul

def edit_modul_db(modul_id: int, start_topic_chem: Optional[int] = None,
                  start_topic_bio: Optional[int] = None, end_topic_chem: Optional[int] = None,
                  end_topic_bio: Optional[int] = None, order_number: Optional[int] = None,
                  name: Optional[str] = None) -> Moduls:
    """Редактирование модуля"""
    with next(get_db()) as db:
        modul = db.query(Moduls).filter_by(modul_id=modul_id).first()
        if not modul:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Модуль не найден"
            )
        
        if start_topic_chem is not None:
            modul.start_topic_chem = start_topic_chem
        if start_topic_bio is not None:
            modul.start_topic_bio = start_topic_bio
        if end_topic_chem is not None:
            modul.end_topic_chem = end_topic_chem
        if end_topic_bio is not None:
            modul.end_topic_bio = end_topic_bio
        if order_number is not None:
            modul.order_number = order_number
        if name is not None:
            modul.name = name
            
        db.commit()
        db.refresh(modul)
        return modul

# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================

def get_all_modules_db() -> List[Moduls]:
    """Получение всех модулей"""
    with next(get_db()) as db:
        modules = db.query(Moduls).order_by(Moduls.order_number).all()
        return modules

def get_modules_by_subject_db(subject_name: str) -> List[Moduls]:
    """Получение модулей по предмету (химия или биология)"""
    with next(get_db()) as db:
        if subject_name.lower() in ['химия', 'chemistry', 'chem']:
            # Возвращаем модули, которые включают темы по химии
            modules = db.query(Moduls).filter(
                Moduls.start_topic_chem.isnot(None),
                Moduls.end_topic_chem.isnot(None)
            ).order_by(Moduls.order_number).all()
        elif subject_name.lower() in ['биология', 'biology', 'bio']:
            # Возвращаем модули, которые включают темы по биологии
            modules = db.query(Moduls).filter(
                Moduls.start_topic_bio.isnot(None),
                Moduls.end_topic_bio.isnot(None)
            ).order_by(Moduls.order_number).all()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверное название предмета. Используйте 'химия' или 'биология'"
            )
        
        if not modules:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Модули по предмету '{subject_name}' не найдены"
            )
        
        return modules

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_module_by_order_db(order_number: int) -> Moduls:
    """Получение модуля по порядковому номеру"""
    with next(get_db()) as db:
        modul = db.query(Moduls).filter_by(order_number=order_number).first()
        if not modul:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Модуль с порядковым номером {order_number} не найден"
            )
        return modul

def get_modules_count_db() -> int:
    """Получение количества модулей"""
    with next(get_db()) as db:
        return db.query(Moduls).count()

def get_modules_by_topic_range_db(subject_type: str, start_topic: int, end_topic: int) -> List[Moduls]:
    """Получение модулей по диапазону тем"""
    with next(get_db()) as db:
        if subject_type.lower() in ['химия', 'chemistry', 'chem']:
            modules = db.query(Moduls).filter(
                Moduls.start_topic_chem <= end_topic,
                Moduls.end_topic_chem >= start_topic
            ).order_by(Moduls.order_number).all()
        elif subject_type.lower() in ['биология', 'biology', 'bio']:
            modules = db.query(Moduls).filter(
                Moduls.start_topic_bio <= end_topic,
                Moduls.end_topic_bio >= start_topic
            ).order_by(Moduls.order_number).all()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный тип предмета"
            )
        
        return modules