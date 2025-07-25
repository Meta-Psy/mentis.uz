from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import calendar

# Импорты базы данных и моделей
from app.database import get_db
from app.database.models.assessment import AttendanceType, CommentType
from app.database.models.academic import Section, Block
from app.database.models.user import Student

# Импорты сервисов
from app.services.assessment.attendance_service import (
    get_attendance_by_student_and_subject_db,
    get_attendance_statistics_db,
)
from app.services.assessment.comment_service import (
    get_all_comments_by_student_db,
)
from app.services.assessment.grade_service import (
    get_current_score_db,
    get_second_current_score_db,
    calculate_final_grade_db,
)
from app.services.auth.student_service import get_student_by_id_db
from app.services.content.subject_service import (
    get_all_subjects_db,
)
from app.services.content.section_service import get_sections_by_subject_db
from app.services.content.topic_service import get_topics_by_block_db

# Импорты схем
from app.schemas.assessment.attendance import (
    AttendanceResponse,
    AttendanceCalendarResponse,
    AttendanceMonth,
    AttendanceDay,
    PerformanceTopic,
    CommentResponse,
    FinalGradeResponse,
    StudentDetailsResponse,
    ModulePerformanceResponse,
    StudentStatistics,
    AssessmentHealthResponse,
)

# Создание роутера
router = APIRouter()

# ===========================================
# ПОЛУЧЕНИЕ ПОЛНОЙ ИНФОРМАЦИИ О СТУДЕНТЕ
# ===========================================


@router.get(
    "/student/{student_id}/details",
    response_model=StudentDetailsResponse,
    summary="Получить полную информацию о студенте",
    description="Получение всех данных студента для родительской страницы",
)
async def get_student_details(
    student_id: int = Path(..., gt=0, description="ID студента"),
    db: AsyncSession = Depends(get_db),
) -> StudentDetailsResponse:
    """Получение полной информации о студенте"""

    try:
        # Проверяем существование студента
        student = await get_student_by_id_db(db, student_id)

        # Получаем все предметы
        subjects = await get_all_subjects_db(db)

        subjects_data = {}

        for subject in subjects:
            subject_name = "chemistry" if "химия" in subject.name.lower() else "biology"

            # Получаем посещаемость
            try:
                attendance_records = await get_attendance_by_student_and_subject_db(
                    db, student_id, subject.subject_id
                )
                attendance_stats = await get_attendance_statistics_db(
                    db, student_id, subject.subject_id
                )
            except:
                attendance_records = []
                attendance_stats = None

            # Получаем итоговые оценки
            try:
                final_grades = await calculate_final_grade_db(
                    db, student_id, subject.subject_id
                )
            except:
                final_grades = None

            # Получаем разделы для успеваемости
            try:
                sections = await get_sections_by_subject_db(db, subject.subject_id)
                performance_data = await _get_performance_data(db, student_id, sections)
            except:
                performance_data = {}

            subjects_data[subject_name] = {
                "attendance": {
                    "records": [
                        AttendanceResponse(
                            attendance_id=att.attendance_id,
                            student_id=att.student_id,
                            lesson_date_time=att.lesson_date_time,
                            att_status=att.att_status,
                            subject_id=att.subject_id,
                            topic_id=att.topic_id,
                            excuse_reason=att.excuse_reason,
                            extra_lesson=att.extra_lesson,
                        )
                        for att in attendance_records
                    ],
                    "statistics": attendance_stats,
                },
                "performance": performance_data,
                "final_grades": final_grades,
            }

        return StudentDetailsResponse(
            student_id=student_id,
            student_name=student.user.name,
            student_surname=student.user.surname,
            subjects_data=subjects_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения данных студента: {str(e)}",
        )


# ===========================================
# КАЛЕНДАРЬ ПОСЕЩАЕМОСТИ
# ===========================================


@router.get(
    "/student/{student_id}/attendance/calendar",
    response_model=AttendanceCalendarResponse,
    summary="Получить календарь посещаемости",
    description="Получение календаря посещаемости студента по предмету",
)
async def get_attendance_calendar(
    student_id: int = Path(..., gt=0, description="ID студента"),
    subject_name: str = Query(..., description="Название предмета (chemistry/biology)"),
    module_id: Optional[int] = Query(None, description="ID модуля для фильтрации"),
    db: AsyncSession = Depends(get_db),
) -> AttendanceCalendarResponse:
    """Получение календаря посещаемости"""

    try:
        # Находим предмет
        subjects = await get_all_subjects_db(db)
        subject = None

        if subject_name.lower() in ["chemistry", "химия"]:
            subject = next((s for s in subjects if "химия" in s.name.lower()), None)
        elif subject_name.lower() in ["biology", "биология"]:
            subject = next((s for s in subjects if "биология" in s.name.lower()), None)

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
            )

        # Получаем записи посещаемости
        attendance_records = await get_attendance_by_student_and_subject_db(
            db, student_id, subject.subject_id
        )

        # Группируем по месяцам
        months_data = {}

        for record in attendance_records:
            date: datetime = record.lesson_date_time
            month_key = f"{date.year}-{date.month:02d}"

            if month_key not in months_data:
                months_data[month_key] = {
                    "name": f"{_get_month_name(date.month)} {date.year}",
                    "year": date.year,
                    "month": date.month,
                    "days": [],
                }
            lesson_name = _get_topic_name(db=db, topic_id=record.topic_id)
            # Определяем статус
            status_map = {
                AttendanceType.PRESENT: "present",
                AttendanceType.ABSENT: "absent",
                AttendanceType.LATE: "late",
            }
            day_data = AttendanceDay(
                date=date.day,
                status=status_map.get(record.att_status, "present"),
                lesson=lesson_name,
                topic_id=record.topic_id,
                attendance_id=record.attendance_id,
            )

            months_data[month_key]["days"].append(day_data)

        # Конвертируем в список месяцев
        months = []
        for month_key in sorted(months_data.keys()):
            month_data = months_data[month_key]
            months.append(
                AttendanceMonth(
                    name=month_data["name"],
                    year=month_data["year"],
                    month=month_data["month"],
                    days=month_data["days"],
                )
            )

        return AttendanceCalendarResponse(
            student_id=student_id, subject_id=subject.subject_id, months=months
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения календаря: {str(e)}",
        )


# ===========================================
# УСПЕВАЕМОСТЬ ПО МОДУЛЮ
# ===========================================


@router.get(
    "/student/{student_id}/performance/module",
    response_model=List[ModulePerformanceResponse],
    summary="Получить успеваемость по модулям",
    description="Получение успеваемости студента по модулям",
)
async def get_module_performance(
    student_id: int = Path(..., gt=0, description="ID студента"),
    subject_name: str = Query(..., description="Название предмета"),
    module_id: Optional[int] = Query(None, description="ID конкретного модуля"),
    db: AsyncSession = Depends(get_db),
) -> List[ModulePerformanceResponse]:
    """Получение успеваемости по модулям"""

    try:
        # Находим предмет
        subjects = await get_all_subjects_db(db)
        subject = None

        if subject_name.lower() in ["chemistry", "химия"]:
            subject = next((s for s in subjects if "химия" in s.name.lower()), None)
        elif subject_name.lower() in ["biology", "биология"]:
            subject = next((s for s in subjects if "биология" in s.name.lower()), None)

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
            )

        # Получаем разделы (модули)
        sections = await get_sections_by_subject_db(db, subject.subject_id)

        if module_id:
            sections = [s for s in sections if s.section_id == module_id]

        modules_performance = []

        for section in sections:
            # Получаем темы для раздела
            from sqlalchemy import select

            blocks_result = await db.execute(
                select(Block).filter(Block.section_id == section.section_id)
            )
            blocks = blocks_result.scalars().all()

            topics_performance = []
            total_average = 0
            topics_count = 0

            for block in blocks:
                topics = await get_topics_by_block_db(db, block.block_id)

                for topic in topics:
                    # Получаем текущие оценки
                    try:
                        first_score = await get_current_score_db(
                            db, student_id, subject.subject_id, topic.topic_id
                        )
                        second_score = await get_second_current_score_db(
                            db, student_id, subject.subject_id, topic.topic_id
                        )

                        average = (
                            (first_score + second_score) / 2
                            if second_score
                            else first_score
                        )

                        topic_perf = PerformanceTopic(
                            number=topic.number or topics_count + 1,
                            topic_id=topic.topic_id,
                            topic_name=topic.name,
                            listened=True,  # TODO: определить из посещаемости
                            first_try=first_score if first_score > 0 else None,
                            second_try=(
                                second_score
                                if second_score and second_score > 0
                                else None
                            ),
                            average=average,
                        )

                        topics_performance.append(topic_perf)
                        total_average += average
                        topics_count += 1

                    except:
                        # Если нет оценок
                        topic_perf = PerformanceTopic(
                            number=topic.number or topics_count + 1,
                            topic_id=topic.topic_id,
                            topic_name=topic.name,
                            listened=False,
                            first_try=None,
                            second_try=None,
                            average=0,
                        )
                        topics_performance.append(topic_perf)
                        topics_count += 1

            module_average = total_average / topics_count if topics_count > 0 else 0

            modules_performance.append(
                ModulePerformanceResponse(
                    module_id=section.section_id,
                    module_name=section.name,
                    topics=topics_performance,
                    average_grade=module_average,
                )
            )

        return modules_performance

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения успеваемости: {str(e)}",
        )


# ===========================================
# ИТОГОВЫЕ ОЦЕНКИ
# ===========================================


@router.get(
    "/student/{student_id}/final-grades",
    response_model=Dict[str, FinalGradeResponse],
    summary="Получить итоговые оценки",
    description="Получение итоговых оценок студента по всем предметам",
)
async def get_final_grades(
    student_id: int = Path(..., gt=0, description="ID студента"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, FinalGradeResponse]:
    """Получение итоговых оценок"""

    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)

        # Получаем все предметы
        subjects = await get_all_subjects_db(db)

        final_grades = {}

        for subject in subjects:
            subject_name = "chemistry" if "химия" in subject.name.lower() else "biology"

            try:
                grade_data = await calculate_final_grade_db(
                    db, student_id, subject.subject_id
                )
                final_grades[subject_name] = FinalGradeResponse(**grade_data)
            except:
                # Если нет данных для расчета
                final_grades[subject_name] = FinalGradeResponse(
                    student_id=student_id,
                    subject_id=subject.subject_id,
                    section_average=0.0,
                    block_average=0.0,
                    current_average=0.0,
                    topic_average=0.0,
                    final_grade=0.0,
                    counts={
                        "section_exams": 0,
                        "block_exams": 0,
                        "current_ratings": 0,
                        "topic_tests": 0,
                    },
                )

        return final_grades

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения итоговых оценок: {str(e)}",
        )


# ===========================================
# КОММЕНТАРИИ
# ===========================================


@router.get(
    "/student/{student_id}/comments",
    response_model=List[CommentResponse],
    summary="Получить комментарии студента",
    description="Получение всех комментариев о студенте",
)
async def get_student_comments(
    student_id: int = Path(..., gt=0, description="ID студента"),
    comment_type: Optional[str] = Query(None, description="Тип комментария"),
    limit: int = Query(50, le=200, description="Лимит результатов"),
    db: AsyncSession = Depends(get_db),
) -> List[CommentResponse]:
    """Получение комментариев студента"""

    try:
        comments = await get_all_comments_by_student_db(db, student_id)

        # Фильтруем по типу если указан
        if comment_type:
            comments = [c for c in comments if c.comment_type.value == comment_type]

        # Ограничиваем количество
        comments = comments[:limit]

        return [
            CommentResponse(
                comment_id=comment.comment_id,
                teacher_id=comment.teacher_id,
                student_id=comment.student_id,
                comment_text=comment.comment_text,
                comment_date=comment.comment_date,
                comment_type=comment.comment_type.value,
                teacher_name=comment.teacher.user.name if comment.teacher else None,
                teacher_surname=(
                    comment.teacher.user.surname if comment.teacher else None
                ),
            )
            for comment in comments
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения комментариев: {str(e)}",
        )


# ===========================================
# СТАТИСТИКА
# ===========================================


@router.get(
    "/student/{student_id}/statistics",
    response_model=StudentStatistics,
    summary="Получить статистику студента",
    description="Получение полной статистики студента",
)
async def get_student_statistics(
    student_id: int = Path(..., gt=0, description="ID студента"),
    db: AsyncSession = Depends(get_db),
) -> StudentStatistics:
    """Получение статистики студента"""

    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)

        # Получаем все предметы
        subjects = await get_all_subjects_db(db)

        attendance_stats = {}
        performance_stats = {}

        for subject in subjects:
            subject_name = "chemistry" if "химия" in subject.name.lower() else "biology"

            # Статистика посещаемости
            try:
                att_stats = await get_attendance_statistics_db(
                    db, student_id, subject.subject_id
                )
                attendance_stats[subject_name] = att_stats
            except:
                attendance_stats[subject_name] = None

            # Статистика успеваемости
            try:
                perf_stats = await calculate_final_grade_db(
                    db, student_id, subject.subject_id
                )
                performance_stats[subject_name] = FinalGradeResponse(**perf_stats)
            except:
                performance_stats[subject_name] = None

        # Подсчитываем комментарии
        try:
            all_comments = await get_all_comments_by_student_db(db, student_id)
            comments_count = {
                "positive": len(
                    [c for c in all_comments if c.comment_type == CommentType.POSITIVE]
                ),
                "negative": len(
                    [c for c in all_comments if c.comment_type == CommentType.NEGATIVE]
                ),
                "neutral": len(
                    [c for c in all_comments if c.comment_type == CommentType.NEUTRAL]
                ),
            }
        except:
            comments_count = {"positive": 0, "negative": 0, "neutral": 0}

        return StudentStatistics(
            student_id=student_id,
            attendance_stats=attendance_stats,
            performance_stats=performance_stats,
            comments_count=comments_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики: {str(e)}",
        )


# ===========================================
# ПРОВЕРКА ЗДОРОВЬЯ API
# ===========================================


@router.get(
    "/health",
    response_model=AssessmentHealthResponse,
    summary="Проверка здоровья API",
    description="Проверка работоспособности API оценок",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> AssessmentHealthResponse:
    """Проверка здоровья API оценок"""

    try:
        # Проверяем подключение к базе данных
        from sqlalchemy import text

        await db.execute(text("SELECT 1"))

        # Подсчитываем активных студентов
        from sqlalchemy import select, func

        result = await db.execute(
            select(func.count(Student.student_id)).filter(
                Student.student_status == "ACTIVE"
            )
        )
        active_students = result.scalar()

        return AssessmentHealthResponse(
            status="healthy",
            service="assessment-api",
            version="1.0.0",
            timestamp=datetime.now(),
            active_students=active_students,
        )

    except Exception as e:
        return AssessmentHealthResponse(
            status="unhealthy",
            service="assessment-api",
            version="1.0.0",
            timestamp=datetime.now(),
            active_students=None,
        )


# ===========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ===========================================


def _get_month_name(month: int) -> str:
    """Получение названия месяца на русском"""
    months = {
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь",
    }
    return months.get(month, "Неизвестно")


async def _get_performance_data(
    db: AsyncSession, student_id: int, sections: List[Section]
) -> Dict[str, Any]:
    """Получение данных успеваемости по разделам"""

    performance_data = {}

    for section in sections:
        try:
            # Получаем блоки раздела
            from sqlalchemy import select

            blocks_result = await db.execute(
                select(Block).filter(Block.section_id == section.section_id)
            )
            blocks = blocks_result.scalars().all()

            topics_performance = []

            for block in blocks:
                topics = await get_topics_by_block_db(db, block.block_id)

                for topic in topics:
                    try:
                        # Получаем текущие оценки
                        first_score = await get_current_score_db(
                            db, student_id, section.subject_id, topic.topic_id
                        )
                        second_score = await get_second_current_score_db(
                            db, student_id, section.subject_id, topic.topic_id
                        )

                        average = (
                            (first_score + second_score) / 2
                            if second_score
                            else first_score if first_score else 0
                        )

                        topics_performance.append(
                            {
                                "number": topic.number or len(topics_performance) + 1,
                                "topic_id": topic.topic_id,
                                "topic_name": topic.name,
                                "listened": True,  # TODO: определить из посещаемости
                                "first_try": (
                                    first_score
                                    if first_score and first_score > 0
                                    else None
                                ),
                                "second_try": (
                                    second_score
                                    if second_score and second_score > 0
                                    else None
                                ),
                                "average": average,
                            }
                        )

                    except:
                        topics_performance.append(
                            {
                                "number": topic.number or len(topics_performance) + 1,
                                "topic_id": topic.topic_id,
                                "topic_name": topic.name,
                                "listened": False,
                                "first_try": None,
                                "second_try": None,
                                "average": 0,
                            }
                        )

            performance_data[f"module_{section.section_id}"] = {
                "module_id": section.section_id,
                "module_name": section.name,
                "topics": topics_performance,
            }

        except Exception as e:
            print(f"Ошибка получения данных для раздела {section.section_id}: {e}")
            continue

    return performance_data


async def _get_topic_name(db: AsyncSession, topic_id: int) -> str:
    """Получение названия темы"""
    try:
        from app.services.content.topic_service import find_topic_db

        topic = await find_topic_db(db, topic_id)
        return topic.name
    except:
        return f"Урок {topic_id}"
