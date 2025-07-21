from typing import List, Optional
from fastapi import HTTPException, status
from app.database import get_db
from app.database.models.academic import Section, Subject

# ===========================================
# EXISTING SECTION OPERATIONS (Updated)
# ===========================================

def add_section_db(subject_id: int, name: str, order_number: Optional[int] = None) -> Section:
    """Добавление нового раздела"""
    with next(get_db()) as db:
        # Проверяем, что предмет существует
        subject = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        
        new_section = Section(
            subject_id=subject_id,
            name=name,
            order_number=order_number
        )
        db.add(new_section)
        db.commit()
        db.refresh(new_section)
        return new_section

def delete_section_db(section_id: int) -> dict:
    """Удаление раздела"""
    with next(get_db()) as db:
        sec = db.query(Section).filter_by(section_id=section_id).first()
        if not sec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Раздел не найден"
            )
        db.delete(sec)
        db.commit()
        return {"status": "Удалён"}

def find_section_db(section_id: int) -> Section:
    """Поиск раздела по ID"""
    with next(get_db()) as db:
        section = db.query(Section).filter_by(section_id=section_id).first()
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Раздел не найден"
            )
        return section

def edit_section_db(section_id: int, subject_id: Optional[int] = None,
                   name: Optional[str] = None, order_number: Optional[int] = None) -> Section:
    """Редактирование раздела"""
    with next(get_db()) as db:
        sec = db.query(Section).filter_by(section_id=section_id).first()
        if not sec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Раздел не найден"
            )
        
        if subject_id is not None:
            # Проверяем, что новый предмет существует
            subject = db.query(Subject).filter_by(subject_id=subject_id).first()
            if not subject:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Предмет не найден"
                )
            sec.subject_id = subject_id
        if name is not None:
            sec.name = name
        if order_number is not None:
            sec.order_number = order_number
            
        db.commit()
        db.refresh(sec)
        return sec

def get_section_name_db(section_id: int) -> str:
    """Получение названия раздела"""
    with next(get_db()) as db:
        section = db.query(Section).filter_by(section_id=section_id).first()
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Раздел не найден"
            )
        return section.name

def count_sections_by_subject_db(subject_id: int) -> int:
    """Подсчет количества разделов по предмету"""
    with next(get_db()) as db:
        # Проверяем, что предмет существует
        subject = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        
        return db.query(Section).filter_by(subject_id=subject_id).count()

# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================

def get_sections_by_subject_db(subject_id: int) -> List[Section]:
    """Получение всех разделов по предмету"""
    with next(get_db()) as db:
        # Проверяем, что предмет существует
        subject = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        
        sections = db.query(Section).filter_by(subject_id=subject_id).order_by(Section.order_number).all()
        
        if not sections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Разделы для предмета {subject_id} не найдены"
            )
        
        return sections

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_all_sections_db() -> List[Section]:
    """Получение всех разделов"""
    with next(get_db()) as db:
        sections = db.query(Section).order_by(Section.subject_id, Section.order_number).all()
        return sections

def get_section_by_order_db(subject_id: int, order_number: int) -> Section:
    """Получение раздела по порядковому номеру в рамках предмета"""
    with next(get_db()) as db:
        section = db.query(Section).filter_by(
            subject_id=subject_id,
            order_number=order_number
        ).first()
        
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Раздел с порядковым номером {order_number} для предмета {subject_id} не найден"
            )
        
        return section

def get_first_section_db(subject_id: int) -> Section:
    """Получение первого раздела предмета"""
    with next(get_db()) as db:
        section = db.query(Section).filter_by(subject_id=subject_id).order_by(Section.order_number).first()
        
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Разделы для предмета {subject_id} не найдены"
            )
        
        return section

def get_last_section_db(subject_id: int) -> Section:
    """Получение последнего раздела предмета"""
    with next(get_db()) as db:
        section = db.query(Section).filter_by(subject_id=subject_id).order_by(Section.order_number.desc()).first()
        
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Разделы для предмета {subject_id} не найдены"
            )
        
        return section

def search_sections_by_name_db(search_name: str) -> List[Section]:
    """Поиск разделов по названию"""
    with next(get_db()) as db:
        sections = db.query(Section).filter(
            Section.name.ilike(f"%{search_name}%")
        ).order_by(Section.subject_id, Section.order_number).all()
        
        if not sections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Разделы с названием, содержащим '{search_name}', не найдены"
            )
        
        return sections

def update_section_order_db(section_id: int, new_order: int) -> Section:
    """Обновление порядкового номера раздела"""
    with next(get_db()) as db:
        section = db.query(Section).filter_by(section_id=section_id).first()
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Раздел не найден"
            )
        
        section.order_number = new_order
        db.commit()
        db.refresh(section)
        return section