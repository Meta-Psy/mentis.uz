import sqlalchemy.orm
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database.models.user import Teacher, TeacherInfo, TeacherStatus, User, UserRole
from app.database.models.academic import Subject

# ===========================================
# TEACHER OPERATIONS (Updated - without create)
# ===========================================


async def get_teacher_by_id_db(db: AsyncSession, teacher_id: int) -> Teacher:
    """Получение учителя по ID"""

    result = await db.execute(select(Teacher).filter_by(teacher_id=teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )
    return teacher


async def update_teacher_db(
    db: AsyncSession,
    teacher_id: int,
    teacher_schedule: Optional[str] = None,
    teacher_status: Optional[TeacherStatus] = None,
) -> Teacher:
    """Обновление данных учителя"""

    result = await db.execute(select(Teacher).filter_by(teacher_id=teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    if teacher_schedule is not None:
        teacher.teacher_schedule = teacher_schedule
    if teacher_status is not None:
        teacher.teacher_status = teacher_status

    await db.commit()
    await db.refresh(teacher)
    return teacher


async def delete_teacher_db(db: AsyncSession, teacher_id: int) -> dict:
    """Удаление учителя"""

    result = await db.execute(select(Teacher).filter_by(teacher_id=teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )
    await db.delete(teacher)
    await db.commit()
    return {"status": "Удален"}


# ===========================================
# TEACHER INFO OPERATIONS
# ===========================================


async def create_teacher_info_db(
    db: AsyncSession,
    teacher_id: int,
    teacher_employment: Optional[str] = None,
    teacher_number: Optional[str] = None,
    dop_info: Optional[str] = None,
    education_background: Optional[str] = None,
    years_experiense: Optional[int] = None,
    certifications: Optional[str] = None,
    availability: Optional[str] = None,
    languages: Optional[str] = None,
) -> TeacherInfo:
    """Создание дополнительной информации об учителе"""

    # Проверяем, что учитель существует
    result = await db.execute(select(Teacher).filter_by(teacher_id=teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    # Проверяем, что информация еще не создана
    result = await db.execute(select(TeacherInfo).filter_by(teacher_id=teacher_id))
    existing_info = result.scalar_one_or_none()
    if existing_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Информация об учителе уже существует",
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
        languages=languages,
    )
    db.add(teacher_info)
    await db.commit()
    await db.refresh(teacher_info)
    return teacher_info


async def get_teacher_info_db(db: AsyncSession, teacher_id: int) -> TeacherInfo:
    """Получение дополнительной информации об учителе"""

    result = await db.execute(select(TeacherInfo).filter_by(teacher_id=teacher_id))
    teacher_info = result.scalar_one_or_none()
    if not teacher_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об учителе не найдена",
        )
    return teacher_info


async def update_teacher_info_db(
    db: AsyncSession,
    teacher_id: int,
    teacher_employment: Optional[str] = None,
    teacher_number: Optional[str] = None,
    dop_info: Optional[str] = None,
    education_background: Optional[str] = None,
    years_experiense: Optional[int] = None,
    certifications: Optional[str] = None,
    availability: Optional[str] = None,
    languages: Optional[str] = None,
) -> TeacherInfo:
    """Обновление дополнительной информации об учителе"""

    result = await db.execute(select(TeacherInfo).filter_by(teacher_id=teacher_id))
    teacher_info = result.scalar_one_or_none()
    if not teacher_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об учителе не найдена",
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

    await db.commit()
    await db.refresh(teacher_info)
    return teacher_info


async def delete_teacher_info_db(db: AsyncSession, teacher_id: int) -> dict:
    """Удаление дополнительной информации об учителе"""

    result = await db.execute(select(TeacherInfo).filter_by(teacher_id=teacher_id))
    teacher_info = result.scalar_one_or_none()
    if not teacher_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об учителе не найдена",
        )
    await db.delete(teacher_info)
    await db.commit()
    return {"status": "Удалена"}


# ===========================================
# TEACHER-SUBJECT OPERATIONS
# ===========================================


async def assign_subject_to_teacher_db(
    db: AsyncSession, teacher_id: int, subject_id: int
) -> Teacher:
    """Назначение предмета учителю"""

    # Получаем учителя с загруженными предметами
    result = await db.execute(
        select(Teacher).filter_by(teacher_id=teacher_id).options(selectinload(Teacher.subjects))
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    result = await db.execute(select(Subject).filter_by(subject_id=subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    # Проверяем, не назначен ли уже этот предмет учителю
    if subject in teacher.subjects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Предмет уже назначен данному учителю",
        )

    teacher.subjects.append(subject)
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def remove_subject_from_teacher_db(
    db: AsyncSession, teacher_id: int, subject_id: int
) -> Teacher:
    """Удаление предмета у учителя"""

    # Получаем учителя с загруженными предметами
    result = await db.execute(
        select(Teacher).filter_by(teacher_id=teacher_id).options(selectinload(Teacher.subjects))
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    result = await db.execute(select(Subject).filter_by(subject_id=subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    # Проверяем, назначен ли этот предмет учителю
    if subject not in teacher.subjects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Предмет не назначен данному учителю",
        )

    teacher.subjects.remove(subject)
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def get_teacher_subjects_db(db: AsyncSession, teacher_id: int) -> List[Subject]:
    """Получение предметов учителя"""

    result = await db.execute(
        select(Teacher).filter_by(teacher_id=teacher_id).options(selectinload(Teacher.subjects))
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )
    return teacher.subjects


async def get_teachers_by_subject_db(db: AsyncSession, subject_id: int) -> List[Teacher]:
    """Получение учителей по предмету"""

    result = await db.execute(
        select(Subject).filter_by(subject_id=subject_id).options(selectinload(Subject.teachers))
    )
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )
    return subject.teachers


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_all_teachers_db(db: AsyncSession) -> List[Teacher]:
    """Получение всех учителей"""

    result = await db.execute(select(Teacher))
    teachers = result.scalars().all()
    return list(teachers)


async def get_active_teachers_db(db: AsyncSession) -> List[Teacher]:
    """Получение всех активных учителей"""

    result = await db.execute(select(Teacher).filter_by(teacher_status=TeacherStatus.ACTIVE))
    teachers = result.scalars().all()
    return list(teachers)


async def get_inactive_teachers_db(db: AsyncSession) -> List[Teacher]:
    """Получение всех неактивных учителей"""

    result = await db.execute(select(Teacher).filter_by(teacher_status=TeacherStatus.INACTIVE))
    teachers = result.scalars().all()
    return list(teachers)


async def activate_teacher_db(db: AsyncSession, teacher_id: int) -> Teacher:
    """Активация учителя"""

    result = await db.execute(select(Teacher).filter_by(teacher_id=teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    teacher.teacher_status = TeacherStatus.ACTIVE
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def deactivate_teacher_db(db: AsyncSession, teacher_id: int) -> Teacher:
    """Деактивация учителя"""

    result = await db.execute(select(Teacher).filter_by(teacher_id=teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    teacher.teacher_status = TeacherStatus.INACTIVE
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def get_teacher_statistics_db(db: AsyncSession) -> dict:
    """Получение статистики учителей"""

    total_teachers = await db.scalar(select(func.count(Teacher.teacher_id)))
    active_teachers = await db.scalar(
        select(func.count(Teacher.teacher_id)).filter_by(teacher_status=TeacherStatus.ACTIVE)
    )
    inactive_teachers = await db.scalar(
        select(func.count(Teacher.teacher_id)).filter_by(teacher_status=TeacherStatus.INACTIVE)
    )

    return {
        "total_teachers": total_teachers,
        "active_teachers": active_teachers,
        "inactive_teachers": inactive_teachers,
    }