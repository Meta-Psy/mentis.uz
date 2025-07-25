from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models.assessment import Question
from app.database.models.academic import Topic

# ===========================================
# EXISTING QUESTION OPERATIONS (Updated)
# ===========================================


async def add_question_db(
    db: AsyncSession,
    topic_id: int,
    text: str,
    correct_answers: int,
    answer_1: Optional[str] = None,
    answer_2: Optional[str] = None,
    answer_3: Optional[str] = None,
    answer_4: Optional[str] = None,
    explanation: Optional[str] = None,
    category: Optional[List] = None,
) -> Question:
    """Добавление нового вопроса"""

    # Проверяем, что тема существует
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = topic_result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    new_q = Question(
        topic_id=topic_id,
        text=text,
        answer_1=answer_1,
        answer_2=answer_2,
        answer_3=answer_3,
        answer_4=answer_4,
        correct_answers=correct_answers,
        explanation=explanation,
        category=category or [],
    )
    db.add(new_q)
    await db.commit()
    await db.refresh(new_q)
    return new_q


async def delete_question_db(db: AsyncSession, question_id: int) -> dict:
    """Удаление вопроса"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )
    await db.delete(q)
    await db.commit()
    return {"status": "Удалён"}


async def find_question_db(db: AsyncSession, question_id: int) -> Question:
    """Поиск вопроса по ID"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )
    return q


async def edit_question_db(
    db: AsyncSession,
    question_id: int,
    topic_id: Optional[int] = None,
    text: Optional[str] = None,
    correct_answers: Optional[int] = None,
    answer_1: Optional[str] = None,
    answer_2: Optional[str] = None,
    answer_3: Optional[str] = None,
    answer_4: Optional[str] = None,
    explanation: Optional[str] = None,
    category: Optional[List] = None,
) -> Question:
    """Редактирование вопроса"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )

    if topic_id is not None:
        # Проверяем, что новая тема существует
        topic_result = await db.execute(
            select(Topic).filter(Topic.topic_id == topic_id)
        )
        topic = topic_result.scalar_one_or_none()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
            )
        q.topic_id = topic_id
    if text is not None:
        q.text = text
    if correct_answers is not None:
        q.correct_answers = correct_answers
    if answer_1 is not None:
        q.answer_1 = answer_1
    if answer_2 is not None:
        q.answer_2 = answer_2
    if answer_3 is not None:
        q.answer_3 = answer_3
    if answer_4 is not None:
        q.answer_4 = answer_4
    if explanation is not None:
        q.explanation = explanation
    if category is not None:
        q.category = category

    await db.commit()
    await db.refresh(q)
    return q


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_questions_by_topic_db(db: AsyncSession, topic_id: int) -> List[Question]:
    """Получение всех вопросов по теме"""

    # Проверяем, что тема существует
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = topic_result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    result = await db.execute(select(Question).filter(Question.topic_id == topic_id))
    questions = result.scalars().all()

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопросы для темы {topic_id} не найдены",
        )

    return questions


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_all_questions_db(db: AsyncSession) -> List[Question]:
    """Получение всех вопросов"""

    result = await db.execute(select(Question))
    questions = result.scalars().all()
    return questions


async def get_questions_count_by_topic_db(db: AsyncSession, topic_id: int) -> int:
    """Получение количества вопросов по теме"""

    # Проверяем, что тема существует
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = topic_result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    result = await db.execute(
        select(func.count(Question.question_id)).filter(Question.topic_id == topic_id)
    )
    return result.scalar()


async def get_questions_by_category_db(
    db: AsyncSession, category: str
) -> List[Question]:
    """Получение вопросов по категории"""

    # Поиск вопросов, где category содержит указанную категорию
    result = await db.execute(
        select(Question).filter(Question.category.contains([category]))
    )
    questions = result.scalars().all()

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопросы с категорией '{category}' не найдены",
        )

    return questions


async def search_questions_by_text_db(
    db: AsyncSession, search_text: str
) -> List[Question]:
    """Поиск вопросов по тексту"""

    result = await db.execute(
        select(Question).filter(Question.text.ilike(f"%{search_text}%"))
    )
    questions = result.scalars().all()

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопросы, содержащие '{search_text}', не найдены",
        )

    return questions


async def get_questions_without_explanation_db(db: AsyncSession) -> List[Question]:
    """Получение вопросов без объяснения"""

    result = await db.execute(select(Question).filter(Question.explanation.is_(None)))
    questions = result.scalars().all()
    return questions


async def add_explanation_to_question_db(
    db: AsyncSession, question_id: int, explanation: str
) -> Question:
    """Добавление объяснения к вопросу"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )

    question.explanation = explanation
    await db.commit()
    await db.refresh(question)
    return question


async def remove_explanation_from_question_db(
    db: AsyncSession, question_id: int
) -> Question:
    """Удаление объяснения у вопроса"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )

    question.explanation = None
    await db.commit()
    await db.refresh(question)
    return question


async def update_question_category_db(
    db: AsyncSession, question_id: int, category: List
) -> Question:
    """Обновление категории вопроса"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )

    question.category = category
    await db.commit()
    await db.refresh(question)
    return question
