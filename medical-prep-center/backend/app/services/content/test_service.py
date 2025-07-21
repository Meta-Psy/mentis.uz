from sqlalchemy import func
from typing import List, Dict
from app.database.models.assessment import Question
from app.database.models.academic import Topic, Block, Section, Subject, Moduls
from app.database import get_db

# ===========================================
# EXISTING TEST FUNCTIONS (from test_service)
# ===========================================

def get_random_questions_by_topic(topic_id: int, limit: int = 30) -> List[Question]:
    """Получить случайные вопросы по определенной теме"""
    with next(get_db()) as db:
        questions = (
            db.query(Question)
            .filter(Question.topic_id == topic_id)
            .order_by(func.rand())
            .limit(limit)
            .all()
        )
        return questions

def get_random_questions_by_block(block_id: int, limit: int = 30) -> List[Question]:
    """Получить случайные вопросы по определенному блоку"""
    with next(get_db()) as db:
        questions = (
            db.query(Question)
            .join(Topic, Question.topic_id == Topic.topic_id)
            .filter(Topic.block_id == block_id)
            .order_by(func.rand())
            .limit(limit)
            .all()
        )
        return questions

def get_random_questions_by_modul(modul_id: int, limit_per_subject: int = 30) -> Dict[str, List[Question]]:
    """Получить случайные вопросы по модулю (по 30 на химию и биологию)"""
    with next(get_db()) as db:
        # Получаем информацию о модуле
        modul = db.query(Moduls).filter(Moduls.modul_id == modul_id).first()
        if not modul:
            return {"chemistry": [], "biology": []}

        # Получаем вопросы по химии
        chemistry_questions = (
            db.query(Question)
            .join(Topic, Question.topic_id == Topic.topic_id)
            .join(Block, Topic.block_id == Block.block_id)
            .join(Section, Block.section_id == Section.section_id)
            .join(Subject, Section.subject_id == Subject.subject_id)
            .filter(
                Subject.name.ilike('%химия%'),
                Topic.topic_id >= modul.start_topic_chem,
                Topic.topic_id <= modul.end_topic_chem
            )
            .order_by(func.rand())
            .limit(limit_per_subject)
            .all()
        )

        # Получаем вопросы по биологии
        biology_questions = (
            db.query(Question)
            .join(Topic, Question.topic_id == Topic.topic_id)
            .join(Block, Topic.block_id == Block.block_id)
            .join(Section, Block.section_id == Section.section_id)
            .join(Subject, Section.subject_id == Subject.subject_id)
            .filter(
                Subject.name.ilike('%биология%'),
                Topic.topic_id >= modul.start_topic_bio,
                Topic.topic_id <= modul.end_topic_bio
            )
            .order_by(func.rand())
            .limit(limit_per_subject)
            .all()
        )

        return {
            "chemistry": chemistry_questions,
            "biology": biology_questions
        }

def get_random_questions_by_section(section_id: int, limit: int = 30) -> List[Question]:
    """Получить случайные вопросы по определенному разделу"""
    with next(get_db()) as db:
        questions = (
            db.query(Question)
            .join(Topic, Question.topic_id == Topic.topic_id)
            .join(Block, Topic.block_id == Block.block_id)
            .filter(Block.section_id == section_id)
            .order_by(func.rand())
            .limit(limit)
            .all()
        )
        return questions

def get_random_questions_by_subject(subject_id: int, limit: int = 30) -> List[Question]:
    """Получить случайные вопросы по определенному предмету"""
    with next(get_db()) as db:
        questions = (
            db.query(Question)
            .join(Topic, Question.topic_id == Topic.topic_id)
            .join(Block, Topic.block_id == Block.block_id)
            .join(Section, Block.section_id == Section.section_id)
            .filter(Section.subject_id == subject_id)
            .order_by(func.rand())
            .limit(limit)
            .all()
        )
        return questions

def get_questions_count_by_topic(topic_id: int) -> int:
    """Получить количество вопросов по теме"""
    with next(get_db()) as db:
        count = db.query(Question).filter(Question.topic_id == topic_id).count()
        return count

def get_questions_count_by_block(block_id: int) -> int:
    """Получить количество вопросов по блоку"""
    with next(get_db()) as db:
        count = (
            db.query(Question)
            .join(Topic, Question.topic_id == Topic.topic_id)
            .filter(Topic.block_id == block_id)
            .count()
        )
        return count

def get_questions_count_by_section(section_id: int) -> int:
    """Получить количество вопросов по разделу"""
    with next(get_db()) as db:
        count = (
            db.query(Question)
            .join(Topic, Question.topic_id == Topic.topic_id)
            .join(Block, Topic.block_id == Block.block_id)
            .filter(Block.section_id == section_id)
            .count()
        )
        return count

def get_questions_count_by_subject(subject_id: int) -> int:
    """Получить количество вопросов по предмету"""
    with next(get_db()) as db:
        count = (
            db.query(Question)
            .join(Topic, Question.topic_id == Topic.topic_id)
            .join(Block, Topic.block_id == Block.block_id)
            .join(Section, Block.section_id == Section.section_id)
            .filter(Section.subject_id == subject_id)
            .count()
        )
        return count

# ===========================================
# ADDITIONAL HELPER FUNCTIONS
# ===========================================

def get_questions_by_difficulty_db(difficulty_level: str, limit: int = 30) -> List[Question]:
    """Получить вопросы по уровню сложности (через категории)"""
    with next(get_db()) as db:
        questions = (
            db.query(Question)
            .filter(Question.category.contains([difficulty_level]))
            .order_by(func.rand())
            .limit(limit)
            .all()
        )
        return questions

def get_questions_statistics_db() -> Dict[str, int]:
    """Получить статистику вопросов"""
    with next(get_db()) as db:
        total_questions = db.query(Question).count()
        questions_with_explanation = db.query(Question).filter(Question.explanation.isnot(None)).count()
        questions_without_explanation = total_questions - questions_with_explanation
        
        return {
            "total_questions": total_questions,
            "questions_with_explanation": questions_with_explanation,
            "questions_without_explanation": questions_without_explanation
        }

def get_questions_by_multiple_topics_db(topic_ids: List[int], limit: int = 30) -> List[Question]:
    """Получить случайные вопросы по нескольким темам"""
    with next(get_db()) as db:
        questions = (
            db.query(Question)
            .filter(Question.topic_id.in_(topic_ids))
            .order_by(func.rand())
            .limit(limit)
            .all()
        )
        return questions

def get_questions_by_category_and_topic_db(topic_id: int, category: str, limit: int = 30) -> List[Question]:
    """Получить вопросы по теме и категории"""
    with next(get_db()) as db:
        questions = (
            db.query(Question)
            .filter(
                Question.topic_id == topic_id,
                Question.category.contains([category])
            )
            .order_by(func.rand())
            .limit(limit)
            .all()
        )
        return questions

def get_mixed_questions_db(chemistry_count: int = 15, biology_count: int = 15) -> Dict[str, List[Question]]:
    """Получить смешанные вопросы по химии и биологии"""
    with next(get_db()) as db:
        # Получаем вопросы по химии
        chemistry_questions = (
            db.query(Question)
            .join(Topic, Question.topic_id == Topic.topic_id)
            .join(Block, Topic.block_id == Block.block_id)
            .join(Section, Block.section_id == Section.section_id)
            .join(Subject, Section.subject_id == Subject.subject_id)
            .filter(Subject.name.ilike('%химия%'))
            .order_by(func.rand())
            .limit(chemistry_count)
            .all()
        )

        # Получаем вопросы по биологии
        biology_questions = (
            db.query(Question)
            .join(Topic, Question.topic_id == Topic.topic_id)
            .join(Block, Topic.block_id == Block.block_id)
            .join(Section, Block.section_id == Section.section_id)
            .join(Subject, Section.subject_id == Subject.subject_id)
            .filter(Subject.name.ilike('%биология%'))
            .order_by(func.rand())
            .limit(biology_count)
            .all()
        )

        return {
            "chemistry": chemistry_questions,
            "biology": biology_questions,
            "mixed": chemistry_questions + biology_questions
        }

def validate_test_parameters_db(topic_id: int = None, block_id: int = None,
                               section_id: int = None, subject_id: int = None,
                               modul_id: int = None) -> Dict[str, bool]:
    """Проверить корректность параметров для создания теста"""
    with next(get_db()) as db:
        result = {}
        
        if topic_id:
            result['topic_exists'] = db.query(Topic).filter_by(topic_id=topic_id).first() is not None
            
        if block_id:
            result['block_exists'] = db.query(Block).filter_by(block_id=block_id).first() is not None
            
        if section_id:
            result['section_exists'] = db.query(Section).filter_by(section_id=section_id).first() is not None
            
        if subject_id:
            result['subject_exists'] = db.query(Subject).filter_by(subject_id=subject_id).first() is not None
            
        if modul_id:
            result['modul_exists'] = db.query(Moduls).filter_by(modul_id=modul_id).first() is not None
            
        return result