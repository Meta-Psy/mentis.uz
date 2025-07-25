from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from app.database.models.assessment import Question
from app.database.models.academic import Topic, Block, Section, Subject, Moduls

# ===========================================
# EXISTING TEST FUNCTIONS (from test_service)
# ===========================================


async def get_random_questions_by_topic_db(
    db: AsyncSession, topic_id: int, limit: int = 30
) -> List[Question]:
    """Получить случайные вопросы по определенной теме"""

    result = await db.execute(
        select(Question)
        .filter(Question.topic_id == topic_id)
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_random_questions_by_block_db(
    db: AsyncSession, block_id: int, limit: int = 30
) -> List[Question]:
    """Получить случайные вопросы по определенному блоку"""

    result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .filter(Topic.block_id == block_id)
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_random_questions_by_modul_db(
    db: AsyncSession, modul_id: int, limit_per_subject: int = 30
) -> Dict[str, List[Question]]:
    """Получить случайные вопросы по модулю (по 30 на химию и биологию)"""

    # Получаем информацию о модуле
    modul_result = await db.execute(select(Moduls).filter(Moduls.modul_id == modul_id))
    modul = modul_result.scalar_one_or_none()
    if not modul:
        return {"chemistry": [], "biology": []}

    # Получаем вопросы по химии
    chemistry_result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .join(Subject, Section.subject_id == Subject.subject_id)
        .filter(
            Subject.name.ilike("%химия%"),
            Topic.topic_id >= modul.start_topic_chem,
            Topic.topic_id <= modul.end_topic_chem,
        )
        .order_by(func.random())
        .limit(limit_per_subject)
    )
    chemistry_questions = chemistry_result.scalars().all()

    # Получаем вопросы по биологии
    biology_result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .join(Subject, Section.subject_id == Subject.subject_id)
        .filter(
            Subject.name.ilike("%биология%"),
            Topic.topic_id >= modul.start_topic_bio,
            Topic.topic_id <= modul.end_topic_bio,
        )
        .order_by(func.random())
        .limit(limit_per_subject)
    )
    biology_questions = biology_result.scalars().all()

    return {"chemistry": chemistry_questions, "biology": biology_questions}


async def get_random_questions_by_section_db(
    db: AsyncSession, section_id: int, limit: int = 30
) -> List[Question]:
    """Получить случайные вопросы по определенному разделу"""

    result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .filter(Block.section_id == section_id)
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_random_questions_by_subject_db(
    db: AsyncSession, subject_id: int, limit: int = 30
) -> List[Question]:
    """Получить случайные вопросы по определенному предмету"""

    result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .filter(Section.subject_id == subject_id)
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_questions_count_by_topic_db(db: AsyncSession, topic_id: int) -> int:
    """Получить количество вопросов по теме"""

    result = await db.execute(
        select(func.count(Question.question_id)).filter(Question.topic_id == topic_id)
    )
    count = result.scalar()
    return count


async def get_questions_count_by_block_db(db: AsyncSession, block_id: int) -> int:
    """Получить количество вопросов по блоку"""

    result = await db.execute(
        select(func.count(Question.question_id))
        .join(Topic, Question.topic_id == Topic.topic_id)
        .filter(Topic.block_id == block_id)
    )
    count = result.scalar()
    return count


async def get_questions_count_by_section_db(db: AsyncSession, section_id: int) -> int:
    """Получить количество вопросов по разделу"""

    result = await db.execute(
        select(func.count(Question.question_id))
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .filter(Block.section_id == section_id)
    )
    count = result.scalar()
    return count


async def get_questions_count_by_subject_db(db: AsyncSession, subject_id: int) -> int:
    """Получить количество вопросов по предмету"""

    result = await db.execute(
        select(func.count(Question.question_id))
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .filter(Section.subject_id == subject_id)
    )
    count = result.scalar()
    return count


# ===========================================
# ADDITIONAL HELPER FUNCTIONS
# ===========================================


async def get_questions_by_difficulty_db(
    db: AsyncSession, difficulty_level: str, limit: int = 30
) -> List[Question]:
    """Получить вопросы по уровню сложности (через категории)"""

    result = await db.execute(
        select(Question)
        .filter(Question.category.contains([difficulty_level]))
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_questions_statistics_db(db: AsyncSession) -> Dict[str, int]:
    """Получить статистику вопросов"""

    total_questions_result = await db.execute(select(func.count(Question.question_id)))
    total_questions = total_questions_result.scalar()

    questions_with_explanation_result = await db.execute(
        select(func.count(Question.question_id)).filter(
            Question.explanation.isnot(None)
        )
    )
    questions_with_explanation = questions_with_explanation_result.scalar()

    questions_without_explanation = total_questions - questions_with_explanation

    return {
        "total_questions": total_questions,
        "questions_with_explanation": questions_with_explanation,
        "questions_without_explanation": questions_without_explanation,
    }


async def get_questions_by_multiple_topics_db(
    db: AsyncSession, topic_ids: List[int], limit: int = 30
) -> List[Question]:
    """Получить случайные вопросы по нескольким темам"""

    result = await db.execute(
        select(Question)
        .filter(Question.topic_id.in_(topic_ids))
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_questions_by_category_and_topic_db(
    db: AsyncSession, topic_id: int, category: str, limit: int = 30
) -> List[Question]:
    """Получить вопросы по теме и категории"""

    result = await db.execute(
        select(Question)
        .filter(Question.topic_id == topic_id, Question.category.contains([category]))
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_mixed_questions_db(
    db: AsyncSession, chemistry_count: int = 15, biology_count: int = 15
) -> Dict[str, List[Question]]:
    """Получить смешанные вопросы по химии и биологии"""

    # Получаем вопросы по химии
    chemistry_result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .join(Subject, Section.subject_id == Subject.subject_id)
        .filter(Subject.name.ilike("%химия%"))
        .order_by(func.random())
        .limit(chemistry_count)
    )
    chemistry_questions = chemistry_result.scalars().all()

    # Получаем вопросы по биологии
    biology_result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .join(Subject, Section.subject_id == Subject.subject_id)
        .filter(Subject.name.ilike("%биология%"))
        .order_by(func.random())
        .limit(biology_count)
    )
    biology_questions = biology_result.scalars().all()

    return {
        "chemistry": chemistry_questions,
        "biology": biology_questions,
        "mixed": chemistry_questions + biology_questions,
    }


async def validate_test_parameters_db(
    db: AsyncSession,
    topic_id: int = None,
    block_id: int = None,
    section_id: int = None,
    subject_id: int = None,
    modul_id: int = None,
) -> Dict[str, bool]:
    """Проверить корректность параметров для создания теста"""

    result = {}

    if topic_id:
        topic_result = await db.execute(
            select(Topic).filter(Topic.topic_id == topic_id)
        )
        result["topic_exists"] = topic_result.scalar_one_or_none() is not None

    if block_id:
        block_result = await db.execute(
            select(Block).filter(Block.block_id == block_id)
        )
        result["block_exists"] = block_result.scalar_one_or_none() is not None

    if section_id:
        section_result = await db.execute(
            select(Section).filter(Section.section_id == section_id)
        )
        result["section_exists"] = section_result.scalar_one_or_none() is not None

    if subject_id:
        subject_result = await db.execute(
            select(Subject).filter(Subject.subject_id == subject_id)
        )
        result["subject_exists"] = subject_result.scalar_one_or_none() is not None

    if modul_id:
        modul_result = await db.execute(
            select(Moduls).filter(Moduls.modul_id == modul_id)
        )
        result["modul_exists"] = modul_result.scalar_one_or_none() is not None

    return result
