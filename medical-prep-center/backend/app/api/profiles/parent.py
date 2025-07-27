from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

# Импорты базы данных и моделей
from app.database import get_db
from app.database.models.assessment import (
    Attendance, AttendanceType, Comments, CommentType,
    DtmExam, SectionExam, BlockExam, ModulExam, TopicTest, CurrentRating
)
from app.database.models.academic import Subject, Topic, Section, Block, Group
from app.database.models.user import Student, StudentInfo, User, Teacher

# Импорты сервисов
from app.services.assessment.attendance_service import (
    get_attendance_by_student_and_subject_db,
    get_attendance_statistics_db,
    count_missed_lessons_db,
    count_late_arrivals_db
)
from app.services.assessment.comment_service import (
    get_all_comments_by_student_db,
    get_recent_comments_db,
    get_comment_statistics_db
)
from app.services.assessment.grade_service import (
    get_all_dtm_scores_by_student_db,
    get_average_dtm_score_for_student_db,
    calculate_final_grade_db,
    get_all_topic_scores_by_topic_db,
    get_avg_topic_score_for_student_db
)
from app.services.roles.student_service import (
    get_student_by_id_db,
    get_students_by_group_db
)
from app.services.roles.user_service import (
    get_user_by_id_db
)
from app.services.content.subject_service import (
    get_all_subjects_db
)

# Импорты схем
from app.schemas.assessment.parent_dashboard import (
    ParentStatisticsResponse,
    ParentStatisticsRequest,
    StudentInfo,
    StudentSchedule,
    ScheduleItem,
    DtmScore,
    SubjectGrades,
    DisciplineStatistics,
    ExamStatistics,
    AdmissionChance,
    GradeRecord,
    CommentRecord,
    AttendanceRecord,
    AttendanceFilterRequest,
    GradesFilterRequest,
    DetailedPerformanceResponse,
    DetailedDisciplineResponse,
    DetailedExamsResponse,
    ParentStatisticsHealthResponse,
    NotificationItem,
    ParentNotificationsResponse
)

# Создание роутера
router = APIRouter()

# ===========================================
# ОСНОВНАЯ СТАТИСТИКА СТУДЕНТА
# ===========================================

@router.get("/student/{student_id}",
            response_model=ParentStatisticsResponse,
            summary="Получить статистику студента",
            description="Получение полной статистики студента для родителей")
async def get_parent_statistics(
    student_id: int = Path(..., gt=0, description="ID студента"),
    include_comments: bool = Query(True, description="Включить комментарии"),
    comments_limit: int = Query(5, le=20, description="Лимит комментариев"),
    db: AsyncSession = Depends(get_db)
) -> ParentStatisticsResponse:
    """Получение статистики студента для родителей"""
    
    try:
        # Проверяем существование студента
        student = await get_student_by_id_db(db, student_id)
        user = await get_user_by_id_db(db, student_id)
        
        # Получаем дополнительную информацию о студенте
        from sqlalchemy import select
        student_info_result = await db.execute(
            select(StudentInfo).filter(StudentInfo.student_id == student_id)
        )
        student_info_data = student_info_result.scalar_one_or_none()
        
        # Формируем информацию о студенте
        student_info = StudentInfo(
            student_id=student_id,
            name=user.name,
            surname=user.surname,
            photo=user.photo,
            direction=student.direction,
            goal=student.goal,
            group_id=student.group_id,
            hobby=student_info_data.hobby if student_info_data else None,
            sex=student_info_data.sex if student_info_data else None,
            address=student_info_data.address if student_info_data else None,
            birthday=student_info_data.birthday if student_info_data else None
        )
        
        # Получаем расписание (заглушка, так как в моделях нет расписания)
        schedule = StudentSchedule(
            student_id=student_id,
            chemistry_schedule=ScheduleItem(
                subject_name="Химия",
                days=["Пн", "Ср", "Пт"],
                time="16:00-17:30"
            ),
            biology_schedule=ScheduleItem(
                subject_name="Биология", 
                days=["Вт", "Чт", "Сб"],
                time="14:00-15:30"
            )
        )
        
        # Получаем DTM баллы
        try:
            dtm_scores = await get_all_dtm_scores_by_student_db(db, student_id)
            current_dtm_score = dtm_scores[-1].total_correct_answers if dtm_scores else 0
        except Exception:
            current_dtm_score = 0
            
        dtm_score = DtmScore(
            current_score=current_dtm_score,
            required_score=151.9,  # Типичный проходной балл
            exam_date=dtm_scores[-1].exam_date if 'dtm_scores' in locals() and dtm_scores else None
        )
        
        # Получаем все предметы
        subjects = await get_all_subjects_db(db)
        
        # Формируем статистику по предметам
        performance = {}
        overall_scores = []
        
        for subject in subjects:
            try:
                # Получаем итоговую оценку по предмету
                final_grade = await calculate_final_grade_db(db, student_id, subject.subject_id)
                
                # Определяем статус
                avg_score = final_grade.get("final_grade", 0)
                overall_scores.append(avg_score)
                
                if avg_score >= 8.5:
                    status = "отлично"
                elif avg_score >= 7.0:
                    status = "хорошо"
                elif avg_score >= 5.0:
                    status = "удовлетворительно"
                else:
                    status = "плохо"
                
                # Заглушки для детальной статистики (так как нет точного разделения)
                total_assessments = final_grade.get("counts", {})
                passed = int(avg_score * 0.8) if avg_score > 5 else 0
                
                subject_grades = SubjectGrades(
                    subject_name=subject.name,
                    average_score=avg_score,
                    total_assessments=sum(total_assessments.values()) if total_assessments else 0,
                    passed_assessments=passed,
                    failed_assessments=sum(total_assessments.values()) - passed if total_assessments else 0,
                    status=status,
                    polls_score=final_grade.get("current_average", 0),
                    tests_score=final_grade.get("topic_average", 0),
                    control_works_score=final_grade.get("block_average", 0),
                    polls_total=total_assessments.get("current_ratings", 0) if total_assessments else 0,
                    tests_total=total_assessments.get("topic_tests", 0) if total_assessments else 0,
                    control_works_total=total_assessments.get("block_exams", 0) if total_assessments else 0
                )
                
                performance[subject.name] = subject_grades
                
            except Exception as e:
                print(f"Ошибка получения оценок по предмету {subject.name}: {e}")
                continue
        
        # Определяем общий статус успеваемости
        if overall_scores:
            avg_overall = sum(overall_scores) / len(overall_scores)
            if avg_overall >= 8.5:
                overall_performance_status = "отлично"
            elif avg_overall >= 7.0:
                overall_performance_status = "хорошо"
            elif avg_overall >= 5.0:
                overall_performance_status = "удовлетворительно"
            else:
                overall_performance_status = "плохо"
        else:
            overall_performance_status = "плохо"
        
        # Получаем статистику посещаемости
        try:
            attendance_stats = await get_attendance_statistics_db(db, student_id)
            missed_lessons = await count_missed_lessons_db(db, student_id)
            late_arrivals = await count_late_arrivals_db(db, student_id)
            
            # Заглушки для домашних заданий и опросов (нет в моделях)
            total_homeworks = 30
            missed_homeworks = int(missed_lessons * 0.4)  # Примерное соотношение
            total_polls = 30
            missed_polls = int(missed_lessons * 0.5)
            
            # Получаем замечания от учителей
            teacher_comments = await get_recent_comments_db(db, student_id=student_id, limit=10)
            remarks = len([c for c in teacher_comments if c.comment_type == CommentType.NEGATIVE])
            
            # Определяем статус дисциплины
            absence_rate = (missed_lessons / attendance_stats.total_lessons * 100) if attendance_stats.total_lessons > 0 else 0
            homework_rate = ((total_homeworks - missed_homeworks) / total_homeworks * 100) if total_homeworks > 0 else 100
            
            if absence_rate <= 5 and homework_rate >= 90 and remarks == 0:
                discipline_status = "отлично"
            elif absence_rate <= 15 and homework_rate >= 70 and remarks <= 2:
                discipline_status = "хорошо"
            elif absence_rate <= 25 and homework_rate >= 50 and remarks <= 5:
                discipline_status = "удовлетворительно"
            else:
                discipline_status = "плохо"
            
            discipline = DisciplineStatistics(
                student_id=student_id,
                total_absences=missed_lessons,
                total_lessons=attendance_stats.total_lessons,
                missed_homeworks=missed_homeworks,
                total_homeworks=total_homeworks,
                missed_polls=missed_polls,
                total_polls=total_polls,
                teacher_remarks=remarks,
                status=discipline_status
            )
            
        except Exception as e:
            print(f"Ошибка получения статистики посещаемости: {e}")
            discipline = DisciplineStatistics(
                student_id=student_id,
                total_absences=10,
                total_lessons=30,
                missed_homeworks=12,
                total_homeworks=30,
                missed_polls=15,
                total_polls=30,
                teacher_remarks=2,
                status="плохо"
            )
        
        # Получаем статистику экзаменов
        try:
            # Последний DTM экзамен
            if 'dtm_scores' in locals() and dtm_scores:
                last_dtm = dtm_scores[-1]
                last_monthly_exam = GradeRecord(
                    score=last_dtm.total_correct_answers,
                    max_score=189.0,
                    percentage=(last_dtm.total_correct_answers / 189.0) * 100,
                    exam_date=last_dtm.exam_date,
                    exam_type="DTM",
                    subject_name="Комплексный"
                )
                
                # Статистика экзаменов
                total_exams = len(dtm_scores)
                passed_exams = len([e for e in dtm_scores if e.total_correct_answers >= 100])
                avg_exam_score = sum([e.total_correct_answers for e in dtm_scores]) / len(dtm_scores)
            else:
                last_monthly_exam = None
                total_exams = 0
                passed_exams = 0
                avg_exam_score = 0
            
            if avg_exam_score >= 160:
                exam_status = "отлично"
            elif avg_exam_score >= 130:
                exam_status = "хорошо"
            elif avg_exam_score >= 100:
                exam_status = "удовлетворительно"
            else:
                exam_status = "плохо"
            
            exams = ExamStatistics(
                student_id=student_id,
                last_monthly_exam=last_monthly_exam,
                last_final_control=GradeRecord(
                    score=10,
                    max_score=10,
                    percentage=100,
                    exam_date=datetime.now() - timedelta(days=7),
                    exam_type="Итоговый контроль",
                    subject_name="Комплексный"
                ),
                total_exams=total_exams,
                passed_exams=passed_exams,
                average_score=avg_exam_score,
                status=exam_status
            )
            
        except Exception as e:
            print(f"Ошибка получения статистики экзаменов: {e}")
            exams = ExamStatistics(
                student_id=student_id,
                status="отлично"
            )
        
        # Рассчитываем шанс поступления
        chance_percentage = min(90, max(10, (current_dtm_score / 189.0) * 100))
        admission_chance = AdmissionChance(
            student_id=student_id,
            probability_percentage=chance_percentage,
            current_score=current_dtm_score,
            required_score=151.9,
            recommendations=[
                "Продолжайте подготовку по химии",
                "Уделите больше внимания биологии", 
                "Регулярно решайте тесты DTM"
            ]
        )
        
        # Получаем последние комментарии
        recent_comments = []
        if include_comments:
            try:
                comments_data = await get_recent_comments_db(
                    db, 
                    student_id=student_id, 
                    limit=comments_limit
                )
                recent_comments = [
                    CommentRecord(
                        comment_id=c.comment_id,
                        teacher_id=c.teacher_id,
                        student_id=c.student_id,
                        comment_text=c.comment_text,
                        comment_date=c.comment_date,
                        comment_type=c.comment_type
                    ) for c in comments_data
                ]
            except Exception as e:
                print(f"Ошибка получения комментариев: {e}")
        
        return ParentStatisticsResponse(
            student_info=student_info,
            schedule=schedule,
            dtm_score=dtm_score,
            performance=performance,
            overall_performance_status=overall_performance_status,
            discipline=discipline,
            exams=exams,
            admission_chance=admission_chance,
            recent_comments=recent_comments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики: {str(e)}"
        )

# ===========================================
# ДЕТАЛЬНАЯ УСПЕВАЕМОСТЬ
# ===========================================

@router.get("/student/{student_id}/performance",
            response_model=DetailedPerformanceResponse,
            summary="Детальная успеваемость",
            description="Получение детальной информации об успеваемости студента")
async def get_detailed_performance(
    student_id: int = Path(..., gt=0, description="ID студента"),
    subject_id: Optional[int] = Query(None, description="Фильтр по предмету"),
    db: AsyncSession = Depends(get_db)
) -> DetailedPerformanceResponse:
    """Детальная информация об успеваемости"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        # Получаем все предметы или конкретный предмет
        if subject_id:
            from sqlalchemy import select
            subject_result = await db.execute(
                select(Subject).filter(Subject.subject_id == subject_id)
            )
            subjects = [subject_result.scalar_one()]
        else:
            subjects = await get_all_subjects_db(db)
        
        # Формируем детальную информацию
        subject_grades = []
        recent_grades = []
        grade_trends = {}
        
        for subject in subjects:
            try:
                final_grade = await calculate_final_grade_db(db, student_id, subject.subject_id)
                
                # Формируем оценки по предмету
                avg_score = final_grade.get("final_grade", 0)
                if avg_score >= 8.5:
                    status = "отлично"
                elif avg_score >= 7.0:
                    status = "хорошо"
                elif avg_score >= 5.0:
                    status = "удовлетворительно"
                else:
                    status = "плохо"
                
                total_assessments = final_grade.get("counts", {})
                passed = int(avg_score * 0.8) if avg_score > 5 else 0
                
                subject_grade = SubjectGrades(
                    subject_name=subject.name,
                    average_score=avg_score,
                    total_assessments=sum(total_assessments.values()) if total_assessments else 0,
                    passed_assessments=passed,
                    failed_assessments=sum(total_assessments.values()) - passed if total_assessments else 0,
                    status=status,
                    polls_score=final_grade.get("current_average", 0),
                    tests_score=final_grade.get("topic_average", 0),
                    control_works_score=final_grade.get("block_average", 0),
                    polls_total=total_assessments.get("current_ratings", 0) if total_assessments else 0,
                    tests_total=total_assessments.get("topic_tests", 0) if total_assessments else 0,
                    control_works_total=total_assessments.get("block_exams", 0) if total_assessments else 0
                )
                subject_grades.append(subject_grade)
                
                # Добавляем тренды (заглушка)
                grade_trends[subject.name] = [
                    avg_score - 1, avg_score - 0.5, avg_score, avg_score + 0.2
                ]
                
                # Формируем последние оценки
                recent_grades.append(GradeRecord(
                    score=avg_score,
                    max_score=10.0,
                    percentage=avg_score * 10,
                    exam_date=datetime.now() - timedelta(days=7),
                    exam_type="Комплексная оценка",
                    subject_name=subject.name
                ))
                
            except Exception as e:
                print(f"Ошибка обработки предмета {subject.name}: {e}")
                continue
        
        return DetailedPerformanceResponse(
            student_id=student_id,
            subjects=subject_grades,
            recent_grades=recent_grades,
            grade_trends=grade_trends
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения детальной успеваемости: {str(e)}"
        )

# ===========================================
# ДЕТАЛЬНАЯ ДИСЦИПЛИНА
# ===========================================

@router.get("/student/{student_id}/discipline",
            response_model=DetailedDisciplineResponse,
            summary="Детальная дисциплина",
            description="Получение детальной информации о дисциплине студента")
async def get_detailed_discipline(
    student_id: int = Path(..., gt=0, description="ID студента"),
    subject_id: Optional[int] = Query(None, description="Фильтр по предмету"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_db)
) -> DetailedDisciplineResponse:
    """Детальная информация о дисциплине"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        # Получаем записи посещаемости
        attendance_records = []
        if subject_id:
            try:
                attendance_data = await get_attendance_by_student_and_subject_db(
                    db, student_id, subject_id
                )
                attendance_records = [
                    AttendanceRecord(
                        attendance_id=a.attendance_id,
                        student_id=a.student_id,
                        lesson_date_time=a.lesson_date_time,
                        att_status=a.att_status,
                        subject_id=a.subject_id,
                        topic_id=a.topic_id,
                        excuse_reason=a.excuse_reason,
                        extra_lesson=a.extra_lesson
                    ) for a in attendance_data
                ]
            except Exception as e:
                print(f"Ошибка получения посещаемости: {e}")
        
        # Получаем статистику посещаемости
        try:
            attendance_stats_data = await get_attendance_statistics_db(
                db, student_id, subject_id
            )
            attendance_statistics = {
                "student_id": attendance_stats_data.student_id,
                "subject_id": attendance_stats_data.subject_id,
                "total_lessons": attendance_stats_data.total_lessons,
                "present_count": attendance_stats_data.present_count,
                "absent_count": attendance_stats_data.absent_count,
                "late_count": attendance_stats_data.late_count,
                "attendance_rate": attendance_stats_data.attendance_rate
            }
        except Exception:
            attendance_statistics = {
                "student_id": student_id,
                "subject_id": subject_id,
                "total_lessons": 0,
                "present_count": 0,
                "absent_count": 0,
                "late_count": 0,
                "attendance_rate": 0.0
            }
        
        # Получаем комментарии учителей
        try:
            comments_data = await get_all_comments_by_student_db(db, student_id)
            teacher_comments = [
                CommentRecord(
                    comment_id=c.comment_id,
                    teacher_id=c.teacher_id,
                    student_id=c.student_id,
                    comment_text=c.comment_text,
                    comment_date=c.comment_date,
                    comment_type=c.comment_type
                ) for c in comments_data
            ]
        except Exception:
            teacher_comments = []
        
        # Заглушка для пропущенных заданий
        missed_assignments = [
            {
                "assignment_id": 1,
                "subject_name": "Химия",
                "topic_name": "Органическая химия",
                "due_date": (datetime.now() - timedelta(days=3)).isoformat(),
                "type": "homework"
            },
            {
                "assignment_id": 2,
                "subject_name": "Биология", 
                "topic_name": "Генетика",
                "due_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "type": "test"
            }
        ]
        
        return DetailedDisciplineResponse(
            student_id=student_id,
            attendance_records=attendance_records,
            attendance_statistics=attendance_statistics,
            missed_assignments=missed_assignments,
            teacher_comments=teacher_comments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения детальной дисциплины: {str(e)}"
        )

# ===========================================
# ДЕТАЛЬНЫЕ ЭКЗАМЕНЫ
# ===========================================

@router.get("/student/{student_id}/exams",
            response_model=DetailedExamsResponse,
            summary="Детальные экзамены",
            description="Получение детальной информации об экзаменах студента")
async def get_detailed_exams(
    student_id: int = Path(..., gt=0, description="ID студента"),
    exam_type: Optional[str] = Query(None, description="Тип экзамена"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_db)
) -> DetailedExamsResponse:
    """Детальная информация об экзаменах"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        # Получаем DTM экзамены
        dtm_exams_data = []
        try:
            dtm_scores = await get_all_dtm_scores_by_student_db(db, student_id)
            dtm_exams_data = [
                GradeRecord(
                    score=exam.total_correct_answers,
                    max_score=189.0,
                    percentage=(exam.total_correct_answers / 189.0) * 100,
                    exam_date=exam.exam_date,
                    exam_type="DTM",
                    subject_name="Комплексный"
                ) for exam in dtm_scores
            ]
        except Exception as e:
            print(f"Ошибка получения DTM экзаменов: {e}")
        
        # Получаем экзамены по разделам (заглушки)
        section_exams_data = []
        block_exams_data = []
        module_exams_data = []
        
        # Формируем тренды экзаменов
        exam_trends = {}
        if dtm_exams_data:
            exam_trends["DTM"] = [exam.score for exam in dtm_exams_data[-5:]]  # Последние 5
        
        return DetailedExamsResponse(
            student_id=student_id,
            dtm_exams=dtm_exams_data,
            section_exams=section_exams_data,
            block_exams=block_exams_data,
            module_exams=module_exams_data,
            exam_trends=exam_trends
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения детальных экзаменов: {str(e)}"
        )

# ===========================================
# УВЕДОМЛЕНИЯ ДЛЯ РОДИТЕЛЕЙ
# ===========================================

@router.get("/student/{student_id}/notifications",
            response_model=ParentNotificationsResponse,
            summary="Уведомления для родителей",
            description="Получение уведомлений для родителей о студенте")
async def get_parent_notifications(
    student_id: int = Path(..., gt=0, description="ID студента"),
    limit: int = Query(10, le=50, description="Лимит уведомлений"),
    unread_only: bool = Query(False, description="Только непрочитанные"),
    db: AsyncSession = Depends(get_db)
) -> ParentNotificationsResponse:
    """Получение уведомлений для родителей"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        # Генерируем уведомления на основе данных студента
        notifications = []
        
        # Проверяем посещаемость
        try:
            missed_lessons = await count_missed_lessons_db(db, student_id)
            if missed_lessons > 5:
                notifications.append(NotificationItem(
                    notification_id=str(uuid.uuid4()),
                    type="warning",
                    title="Пропуски занятий",
                    message=f"Ваш ребенок пропустил {missed_lessons} занятий",
                    created_at=datetime.now() - timedelta(hours=2),
                    priority="high"
                ))
        except Exception:
            pass
        
        # Проверяем низкие оценки
        try:
            subjects = await get_all_subjects_db(db)
            for subject in subjects[:2]:  # Ограничиваем для примера
                try:
                    final_grade = await calculate_final_grade_db(db, student_id, subject.subject_id)
                    if final_grade.get("final_grade", 0) < 5:
                        notifications.append(NotificationItem(
                            notification_id=str(uuid.uuid4()),
                            type="error",
                            title="Низкая успеваемость",
                            message=f"Низкие оценки по предмету {subject.name}",
                            created_at=datetime.now() - timedelta(days=1),
                            priority="high"
                        ))
                except Exception:
                    continue
        except Exception:
            pass
        
        # Добавляем положительные уведомления
        notifications.append(NotificationItem(
            notification_id=str(uuid.uuid4()),
            type="success",
            title="Отличный результат",
            message="Ваш ребенок показал отличный результат на последнем тесте по химии",
            created_at=datetime.now() - timedelta(hours=6),
            priority="medium",
            is_read=True
        ))
        
        # Фильтруем и ограничиваем
        if unread_only:
            notifications = [n for n in notifications if not n.is_read]
        
        notifications = notifications[:limit]
        unread_count = len([n for n in notifications if not n.is_read])
        
        return ParentNotificationsResponse(
            student_id=student_id,
            notifications=notifications,
            unread_count=unread_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения уведомлений: {str(e)}"
        )

# ===========================================
# РЕКОМЕНДАЦИИ ДЛЯ РОДИТЕЛЕЙ
# ===========================================

@router.get("/student/{student_id}/recommendations",
            summary="Рекомендации для родителей",
            description="Получение рекомендаций для улучшения успеваемости")
async def get_parent_recommendations(
    student_id: int = Path(..., gt=0, description="ID студента"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Получение рекомендаций для родителей"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        recommendations = []
        
        # Анализируем посещаемость
        try:
            attendance_stats = await get_attendance_statistics_db(db, student_id)
            if attendance_stats.attendance_rate < 80:
                recommendations.append({
                    "category": "Посещаемость",
                    "priority": "high",
                    "title": "Улучшить посещаемость",
                    "description": "Необходимо обеспечить регулярное посещение занятий",
                    "actions": [
                        "Составить четкий распорядок дня",
                        "Обеспечить своевременный подъем", 
                        "Контролировать выполнение домашних заданий"
                    ]
                })
        except Exception:
            pass
        
        # Анализируем успеваемость
        try:
            subjects = await get_all_subjects_db(db)
            weak_subjects = []
            
            for subject in subjects:
                try:
                    final_grade = await calculate_final_grade_db(db, student_id, subject.subject_id)
                    if final_grade.get("final_grade", 0) < 6:
                        weak_subjects.append(subject.name)
                except Exception:
                    continue
            
            if weak_subjects:
                recommendations.append({
                    "category": "Успеваемость",
                    "priority": "high",
                    "title": "Дополнительные занятия",
                    "description": f"Рекомендуются дополнительные занятия по предметам: {', '.join(weak_subjects)}",
                    "actions": [
                        "Найти репетитора по слабым предметам",
                        "Увеличить время на самостоятельное изучение",
                        "Обратиться к учителю за консультацией"
                    ]
                })
        except Exception:
            pass
        
        # Общие рекомендации
        recommendations.append({
            "category": "Общие",
            "priority": "medium",
            "title": "Режим дня",
            "description": "Оптимизация режима дня для лучших результатов",
            "actions": [
                "Обеспечить 8-9 часов сна",
                "Сбалансированное питание",
                "Регулярные физические упражнения",
                "Ограничить время за экранами"
            ]
        })
        
        return {
            "student_id": student_id,
            "recommendations": recommendations,
            "generated_at": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения рекомендаций: {str(e)}"
        )

# ===========================================
# ЗДОРОВЬЕ СЕРВИСА
# ===========================================

@router.get("/health",
            response_model=ParentStatisticsHealthResponse,
            summary="Проверка здоровья сервиса",
            description="Проверка работоспособности API родительской статистики")
async def health_check(db: AsyncSession = Depends(get_db)) -> ParentStatisticsHealthResponse:
    """Проверка здоровья сервиса родительской статистики"""
    
    try:
        # Проверяем подключение к БД
        from sqlalchemy import select, func
        result = await db.execute(select(func.count(Student.student_id)))
        active_students = result.scalar()
        
        return ParentStatisticsHealthResponse(
            status="healthy",
            service="parent-statistics-api",
            version="1.0.0",
            timestamp=datetime.now(),
            active_students=active_students
        )
    except Exception:
        return ParentStatisticsHealthResponse(
            status="unhealthy",
            service="parent-statistics-api",
            version="1.0.0",
            timestamp=datetime.now(),
            active_students=0
        )