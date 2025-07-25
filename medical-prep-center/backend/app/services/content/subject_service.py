from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models.academic import Subject, Section, Topic, MaterialFile
from app.services.content.section_service import get_section_with_materials_db

# ===========================================
# EXISTING SUBJECT OPERATIONS (Updated)
# ===========================================


async def add_subject_db(
    db: AsyncSession, name: str, description: Optional[str] = None
) -> Subject:
    """Добавление нового предмета"""

    # Проверяем, что предмет с таким названием не существует
    existing_subject_result = await db.execute(
        select(Subject).filter(Subject.name == name)
    )
    existing_subject = existing_subject_result.scalar_one_or_none()
    if existing_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Предмет с названием '{name}' уже существует",
        )

    new_subject = Subject(name=name, description=description)
    db.add(new_subject)
    await db.commit()
    await db.refresh(new_subject)
    return new_subject


async def delete_subject_db(db: AsyncSession, subject_id: int) -> dict:
    """Удаление предмета"""

    result = await db.execute(select(Subject).filter(Subject.subject_id == subject_id))
    subj = result.scalar_one_or_none()
    if not subj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )
    await db.delete(subj)
    await db.commit()
    return {"status": "Удалён"}


async def find_subject_db(db: AsyncSession, subject_id: int) -> Subject:
    """Поиск предмета по ID"""

    result = await db.execute(select(Subject).filter(Subject.subject_id == subject_id))
    subj = result.scalar_one_or_none()
    if not subj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )
    return subj


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_all_subjects_db(db: AsyncSession) -> List[Subject]:
    """Получение всех предметов"""

    result = await db.execute(select(Subject))
    subjects = result.scalars().all()
    return subjects


async def edit_subject_db(
    db: AsyncSession,
    subject_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Subject:
    """Редактирование предмета"""

    result = await db.execute(select(Subject).filter(Subject.subject_id == subject_id))
    subj = result.scalar_one_or_none()
    if not subj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    # Проверяем уникальность названия, если оно изменяется
    if name is not None and name != subj.name:
        existing_subject_result = await db.execute(
            select(Subject).filter(Subject.name == name)
        )
        existing_subject = existing_subject_result.scalar_one_or_none()
        if existing_subject:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Предмет с названием '{name}' уже существует",
            )
        subj.name = name

    if description is not None:
        subj.description = description

    await db.commit()
    await db.refresh(subj)
    return subj


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_subject_by_name_db(db: AsyncSession, name: str) -> Subject:
    """Получение предмета по названию"""

    result = await db.execute(select(Subject).filter(Subject.name == name))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Предмет с названием '{name}' не найден",
        )
    return subject


async def search_subjects_by_name_db(
    db: AsyncSession, search_name: str
) -> List[Subject]:
    """Поиск предметов по названию"""

    result = await db.execute(
        select(Subject).filter(Subject.name.ilike(f"%{search_name}%"))
    )
    subjects = result.scalars().all()

    if not subjects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Предметы с названием, содержащим '{search_name}', не найдены",
        )

    return subjects


async def get_subjects_count_db(db: AsyncSession) -> int:
    """Получение количества предметов"""

    result = await db.execute(select(func.count(Subject.subject_id)))
    return result.scalar()


async def get_subjects_with_sections_db(db: AsyncSession) -> List[Subject]:
    """Получение предметов, у которых есть разделы"""

    result = await db.execute(select(Subject).filter(Subject.sections.any()))
    subjects = result.scalars().all()
    return subjects


async def get_subjects_without_sections_db(db: AsyncSession) -> List[Subject]:
    """Получение предметов без разделов"""

    result = await db.execute(select(Subject).filter(~Subject.sections.any()))
    subjects = result.scalars().all()
    return subjects


async def update_subject_description_db(
    db: AsyncSession, subject_id: int, description: str
) -> Subject:
    """Обновление описания предмета"""

    result = await db.execute(select(Subject).filter(Subject.subject_id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    subject.description = description
    await db.commit()
    await db.refresh(subject)
    return subject


async def remove_subject_description_db(db: AsyncSession, subject_id: int) -> Subject:
    """Удаление описания предмета"""

    result = await db.execute(select(Subject).filter(Subject.subject_id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    subject.description = None
    await db.commit()
    await db.refresh(subject)
    return subject


async def get_subject_materials_db(db: AsyncSession, subject_name: str) -> dict:
    """Получение всех материалов предмета"""

    # Ищем предмет
    result = await db.execute(
        select(Subject).filter(Subject.name.ilike(f"%{subject_name}%"))
    )
    subject = result.scalar_one_or_none()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Предмет '{subject_name}' не найден",
        )

    # Получаем все разделы предмета
    sections_result = await db.execute(
        select(Section)
        .filter(Section.subject_id == subject.subject_id)
        .order_by(Section.order_number)
    )
    sections = sections_result.scalars().all()

    modules = []
    for section in sections:
        try:
            section_data = await get_section_with_materials_db(db, section.section_id)
            modules.append(section_data)
        except HTTPException:
            # Если не удается получить данные раздела, пропускаем
            continue

    return {"modules": modules}  # Используем "modules" для совместимости с фронтендом


async def get_materials_statistics_db(db: AsyncSession) -> dict:
    """Получение статистики материалов"""

    total_subjects_result = await db.execute(select(func.count(Subject.subject_id)))
    total_subjects = total_subjects_result.scalar()

    total_sections_result = await db.execute(select(func.count(Section.section_id)))
    total_sections = total_sections_result.scalar()

    total_topics_result = await db.execute(select(func.count(Topic.topic_id)))
    total_topics = total_topics_result.scalar()

    total_files_result = await db.execute(select(func.count(MaterialFile.file_id)))
    total_files = total_files_result.scalar()

    # Статистика по предметам
    subjects_breakdown = {}
    subjects_result = await db.execute(select(Subject))
    subjects = subjects_result.scalars().all()

    for subject in subjects:
        sections_count_result = await db.execute(
            select(func.count(Section.section_id)).filter(
                Section.subject_id == subject.subject_id
            )
        )
        sections_count = sections_count_result.scalar()
        subjects_breakdown[subject.name] = sections_count

    return {
        "total_subjects": total_subjects,
        "total_sections": total_sections,
        "total_topics": total_topics,
        "total_files": total_files,
        "subjects_breakdown": subjects_breakdown,
    }
