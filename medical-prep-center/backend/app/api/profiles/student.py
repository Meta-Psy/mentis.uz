from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select

# Импорты базы данных и моделей
from app.database import get_db
from app.database.models.user import Student, StudentInfo, User, StudentSkill, Teacher
from app.database.models.academic import University, Topic, Subject, Section, Block
from app.database.models.assessment import (
    TopicTest, Attendance
)

# Импорты сервисов
from app.services.roles.student_service import (
    get_student_by_id_db,
    update_student_db,
    create_student_info_db,
    update_student_info_db
)
from app.services.roles.user_service import (
    get_user_by_id_db
)
from app.services.assessment.grade_service import (
    get_all_dtm_scores_by_student_db
)
from app.services.assessment.attendance_service import (
    get_attendance_statistics_db
)
from app.services.assessment.comment_service import (
    get_all_comments_by_student_db,
    get_positive_comments_by_student_db,
    get_negative_comments_by_student_db,
    get_neutral_comments_by_student_db,
    get_comment_statistics_db
)
from app.services.content.subject_service import get_all_subjects_db

# Импорты схем
from app.schemas.assessment.student_dashboard import (
    StudentInfoResponse,
    UniversityResponse,
    TestResultResponse,
    AttendanceResponse,
    CommentResponse,
    ExamScoreResponse,
    StudentStatisticsResponse,
    StudentAnalyticsResponse,
    StudentProgressResponse,
    StudentProfileResponse,
    UpdateStudentInfoRequest,
    AddUniversityRequest,
    StudentGoalRequest,
    StudentTestsResponse,
    StudentAttendanceResponse,
    StudentCommentsResponse,
    StudentProfileHealthResponse
)
from app.database.models.user import Teacher

# Создание роутера
router = APIRouter()

# ===========================================
# ПОЛУЧЕНИЕ ПОЛНОГО ПРОФИЛЯ СТУДЕНТА
# ===========================================

@router.get("/{student_id}", 
            response_model=StudentProfileResponse,
            summary="Получить профиль студента",
            description="Получение полного профиля студента со всей информацией")
async def get_student_profile(
    student_id: int = Path(..., gt=0, description="ID студента"),
    db: AsyncSession = Depends(get_db)
) -> StudentProfileResponse:
    """Получение полного профиля студента"""
    
    try:
        # Получаем основную информацию о студенте
        student = await get_student_by_id_db(db, student_id)
        user = await get_user_by_id_db(db, student_id)
        
        # Основная информация
        student_info = StudentInfoResponse(
            student_id=student.student_id,
            name=user.name,
            surname=user.surname,
            phone=user.phone,
            email=user.email,
            photo=user.photo,
            direction=student.direction,
            goal=student.goal,
            group_id=student.group_id,
            student_status=student.student_status.value,
            last_login=student.last_login
        )
        
        # Дополнительная информация если есть
        try:
            from sqlalchemy import select
            student_info_result = await db.execute(
                select(StudentInfo).filter(StudentInfo.student_id == student_id)
            )
            student_info_data = student_info_result.scalar_one_or_none()
            
            if student_info_data:
                student_info.hobby = student_info_data.hobby
                student_info.sex = student_info_data.sex
                student_info.address = student_info_data.address
                student_info.birthday = student_info_data.birthday
        except Exception:
            pass
        
        # Получаем университеты студента
        universities = []
        try:
            from sqlalchemy import select
            from app.database.models.user import student_university_table
            
            universities_result = await db.execute(
                select(University, student_university_table.c.priority_order)
                .join(student_university_table, University.university_id == student_university_table.c.university_id)
                .filter(student_university_table.c.student_id == student_id)
                .order_by(student_university_table.c.priority_order)
            )
            
            for university, priority in universities_result.all():
                universities.append(UniversityResponse(
                    university_id=university.university_id,
                    name=university.name,
                    university_type=university.type.value,
                    entrance_score=university.entrance_score,
                    location=university.location,
                    website_url=university.website_url,
                    logo_url=university.logo_url,
                    contact_phone=university.contact_phone,
                    priority_order=priority
                ))
        except Exception:
            pass
        
        # Получаем последние тесты
        recent_tests = await get_recent_tests(db, student_id, limit=10)
        
        # Получаем статистику посещаемости
        attendance_summary = await get_attendance_summary(db, student_id)
        
        # Получаем последние комментарии
        recent_comments = await get_recent_comments(db, student_id, limit=5)
        
        # Получаем оценки за экзамены
        exam_scores = await get_exam_scores(db, student_id)
        
        # Получаем общую статистику
        statistics = await get_student_statistics(db, student_id)
        
        # Получаем аналитику
        analytics = await get_student_analytics(db, student_id)
        
        # Получаем прогресс по темам
        progress = await get_student_progress(db, student_id)
        
        return StudentProfileResponse(
            student_info=student_info,
            universities=universities,
            recent_tests=recent_tests,
            attendance_summary=attendance_summary,
            recent_comments=recent_comments,
            exam_scores=exam_scores,
            statistics=statistics,
            analytics=analytics,
            progress=progress
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения профиля студента: {str(e)}"
        )

# ===========================================
# ОБНОВЛЕНИЕ ИНФОРМАЦИИ О СТУДЕНТЕ
# ===========================================

@router.put("/{student_id}/info", 
            response_model=StudentInfoResponse,
            summary="Обновить информацию студента",
            description="Обновление дополнительной информации о студенте")
async def update_student_info(
    student_id: int = Path(..., gt=0, description="ID студента"),
    request: UpdateStudentInfoRequest = ...,
    db: AsyncSession = Depends(get_db)
) -> StudentInfoResponse:
    """Обновление информации о студенте"""
    
    try:
        # Проверяем существование студента
        student = await get_student_by_id_db(db, student_id)
        
        # Обновляем цель если указана
        if request.goal is not None:
            await update_student_db(db, student_id, goal=request.goal)
        
        # Обновляем дополнительную информацию
        try:
            await update_student_info_db(
                db=db,
                student_id=student_id,
                hobby=request.hobby,
                sex=request.sex,
                address=request.address,
                birthday=request.birthday
            )
        except HTTPException:
            # Если информации нет, создаем новую
            await create_student_info_db(
                db=db,
                student_id=student_id,
                hobby=request.hobby,
                sex=request.sex,
                address=request.address,
                birthday=request.birthday
            )
        
        # Возвращаем обновленную информацию
        updated_student = await get_student_by_id_db(db, student_id)
        user = await get_user_by_id_db(db, student_id)
        
        return StudentInfoResponse(
            student_id=updated_student.student_id,
            name=user.name,
            surname=user.surname,
            phone=user.phone,
            email=user.email,
            photo=user.photo,
            direction=updated_student.direction,
            goal=updated_student.goal,
            group_id=updated_student.group_id,
            student_status=updated_student.student_status.value,
            last_login=updated_student.last_login,
            hobby=request.hobby,
            sex=request.sex,
            address=request.address,
            birthday=request.birthday
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обновления информации: {str(e)}"
        )

# ===========================================
# ПОЛУЧЕНИЕ ТЕСТОВ СТУДЕНТА
# ===========================================

@router.get("/{student_id}/tests", 
            response_model=StudentTestsResponse,
            summary="Получить тесты студента",
            description="Получение списка тестов студента с фильтрацией")
async def get_student_tests(
    student_id: int = Path(..., gt=0, description="ID студента"),
    subject_name: Optional[str] = Query(None, description="Фильтр по предмету"),
    test_type: Optional[str] = Query(None, description="Тип теста"),
    passed_only: Optional[bool] = Query(None, description="Только пройденные"),
    limit: int = Query(20, le=100, description="Лимит результатов"),
    db: AsyncSession = Depends(get_db)
) -> StudentTestsResponse:
    """Получение тестов студента"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        tests = await get_recent_tests(db, student_id, limit=limit)
        
        # Фильтрация
        if subject_name:
            tests = [t for t in tests if subject_name.lower() in t.subject_name.lower()]
        
        if test_type:
            tests = [t for t in tests if t.test_type == test_type]
        
        if passed_only is not None:
            tests = [t for t in tests if t.passed == passed_only]
        
        # Статистика
        total_count = len(tests)
        average_score = sum(t.score_percentage for t in tests) / total_count if total_count > 0 else 0
        passed_count = len([t for t in tests if t.passed])
        failed_count = total_count - passed_count
        
        return StudentTestsResponse(
            tests=tests,
            total_count=total_count,
            average_score=average_score,
            passed_count=passed_count,
            failed_count=failed_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения тестов: {str(e)}"
        )

# ===========================================
# ПОЛУЧЕНИЕ ПОСЕЩАЕМОСТИ СТУДЕНТА
# ===========================================

@router.get("/{student_id}/attendance", 
            response_model=StudentAttendanceResponse,
            summary="Получить посещаемость студента",
            description="Получение записей о посещаемости студента")
async def get_student_attendance(
    student_id: int = Path(..., gt=0, description="ID студента"),
    subject_name: Optional[str] = Query(None, description="Фильтр по предмету"),
    limit: int = Query(50, le=200, description="Лимит результатов"),
    db: AsyncSession = Depends(get_db)
) -> StudentAttendanceResponse:
    """Получение посещаемости студента"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        # Получаем статистику посещаемости
        attendance_stats = await get_attendance_statistics_db(db, student_id)
        
        # Получаем записи посещаемости
        from sqlalchemy import select
        
        query = select(Attendance).filter(Attendance.student_id == student_id)
        
        if subject_name:
            query = query.join(Subject).filter(Subject.name.ilike(f"%{subject_name}%"))
        
        query = query.order_by(Attendance.lesson_date_time.desc()).limit(limit)
        
        result = await db.execute(query)
        attendance_records = result.scalars().all()
        
        # Преобразуем в ответы
        attendance_responses = []
        for record in attendance_records:
            # Получаем информацию о предмете и теме
            subject_result = await db.execute(
                select(Subject).filter(Subject.subject_id == record.subject_id)
            )
            subject = subject_result.scalar_one_or_none()
            
            topic_result = await db.execute(
                select(Topic).filter(Topic.topic_id == record.topic_id)
            )
            topic = topic_result.scalar_one_or_none()
            
            attendance_responses.append(AttendanceResponse(
                attendance_id=record.attendance_id,
                lesson_date_time=record.lesson_date_time,
                att_status=record.att_status.value,
                topic_name=topic.name if topic else None,
                subject_name=subject.name if subject else "Неизвестно",
                excuse_reason=record.excuse_reason,
                extra_lesson=record.extra_lesson
            ))
        
        return StudentAttendanceResponse(
            attendance_records=attendance_responses,
            total_count=attendance_stats["total_lessons"],
            attendance_rate=attendance_stats["attendance_rate"],
            present_count=attendance_stats["present_count"],
            absent_count=attendance_stats["absent_count"],
            late_count=attendance_stats["late_count"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения посещаемости: {str(e)}"
        )

# ===========================================
# ПОЛУЧЕНИЕ КОММЕНТАРИЕВ О СТУДЕНТЕ
# ===========================================

@router.get("/{student_id}/comments", 
            response_model=StudentCommentsResponse,
            summary="Получить комментарии о студенте",
            description="Получение комментариев учителей о студенте")
async def get_student_comments(
    student_id: int = Path(..., gt=0, description="ID студента"),
    comment_type: Optional[str] = Query(None, description="Тип комментария"),
    limit: int = Query(20, le=100, description="Лимит результатов"),
    db: AsyncSession = Depends(get_db)
) -> StudentCommentsResponse:
    """Получение комментариев о студенте"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        # Получаем комментарии
        if comment_type == "positive":
            comments = await get_positive_comments_by_student_db(db, student_id)
        elif comment_type == "negative":
            comments = await get_negative_comments_by_student_db(db, student_id)
        elif comment_type == "neutral":
            comments = await get_neutral_comments_by_student_db(db, student_id)
        else:
            comments = await get_all_comments_by_student_db(db, student_id)
        
        # Ограничиваем количество
        comments = comments[:limit]
        
        # Получаем статистику
        comment_stats = await get_comment_statistics_db(db, student_id)
        
        # Преобразуем в ответы
        comment_responses = []
        for comment in comments:
            # Получаем информацию об учителе
            from sqlalchemy import select
            teacher_result = await db.execute(
                select(User).join(
                    Teacher, User.user_id == Teacher.teacher_id
                ).filter(Teacher.teacher_id == comment.teacher_id)
            )
            teacher_user = teacher_result.scalar_one_or_none()
            
            teacher_name = f"{teacher_user.name} {teacher_user.surname}" if teacher_user else "Неизвестный учитель"
            
            comment_responses.append(CommentResponse(
                comment_id=comment.comment_id,
                teacher_name=teacher_name,
                comment_text=comment.comment_text,
                comment_date=comment.comment_date,
                comment_type=comment.comment_type.value
            ))
        
        return StudentCommentsResponse(
            comments=comment_responses,
            total_count=comment_stats["total_comments"],
            positive_count=comment_stats["positive_count"],
            negative_count=comment_stats["negative_count"],
            neutral_count=comment_stats["neutral_count"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения комментариев: {str(e)}"
        )

# ===========================================
# ПОЛУЧЕНИЕ СТАТИСТИКИ СТУДЕНТА
# ===========================================

@router.get("/{student_id}/statistics", 
            response_model=StudentStatisticsResponse,
            summary="Получить статистику студента",
            description="Получение подробной статистики успеваемости студента")
async def get_student_detailed_statistics(
    student_id: int = Path(..., gt=0, description="ID студента"),
    db: AsyncSession = Depends(get_db)
) -> StudentStatisticsResponse:
    """Получение статистики студента"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        return await get_student_statistics(db, student_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики: {str(e)}"
        )

# ===========================================
# УПРАВЛЕНИЕ УНИВЕРСИТЕТАМИ
# ===========================================

@router.get("/{student_id}/universities", 
            response_model=List[UniversityResponse],
            summary="Получить университеты студента",
            description="Получение списка выбранных университетов студента")
async def get_student_universities(
    student_id: int = Path(..., gt=0, description="ID студента"),
    db: AsyncSession = Depends(get_db)
) -> List[UniversityResponse]:
    """Получение университетов студента"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        from sqlalchemy import select
        from app.database.models.user import student_university_table
        
        universities_result = await db.execute(
            select(University, student_university_table.c.priority_order)
            .join(student_university_table, University.university_id == student_university_table.c.university_id)
            .filter(student_university_table.c.student_id == student_id)
            .order_by(student_university_table.c.priority_order)
        )
        
        universities = []
        for university, priority in universities_result.all():
            universities.append(UniversityResponse(
                university_id=university.university_id,
                name=university.name,
                university_type=university.type.value,
                entrance_score=university.entrance_score,
                location=university.location,
                website_url=university.website_url,
                logo_url=university.logo_url,
                contact_phone=university.contact_phone,
                priority_order=priority
            ))
        
        return universities
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения университетов: {str(e)}"
        )

@router.post("/{student_id}/universities", 
             summary="Добавить университет",
             description="Добавление университета в список студента")
async def add_student_university(
    student_id: int = Path(..., gt=0, description="ID студента"),
    request: AddUniversityRequest = ...,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Добавление университета студенту"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        # Проверяем существование университета
        from sqlalchemy import select
        university_result = await db.execute(
            select(University).filter(University.university_id == request.university_id)
        )
        university = university_result.scalar_one_or_none()
        if not university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Университет не найден"
            )
        
        # Добавляем связь
        from app.database.models.user import student_university_table
        
        # Проверяем, не добавлен ли уже
        existing_result = await db.execute(
            select(student_university_table).filter(
                student_university_table.c.student_id == student_id,
                student_university_table.c.university_id == request.university_id
            )
        )
        if existing_result.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Университет уже добавлен"
            )
        
        # Добавляем
        await db.execute(
            student_university_table.insert().values(
                student_id=student_id,
                university_id=request.university_id,
                priority_order=request.priority_order
            )
        )
        await db.commit()
        
        return {"status": "success", "message": "Университет добавлен"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка добавления университета: {str(e)}"
        )

@router.delete("/{student_id}/universities/{university_id}", 
               summary="Удалить университет",
               description="Удаление университета из списка студента")
async def remove_student_university(
    student_id: int = Path(..., gt=0, description="ID студента"),
    university_id: int = Path(..., gt=0, description="ID университета"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Удаление университета у студента"""
    
    try:
        # Проверяем существование студента
        await get_student_by_id_db(db, student_id)
        
        from app.database.models.user import student_university_table
        
        # Удаляем связь
        result = await db.execute(
            student_university_table.delete().where(
                student_university_table.c.student_id == student_id,
                student_university_table.c.university_id == university_id
            )
        )
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Университет не найден в списке студента"
            )
        
        await db.commit()
        
        return {"status": "success", "message": "Университет удален"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка удаления университета: {str(e)}"
        )

# ===========================================
# ОБНОВЛЕНИЕ ЦЕЛИ СТУДЕНТА
# ===========================================

@router.put("/{student_id}/goal", 
            summary="Обновить цель студента",
            description="Обновление цели студента")
async def update_student_goal(
    student_id: int = Path(..., gt=0, description="ID студента"),
    request: StudentGoalRequest = ...,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Обновление цели студента"""
    
    try:
        # Обновляем цель
        await update_student_db(db, student_id, goal=request.goal)
        
        return {"status": "success", "message": "Цель обновлена"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обновления цели: {str(e)}"
        )

# ===========================================
# ПРОВЕРКА ЗДОРОВЬЯ API
# ===========================================

@router.get("/health",
            response_model=StudentProfileHealthResponse,
            summary="Проверка здоровья API",
            description="Проверка работоспособности API профиля студента")
async def health_check(db: AsyncSession = Depends(get_db)) -> StudentProfileHealthResponse:
    """Проверка здоровья API профиля студента"""
    
    try:
        # Подсчитываем активных студентов
        from sqlalchemy import select, func
        from app.database.models.user import StudentStatus
        
        active_students_result = await db.execute(
            select(func.count(Student.student_id)).filter(
                Student.student_status == StudentStatus.ACTIVE
            )
        )
        active_students = active_students_result.scalar()
        
        return StudentProfileHealthResponse(
            status="healthy",
            service="student-profile-api",
            version="1.0.0",
            timestamp=datetime.now(),
            active_students=active_students
        )
    except Exception:
        return StudentProfileHealthResponse(
            status="healthy",
            service="student-profile-api",
            version="1.0.0",
            timestamp=datetime.now()
        )

# ===========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ===========================================

async def get_recent_tests(db: AsyncSession, student_id: int, limit: int = 10) -> List[TestResultResponse]:
    """Получение последних тестов студента"""
    
    tests = []
    
    try:
        # Получаем тесты по темам
        from sqlalchemy import select
        
        topic_tests_result = await db.execute(
            select(TopicTest)
            .filter(TopicTest.student_id == student_id)
            .order_by(TopicTest.attempt_date.desc())
            .limit(limit)
        )
        topic_tests = topic_tests_result.scalars().all()
        
        for test in topic_tests:
            # Получаем информацию о теме и предмете
            topic_result = await db.execute(
                select(Topic).filter(Topic.topic_id == test.topic_id)
            )
            topic = topic_result.scalar_one_or_none()
            
            if topic:
                # Получаем предмет через блок и раздел
                block_result = await db.execute(
                    select(Block).filter(Block.block_id == topic.block_id)
                )
                block = block_result.scalar_one_or_none()
                
                if block:
                    section_result = await db.execute(
                        select(Section).filter(Section.section_id == block.section_id)
                    )
                    section = section_result.scalar_one_or_none()
                    
                    if section:
                        subject_result = await db.execute(
                            select(Subject).filter(Subject.subject_id == section.subject_id)
                        )
                        subject = subject_result.scalar_one_or_none()
                        
                        if subject:
                            score_percentage = (test.correct_answers / test.question_count * 100) if test.question_count > 0 else 0
                            
                            tests.append(TestResultResponse(
                                test_id=test.topic_test_id,
                                test_type="training",
                                topic_name=topic.name,
                                subject_name=subject.name,
                                score_percentage=score_percentage,
                                correct_answers=int(test.correct_answers),
                                total_questions=test.question_count,
                                attempt_date=test.attempt_date,
                                time_spent=test.time_spent,
                                passed=score_percentage >= 60
                            ))
    except Exception as e:
        print(f"Ошибка получения тестов: {e}")
    
    return tests[:limit]

async def get_attendance_summary(db: AsyncSession, student_id: int) -> Dict[str, Any]:
    """Получение краткой сводки посещаемости"""
    
    try:
        stats = await get_attendance_statistics_db(db, student_id)
        return {
            "attendance_rate": stats["attendance_rate"],
            "total_lessons": stats["total_lessons"],
            "missed_lessons": stats["absent_count"],
            "late_arrivals": stats["late_count"]
        }
    except Exception:
        return {
            "attendance_rate": 0,
            "total_lessons": 0,
            "missed_lessons": 0,
            "late_arrivals": 0
        }

async def get_recent_comments(db: AsyncSession, student_id: int, limit: int = 5) -> List[CommentResponse]:
    """Получение последних комментариев"""
    
    try:
        comments = await get_all_comments_by_student_db(db, student_id)
        comments = comments[:limit]
        
        comment_responses = []
        for comment in comments:
            # Получаем информацию об учителе
            from sqlalchemy import select
            from app.database.models.user import Teacher
            
            teacher_result = await db.execute(
                select(User).join(
                    Teacher, User.user_id == Teacher.teacher_id
                ).filter(Teacher.teacher_id == comment.teacher_id)
            )
            teacher_user = teacher_result.scalar_one_or_none()
            
            teacher_name = f"{teacher_user.name} {teacher_user.surname}" if teacher_user else "Неизвестный учитель"
            
            comment_responses.append(CommentResponse(
                comment_id=comment.comment_id,
                teacher_name=teacher_name,
                comment_text=comment.comment_text,
                comment_date=comment.comment_date,
                comment_type=comment.comment_type.value
            ))
        
        return comment_responses
    except Exception:
        return []

async def get_exam_scores(db: AsyncSession, student_id: int) -> List[ExamScoreResponse]:
    """Получение оценок за экзамены"""
    
    exam_scores = []
    
    try:
        # ДТМ экзамены
        dtm_exams = await get_all_dtm_scores_by_student_db(db, student_id)
        for exam in dtm_exams:
            # Получаем информацию о предмете
            subject_result = await db.execute(
                select(Subject).filter(Subject.subject_id == exam.subject_id)
            )
            subject = subject_result.scalar_one_or_none()
            
            exam_scores.append(ExamScoreResponse(
                exam_type="dtm",
                subject_name=subject.name if subject else "Неизвестно",
                score=exam.total_correct_answers,
                exam_date=exam.exam_date,
                passed=exam.total_correct_answers >= 112.5  # 60% от 187.5
            ))
            
        # Другие экзамены можно добавить аналогично
        
    except Exception as e:
        print(f"Ошибка получения экзаменов: {e}")
    
    return exam_scores

async def get_student_statistics(db: AsyncSession, student_id: int) -> StudentStatisticsResponse:
    """Получение статистики студента"""
    
    try:
        # Получаем статистику тестов
        tests = await get_recent_tests(db, student_id, limit=1000)
        total_tests = len(tests)
        average_score = sum(t.score_percentage for t in tests) / total_tests if total_tests > 0 else 0
        
        # Получаем статистику посещаемости
        attendance_stats = await get_attendance_statistics_db(db, student_id)
        
        # Получаем оценки по предметам
        subjects = await get_all_subjects_db(db)
        subject_averages = {}
        
        for subject in subjects:
            subject_tests = [t for t in tests if t.subject_name == subject.name]
            if subject_tests:
                subject_averages[subject.name] = sum(t.score_percentage for t in subject_tests) / len(subject_tests)
        
        # Прогресс по темам (заглушка)
        completed_topics = len([t for t in tests if t.passed])
        total_topics = 100  # Заглушка
        
        return StudentStatisticsResponse(
            total_tests_completed=total_tests,
            average_score=average_score,
            total_time_studied_hours=total_tests * 0.5,  # Примерно 30 минут на тест
            attendance_rate=attendance_stats.get("attendance_rate", 0),
            total_lessons=attendance_stats.get("total_lessons", 0),
            present_count=attendance_stats.get("present_count", 0),
            absent_count=attendance_stats.get("absent_count", 0),
            late_count=attendance_stats.get("late_count", 0),
            subject_averages=subject_averages,
            completed_topics=completed_topics,
            total_topics=total_topics,
            progress_percentage=(completed_topics / total_topics * 100) if total_topics > 0 else 0
        )
        
    except Exception as e:
        print(f"Ошибка получения статистики: {e}")
        return StudentStatisticsResponse(
            total_tests_completed=0,
            average_score=0,
            total_time_studied_hours=0,
            attendance_rate=0,
            total_lessons=0,
            present_count=0,
            absent_count=0,
            late_count=0,
            subject_averages={},
            completed_topics=0,
            total_topics=0,
            progress_percentage=0
        )

async def get_student_analytics(db: AsyncSession, student_id: int) -> StudentAnalyticsResponse:
    """Получение аналитики студента"""
    
    try:
        # Получаем навыки студента
        from sqlalchemy import select
        
        skills_result = await db.execute(
            select(StudentSkill).filter(StudentSkill.student_id == student_id)
        )
        skills = skills_result.scalars().all()
        
        correct_by_category = {}
        mistakes_by_category = {}
        total_correct = 0
        total_mistakes = 0
        
        for skill in skills:
            if skill.correct:
                for category in skill.correct:
                    correct_by_category[str(category)] = correct_by_category.get(str(category), 0) + 1
                    total_correct += 1
            
            if skill.mistakes:
                for category in skill.mistakes:
                    mistakes_by_category[str(category)] = mistakes_by_category.get(str(category), 0) + 1
                    total_mistakes += 1
        
        # Определяем слабые и сильные места
        weak_categories = []
        strong_categories = []
        
        for category in set(list(correct_by_category.keys()) + list(mistakes_by_category.keys())):
            correct = correct_by_category.get(category, 0)
            mistakes = mistakes_by_category.get(category, 0)
            total = correct + mistakes
            
            if total > 0:
                accuracy = correct / total
                if accuracy < 0.5:
                    weak_categories.append(category)
                elif accuracy > 0.8:
                    strong_categories.append(category)
        
        accuracy_percentage = (total_correct / (total_correct + total_mistakes) * 100) if (total_correct + total_mistakes) > 0 else 0
        
        return StudentAnalyticsResponse(
            correct_by_category=correct_by_category,
            mistakes_by_category=mistakes_by_category,
            total_correct=total_correct,
            total_mistakes=total_mistakes,
            accuracy_percentage=accuracy_percentage,
            weak_categories=weak_categories,
            strong_categories=strong_categories
        )
        
    except Exception as e:
        print(f"Ошибка получения аналитики: {e}")
        return StudentAnalyticsResponse(
            correct_by_category={},
            mistakes_by_category={},
            total_correct=0,
            total_mistakes=0,
            accuracy_percentage=0,
            weak_categories=[],
            strong_categories=[]
        )

async def get_student_progress(db: AsyncSession, student_id: int) -> List[StudentProgressResponse]:
    """Получение прогресса студента по темам"""
    
    progress = []
    
    try:
        # Получаем тесты студента
        tests = await get_recent_tests(db, student_id, limit=1000)
        
        # Группируем по темам
        topic_tests = {}
        for test in tests:
            if test.topic_name not in topic_tests:
                topic_tests[test.topic_name] = []
            topic_tests[test.topic_name].append(test)
        
        # Создаем прогресс по темам
        for topic_name, topic_test_list in topic_tests.items():
            best_test = max(topic_test_list, key=lambda x: x.score_percentage)
            
            progress.append(StudentProgressResponse(
                topic_id=best_test.test_id,  # Заглушка
                topic_name=topic_name,
                subject_name=best_test.subject_name,
                section_name="Раздел",  # Заглушка
                block_name="Блок",  # Заглушка
                is_completed=best_test.passed,
                test_score=best_test.score_percentage,
                attendance="present",  # Заглушка
                last_activity=best_test.attempt_date
            ))
    
    except Exception as e:
        print(f"Ошибка получения прогресса: {e}")
    
    return progress