from typing import List, Optional
from fastapi import HTTPException, status
from app.database import get_db
from app.database.models.assessment import Question
from app.database.models.academic import Topic

# ===========================================
# EXISTING QUESTION OPERATIONS (Updated)
# ===========================================

def add_question_db(topic_id: int, text: str, correct_answers: int,
                   answer_1: Optional[str] = None, answer_2: Optional[str] = None,
                   answer_3: Optional[str] = None, answer_4: Optional[str] = None,
                   explanation: Optional[str] = None, category: Optional[List] = None) -> Question:
    """Добавление нового вопроса"""
    with next(get_db()) as db:
        # Проверяем, что тема существует
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
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
            category=category or []
        )
        db.add(new_q)
        db.commit()
        db.refresh(new_q)
        return new_q

def delete_question_db(question_id: int) -> dict:
    """Удаление вопроса"""
    with next(get_db()) as db:
        q = db.query(Question).filter_by(question_id=question_id).first()
        if not q:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вопрос не найден"
            )
        db.delete(q)
        db.commit()
        return {"status": "Удалён"}

def find_question_db(question_id: int) -> Question:
    """Поиск вопроса по ID"""
    with next(get_db()) as db:
        q = db.query(Question).filter_by(question_id=question_id).first()
        if not q:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вопрос не найден"
            )
        return q

def edit_question_db(question_id: int, topic_id: Optional[int] = None, text: Optional[str] = None,
                    correct_answers: Optional[int] = None, answer_1: Optional[str] = None,
                    answer_2: Optional[str] = None, answer_3: Optional[str] = None,
                    answer_4: Optional[str] = None, explanation: Optional[str] = None,
                    category: Optional[List] = None) -> Question:
    """Редактирование вопроса"""
    with next(get_db()) as db:
        q = db.query(Question).filter_by(question_id=question_id).first()
        if not q:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вопрос не найден"
            )
        
        if topic_id is not None:
            # Проверяем, что новая тема существует
            topic = db.query(Topic).filter_by(topic_id=topic_id).first()
            if not topic:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Тема не найдена"
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
            
        db.commit()
        db.refresh(q)
        return q

# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================

def get_questions_by_topic_db(topic_id: int) -> List[Question]:
    """Получение всех вопросов по теме"""
    with next(get_db()) as db:
        # Проверяем, что тема существует
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        
        questions = db.query(Question).filter_by(topic_id=topic_id).all()
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Вопросы для темы {topic_id} не найдены"
            )
        
        return questions

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_all_questions_db() -> List[Question]:
    """Получение всех вопросов"""
    with next(get_db()) as db:
        questions = db.query(Question).all()
        return questions

def get_questions_count_by_topic_db(topic_id: int) -> int:
    """Получение количества вопросов по теме"""
    with next(get_db()) as db:
        # Проверяем, что тема существует
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        
        return db.query(Question).filter_by(topic_id=topic_id).count()

def get_questions_by_category_db(category: str) -> List[Question]:
    """Получение вопросов по категории"""
    with next(get_db()) as db:
        # Поиск вопросов, где category содержит указанную категорию
        questions = db.query(Question).filter(
            Question.category.contains([category])
        ).all()
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Вопросы с категорией '{category}' не найдены"
            )
        
        return questions

def search_questions_by_text_db(search_text: str) -> List[Question]:
    """Поиск вопросов по тексту"""
    with next(get_db()) as db:
        questions = db.query(Question).filter(
            Question.text.ilike(f"%{search_text}%")
        ).all()
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Вопросы, содержащие '{search_text}', не найдены"
            )
        
        return questions

def get_questions_without_explanation_db() -> List[Question]:
    """Получение вопросов без объяснения"""
    with next(get_db()) as db:
        questions = db.query(Question).filter(
            Question.explanation.is_(None)
        ).all()
        return questions

def add_explanation_to_question_db(question_id: int, explanation: str) -> Question:
    """Добавление объяснения к вопросу"""
    with next(get_db()) as db:
        question = db.query(Question).filter_by(question_id=question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вопрос не найден"
            )
        
        question.explanation = explanation
        db.commit()
        db.refresh(question)
        return question

def remove_explanation_from_question_db(question_id: int) -> Question:
    """Удаление объяснения у вопроса"""
    with next(get_db()) as db:
        question = db.query(Question).filter_by(question_id=question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вопрос не найден"
            )
        
        question.explanation = None
        db.commit()
        db.refresh(question)
        return question

def update_question_category_db(question_id: int, category: List) -> Question:
    """Обновление категории вопроса"""
    with next(get_db()) as db:
        question = db.query(Question).filter_by(question_id=question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вопрос не найден"
            )
        
        question.category = category
        db.commit()
        db.refresh(question)
        return question