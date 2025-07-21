from typing import List, Optional
from fastapi import HTTPException, status
from app.database import get_db
from app.database.models.user import (
    Teacher, TeacherInfo, TeacherStatus, User, UserRole
)
from app.database.models.academic import Subject

# ===========================================
# TEACHER OPERATIONS (Updated - without create)
# ===========================================

def get_teacher_by_id_db(teacher_id: int) -> Teacher:
    """Получение учителя по ID"""
    with next(get_db()) as db:
        teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Учитель не найден"
            )
        return teacher

def update_teacher_db(teacher_id: int, teacher_schedule: Optional[str] = None,
                     teacher_status: Optional[TeacherStatus] = None) -> Teacher:
    """Обновление данных учителя"""
    with next(get_db()) as db:
        teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Учитель не найден"
            )

        if teacher_schedule is not None:
            teacher.teacher_schedule = teacher_schedule
        if teacher_status is not None:
            teacher.teacher_status = teacher_status

        db.commit()
        db.refresh(teacher)
        return teacher

def delete_teacher_db(teacher_id: int) -> dict:
    """Удаление учителя"""
    with next(get_db()) as db:
        teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Учитель не найден"
            )
        db.delete(teacher)
        db.commit()
        return {"status": "Удален"}

# ===========================================
# TEACHER INFO OPERATIONS
# ===========================================

def create_teacher_info_db(teacher_id: int, teacher_employment: Optional[str] = None,
                          teacher_number: Optional[str] = None, dop_info: Optional[str] = None,
                          education_background: Optional[str] = None,
                          years_experiense: Optional[int] = None,
                          certifications: Optional[str] = None,
                          availability: Optional[str] = None,
                          languages: Optional[str] = None) -> TeacherInfo:
    """Создание дополнительной информации об учителе"""
    with next(get_db()) as db:
        # Проверяем, что учитель существует
        teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Учитель не найден"
            )

        # Проверяем, что информация еще не создана
        existing_info = db.query(TeacherInfo).filter_by(teacher_id=teacher_id).first()
        if existing_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Информация об учителе уже существует"
            )

        teacher_info = TeacherInfo(
            teacher_id=teacher_id,
            teacher_employment=teacher_employment,
            teacher_number=teacher_number,
            dop_info=dop_info,
            education_background=education_background,
            years_experiense=years_experiense,
            certifications=certifications,
            availability=availability,
            languages=languages
        )
        db.add(teacher_info)
        db.commit()
        db.refresh(teacher_info)
        return teacher_info

def get_teacher_info_db(teacher_id: int) -> TeacherInfo:
    """Получение дополнительной информации об учителе"""
    with next(get_db()) as db:
        teacher_info = db.query(TeacherInfo).filter_by(teacher_id=teacher_id).first()
        if not teacher_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Информация об учителе не найдена"
            )
        return teacher_info

def update_teacher_info_db(teacher_id: int, teacher_employment: Optional[str] = None,
                          teacher_number: Optional[str] = None, dop_info: Optional[str] = None,
                          education_background: Optional[str] = None,
                          years_experiense: Optional[int] = None,
                          certifications: Optional[str] = None,
                          availability: Optional[str] = None,
                          languages: Optional[str] = None) -> TeacherInfo:
    """Обновление дополнительной информации об учителе"""
    with next(get_db()) as db:
        teacher_info = db.query(TeacherInfo).filter_by(teacher_id=teacher_id).first()
        if not teacher_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Информация об учителе не найдена"
            )

        if teacher_employment is not None:
            teacher_info.teacher_employment = teacher_employment
        if teacher_number is not None:
            teacher_info.teacher_number = teacher_number
        if dop_info is not None:
            teacher_info.dop_info = dop_info
        if education_background is not None:
            teacher_info.education_background = education_background
        if years_experiense is not None:
            teacher_info.years_experiense = years_experiense
        if certifications is not None:
            teacher_info.certifications = certifications
        if availability is not None:
            teacher_info.availability = availability
        if languages is not None:
            teacher_info.languages = languages

        db.commit()
        db.refresh(teacher_info)
        return teacher_info

def delete_teacher_info_db(teacher_id: int) -> dict:
    """Удаление дополнительной информации об учителе"""
    with next(get_db()) as db:
        teacher_info = db.query(TeacherInfo).filter_by(teacher_id=teacher_id).first()
        if not teacher_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Информация об учителе не найдена"
            )
        db.delete(teacher_info)
        db.commit()
        return {"status": "Удалена"}

# ===========================================
# TEACHER-SUBJECT OPERATIONS
# ===========================================

def assign_subject_to_teacher_db(teacher_id: int, subject_id: int) -> Teacher:
    """Назначение предмета учителю"""
    with next(get_db()) as db:
        teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Учитель не найден"
            )
        
        subject = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        
        # Проверяем, не назначен ли уже этот предмет учителю
        if subject in teacher.subjects:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Предмет уже назначен данному учителю"
            )
        
        teacher.subjects.append(subject)
        db.commit()
        db.refresh(teacher)
        return teacher

def remove_subject_from_teacher_db(teacher_id: int, subject_id: int) -> Teacher:
    """Удаление предмета у учителя"""
    with next(get_db()) as db:
        teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Учитель не найден"
            )
        
        subject = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        
        # Проверяем, назначен ли этот предмет учителю
        if subject not in teacher.subjects:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Предмет не назначен данному учителю"
            )
        
        teacher.subjects.remove(subject)
        db.commit()
        db.refresh(teacher)
        return teacher

def get_teacher_subjects_db(teacher_id: int) -> List[Subject]:
    """Получение предметов учителя"""
    with next(get_db()) as db:
        teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Учитель не найден"
            )
        return teacher.subjects

def get_teachers_by_subject_db(subject_id: int) -> List[Teacher]:
    """Получение учителей по предмету"""
    with next(get_db()) as db:
        subject = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Предмет не найден"
            )
        return subject.teachers

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_all_teachers_db() -> List[Teacher]:
    """Получение всех учителей"""
    with next(get_db()) as db:
        teachers = db.query(Teacher).all()
        return teachers

def get_active_teachers_db() -> List[Teacher]:
    """Получение всех активных учителей"""
    with next(get_db()) as db:
        teachers = db.query(Teacher).filter_by(teacher_status=TeacherStatus.ACTIVE).all()
        return teachers

def get_inactive_teachers_db() -> List[Teacher]:
    """Получение всех неактивных учителей"""
    with next(get_db()) as db:
        teachers = db.query(Teacher).filter_by(teacher_status=TeacherStatus.INACTIVE).all()
        return teachers

def activate_teacher_db(teacher_id: int) -> Teacher:
    """Активация учителя"""
    with next(get_db()) as db:
        teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Учитель не найден"
            )
        
        teacher.teacher_status = TeacherStatus.ACTIVE
        db.commit()
        db.refresh(teacher)
        return teacher

def deactivate_teacher_db(teacher_id: int) -> Teacher:
    """Деактивация учителя"""
    with next(get_db()) as db:
        teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Учитель не найден"
            )
        
        teacher.teacher_status = TeacherStatus.INACTIVE
        db.commit()
        db.refresh(teacher)
        return teacher

def get_teacher_statistics_db() -> dict:
    """Получение статистики учителей"""
    with next(get_db()) as db:
        total_teachers = db.query(Teacher).count()
        active_teachers = db.query(Teacher).filter_by(teacher_status=TeacherStatus.ACTIVE).count()
        inactive_teachers = db.query(Teacher).filter_by(teacher_status=TeacherStatus.INACTIVE).count()
        
        return {
            "total_teachers": total_teachers,
            "active_teachers": active_teachers,
            "inactive_teachers": inactive_teachers
        }