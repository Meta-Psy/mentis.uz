from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# Импорты базы данных и моделей
from app.database import get_db
from app.database.models.assessment import TopicTest, Question
from app.database.models.academic import Topic, Block, Section, Subject, TestType

# Импорты сервисов
from app.services.assessment.grade_service import (
    add_topic_test_db,
    get_all_topic_scores_by_topic_db,
    get_avg_topic_score_for_student_db
)
from app.services.content.question_service import (
    get_questions_by_topic_db,
)
from app.services.content.test_service import (
    get_random_questions_by_topic_db,
    get_questions_count_by_topic_db
)
from app.services.content.topic_service import (
    find_topic_db,
    get_topics_by_block_db,
    get_all_topics_db
)
from app.services.content.section_service import (
    get_sections_by_subject_db,
    get_all_sections_db
)
from app.services.content.subject_service import (
    get_all_subjects_db,
)
from app.services.auth.student_service import (
    get_student_by_id_db
)

# Импорты схем (из нашего файла schemas)
from app.schemas.assessment.tests import (
    TestInfo,
    TestSession,
    TestResult,
    TestsListResponse,
    TestSessionResponse,
    TestResultResponse,
    TestStatistics,
    TestCounts,
    CreateTestSessionRequest,
    SubmitAnswerRequest,
    FinishTestRequest,
    QuestionResponse,
    TestAttempt,
    TestsHealthResponse
)

# Создание роутера
router = APIRouter()

# Временное хранилище активных сессий (в продакшене использовать Redis)
active_sessions: Dict[str, Dict[str, Any]] = {}

# ===========================================
# ПОЛУЧЕНИЕ СПИСКА ТЕСТОВ СТУДЕНТА
# ===========================================

@router.get("/student/{student_id}", 
            response_model=TestsListResponse,
            summary="Получить тесты студента",
            description="Получение всех тестов студента с фильтрацией и статистикой")
async def get_student_tests(
    student_id: int = Path(..., gt=0, description="ID студента"),
    subject_name: Optional[str] = Query(None, description="Фильтр по предмету"),
    section_id: Optional[int] = Query(None, gt=0, description="Фильтр по разделу"),
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу"),
    limit: int = Query(50, le=200, description="Лимит результатов"),
    db: AsyncSession = Depends(get_db)
) -> TestsListResponse:
    """Получение списка тестов студента"""
    
    try:
        # Проверяем существование студента
        student = await get_student_by_id_db(db, student_id)
        
        # Получаем все предметы
        subjects = await get_all_subjects_db(db)
        subject_filter = None
        
        if subject_name:
            # Нормализуем название предмета
            normalized_subject = subject_name.lower()
            if normalized_subject in ['chemistry', 'химия']:
                subject_filter = next((s for s in subjects if 'химия' in s.name.lower()), None)
            elif normalized_subject in ['biology', 'биология']:
                subject_filter = next((s for s in subjects if 'биология' in s.name.lower()), None)
        
        tests = []
        
        # Получаем разделы
        if subject_filter:
            sections = await get_sections_by_subject_db(db, subject_filter.subject_id)
        else:
            sections = await get_all_sections_db(db)
        
        # Фильтруем по section_id если указан
        if section_id:
            sections = [s for s in sections if s.section_id == section_id]
        
        # Собираем тесты по темам
        for section in sections[:limit]:
            try:
                # Получаем блоки раздела
                from sqlalchemy import select
                
                blocks_result = await db.execute(
                    select(Block).filter(Block.section_id == section.section_id)
                )
                blocks = blocks_result.scalars().all()
                
                for block in blocks:
                    topics = await get_topics_by_block_db(db, block.block_id)
                    
                    for topic in topics:
                        # Получаем статистику по теме
                        questions_count = await get_questions_count_by_topic_db(db, topic.topic_id)
                        
                        if questions_count == 0:
                            continue
                        
                        # Получаем попытки студента по теме
                        try:
                            from sqlalchemy import select
                            topic_tests_result = await db.execute(
                                select(TopicTest).filter(
                                    TopicTest.student_id == student_id,
                                    TopicTest.topic_id == topic.topic_id
                                )
                            )
                            topic_tests = topic_tests_result.scalars().all()
                            
                            training_attempts = [
                                TestAttempt(
                                    attempt_id=test.topic_test_id,
                                    score_percentage=(test.correct_answers / test.question_count) * 100 if test.question_count > 0 else 0,
                                    correct_answers=test.correct_answers,
                                    total_questions=test.question_count,
                                    attempt_date=test.attempt_date,
                                    time_spent=test.time_spent,
                                    passed=test.correct_answers >= (test.question_count * 0.6) if test.question_count > 0 else False
                                ) for test in topic_tests
                            ]
                            
                        except Exception:
                            training_attempts = []
                        
                        # Определяем статус теста
                        status = "available"
                        if training_attempts:
                            best_score = max(att.score_percentage for att in training_attempts)
                            if best_score >= 60:
                                status = "completed"
                            else:
                                status = "current"
                        else:
                            status = "current"
                        
                        # Фильтруем по статусу
                        if status_filter and status != status_filter:
                            continue
                        
                        test_info = TestInfo(
                            topic_id=topic.topic_id,
                            topic_name=topic.name,
                            section_id=section.section_id,
                            section_name=section.name,
                            subject_id=section.subject_id,
                            subject_name=section.subject.name,
                            block_id=block.block_id,
                            block_name=block.name,
                            status=status,
                            training_attempts=training_attempts,
                            questions_count=questions_count
                        )
                        
                        tests.append(test_info)
                        
                        if len(tests) >= limit:
                            break
                    
                    if len(tests) >= limit:
                        break
                        
            except Exception:
                continue
        
        # Подсчитываем статистику
        completed_count = len([t for t in tests if t.status == "completed"])
        current_count = len([t for t in tests if t.status == "current"])
        overdue_count = len([t for t in tests if t.status == "overdue"])
        
        # Получаем общую статистику студента
        from sqlalchemy import select, func
        total_tests_result = await db.execute(
            select(func.count(TopicTest.topic_test_id))
            .filter(TopicTest.student_id == student_id)
        )
        total_completed = total_tests_result.scalar() or 0
        
        avg_score_result = await db.execute(
            select(func.avg(TopicTest.correct_answers / TopicTest.question_count * 100))
            .filter(TopicTest.student_id == student_id, TopicTest.question_count > 0)
        )
        avg_score = avg_score_result.scalar() or 0.0
        
        statistics = TestStatistics(
            student_id=student_id,
            completed_tests=total_completed,
            current_tests=current_count,
            overdue_tests=overdue_count,
            total_tests=len(tests),
            average_score=float(avg_score) if avg_score else 0.0,
            total_time_spent_hours=total_completed * 0.5
        )
        
        test_counts = TestCounts(
            completed=completed_count,
            current=current_count,
            overdue=overdue_count,
            available=len(tests)
        )
        
        return TestsListResponse(
            tests=tests[:limit],
            total_count=len(tests),
            statistics=statistics,
            test_counts=test_counts
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения тестов: {str(e)}"
        )

# ===========================================
# СОЗДАНИЕ СЕССИИ ТЕСТИРОВАНИЯ
# ===========================================

@router.post("/session", 
             response_model=TestSessionResponse,
             summary="Создать сессию тестирования",
             description="Создание новой сессии для прохождения теста")
async def create_test_session(
    request: CreateTestSessionRequest,
    db: AsyncSession = Depends(get_db)
) -> TestSessionResponse:
    """Создание сессии тестирования"""
    
    try:
        # Проверяем существование темы
        topic = await find_topic_db(db, request.topic_id)
        
        # Получаем вопросы по теме
        questions = await get_random_questions_by_topic_db(
            db, 
            request.topic_id, 
            limit=request.questions_limit
        )
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Нет доступных вопросов для данной темы"
            )
        
        # Создаем сессию
        session_id = str(uuid.uuid4())
        
        # Конвертируем вопросы в нужный формат
        question_responses = [
            QuestionResponse(
                question_id=q.question_id,
                text=q.text,
                answer_1=q.answer_1,
                answer_2=q.answer_2,
                answer_3=q.answer_3,
                answer_4=q.answer_4,
                correct_answers=q.correct_answers,
                explanation=q.explanation,
                category=q.category or [],
                topic_id=q.topic_id
            ) for q in questions
        ]
        
        # Определяем лимит времени
        time_limit = None
        if request.test_type == "final":
            time_limit = 45  # 45 минут для экзамена
        
        session = TestSession(
            session_id=session_id,
            topic_id=request.topic_id,
            test_type=request.test_type,
            questions=question_responses,
            current_question=0,
            start_time=datetime.now(),
            time_limit_minutes=time_limit,
            is_active=True
        )
        
        # Сохраняем сессию в памяти
        active_sessions[session_id] = {
            "session": session,
            "answers": {},
            "start_time": datetime.now()
        }
        
        return TestSessionResponse(
            session=session,
            current_question=question_responses[0] if question_responses else None,
            progress={
                "current": 0,
                "total": len(question_responses),
                "percentage": 0
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания сессии: {str(e)}"
        )

# ===========================================
# ПОЛУЧЕНИЕ ТЕКУЩЕГО ВОПРОСА
# ===========================================

@router.get("/session/{session_id}/question", 
            response_model=QuestionResponse,
            summary="Получить текущий вопрос",
            description="Получение текущего вопроса в сессии")
async def get_current_question(
    session_id: str = Path(..., description="ID сессии")
) -> QuestionResponse:
    """Получение текущего вопроса"""
    
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )
    
    session_data = active_sessions[session_id]
    session = session_data["session"]
    
    if not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сессия завершена"
        )
    
    if session.current_question >= len(session.questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Все вопросы пройдены"
        )
    
    return session.questions[session.current_question]

# ===========================================
# ОТПРАВКА ОТВЕТА
# ===========================================

@router.post("/session/{session_id}/answer",
             summary="Отправить ответ",
             description="Отправка ответа на вопрос")
async def submit_answer(
    session_id: str = Path(..., description="ID сессии"),
    request: SubmitAnswerRequest = ...,
) -> Dict[str, Any]:
    """Отправка ответа на вопрос"""
    
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )
    
    session_data = active_sessions[session_id]
    session = session_data["session"]
    
    if not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сессия завершена"
        )
    
    # Сохраняем ответ
    session_data["answers"][request.question_id] = request.answer_choice
    
    # Переходим к следующему вопросу
    session.current_question += 1
    
    is_finished = session.current_question >= len(session.questions)
    
    return {
        "status": "success",
        "question_answered": request.question_id,
        "current_question": session.current_question,
        "total_questions": len(session.questions),
        "is_finished": is_finished,
        "progress_percentage": (session.current_question / len(session.questions)) * 100
    }

# ===========================================
# ЗАВЕРШЕНИЕ ТЕСТА
# ===========================================

@router.post("/session/{session_id}/finish", 
             response_model=TestResultResponse,
             summary="Завершить тест",
             description="Завершение теста и получение результатов")
async def finish_test(
    session_id: str = Path(..., description="ID сессии"),
    request: FinishTestRequest = ...,
    db: AsyncSession = Depends(get_db)
) -> TestResultResponse:
    """Завершение теста"""
    
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )
    
    session_data = active_sessions[session_id]
    session = session_data["session"]
    
    try:
        # Обновляем ответы из запроса
        session_data["answers"].update(request.answers)
        
        # Подсчитываем результаты
        correct_count = 0
        total_questions = len(session.questions)
        detailed_results = []
        
        for question in session.questions:
            user_answer = session_data["answers"].get(question.question_id, 0)
            is_correct = user_answer == question.correct_answers
            
            if is_correct:
                correct_count += 1
            
            detailed_results.append({
                "question_id": question.question_id,
                "question_text": question.text,
                "user_answer": user_answer,
                "correct_answer": question.correct_answers,
                "is_correct": is_correct,
                "explanation": question.explanation
            })
        
        # Рассчитываем время
        end_time = datetime.now()
        time_spent = int((end_time - session.start_time).total_seconds())
        score_percentage = (correct_count / total_questions) * 100
        passed = score_percentage >= 60  # 60% проходной балл
        
        # Создаем результат
        result = TestResult(
            session_id=session_id,
            topic_id=session.topic_id,
            test_type=session.test_type,
            score_percentage=score_percentage,
            correct_answers=correct_count,
            total_questions=total_questions,
            time_spent_seconds=time_spent,
            passed=passed,
            answers=session_data["answers"]
        )
        
        # Сохраняем результат в базу данных для тренировочных тестов
        try:
            if session.test_type == "training":
                # TODO: получить student_id из контекста аутентификации
                student_id = 1  # Временно используем 1, нужно получить из JWT токена
                await add_topic_test_db(
                    db=db,
                    student_id=student_id,
                    topic_id=session.topic_id,
                    question_count=total_questions,
                    correct_answers=float(correct_count),
                    attempt_date=end_time,
                    time_spent=f"{time_spent}s"
                )
        except Exception as save_error:
            # Логируем ошибку, но не прерываем выполнение
            print(f"Ошибка сохранения результата: {save_error}")
        
        # Формируем рекомендации
        recommendations = []
        if score_percentage < 40:
            recommendations.append("Рекомендуем повторить теоретический материал")
        elif score_percentage < 60:
            recommendations.append("Неплохой результат, но есть возможности для улучшения")
        elif score_percentage < 80:
            recommendations.append("Хороший результат! Продолжайте в том же духе")
        else:
            recommendations.append("Отличный результат! Вы хорошо усвоили материал")
        
        # Завершаем сессию
        session.is_active = False
        session.end_time = end_time
        
        return TestResultResponse(
            result=result,
            detailed_results=detailed_results,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка завершения теста: {str(e)}"
        )
    finally:
        # Помечаем сессию как неактивную
        if session_id in active_sessions:
            active_sessions[session_id]["session"].is_active = False

# ===========================================
# ПОЛУЧЕНИЕ СТАТИСТИКИ СТУДЕНТА
# ===========================================

@router.get("/student/{student_id}/statistics", 
            response_model=TestStatistics,
            summary="Получить статистику студента",
            description="Получение детальной статистики тестов студента")
async def get_student_statistics(
    student_id: int = Path(..., gt=0, description="ID студента"),
    db: AsyncSession = Depends(get_db)
) -> TestStatistics:
    """Получение статистики тестов студента"""
    
    try:
        # Проверяем существование студента
        student = await get_student_by_id_db(db, student_id)
        
        # Получаем статистику тестов
        from sqlalchemy import select, func
        
        total_tests_result = await db.execute(
            select(func.count(TopicTest.topic_test_id))
            .filter(TopicTest.student_id == student_id)
        )
        total_tests = total_tests_result.scalar() or 0
        
        # Средний балл
        avg_score_result = await db.execute(
            select(func.avg(TopicTest.correct_answers / TopicTest.question_count * 100))
            .filter(TopicTest.student_id == student_id, TopicTest.question_count > 0)
        )
        avg_score = avg_score_result.scalar() or 0.0
        
        statistics = TestStatistics(
            student_id=student_id,
            completed_tests=total_tests,
            current_tests=0,
            overdue_tests=0,
            total_tests=total_tests,
            average_score=float(avg_score) if avg_score else 0.0,
            total_time_spent_hours=total_tests * 0.5
        )
        
        return statistics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики: {str(e)}"
        )

# ===========================================
# ПОЛУЧЕНИЕ ВОПРОСОВ ПО ТЕМЕ
# ===========================================

@router.get("/topic/{topic_id}/questions",
            response_model=List[QuestionResponse],
            summary="Получить вопросы по теме",
            description="Получение всех вопросов по конкретной теме")
async def get_topic_questions(
    topic_id: int = Path(..., gt=0, description="ID темы"),
    limit: int = Query(30, le=100, description="Лимит вопросов"),
    random: bool = Query(False, description="Случайная выборка"),
    db: AsyncSession = Depends(get_db)
) -> List[QuestionResponse]:
    """Получение вопросов по теме"""
    
    try:
        # Проверяем существование темы
        await find_topic_db(db, topic_id)
        
        if random:
            questions = await get_random_questions_by_topic_db(db, topic_id, limit)
        else:
            all_questions = await get_questions_by_topic_db(db, topic_id)
            questions = all_questions[:limit]
        
        return [
            QuestionResponse(
                question_id=q.question_id,
                text=q.text,
                answer_1=q.answer_1,
                answer_2=q.answer_2,
                answer_3=q.answer_3,
                answer_4=q.answer_4,
                correct_answers=q.correct_answers,
                explanation=q.explanation,
                category=q.category or [],
                topic_id=q.topic_id
            ) for q in questions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения вопросов: {str(e)}"
        )

# ===========================================
# ПРОВЕРКА ЗДОРОВЬЯ API
# ===========================================

@router.get("/health",
            response_model=TestsHealthResponse,
            summary="Проверка здоровья API",
            description="Проверка работоспособности API тестирования")
async def health_check() -> TestsHealthResponse:
    """Проверка здоровья API тестирования"""
    
    active_count = len([s for s in active_sessions.values() if s["session"].is_active])
    
    return TestsHealthResponse(
        status="healthy",
        service="tests-api",
        version="1.0.0",
        timestamp=datetime.now(),
        active_sessions=active_count
    )

# ===========================================
# ПОЛУЧЕНИЕ АКТИВНЫХ СЕССИЙ
# ===========================================

@router.get("/sessions/active",
            summary="Получить активные сессии",
            description="Получение списка активных сессий тестирования")
async def get_active_sessions() -> Dict[str, Any]:
    """Получение активных сессий"""
    
    active_count = len([s for s in active_sessions.values() if s["session"].is_active])
    total_count = len(active_sessions)
    
    return {
        "active_sessions": active_count,
        "total_sessions": total_count,
        "sessions": [
            {
                "session_id": session_id,
                "topic_id": data["session"].topic_id,
                "test_type": data["session"].test_type,
                "is_active": data["session"].is_active,
                "start_time": data["session"].start_time,
                "current_question": data["session"].current_question,
                "total_questions": len(data["session"].questions)
            }
            for session_id, data in active_sessions.items()
        ]
    }

# ===========================================
# УДАЛЕНИЕ СЕССИИ
# ===========================================

@router.delete("/session/{session_id}",
               summary="Удалить сессию",
               description="Принудительное удаление сессии тестирования")
async def delete_session(
    session_id: str = Path(..., description="ID сессии")
) -> Dict[str, str]:
    """Удаление сессии"""
    
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )
    
    del active_sessions[session_id]
    
    return {"status": "success", "message": "Сессия удалена"}

# ===========================================
# ПОЛУЧЕНИЕ РЕЗУЛЬТАТА ТЕСТА
# ===========================================

@router.get("/result/{session_id}", 
            response_model=TestResultResponse,
            summary="Получить результат теста",
            description="Получение результата завершенного теста")
async def get_test_result(
    session_id: str = Path(..., description="ID сессии")
) -> TestResultResponse:
    """Получение результата теста"""
    
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результат теста не найден"
        )
    
    session_data = active_sessions[session_id]
    session = session_data["session"]
    
    if session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тест еще не завершен"
        )
    
    # Пересчитываем результаты
    correct_count = 0
    total_questions = len(session.questions)
    detailed_results = []
    
    for question in session.questions:
        user_answer = session_data["answers"].get(question.question_id, 0)
        is_correct = user_answer == question.correct_answers
        
        if is_correct:
            correct_count += 1
        
        detailed_results.append({
            "question_id": question.question_id,
            "question_text": question.text,
            "user_answer": user_answer,
            "correct_answer": question.correct_answers,
            "is_correct": is_correct,
            "explanation": question.explanation
        })
    
    # Рассчитываем время
    time_spent = int((session.end_time - session.start_time).total_seconds()) if session.end_time else 0
    score_percentage = (correct_count / total_questions) * 100
    passed = score_percentage >= 60
    
    result = TestResult(
        session_id=session_id,
        topic_id=session.topic_id,
        test_type=session.test_type,
        score_percentage=score_percentage,
        correct_answers=correct_count,
        total_questions=total_questions,
        time_spent_seconds=time_spent,
        passed=passed,
        answers=session_data["answers"]
    )
    
    return TestResultResponse(
        result=result,
        detailed_results=detailed_results,
        recommendations=[]
    )