from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.auth.student_service import *
from app.services.assessment.grade_service import *
from app.services.assessment.attendance_service import *
from app.services.assessment.comment_service import *
from app.schemas.auth.admin import *
from app.database import get_current_user
from app.database.models.user import UserRole
from app.schemas.base import StudentProfileResponse, StudentResponse, StudentUpdate, TestHistoryResponse, CommentResponse

router = APIRouter()

# ===== ПРОФИЛЬ СТУДЕНТА =====

@router.get("/profile", response_model=StudentProfileResponse)
async def get_student_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение профиля текущего студента"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    try:
        student = get_student_by_id_db(current_user.user_id)
        
        # Получаем дополнительную статистику
        overdue_tests = get_overdue_exams_db(current_user.user_id)
        upcoming_tests = get_upcoming_exams_db(current_user.user_id)
        
        # Считаем средние баллы (примерная логика)
        chemistry_avg = 8.7  # Заглушка, нужно будет вычислять из grade_service
        biology_avg = 8.3    # Заглушка
        attendance_rate = 90  # Заглушка
        
        return StudentProfileResponse(
            student_info=student,
            chemistry_average=chemistry_avg,
            biology_average=biology_avg,
            attendance_rate=attendance_rate,
            overdue_tests=overdue_tests,
            upcoming_tests=upcoming_tests
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/profile", response_model=StudentResponse)
async def update_student_profile(
    student_update: StudentUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление профиля студента"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    try:
        updated_student = update_student_db(
            current_user.user_id,
            direction=student_update.direction,
            goal=student_update.goal
        )
        return StudentResponse.from_orm(updated_student)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== ТЕСТЫ И ЭКЗАМЕНЫ =====

@router.get("/tests/history", response_model=List[TestHistoryResponse])
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
    
    # Здесь будет логика получения истории тестов из grade_service
    # Пока возвращаем заглушку
    return []

@router.get("/tests/current")
async def get_current_test_session(
    test_id: int,
    current_user = Depends(get_current_user)
):
    """Получение текущей сессии теста"""
    # Логика для получения активного теста
    # Проверяем, есть ли сохраненный прогресс
    pass

@router.post("/tests/{test_id}/start")
async def start_test(
    test_id: int,
    current_user = Depends(get_current_user)
):
    """Начало прохождения теста"""
    # Логика начала теста
    pass

@router.post("/tests/{test_id}/submit")
async def submit_test(
    test_id: int,
    answers: dict,
    current_user = Depends(get_current_user)
):
    """Отправка теста на проверку"""
    # Логика отправки теста
    pass

@router.post("/tests/{test_id}/save-progress")
async def save_test_progress(
    test_id: int,
    answers: dict,
    current_user = Depends(get_current_user)
):
    """Сохранение прогресса теста"""
    # Логика сохранения прогресса
    pass

# ===== СТАТИСТИКА И РЕЙТИНГИ =====

@router.get("/statistics/performance")
async def get_performance_statistics(
    subject: Optional[str] = Query(None),
    period: str = Query("month", regex="^(week|month|semester|year)$"),
    current_user = Depends(get_current_user)
):
    """Получение статистики успеваемости"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    # Заглушка согласно frontend структуре
    return {
        "grades": {
            "chemistry": {
                "current_grades": [
                    {"month": "сент.", "value": 7.5},
                    {"month": "окт.", "value": 8.2},
                    {"month": "нояб.", "value": 8.8}
                ],
                "tests": [
                    {"month": "сент.", "value": 6.8},
                    {"month": "окт.", "value": 7.5}
                ]
            }
        }
    }

@router.get("/rankings")
async def get_student_rankings(
    ranking_type: str = Query("overall", regex="^(overall|group|dtm_all_time|dtm_last_month)$"),
    current_user = Depends(get_current_user)
):
    """Получение рейтингов студента"""
    # Логика для получения рейтингов
    pass

# ===== ПОСЕЩАЕМОСТЬ =====

@router.get("/attendance")
async def get_attendance_record(
    subject_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    """Получение записей о посещаемости"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    try:
        if subject_id:
            attendance_records = get_attendance_by_student_and_subject_db(
                current_user.user_id, 
                subject_id
            )
        else:
            # Получить всю посещаемость студента
            attendance_records = []  # Нужно добавить функцию в сервис
        
        return attendance_records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== КОММЕНТАРИИ ОТ УЧИТЕЛЕЙ =====

@router.get("/comments", response_model=List[CommentResponse])
async def get_student_comments(
    comment_type: Optional[str] = Query(None, regex="^(positive|negative|neutral)$"),
    limit: int = Query(20, le=50),
    current_user = Depends(get_current_user)
):
    """Получение комментариев учителей"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    try:
        if comment_type:
            if comment_type == "positive":
                comments = get_positive_comments_by_student_db(current_user.user_id)
            elif comment_type == "negative":
                comments = get_negative_comments_by_student_db(current_user.user_id)
            else:
                comments = get_neutral_comments_by_student_db(current_user.user_id)
        else:
            comments = get_all_comments_by_student_db(current_user.user_id)
        
        return [CommentResponse.from_orm(comment) for comment in comments[:limit]]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )