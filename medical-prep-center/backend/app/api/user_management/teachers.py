from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.auth.teacher_service import *
from app.services.assessment.attendance_service import *
from app.services.assessment.comment_service import *
from app.services.assessment.grade_service import *
from app.services.auth.student_service import *
from app.schemas.auth.teacher import *
from app.core.dependencies import get_current_user, require_roles
from app.database.models.user import UserRole
from app.database.models.assessment import AttendanceType, CommentType

router = APIRouter()

# ===== ПРОФИЛЬ УЧИТЕЛЯ =====

@router.get("/profile", response_model=TeacherProfileResponse)
async def get_teacher_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение профиля текущего учителя"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        teacher = get_teacher_by_id_db(current_user.user_id)
        teacher_info = get_teacher_info_db(current_user.user_id)
        subjects = get_teacher_subjects_db(current_user.user_id)
        
        return TeacherProfileResponse(
            teacher=teacher,
            teacher_info=teacher_info,
            subjects=subjects
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/profile", response_model=TeacherResponse)
async def update_teacher_profile(
    teacher_update: TeacherUpdate,
    current_user = Depends(get_current_user)
):
    """Обновление профиля учителя"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        updated_teacher = update_teacher_db(
            current_user.user_id,
            teacher_schedule=teacher_update.teacher_schedule
        )
        return TeacherResponse.from_orm(updated_teacher)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== УПРАВЛЕНИЕ ГРУППАМИ =====

@router.get("/groups", response_model=List[GroupResponse])
async def get_teacher_groups(
    current_user = Depends(get_current_user)
):
    """Получение групп учителя"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        teacher = get_teacher_by_id_db(current_user.user_id)
        groups = teacher.groups
        return [GroupResponse.from_orm(group) for group in groups]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/groups/{group_id}/students", response_model=List[StudentResponse])
async def get_group_students(
    group_id: int,
    current_user = Depends(get_current_user)
):
    """Получение студентов группы"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        # Проверяем, что группа принадлежит учителю
        teacher = get_teacher_by_id_db(current_user.user_id)
        teacher_group_ids = [group.group_id for group in teacher.groups]
        
        if group_id not in teacher_group_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет доступа к этой группе"
            )
        
        students = get_students_by_group_db(group_id)
        return [StudentResponse.from_orm(student) for student in students]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== УПРАВЛЕНИЕ ПОСЕЩАЕМОСТЬЮ =====

@router.post("/attendance", response_model=AttendanceResponse)
async def mark_attendance(
    attendance_data: CreateAttendanceRequest,
    current_user = Depends(get_current_user)
):
    """Отметка посещаемости студента"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        # Проверяем права доступа учителя к студенту
        verify_teacher_student_access(current_user.user_id, attendance_data.student_id)
        
        attendance = add_attendance_db(
            student_id=attendance_data.student_id,
            lesson_date_time=attendance_data.lesson_date_time,
            att_status=attendance_data.att_status,
            subject_id=attendance_data.subject_id,
            topic_id=attendance_data.topic_id,
            excuse_reason=attendance_data.excuse_reason,
            extra_lesson=attendance_data.extra_lesson
        )
        
        return AttendanceResponse.from_orm(attendance)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    attendance_update: UpdateAttendanceRequest,
    current_user = Depends(get_current_user)
):
    """Обновление записи о посещаемости"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        updated_attendance = update_attendance_db(
            attendance_id=attendance_id,
            att_status=attendance_update.att_status,
            excuse_reason=attendance_update.excuse_reason,
            extra_lesson=attendance_update.extra_lesson
        )
        
        return AttendanceResponse.from_orm(updated_attendance)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/attendance/group/{group_id}")
async def get_group_attendance(
    group_id: int,
    subject_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    """Получение посещаемости группы"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        # Проверяем права доступа
        verify_teacher_group_access(current_user.user_id, group_id)
        
        attendance_records = get_attendance_by_group_and_subject_db(group_id, subject_id)
        
        # Фильтруем по датам если указаны
        if start_date and end_date:
            # Логика фильтрации по датам
            pass
        
        return attendance_records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/attendance/statistics/{student_id}")
async def get_student_attendance_statistics(
    student_id: int,
    subject_id: Optional[int] = Query(None),
    current_user = Depends(get_current_user)
):
    """Получение статистики посещаемости студента"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        verify_teacher_student_access(current_user.user_id, student_id)
        
        statistics = get_attendance_statistics_db(student_id, subject_id)
        return statistics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== УПРАВЛЕНИЕ КОММЕНТАРИЯМИ =====

@router.post("/comments", response_model=CommentResponse)
async def add_student_comment(
    comment_data: CreateCommentRequest,
    current_user = Depends(get_current_user)
):
    """Добавление комментария к студенту"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        verify_teacher_student_access(current_user.user_id, comment_data.student_id)
        
        comment = add_comment_db(
            teacher_id=current_user.user_id,
            student_id=comment_data.student_id,
            comment_text=comment_data.comment_text,
            comment_type=comment_data.comment_type
        )
        
        return CommentResponse.from_orm(comment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: UpdateCommentRequest,
    current_user = Depends(get_current_user)
):
    """Обновление комментария"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        # Проверяем, что комментарий принадлежит учителю
        verify_teacher_comment_access(current_user.user_id, comment_id)
        
        updated_comment = update_comment_db(
            comment_id=comment_id,
            comment_text=comment_update.comment_text,
            comment_type=comment_update.comment_type
        )
        
        return CommentResponse.from_orm(updated_comment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user = Depends(get_current_user)
):
    """Удаление комментария"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        verify_teacher_comment_access(current_user.user_id, comment_id)
        result = delete_comment_db(comment_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/comments", response_model=List[CommentResponse])
async def get_teacher_comments(
    limit: int = Query(50, le=100),
    current_user = Depends(get_current_user)
):
    """Получение комментариев учителя"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        comments = get_comments_by_teacher_db(current_user.user_id)
        return [CommentResponse.from_orm(comment) for comment in comments[:limit]]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== УПРАВЛЕНИЕ ОЦЕНКАМИ =====

@router.post("/grades/current-rating", response_model=CurrentRatingResponse)
async def add_current_rating(
    rating_data: CreateCurrentRatingRequest,
    current_user = Depends(get_current_user)
):
    """Добавление текущей оценки (опрос)"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        verify_teacher_student_access(current_user.user_id, rating_data.student_id)
        
        rating = add_current_rating_db(
            student_id=rating_data.student_id,
            subject_id=rating_data.subject_id,
            topic_id=rating_data.topic_id,
            current_correct_answers=rating_data.current_correct_answers,
            second_current_correct_answers=rating_data.second_current_correct_answers
        )
        
        return CurrentRatingResponse.from_orm(rating)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/grades/current-rating/{rating_id}", response_model=CurrentRatingResponse)
async def update_current_rating(
    rating_id: int,
    rating_update: UpdateCurrentRatingRequest,
    current_user = Depends(get_current_user)
):
    """Обновление текущей оценки"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        updated_rating = update_current_rating_db(
            rating_id=rating_id,
            current_correct_answers=rating_update.current_correct_answers,
            second_current_correct_answers=rating_update.second_current_correct_answers
        )
        
        return CurrentRatingResponse.from_orm(updated_rating)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/grades/student/{student_id}")
async def get_student_grades(
    student_id: int,
    subject_id: Optional[int] = Query(None),
    current_user = Depends(get_current_user)
):
    """Получение всех оценок студента"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        verify_teacher_student_access(current_user.user_id, student_id)
        
        # Получаем итоговую оценку студента
        final_grade = calculate_final_grade_db(student_id, subject_id)
        
        return final_grade
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== СТАТИСТИКА И ОТЧЕТЫ =====

@router.get("/statistics/group/{group_id}")
async def get_group_statistics(
    group_id: int,
    subject_id: int,
    current_user = Depends(get_current_user)
):
    """Получение статистики группы"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        verify_teacher_group_access(current_user.user_id, group_id)
        
        # Получаем студентов группы
        students = get_students_by_group_db(group_id)
        
        # Собираем статистику
        group_stats = {
            "group_id": group_id,
            "subject_id": subject_id,
            "total_students": len(students),
            "students_statistics": []
        }
        
        for student in students:
            student_stats = {
                "student_id": student.student_id,
                "student_name": f"{student.user.name} {student.user.surname}",
                "attendance": get_attendance_statistics_db(student.student_id, subject_id),
                "final_grade": calculate_final_grade_db(student.student_id, subject_id),
                "comments_count": len(get_all_comments_by_student_db(student.student_id))
            }
            group_stats["students_statistics"].append(student_stats)
        
        return group_stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/statistics/performance")
async def get_teacher_performance_statistics(
    period: str = Query("month", regex="^(week|month|semester|year)$"),
    current_user = Depends(get_current_user)
):
    """Получение статистики работы учителя"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешен только учителям"
        )
    
    try:
        # Получаем все группы учителя
        teacher = get_teacher_by_id_db(current_user.user_id)
        
        stats = {
            "teacher_id": current_user.user_id,
            "period": period,
            "total_groups": len(teacher.groups),
            "total_students": sum(len(get_students_by_group_db(group.group_id)) for group in teacher.groups),
            "total_comments": len(get_comments_by_teacher_db(current_user.user_id)),
            "subjects": [subject.name for subject in teacher.subjects]
        }
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def verify_teacher_student_access(teacher_id: int, student_id: int):
    """Проверка прав доступа учителя к студенту"""
    teacher = get_teacher_by_id_db(teacher_id)
    student = get_student_by_id_db(student_id)
    
    teacher_group_ids = [group.group_id for group in teacher.groups]
    
    if student.group_id not in teacher_group_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этому студенту"
        )

def verify_teacher_group_access(teacher_id: int, group_id: int):
    """Проверка прав доступа учителя к группе"""
    teacher = get_teacher_by_id_db(teacher_id)
    teacher_group_ids = [group.group_id for group in teacher.groups]
    
    if group_id not in teacher_group_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этой группе"
        )

def verify_teacher_comment_access(teacher_id: int, comment_id: int):
    """Проверка прав доступа учителя к комментарию"""
    # Логика проверки, что комментарий принадлежит учителю
    # Нужно добавить функцию в comment_service для получения комментария по ID
    pass