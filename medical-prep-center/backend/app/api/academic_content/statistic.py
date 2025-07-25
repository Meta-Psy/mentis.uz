from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import calendar

# Импорты базы данных и моделей
from app.database import get_db
from app.database.models.assessment import (
    DtmExam, SectionExam, BlockExam, TopicTest, CurrentRating, AttendanceType
)
from app.database.models.academic import Subject, Topic, Block, Section, Group
from app.database.models.user import Student

# Импорты сервисов
from app.services.assessment.grade_service import (
    get_all_dtm_scores_by_student_db,
    get_average_dtm_score_for_student_db,
    get_avg_score_by_student_subject_db,
    get_avg_block_score_by_student_subject_db,
    get_current_score_db,
    get_second_current_score_db,
    calculate_final_grade_db
)
from app.services.assessment.attendance_service import (
    get_attendance_statistics_db
)
from app.services.auth.student_service import (
    get_student_by_id_db,
    get_students_by_group_db
)
from app.services.content.subject_service import (
    get_all_subjects_db,
    find_subject_db
)

# Импорты схем
from app.schemas.assessment.statistic import (
    StudentStatisticsResponse,
    SubjectProgressResponse, 
    RankingResponse,
    StatisticsRequest,
    SubjectProgressRequest,
    RankingRequest,
    StatisticsHealthResponse,
    GradePoint,
    SubjectStatistics,
    OverallStatistics,
    StudentRankingInfo,
    TournamentTable,
    DetailedStatisticsResponse,
    PerformanceInsights,
    TrendAnalysis
)

from sqlalchemy import select, func, and_, or_
from collections import defaultdict

# Создание роутера
router = APIRouter()

# ===========================================
# ПОЛУЧЕНИЕ ПОЛНОЙ СТАТИСТИКИ СТУДЕНТА
# ===========================================

@router.get("/student/{student_id}", 
            response_model=StudentStatisticsResponse,
            summary="Получить полную статистику студента",
            description="Получение всех данных статистики студента включая графики и рейтинги")
async def get_student_statistics(
    student_id: int = Path(..., gt=0, description="ID студента"),
    period: str = Query("monthly", description="Период (monthly, weekly, daily)"),
    include_tournaments: bool = Query(True, description="Включить турнирные таблицы"),
    db: AsyncSession = Depends(get_db)
) -> StudentStatisticsResponse:
    """Получение полной статистики студента"""
    
    try:
        # Проверяем существование студента
        student = await get_student_by_id_db(db, student_id)
        
        # Получаем информацию о группе
        group_result = await db.execute(
            select(Group).filter(Group.group_id == student.group_id)
        )
        group = group_result.scalar_one_or_none()
        group_name = group.name if group else f"Группа {student.group_id}"
        
        # Получаем все предметы
        subjects = await get_all_subjects_db(db)
        chemistry_subject = next((s for s in subjects if 'химия' in s.name.lower()), None)
        biology_subject = next((s for s in subjects if 'биология' in s.name.lower()), None)
        
        # Создаем статистику по предметам
        chemistry_stats = await _get_subject_statistics(
            db, student_id, chemistry_subject, period
        ) if chemistry_subject else SubjectStatistics(
            subject_id=0, subject_name="Химия"
        )
        
        biology_stats = await _get_subject_statistics(
            db, student_id, biology_subject, period
        ) if biology_subject else SubjectStatistics(
            subject_id=0, subject_name="Биология"
        )
        
        # Получаем общую статистику
        overall_stats = await _get_overall_statistics(db, student_id)
        
        # Получаем турнирные таблицы если запрошены
        tournament_tables = []
        if include_tournaments:
            tournament_tables = await _get_all_tournament_tables(db, student_id)
        
        return StudentStatisticsResponse(
            student_id=student_id,
            student_name=f"{student.user.name} {student.user.surname}",
            group_id=student.group_id,
            group_name=group_name,
            chemistry=chemistry_stats,
            biology=biology_stats,
            overall=overall_stats,
            tournament_tables=tournament_tables
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики: {str(e)}"
        )


# ===========================================
# ПОЛУЧЕНИЕ ПРОГРЕССА ПО ПРЕДМЕТУ
# ===========================================

@router.get("/student/{student_id}/subject/{subject_name}",
            response_model=SubjectProgressResponse,
            summary="Получить прогресс по предмету",
            description="Детальный прогресс студента по конкретному предмету")
async def get_subject_progress(
    student_id: int = Path(..., gt=0, description="ID студента"),
    subject_name: str = Path(..., description="Название предмета (chemistry/biology)"),
    metric_type: str = Query("current_grades", description="Тип метрики"),
    period: str = Query("monthly", description="Период"),
    db: AsyncSession = Depends(get_db)
) -> SubjectProgressResponse:
    """Получение прогресса по предмету"""
    
    try:
        # Проверяем студента
        student = await get_student_by_id_db(db, student_id)
        
        # Находим предмет
        subjects = await get_all_subjects_db(db)
        subject = None
        
        if subject_name.lower() in ['chemistry', 'химия']:
            subject = next((s for s in subjects if 'химия' in s.name.lower()), None)
        elif subject_name.lower() in ['biology', 'биология']:
            subject = next((s for s in subjects if 'биология' in s.name.lower()), None)
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Предмет {subject_name} не найден"
            )
        
        # Получаем данные для графика
        progress_data = await _get_progress_data(
            db, student_id, subject, metric_type, period
        )
        
        # Рассчитываем сводную информацию
        current_average = await _calculate_current_average(db, student_id, subject)
        improvement_trend = await _calculate_improvement_trend(progress_data.get(metric_type, []))
        last_month_average = await _calculate_last_month_average(progress_data.get(metric_type, []))
        
        return SubjectProgressResponse(
            subject_id=subject.subject_id,
            subject_name=subject.name,
            student_id=student_id,
            progress_data=progress_data,
            current_average=current_average,
            improvement_trend=improvement_trend,
            last_month_average=last_month_average
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения прогресса: {str(e)}"
        )


# ===========================================
# ПОЛУЧЕНИЕ ТУРНИРНОЙ ТАБЛИЦЫ
# ===========================================

@router.get("/ranking/{table_type}",
            response_model=RankingResponse,
            summary="Получить турнирную таблицу",
            description="Получение рейтинга студентов по различным критериям")
async def get_ranking(
    table_type: str = Path(..., description="Тип таблицы"),
    student_id: int = Query(..., gt=0, description="ID текущего студента"),
    group_id: Optional[int] = Query(None, description="Фильтр по группе"),
    limit: int = Query(50, le=200, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
) -> RankingResponse:
    """Получение турнирной таблицы"""
    
    try:
        # Проверяем студента
        current_student = await get_student_by_id_db(db, student_id)
        
        # Получаем рейтинг в зависимости от типа
        students_ranking = await _get_ranking_by_type(
            db, table_type, student_id, group_id, limit
        )
        
        # Находим позицию текущего студента
        current_student_rank = 0
        current_student_info = None
        
        for i, student_info in enumerate(students_ranking):
            if student_info.student_id == student_id:
                current_student_rank = i + 1
                current_student_info = student_info
                break
        
        # Определяем заголовок
        title = _get_table_title(table_type, group_id)
        
        return RankingResponse(
            table_type=table_type,
            title=title,
            students=students_ranking[:limit],
            current_student=current_student_info,
            current_student_rank=current_student_rank,
            total_participants=len(students_ranking),
            group_filter=group_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения рейтинга: {str(e)}"
        )


# ===========================================
# ПОЛУЧЕНИЕ ДЕТАЛЬНОЙ АНАЛИТИКИ
# ===========================================

@router.get("/student/{student_id}/insights",
            response_model=DetailedStatisticsResponse,
            summary="Получить детальную аналитику",
            description="Аналитические выводы и рекомендации для студента")
async def get_detailed_insights(
    student_id: int = Path(..., gt=0, description="ID студента"),
    db: AsyncSession = Depends(get_db)
) -> DetailedStatisticsResponse:
    """Получение детальной аналитики"""
    
    try:
        # Получаем базовую статистику
        student_stats = await get_student_statistics(student_id, db=db)
        
        # Генерируем аналитические выводы
        insights = await _generate_performance_insights(db, student_id, student_stats)
        
        # Получаем данные для сравнения
        comparison_data = await _get_comparison_data(db, student_id)
        
        return DetailedStatisticsResponse(
            student_statistics=student_stats,
            performance_insights=insights,
            comparison_data=comparison_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения аналитики: {str(e)}"
        )


# ===========================================
# ПРОВЕРКА ЗДОРОВЬЯ API
# ===========================================

@router.get("/health",
            response_model=StatisticsHealthResponse,
            summary="Проверка здоровья API",
            description="Проверка работоспособности API статистики")
async def health_check(db: AsyncSession = Depends(get_db)) -> StatisticsHealthResponse:
    """Проверка здоровья API статистики"""
    
    try:
        # Проверяем доступность базы данных
        await db.execute(select(1))
        
        return StatisticsHealthResponse(
            status="healthy",
            service="statistics-api",
            version="1.0.0",
            timestamp=datetime.now(),
            active_calculations=0,
            cache_status="operational"
        )
    except Exception:
        return StatisticsHealthResponse(
            status="unhealthy",
            service="statistics-api",
            version="1.0.0",
            timestamp=datetime.now(),
            active_calculations=0,
            cache_status="error"
        )


# ===========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ===========================================

async def _get_subject_statistics(
    db: AsyncSession, 
    student_id: int, 
    subject: Subject, 
    period: str
) -> SubjectStatistics:
    """Получение статистики по предмету"""
    
    # Получаем данные для графиков
    current_grades = await _get_current_grades_data(db, student_id, subject, period)
    tests_data = await _get_tests_data(db, student_id, subject, period)
    dtm_data = await _get_dtm_data(db, student_id, subject, period)
    section_exams_data = await _get_section_exams_data(db, student_id, subject, period)
    block_exams_data = await _get_block_exams_data(db, student_id, subject, period)
    
    # Рассчитываем средние значения
    try:
        avg_current = await _calculate_avg_current_grade(db, student_id, subject)
    except:
        avg_current = 0.0
        
    try:
        avg_test = await _calculate_avg_test_score(db, student_id, subject)
    except:
        avg_test = 0.0
        
    try:
        avg_dtm = await _calculate_avg_dtm_score(db, student_id, subject)
    except:
        avg_dtm = 0.0
        
    try:
        avg_section = await get_avg_score_by_student_subject_db(db, student_id, subject.subject_id)
    except:
        avg_section = 0.0
        
    try:
        avg_block = await get_avg_block_score_by_student_subject_db(db, student_id, subject.subject_id)
    except:
        avg_block = 0.0
    
    return SubjectStatistics(
        subject_id=subject.subject_id,
        subject_name=subject.name,
        current_grades=current_grades,
        tests=tests_data,
        dtm=dtm_data,
        section_exams=section_exams_data,
        block_exams=block_exams_data,
        avg_current_grade=avg_current,
        avg_test_score=avg_test,
        avg_dtm_score=avg_dtm,
        avg_section_score=avg_section,
        avg_block_score=avg_block
    )


async def _get_overall_statistics(db: AsyncSession, student_id: int) -> OverallStatistics:
    """Получение общей статистики"""
    
    # Подсчет общих показателей
    subjects_result = await db.execute(select(func.count(Subject.subject_id)))
    total_subjects = subjects_result.scalar() or 0
    
    # Подсчет тестов
    topic_tests_result = await db.execute(
        select(func.count(TopicTest.topic_test_id))
        .filter(TopicTest.student_id == student_id)
    )
    completed_tests = topic_tests_result.scalar() or 0
    
    # Получаем статистику посещаемости
    try:
        attendance_stats = await get_attendance_statistics_db(db, student_id)
        total_lessons = attendance_stats.get('total_lessons', 0)
        attended_lessons = attendance_stats.get('present_count', 0)
        attendance_rate = attendance_stats.get('attendance_rate', 0.0)
    except:
        total_lessons = 0
        attended_lessons = 0
        attendance_rate = 0.0
    
    # Подсчет ДТМ
    dtm_attempts_result = await db.execute(
        select(func.count(DtmExam.exam_id))
        .filter(DtmExam.student_id == student_id)
    )
    total_dtm_attempts = dtm_attempts_result.scalar() or 0
    
    # Лучший и последний ДТМ балл
    try:
        dtm_scores = await get_all_dtm_scores_by_student_db(db, student_id)
        if dtm_scores:
            best_dtm = max(exam.total_correct_answers for exam in dtm_scores)
            latest_dtm = dtm_scores[-1].total_correct_answers if dtm_scores else 0
        else:
            best_dtm = 0
            latest_dtm = 0
    except:
        best_dtm = 0
        latest_dtm = 0
    
    return OverallStatistics(
        student_id=student_id,
        total_subjects=total_subjects,
        completed_tests=completed_tests,
        pending_tests=0,  # TODO: рассчитать на основе доступных тестов
        overdue_tests=0,  # TODO: рассчитать на основе дедлайнов
        overall_average=0.0,  # TODO: рассчитать общий средний балл
        chemistry_average=0.0,  # TODO: рассчитать из subject statistics
        biology_average=0.0,  # TODO: рассчитать из subject statistics
        total_dtm_attempts=total_dtm_attempts,
        best_dtm_score=float(best_dtm),
        latest_dtm_score=float(latest_dtm),
        total_lessons=total_lessons,
        attended_lessons=attended_lessons,
        attendance_rate=attendance_rate
    )


async def _get_current_grades_data(
    db: AsyncSession, 
    student_id: int, 
    subject: Subject, 
    period: str
) -> List[GradePoint]:
    """Получение данных текущих оценок для графика"""
    
    # Получаем оценки текущих по месяцам
    current_ratings_result = await db.execute(
        select(CurrentRating)
        .filter(
            CurrentRating.student_id == student_id,
            CurrentRating.subject_id == subject.subject_id
        )
        .order_by(CurrentRating.last_updated)
    )
    current_ratings = current_ratings_result.scalars().all()
    
    # Группируем по месяцам
    monthly_data = defaultdict(list)
    for rating in current_ratings:
        month_key = rating.last_updated.strftime("%b") if rating.last_updated else "Unknown"
        total_score = (rating.current_correct_answers + rating.second_current_correct_answers)
        monthly_data[month_key].append(total_score)
    
    # Создаем точки для графика
    months = ["сент.", "окт.", "нояб.", "дек.", "янв.", "февр.", "март", "апр.", "май", "июнь", "июль"]
    grade_points = []
    
    for month in months:
        if month in monthly_data:
            avg_score = sum(monthly_data[month]) / len(monthly_data[month])
            # Нормализуем оценку к шкале 0-10
            normalized_score = min(10.0, max(0.0, avg_score / 2))
        else:
            normalized_score = 0.0
        
        grade_points.append(GradePoint(month=month, value=round(normalized_score, 1)))
    
    return grade_points


async def _get_tests_data(
    db: AsyncSession, 
    student_id: int, 
    subject: Subject, 
    period: str
) -> List[GradePoint]:
    """Получение данных тестов для графика"""
    
    # Получаем результаты тестов по темам
    topic_tests_result = await db.execute(
        select(TopicTest)
        .join(Topic, TopicTest.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .filter(
            TopicTest.student_id == student_id,
            Section.subject_id == subject.subject_id
        )
        .order_by(TopicTest.attempt_date)
    )
    topic_tests = topic_tests_result.scalars().all()
    
    # Группируем по месяцам
    monthly_data = defaultdict(list)
    for test in topic_tests:
        month_key = test.attempt_date.strftime("%b") if test.attempt_date else "Unknown"
        score_percentage = (test.correct_answers / test.question_count * 10) if test.question_count > 0 else 0
        monthly_data[month_key].append(score_percentage)
    
    # Создаем точки для графика
    months = ["сент.", "окт.", "нояб.", "дек.", "янв.", "февр.", "март", "апр.", "май", "июнь", "июль"]
    grade_points = []
    
    for month in months:
        if month in monthly_data:
            avg_score = sum(monthly_data[month]) / len(monthly_data[month])
        else:
            avg_score = 0.0
        
        grade_points.append(GradePoint(month=month, value=round(avg_score, 1)))
    
    return grade_points


async def _get_dtm_data(
    db: AsyncSession, 
    student_id: int, 
    subject: Subject, 
    period: str
) -> List[GradePoint]:
    """Получение данных ДТМ для графика"""
    
    # Получаем результаты ДТМ
    dtm_exams_result = await db.execute(
        select(DtmExam)
        .filter(
            DtmExam.student_id == student_id,
            DtmExam.subject_id == subject.subject_id
        )
        .order_by(DtmExam.exam_date)
    )
    dtm_exams = dtm_exams_result.scalars().all()
    
    # Группируем по месяцам
    monthly_data = defaultdict(list)
    for exam in dtm_exams:
        if exam.exam_date:
            month_key = exam.exam_date.strftime("%b")
            monthly_data[month_key].append(exam.total_correct_answers)
    
    # Создаем точки для графика
    months = ["сент.", "окт.", "нояб.", "дек.", "янв.", "февр.", "март", "апр.", "май", "июнь", "июль"]
    grade_points = []
    
    for month in months:
        if month in monthly_data:
            avg_score = sum(monthly_data[month]) / len(monthly_data[month])
        else:
            avg_score = 25.0  # Средний балл по умолчанию
        
        grade_points.append(GradePoint(month=month, value=round(avg_score, 1)))
    
    return grade_points


async def _get_section_exams_data(
    db: AsyncSession, 
    student_id: int, 
    subject: Subject, 
    period: str
) -> List[GradePoint]:
    """Получение данных экзаменов по разделам"""
    
    section_exams_result = await db.execute(
        select(SectionExam)
        .join(Section, SectionExam.section_id == Section.section_id)
        .filter(
            SectionExam.student_id == student_id,
            Section.subject_id == subject.subject_id
        )
        .order_by(SectionExam.exam_date)
    )
    section_exams = section_exams_result.scalars().all()
    
    # Группируем по месяцам
    monthly_data = defaultdict(list)
    for exam in section_exams:
        month_key = exam.exam_date.strftime("%b") if exam.exam_date else "Unknown"
        # Нормализуем к шкале 0-10
        normalized_score = min(10.0, max(0.0, exam.correct_answers))
        monthly_data[month_key].append(normalized_score)
    
    # Создаем точки для графика
    months = ["сент.", "окт.", "нояб.", "дек.", "янв.", "февр.", "март", "апр.", "май", "июнь", "июль"]
    grade_points = []
    
    for month in months:
        if month in monthly_data:
            avg_score = sum(monthly_data[month]) / len(monthly_data[month])
        else:
            avg_score = 0.0
        
        grade_points.append(GradePoint(month=month, value=round(avg_score, 1)))
    
    return grade_points


async def _get_block_exams_data(
    db: AsyncSession, 
    student_id: int, 
    subject: Subject, 
    period: str
) -> List[GradePoint]:
    """Получение данных экзаменов по блокам"""
    
    block_exams_result = await db.execute(
        select(BlockExam)
        .filter(
            BlockExam.student_id == student_id,
            BlockExam.subject_id == subject.subject_id
        )
        .order_by(BlockExam.exam_date)
    )
    block_exams = block_exams_result.scalars().all()
    
    # Группируем по месяцам
    monthly_data = defaultdict(list)
    for exam in block_exams:
        month_key = exam.exam_date.strftime("%b") if exam.exam_date else "Unknown"
        # Нормализуем к шкале 0-10
        normalized_score = min(10.0, max(0.0, exam.correct_answers))
        monthly_data[month_key].append(normalized_score)
    
    # Создаем точки для графика
    months = ["сент.", "окт.", "нояб.", "дек.", "янв.", "февр.", "март", "апр.", "май", "июнь", "июль"]
    grade_points = []
    
    for month in months:
        if month in monthly_data:
            avg_score = sum(monthly_data[month]) / len(monthly_data[month])
        else:
            avg_score = 0.0
        
        grade_points.append(GradePoint(month=month, value=round(avg_score, 1)))
    
    return grade_points


async def _get_all_tournament_tables(
    db: AsyncSession, 
    student_id: int
) -> List[TournamentTable]:
    """Получение всех турнирных таблиц"""
    
    tables = []
    
    # Все группы - средний балл
    all_groups_avg = await _get_ranking_by_type(db, "all_groups_average", student_id, None, 50)
    tables.append(TournamentTable(
        table_type="all_groups_average",
        title="По всем группам (средний балл)",
        students=all_groups_avg,
        current_student_rank=_find_student_rank(all_groups_avg, student_id),
        total_participants=len(all_groups_avg)
    ))
    
    # Моя группа - средний балл
    student = await get_student_by_id_db(db, student_id)
    my_group_avg = await _get_ranking_by_type(db, "my_group_average", student_id, student.group_id, 50)
    tables.append(TournamentTable(
        table_type="my_group_average",
        title="Внутри моей группы (средний балл)",
        students=my_group_avg,
        current_student_rank=_find_student_rank(my_group_avg, student_id),
        total_participants=len(my_group_avg)
    ))
    
    # ДТМ за все время
    dtm_all_time = await _get_ranking_by_type(db, "dtm_all_time", student_id, None, 50)
    tables.append(TournamentTable(
        table_type="dtm_all_time",
        title="ДТМ за все время (по всем группам)",
        students=dtm_all_time,
        current_student_rank=_find_student_rank(dtm_all_time, student_id),
        total_participants=len(dtm_all_time)
    ))
    
    # ДТМ за последний месяц
    dtm_last_month = await _get_ranking_by_type(db, "dtm_last_month", student_id, None, 50)
    tables.append(TournamentTable(
        table_type="dtm_last_month",
        title="ДТМ за последний месяц (по всем группам)",
        students=dtm_last_month,
        current_student_rank=_find_student_rank(dtm_last_month, student_id),
        total_participants=len(dtm_last_month)
    ))
    
    return tables


async def _get_ranking_by_type(
    db: AsyncSession,
    table_type: str,
    student_id: int,
    group_id: Optional[int],
    limit: int
) -> List[StudentRankingInfo]:
    """Получение рейтинга по типу таблицы"""
    
    # Получаем всех студентов или студентов группы
    if group_id:
        students_result = await db.execute(
            select(Student)
            .join(Student.user)
            .filter(Student.group_id == group_id)
        )
    else:
        students_result = await db.execute(
            select(Student).join(Student.user)
        )
    
    students = students_result.scalars().all()
    ranking_data = []
    
    for student in students:
        student_info = StudentRankingInfo(
            student_id=student.student_id,
            full_name=f"{student.user.name} {student.user.surname}",
            group_id=student.group_id
        )
        
        # Рассчитываем данные в зависимости от типа таблицы
        if table_type in ["all_groups_average", "my_group_average"]:
            # Средние баллы по предметам
            try:
                subjects = await get_all_subjects_db(db)
                chemistry_subject = next((s for s in subjects if 'химия' in s.name.lower()), None)
                biology_subject = next((s for s in subjects if 'биология' in s.name.lower()), None)
                
                if chemistry_subject:
                    final_grade_chem = await calculate_final_grade_db(db, student.student_id, chemistry_subject.subject_id)
                    student_info.chemistry_avg = final_grade_chem.get('final_grade', 0.0)
                
                if biology_subject:
                    final_grade_bio = await calculate_final_grade_db(db, student.student_id, biology_subject.subject_id)
                    student_info.biology_avg = final_grade_bio.get('final_grade', 0.0)
                
                # Общий средний балл
                if student_info.chemistry_avg and student_info.biology_avg:
                    student_info.overall_avg = (student_info.chemistry_avg + student_info.biology_avg) / 2
                
            except Exception:
                student_info.chemistry_avg = 0.0
                student_info.biology_avg = 0.0
                student_info.overall_avg = 0.0
                
        elif table_type in ["dtm_all_time", "dtm_last_month"]:
            # ДТМ баллы
            try:
                if table_type == "dtm_all_time":
                    # Все ДТМ результаты
                    dtm_exams = await get_all_dtm_scores_by_student_db(db, student.student_id)
                    if dtm_exams:
                        # Берем лучшие результаты
                        best_exam = max(dtm_exams, key=lambda x: x.total_correct_answers)
                        student_info.chemistry_dtm = best_exam.first_subject_correct_answers
                        student_info.biology_dtm = best_exam.second_subject_correct_answers
                        student_info.general_dtm = best_exam.common_subject_correct_answers
                        student_info.total_dtm = best_exam.total_correct_answers
                else:
                    # За последний месяц
                    last_month = datetime.now() - timedelta(days=30)
                    dtm_recent_result = await db.execute(
                        select(DtmExam)
                        .filter(
                            DtmExam.student_id == student.student_id,
                            DtmExam.exam_date >= last_month
                        )
                        .order_by(DtmExam.exam_date.desc())
                        .limit(1)
                    )
                    recent_exam = dtm_recent_result.scalar_one_or_none()
                    if recent_exam:
                        student_info.last_chemistry_dtm = recent_exam.first_subject_correct_answers
                        student_info.last_biology_dtm = recent_exam.second_subject_correct_answers
                        student_info.last_general_dtm = recent_exam.common_subject_correct_answers
                        student_info.last_total_dtm = recent_exam.total_correct_answers
                        
            except Exception:
                # Устанавливаем значения по умолчанию
                if table_type == "dtm_all_time":
                    student_info.chemistry_dtm = 0.0
                    student_info.biology_dtm = 0.0
                    student_info.general_dtm = 0.0
                    student_info.total_dtm = 0.0
                else:
                    student_info.last_chemistry_dtm = 0.0
                    student_info.last_biology_dtm = 0.0
                    student_info.last_general_dtm = 0.0
                    student_info.last_total_dtm = 0.0
        
        ranking_data.append(student_info)
    
    # Сортируем по соответствующему критерию
    if table_type in ["all_groups_average", "my_group_average"]:
        ranking_data.sort(key=lambda x: x.overall_avg or 0, reverse=True)
    elif table_type == "dtm_all_time":
        ranking_data.sort(key=lambda x: x.total_dtm or 0, reverse=True)
    elif table_type == "dtm_last_month":
        ranking_data.sort(key=lambda x: x.last_total_dtm or 0, reverse=True)
    
    # Устанавливаем ранги
    for i, student_info in enumerate(ranking_data):
        student_info.rank = i + 1
    
    return ranking_data


def _find_student_rank(ranking: List[StudentRankingInfo], student_id: int) -> int:
    """Поиск ранга студента в рейтинге"""
    for i, student_info in enumerate(ranking):
        if student_info.student_id == student_id:
            return i + 1
    return 0


def _get_table_title(table_type: str, group_id: Optional[int]) -> str:
    """Получение заголовка таблицы"""
    titles = {
        "all_groups_average": "По всем группам (средний балл)",
        "my_group_average": "Внутри моей группы (средний балл)",
        "dtm_all_time": "ДТМ за все время (по всем группам)",
        "dtm_last_month": "ДТМ за последний месяц (по всем группам)"
    }
    return titles.get(table_type, "Неизвестная таблица")


async def _get_progress_data(
    db: AsyncSession,
    student_id: int,
    subject: Subject,
    metric_type: str,
    period: str
) -> Dict[str, List[GradePoint]]:
    """Получение данных прогресса для графика"""
    
    data = {}
    
    if metric_type == "current_grades":
        data["current_grades"] = await _get_current_grades_data(db, student_id, subject, period)
    elif metric_type == "tests":
        data["tests"] = await _get_tests_data(db, student_id, subject, period)
    elif metric_type == "dtm":
        data["dtm"] = await _get_dtm_data(db, student_id, subject, period)
    elif metric_type == "section_exams":
        data["section_exams"] = await _get_section_exams_data(db, student_id, subject, period)
    elif metric_type == "block_exams":
        data["block_exams"] = await _get_block_exams_data(db, student_id, subject, period)
    else:
        # Возвращаем все типы данных
        data["current_grades"] = await _get_current_grades_data(db, student_id, subject, period)
        data["tests"] = await _get_tests_data(db, student_id, subject, period)
        data["dtm"] = await _get_dtm_data(db, student_id, subject, period)
        data["section_exams"] = await _get_section_exams_data(db, student_id, subject, period)
        data["block_exams"] = await _get_block_exams_data(db, student_id, subject, period)
    
    return data


async def _calculate_current_average(db: AsyncSession, student_id: int, subject: Subject) -> float:
    """Расчет текущего среднего балла"""
    try:
        final_grade = await calculate_final_grade_db(db, student_id, subject.subject_id)
        return final_grade.get('final_grade', 0.0)
    except:
        return 0.0


def _calculate_improvement_trend(data: List[GradePoint]) -> float:
    """Расчет тренда улучшения"""
    if len(data) < 2:
        return 0.0
    
    # Простой расчет тренда как разница между последним и первым значением
    first_value = data[0].value
    last_value = data[-1].value
    
    if first_value == 0:
        return 0.0
    
    return ((last_value - first_value) / first_value) * 100


def _calculate_last_month_average(data: List[GradePoint]) -> float:
    """Расчет среднего за последний месяц"""
    if not data:
        return 0.0
    
    # Берем последние 3 точки данных (примерно месяц)
    last_month_data = data[-3:] if len(data) >= 3 else data
    return sum(point.value for point in last_month_data) / len(last_month_data)


async def _calculate_avg_current_grade(db: AsyncSession, student_id: int, subject: Subject) -> float:
    """Расчет среднего текущего балла"""
    try:
        current_ratings_result = await db.execute(
            select(func.avg(CurrentRating.current_correct_answers + CurrentRating.second_current_correct_answers))
            .filter(
                CurrentRating.student_id == student_id,
                CurrentRating.subject_id == subject.subject_id
            )
        )
        avg = current_ratings_result.scalar() or 0.0
        # Нормализуем к шкале 0-10
        return min(10.0, max(0.0, avg / 2))
    except:
        return 0.0


async def _calculate_avg_test_score(db: AsyncSession, student_id: int, subject: Subject) -> float:
    """Расчет среднего балла за тесты"""
    try:
        tests_result = await db.execute(
            select(func.avg(TopicTest.correct_answers / TopicTest.question_count * 10))
            .join(Topic, TopicTest.topic_id == Topic.topic_id)
            .join(Block, Topic.block_id == Block.block_id)
            .join(Section, Block.section_id == Section.section_id)
            .filter(
                TopicTest.student_id == student_id,
                Section.subject_id == subject.subject_id,
                TopicTest.question_count > 0
            )
        )
        return tests_result.scalar() or 0.0
    except:
        return 0.0


async def _calculate_avg_dtm_score(db: AsyncSession, student_id: int, subject: Subject) -> float:
    """Расчет среднего ДТМ балла"""
    try:
        dtm_result = await db.execute(
            select(func.avg(DtmExam.total_correct_answers))
            .filter(
                DtmExam.student_id == student_id,
                DtmExam.subject_id == subject.subject_id
            )
        )
        return dtm_result.scalar() or 0.0
    except:
        return 0.0


async def _generate_performance_insights(
    db: AsyncSession, 
    student_id: int, 
    student_stats: StudentStatisticsResponse
) -> PerformanceInsights:
    """Генерация аналитических выводов"""
    
    strengths = []
    areas_for_improvement = []
    recommendations = []
    trends = []
    
    # Анализ сильных сторон
    if student_stats.chemistry.avg_current_grade > 8.0:
        strengths.append("Отличные результаты по химии")
    
    if student_stats.biology.avg_current_grade > 8.0:
        strengths.append("Отличные результаты по биологии")
    
    if student_stats.overall.attendance_rate > 90:
        strengths.append("Высокая посещаемость занятий")
    
    # Анализ областей для улучшения
    if student_stats.chemistry.avg_current_grade < 6.0:
        areas_for_improvement.append("Текущие оценки по химии требуют внимания")
    
    if student_stats.biology.avg_current_grade < 6.0:
        areas_for_improvement.append("Текущие оценки по биологии требуют внимания")
    
    if student_stats.overall.attendance_rate < 80:
        areas_for_improvement.append("Низкая посещаемость занятий")
    
    # Рекомендации
    if len(areas_for_improvement) > 0:
        recommendations.append("Рекомендуется дополнительная работа с преподавателем")
        recommendations.append("Увеличить время на изучение проблемных тем")
    
    if student_stats.overall.attendance_rate < 90:
        recommendations.append("Повысить посещаемость занятий")
    
    # Анализ трендов
    chemistry_trend = _analyze_trend(student_stats.chemistry.current_grades)
    biology_trend = _analyze_trend(student_stats.biology.current_grades)
    
    trends.append(TrendAnalysis(
        metric_name="Химия - текущие оценки",
        current_value=student_stats.chemistry.avg_current_grade,
        previous_value=student_stats.chemistry.current_grades[0].value if student_stats.chemistry.current_grades else 0,
        change_percentage=chemistry_trend,
        trend="improving" if chemistry_trend > 5 else "declining" if chemistry_trend < -5 else "stable"
    ))
    
    trends.append(TrendAnalysis(
        metric_name="Биология - текущие оценки", 
        current_value=student_stats.biology.avg_current_grade,
        previous_value=student_stats.biology.current_grades[0].value if student_stats.biology.current_grades else 0,
        change_percentage=biology_trend,
        trend="improving" if biology_trend > 5 else "declining" if biology_trend < -5 else "stable"
    ))
    
    return PerformanceInsights(
        student_id=student_id,
        strengths=strengths,
        areas_for_improvement=areas_for_improvement,
        recommendations=recommendations,
        trends=trends
    )


def _analyze_trend(data: List[GradePoint]) -> float:
    """Анализ тренда данных"""
    if len(data) < 2:
        return 0.0
    
    first_half = data[:len(data)//2]
    second_half = data[len(data)//2:]
    
    first_avg = sum(p.value for p in first_half) / len(first_half)
    second_avg = sum(p.value for p in second_half) / len(second_half)
    
    if first_avg == 0:
        return 0.0
    
    return ((second_avg - first_avg) / first_avg) * 100


async def _get_comparison_data(db: AsyncSession, student_id: int) -> Dict[str, Any]:
    """Получение данных для сравнения"""
    
    # Получаем среднее по группе
    student = await get_student_by_id_db(db, student_id)
    group_students = await get_students_by_group_db(db, student.group_id)
    
    comparison_data = {
        "group_average": 0.0,
        "class_rank": 0,
        "total_students_in_group": len(group_students)
    }
    
    return comparison_data