from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.services.auth.student_service import *
from app.services.assessment.grade_service import *
from app.services.assessment.attendance_service import *
from app.services.assessment.comment_service import *
from app.schemas.content.dashboard import *
from app.core.dependencies import get_current_user
from app.database.models.user import UserRole
from datetime import datetime, timedelta

router = APIRouter()

# ===== СТУДЕНТСКИЙ ДАШБОРД =====

@router.get("/student", response_model=StudentDashboardResponse)
async def get_student_dashboard(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение дашборда студента"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только студентам"
        )
    
    try:
        student = get_student_by_id_db(current_user.user_id)
        
        # Получаем основную статистику
        chemistry_avg = calculate_subject_average(current_user.user_id, "chemistry")
        biology_avg = calculate_subject_average(current_user.user_id, "biology")
        attendance_rate = calculate_attendance_rate(current_user.user_id)
        completed_tests = count_completed_tests(current_user.user_id)
        upcoming_tests = count_upcoming_tests(current_user.user_id)
        
        # Получаем последние результаты тестов
        recent_tests = get_recent_test_results(current_user.user_id, limit=3)
        
        # Получаем прогресс по модулям
        module_progress = get_module_progress_data(current_user.user_id)
        
        # Получаем предстоящие задания
        upcoming_tasks = get_upcoming_tasks_data(current_user.user_id)
        
        return StudentDashboardResponse(
            student_info={
                "name": f"{student.user.name} {student.user.surname}",
                "group": f"Группа {student.group_id}",
                "subjects": ["Химия", "Биология"]
            },
            statistics={
                "average_score": round((chemistry_avg + biology_avg) / 2, 1),
                "chemistry_average": chemistry_avg,
                "biology_average": biology_avg,
                "attendance": attendance_rate,
                "completed_tests": completed_tests,
                "upcoming_tests": upcoming_tests
            },
            recent_tests=recent_tests,
            module_progress=module_progress,
            upcoming_tasks=upcoming_tasks
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def calculate_subject_average(student_id: int, subject: str) -> float:
    """Вычисление среднего балла по предмету"""
    # Заглушка - в реальности вычислять из grade_service
    if subject == "chemistry":
        return 8.4
    else:
        return 8.1

def calculate_attendance_rate(student_id: int) -> int:
    """Вычисление процента посещаемости"""
    try:
        stats = get_attendance_statistics_db(student_id)
        return int(stats["attendance_rate"])
    except:
        return 95

def count_completed_tests(student_id: int) -> int:
    """Подсчет количества выполненных тестов"""
    # Заглушка
    return 247

def count_upcoming_tests(student_id: int) -> int:
    """Подсчет предстоящих тестов"""
    # Заглушка
    return 3

def get_recent_test_results(student_id: int, limit: int = 3) -> List[Dict[str, Any]]:
    """Получение последних результатов тестов"""
    # Заглушка согласно frontend структуре
    return [
        {
            "subject": "Химия",
            "topic": "Органические соединения",
            "score": 92,
            "date": "2 часа назад",
            "status": "completed"
        },
        {
            "subject": "Биология",
            "topic": "Анатомия человека",
            "score": 85,
            "date": "1 день назад",
            "status": "completed"
        },
        {
            "subject": "Химия",
            "topic": "Неорганическая химия",
            "score": 78,
            "date": "2 дня назад",
            "status": "completed"
        }
    ]

def get_module_progress_data(student_id: int) -> List[Dict[str, Any]]:
    """Получение данных прогресса по модулям"""
    # Заглушка согласно frontend структуре
    return [
        {
            "subject": "Химия",
            "module": "Модуль 3",
            "progress": 75,
            "topics": 12,
            "completed": 9
        },
        {
            "subject": "Биология",
            "module": "Модуль 2",
            "progress": 90,
            "topics": 10,
            "completed": 9
        }
    ]

def get_upcoming_tasks_data(student_id: int) -> List[Dict[str, Any]]:
    """Получение предстоящих заданий"""
    # Заглушка согласно frontend структуре
    return [
        {
            "type": "test",
            "subject": "Биология",
            "topic": "Генетика",
            "deadline": "2 дня",
            "priority": "high"
        },
        {
            "type": "homework",
            "subject": "Химия",
            "topic": "Решение задач",
            "deadline": "4 дня",
            "priority": "medium"
        },
        {
            "type": "test",
            "subject": "Биология",
            "topic": "Экология",
            "deadline": "1 неделя",
            "priority": "low"
        }
    ]

# ===== УЧИТЕЛЬСКИЙ ДАШБОРД =====

@router.get("/teacher", response_model=TeacherDashboardResponse)
async def get_teacher_dashboard(
    current_user = Depends(get_current_user)
):
    """Получение дашборда учителя"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        teacher = get_teacher_by_id_db(current_user.user_id)
        
        # Получаем статистику учителя
        total_students = sum(len(get_students_by_group_db(group.group_id)) for group in teacher.groups)
        total_groups = len(teacher.groups)
        recent_comments = len(get_recent_comments_db(teacher_id=current_user.user_id, limit=10))
        
        # Получаем последнюю активность
        recent_activity = get_teacher_recent_activity(current_user.user_id)
        
        # Получаем статистику групп
        groups_statistics = get_teacher_groups_statistics(current_user.user_id)
        
        return TeacherDashboardResponse(
            teacher_info={
                "name": f"{teacher.user.name} {teacher.user.surname}",
                "subjects": [subject.name for subject in teacher.subjects],
                "groups_count": total_groups
            },
            statistics={
                "total_students": total_students,
                "total_groups": total_groups,
                "total_comments": recent_comments,
                "active_subjects": len(teacher.subjects)
            },
            recent_activity=recent_activity,
            groups_statistics=groups_statistics
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def get_teacher_recent_activity(teacher_id: int) -> List[Dict[str, Any]]:
    """Получение последней активности учителя"""
    return [
        {
            "type": "comment",
            "description": "Добавлен комментарий к студенту Иванов А.",
            "timestamp": "2 часа назад"
        },
        {
            "type": "attendance",
            "description": "Отмечена посещаемость группы 3",
            "timestamp": "4 часа назад"
        }
    ]

def get_teacher_groups_statistics(teacher_id: int) -> List[Dict[str, Any]]:
    """Получение статистики по группам учителя"""
    teacher = get_teacher_by_id_db(teacher_id)
    groups_stats = []
    
    for group in teacher.groups:
        students = get_students_by_group_db(group.group_id)
        avg_attendance = calculate_group_attendance_average(group.group_id)
        
        groups_stats.append({
            "group_id": group.group_id,
            "group_name": group.name,
            "students_count": len(students),
            "average_attendance": avg_attendance,
            "average_grade": calculate_group_grade_average(group.group_id)
        })
    
    return groups_stats

def calculate_group_attendance_average(group_id: int) -> float:
    """Вычисление средней посещаемости группы"""
    # Заглушка
    return 85.5

def calculate_group_grade_average(group_id: int) -> float:
    """Вычисление среднего балла группы"""
    # Заглушка
    return 8.2

# ===== АДМИНСКИЙ ДАШБОРД =====

@router.get("/admin", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    current_user = Depends(get_current_user)
):
    """Получение дашборда администратора"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только администраторам"
        )
    
    try:
        # Получаем общую статистику системы
        system_statistics = get_system_statistics()
        
        # Получаем последнюю активность в системе
        recent_system_activity = get_system_recent_activity()
        
        # Получаем статистику пользователей
        users_statistics = get_user_statistics_db()
        
        return AdminDashboardResponse(
            system_statistics=system_statistics,
            users_statistics=users_statistics,
            recent_activity=recent_system_activity
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def get_system_statistics() -> Dict[str, Any]:
    """Получение системной статистики"""
    return {
        "total_tests_taken": 1250,
        "total_questions": 5000,
        "total_materials": 150,
        "system_uptime": "99.9%",
        "active_sessions": 45
    }

def get_system_recent_activity() -> List[Dict[str, Any]]:
    """Получение последней системной активности"""
    return [
        {
            "type": "user_registration",
            "description": "Новый студент зарегистрирован",
            "timestamp": "30 минут назад",
            "details": "Петров И.С. - Группа 2"
        },
        {
            "type": "test_completion",
            "description": "Завершен тест по биологии",
            "timestamp": "1 час назад",
            "details": "Тема 21. Дыхательная система - 156 участников"
        },
        {
            "type": "material_upload",
            "description": "Загружен новый материал",
            "timestamp": "2 часа назад",
            "details": "Сборник задач по химии - Модуль 3"
        }
    ]

# ===== РОДИТЕЛЬСКИЙ ДАШБОРД =====

@router.get("/parent", response_model=ParentDashboardResponse)
async def get_parent_dashboard(
    current_user = Depends(get_current_user)
):
    """Получение дашборда родителя"""
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только родителям"
        )
    
    try:
        # Получаем ID студента (ребенка) по родителю
        student_id = get_student_id_by_parent_id(current_user.user_id)
        student = get_student_by_id_db(student_id)
        
        # Получаем сводную информацию по всем разделам
        performance_summary = analyze_student_performance(student_id)
        discipline_summary = analyze_student_discipline(student_id)
        exam_summary = analyze_student_exams(student_id)
        dtm_summary = analyze_student_dtm(student_id)
        
        # Вычисляем шанс поступления
        admission_chance = calculate_admission_chance(dtm_summary["current_score"], dtm_summary["required_score"])
        
        return ParentDashboardResponse(
            student_info={
                "name": f"{student.user.name} {student.user.surname}",
                "group": student.group_id,
                "photo_url": student.user.photo
            },
            performance=performance_summary,
            discipline=discipline_summary,
            exams=exam_summary,
            dtm_progress=dtm_summary,
            university_admission_chance=admission_chance,
            schedule={
                "chemistry": "Пн, Ср, Пт - 16:00-17:30",
                "biology": "Вт, Чт, Сб - 14:00-15:30"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def analyze_student_performance(student_id: int) -> Dict[str, Any]:
    """Анализ успеваемости студента"""
    chemistry_grade = calculate_subject_average(student_id, "chemistry")
    biology_grade = calculate_subject_average(student_id, "biology")
    
    # Определяем общий статус
    overall_avg = (chemistry_grade + biology_grade) / 2
    if overall_avg >= 9:
        status = "отлично"
    elif overall_avg >= 7:
        status = "хорошо"
    else:
        status = "плохо"
    
    return {
        "status": status,
        "chemistry": {
            "polls": {"current": 8, "total": 10},
            "tests": {"current": 7, "total": 10},
            "control_works": {"current": 10, "total": 10},
            "grade": chemistry_grade
        },
        "biology": {
            "polls": {"current": 7, "total": 10},
            "tests": {"current": 8, "total": 10},
            "control_works": {"current": 8, "total": 10},
            "grade": biology_grade
        }
    }

def analyze_student_discipline(student_id: int) -> Dict[str, Any]:
    """Анализ дисциплины студента"""
    missed_lessons = count_missed_lessons_db(student_id)
    late_arrivals = count_late_arrivals_db(student_id)
    
    # Определяем статус дисциплины
    if missed_lessons > 8 or late_arrivals > 5:
        status = "плохо"
    elif missed_lessons > 3 or late_arrivals > 2:
        status = "хорошо"
    else:
        status = "отлично"
    
    return {
        "status": status,
        "missed_lessons": {"current": missed_lessons, "total": 30},
        "missed_homework": {"current": 12, "total": 30},  # Заглушка
        "missed_polls": {"current": 15, "total": 30},     # Заглушка
        "teacher_remarks": 2                               # Заглушка
    }

def analyze_student_exams(student_id: int) -> Dict[str, Any]:
    """Анализ результатов экзаменов студента"""
    # Получаем последние результаты экзаменов
    latest_monthly = get_latest_monthly_exam_score(student_id)
    latest_final = get_latest_final_control_score(student_id)
    
    # Определяем статус
    if latest_monthly >= 85:
        status = "отлично"
    elif latest_monthly >= 70:
        status = "хорошо"
    else:
        status = "плохо"
    
    return {
        "status": status,
        "monthly_exam_last": {"score": latest_monthly, "max_score": 189},
        "final_control_last": {"score": latest_final, "max_score": 10},
        "intermediate_control_last": None
    }

def analyze_student_dtm(student_id: int) -> Dict[str, Any]:
    """Анализ прогресса ДТМ студента"""
    current_score = get_current_dtm_total_score(student_id)
    required_score = get_required_dtm_score_for_student(student_id)
    
    return {
        "current_score": current_score,
        "max_possible": 189,
        "required_score": required_score,
        "progress_percentage": round((current_score / 189) * 100, 1)
    }

def calculate_admission_chance(current_score: float, required_score: float) -> int:
    """Вычисление шанса поступления"""
    if current_score >= required_score + 20:
        return 90
    elif current_score >= required_score + 10:
        return 75
    elif current_score >= required_score:
        return 60
    else:
        return 30

# ===== ОБЩИЕ АНАЛИТИЧЕСКИЕ ФУНКЦИИ =====

def get_latest_monthly_exam_score(student_id: int) -> float:
    """Получение последней оценки за ежемесячный экзамен"""
    # Заглушка
    return 160.0

def get_latest_final_control_score(student_id: int) -> float:
    """Получение последней оценки за итоговый контроль"""
    # Заглушка
    return 10.0

def get_current_dtm_total_score(student_id: int) -> float:
    """Получение текущего общего балла ДТМ"""
    # Заглушка
    return 180.1

def get_required_dtm_score_for_student(student_id: int) -> float:
    """Получение необходимого балла ДТМ для студента"""
    # Заглушка
    return 151.9

def get_student_id_by_parent_id(parent_id: int) -> int:
    """Получение ID студента по ID родителя"""
    # Заглушка - в реальности должна быть связь в базе данных
    return 1

# ===== БЫСТРЫЕ ДЕЙСТВИЯ =====

@router.get("/quick-actions")
async def get_quick_actions(
    current_user = Depends(get_current_user)
):
    """Получение быстрых действий для пользователя"""
    try:
        actions = []
        
        if current_user.role == UserRole.STUDENT:
            actions = [
                {
                    "id": "start_test",
                    "title": "Начать новый тест",
                    "icon": "BookOpen",
                    "url": "/tests/available",
                    "color": "green"
                },
                {
                    "id": "view_schedule",
                    "title": "Посмотреть расписание",
                    "icon": "Calendar",
                    "url": "/schedule",
                    "color": "blue"
                },
                {
                    "id": "view_materials",
                    "title": "Учебные материалы",
                    "icon": "FileText",
                    "url": "/materials",
                    "color": "purple"
                }
            ]
        elif current_user.role == UserRole.TEACHER:
            actions = [
                {
                    "id": "mark_attendance",
                    "title": "Отметить посещаемость",
                    "icon": "Calendar",
                    "url": "/teacher/attendance",
                    "color": "blue"
                },
                {
                    "id": "add_comment",
                    "title": "Добавить комментарий",
                    "icon": "MessageSquare",
                    "url": "/teacher/comments",
                    "color": "green"
                },
                {
                    "id": "view_groups",
                    "title": "Мои группы",
                    "icon": "Users",
                    "url": "/teacher/groups",
                    "color": "purple"
                }
            ]
        elif current_user.role == UserRole.PARENT:
            actions = [
                {
                    "id": "view_progress",
                    "title": "Успеваемость ребенка",
                    "icon": "TrendingUp",
                    "url": "/parent/details",
                    "color": "green"
                },
                {
                    "id": "view_statistics",
                    "title": "Статистика",
                    "icon": "BarChart",
                    "url": "/parent/statistics",
                    "color": "blue"
                },
                {
                    "id": "view_recommendations",
                    "title": "Рекомендации",
                    "icon": "Target",
                    "url": "/parent/recommendations",
                    "color": "purple"
                }
            ]
        
        return {"actions": actions}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== УВЕДОМЛЕНИЯ =====

@router.get("/notifications")
async def get_user_notifications(
    limit: int = Query(10, le=50),
    unread_only: bool = Query(False),
    current_user = Depends(get_current_user)
):
    """Получение уведомлений пользователя"""
    try:
        notifications = []
        
        if current_user.role == UserRole.STUDENT:
            notifications = [
                {
                    "id": 1,
                    "type": "test_reminder",
                    "title": "Напоминание о тесте",
                    "message": "У вас есть незавершенный тест по биологии",
                    "is_read": False,
                    "created_at": datetime.now() - timedelta(hours=2),
                    "action_url": "/tests/active/123"
                },
                {
                    "id": 2,
                    "type": "grade_update",
                    "title": "Новая оценка",
                    "message": "Получена оценка за тест по химии: 8.5",
                    "is_read": True,
                    "created_at": datetime.now() - timedelta(days=1),
                    "action_url": "/tests/results/456"
                }
            ]
        elif current_user.role == UserRole.TEACHER:
            notifications = [
                {
                    "id": 1,
                    "type": "student_question",
                    "title": "Вопрос от студента",
                    "message": "Иванов А. задал вопрос по теме 'Органическая химия'",
                    "is_read": False,
                    "created_at": datetime.now() - timedelta(hours=1),
                    "action_url": "/teacher/messages/123"
                }
            ]
        elif current_user.role == UserRole.PARENT:
            notifications = [
                {
                    "id": 1,
                    "type": "grade_alert",
                    "title": "Снижение успеваемости",
                    "message": "Средний балл вашего ребенка по биологии снизился до 7.2",
                    "is_read": False,
                    "created_at": datetime.now() - timedelta(hours=3),
                    "action_url": "/parent/details/biology"
                }
            ]
        
        if unread_only:
            notifications = [n for n in notifications if not n["is_read"]]
        
        return {
            "notifications": notifications[:limit],
            "unread_count": len([n for n in notifications if not n["is_read"]])
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user = Depends(get_current_user)
):
    """Отметка уведомления как прочитанного"""
    try:
        # Логика отметки уведомления как прочитанного
        return {"message": "Уведомление отмечено как прочитанное"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )