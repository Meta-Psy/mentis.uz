from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# Импорты базы данных и моделей
from app.database import get_db
from app.database.models.user import Teacher, Student, User, StudentSkill
from app.database.models.academic import Group, Subject
from app.database.models.assessment import Comments, CommentType, Attendance, CurrentRating, TopicTest

# Импорты сервисов
from app.services.auth.teacher_service import (
    get_teacher_by_id_db,
    get_teacher_info_db,
    get_teacher_subjects_db
)
from app.services.auth.student_service import (
    get_students_by_group_db,
    get_student_by_id_db
)
from app.services.assessment.comment_service import (
    add_comment_db,
    update_comment_db,
    get_all_comments_by_student_db
)
from app.services.assessment.attendance_service import (
    get_attendance_statistics_db
)
from app.services.assessment.grade_service import (
    get_avg_topic_score_for_student_db,
    get_all_dtm_scores_by_student_db
)

# Импорты схем
from app.schemas.assessment.teacher_dashboard import (
    TeacherDashboardResponse,
    TeacherProfileInfo,
    GroupStudentsResponse,
    StudentDetailInfo,
    StudentSkillAnalysis,
    StudentTestStatistics,
    StudentAttendanceInfo,
    StudentCommentInfo,
    GroupScheduleInfo,
    UpdateCommentRequest,
    GetGroupStudentsRequest,
    StudentAnalyticsResponse,
    CriterionAnalysis,
    TeacherAPIHealthResponse
)
from app.database.models.user import StudentSkill

# Создание роутера
router = APIRouter()

# ===========================================
# ПОЛУЧЕНИЕ ПРОФИЛЯ ПРЕПОДАВАТЕЛЯ
# ===========================================

@router.get("/profile/{teacher_id}", 
            response_model=TeacherDashboardResponse,
            summary="Получить профиль преподавателя",
            description="Получение полного профиля преподавателя с группами и расписанием")
async def get_teacher_profile(
    teacher_id: int = Path(..., gt=0, description="ID преподавателя"),
    db: AsyncSession = Depends(get_db)
) -> TeacherDashboardResponse:
    """Получение профиля преподавателя"""
    
    try:
        # Получаем преподавателя
        teacher = await get_teacher_by_id_db(db, teacher_id)
        
        # Получаем информацию о преподавателе
        try:
            teacher_info = await get_teacher_info_db(db, teacher_id)
        except HTTPException:
            teacher_info = None
        
        # Получаем предметы преподавателя
        subjects = await get_teacher_subjects_db(db, teacher_id)
        subject_names = [subject.name for subject in subjects]
        
        # Получаем группы преподавателя
        from sqlalchemy import select
        groups_result = await db.execute(
            select(Group).filter(Group.teacher_id == teacher_id)
        )
        groups = groups_result.scalars().all()
        
        # Формируем расписание групп
        schedule = []
        total_students = 0
        
        for group in groups:
            # Получаем количество студентов в группе
            students_result = await db.execute(
                select(Student).filter(Student.group_id == group.group_id)
            )
            students = students_result.scalars().all()
            student_count = len(students)
            total_students += student_count
            
            # Парсим расписание (предполагаем, что оно хранится в формате JSON)
            days = ["Пн", "Ср", "Пт"]  # Значение по умолчанию
            start_time = "16:00"  # Значение по умолчанию
            
            try:
                if teacher.teacher_schedule:
                    schedule_data = json.loads(teacher.teacher_schedule)
                    group_schedule = schedule_data.get(str(group.group_id), {})
                    days = group_schedule.get("days", days)
                    start_time = group_schedule.get("start_time", start_time)
            except (json.JSONDecodeError, AttributeError):
                pass
            
            schedule_info = GroupScheduleInfo(
                group_id=group.group_id,
                group_name=group.name,
                days=days,
                start_time=start_time,
                student_count=student_count,
                subject_name=group.subject.name if group.subject else ""
            )
            schedule.append(schedule_info)
        
        # Формируем профиль преподавателя
        teacher_profile = TeacherProfileInfo(
            teacher_id=teacher.teacher_id,
            full_name=f"{teacher.user.surname} {teacher.user.name}",
            surname=teacher.user.surname,
            email=teacher.user.email,
            phone=teacher.user.phone,
            photo=teacher.user.photo,
            education_background=teacher_info.education_background if teacher_info else None,
            years_experience=teacher_info.years_experiense if teacher_info else None,
            certifications=teacher_info.certifications if teacher_info else None,
            languages=teacher_info.languages if teacher_info else None,
            subjects=subject_names,
            schedule=schedule
        )
        
        return TeacherDashboardResponse(
            teacher_profile=teacher_profile,
            groups=schedule,
            total_students=total_students
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения профиля преподавателя: {str(e)}"
        )

# ===========================================
# ПОЛУЧЕНИЕ СТУДЕНТОВ ГРУППЫ
# ===========================================

@router.get("/group/{group_id}/students", 
            response_model=GroupStudentsResponse,
            summary="Получить студентов группы",
            description="Получение списка студентов группы с детальной информацией")
async def get_group_students(
    group_id: int = Path(..., gt=0, description="ID группы"),
    include_inactive: bool = Query(False, description="Включить неактивных студентов"),
    sort_by: Optional[str] = Query("name", description="Поле для сортировки"),
    sort_order: Optional[str] = Query("asc", description="Порядок сортировки"),
    db: AsyncSession = Depends(get_db)
) -> GroupStudentsResponse:
    """Получение студентов группы"""
    
    try:
        # Получаем группу
        from sqlalchemy import select
        group_result = await db.execute(
            select(Group).filter(Group.group_id == group_id)
        )
        group = group_result.scalar_one_or_none()
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Группа не найдена"
            )
        
        # Получаем студентов группы
        students = await get_students_by_group_db(db, group_id)
        
        # Фильтруем неактивных студентов если нужно
        if not include_inactive:
            students = [s for s in students if s.student_status.value == "active"]
        
        # Формируем детальную информацию о каждом студенте
        student_details = []
        
        for student in students:
            # Получаем статистику тестов
            test_stats = await _get_student_test_statistics(db, student.student_id)
            
            # Получаем статистику посещаемости
            attendance_stats = await _get_student_attendance_statistics(db, student.student_id, group.subject_id)
            
            # Получаем анализ навыков
            skill_analysis = await _get_student_skill_analysis(db, student.student_id)
            
            # Получаем комментарии
            comment_info = await _get_student_comment_info(db, student.student_id)
            
            student_detail = StudentDetailInfo(
                id=student.student_id,
                full_name=f"{student.user.surname} {student.user.name}",
                photo=student.user.photo,
                email=student.user.email,
                phone=student.user.phone,
                test_statistics=test_stats,
                attendance_info=attendance_stats,
                skill_analysis=skill_analysis,
                comment_info=comment_info,
                student_status=student.student_status,
                last_seen=student.last_login
            )
            
            student_details.append(student_detail)
        
        # Сортировка
        if sort_by == "name":
            student_details.sort(
                key=lambda x: x.name, 
                reverse=(sort_order == "desc")
            )
        elif sort_by == "score":
            student_details.sort(
                key=lambda x: x.test_statistics.average_score, 
                reverse=(sort_order == "desc")
            )
        elif sort_by == "attendance":
            student_details.sort(
                key=lambda x: x.attendance_info.attendance_rate, 
                reverse=(sort_order == "desc")
            )
        elif sort_by == "last_seen":
            student_details.sort(
                key=lambda x: x.last_seen or datetime.min, 
                reverse=(sort_order == "desc")
            )
        
        return GroupStudentsResponse(
            group_id=group_id,
            group_name=group.name,
            students=student_details,
            total_count=len(student_details)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения студентов группы: {str(e)}"
        )

# ===========================================
# ОБНОВЛЕНИЕ КОММЕНТАРИЯ СТУДЕНТА
# ===========================================

@router.post("/student/comment", 
             summary="Обновить комментарий студента",
             description="Добавление или обновление комментария о студенте")
async def update_student_comment(
    request: UpdateCommentRequest,
    teacher_id: int = Query(..., gt=0, description="ID преподавателя"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Обновление комментария студента"""
    
    try:
        # Проверяем существование студента
        student = await get_student_by_id_db(db, request.student_id)
        
        # Проверяем существование преподавателя
        teacher = await get_teacher_by_id_db(db, teacher_id)
        
        # Проверяем, есть ли уже комментарий
        try:
            existing_comments = await get_all_comments_by_student_db(db, request.student_id)
            teacher_comment = next(
                (c for c in existing_comments if c.teacher_id == teacher_id), 
                None
            )
            
            if teacher_comment:
                # Обновляем существующий комментарий
                await update_comment_db(
                    db=db,
                    comment_id=teacher_comment.comment_id,
                    comment_text=request.comment_text,
                    comment_type=CommentType(request.comment_type)
                )
            else:
                # Создаем новый комментарий
                await add_comment_db(
                    db=db,
                    teacher_id=teacher_id,
                    student_id=request.student_id,
                    comment_text=request.comment_text,
                    comment_type=CommentType(request.comment_type)
                )
                
        except HTTPException:
            # Создаем новый комментарий
            await add_comment_db(
                db=db,
                teacher_id=teacher_id,
                student_id=request.student_id,
                comment_text=request.comment_text,
                comment_type=CommentType(request.comment_type)
            )
        
        return {"status": "success", "message": "Комментарий сохранен"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сохранения комментария: {str(e)}"
        )

# ===========================================
# ПОЛУЧЕНИЕ АНАЛИТИКИ СТУДЕНТА
# ===========================================

@router.get("/student/{student_id}/analytics", 
            response_model=StudentAnalyticsResponse,
            summary="Получить аналитику студента",
            description="Получение детальной аналитики по критериям для студента")
async def get_student_analytics(
    student_id: int = Path(..., gt=0, description="ID студента"),
    db: AsyncSession = Depends(get_db)
) -> StudentAnalyticsResponse:
    """Получение аналитики студента"""
    
    try:
        # Проверяем существование студента
        student = await get_student_by_id_db(db, student_id)
        
        # Получаем анализ навыков
        skill_analysis = await _get_student_skill_analysis(db, student_id)
        
        # Формируем анализ по критериям
        criteria_analysis = []
        total_questions = 0
        total_correct = 0
        
        for i in range(8):
            correct = skill_analysis.correct_answers[i]
            incorrect = skill_analysis.incorrect_answers[i]
            total = correct + incorrect
            accuracy = skill_analysis.get_criterion_accuracy(i)
            
            total_questions += total
            total_correct += correct
            
            criterion = CriterionAnalysis(
                criterion_number=i + 1,
                correct_count=correct,
                incorrect_count=incorrect,
                total_count=total,
                accuracy_percentage=accuracy * 100
            )
            criteria_analysis.append(criterion)
        
        overall_accuracy = total_correct / total_questions if total_questions > 0 else 0.0
        
        return StudentAnalyticsResponse(
            student_id=student_id,
            criteria_analysis=criteria_analysis,
            overall_accuracy=overall_accuracy * 100,
            total_questions=total_questions,
            last_updated=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения аналитики студента: {str(e)}"
        )

# ===========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ===========================================

async def _get_student_test_statistics(db: AsyncSession, student_id: int) -> StudentTestStatistics:
    """Получение статистики тестов студента"""
    
    try:
        from sqlalchemy import select, func
        
        # Подсчитываем активных преподавателей
        active_teachers_result = await db.execute(
            select(func.count(Teacher.teacher_id))
            .filter(Teacher.teacher_status == "active")
        )
        active_teachers = active_teachers_result.scalar() or 0
        
        # Подсчитываем общее количество групп
        total_groups_result = await db.execute(
            select(func.count(Group.group_id))
        )
        total_groups = total_groups_result.scalar() or 0
        
        return TeacherAPIHealthResponse(
            status="healthy",
            service="teacher-api",
            version="1.0.0",
            timestamp=datetime.now(),
            active_teachers=active_teachers,
            total_groups=total_groups
        )
        
    except Exception as e:
        return TeacherAPIHealthResponse(
            status="unhealthy",
            service="teacher-api",
            version="1.0.0",
            timestamp=datetime.now(),
            active_teachers=0,
            total_groups=0
        )
        
        # Получаем статистику по тестам тем
        topic_tests_result = await db.execute(
            select(
                func.count(TopicTest.topic_test_id).label("total"),
                func.avg(TopicTest.correct_answers / TopicTest.question_count * 10).label("avg_score"),
                func.max(TopicTest.correct_answers / TopicTest.question_count * 10).label("best_score"),
                func.max(TopicTest.attempt_date).label("last_test")
            ).filter(TopicTest.student_id == student_id, TopicTest.question_count > 0)
        )
        topic_stats = topic_tests_result.first()
        
        # Получаем DTM балл
        dtm_scores = await get_all_dtm_scores_by_student_db(db, student_id)
        dtm_score = dtm_scores[-1].total_correct_answers if dtm_scores else None
        
        return StudentTestStatistics(
            total_tests=topic_stats.total or 0,
            completed_tests=topic_stats.total or 0,
            pending_tests=0,  # Будет рассчитано отдельно если нужно
            average_score=float(topic_stats.avg_score or 0.0),
            best_score=float(topic_stats.best_score or 0.0),
            dtm_score=float(dtm_score) if dtm_score else None,
            last_test_date=topic_stats.last_test
        )
        
    except Exception:
        return StudentTestStatistics()


async def _get_student_attendance_statistics(db: AsyncSession, student_id: int, subject_id: int) -> StudentAttendanceInfo:
    """Получение статистики посещаемости студента"""
    
    try:
        attendance_stats = await get_attendance_statistics_db(db, student_id, subject_id)
        
        # Получаем дату последнего посещения
        from sqlalchemy import select, desc
        last_attendance_result = await db.execute(
            select(Attendance.lesson_date_time)
            .filter(Attendance.student_id == student_id, Attendance.subject_id == subject_id)
            .order_by(desc(Attendance.lesson_date_time))
            .limit(1)
        )
        last_attendance = last_attendance_result.scalar_one_or_none()
        
        return StudentAttendanceInfo(
            total_lessons=attendance_stats["total_lessons"],
            present_count=attendance_stats["present_count"],
            absent_count=attendance_stats["absent_count"],
            late_count=attendance_stats["late_count"],
            attendance_rate=attendance_stats["attendance_rate"] / 100.0,
            last_attendance_date=last_attendance
        )
        
    except Exception:
        return StudentAttendanceInfo()


async def _get_student_skill_analysis(db: AsyncSession, student_id: int) -> StudentSkillAnalysis:
    """Получение анализа навыков студента"""
    
    try:
        from sqlalchemy import select
        
        # Получаем данные о навыках студента
        skills_result = await db.execute(
            select(StudentSkill).filter(StudentSkill.student_id == student_id)
        )
        student_skills = skills_result.scalars().all()
        
        # Агрегируем данные по всем навыкам
        correct_answers = [0] * 8
        incorrect_answers = [0] * 8
        
        for skill in student_skills:
            if skill.correct and len(skill.correct) >= 8:
                for i in range(8):
                    correct_answers[i] += skill.correct[i]
            
            if skill.mistakes and len(skill.mistakes) >= 8:
                for i in range(8):
                    incorrect_answers[i] += skill.mistakes[i]
        
        return StudentSkillAnalysis(
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers
        )
        
    except Exception:
        return StudentSkillAnalysis()


async def _get_student_comment_info(db: AsyncSession, student_id: int) -> StudentCommentInfo:
    """Получение информации о комментариях студента"""
    
    try:
        comments = await get_all_comments_by_student_db(db, student_id)
        
        if comments:
            # Берем последний комментарий
            latest_comment = comments[-1]
            return StudentCommentInfo(
                comment_id=latest_comment.comment_id,
                comment_text=latest_comment.comment_text,
                comment_type=latest_comment.comment_type.value,
                last_updated=latest_comment.comment_date
            )
        
        return StudentCommentInfo()
        
    except Exception:
        return StudentCommentInfo()
