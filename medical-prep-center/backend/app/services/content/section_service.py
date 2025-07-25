from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database.models.academic import (
    Section,
    Subject,
    MaterialFile,
    Block,
    Topic,
    TopicTestMapping,
    TestType,
)
from app.services.content.topic_service import get_material_files_by_section_db

# ===========================================
# EXISTING SECTION OPERATIONS (Updated)
# ===========================================


async def add_section_db(
    db: AsyncSession, subject_id: int, name: str, order_number: Optional[int] = None
) -> Section:
    """Добавление нового раздела"""

    # Проверяем, что предмет существует
    subject_result = await db.execute(
        select(Subject).filter(Subject.subject_id == subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    new_section = Section(subject_id=subject_id, name=name, order_number=order_number)
    db.add(new_section)
    await db.commit()
    await db.refresh(new_section)
    return new_section


async def delete_section_db(db: AsyncSession, section_id: int) -> dict:
    """Удаление раздела"""

    result = await db.execute(select(Section).filter(Section.section_id == section_id))
    sec = result.scalar_one_or_none()
    if not sec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )
    await db.delete(sec)
    await db.commit()
    return {"status": "Удалён"}


async def find_section_db(db: AsyncSession, section_id: int) -> Section:
    """Поиск раздела по ID"""

    result = await db.execute(select(Section).filter(Section.section_id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )
    return section


async def edit_section_db(
    db: AsyncSession,
    section_id: int,
    subject_id: Optional[int] = None,
    name: Optional[str] = None,
    order_number: Optional[int] = None,
) -> Section:
    """Редактирование раздела"""

    result = await db.execute(select(Section).filter(Section.section_id == section_id))
    sec = result.scalar_one_or_none()
    if not sec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )

    if subject_id is not None:
        # Проверяем, что новый предмет существует
        subject_result = await db.execute(
            select(Subject).filter(Subject.subject_id == subject_id)
        )
        subject = subject_result.scalar_one_or_none()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
            )
        sec.subject_id = subject_id
    if name is not None:
        sec.name = name
    if order_number is not None:
        sec.order_number = order_number

    await db.commit()
    await db.refresh(sec)
    return sec


async def get_section_name_db(db: AsyncSession, section_id: int) -> str:
    """Получение названия раздела"""

    result = await db.execute(select(Section).filter(Section.section_id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )
    return section.name


async def count_sections_by_subject_db(db: AsyncSession, subject_id: int) -> int:
    """Подсчет количества разделов по предмету"""

    # Проверяем, что предмет существует
    subject_result = await db.execute(
        select(Subject).filter(Subject.subject_id == subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    result = await db.execute(
        select(func.count(Section.section_id)).filter(Section.subject_id == subject_id)
    )
    return result.scalar()


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_sections_by_subject_db(
    db: AsyncSession, subject_id: int
) -> List[Section]:
    """Получение всех разделов по предмету"""

    # Проверяем, что предмет существует
    subject_result = await db.execute(
        select(Subject).filter(Subject.subject_id == subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    result = await db.execute(
        select(Section)
        .filter(Section.subject_id == subject_id)
        .order_by(Section.order_number)
    )
    sections = result.scalars().all()

    if not sections:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Разделы для предмета {subject_id} не найдены",
        )

    return sections


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_all_sections_db(db: AsyncSession) -> List[Section]:
    """Получение всех разделов"""

    result = await db.execute(
        select(Section).order_by(Section.subject_id, Section.order_number)
    )
    sections = result.scalars().all()
    return sections


async def get_section_by_order_db(
    db: AsyncSession, subject_id: int, order_number: int
) -> Section:
    """Получение раздела по порядковому номеру в рамках предмета"""

    result = await db.execute(
        select(Section).filter(
            Section.subject_id == subject_id, Section.order_number == order_number
        )
    )
    section = result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Раздел с порядковым номером {order_number} для предмета {subject_id} не найден",
        )

    return section


async def get_first_section_db(db: AsyncSession, subject_id: int) -> Section:
    """Получение первого раздела предмета"""

    result = await db.execute(
        select(Section)
        .filter(Section.subject_id == subject_id)
        .order_by(Section.order_number)
        .limit(1)
    )
    section = result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Разделы для предмета {subject_id} не найдены",
        )

    return section


async def get_last_section_db(db: AsyncSession, subject_id: int) -> Section:
    """Получение последнего раздела предмета"""

    result = await db.execute(
        select(Section)
        .filter(Section.subject_id == subject_id)
        .order_by(Section.order_number.desc())
        .limit(1)
    )
    section = result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Разделы для предмета {subject_id} не найдены",
        )

    return section


async def search_sections_by_name_db(
    db: AsyncSession, search_name: str
) -> List[Section]:
    """Поиск разделов по названию"""

    result = await db.execute(
        select(Section)
        .filter(Section.name.ilike(f"%{search_name}%"))
        .order_by(Section.subject_id, Section.order_number)
    )
    sections = result.scalars().all()

    if not sections:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Разделы с названием, содержащим '{search_name}', не найдены",
        )

    return sections


async def update_section_order_db(
    db: AsyncSession, section_id: int, new_order: int
) -> Section:
    """Обновление порядкового номера раздела"""

    result = await db.execute(select(Section).filter(Section.section_id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )

    section.order_number = new_order
    await db.commit()
    await db.refresh(section)
    return section


async def get_section_with_materials_db(db: AsyncSession, section_id: int) -> dict:
    """Получение раздела с материалами и темами"""

    result = await db.execute(
        select(Section)
        .options(selectinload(Section.material_files))
        .filter(Section.section_id == section_id)
    )
    section = result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )

    # Получаем файлы материалов
    material_files = await get_material_files_by_section_db(section_id)

    # Получаем темы через блоки
    blocks_result = await db.execute(
        select(Block).filter(Block.section_id == section_id)
    )
    blocks = blocks_result.scalars().all()
    topics = []

    for block in blocks:
        block_topics_result = await db.execute(
            select(Topic)
            .filter(Topic.block_id == block.block_id)
            .order_by(Topic.number)
        )
        block_topics = block_topics_result.scalars().all()

        for topic in block_topics:
            # Получаем test_id для темы
            test_mapping_result = await db.execute(
                select(TopicTestMapping).filter(
                    TopicTestMapping.topic_id == topic.topic_id,
                    TopicTestMapping.test_type == TestType.TRAINING,
                )
            )
            test_mapping = test_mapping_result.scalar_one_or_none()
            test_id = test_mapping.test_id if test_mapping else topic.topic_id + 100

            topics.append(
                {
                    "id": topic.topic_id,
                    "title": topic.name,
                    "homework": topic.homework.split("\n") if topic.homework else [],
                    "videoUrl": topic.video_url
                    or "https://www.youtube.com/embed/dQw4w9WgXcQ",
                    "testId": test_id,
                    "block_name": block.name,
                }
            )

    return {
        "id": section.section_id,
        "name": (
            f"Модуль {section.order_number}" if section.order_number else section.name
        ),
        "books": [
            {
                "id": file.file_id,
                "title": file.title,
                "author": file.author,
                "size": file.file_size,
                "format": file.file_format,
                "download_url": file.download_url,
            }
            for file in material_files["books"]
        ],
        "testBooks": [
            {
                "id": file.file_id,
                "title": file.title,
                "author": file.author,
                "size": file.file_size,
                "format": file.file_format,
                "download_url": file.download_url,
            }
            for file in material_files["test_books"]
        ],
        "topics": topics,
    }


async def search_materials_db(
    db: AsyncSession,
    query: str,
    subject_filter: Optional[str] = None,
    section_filter: Optional[int] = None,
) -> List[dict]:
    """Поиск по материалам"""

    results = []

    # Поиск по темам
    topic_query = select(Topic).join(Block).join(Section).join(Subject)

    if subject_filter:
        topic_query = topic_query.filter(Subject.name.ilike(f"%{subject_filter}%"))
    if section_filter:
        topic_query = topic_query.filter(Section.section_id == section_filter)

    topic_query = topic_query.filter(Topic.name.ilike(f"%{query}%"))
    topics_result = await db.execute(topic_query)
    topics = topics_result.scalars().all()

    for topic in topics:
        results.append(
            {
                "type": "topic",
                "id": topic.topic_id,
                "title": topic.name,
                "description": (
                    topic.homework[:100] + "..."
                    if topic.homework and len(topic.homework) > 100
                    else topic.homework
                ),
                "subject_name": topic.block.section.subject.name,
                "section_name": topic.block.section.name,
            }
        )

    # Поиск по разделам
    section_query = select(Section).join(Subject)

    if subject_filter:
        section_query = section_query.filter(Subject.name.ilike(f"%{subject_filter}%"))

    section_query = section_query.filter(Section.name.ilike(f"%{query}%"))
    sections_result = await db.execute(section_query)
    sections = sections_result.scalars().all()

    for section in sections:
        results.append(
            {
                "type": "section",
                "id": section.section_id,
                "title": section.name,
                "description": section.description,
                "subject_name": section.subject.name,
                "section_name": section.name,
            }
        )

    # Поиск по файлам материалов
    file_query = select(MaterialFile).join(Section).join(Subject)

    if subject_filter:
        file_query = file_query.filter(Subject.name.ilike(f"%{subject_filter}%"))
    if section_filter:
        file_query = file_query.filter(Section.section_id == section_filter)

    file_query = file_query.filter(
        or_(
            MaterialFile.title.ilike(f"%{query}%"),
            MaterialFile.author.ilike(f"%{query}%"),
        )
    )
    files_result = await db.execute(file_query)
    files = files_result.scalars().all()

    for file in files:
        results.append(
            {
                "type": "file",
                "id": file.file_id,
                "title": file.title,
                "description": f"Автор: {file.author}, Размер: {file.file_size}",
                "subject_name": file.section.subject.name,
                "section_name": file.section.name,
            }
        )

    return results


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
