from typing import List, Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.academic import (
    Topic,
    Block,
    SectionMaterial,
    MaterialFileType,
    MaterialFile,
    TestType,
    Section,
    TopicTestMapping,
    Subject,
)

# ===========================================
# EXISTING TOPIC OPERATIONS (Updated)
# ===========================================


async def add_topic_db(
    db: AsyncSession,
    block_id: int,
    name: str,
    homework: Optional[str] = None,
    number: Optional[int] = None,
    additional_material: Optional[str] = None,
) -> Topic:
    """Добавление новой темы"""
    # Проверяем, что блок существует
    block_result = await db.execute(select(Block).filter(Block.block_id == block_id))
    block = block_result.scalar_one_or_none()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Блок не найден"
        )

    new_topic = Topic(
        block_id=block_id,
        name=name,
        homework=homework,
        number=number,
        additional_material=additional_material,
    )
    db.add(new_topic)
    await db.commit()
    await db.refresh(new_topic)
    return new_topic


async def delete_topic_db(db: AsyncSession, topic_id: int) -> dict:
    """Удаление темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    top = result.scalar_one_or_none()
    if not top:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    await db.delete(top)
    await db.commit()
    return {"status": "Удалена"}


async def find_topic_db(db: AsyncSession, topic_id: int) -> Topic:
    """Поиск темы по ID"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    top = result.scalar_one_or_none()
    if not top:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    return top


async def edit_topic_db(
    db: AsyncSession,
    topic_id: int,
    block_id: Optional[int] = None,
    name: Optional[str] = None,
    homework: Optional[str] = None,
    number: Optional[int] = None,
    additional_material: Optional[str] = None,
) -> Topic:
    """Редактирование темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    top = result.scalar_one_or_none()
    if not top:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    if block_id is not None:
        # Проверяем, что новый блок существует
        block_result = await db.execute(
            select(Block).filter(Block.block_id == block_id)
        )
        block = block_result.scalar_one_or_none()
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Блок не найден"
            )
        top.block_id = block_id
    if name is not None:
        top.name = name
    if homework is not None:
        top.homework = homework
    if number is not None:
        top.number = number
    if additional_material is not None:
        top.additional_material = additional_material

    await db.commit()
    await db.refresh(top)
    return top


# ===========================================
# HOMEWORK OPERATIONS
# ===========================================


async def add_homework_db(db: AsyncSession, topic_id: int, homework: str) -> Topic:
    """Добавление домашнего задания к теме"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.homework = homework
    await db.commit()
    await db.refresh(topic)
    return topic


async def delete_homework_db(db: AsyncSession, topic_id: int) -> Topic:
    """Удаление домашнего задания у темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.homework = None
    await db.commit()
    await db.refresh(topic)
    return topic


async def edit_homework_db(db: AsyncSession, topic_id: int, homework: str) -> Topic:
    """Редактирование домашнего задания"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.homework = homework
    await db.commit()
    await db.refresh(topic)
    return topic


# ===========================================
# TOPIC NUMBER OPERATIONS
# ===========================================


async def add_topic_number_db(db: AsyncSession, topic_id: int, number: int) -> Topic:
    """Добавление номера к теме"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.number = number
    await db.commit()
    await db.refresh(topic)
    return topic


async def delete_topic_number_db(db: AsyncSession, topic_id: int) -> Topic:
    """Удаление номера у темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.number = None
    await db.commit()
    await db.refresh(topic)
    return topic


async def edit_topic_number_db(db: AsyncSession, topic_id: int, number: int) -> Topic:
    """Редактирование номера темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.number = number
    await db.commit()
    await db.refresh(topic)
    return topic


# ===========================================
# ADDITIONAL MATERIAL OPERATIONS
# ===========================================


async def add_additional_material_db(
    db: AsyncSession, topic_id: int, additional_material: str
) -> Topic:
    """Добавление дополнительного материала к теме"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.additional_material = additional_material
    await db.commit()
    await db.refresh(topic)
    return topic


async def delete_additional_material_db(db: AsyncSession, topic_id: int) -> Topic:
    """Удаление дополнительного материала у темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.additional_material = None
    await db.commit()
    await db.refresh(topic)
    return topic


async def edit_additional_material_db(
    db: AsyncSession, topic_id: int, additional_material: str
) -> Topic:
    """Редактирование дополнительного материала"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.additional_material = additional_material
    await db.commit()
    await db.refresh(topic)
    return topic


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_topics_by_block_db(db: AsyncSession, block_id: int) -> List[Topic]:
    """Получение всех тем по блоку"""

    # Проверяем, что блок существует
    block_result = await db.execute(select(Block).filter(Block.block_id == block_id))
    block = block_result.scalar_one_or_none()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Блок не найден"
        )

    result = await db.execute(
        select(Topic).filter(Topic.block_id == block_id).order_by(Topic.number)
    )
    topics = result.scalars().all()

    if not topics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Темы для блока {block_id} не найдены",
        )

    return topics


async def get_topic_materials_db(db: AsyncSession, topic_id: int) -> dict:
    """Получение всех материалов по теме"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    # Получаем материалы раздела, к которому относится тема
    section_materials_result = await db.execute(
        select(SectionMaterial).filter(
            SectionMaterial.section_id == topic.block.section_id
        )
    )
    section_materials = section_materials_result.scalars().all()

    return {
        "topic_id": topic_id,
        "topic_name": topic.name,
        "homework": topic.homework,
        "additional_material": topic.additional_material,
        "section_materials": [
            {
                "section_material_id": material.section_material_id,
                "material_links": material.material_links,
            }
            for material in section_materials
        ],
    }


async def get_next_topic_db(db: AsyncSession, current_topic_id: int) -> Optional[Topic]:
    """Получение следующей темы"""

    current_topic_result = await db.execute(
        select(Topic).filter(Topic.topic_id == current_topic_id)
    )
    current_topic = current_topic_result.scalar_one_or_none()
    if not current_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Текущая тема не найдена"
        )

    # Ищем следующую тему в том же блоке
    if current_topic.number is not None:
        next_topic_result = await db.execute(
            select(Topic)
            .filter(
                Topic.block_id == current_topic.block_id,
                Topic.number > current_topic.number,
            )
            .order_by(Topic.number)
            .limit(1)
        )
        next_topic = next_topic_result.scalar_one_or_none()
    else:
        # Если у текущей темы нет номера, ищем по topic_id
        next_topic_result = await db.execute(
            select(Topic)
            .filter(
                Topic.block_id == current_topic.block_id,
                Topic.topic_id > current_topic.topic_id,
            )
            .order_by(Topic.topic_id)
            .limit(1)
        )
        next_topic = next_topic_result.scalar_one_or_none()

    return next_topic


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_all_topics_db(db: AsyncSession) -> List[Topic]:
    """Получение всех тем"""

    result = await db.execute(select(Topic).order_by(Topic.block_id, Topic.number))
    topics = result.scalars().all()
    return topics


async def get_topics_with_homework_db(db: AsyncSession) -> List[Topic]:
    """Получение тем с домашними заданиями"""

    result = await db.execute(select(Topic).filter(Topic.homework.isnot(None)))
    topics = result.scalars().all()
    return topics


async def get_topics_without_homework_db(db: AsyncSession) -> List[Topic]:
    """Получение тем без домашних заданий"""

    result = await db.execute(select(Topic).filter(Topic.homework.is_(None)))
    topics = result.scalars().all()
    return topics


async def get_previous_topic_db(
    db: AsyncSession, current_topic_id: int
) -> Optional[Topic]:
    """Получение предыдущей темы"""

    current_topic_result = await db.execute(
        select(Topic).filter(Topic.topic_id == current_topic_id)
    )
    current_topic = current_topic_result.scalar_one_or_none()
    if not current_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Текущая тема не найдена"
        )

    # Ищем предыдущую тему в том же блоке
    if current_topic.number is not None:
        prev_topic_result = await db.execute(
            select(Topic)
            .filter(
                Topic.block_id == current_topic.block_id,
                Topic.number < current_topic.number,
            )
            .order_by(Topic.number.desc())
            .limit(1)
        )
        prev_topic = prev_topic_result.scalar_one_or_none()
    else:
        # Если у текущей темы нет номера, ищем по topic_id
        prev_topic_result = await db.execute(
            select(Topic)
            .filter(
                Topic.block_id == current_topic.block_id,
                Topic.topic_id < current_topic.topic_id,
            )
            .order_by(Topic.topic_id.desc())
            .limit(1)
        )
        prev_topic = prev_topic_result.scalar_one_or_none()

    return prev_topic


async def get_first_topic_in_block_db(
    db: AsyncSession, block_id: int
) -> Optional[Topic]:
    """Получение первой темы в блоке"""

    result = await db.execute(
        select(Topic).filter(Topic.block_id == block_id).order_by(Topic.number).limit(1)
    )
    topic = result.scalar_one_or_none()
    return topic


async def get_last_topic_in_block_db(
    db: AsyncSession, block_id: int
) -> Optional[Topic]:
    """Получение последней темы в блоке"""

    result = await db.execute(
        select(Topic)
        .filter(Topic.block_id == block_id)
        .order_by(Topic.number.desc())
        .limit(1)
    )
    topic = result.scalar_one_or_none()
    return topic


async def search_topics_by_name_db(db: AsyncSession, search_name: str) -> List[Topic]:
    """Поиск тем по названию"""

    result = await db.execute(
        select(Topic)
        .filter(Topic.name.ilike(f"%{search_name}%"))
        .order_by(Topic.block_id, Topic.number)
    )
    topics = result.scalars().all()

    if not topics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Темы с названием, содержащим '{search_name}', не найдены",
        )

    return topics


async def get_topics_count_by_block_db(db: AsyncSession, block_id: int) -> int:
    """Получение количества тем в блоке"""

    result = await db.execute(
        select(func.count(Topic.topic_id)).filter(Topic.block_id == block_id)
    )
    return result.scalar()


async def add_material_file_db(
    db: AsyncSession,
    section_id: int,
    file_type: MaterialFileType,
    title: str,
    author: str,
    file_size: str,
    file_format: str = "PDF",
    download_url: Optional[str] = None,
) -> MaterialFile:
    """Добавление файла материала к разделу"""

    # Проверяем существование раздела
    section_result = await db.execute(
        select(Section).filter(Section.section_id == section_id)
    )
    section = section_result.scalar_one_or_none()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )

    material_file = MaterialFile(
        section_id=section_id,
        file_type=file_type,
        title=title,
        author=author,
        file_size=file_size,
        file_format=file_format,
        download_url=download_url,
    )

    db.add(material_file)
    await db.commit()
    await db.refresh(material_file)
    return material_file


async def get_material_files_by_section_db(
    db: AsyncSession, section_id: int
) -> Dict[str, List[MaterialFile]]:
    """Получение всех файлов материалов раздела, сгруппированных по типу"""
    result = await db.execute(
        select(MaterialFile).filter(MaterialFile.section_id == section_id)
    )
    files = result.scalars().all()

    result_dict = {"books": [], "test_books": []}

    for file in files:
        if file.file_type == MaterialFileType.BOOK:
            result_dict["books"].append(file)
        elif file.file_type == MaterialFileType.TEST_BOOK:
            result_dict["test_books"].append(file)

    return result_dict


async def update_material_file_db(
    db: AsyncSession,
    file_id: int,
    title: Optional[str] = None,
    author: Optional[str] = None,
    file_size: Optional[str] = None,
    file_format: Optional[str] = None,
    download_url: Optional[str] = None,
) -> MaterialFile:
    """Обновление файла материала"""

    result = await db.execute(
        select(MaterialFile).filter(MaterialFile.file_id == file_id)
    )
    material_file = result.scalar_one_or_none()
    if not material_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Файл материала не найден"
        )

    if title is not None:
        material_file.title = title
    if author is not None:
        material_file.author = author
    if file_size is not None:
        material_file.file_size = file_size
    if file_format is not None:
        material_file.file_format = file_format
    if download_url is not None:
        material_file.download_url = download_url

    await db.commit()
    await db.refresh(material_file)
    return material_file


async def delete_material_file_db(db: AsyncSession, file_id: int) -> dict:
    """Удаление файла материала"""

    result = await db.execute(
        select(MaterialFile).filter(MaterialFile.file_id == file_id)
    )
    material_file = result.scalar_one_or_none()
    if not material_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Файл материала не найден"
        )

    await db.delete(material_file)
    await db.commit()
    return {"status": "Удален"}


async def add_topic_test_mapping_db(
    db: AsyncSession,
    topic_id: int,
    test_id: int,
    test_type: TestType = TestType.TRAINING,
) -> TopicTestMapping:
    """Создание связи темы с тестом"""

    # Проверяем существование темы
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = topic_result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    # Проверяем, не существует ли уже такая связь
    existing_result = await db.execute(
        select(TopicTestMapping).filter(
            TopicTestMapping.topic_id == topic_id, TopicTestMapping.test_id == test_id
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Связь темы с тестом уже существует",
        )

    mapping = TopicTestMapping(topic_id=topic_id, test_id=test_id, test_type=test_type)

    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    return mapping


async def get_topic_tests_db(db: AsyncSession, topic_id: int) -> List[TopicTestMapping]:
    """Получение всех тестов для темы"""

    result = await db.execute(
        select(TopicTestMapping).filter(TopicTestMapping.topic_id == topic_id)
    )
    return result.scalars().all()


async def get_test_id_for_topic_db(
    db: AsyncSession, topic_id: int, test_type: TestType = TestType.TRAINING
) -> Optional[int]:
    """Получение ID теста для темы"""

    result = await db.execute(
        select(TopicTestMapping).filter(
            TopicTestMapping.topic_id == topic_id,
            TopicTestMapping.test_type == test_type,
        )
    )
    mapping = result.scalar_one_or_none()
    return mapping.test_id if mapping else None


async def update_topic_video_url_db(
    db: AsyncSession, topic_id: int, video_url: str
) -> Topic:
    """Обновление URL видео для темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    topic.video_url = video_url
    await db.commit()
    await db.refresh(topic)
    return topic


async def get_topic_with_details_db(db: AsyncSession, topic_id: int) -> dict:
    """Получение темы с полной детализацией"""

    # Используем представление для получения данных
    from app.database.models.academic import TopicDetailsView

    result = await db.execute(
        select(TopicDetailsView).filter(TopicDetailsView.topic_id == topic_id)
    )
    topic_view = result.scalar_one_or_none()
    if not topic_view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    # Получаем тесты для темы
    tests = await get_topic_tests_db(db, topic_id)

    return {
        "topic_id": topic_view.topic_id,
        "title": topic_view.topic_name,
        "homework": topic_view.homework.split("\n") if topic_view.homework else [],
        "number": topic_view.topic_number,
        "additional_material": topic_view.additional_material,
        "video_url": topic_view.video_url
        or "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "block_name": topic_view.block_name,
        "section_name": topic_view.section_name,
        "section_id": topic_view.section_id,
        "subject_name": topic_view.subject_name,
        "subject_id": topic_view.subject_id,
        "questions_count": topic_view.questions_count or 0,
        "tests_count": topic_view.tests_count or 0,
        "test_id": tests[0].test_id if tests else topic_view.topic_id + 100,
        "tests": [
            {"test_id": test.test_id, "test_type": test.test_type.value}
            for test in tests
        ],
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
