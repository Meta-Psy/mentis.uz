from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.auth.student_service import *
from app.services.assessment.grade_service import *
from app.services.assessment.attendance_service import *
from app.services.assessment.comment_service import *
from app.schemas.auth.parent import *
from app.core.dependencies import get_current_user, require_roles
from app.database.models.user import UserRole

router = APIRouter()

# ===== ОСНОВНОЙ ДАШБОРД =====

@router.get("/dashboard", response_model=ParentDashboardResponse)
async def get_parent_dashboard(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение главной страницы родителя с обзором ребенка"""
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только родителям"
        )
    
    try:
        # Получаем информацию о студенте (ребенке)
        # Предполагаем, что есть связь родитель-студент
        student_id = get_student_id_by_parent_id(current_user.user_id)
        student = get_student_by_id_db(student_id)
        
        # Получаем статистику по всем разделам
        performance_stats = get_performance_summary(student_id)
        discipline_stats = get_discipline_summary(student_id)
        exam_stats = get_exam_summary(student_id)
        dtm_stats = get_dtm_summary(student_id)
        
        return ParentDashboardResponse(
            student_info=student,
            performance=performance_stats,
            discipline=discipline_stats,
            exams=exam_stats,
            dtm_progress=dtm_stats,
            university_admission_chance=90  # Вычисляется на основе всех данных
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def get_performance_summary(student_id: int):
    """Вспомогательная функция для получения сводки по успеваемости"""
    # Логика вычисления статуса (отлично/хорошо/плохо) на основе оценок
    return {
        "status": "хорошо",
        "chemistry": {
            "polls": {"current": 8, "total": 10},
            "tests": {"current": 7, "total": 10},
            "control_works": {"current": 10, "total": 10}
        },
        "biology": {
            "polls": {"current": 7, "total": 10},
            "tests": {"current": 8, "total": 10},
            "control_works": {"current": 8, "total": 10}
        }
    }

def get_discipline_summary(student_id: int):
    """Вспомогательная функция для получения сводки по дисциплине"""
    return {
        "status": "плохо",
        "missed_lessons": {"current": 10, "total": 30},
        "missed_homework": {"current": 12, "total": 30},
        "missed_polls": {"current": 15, "total": 30},
        "teacher_remarks": 2
    }

def get_exam_summary(student_id: int):
    """Вспомогательная функция для получения сводки по экзаменам"""
    return {
        "status": "отлично",
        "monthly_exam_last": {"score": 160, "max_score": 189},
        "final_control_last": {"score": 10, "max_score": 10},
        "intermediate_control_last": None
    }

def get_dtm_summary(student_id: int):
    """Вспомогательная функция для получения сводки по ДТМ"""
    return {
        "current_score": 180.1,
        "max_possible": 189,
        "required_score": 151.9,
        "admission_chance": 90
    }

# ===== ДЕТАЛИЗИРОВАННАЯ СТАТИСТИКА =====

@router.get("/statistics/detailed")
async def get_detailed_statistics(
    current_user = Depends(get_current_user)
):
    """Получение детализированной статистики (для страницы ParentStatistics)"""
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только родителям"
        )
    
    # Заглушка согласно frontend структуре ParentStatistics
    return {
        "currentStudent": {
            "id": 1,
            "name": "Иванов Алексей Игоревич",
            "group": 3
        },
        "grades": {
            "chemistry": {
                "current_grades": [
                    {"month": "сент.", "value": 7.5},
                    {"month": "окт.", "value": 8.2},
                    {"month": "нояб.", "value": 8.8},
                    {"month": "дек.", "value": 9.1}
                ],
                "tests": [
                    {"month": "сент.", "value": 6.8},
                    {"month": "окт.", "value": 7.5},
                    {"month": "нояб.", "value": 8.0}
                ],
                "dtm": [
                    {"month": "сент.", "value": 25},
                    {"month": "окт.", "value": 22},
                    {"month": "нояб.", "value": 28}
                ]
            },
            "biology": {
                "current_grades": [
                    {"month": "сент.", "value": 6.8},
                    {"month": "окт.", "value": 7.3},
                    {"month": "нояб.", "value": 7.9}
                ],
                "tests": [
                    {"month": "сент.", "value": 6.2},
                    {"month": "окт.", "value": 6.8},
                    {"month": "нояб.", "value": 7.2}
                ],
                "dtm": [
                    {"month": "сент.", "value": 25},
                    {"month": "окт.", "value": 22},
                    {"month": "нояб.", "value": 28}
                ]
            }
        },
        "allStudents": [
            {
                "id": 1,
                "name": "Иванов Алексей Игоревич",
                "group": 3,
                "chemistry": 9.4,
                "biology": 8.8,
                "chemistryDTM": 22,
                "biologyDTM": 22,
                "generalDTM": 25
            }
            # Остальные студенты для турнирных таблиц
        ]
    }

# ===== ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ПО ПРЕДМЕТАМ =====

@router.get("/details/{subject}")
async def get_subject_details(
    subject: str,
    module_filter: Optional[str] = Query("all"),
    current_user = Depends(get_current_user)
):
    """Получение детальной информации по предмету (для страницы ParentDetails)"""
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только родителям"
        )
    
    student_id = get_student_id_by_parent_id(current_user.user_id)
    
    if subject not in ["chemistry", "biology"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный предмет. Используйте 'chemistry' или 'biology'"
        )
    
    # Получаем данные посещаемости
    attendance_data = get_attendance_calendar_data(student_id, subject, module_filter)
    
    # Получаем данные успеваемости
    performance_data = get_performance_table_data(student_id, subject, module_filter)
    
    return {
        "attendance": attendance_data,
        "performance": performance_data,
        "final_grades": {
            "average_control": 10,
            "final_control": 9.2,
            "total_grade": 9.6
        }
    }

def get_attendance_calendar_data(student_id: int, subject: str, module_filter: str):
    """Получение данных календаря посещаемости"""
    # Заглушка согласно структуре ParentDetails
    return {
        "module1": {
            "months": [
                {
                    "name": "Сентябрь 2024",
                    "days": [
                        {
                            "date": 2,
                            "status": "present",
                            "lesson": "Введение в органическую химию"
                        },
                        {
                            "date": 4,
                            "status": "late",
                            "lesson": "Углеводороды"
                        },
                        {
                            "date": 6,
                            "status": "absent",
                            "lesson": "Алканы и их свойства"
                        }
                    ]
                }
            ]
        }
    }

def get_performance_table_data(student_id: int, subject: str, module_filter: str):
    """Получение данных таблицы успеваемости"""
    # Заглушка согласно структуре ParentDetails
    return {
        "module1": {
            "topics": [
                {
                    "number": 1,
                    "listened": True,
                    "firstTry": 8,
                    "secondTry": None,
                    "average": 8
                },
                {
                    "number": 2,
                    "listened": True,
                    "firstTry": None,
                    "secondTry": 7,
                    "average": 7
                }
            ]
        }
    }

# ===== РЕКОМЕНДАЦИИ =====

@router.get("/recommendations")
async def get_parent_recommendations(
    current_user = Depends(get_current_user)
):
    """Получение рекомендаций для родителей (для страницы ParentRecommendations)"""
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только родителям"
        )
    
    student_id = get_student_id_by_parent_id(current_user.user_id)
    
    # Анализируем все аспекты успеваемости и генерируем рекомендации
    discipline_analysis = analyze_discipline(student_id)
    performance_analysis = analyze_performance(student_id)
    exam_analysis = analyze_exams(student_id)
    dtm_analysis = analyze_dtm_progress(student_id)
    
    return {
        "sections": [
            {
                "id": "discipline",
                "name": "Дисциплина",
                "status": discipline_analysis["status"],
                "data": {
                    "currentState": discipline_analysis["current_state"],
                    "goals": discipline_analysis["goals"],
                    "recommendations": discipline_analysis["recommendations"]
                }
            },
            {
                "id": "performance",
                "name": "Успеваемость", 
                "status": performance_analysis["status"],
                "data": {
                    "currentState": performance_analysis["current_state"],
                    "goals": performance_analysis["goals"],
                    "recommendations": performance_analysis["recommendations"]
                }
            },
            {
                "id": "exams",
                "name": "Экзамены",
                "status": exam_analysis["status"],
                "data": {
                    "currentState": exam_analysis["current_state"],
                    "goals": exam_analysis["goals"],
                    "recommendations": exam_analysis["recommendations"]
                }
            },
            {
                "id": "dtm",
                "name": "ДТМ/Поступление",
                "status": dtm_analysis["status"],
                "data": {
                    "currentState": dtm_analysis["current_state"],
                    "goals": dtm_analysis["goals"],
                    "recommendations": dtm_analysis["recommendations"]
                }
            }
        ],
        "summary": generate_summary_recommendations(
            discipline_analysis, performance_analysis, exam_analysis, dtm_analysis
        )
    }

def analyze_discipline(student_id: int):
    """Анализ дисциплины студента"""
    # Получаем статистику посещаемости и выполнения заданий
    missed_lessons = count_missed_lessons_db(student_id)
    # Добавить функции для подсчета невыполненных заданий
    
    if missed_lessons > 8:
        status = "плохо"
    elif missed_lessons > 4:
        status = "хорошо"
    else:
        status = "отлично"
    
    return {
        "status": status,
        "current_state": f"В настоящее время наблюдается значительное количество пропусков занятий ({missed_lessons} из 30)...",
        "goals": "Цель - сократить количество пропусков до минимума...",
        "recommendations": "Рекомендуется ежедневно контролировать выполнение домашних заданий..."
    }

def analyze_performance(student_id: int):
    """Анализ успеваемости студента"""
    # Получаем средние оценки по предметам
    chemistry_avg = get_average_grade_by_subject(student_id, "chemistry")
    biology_avg = get_average_grade_by_subject(student_id, "biology")
    
    overall_avg = (chemistry_avg + biology_avg) / 2
    
    if overall_avg >= 9:
        status = "отлично"
    elif overall_avg >= 7:
        status = "хорошо" 
    else:
        status = "плохо"
    
    return {
        "status": status,
        "current_state": f"По химии показывает результаты {chemistry_avg:.1f}, по биологии {biology_avg:.1f}...",
        "goals": "Цель - достичь стабильно высоких результатов по обеим дисциплинам...",
        "recommendations": "Увеличить время на изучение биологии, использовать интерактивные методы..."
    }

def analyze_exams(student_id: int):
    """Анализ результатов экзаменов"""
    # Получаем последние результаты экзаменов
    latest_exam_score = get_latest_exam_score(student_id)
    
    if latest_exam_score >= 85:
        status = "отлично"
    elif latest_exam_score >= 70:
        status = "хорошо"
    else:
        status = "плохо"
    
    return {
        "status": status,
        "current_state": f"Результаты ежемесячных экзаменов показывают {latest_exam_score} баллов...",
        "goals": "Цель - поддержать и улучшить текущий уровень...",
        "recommendations": "Продолжать регулярную подготовку к экзаменам..."
    }

def analyze_dtm_progress(student_id: int):
    """Анализ прогресса ДТМ"""
    current_dtm_score = get_current_dtm_score(student_id)
    required_score = get_required_dtm_score(student_id)
    
    if current_dtm_score >= required_score + 20:
        status = "отлично"
    elif current_dtm_score >= required_score:
        status = "хорошо"
    else:
        status = "плохо"
    
    return {
        "status": status,
        "current_state": f"Текущий балл составляет {current_dtm_score} из 189...",
        "goals": "Цель - стабилизировать результат на уровне 180+ баллов...",
        "recommendations": "Поддерживать текущий уровень подготовки..."
    }

def generate_summary_recommendations(discipline, performance, exams, dtm):
    """Генерация итоговых рекомендаций"""
    return "На основе комплексного анализа успеваемости вашего ребенка можно сделать вывод о хорошем уровне подготовки..."

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def get_student_id_by_parent_id(parent_id: int) -> int:
    """Получение ID студента по ID родителя"""
    # Здесь должна быть логика связи родитель-студент
    # Пока возвращаем заглушку
    return 1

def get_average_grade_by_subject(student_id: int, subject: str) -> float:
    """Получение средней оценки по предмету"""
    # Заглушка
    return 8.5

def get_latest_exam_score(student_id: int) -> float:
    """Получение последней оценки за экзамен"""
    # Заглушка
    return 160

def get_current_dtm_score(student_id: int) -> float:
    """Получение текущего балла ДТМ"""
    # Заглушка
    return 180.1

def get_required_dtm_score(student_id: int) -> float:
    """Получение необходимого балла ДТМ"""
    # Заглушка
    return 151.9