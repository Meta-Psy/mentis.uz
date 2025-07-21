from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict
from app.database import get_db
from app.services.content.test_service import *
from app.services.assessment.grade_service import *
from app.services.content.question_service import *
from app.schemas.assessment.tests import *
from app.core.dependencies import get_current_user
from app.database.models.user import UserRole
import json
import redis
from datetime import datetime

router = APIRouter()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# ===== ПОЛУЧЕНИЕ ТЕСТОВ =====

@router.get("/available", response_model=List[AvailableTestResponse])
async def get_available_tests(
    subject: Optional[str] = Query(None),
    test_type: Optional[str] = Query(None, regex="^(training|control|dtm)$"),
    current_user = Depends(get_current_user)
):
    """Получение доступных тестов для студента"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    # Здесь будет логика получения доступных тестов
    # На основе прогресса студента, завершенных тем и т.д.
    available_tests = []
    
    # Заглушка согласно frontend структуре
    mock_tests = [
        {
            "id": 1,
            "title": "Тема 21. Дыхательная система",
            "subject": "biology",
            "type": "training",
            "questions_count": 50,
            "estimated_time": 45,
            "topic_id": 21,
            "is_available": True,
            "required_topics": [19, 20]
        },
        {
            "id": 2,
            "title": "Тема 25. Нервная система человека",
            "subject": "biology", 
            "type": "training",
            "questions_count": 50,
            "estimated_time": 45,
            "topic_id": 25,
            "is_available": True,
            "required_topics": [21, 22, 23, 24]
        }
    ]
    
    return mock_tests

@router.get("/by-category")
async def get_tests_by_category(
    category: str = Query(..., regex="^(topic|block|section|module|dtm)$"),
    category_id: int = Query(...),
    limit: int = Query(30, le=50),
    current_user = Depends(get_current_user)
):
    """Получение тестов по категории (тема, блок, раздел, модуль, ДТМ)"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    try:
        if category == "topic":
            questions = get_random_questions_by_topic(category_id, limit)
        elif category == "block":
            questions = get_random_questions_by_block(category_id, limit)
        elif category == "section":
            questions = get_random_questions_by_section(category_id, limit)
        elif category == "module":
            questions = get_random_questions_by_modul(category_id, limit)
        elif category == "dtm":
            questions = get_mixed_questions_db(15, 15)  # По 15 химия/биология
            
        return {
            "category": category,
            "category_id": category_id,
            "questions": questions,
            "total_count": len(questions.get("mixed", questions)) if category == "dtm" else len(questions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== УПРАВЛЕНИЕ СЕССИЕЙ ТЕСТА =====

@router.post("/start", response_model=TestSessionResponse)
async def start_test_session(
    test_request: StartTestRequest,
    current_user = Depends(get_current_user)
):
    """Начало новой сессии теста"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    try:
        # Проверяем, нет ли уже активной сессии
        session_key = f"test_session:{current_user.user_id}:{test_request.test_id}"
        existing_session = redis_client.get(session_key)
        
        if existing_session:
            return json.loads(existing_session)
        
        # Получаем вопросы для теста
        if test_request.category == "topic":
            questions = get_random_questions_by_topic(test_request.category_id, test_request.questions_limit)
        elif test_request.category == "block":
            questions = get_random_questions_by_block(test_request.category_id, test_request.questions_limit)
        elif test_request.category == "section":
            questions = get_random_questions_by_section(test_request.category_id, test_request.questions_limit)
        elif test_request.category == "module":
            questions_data = get_random_questions_by_modul(test_request.category_id, test_request.questions_limit)
            questions = questions_data.get("mixed", [])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверная категория теста"
            )
        
        # Создаем сессию теста
        session_data = {
            "session_id": f"{current_user.user_id}_{test_request.test_id}_{datetime.now().timestamp()}",
            "student_id": current_user.user_id,
            "test_id": test_request.test_id,
            "category": test_request.category,
            "category_id": test_request.category_id,
            "questions": [
                {
                    "id": q.question_id,
                    "question": q.text,
                    "options": [
                        {"id": "A", "text": q.answer_1},
                        {"id": "B", "text": q.answer_2},
                        {"id": "C", "text": q.answer_3},
                        {"id": "D", "text": q.answer_4}
                    ]
                } for q in questions
            ],
            "answers": {},
            "start_time": datetime.now().isoformat(),
            "time_elapsed": 0,
            "is_completed": False
        }
        
        # Сохраняем в Redis на 2 часа
        redis_client.setex(session_key, 7200, json.dumps(session_data, default=str))
        
        return TestSessionResponse(**session_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/session/{test_id}", response_model=TestSessionResponse)
async def get_test_session(
    test_id: int,
    current_user = Depends(get_current_user)
):
    """Получение текущей сессии теста"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    session_key = f"test_session:{current_user.user_id}:{test_id}"
    session_data = redis_client.get(session_key)
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активная сессия теста не найдена"
        )
    
    return json.loads(session_data)

@router.put("/session/{test_id}/save-progress")
async def save_test_progress(
    test_id: int,
    progress_data: SaveProgressRequest,
    current_user = Depends(get_current_user)
):
    """Сохранение прогресса теста"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    session_key = f"test_session:{current_user.user_id}:{test_id}"
    session_data = redis_client.get(session_key)
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия теста не найдена"
        )
    
    session = json.loads(session_data)
    session["answers"] = progress_data.answers
    session["time_elapsed"] = progress_data.time_elapsed
    
    # Обновляем сессию в Redis
    redis_client.setex(session_key, 7200, json.dumps(session, default=str))
    
    return {"message": "Прогресс сохранен"}

@router.post("/session/{test_id}/submit", response_model=TestResultResponse)
async def submit_test(
    test_id: int,
    submission_data: SubmitTestRequest,
    current_user = Depends(get_current_user)
):
    """Отправка теста на проверку и получение результатов"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    try:
        session_key = f"test_session:{current_user.user_id}:{test_id}"
        session_data = redis_client.get(session_key)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сессия теста не найдена"
            )
        
        session = json.loads(session_data)
        
        # Получаем правильные ответы
        question_ids = [q["id"] for q in session["questions"]]
        correct_answers = get_correct_answers_for_questions(question_ids)
        
        # Проверяем ответы
        total_questions = len(session["questions"])
        correct_count = 0
        incorrect_questions = []
        
        for question in session["questions"]:
            question_id = question["id"]
            student_answer = submission_data.answers.get(str(question_id))
            correct_answer = correct_answers.get(question_id)
            
            if student_answer == correct_answer:
                correct_count += 1
            else:
                incorrect_questions.append({
                    "question_id": question_id,
                    "student_answer": student_answer,
                    "correct_answer": correct_answer
                })
        
        # Сохраняем результат в базу данных
        if session["category"] == "topic":
            saved_result = add_topic_test_db(
                student_id=current_user.user_id,
                topic_id=session["category_id"],
                question_count=total_questions,
                correct_answers=correct_count,
                attempt_date=datetime.now(),
                time_spent=f"{submission_data.time_elapsed} секунд"
            )
        elif session["category"] == "block":
            saved_result = add_block_exam_db(
                student_id=current_user.user_id,
                block_id=session["category_id"],
                subject_id=get_subject_by_block(session["category_id"]),
                correct_answers=correct_count,
                exam_date=datetime.now(),
                time_spent=f"{submission_data.time_elapsed} секунд",
                passed=correct_count >= (total_questions * 0.7)
            )
        
        # Получаем рейтинг студента
        ranking = calculate_student_ranking(current_user.user_id, correct_count, session["category"])
        
        # Удаляем сессию из Redis
        redis_client.delete(session_key)
        
        return TestResultResponse(
            test_id=test_id,
            student_id=current_user.user_id,
            total_questions=total_questions,
            correct_answers=correct_count,
            incorrect_answers=total_questions - correct_count,
            time_spent=submission_data.time_elapsed,
            percentage=round((correct_count / total_questions) * 100, 1),
            ranking=ranking,
            question_results=create_question_results(session["questions"], submission_data.answers, correct_answers)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== РЕЗУЛЬТАТЫ ТЕСТОВ =====

@router.get("/results/history", response_model=List[TestHistoryItem])
async def get_test_history(
    subject: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """Получение истории тестов студента"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    # Получаем историю из разных типов тестов
    topic_tests = get_student_topic_tests(current_user.user_id, subject, limit, offset)
    block_exams = get_student_block_exams(current_user.user_id, subject, limit, offset)
    section_exams = get_student_section_exams(current_user.user_id, subject, limit, offset)
    
    # Объединяем и сортируем по дате
    all_tests = combine_and_sort_test_history(topic_tests, block_exams, section_exams)
    
    return all_tests

@router.get("/results/{result_id}", response_model=DetailedTestResultResponse)
async def get_test_result_details(
    result_id: int,
    result_type: str = Query(..., regex="^(topic|block|section|module|dtm)$"),
    current_user = Depends(get_current_user)
):
    """Получение детальных результатов конкретного теста"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    try:
        # Получаем детали теста в зависимости от типа
        if result_type == "topic":
            test_result = get_topic_test_details(result_id, current_user.user_id)
        elif result_type == "block":
            test_result = get_block_exam_details(result_id, current_user.user_id)
        elif result_type == "section":
            test_result = get_section_exam_details(result_id, current_user.user_id)
        
        # Получаем рейтинг для этого теста
        ranking_data = get_test_ranking_data(result_id, result_type, current_user.user_id)
        
        return DetailedTestResultResponse(
            **test_result,
            ranking=ranking_data
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== РЕЙТИНГИ =====

@router.get("/rankings")
async def get_test_rankings(
    test_type: str = Query(..., regex="^(topic|block|section|overall)$"),
    period: str = Query("all", regex="^(week|month|semester|all)$"),
    current_user = Depends(get_current_user)
):
    """Получение рейтингов по тестам"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    try:
        rankings = calculate_rankings_by_type_and_period(test_type, period)
        student_position = get_student_position_in_ranking(current_user.user_id, rankings)
        
        return {
            "test_type": test_type,
            "period": period,
            "rankings": rankings,
            "student_position": student_position
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def get_correct_answers_for_questions(question_ids: List[int]) -> Dict[int, str]:
    """Получение правильных ответов для списка вопросов"""
    correct_answers = {}
    for question_id in question_ids:
        question = find_question_db(question_id)
        # Преобразуем номер правильного ответа в букву
        answer_map = {1: "A", 2: "B", 3: "C", 4: "D"}
        correct_answers[question_id] = answer_map.get(question.correct_answers, "A")
    return correct_answers

def calculate_student_ranking(student_id: int, score: int, category: str) -> Dict[str, int]:
    """Вычисление рейтинга студента"""
    # Заглушка
    return {"overall": 10, "group": 3}

def create_question_results(questions: List[Dict], student_answers: Dict, correct_answers: Dict) -> List[Dict]:
    """Создание детальных результатов по вопросам"""
    results = []
    for i, question in enumerate(questions):
        question_id = question["id"]
        student_answer = student_answers.get(str(question_id))
        correct_answer = correct_answers.get(question_id)
        
        results.append({
            "questionNumber": i + 1,
            "questionText": question["question"],
            "correctAnswer": correct_answer,
            "studentAnswer": student_answer,
            "isCorrect": student_answer == correct_answer,
            "options": {opt["id"]: opt["text"] for opt in question["options"]}
        })
    
    return results

def get_subject_by_block(block_id: int) -> int:
    """Получение ID предмета по ID блока"""
    # Заглушка
    return 1

def get_student_topic_tests(student_id: int, subject: Optional[str], limit: int, offset: int):
    """Получение тестов по темам для студента"""
    # Заглушка
    return []

def get_student_block_exams(student_id: int, subject: Optional[str], limit: int, offset: int):
    """Получение экзаменов по блокам для студента"""
    # Заглушка  
    return []

def get_student_section_exams(student_id: int, subject: Optional[str], limit: int, offset: int):
    """Получение экзаменов по разделам для студента"""
    # Заглушка
    return []

def combine_and_sort_test_history(topic_tests, block_exams, section_exams):
    """Объединение и сортировка истории тестов"""
    # Заглушка
    return []

def get_topic_test_details(result_id: int, student_id: int):
    """Получение деталей теста по теме"""
    # Заглушка
    return {}

def get_block_exam_details(result_id: int, student_id: int):
    """Получение деталей экзамена по блоку"""
    # Заглушка
    return {}

def get_section_exam_details(result_id: int, student_id: int):
    """Получение деталей экзамена по разделу"""
    # Заглушка
    return {}

def get_test_ranking_data(result_id: int, result_type: str, student_id: int):
    """Получение данных рейтинга для теста"""
    # Заглушка
    return {"overall": [], "group": []}

def calculate_rankings_by_type_and_period(test_type: str, period: str):
    """Вычисление рейтингов по типу и периоду"""
    # Заглушка
    return []

def get_student_position_in_ranking(student_id: int, rankings):
    """Получение позиции студента в рейтинге"""
    # Заглушка
    return {"overall": 10, "group": 3}