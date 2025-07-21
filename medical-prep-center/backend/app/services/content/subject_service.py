from typing import List, Optional
from fastapi import HTTPException, status
from app.database import get_db
from app.database.models.academic import Subject

# ===========================================
# EXISTING SUBJECT OPERATIONS (Updated)
# ===========================================

def add_subject_db(name: str, description: Optional[str] = None) -> Subject:
    """Добавление нового предмета"""
    with next(get_db()) as db:
        # Проверяем, что предмет с таким названием не существует
        existing_subject = db.query(Subject).filter_by(name=name).first()
        if existing_subject:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Предмет с названием '{name}' уже существует"
            )
        
        new_subject = Subject(name=name, description=description)
        db.add(new_subject)
        db.commit()
        db.refresh(new_subject)
        return new_subject

def delete_subject_db(subject_id: int) -> dict:
    """Удаление предмета"""
    with next(get_db()) as db:
        subj = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        db.delete(subj)
        db.commit()
        return {"status": "Удалён"}

def find_subject_db(subject_id: int) -> Subject:
    """Поиск предмета по ID"""
    with next(get_db()) as db:
        subj = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        return subj

# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================

def get_all_subjects_db() -> List[Subject]:
    """Получение всех предметов"""
    with next(get_db()) as db:
        subjects = db.query(Subject).all()
        return subjects

def edit_subject_db(subject_id: int, name: Optional[str] = None,
                   description: Optional[str] = None) -> Subject:
    """Редактирование предмета"""
    with next(get_db()) as db:
        subj = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        
        # Проверяем уникальность названия, если оно изменяется
        if name is not None and name != subj.name:
            existing_subject = db.query(Subject).filter_by(name=name).first()
            if existing_subject:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Предмет с названием '{name}' уже существует"
                )
            subj.name = name
            
        if description is not None:
            subj.description = description
            
        db.commit()
        db.refresh(subj)
        return subj

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_subject_by_name_db(name: str) -> Subject:
    """Получение предмета по названию"""
    with next(get_db()) as db:
        subject = db.query(Subject).filter_by(name=name).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Предмет с названием '{name}' не найден"
            )
        return subject

def search_subjects_by_name_db(search_name: str) -> List[Subject]:
    """Поиск предметов по названию"""
    with next(get_db()) as db:
        subjects = db.query(Subject).filter(
            Subject.name.ilike(f"%{search_name}%")
        ).all()
        
        if not subjects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Предметы с названием, содержащим '{search_name}', не найдены"
            )
        
        return subjects

def get_subjects_count_db() -> int:
    """Получение количества предметов"""
    with next(get_db()) as db:
        return db.query(Subject).count()

def get_subjects_with_sections_db() -> List[Subject]:
    """Получение предметов, у которых есть разделы"""
    with next(get_db()) as db:
        subjects = db.query(Subject).filter(Subject.sections.any()).all()
        return subjects

def get_subjects_without_sections_db() -> List[Subject]:
    """Получение предметов без разделов"""
    with next(get_db()) as db:
        subjects = db.query(Subject).filter(~Subject.sections.any()).all()
        return subjects

def update_subject_description_db(subject_id: int, description: str) -> Subject:
    """Обновление описания предмета"""
    with next(get_db()) as db:
        subject = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        
        subject.description = description
        db.commit()
        db.refresh(subject)
        return subject

def remove_subject_description_db(subject_id: int) -> Subject:
    """Удаление описания предмета"""
    with next(get_db()) as db:
        subject = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        
        subject.description = None
        db.commit()
        db.refresh(subject)
        return subject