# assessment/
# 1. attendance_service
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models.assessment import Attendance, AttendanceType
from app.database.models.user import Student


# -----------------------
# ADD ATTENDANCE
# -----------------------
async def add_attendance_db(
    db: AsyncSession,
    student_id: int,
    lesson_date_time: datetime,
    att_status: AttendanceType,
    subject_id: int,
    topic_id: int,
    excuse_reason: Optional[str] = None,
    extra_lesson: Optional[str] = None,
) -> Attendance:
    """Добавление записи о посещаемости"""

    new_att = Attendance(
        student_id=student_id,
        lesson_date_time=lesson_date_time,
        att_status=att_status,
        subject_id=subject_id,
        topic_id=topic_id,
        excuse_reason=excuse_reason,
        extra_lesson=extra_lesson,
    )
    db.add(new_att)
    await db.commit()
    await db.refresh(new_att)
    return new_att


# -----------------------
# DELETE ATTENDANCE
# -----------------------
async def delete_attendance_db(db: AsyncSession, attendance_id: int) -> dict:
    """Удаление записи о посещаемости"""

    result = await db.execute(
        select(Attendance).filter(Attendance.attendance_id == attendance_id)
    )
    att = result.scalar_one_or_none()
    if not att:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись о посещаемости не найдена",
        )
    await db.delete(att)
    await db.commit()
    return {"status": "Удалена"}


# -----------------------
# UPDATE ATTENDANCE
# -----------------------
async def update_attendance_db(
    db: AsyncSession,
    attendance_id: int,
    att_status: Optional[AttendanceType] = None,
    excuse_reason: Optional[str] = None,
    extra_lesson: Optional[str] = None,
) -> Attendance:
    """Обновление записи о посещаемости"""

    result = await db.execute(
        select(Attendance).filter(Attendance.attendance_id == attendance_id)
    )
    att = result.scalar_one_or_none()
    if not att:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись о посещаемости не найдена",
        )

    if att_status is not None:
        att.att_status = att_status
    if excuse_reason is not None:
        att.excuse_reason = excuse_reason
    if extra_lesson is not None:
        att.extra_lesson = extra_lesson

    await db.commit()
    await db.refresh(att)
    return att


# -----------------------
# GET ATTENDANCE BY GROUP & SUBJECT
# -----------------------
async def get_attendance_by_group_and_subject_db(
    db: AsyncSession, group_id: int, subject_id: int
) -> List[Attendance]:
    """Получение посещаемости группы по предмету"""

    result = await db.execute(
        select(Attendance)
        .join(Attendance.student)
        .filter(Student.group_id == group_id, Attendance.subject_id == subject_id)
    )
    records = result.scalars().all()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Посещаемость группы {group_id} по предмету {subject_id} не найдена",
        )
    return records


# -----------------------
# GET ATTENDANCE BY STUDENT & SUBJECT
# -----------------------
async def get_attendance_by_student_and_subject_db(
    db: AsyncSession, student_id: int, subject_id: int
) -> List[Attendance]:
    """Получение посещаемости студента по предмету"""

    result = await db.execute(
        select(Attendance).filter(
            Attendance.student_id == student_id, Attendance.subject_id == subject_id
        )
    )
    records = result.scalars().all()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Посещаемость студента {student_id} по предмету {subject_id} не найдена",
        )
    return records


# -----------------------
# GET ATTENDANCE BY STUDENT & TOPIC
# -----------------------
async def get_attendance_by_student_and_topic_db(
    db: AsyncSession, student_id: int, topic_id: int
) -> Attendance:
    """Получение посещаемости студента по теме"""

    result = await db.execute(
        select(Attendance).filter(
            Attendance.student_id == student_id, Attendance.topic_id == topic_id
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Посещаемость студента {student_id} по теме {topic_id} не найдена",
        )
    return record


# -----------------------
# CHANGE STATUS BY LESSON
# -----------------------
async def change_attendance_status_by_lesson_db(
    db: AsyncSession, student_id: int, topic_id: int, new_status: AttendanceType
) -> Attendance:
    """Изменение статуса посещаемости по уроку"""

    result = await db.execute(
        select(Attendance).filter(
            Attendance.student_id == student_id, Attendance.topic_id == topic_id
        )
    )
    att = result.scalar_one_or_none()
    if not att:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись о посещаемости для данного урока не найдена",
        )
    att.att_status = new_status
    await db.commit()
    await db.refresh(att)
    return att


# -----------------------
# COUNT MISSED LESSONS
# -----------------------
async def count_missed_lessons_db(
    db: AsyncSession, student_id: int, subject_id: Optional[int] = None
) -> int:
    """Подсчет пропущенных уроков студента"""

    query = select(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.att_status == AttendanceType.ABSENT,
    )
    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)

    result = await db.execute(query)
    return len(result.scalars().all())


# -----------------------
# COUNT LATE ARRIVALS
# -----------------------
async def count_late_arrivals_db(
    db: AsyncSession, student_id: int, subject_id: Optional[int] = None
) -> int:
    """Подсчет опозданий студента"""

    query = select(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.att_status == AttendanceType.LATE,
    )
    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)

    result = await db.execute(query)
    return len(result.scalars().all())


# -----------------------
# GET ATTENDANCE STATISTICS
# -----------------------
async def get_attendance_statistics_db(
    db: AsyncSession, student_id: int, subject_id: Optional[int] = None
) -> dict:
    """Получение статистики посещаемости студента"""

    query = select(Attendance).filter(Attendance.student_id == student_id)
    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)

    result = await db.execute(query)
    all_records = result.scalars().all()
    total_lessons = len(all_records)

    present_count = len(
        [r for r in all_records if r.att_status == AttendanceType.PRESENT]
    )
    absent_count = len(
        [r for r in all_records if r.att_status == AttendanceType.ABSENT]
    )
    late_count = len([r for r in all_records if r.att_status == AttendanceType.LATE])

    attendance_rate = (present_count / total_lessons * 100) if total_lessons > 0 else 0

    return {
        "student_id": student_id,
        "subject_id": subject_id,
        "total_lessons": total_lessons,
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count,
        "attendance_rate": round(attendance_rate, 2),
    }


# -----------------------
# GET STUDENTS WITH EXCUSE
# -----------------------
async def get_students_with_excuse_db(
    db: AsyncSession, topic_id: int
) -> List[Attendance]:
    """Получение студентов с уважительной причиной отсутствия по теме"""

    result = await db.execute(
        select(Attendance).filter(
            Attendance.topic_id == topic_id,
            Attendance.att_status == AttendanceType.ABSENT,
            Attendance.excuse_reason.isnot(None),
        )
    )
    records = result.scalars().all()
    return records


# -----------------------
# GET STUDENTS FOR EXTRA LESSON
# -----------------------
async def get_students_for_extra_lesson_db(
    db: AsyncSession, topic_id: int
) -> List[Attendance]:
    """Получение студентов, которым назначен дополнительный урок"""

    result = await db.execute(
        select(Attendance).filter(
            Attendance.topic_id == topic_id, Attendance.extra_lesson.isnot(None)
        )
    )
    records = result.scalars().all()
    return records

# 2. comment_service
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import or_, desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.assessment import CommentType, Comments


# -----------------------
# ADD COMMENT
# -----------------------
async def add_comment_db(
    db: AsyncSession,
    teacher_id: int,
    student_id: int,
    comment_text: str,
    comment_type: CommentType,
) -> Comments:
    """Добавление комментария"""

    new_comment = Comments(
        teacher_id=teacher_id,
        student_id=student_id,
        comment_text=comment_text,
        comment_type=comment_type,
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


# -----------------------
# DELETE COMMENT
# -----------------------
async def delete_comment_db(db: AsyncSession, comment_id: int) -> dict:
    """Удаление комментария"""

    result = await db.execute(
        select(Comments).filter(Comments.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден"
        )
    await db.delete(comment)
    await db.commit()
    return {"status": "Удалён"}


# -----------------------
# EDIT COMMENT TEXT
# -----------------------
async def edit_comment_text_db(
    db: AsyncSession, comment_id: int, new_text: str
) -> Comments:
    """Редактирование текста комментария"""

    result = await db.execute(
        select(Comments).filter(Comments.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден"
        )
    comment.comment_text = new_text
    await db.commit()
    await db.refresh(comment)
    return comment


# -----------------------
# EDIT COMMENT TYPE
# -----------------------
async def edit_comment_type_db(
    db: AsyncSession, comment_id: int, new_type: CommentType
) -> Comments:
    """Редактирование типа комментария"""

    result = await db.execute(
        select(Comments).filter(Comments.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден"
        )
    comment.comment_type = new_type
    await db.commit()
    await db.refresh(comment)
    return comment


# -----------------------
# UPDATE COMMENT
# -----------------------
async def update_comment_db(
    db: AsyncSession,
    comment_id: int,
    comment_text: Optional[str] = None,
    comment_type: Optional[CommentType] = None,
) -> Comments:
    """Обновление комментария"""

    result = await db.execute(
        select(Comments).filter(Comments.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден"
        )

    if comment_text is not None:
        comment.comment_text = comment_text
    if comment_type is not None:
        comment.comment_type = comment_type

    await db.commit()
    await db.refresh(comment)
    return comment


# -----------------------
# GET COMMENTS BY STUDENT & TYPE
# -----------------------
async def get_negative_comments_by_student_db(
    db: AsyncSession, student_id: int
) -> List[Comments]:
    """Получение негативных комментариев студента"""

    result = await db.execute(
        select(Comments)
        .filter(
            Comments.student_id == student_id,
            Comments.comment_type == CommentType.NEGATIVE,
        )
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Негативные комментарии для студента {student_id} не найдены",
        )
    return records


async def get_positive_comments_by_student_db(
    db: AsyncSession, student_id: int
) -> List[Comments]:
    """Получение позитивных комментариев студента"""

    result = await db.execute(
        select(Comments)
        .filter(
            Comments.student_id == student_id,
            Comments.comment_type == CommentType.POSITIVE,
        )
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Позитивные комментарии для студента {student_id} не найдены",
        )
    return records


async def get_neutral_comments_by_student_db(
    db: AsyncSession, student_id: int
) -> List[Comments]:
    """Получение нейтральных комментариев студента"""

    result = await db.execute(
        select(Comments)
        .filter(
            Comments.student_id == student_id,
            Comments.comment_type == CommentType.NEUTRAL,
        )
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Нейтральные комментарии для студента {student_id} не найдены",
        )
    return records


async def get_all_comments_by_student_db(
    db: AsyncSession, student_id: int
) -> List[Comments]:
    """Получение всех комментариев студента"""

    result = await db.execute(
        select(Comments)
        .filter(Comments.student_id == student_id)
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комментарии для студента {student_id} не найдены",
        )
    return records


# -----------------------
# GET COMMENTS BY TEACHER
# -----------------------
async def get_comments_by_teacher_db(
    db: AsyncSession, teacher_id: int
) -> List[Comments]:
    """Получение всех комментариев учителя"""

    result = await db.execute(
        select(Comments)
        .filter(Comments.teacher_id == teacher_id)
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комментарии учителя {teacher_id} не найдены",
        )
    return records


# -----------------------
# SEARCH COMMENTS
# -----------------------
async def search_comments_by_text_db(
    db: AsyncSession, search_text: str
) -> List[Comments]:
    """Поиск комментариев по тексту"""

    result = await db.execute(
        select(Comments)
        .filter(Comments.comment_text.ilike(f"%{search_text}%"))
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комментариев, содержащих «{search_text}», не найдено",
        )
    return records


# -----------------------
# GET RECENT COMMENTS
# -----------------------
async def get_recent_comments_db(
    db: AsyncSession,
    student_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    limit: int = 10,
) -> List[Comments]:
    """Получение последних комментариев"""

    query = select(Comments)

    if student_id:
        query = query.filter(Comments.student_id == student_id)
    if teacher_id:
        query = query.filter(Comments.teacher_id == teacher_id)

    query = query.order_by(desc(Comments.comment_date)).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()
    return records


# -----------------------
# GET COMMENTS BY DATE RANGE
# -----------------------
async def get_comments_by_date_range_db(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    student_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
) -> List[Comments]:
    """Получение комментариев за период"""

    query = select(Comments).filter(
        Comments.comment_date >= start_date, Comments.comment_date <= end_date
    )

    if student_id:
        query = query.filter(Comments.student_id == student_id)
    if teacher_id:
        query = query.filter(Comments.teacher_id == teacher_id)

    query = query.order_by(desc(Comments.comment_date))
    result = await db.execute(query)
    records = result.scalars().all()
    return records


# -----------------------
# GET COMMENT STATISTICS
# -----------------------
async def get_comment_statistics_db(
    db: AsyncSession, student_id: Optional[int] = None, teacher_id: Optional[int] = None
) -> dict:
    """Получение статистики комментариев"""

    query = select(Comments)

    if student_id:
        query = query.filter(Comments.student_id == student_id)
    if teacher_id:
        query = query.filter(Comments.teacher_id == teacher_id)

    # Общее количество комментариев
    result = await db.execute(query)
    all_comments = result.scalars().all()
    total_comments = len(all_comments)

    # Подсчет по типам
    positive_count = len(
        [c for c in all_comments if c.comment_type == CommentType.POSITIVE]
    )
    negative_count = len(
        [c for c in all_comments if c.comment_type == CommentType.NEGATIVE]
    )
    neutral_count = len(
        [c for c in all_comments if c.comment_type == CommentType.NEUTRAL]
    )

    return {
        "total_comments": total_comments,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "positive_percentage": round(
            (positive_count / total_comments * 100) if total_comments > 0 else 0, 2
        ),
        "negative_percentage": round(
            (negative_count / total_comments * 100) if total_comments > 0 else 0, 2
        ),
        "neutral_percentage": round(
            (neutral_count / total_comments * 100) if total_comments > 0 else 0, 2
        ),
    }

# 3. grade_service
from datetime import datetime, timedelta
from typing import List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models.assessment import (
    DtmExam,
    SectionExam,
    BlockExam,
    ModulExam,
    TopicTest,
    CurrentRating,
)
from app.database.models.academic import Section, Block, Subject, Topic, Moduls
from app.database.models.user import Student
from fastapi import HTTPException, status

# ===========================================
# DTM EXAM OPERATIONS
# ===========================================


async def add_dtm_exam_db(
    db: AsyncSession,
    student_id: int,
    subject_id: int,
    common_subject_correct_answers: float,
    second_subject_correct_answers: float,
    first_subject_correct_answers: float,
    total_correct_answers: float,
    exam_date: Optional[datetime] = None,
    category_correct: Optional[List[int]] = None,
    category_mistake: Optional[List[int]] = None,
    attempt_number: Optional[int] = None,
) -> DtmExam:
    """Добавление DTM экзамена"""

    new_exam = DtmExam(
        student_id=student_id,
        subject_id=subject_id,
        common_subject_correct_answers=common_subject_correct_answers,
        second_subject_correct_answers=second_subject_correct_answers,
        first_subject_correct_answers=first_subject_correct_answers,
        total_correct_answers=total_correct_answers,
        exam_date=exam_date or datetime.now(),
        category_correct=category_correct or [],
        category_mistake=category_mistake or [],
        attempt_number=attempt_number,
    )
    db.add(new_exam)
    await db.commit()
    await db.refresh(new_exam)
    return new_exam


async def delete_dtm_exam_db(
    db: AsyncSession, exam_id: int, student_id: int, subject_id: int
) -> dict:
    """Удаление DTM экзамена"""

    result = await db.execute(
        select(DtmExam).filter(
            DtmExam.exam_id == exam_id,
            DtmExam.student_id == student_id,
            DtmExam.subject_id == subject_id,
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен id={exam_id} для студента {student_id} по предмету {subject_id} не найден",
        )
    await db.delete(exam)
    await db.commit()
    return {"status": "Удалён"}


async def edit_dtm_exam_db(
    db: AsyncSession,
    exam_id: int,
    student_id: int,
    subject_id: int,
    common_subject_correct_answers: Optional[float] = None,
    second_subject_correct_answers: Optional[float] = None,
    first_subject_correct_answers: Optional[float] = None,
    total_correct_answers: Optional[float] = None,
    exam_date: Optional[datetime] = None,
    category_correct: Optional[List[int]] = None,
    category_mistake: Optional[List[int]] = None,
    attempt_number: Optional[int] = None,
) -> DtmExam:
    """Редактирование DTM экзамена"""

    result = await db.execute(
        select(DtmExam).filter(
            DtmExam.exam_id == exam_id,
            DtmExam.student_id == student_id,
            DtmExam.subject_id == subject_id,
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен id={exam_id} для студента {student_id} по предмету {subject_id} не найден",
        )

    if common_subject_correct_answers is not None:
        exam.common_subject_correct_answers = common_subject_correct_answers
    if second_subject_correct_answers is not None:
        exam.second_subject_correct_answers = second_subject_correct_answers
    if first_subject_correct_answers is not None:
        exam.first_subject_correct_answers = first_subject_correct_answers
    if total_correct_answers is not None:
        exam.total_correct_answers = total_correct_answers
    if exam_date is not None:
        exam.exam_date = exam_date
    if category_correct is not None:
        exam.category_correct = category_correct
    if category_mistake is not None:
        exam.category_mistake = category_mistake
    if attempt_number is not None:
        exam.attempt_number = attempt_number

    await db.commit()
    await db.refresh(exam)
    return exam


async def get_dtm_exam_scores_by_student_and_date_db(
    db: AsyncSession, student_id: int, exam_date: datetime
) -> Dict[str, float]:
    """Получение всех оценок DTM экзамена по студенту и дате"""

    result = await db.execute(
        select(DtmExam).filter(
            DtmExam.student_id == student_id,
            func.date(DtmExam.exam_date) == exam_date.date(),
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DTM экзамен не найден для студента {student_id} на дату {exam_date}",
        )
    return {
        "common_subject_correct_answers": exam.common_subject_correct_answers,
        "second_subject_correct_answers": exam.second_subject_correct_answers,
        "first_subject_correct_answers": exam.first_subject_correct_answers,
        "total_correct_answers": exam.total_correct_answers,
    }


async def get_all_dtm_scores_by_student_db(
    db: AsyncSession, student_id: int
) -> List[DtmExam]:
    """Получение всех DTM экзаменов студента"""

    result = await db.execute(
        select(DtmExam)
        .filter(DtmExam.student_id == student_id)
        .order_by(DtmExam.exam_date)
    )
    exams = result.scalars().all()
    return exams


async def get_average_dtm_score_for_student_db(
    db: AsyncSession, student_id: int
) -> Dict[str, float]:
    """Получение средних оценок DTM экзаменов студента"""

    result = await db.execute(
        select(
            func.avg(DtmExam.common_subject_correct_answers).label("avg_common"),
            func.avg(DtmExam.second_subject_correct_answers).label("avg_second"),
            func.avg(DtmExam.first_subject_correct_answers).label("avg_first"),
            func.avg(DtmExam.total_correct_answers).label("avg_total"),
        ).filter(DtmExam.student_id == student_id)
    )
    row = result.first()

    if not row or row.avg_total is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DTM экзамены для студента {student_id} не найдены",
        )

    return {
        "avg_common_subject": float(row.avg_common),
        "avg_second_subject": float(row.avg_second),
        "avg_first_subject": float(row.avg_first),
        "avg_total": float(row.avg_total),
    }


# ===========================================
# SECTION EXAM OPERATIONS
# ===========================================


async def add_section_exam_db(
    db: AsyncSession,
    student_id: int,
    section_id: int,
    correct_answers: float,
    exam_date: datetime,
    category_correct: Optional[List[int]] = None,
    category_mistake: Optional[List[int]] = None,
    time_spent: Optional[str] = None,
    passed: Optional[bool] = None,
    max_correct_answers: Optional[float] = None,
    attempt_count: Optional[str] = None,
) -> SectionExam:
    """Создание новой записи SectionExam"""

    # Проверяем существование студента
    student_result = await db.execute(
        select(Student).filter(Student.student_id == student_id)
    )
    if not student_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент id={student_id} не найден",
        )

    # Проверяем существование раздела
    section_result = await db.execute(
        select(Section).filter(Section.section_id == section_id)
    )
    if not section_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Раздел id={section_id} не найден",
        )

    exam = SectionExam(
        student_id=student_id,
        section_id=section_id,
        correct_answers=correct_answers,
        exam_date=exam_date,
        category_correct=category_correct or [],
        category_mistake=category_mistake or [],
        time_spent=time_spent,
        passed=passed,
        max_correct_answers=max_correct_answers,
        attempt_count=attempt_count,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


async def delete_section_exam_db(db: AsyncSession, section_exam_id: int) -> None:
    """Удаление SectionExam"""

    result = await db.execute(
        select(SectionExam).filter(SectionExam.section_exam_id == section_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по разделу id={section_exam_id} не найден",
        )
    await db.delete(exam)
    await db.commit()


async def update_section_exam_db(
    db: AsyncSession,
    section_exam_id: int,
    correct_answers: Optional[float] = None,
    section_id: Optional[int] = None,
    student_id: Optional[int] = None,
    exam_date: Optional[datetime] = None,
    time_spent: Optional[str] = None,
    passed: Optional[bool] = None,
    max_correct_answers: Optional[float] = None,
    attempt_count: Optional[str] = None,
) -> SectionExam:
    """Обновление полей SectionExam"""

    result = await db.execute(
        select(SectionExam).filter(SectionExam.section_exam_id == section_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по разделу id={section_exam_id} не найден",
        )

    if student_id is not None:
        student_result = await db.execute(
            select(Student).filter(Student.student_id == student_id)
        )
        if not student_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент id={student_id} не найден",
            )
        exam.student_id = student_id

    if section_id is not None:
        section_result = await db.execute(
            select(Section).filter(Section.section_id == section_id)
        )
        if not section_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Раздел id={section_id} не найден",
            )
        exam.section_id = section_id

    if correct_answers is not None:
        exam.correct_answers = correct_answers
    if exam_date is not None:
        exam.exam_date = exam_date
    if time_spent is not None:
        exam.time_spent = time_spent
    if passed is not None:
        exam.passed = passed
    if max_correct_answers is not None:
        exam.max_correct_answers = max_correct_answers
    if attempt_count is not None:
        exam.attempt_count = attempt_count

    await db.commit()
    await db.refresh(exam)
    return exam


async def get_section_exam_score_db(
    db: AsyncSession, student_id: int, exam_date: datetime
) -> float:
    """Получение оценки за экзамен по разделу"""

    result = await db.execute(
        select(SectionExam).filter(
            SectionExam.student_id == student_id, SectionExam.exam_date == exam_date
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по разделу для студента {student_id} на дату {exam_date} не найден",
        )
    return exam.correct_answers


async def get_avg_score_by_student_subject_db(
    db: AsyncSession, student_id: int, subject_id: int
) -> float:
    """Средний балл студента по предмету (через связь Section → Subject)"""

    result = await db.execute(
        select(func.avg(SectionExam.correct_answers))
        .join(SectionExam.section)
        .filter(SectionExam.student_id == student_id, Section.subject_id == subject_id)
    )
    avg_score = result.scalar()
    if avg_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамены по разделам для студента {student_id} по предмету {subject_id} не найдены",
        )
    return float(avg_score)


async def get_avg_score_for_subject_db(db: AsyncSession, subject_id: int) -> float:
    """Средний балл по предмету среди всех студентов"""

    result = await db.execute(
        select(func.avg(SectionExam.correct_answers))
        .join(SectionExam.section)
        .filter(Section.subject_id == subject_id)
    )
    avg_score = result.scalar()
    if avg_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамены по разделам для предмета {subject_id} не найдены",
        )
    return float(avg_score)


# ===========================================
# BLOCK EXAM OPERATIONS
# ===========================================


async def add_block_exam_db(
    db: AsyncSession,
    student_id: int,
    block_id: int,
    subject_id: int,
    correct_answers: float,
    exam_date: datetime,
    category_correct: Optional[List[Any]] = None,
    category_mistake: Optional[List[Any]] = None,
    time_spent: Optional[str] = None,
    passed: Optional[bool] = None,
    max_correct_answers: Optional[float] = None,
    attempt_count: Optional[str] = None,
    time_limit: Optional[str] = None,
) -> BlockExam:
    """Создание новой записи BlockExam"""

    # Проверяем существование студента
    student_result = await db.execute(
        select(Student).filter(Student.student_id == student_id)
    )
    if not student_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент id={student_id} не найден",
        )

    # Проверяем существование блока
    block_result = await db.execute(select(Block).filter(Block.block_id == block_id))
    if not block_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Блок id={block_id} не найден",
        )

    # Проверяем существование предмета
    subject_result = await db.execute(
        select(Subject).filter(Subject.subject_id == subject_id)
    )
    if not subject_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Предмет id={subject_id} не найден",
        )

    exam = BlockExam(
        student_id=student_id,
        block_id=block_id,
        subject_id=subject_id,
        correct_answers=correct_answers,
        exam_date=exam_date,
        category_correct=category_correct or [],
        category_mistake=category_mistake or [],
        time_spent=time_spent,
        passed=passed,
        max_correct_answers=max_correct_answers,
        attempt_count=attempt_count,
        time_limit=time_limit,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


async def delete_block_exam_db(db: AsyncSession, block_exam_id: int) -> None:
    """Удаление записи BlockExam"""

    result = await db.execute(
        select(BlockExam).filter(BlockExam.block_exam_id == block_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по блоку id={block_exam_id} не найден",
        )
    await db.delete(exam)
    await db.commit()


async def update_block_exam_db(
    db: AsyncSession,
    block_exam_id: int,
    student_id: Optional[int] = None,
    block_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    correct_answers: Optional[float] = None,
    exam_date: Optional[datetime] = None,
    time_spent: Optional[str] = None,
    passed: Optional[bool] = None,
    max_correct_answers: Optional[float] = None,
    attempt_count: Optional[str] = None,
    time_limit: Optional[str] = None,
) -> BlockExam:
    """Обновление полей BlockExam"""

    result = await db.execute(
        select(BlockExam).filter(BlockExam.block_exam_id == block_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по блоку id={block_exam_id} не найден",
        )

    if student_id is not None:
        student_result = await db.execute(
            select(Student).filter(Student.student_id == student_id)
        )
        if not student_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Студент id={student_id} не найден",
            )
        exam.student_id = student_id

    if block_id is not None:
        block_result = await db.execute(
            select(Block).filter(Block.block_id == block_id)
        )
        if not block_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Блок id={block_id} не найден",
            )
        exam.block_id = block_id

    if subject_id is not None:
        subject_result = await db.execute(
            select(Subject).filter(Subject.subject_id == subject_id)
        )
        if not subject_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Предмет id={subject_id} не найден",
            )
        exam.subject_id = subject_id

    if correct_answers is not None:
        exam.correct_answers = correct_answers
    if exam_date is not None:
        exam.exam_date = exam_date
    if time_spent is not None:
        exam.time_spent = time_spent
    if passed is not None:
        exam.passed = passed
    if max_correct_answers is not None:
        exam.max_correct_answers = max_correct_answers
    if attempt_count is not None:
        exam.attempt_count = attempt_count
    if time_limit is not None:
        exam.time_limit = time_limit

    await db.commit()
    await db.refresh(exam)
    return exam


async def get_all_block_scores_by_student_subject_db(
    db: AsyncSession, student_id: int, subject_id: int
) -> List[float]:
    """Получение всех оценок по блокам для студента и предмета"""

    result = await db.execute(
        select(BlockExam.correct_answers)
        .filter(BlockExam.student_id == student_id, BlockExam.subject_id == subject_id)
        .order_by(BlockExam.exam_date)
    )
    rows = result.scalars().all()
    return list(rows)


async def get_block_score_by_student_date_subject_db(
    db: AsyncSession, student_id: int, subject_id: int, exam_date: datetime
) -> float:
    """Получение оценки по блоку для студента на конкретную дату"""

    result = await db.execute(
        select(BlockExam).filter(
            BlockExam.student_id == student_id,
            BlockExam.subject_id == subject_id,
            BlockExam.exam_date == exam_date,
        )
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамен по блоку для студента {student_id} по предмету {subject_id} на дату {exam_date} не найден",
        )
    return exam.correct_answers


async def get_avg_block_score_by_student_subject_db(
    db: AsyncSession, student_id: int, subject_id: int
) -> float:
    """Средний балл по блокам для студента и предмета"""

    result = await db.execute(
        select(func.avg(BlockExam.correct_answers)).filter(
            BlockExam.student_id == student_id, BlockExam.subject_id == subject_id
        )
    )
    avg_score = result.scalar()
    if avg_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамены по блокам для студента {student_id} по предмету {subject_id} не найдены",
        )
    return float(avg_score)


async def get_avg_block_score_for_subject_db(
    db: AsyncSession, subject_id: int
) -> Dict[int, float]:
    """Средний балл по блокам для каждого студента по предмету"""

    result = await db.execute(
        select(
            BlockExam.student_id, func.avg(BlockExam.correct_answers).label("avg_score")
        )
        .filter(BlockExam.subject_id == subject_id)
        .group_by(BlockExam.student_id)
    )
    rows = result.all()
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Экзамены по блокам для предмета {subject_id} не найдены",
        )
    return {student_id: float(avg_score) for student_id, avg_score in rows}


# ===========================================
# MODULE EXAM OPERATIONS
# ===========================================


async def add_modul_exam_db(
    db: AsyncSession,
    modul_id: int,
    student_id: int,
    chem_correct_answers: float,
    bio_correct_answers: float,
    exam_date: datetime,
    category_correct: Optional[List[Any]] = None,
    category_mistake: Optional[List[Any]] = None,
    total_questions_chem: Optional[int] = None,
    total_questions_bio: Optional[int] = None,
    time_spent_chem: Optional[str] = None,
    time_spent_bio: Optional[str] = None,
) -> ModulExam:
    """Добавление нового модульного экзамена"""

    # Проверяем существование модуля
    modul_result = await db.execute(select(Moduls).filter(Moduls.modul_id == modul_id))
    if not modul_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модуль id={modul_id} не найден",
        )

    # Проверяем существование студента
    student_result = await db.execute(
        select(Student).filter(Student.student_id == student_id)
    )
    if not student_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент id={student_id} не найден",
        )

    exam = ModulExam(
        modul_id=modul_id,
        student_id=student_id,
        chem_correct_answers=chem_correct_answers,
        bio_correct_answers=bio_correct_answers,
        exam_date=exam_date,
        category_correct=category_correct or [],
        category_mistake=category_mistake or [],
        total_questions_chem=total_questions_chem,
        total_questions_bio=total_questions_bio,
        time_spent_chem=time_spent_chem,
        time_spent_bio=time_spent_bio,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


async def delete_modul_exam_db(db: AsyncSession, modul_exam_id: int) -> None:
    """Удаление модульного экзамена"""

    result = await db.execute(
        select(ModulExam).filter(ModulExam.modul_exam_id == modul_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модульный экзамен id={modul_exam_id} не найден",
        )
    await db.delete(exam)
    await db.commit()


async def update_modul_exam_db(
    db: AsyncSession,
    modul_exam_id: int,
    chem_correct_answers: Optional[float] = None,
    bio_correct_answers: Optional[float] = None,
    exam_date: Optional[datetime] = None,
    total_questions_chem: Optional[int] = None,
    total_questions_bio: Optional[int] = None,
    time_spent_chem: Optional[str] = None,
    time_spent_bio: Optional[str] = None,
) -> ModulExam:
    """Обновление модульного экзамена"""

    result = await db.execute(
        select(ModulExam).filter(ModulExam.modul_exam_id == modul_exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модульный экзамен id={modul_exam_id} не найден",
        )

    if chem_correct_answers is not None:
        exam.chem_correct_answers = chem_correct_answers
    if bio_correct_answers is not None:
        exam.bio_correct_answers = bio_correct_answers
    if exam_date is not None:
        exam.exam_date = exam_date
    if total_questions_chem is not None:
        exam.total_questions_chem = total_questions_chem
    if total_questions_bio is not None:
        exam.total_questions_bio = total_questions_bio
    if time_spent_chem is not None:
        exam.time_spent_chem = time_spent_chem
    if time_spent_bio is not None:
        exam.time_spent_bio = time_spent_bio

    await db.commit()
    await db.refresh(exam)
    return exam


async def get_modul_exam_scores_db(
    db: AsyncSession, student_id: int, modul_id: int, exam_date: datetime
) -> Dict[str, float]:
    """Получение оценок модульного экзамена"""

    result = await db.execute(
        select(ModulExam.chem_correct_answers, ModulExam.bio_correct_answers).filter(
            ModulExam.student_id == student_id,
            ModulExam.modul_id == modul_id,
            ModulExam.exam_date == exam_date,
        )
    )
    exam = result.first()
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оценки модульного экзамена не найдены",
        )
    chem, bio = exam
    return {"chem_correct_answers": chem, "bio_correct_answers": bio}


async def get_avg_bio_score_for_student_db(db: AsyncSession, student_id: int) -> float:
    """Средний балл по биологии для студента"""

    result = await db.execute(
        select(func.avg(ModulExam.bio_correct_answers)).filter(
            ModulExam.student_id == student_id
        )
    )
    avg_bio = result.scalar()
    return avg_bio or 0.0


async def get_avg_chem_score_for_student_db(db: AsyncSession, student_id: int) -> float:
    """Средний балл по химии для студента"""

    result = await db.execute(
        select(func.avg(ModulExam.chem_correct_answers)).filter(
            ModulExam.student_id == student_id
        )
    )
    avg_chem = result.scalar()
    return avg_chem or 0.0


async def get_all_chem_scores_db(
    db: AsyncSession, modul_id: int, exam_date: datetime
) -> Dict[int, float]:
    """Получение всех оценок по химии для модуля на дату"""

    result = await db.execute(
        select(ModulExam.student_id, ModulExam.chem_correct_answers).filter(
            ModulExam.modul_id == modul_id, ModulExam.exam_date == exam_date
        )
    )
    rows = result.all()
    return {sid: score for sid, score in rows}


async def get_all_bio_scores_db(
    db: AsyncSession, modul_id: int, exam_date: datetime
) -> Dict[int, float]:
    """Получение всех оценок по биологии для модуля на дату"""

    result = await db.execute(
        select(ModulExam.student_id, ModulExam.bio_correct_answers).filter(
            ModulExam.modul_id == modul_id, ModulExam.exam_date == exam_date
        )
    )
    rows = result.all()
    return {sid: score for sid, score in rows}


# ===========================================
# TOPIC TEST OPERATIONS
# ===========================================


async def add_topic_test_db(
    db: AsyncSession,
    student_id: int,
    topic_id: int,
    question_count: int,
    correct_answers: float,
    attempt_date: datetime,
    time_spent: Optional[str] = None,
) -> TopicTest:
    """Добавление теста по теме"""

    # Проверяем существование студента
    student_result = await db.execute(
        select(Student).filter(Student.student_id == student_id)
    )
    if not student_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент id={student_id} не найден",
        )

    # Проверяем существование темы
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    if not topic_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тема id={topic_id} не найдена",
        )

    tt = TopicTest(
        student_id=student_id,
        topic_id=topic_id,
        question_count=question_count,
        correct_answers=correct_answers,
        attempt_date=attempt_date,
        time_spent=time_spent,
    )
    db.add(tt)
    await db.commit()
    await db.refresh(tt)
    return tt


async def update_topic_test_score_db(
    db: AsyncSession,
    student_id: int,
    topic_id: int,
    topic_test_id: int,
    new_correct_answers: float,
) -> TopicTest:
    """Изменение оценки в TopicTest"""

    result = await db.execute(
        select(TopicTest).filter(
            TopicTest.topic_test_id == topic_test_id,
            TopicTest.student_id == student_id,
            TopicTest.topic_id == topic_id,
        )
    )
    tt = result.scalar_one_or_none()
    if not tt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тест по теме не найден для обновления",
        )
    tt.correct_answers = new_correct_answers
    await db.commit()
    await db.refresh(tt)
    return tt


async def delete_topic_test_db(db: AsyncSession, topic_test_id: int) -> None:
    """Удаление теста по теме"""

    result = await db.execute(
        select(TopicTest).filter(TopicTest.topic_test_id == topic_test_id)
    )
    tt = result.scalar_one_or_none()
    if not tt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тест по теме id={topic_test_id} не найден",
        )
    await db.delete(tt)
    await db.commit()


async def get_topic_test_score_db(
    db: AsyncSession, student_id: int, topic_id: int, topic_test_id: int
) -> float:
    """Получение оценки теста по теме"""

    result = await db.execute(
        select(TopicTest.correct_answers).filter(
            TopicTest.topic_test_id == topic_test_id,
            TopicTest.student_id == student_id,
            TopicTest.topic_id == topic_id,
        )
    )
    score = result.scalar()
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Оценка теста не найдена"
        )
    return score


async def get_all_topic_scores_by_topic_db(
    db: AsyncSession, topic_id: int
) -> Dict[int, float]:
    """Получение всех оценок по теме"""

    result = await db.execute(
        select(TopicTest.student_id, TopicTest.correct_answers).filter(
            TopicTest.topic_id == topic_id
        )
    )
    rows = result.all()
    return {sid: sc for sid, sc in rows}


async def get_avg_topic_score_for_student_db(
    db: AsyncSession, student_id: int, topic_id: int
) -> float:
    """Средний балл студента по теме"""

    result = await db.execute(
        select(func.avg(TopicTest.correct_answers)).filter(
            TopicTest.student_id == student_id, TopicTest.topic_id == topic_id
        )
    )
    avg = result.scalar()
    return avg or 0.0


# ===========================================
# CURRENT RATING OPERATIONS
# ===========================================


async def add_current_rating_db(
    db: AsyncSession,
    student_id: int,
    subject_id: int,
    topic_id: int,
    current_correct_answers: float,
    second_current_correct_answers: float,
) -> CurrentRating:
    """Добавление текущего рейтинга"""

    # Проверяем существование темы
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    if not topic_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тема id={topic_id} не найдена",
        )

    rating = CurrentRating(
        student_id=student_id,
        subject_id=subject_id,
        topic_id=topic_id,
        current_correct_answers=current_correct_answers,
        second_current_correct_answers=second_current_correct_answers,
        last_updated=datetime.now(),
    )
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def delete_current_rating_db(db: AsyncSession, rating_id: int) -> None:
    """Удаление текущего рейтинга"""

    result = await db.execute(
        select(CurrentRating).filter(CurrentRating.rating_id == rating_id)
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Текущий рейтинг id={rating_id} не найден",
        )
    await db.delete(rating)
    await db.commit()


async def update_current_rating_db(
    db: AsyncSession,
    rating_id: int,
    current_correct_answers: Optional[float] = None,
    second_current_correct_answers: Optional[float] = None,
) -> CurrentRating:
    """Обновление текущего рейтинга"""

    result = await db.execute(
        select(CurrentRating).filter(CurrentRating.rating_id == rating_id)
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Текущий рейтинг id={rating_id} не найден",
        )

    if current_correct_answers is not None:
        rating.current_correct_answers = current_correct_answers
    if second_current_correct_answers is not None:
        rating.second_current_correct_answers = second_current_correct_answers
    rating.last_updated = datetime.now()

    await db.commit()
    await db.refresh(rating)
    return rating


async def get_current_score_db(
    db: AsyncSession, student_id: int, subject_id: int, topic_id: int
) -> float:
    """Получение текущего балла"""

    result = await db.execute(
        select(CurrentRating).filter(
            CurrentRating.student_id == student_id,
            CurrentRating.subject_id == subject_id,
            CurrentRating.topic_id == topic_id,
        )
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Текущий рейтинг не найден"
        )
    return rating.current_correct_answers


async def get_second_current_score_db(
    db: AsyncSession, student_id: int, subject_id: int, topic_id: int
) -> float:
    """Получение второго текущего балла"""

    result = await db.execute(
        select(CurrentRating).filter(
            CurrentRating.student_id == student_id,
            CurrentRating.subject_id == subject_id,
            CurrentRating.topic_id == topic_id,
        )
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Текущий рейтинг не найден"
        )
    return rating.second_current_correct_answers


async def get_avg_sum_scores_by_block_for_student_db(
    db: AsyncSession, student_id: int, block_id: int
) -> float:
    """Средняя сумма баллов по блоку для студента"""

    result = await db.execute(
        select(
            func.avg(
                func.coalesce(CurrentRating.current_correct_answers, 0)
                + func.coalesce(CurrentRating.second_current_correct_answers, 0)
            )
        )
        .join(Topic, CurrentRating.topic_id == Topic.topic_id)
        .filter(CurrentRating.student_id == student_id, Topic.block_id == block_id)
    )
    avg_sum = result.scalar()
    return float(avg_sum) if avg_sum is not None else 0.0


async def get_avg_current_rating_for_block_db(
    db: AsyncSession, block_id: int
) -> Dict[int, float]:
    """Средний текущий рейтинг по блоку для всех студентов"""

    # Проверяем существование блока
    block_result = await db.execute(select(Block).filter(Block.block_id == block_id))
    block = block_result.scalar_one_or_none()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Блок id={block_id} не найден",
        )

    subject_id = block.section.subject_id
    result = await db.execute(
        select(
            CurrentRating.student_id,
            func.avg(
                CurrentRating.current_correct_answers
                + CurrentRating.second_current_correct_answers
            ).label("avg_score"),
        )
        .join(CurrentRating.topic)
        .filter(Topic.block_id == block_id, CurrentRating.subject_id == subject_id)
        .group_by(CurrentRating.student_id)
    )
    rows = result.all()
    return {student_id: avg_score for student_id, avg_score in rows}


# ===========================================
# CALCULATE FINAL GRADE
# ===========================================


async def calculate_final_grade_db(
    db: AsyncSession, student_id: int, subject_id: int
) -> Dict[str, Any]:
    """Вычисление итоговой оценки студента по предмету"""

    # Получаем средние баллы по разным типам экзаменов
    section_avg_result = await db.execute(
        select(func.avg(SectionExam.correct_answers))
        .join(SectionExam.section)
        .filter(SectionExam.student_id == student_id, Section.subject_id == subject_id)
    )
    section_avg = section_avg_result.scalar() or 0

    block_avg_result = await db.execute(
        select(func.avg(BlockExam.correct_answers)).filter(
            BlockExam.student_id == student_id, BlockExam.subject_id == subject_id
        )
    )
    block_avg = block_avg_result.scalar() or 0

    current_avg_result = await db.execute(
        select(
            func.avg(
                CurrentRating.current_correct_answers
                + CurrentRating.second_current_correct_answers
            )
        ).filter(
            CurrentRating.student_id == student_id,
            CurrentRating.subject_id == subject_id,
        )
    )
    current_avg = current_avg_result.scalar() or 0

    topic_avg_result = await db.execute(
        select(func.avg(TopicTest.correct_answers))
        .join(TopicTest.topic)
        .join(Topic.block)
        .join(Block.section)
        .filter(TopicTest.student_id == student_id, Section.subject_id == subject_id)
    )
    topic_avg = topic_avg_result.scalar() or 0

    # Получаем количество записей для весового коэффициента
    section_count_result = await db.execute(
        select(func.count(SectionExam.section_exam_id))
        .join(SectionExam.section)
        .filter(SectionExam.student_id == student_id, Section.subject_id == subject_id)
    )
    section_count = section_count_result.scalar()

    block_count_result = await db.execute(
        select(func.count(BlockExam.block_exam_id)).filter(
            BlockExam.student_id == student_id, BlockExam.subject_id == subject_id
        )
    )
    block_count = block_count_result.scalar()

    current_count_result = await db.execute(
        select(func.count(CurrentRating.rating_id)).filter(
            CurrentRating.student_id == student_id,
            CurrentRating.subject_id == subject_id,
        )
    )
    current_count = current_count_result.scalar()

    topic_count_result = await db.execute(
        select(func.count(TopicTest.topic_test_id))
        .join(TopicTest.topic)
        .join(Topic.block)
        .join(Block.section)
        .filter(TopicTest.student_id == student_id, Section.subject_id == subject_id)
    )
    topic_count = topic_count_result.scalar()

    # Вычисляем итоговую оценку с весовыми коэффициентами
    weights = {"section": 0.3, "block": 0.3, "current": 0.25, "topic": 0.15}

    total_weight = 0
    weighted_sum = 0

    if section_count > 0:
        weighted_sum += section_avg * weights["section"]
        total_weight += weights["section"]

    if block_count > 0:
        weighted_sum += block_avg * weights["block"]
        total_weight += weights["block"]

    if current_count > 0:
        weighted_sum += current_avg * weights["current"]
        total_weight += weights["current"]

    if topic_count > 0:
        weighted_sum += topic_avg * weights["topic"]
        total_weight += weights["topic"]

    final_grade = (weighted_sum / total_weight) if total_weight > 0 else 0

    return {
        "student_id": student_id,
        "subject_id": subject_id,
        "section_average": round(float(section_avg), 2),
        "block_average": round(float(block_avg), 2),
        "current_average": round(float(current_avg), 2),
        "topic_average": round(float(topic_avg), 2),
        "final_grade": round(float(final_grade), 2),
        "counts": {
            "section_exams": section_count,
            "block_exams": block_count,
            "current_ratings": current_count,
            "topic_tests": topic_count,
        },
    }

# auth/
# 1. admin_service
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models.user import Admin, AdminInfo, AdminStatus, User, UserRole

# ===========================================
# ADMIN OPERATIONS (Updated - without create)
# ===========================================


async def get_admin_by_id_db(db: AsyncSession, admin_id: int) -> Admin:
    """Получение администратора по ID"""

    result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )
    return admin


async def update_admin_db(
    db: AsyncSession,
    admin_id: int,
    schedule: Optional[str] = None,
    admin_status: Optional[AdminStatus] = None,
) -> Admin:
    """Обновление данных администратора"""

    result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )

    if schedule is not None:
        admin.schedule = schedule
    if admin_status is not None:
        admin.admin_status = admin_status

    await db.commit()
    await db.refresh(admin)
    return admin


async def delete_admin_db(db: AsyncSession, admin_id: int) -> dict:
    """Удаление администратора"""

    result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )
    await db.delete(admin)
    await db.commit()
    return {"status": "Удален"}


# ===========================================
# ADMIN INFO OPERATIONS
# ===========================================


async def create_admin_info_db(
    db: AsyncSession,
    admin_id: int,
    admin_number: Optional[str] = None,
    employment: Optional[str] = None,
    admin_hobby: Optional[str] = None,
) -> AdminInfo:
    """Создание дополнительной информации об администраторе"""

    # Проверяем, что администратор существует
    admin_result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = admin_result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )

    # Проверяем, что информация еще не создана
    existing_info_result = await db.execute(
        select(AdminInfo).filter(AdminInfo.admin_id == admin_id)
    )
    existing_info = existing_info_result.scalar_one_or_none()
    if existing_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Информация об администраторе уже существует",
        )

    admin_info = AdminInfo(
        admin_id=admin_id,
        admin_number=admin_number,
        employment=employment,
        admin_hobby=admin_hobby,
    )
    db.add(admin_info)
    await db.commit()
    await db.refresh(admin_info)
    return admin_info


async def get_admin_info_db(db: AsyncSession, admin_id: int) -> AdminInfo:
    """Получение дополнительной информации об администраторе"""

    result = await db.execute(select(AdminInfo).filter(AdminInfo.admin_id == admin_id))
    admin_info = result.scalar_one_or_none()
    if not admin_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об администраторе не найдена",
        )
    return admin_info


async def update_admin_info_db(
    db: AsyncSession,
    admin_id: int,
    admin_number: Optional[str] = None,
    employment: Optional[str] = None,
    admin_hobby: Optional[str] = None,
) -> AdminInfo:
    """Обновление дополнительной информации об администраторе"""

    result = await db.execute(select(AdminInfo).filter(AdminInfo.admin_id == admin_id))
    admin_info = result.scalar_one_or_none()
    if not admin_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об администраторе не найдена",
        )

    if admin_number is not None:
        admin_info.admin_number = admin_number
    if employment is not None:
        admin_info.employment = employment
    if admin_hobby is not None:
        admin_info.admin_hobby = admin_hobby

    await db.commit()
    await db.refresh(admin_info)
    return admin_info


async def delete_admin_info_db(db: AsyncSession, admin_id: int) -> dict:
    """Удаление дополнительной информации об администраторе"""

    result = await db.execute(select(AdminInfo).filter(AdminInfo.admin_id == admin_id))
    admin_info = result.scalar_one_or_none()
    if not admin_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об администраторе не найдена",
        )
    await db.delete(admin_info)
    await db.commit()
    return {"status": "Удалена"}


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_all_admins_db(db: AsyncSession) -> List[Admin]:
    """Получение всех администраторов"""

    result = await db.execute(select(Admin))
    admins = result.scalars().all()
    return admins


async def get_active_admins_db(db: AsyncSession) -> List[Admin]:
    """Получение всех активных администраторов"""

    result = await db.execute(
        select(Admin).filter(Admin.admin_status == AdminStatus.ACTIVE)
    )
    admins = result.scalars().all()
    return admins


async def get_inactive_admins_db(db: AsyncSession) -> List[Admin]:
    """Получение всех неактивных администраторов"""

    result = await db.execute(
        select(Admin).filter(Admin.admin_status == AdminStatus.INACTIVE)
    )
    admins = result.scalars().all()
    return admins


async def activate_admin_db(db: AsyncSession, admin_id: int) -> Admin:
    """Активация администратора"""

    result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )

    admin.admin_status = AdminStatus.ACTIVE
    await db.commit()
    await db.refresh(admin)
    return admin


async def deactivate_admin_db(db: AsyncSession, admin_id: int) -> Admin:
    """Деактивация администратора"""

    result = await db.execute(select(Admin).filter(Admin.admin_id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Администратор не найден"
        )

    admin.admin_status = AdminStatus.INACTIVE
    await db.commit()
    await db.refresh(admin)
    return admin


async def get_admin_statistics_db(db: AsyncSession) -> dict:
    """Получение статистики администраторов"""

    total_admins_result = await db.execute(select(func.count(Admin.admin_id)))
    total_admins = total_admins_result.scalar()

    active_admins_result = await db.execute(
        select(func.count(Admin.admin_id)).filter(
            Admin.admin_status == AdminStatus.ACTIVE
        )
    )
    active_admins = active_admins_result.scalar()

    inactive_admins_result = await db.execute(
        select(func.count(Admin.admin_id)).filter(
            Admin.admin_status == AdminStatus.INACTIVE
        )
    )
    inactive_admins = inactive_admins_result.scalar()

    return {
        "total_admins": total_admins,
        "active_admins": active_admins,
        "inactive_admins": inactive_admins,
    }

# 2. student_service
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.academic import (
    GroupProgress,
    University,
    Faculty,
    UniversityType,
)
from app.database.models.assessment import TopicTest, ModulExam, BlockExam, SectionExam
from app.database.models.user import Student, StudentInfo, StudentStatus, User, UserRole

# ===========================================
# STUDENT OPERATIONS (Updated - without create)
# ===========================================


async def get_student_by_id_db(db: AsyncSession, student_id: int) -> Student:
    """Получение студента по ID"""

    result = await db.execute(select(Student).filter(Student.student_id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден"
        )
    return student


async def update_student_db(
    db: AsyncSession,
    student_id: int,
    direction: Optional[str] = None,
    group_id: Optional[int] = None,
    goal: Optional[str] = None,
    student_status: Optional[StudentStatus] = None,
) -> Student:
    """Обновление данных студента"""

    result = await db.execute(select(Student).filter(Student.student_id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден"
        )

    if direction is not None:
        student.direction = direction
    if group_id is not None:
        student.group_id = group_id
    if goal is not None:
        student.goal = goal
    if student_status is not None:
        student.student_status = student_status

    await db.commit()
    await db.refresh(student)
    return student


async def delete_student_db(db: AsyncSession, student_id: int) -> dict:
    """Удаление студента"""

    result = await db.execute(select(Student).filter(Student.student_id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден"
        )
    await db.delete(student)
    await db.commit()
    return {"status": "Удален"}


# ===========================================
# STUDENT INFO OPERATIONS
# ===========================================


async def create_student_info_db(
    db: AsyncSession,
    student_id: int,
    hobby: Optional[str] = None,
    sex: Optional[str] = None,
    address: Optional[str] = None,
    birthday: Optional[datetime] = None,
) -> StudentInfo:
    """Создание дополнительной информации о студенте"""

    # Проверяем, что студент существует
    student_result = await db.execute(
        select(Student).filter(Student.student_id == student_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден"
        )

    # Проверяем, что информация еще не создана
    existing_info_result = await db.execute(
        select(StudentInfo).filter(StudentInfo.student_id == student_id)
    )
    existing_info = existing_info_result.scalar_one_or_none()
    if existing_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Информация о студенте уже существует",
        )

    student_info = StudentInfo(
        student_id=student_id, hobby=hobby, sex=sex, address=address, birthday=birthday
    )
    db.add(student_info)
    await db.commit()
    await db.refresh(student_info)
    return student_info


async def update_student_info_db(
    db: AsyncSession,
    student_id: int,
    hobby: Optional[str] = None,
    sex: Optional[str] = None,
    address: Optional[str] = None,
    birthday: Optional[datetime] = None,
) -> StudentInfo:
    """Обновление дополнительной информации о студенте"""

    result = await db.execute(
        select(StudentInfo).filter(StudentInfo.student_id == student_id)
    )
    student_info = result.scalar_one_or_none()
    if not student_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация о студенте не найдена",
        )

    if hobby is not None:
        student_info.hobby = hobby
    if sex is not None:
        student_info.sex = sex
    if address is not None:
        student_info.address = address
    if birthday is not None:
        student_info.birthday = birthday

    await db.commit()
    await db.refresh(student_info)
    return student_info


# ===========================================
# GROUP PROGRESS OPERATIONS
# ===========================================


async def add_group_progress_db(
    db: AsyncSession,
    group_id: int,
    topic_id: int,
    data: str,
    average_score: Optional[float] = None,
    notes: Optional[str] = None,
) -> GroupProgress:
    """Добавление прогресса группы по конкретному уроку"""

    # Проверяем, существует ли уже запись для данной группы и урока
    existing_progress_result = await db.execute(
        select(GroupProgress).filter(
            GroupProgress.group_id == group_id, GroupProgress.topic_id == topic_id
        )
    )
    existing_progress = existing_progress_result.scalar_one_or_none()

    if existing_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Прогресс для группы {group_id} по уроку {topic_id} уже существует",
        )

    new_progress = GroupProgress(
        group_id=group_id,
        topic_id=topic_id,
        data=data,
        average_score=average_score,
        notes=notes,
    )
    db.add(new_progress)
    await db.commit()
    await db.refresh(new_progress)
    return new_progress


async def update_group_progress_db(
    db: AsyncSession,
    group_progress_id: int,
    data: Optional[str] = None,
    average_score: Optional[float] = None,
    notes: Optional[str] = None,
) -> GroupProgress:
    """Изменение прогресса группы по конкретному уроку"""

    result = await db.execute(
        select(GroupProgress).filter(
            GroupProgress.group_progress_id == group_progress_id
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Прогресс группы не найден"
        )

    if data is not None:
        progress.data = data
    if average_score is not None:
        progress.average_score = average_score
    if notes is not None:
        progress.notes = notes

    await db.commit()
    await db.refresh(progress)
    return progress


async def delete_group_progress_db(db: AsyncSession, group_progress_id: int) -> dict:
    """Удаление прогресса группы по конкретному уроку"""

    result = await db.execute(
        select(GroupProgress).filter(
            GroupProgress.group_progress_id == group_progress_id
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Прогресс группы не найден"
        )

    await db.delete(progress)
    await db.commit()
    return {"status": "Удален"}


async def get_group_progress_by_lesson_db(
    db: AsyncSession, group_id: int, topic_id: int
) -> GroupProgress:
    """Получение прогресса группы по конкретному уроку"""

    result = await db.execute(
        select(GroupProgress).filter(
            GroupProgress.group_id == group_id, GroupProgress.topic_id == topic_id
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Прогресс группы {group_id} по уроку {topic_id} не найден",
        )

    return progress


# ===========================================
# STUDENT EXAM STATUS OPERATIONS
# ===========================================


async def get_overdue_exams_db(db: AsyncSession, student_id: int) -> dict:
    """Получение всех просроченных тестов конкретного ученика"""

    today = datetime.now().date()

    # Получаем все экзамены студента, где дата экзамена меньше сегодняшней
    overdue_topic_tests_result = await db.execute(
        select(TopicTest).filter(
            and_(TopicTest.student_id == student_id, TopicTest.attempt_date < today)
        )
    )
    overdue_topic_tests = overdue_topic_tests_result.scalars().all()

    overdue_module_exams_result = await db.execute(
        select(ModulExam).filter(
            and_(ModulExam.student_id == student_id, ModulExam.exam_date < today)
        )
    )
    overdue_module_exams = overdue_module_exams_result.scalars().all()

    overdue_block_exams_result = await db.execute(
        select(BlockExam).filter(
            and_(BlockExam.student_id == student_id, BlockExam.exam_date < today)
        )
    )
    overdue_block_exams = overdue_block_exams_result.scalars().all()

    overdue_section_exams_result = await db.execute(
        select(SectionExam).filter(
            and_(SectionExam.student_id == student_id, SectionExam.exam_date < today)
        )
    )
    overdue_section_exams = overdue_section_exams_result.scalars().all()

    return {
        "student_id": student_id,
        "overdue_topic_tests": overdue_topic_tests,
        "overdue_module_exams": overdue_module_exams,
        "overdue_block_exams": overdue_block_exams,
        "overdue_section_exams": overdue_section_exams,
        "total_overdue": (
            len(overdue_topic_tests)
            + len(overdue_module_exams)
            + len(overdue_block_exams)
            + len(overdue_section_exams)
        ),
    }


async def get_upcoming_exams_db(db: AsyncSession, student_id: int) -> dict:
    """Получение актуальных тестов (в ближайшие 2 дня) конкретного ученика"""

    today = datetime.now().date()
    two_days_later = today + timedelta(days=2)

    # Получаем все экзамены студента на ближайшие 2 дня
    upcoming_topic_tests_result = await db.execute(
        select(TopicTest).filter(
            and_(
                TopicTest.student_id == student_id,
                TopicTest.attempt_date >= today,
                TopicTest.attempt_date <= two_days_later,
            )
        )
    )
    upcoming_topic_tests = upcoming_topic_tests_result.scalars().all()

    upcoming_module_exams_result = await db.execute(
        select(ModulExam).filter(
            and_(
                ModulExam.student_id == student_id,
                ModulExam.exam_date >= today,
                ModulExam.exam_date <= two_days_later,
            )
        )
    )
    upcoming_module_exams = upcoming_module_exams_result.scalars().all()

    upcoming_block_exams_result = await db.execute(
        select(BlockExam).filter(
            and_(
                BlockExam.student_id == student_id,
                BlockExam.exam_date >= today,
                BlockExam.exam_date <= two_days_later,
            )
        )
    )
    upcoming_block_exams = upcoming_block_exams_result.scalars().all()

    upcoming_section_exams_result = await db.execute(
        select(SectionExam).filter(
            and_(
                SectionExam.student_id == student_id,
                SectionExam.exam_date >= today,
                SectionExam.exam_date <= two_days_later,
            )
        )
    )
    upcoming_section_exams = upcoming_section_exams_result.scalars().all()

    return {
        "student_id": student_id,
        "upcoming_topic_tests": upcoming_topic_tests,
        "upcoming_module_exams": upcoming_module_exams,
        "upcoming_block_exams": upcoming_block_exams,
        "upcoming_section_exams": upcoming_section_exams,
        "total_upcoming": (
            len(upcoming_topic_tests)
            + len(upcoming_module_exams)
            + len(upcoming_block_exams)
            + len(upcoming_section_exams)
        ),
    }


# ===========================================
# UNIVERSITY OPERATIONS
# ===========================================


async def add_university_db(
    db: AsyncSession,
    name: str,
    entrance_score: Optional[float],
    university_type: UniversityType,
    location: str,
    website_url: str,
    logo_url: Optional[str] = None,
    contact_phone: Optional[str] = None,
) -> University:
    """Добавление нового университета"""

    # Проверяем, существует ли уже университет с таким именем
    existing_university_result = await db.execute(
        select(University).filter(University.name == name)
    )
    existing_university = existing_university_result.scalar_one_or_none()
    if existing_university:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Университет с именем '{name}' уже существует",
        )

    new_university = University(
        name=name,
        entrance_score=entrance_score,
        type=university_type,
        location=location,
        website_url=website_url,
        logo_url=logo_url,
        contact_phone=contact_phone,
    )
    db.add(new_university)
    await db.commit()
    await db.refresh(new_university)
    return new_university


async def update_university_db(
    db: AsyncSession,
    university_id: int,
    name: Optional[str] = None,
    entrance_score: Optional[float] = None,
    university_type: Optional[UniversityType] = None,
    location: Optional[str] = None,
    website_url: Optional[str] = None,
    logo_url: Optional[str] = None,
    contact_phone: Optional[str] = None,
) -> University:
    """Изменение информации о университете"""

    result = await db.execute(
        select(University).filter(University.university_id == university_id)
    )
    university = result.scalar_one_or_none()

    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Университет не найден"
        )

    if name is not None:
        university.name = name
    if entrance_score is not None:
        university.entrance_score = entrance_score
    if university_type is not None:
        university.type = university_type
    if location is not None:
        university.location = location
    if website_url is not None:
        university.website_url = website_url
    if logo_url is not None:
        university.logo_url = logo_url
    if contact_phone is not None:
        university.contact_phone = contact_phone

    await db.commit()
    await db.refresh(university)
    return university


async def delete_university_db(db: AsyncSession, university_id: int) -> dict:
    """Удаление университета"""

    result = await db.execute(
        select(University).filter(University.university_id == university_id)
    )
    university = result.scalar_one_or_none()

    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Университет не найден"
        )

    await db.delete(university)
    await db.commit()
    return {"status": "Удален"}


async def get_university_by_id_db(db: AsyncSession, university_id: int) -> University:
    """Получение университета по ID"""

    result = await db.execute(
        select(University).filter(University.university_id == university_id)
    )
    university = result.scalar_one_or_none()

    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Университет не найден"
        )

    return university


async def get_all_universities_db(db: AsyncSession) -> List[University]:
    """Получение всех университетов"""

    result = await db.execute(select(University))
    universities = result.scalars().all()
    return universities


# ===========================================
# FACULTY OPERATIONS
# ===========================================


async def add_faculty_db(
    db: AsyncSession,
    university_id: int,
    name: str,
    description: Optional[str] = None,
    entrance_score: Optional[float] = None,
    annual_cost: Optional[str] = None,
    available_place: Optional[str] = None,
    code: Optional[str] = None,
) -> Faculty:
    """Добавление нового факультета"""

    # Проверяем, существует ли университет
    university_result = await db.execute(
        select(University).filter(University.university_id == university_id)
    )
    university = university_result.scalar_one_or_none()
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Университет не найден"
        )

    # Проверяем, существует ли уже факультет с таким именем в данном университете
    existing_faculty_result = await db.execute(
        select(Faculty).filter(
            Faculty.university_id == university_id, Faculty.name == name
        )
    )
    existing_faculty = existing_faculty_result.scalar_one_or_none()
    if existing_faculty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Факультет '{name}' уже существует в данном университете",
        )

    new_faculty = Faculty(
        university_id=university_id,
        name=name,
        description=description,
        entrance_score=entrance_score,
        annual_cost=annual_cost,
        available_place=available_place,
        code=code,
    )
    db.add(new_faculty)
    await db.commit()
    await db.refresh(new_faculty)
    return new_faculty


async def update_faculty_db(
    db: AsyncSession,
    faculty_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    entrance_score: Optional[float] = None,
    annual_cost: Optional[str] = None,
    available_place: Optional[str] = None,
    code: Optional[str] = None,
) -> Faculty:
    """Изменение информации о факультете"""

    result = await db.execute(select(Faculty).filter(Faculty.faculty_id == faculty_id))
    faculty = result.scalar_one_or_none()

    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Факультет не найден"
        )

    if name is not None:
        faculty.name = name
    if description is not None:
        faculty.description = description
    if entrance_score is not None:
        faculty.entrance_score = entrance_score
    if annual_cost is not None:
        faculty.annual_cost = annual_cost
    if available_place is not None:
        faculty.available_place = available_place
    if code is not None:
        faculty.code = code

    await db.commit()
    await db.refresh(faculty)
    return faculty


async def delete_faculty_db(db: AsyncSession, faculty_id: int) -> dict:
    """Удаление факультета"""

    result = await db.execute(select(Faculty).filter(Faculty.faculty_id == faculty_id))
    faculty = result.scalar_one_or_none()

    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Факультет не найден"
        )

    await db.delete(faculty)
    await db.commit()
    return {"status": "Удален"}


async def get_faculty_by_id_db(db: AsyncSession, faculty_id: int) -> Faculty:
    """Получение факультета по ID"""

    result = await db.execute(select(Faculty).filter(Faculty.faculty_id == faculty_id))
    faculty = result.scalar_one_or_none()

    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Факультет не найден"
        )

    return faculty


async def get_faculties_by_university_db(
    db: AsyncSession, university_id: int
) -> List[Faculty]:
    """Получение всех факультетов конкретного университета"""

    result = await db.execute(
        select(Faculty).filter(Faculty.university_id == university_id)
    )
    faculties = result.scalars().all()

    if not faculties:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Факультеты для университета {university_id} не найдены",
        )

    return faculties


async def get_all_faculties_db(db: AsyncSession) -> List[Faculty]:
    """Получение всех факультетов"""

    result = await db.execute(select(Faculty))
    faculties = result.scalars().all()
    return faculties


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_students_by_group_db(db: AsyncSession, group_id: int) -> List[Student]:
    """Получение всех студентов группы"""

    result = await db.execute(select(Student).filter(Student.group_id == group_id))
    students = result.scalars().all()
    if not students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студенты группы {group_id} не найдены",
        )
    return students


async def get_active_students_db(db: AsyncSession) -> List[Student]:
    """Получение всех активных студентов"""

    result = await db.execute(
        select(Student).filter(Student.student_status == StudentStatus.ACTIVE)
    )
    students = result.scalars().all()
    return students


async def get_inactive_students_db(db: AsyncSession) -> List[Student]:
    """Получение всех неактивных студентов"""

    result = await db.execute(
        select(Student).filter(Student.student_status == StudentStatus.INACTIVE)
    )
    students = result.scalars().all()
    return students


async def activate_student_db(db: AsyncSession, student_id: int) -> Student:
    """Активация студента"""

    result = await db.execute(select(Student).filter(Student.student_id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден"
        )

    student.student_status = StudentStatus.ACTIVE
    await db.commit()
    await db.refresh(student)
    return student


async def deactivate_student_db(db: AsyncSession, student_id: int) -> Student:
    """Деактивация студента"""

    result = await db.execute(select(Student).filter(Student.student_id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден"
        )

    student.student_status = StudentStatus.INACTIVE
    await db.commit()
    await db.refresh(student)
    return student

# 3. teacher_service
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.models.user import Teacher, TeacherInfo, TeacherStatus, User, UserRole
from app.database.models.academic import Subject

# ===========================================
# TEACHER OPERATIONS (Updated - without create)
# ===========================================


def get_teacher_by_id_db(db: Session, teacher_id: int) -> Teacher:
    """Получение учителя по ID"""

    teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )
    return teacher


def update_teacher_db(
    db: Session,
    teacher_id: int,
    teacher_schedule: Optional[str] = None,
    teacher_status: Optional[TeacherStatus] = None,
) -> Teacher:
    """Обновление данных учителя"""

    teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    if teacher_schedule is not None:
        teacher.teacher_schedule = teacher_schedule
    if teacher_status is not None:
        teacher.teacher_status = teacher_status

    db.commit()
    db.refresh(teacher)
    return teacher


def delete_teacher_db(db: Session, teacher_id: int) -> dict:
    """Удаление учителя"""

    teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )
    db.delete(teacher)
    db.commit()
    return {"status": "Удален"}


# ===========================================
# TEACHER INFO OPERATIONS
# ===========================================


def create_teacher_info_db(
    db: Session,
    teacher_id: int,
    teacher_employment: Optional[str] = None,
    teacher_number: Optional[str] = None,
    dop_info: Optional[str] = None,
    education_background: Optional[str] = None,
    years_experiense: Optional[int] = None,
    certifications: Optional[str] = None,
    availability: Optional[str] = None,
    languages: Optional[str] = None,
) -> TeacherInfo:
    """Создание дополнительной информации об учителе"""

    # Проверяем, что учитель существует
    teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    # Проверяем, что информация еще не создана
    existing_info = db.query(TeacherInfo).filter_by(teacher_id=teacher_id).first()
    if existing_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Информация об учителе уже существует",
        )

    teacher_info = TeacherInfo(
        teacher_id=teacher_id,
        teacher_employment=teacher_employment,
        teacher_number=teacher_number,
        dop_info=dop_info,
        education_background=education_background,
        years_experiense=years_experiense,
        certifications=certifications,
        availability=availability,
        languages=languages,
    )
    db.add(teacher_info)
    db.commit()
    db.refresh(teacher_info)
    return teacher_info


def get_teacher_info_db(db: Session, teacher_id: int) -> TeacherInfo:
    """Получение дополнительной информации об учителе"""

    teacher_info = db.query(TeacherInfo).filter_by(teacher_id=teacher_id).first()
    if not teacher_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об учителе не найдена",
        )
    return teacher_info


def update_teacher_info_db(
    db: Session,
    teacher_id: int,
    teacher_employment: Optional[str] = None,
    teacher_number: Optional[str] = None,
    dop_info: Optional[str] = None,
    education_background: Optional[str] = None,
    years_experiense: Optional[int] = None,
    certifications: Optional[str] = None,
    availability: Optional[str] = None,
    languages: Optional[str] = None,
) -> TeacherInfo:
    """Обновление дополнительной информации об учителе"""

    teacher_info = db.query(TeacherInfo).filter_by(teacher_id=teacher_id).first()
    if not teacher_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об учителе не найдена",
        )

    if teacher_employment is not None:
        teacher_info.teacher_employment = teacher_employment
    if teacher_number is not None:
        teacher_info.teacher_number = teacher_number
    if dop_info is not None:
        teacher_info.dop_info = dop_info
    if education_background is not None:
        teacher_info.education_background = education_background
    if years_experiense is not None:
        teacher_info.years_experiense = years_experiense
    if certifications is not None:
        teacher_info.certifications = certifications
    if availability is not None:
        teacher_info.availability = availability
    if languages is not None:
        teacher_info.languages = languages

    db.commit()
    db.refresh(teacher_info)
    return teacher_info


def delete_teacher_info_db(db: Session, teacher_id: int) -> dict:
    """Удаление дополнительной информации об учителе"""

    teacher_info = db.query(TeacherInfo).filter_by(teacher_id=teacher_id).first()
    if not teacher_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Информация об учителе не найдена",
        )
    db.delete(teacher_info)
    db.commit()
    return {"status": "Удалена"}


# ===========================================
# TEACHER-SUBJECT OPERATIONS
# ===========================================


def assign_subject_to_teacher_db(
    db: Session, teacher_id: int, subject_id: int
) -> Teacher:
    """Назначение предмета учителю"""

    teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    subject = db.query(Subject).filter_by(subject_id=subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    # Проверяем, не назначен ли уже этот предмет учителю
    if subject in teacher.subjects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Предмет уже назначен данному учителю",
        )

    teacher.subjects.append(subject)
    db.commit()
    db.refresh(teacher)
    return teacher


def remove_subject_from_teacher_db(
    db: Session, teacher_id: int, subject_id: int
) -> Teacher:
    """Удаление предмета у учителя"""

    teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    subject = db.query(Subject).filter_by(subject_id=subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    # Проверяем, назначен ли этот предмет учителю
    if subject not in teacher.subjects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Предмет не назначен данному учителю",
        )

    teacher.subjects.remove(subject)
    db.commit()
    db.refresh(teacher)
    return teacher


def get_teacher_subjects_db(db: Session, teacher_id: int) -> List[Subject]:
    """Получение предметов учителя"""

    teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )
    return teacher.subjects


def get_teachers_by_subject_db(db: Session, subject_id: int) -> List[Teacher]:
    """Получение учителей по предмету"""

    subject = db.query(Subject).filter_by(subject_id=subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )
    return subject.teachers


# ===========================================
# HELPER FUNCTIONS
# ===========================================


def get_all_teachers_db(db: Session) -> List[Teacher]:
    """Получение всех учителей"""

    teachers = db.query(Teacher).all()
    return teachers


def get_active_teachers_db(db: Session) -> List[Teacher]:
    """Получение всех активных учителей"""

    teachers = db.query(Teacher).filter_by(teacher_status=TeacherStatus.ACTIVE).all()
    return teachers


def get_inactive_teachers_db(db: Session) -> List[Teacher]:
    """Получение всех неактивных учителей"""

    teachers = db.query(Teacher).filter_by(teacher_status=TeacherStatus.INACTIVE).all()
    return teachers


def activate_teacher_db(db: Session, teacher_id: int) -> Teacher:
    """Активация учителя"""

    teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    teacher.teacher_status = TeacherStatus.ACTIVE
    db.commit()
    db.refresh(teacher)
    return teacher


def deactivate_teacher_db(db: Session, teacher_id: int) -> Teacher:
    """Деактивация учителя"""

    teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден"
        )

    teacher.teacher_status = TeacherStatus.INACTIVE
    db.commit()
    db.refresh(teacher)
    return teacher


def get_teacher_statistics_db(db: Session) -> dict:
    """Получение статистики учителей"""

    total_teachers = db.query(Teacher).count()
    active_teachers = (
        db.query(Teacher).filter_by(teacher_status=TeacherStatus.ACTIVE).count()
    )
    inactive_teachers = (
        db.query(Teacher).filter_by(teacher_status=TeacherStatus.INACTIVE).count()
    )

    return {
        "total_teachers": total_teachers,
        "active_teachers": active_teachers,
        "inactive_teachers": inactive_teachers,
    }

# 4. user_service
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import or_, and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import (
    User,
    UserRole,
    Student,
    Teacher,
    Admin,
    ParentInfo,
    StudentStatus,
    TeacherStatus,
    AdminStatus,
)

# ===========================================
# EXISTING USER OPERATIONS (Updated)
# ===========================================


async def create_user_db(
    db: AsyncSession,
    name: str,
    surname: str,
    phone: str,
    password: str,
    role: UserRole,
    email: Optional[str] = None,
    photo: Optional[str] = None,
    # Параметры для студента
    direction: Optional[str] = None,
    group_id: Optional[int] = None,
    goal: Optional[str] = None,
    # Параметры для учителя
    teacher_schedule: Optional[str] = None,
    # Параметры для администратора
    admin_schedule: Optional[str] = None,
) -> User:
    """Создание нового пользователя с соответствующей ролевой записью"""

    # Проверяем уникальность телефона
    existing_user_result = await db.execute(select(User).filter(User.phone == phone))
    existing_user = existing_user_result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким номером телефона уже существует",
        )

    # Проверяем уникальность email, если он указан
    if email:
        existing_email_result = await db.execute(
            select(User).filter(User.email == email)
        )
        existing_email = existing_email_result.scalar_one_or_none()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует",
            )

    new_user = User(
        name=name,
        surname=surname,
        phone=phone,
        email=email,
        password=password,
        role=role,
        photo=photo,
    )
    db.add(new_user)
    await db.flush()  # Получаем ID пользователя без коммита

    # Создаем соответствующую ролевую запись
    if role == UserRole.STUDENT:
        if not group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для студента обязательно указать group_id",
            )
        student = Student(
            student_id=new_user.user_id,
            direction=direction or "",
            group_id=group_id,
            goal=goal,
            student_status=StudentStatus.ACTIVE,
        )
        db.add(student)

    elif role == UserRole.TEACHER:
        teacher = Teacher(
            teacher_id=new_user.user_id,
            teacher_schedule=teacher_schedule,
            teacher_status=TeacherStatus.ACTIVE,
        )
        db.add(teacher)

    elif role == UserRole.ADMIN:
        admin = Admin(
            admin_id=new_user.user_id,
            schedule=admin_schedule,
            admin_status=AdminStatus.ACTIVE,
        )
        db.add(admin)

    elif role == UserRole.PARENT:
        parent = ParentInfo(parent_id=new_user.user_id)
        db.add(parent)

    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user_by_id_db(db: AsyncSession, user_id: int) -> User:
    """Получение пользователя по ID"""

    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )
    return user


async def get_user_by_phone_db(db: AsyncSession, phone: str) -> User:
    """Получение пользователя по номеру телефона"""

    result = await db.execute(select(User).filter(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким номером телефона не найден",
        )
    return user


async def update_user_db(
    db: AsyncSession,
    user_id: int,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    photo: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> User:
    """Обновление данных пользователя"""

    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    # Проверяем уникальность телефона, если он изменяется
    if phone and phone != user.phone:
        existing_phone_result = await db.execute(
            select(User).filter(User.phone == phone)
        )
        existing_phone = existing_phone_result.scalar_one_or_none()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким номером телефона уже существует",
            )

    # Проверяем уникальность email, если он изменяется
    if email and email != user.email:
        existing_email_result = await db.execute(
            select(User).filter(User.email == email)
        )
        existing_email = existing_email_result.scalar_one_or_none()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует",
            )

    if name is not None:
        user.name = name
    if surname is not None:
        user.surname = surname
    if phone is not None:
        user.phone = phone
    if email is not None:
        user.email = email
    if password is not None:
        user.password = password
    if photo is not None:
        user.photo = photo
    if is_active is not None:
        user.is_active = is_active

    user.updated_at = datetime.now()
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user_db(db: AsyncSession, user_id: int) -> dict:
    """Удаление пользователя"""

    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )
    await db.delete(user)
    await db.commit()
    return {"status": "Удален"}


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_users_by_role_db(db: AsyncSession, role: UserRole) -> List[User]:
    """Получение пользователей по роли"""

    result = await db.execute(select(User).filter(User.role == role))
    users = result.scalars().all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователи с ролью {role.value} не найдены",
        )
    return users


async def search_users_db(db: AsyncSession, search_query: str) -> List[User]:
    """Поиск пользователей по имени, фамилии, телефону или email"""

    result = await db.execute(
        select(User).filter(
            or_(
                User.name.ilike(f"%{search_query}%"),
                User.surname.ilike(f"%{search_query}%"),
                User.phone.ilike(f"%{search_query}%"),
                User.email.ilike(f"%{search_query}%") if search_query else False,
            )
        )
    )
    users = result.scalars().all()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователи, соответствующие запросу '{search_query}', не найдены",
        )
    return users


async def update_last_login_time_db(db: AsyncSession, user_id: int) -> User:
    """Обновление времени последнего входа"""

    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    # Обновляем время последнего входа в зависимости от роли
    if user.role == UserRole.STUDENT and user.student:
        user.student.last_login = datetime.now()

    user.updated_at = datetime.now()
    await db.commit()
    await db.refresh(user)
    return user


async def get_inactive_users_db(
    db: AsyncSession, role: Optional[UserRole] = None
) -> List[User]:
    """Получение неактивных пользователей"""

    query = select(User).filter(User.is_active == False)

    if role:
        query = query.filter(User.role == role)

    result = await db.execute(query)
    users = result.scalars().all()

    if not users:
        role_filter = f" с ролью {role.value}" if role else ""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Неактивные пользователи{role_filter} не найдены",
        )
    return users


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_all_users_db(db: AsyncSession) -> List[User]:
    """Получение всех пользователей"""

    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


async def get_active_users_db(
    db: AsyncSession, role: Optional[UserRole] = None
) -> List[User]:
    """Получение активных пользователей"""

    query = select(User).filter(User.is_active == True)

    if role:
        query = query.filter(User.role == role)

    result = await db.execute(query)
    users = result.scalars().all()
    return users


async def deactivate_user_db(db: AsyncSession, user_id: int) -> User:
    """Деактивация пользователя"""

    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    user.is_active = False
    user.updated_at = datetime.now()
    await db.commit()
    await db.refresh(user)
    return user


async def activate_user_db(db: AsyncSession, user_id: int) -> User:
    """Активация пользователя"""

    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    user.is_active = True
    user.updated_at = datetime.now()
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_statistics_db(db: AsyncSession) -> dict:
    """Получение статистики пользователей"""

    total_users_result = await db.execute(select(func.count(User.user_id)))
    total_users = total_users_result.scalar()

    active_users_result = await db.execute(
        select(func.count(User.user_id)).filter(User.is_active == True)
    )
    active_users = active_users_result.scalar()

    inactive_users_result = await db.execute(
        select(func.count(User.user_id)).filter(User.is_active == False)
    )
    inactive_users = inactive_users_result.scalar()

    students_count_result = await db.execute(
        select(func.count(User.user_id)).filter(User.role == UserRole.STUDENT)
    )
    students_count = students_count_result.scalar()

    teachers_count_result = await db.execute(
        select(func.count(User.user_id)).filter(User.role == UserRole.TEACHER)
    )
    teachers_count = teachers_count_result.scalar()

    admins_count_result = await db.execute(
        select(func.count(User.user_id)).filter(User.role == UserRole.ADMIN)
    )
    admins_count = admins_count_result.scalar()

    parents_count_result = await db.execute(
        select(func.count(User.user_id)).filter(User.role == UserRole.PARENT)
    )
    parents_count = parents_count_result.scalar()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "users_by_role": {
            "students": students_count,
            "teachers": teachers_count,
            "admins": admins_count,
            "parents": parents_count,
        },
    }

# content/
# 1. module_service
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models.academic import Moduls

# ===========================================
# EXISTING MODULE OPERATIONS (Updated)
# ===========================================


async def add_modul_db(
    db: AsyncSession,
    start_topic_chem: int,
    start_topic_bio: int,
    end_topic_chem: int,
    end_topic_bio: int,
    order_number: Optional[int] = None,
    name: Optional[str] = None,
) -> Moduls:
    """Добавление нового модуля"""

    new_modul = Moduls(
        start_topic_chem=start_topic_chem,
        start_topic_bio=start_topic_bio,
        end_topic_chem=end_topic_chem,
        end_topic_bio=end_topic_bio,
        order_number=order_number,
        name=name,
    )
    db.add(new_modul)
    await db.commit()
    await db.refresh(new_modul)
    return new_modul


async def delete_modul_db(db: AsyncSession, modul_id: int) -> dict:
    """Удаление модуля"""

    result = await db.execute(select(Moduls).filter(Moduls.modul_id == modul_id))
    modul = result.scalar_one_or_none()
    if not modul:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Модуль не найден"
        )
    await db.delete(modul)
    await db.commit()
    return {"status": "Удалён"}


async def find_modul_db(db: AsyncSession, modul_id: int) -> Moduls:
    """Поиск модуля по ID"""

    result = await db.execute(select(Moduls).filter(Moduls.modul_id == modul_id))
    modul = result.scalar_one_or_none()
    if not modul:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Модуль не найден"
        )
    return modul


async def edit_modul_db(
    db: AsyncSession,
    modul_id: int,
    start_topic_chem: Optional[int] = None,
    start_topic_bio: Optional[int] = None,
    end_topic_chem: Optional[int] = None,
    end_topic_bio: Optional[int] = None,
    order_number: Optional[int] = None,
    name: Optional[str] = None,
) -> Moduls:
    """Редактирование модуля"""

    result = await db.execute(select(Moduls).filter(Moduls.modul_id == modul_id))
    modul = result.scalar_one_or_none()
    if not modul:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Модуль не найден"
        )

    if start_topic_chem is not None:
        modul.start_topic_chem = start_topic_chem
    if start_topic_bio is not None:
        modul.start_topic_bio = start_topic_bio
    if end_topic_chem is not None:
        modul.end_topic_chem = end_topic_chem
    if end_topic_bio is not None:
        modul.end_topic_bio = end_topic_bio
    if order_number is not None:
        modul.order_number = order_number
    if name is not None:
        modul.name = name

    await db.commit()
    await db.refresh(modul)
    return modul


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_all_modules_db(db: AsyncSession) -> List[Moduls]:
    """Получение всех модулей"""

    result = await db.execute(select(Moduls).order_by(Moduls.order_number))
    modules = result.scalars().all()
    return modules


async def get_modules_by_subject_db(
    db: AsyncSession, subject_name: str
) -> List[Moduls]:
    """Получение модулей по предмету (химия или биология)"""

    if subject_name.lower() in ["химия", "chemistry", "chem"]:
        # Возвращаем модули, которые включают темы по химии
        result = await db.execute(
            select(Moduls)
            .filter(
                Moduls.start_topic_chem.isnot(None), Moduls.end_topic_chem.isnot(None)
            )
            .order_by(Moduls.order_number)
        )
        modules = result.scalars().all()
    elif subject_name.lower() in ["биология", "biology", "bio"]:
        # Возвращаем модули, которые включают темы по биологии
        result = await db.execute(
            select(Moduls)
            .filter(
                Moduls.start_topic_bio.isnot(None), Moduls.end_topic_bio.isnot(None)
            )
            .order_by(Moduls.order_number)
        )
        modules = result.scalars().all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверное название предмета. Используйте 'химия' или 'биология'",
        )

    if not modules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модули по предмету '{subject_name}' не найдены",
        )

    return modules


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_module_by_order_db(db: AsyncSession, order_number: int) -> Moduls:
    """Получение модуля по порядковому номеру"""

    result = await db.execute(
        select(Moduls).filter(Moduls.order_number == order_number)
    )
    modul = result.scalar_one_or_none()
    if not modul:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модуль с порядковым номером {order_number} не найден",
        )
    return modul


async def get_modules_count_db(db: AsyncSession) -> int:
    """Получение количества модулей"""

    result = await db.execute(select(func.count(Moduls.modul_id)))
    return result.scalar()


async def get_modules_by_topic_range_db(
    db: AsyncSession, subject_type: str, start_topic: int, end_topic: int
) -> List[Moduls]:
    """Получение модулей по диапазону тем"""

    if subject_type.lower() in ["химия", "chemistry", "chem"]:
        result = await db.execute(
            select(Moduls)
            .filter(
                Moduls.start_topic_chem <= end_topic,
                Moduls.end_topic_chem >= start_topic,
            )
            .order_by(Moduls.order_number)
        )
        modules = result.scalars().all()
    elif subject_type.lower() in ["биология", "biology", "bio"]:
        result = await db.execute(
            select(Moduls)
            .filter(
                Moduls.start_topic_bio <= end_topic, Moduls.end_topic_bio >= start_topic
            )
            .order_by(Moduls.order_number)
        )
        modules = result.scalars().all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный тип предмета"
        )

    return modules

# 2. question_service
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models.assessment import Question
from app.database.models.academic import Topic

# ===========================================
# EXISTING QUESTION OPERATIONS (Updated)
# ===========================================


async def add_question_db(
    db: AsyncSession,
    topic_id: int,
    text: str,
    correct_answers: int,
    answer_1: Optional[str] = None,
    answer_2: Optional[str] = None,
    answer_3: Optional[str] = None,
    answer_4: Optional[str] = None,
    explanation: Optional[str] = None,
    category: Optional[List] = None,
) -> Question:
    """Добавление нового вопроса"""

    # Проверяем, что тема существует
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = topic_result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    new_q = Question(
        topic_id=topic_id,
        text=text,
        answer_1=answer_1,
        answer_2=answer_2,
        answer_3=answer_3,
        answer_4=answer_4,
        correct_answers=correct_answers,
        explanation=explanation,
        category=category or [],
    )
    db.add(new_q)
    await db.commit()
    await db.refresh(new_q)
    return new_q


async def delete_question_db(db: AsyncSession, question_id: int) -> dict:
    """Удаление вопроса"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )
    await db.delete(q)
    await db.commit()
    return {"status": "Удалён"}


async def find_question_db(db: AsyncSession, question_id: int) -> Question:
    """Поиск вопроса по ID"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )
    return q


async def edit_question_db(
    db: AsyncSession,
    question_id: int,
    topic_id: Optional[int] = None,
    text: Optional[str] = None,
    correct_answers: Optional[int] = None,
    answer_1: Optional[str] = None,
    answer_2: Optional[str] = None,
    answer_3: Optional[str] = None,
    answer_4: Optional[str] = None,
    explanation: Optional[str] = None,
    category: Optional[List] = None,
) -> Question:
    """Редактирование вопроса"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )

    if topic_id is not None:
        # Проверяем, что новая тема существует
        topic_result = await db.execute(
            select(Topic).filter(Topic.topic_id == topic_id)
        )
        topic = topic_result.scalar_one_or_none()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
            )
        q.topic_id = topic_id
    if text is not None:
        q.text = text
    if correct_answers is not None:
        q.correct_answers = correct_answers
    if answer_1 is not None:
        q.answer_1 = answer_1
    if answer_2 is not None:
        q.answer_2 = answer_2
    if answer_3 is not None:
        q.answer_3 = answer_3
    if answer_4 is not None:
        q.answer_4 = answer_4
    if explanation is not None:
        q.explanation = explanation
    if category is not None:
        q.category = category

    await db.commit()
    await db.refresh(q)
    return q


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_questions_by_topic_db(db: AsyncSession, topic_id: int) -> List[Question]:
    """Получение всех вопросов по теме"""

    # Проверяем, что тема существует
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = topic_result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    result = await db.execute(select(Question).filter(Question.topic_id == topic_id))
    questions = result.scalars().all()

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопросы для темы {topic_id} не найдены",
        )

    return questions


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_all_questions_db(db: AsyncSession) -> List[Question]:
    """Получение всех вопросов"""

    result = await db.execute(select(Question))
    questions = result.scalars().all()
    return questions


async def get_questions_count_by_topic_db(db: AsyncSession, topic_id: int) -> int:
    """Получение количества вопросов по теме"""

    # Проверяем, что тема существует
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = topic_result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    result = await db.execute(
        select(func.count(Question.question_id)).filter(Question.topic_id == topic_id)
    )
    return result.scalar()


async def get_questions_by_category_db(
    db: AsyncSession, category: str
) -> List[Question]:
    """Получение вопросов по категории"""

    # Поиск вопросов, где category содержит указанную категорию
    result = await db.execute(
        select(Question).filter(Question.category.contains([category]))
    )
    questions = result.scalars().all()

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопросы с категорией '{category}' не найдены",
        )

    return questions


async def search_questions_by_text_db(
    db: AsyncSession, search_text: str
) -> List[Question]:
    """Поиск вопросов по тексту"""

    result = await db.execute(
        select(Question).filter(Question.text.ilike(f"%{search_text}%"))
    )
    questions = result.scalars().all()

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопросы, содержащие '{search_text}', не найдены",
        )

    return questions


async def get_questions_without_explanation_db(db: AsyncSession) -> List[Question]:
    """Получение вопросов без объяснения"""

    result = await db.execute(select(Question).filter(Question.explanation.is_(None)))
    questions = result.scalars().all()
    return questions


async def add_explanation_to_question_db(
    db: AsyncSession, question_id: int, explanation: str
) -> Question:
    """Добавление объяснения к вопросу"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )

    question.explanation = explanation
    await db.commit()
    await db.refresh(question)
    return question


async def remove_explanation_from_question_db(
    db: AsyncSession, question_id: int
) -> Question:
    """Удаление объяснения у вопроса"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )

    question.explanation = None
    await db.commit()
    await db.refresh(question)
    return question


async def update_question_category_db(
    db: AsyncSession, question_id: int, category: List
) -> Question:
    """Обновление категории вопроса"""

    result = await db.execute(
        select(Question).filter(Question.question_id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден"
        )

    question.category = category
    await db.commit()
    await db.refresh(question)
    return question

# 3. section_service
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database.models.academic import (
    Section,
    Subject,
    MaterialFile,
    Block,
    Topic,
    TopicTestMapping,
    TestType,
)
from app.services.content.topic_service import get_material_files_by_section_db

# ===========================================
# EXISTING SECTION OPERATIONS (Updated)
# ===========================================


async def add_section_db(
    db: AsyncSession, subject_id: int, name: str, order_number: Optional[int] = None
) -> Section:
    """Добавление нового раздела"""

    # Проверяем, что предмет существует
    subject_result = await db.execute(
        select(Subject).filter(Subject.subject_id == subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    new_section = Section(subject_id=subject_id, name=name, order_number=order_number)
    db.add(new_section)
    await db.commit()
    await db.refresh(new_section)
    return new_section


async def delete_section_db(db: AsyncSession, section_id: int) -> dict:
    """Удаление раздела"""

    result = await db.execute(select(Section).filter(Section.section_id == section_id))
    sec = result.scalar_one_or_none()
    if not sec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )
    await db.delete(sec)
    await db.commit()
    return {"status": "Удалён"}


async def find_section_db(db: AsyncSession, section_id: int) -> Section:
    """Поиск раздела по ID"""

    result = await db.execute(select(Section).filter(Section.section_id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )
    return section


async def edit_section_db(
    db: AsyncSession,
    section_id: int,
    subject_id: Optional[int] = None,
    name: Optional[str] = None,
    order_number: Optional[int] = None,
) -> Section:
    """Редактирование раздела"""

    result = await db.execute(select(Section).filter(Section.section_id == section_id))
    sec = result.scalar_one_or_none()
    if not sec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )

    if subject_id is not None:
        # Проверяем, что новый предмет существует
        subject_result = await db.execute(
            select(Subject).filter(Subject.subject_id == subject_id)
        )
        subject = subject_result.scalar_one_or_none()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
            )
        sec.subject_id = subject_id
    if name is not None:
        sec.name = name
    if order_number is not None:
        sec.order_number = order_number

    await db.commit()
    await db.refresh(sec)
    return sec


async def get_section_name_db(db: AsyncSession, section_id: int) -> str:
    """Получение названия раздела"""

    result = await db.execute(select(Section).filter(Section.section_id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )
    return section.name


async def count_sections_by_subject_db(db: AsyncSession, subject_id: int) -> int:
    """Подсчет количества разделов по предмету"""

    # Проверяем, что предмет существует
    subject_result = await db.execute(
        select(Subject).filter(Subject.subject_id == subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    result = await db.execute(
        select(func.count(Section.section_id)).filter(Section.subject_id == subject_id)
    )
    return result.scalar()


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_sections_by_subject_db(
    db: AsyncSession, subject_id: int
) -> List[Section]:
    """Получение всех разделов по предмету"""

    # Проверяем, что предмет существует
    subject_result = await db.execute(
        select(Subject).filter(Subject.subject_id == subject_id)
    )
    subject = subject_result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    result = await db.execute(
        select(Section)
        .filter(Section.subject_id == subject_id)
        .order_by(Section.order_number)
    )
    sections = result.scalars().all()

    if not sections:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Разделы для предмета {subject_id} не найдены",
        )

    return sections


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_all_sections_db(db: AsyncSession) -> List[Section]:
    """Получение всех разделов"""

    result = await db.execute(
        select(Section).order_by(Section.subject_id, Section.order_number)
    )
    sections = result.scalars().all()
    return sections


async def get_section_by_order_db(
    db: AsyncSession, subject_id: int, order_number: int
) -> Section:
    """Получение раздела по порядковому номеру в рамках предмета"""

    result = await db.execute(
        select(Section).filter(
            Section.subject_id == subject_id, Section.order_number == order_number
        )
    )
    section = result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Раздел с порядковым номером {order_number} для предмета {subject_id} не найден",
        )

    return section


async def get_first_section_db(db: AsyncSession, subject_id: int) -> Section:
    """Получение первого раздела предмета"""

    result = await db.execute(
        select(Section)
        .filter(Section.subject_id == subject_id)
        .order_by(Section.order_number)
        .limit(1)
    )
    section = result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Разделы для предмета {subject_id} не найдены",
        )

    return section


async def get_last_section_db(db: AsyncSession, subject_id: int) -> Section:
    """Получение последнего раздела предмета"""

    result = await db.execute(
        select(Section)
        .filter(Section.subject_id == subject_id)
        .order_by(Section.order_number.desc())
        .limit(1)
    )
    section = result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Разделы для предмета {subject_id} не найдены",
        )

    return section


async def search_sections_by_name_db(
    db: AsyncSession, search_name: str
) -> List[Section]:
    """Поиск разделов по названию"""

    result = await db.execute(
        select(Section)
        .filter(Section.name.ilike(f"%{search_name}%"))
        .order_by(Section.subject_id, Section.order_number)
    )
    sections = result.scalars().all()

    if not sections:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Разделы с названием, содержащим '{search_name}', не найдены",
        )

    return sections


async def update_section_order_db(
    db: AsyncSession, section_id: int, new_order: int
) -> Section:
    """Обновление порядкового номера раздела"""

    result = await db.execute(select(Section).filter(Section.section_id == section_id))
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )

    section.order_number = new_order
    await db.commit()
    await db.refresh(section)
    return section


async def get_section_with_materials_db(db: AsyncSession, section_id: int) -> dict:
    """Получение раздела с материалами и темами"""

    result = await db.execute(
        select(Section)
        .options(selectinload(Section.material_files))
        .filter(Section.section_id == section_id)
    )
    section = result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )

    # Получаем файлы материалов
    material_files = await get_material_files_by_section_db(section_id)

    # Получаем темы через блоки
    blocks_result = await db.execute(
        select(Block).filter(Block.section_id == section_id)
    )
    blocks = blocks_result.scalars().all()
    topics = []

    for block in blocks:
        block_topics_result = await db.execute(
            select(Topic)
            .filter(Topic.block_id == block.block_id)
            .order_by(Topic.number)
        )
        block_topics = block_topics_result.scalars().all()

        for topic in block_topics:
            # Получаем test_id для темы
            test_mapping_result = await db.execute(
                select(TopicTestMapping).filter(
                    TopicTestMapping.topic_id == topic.topic_id,
                    TopicTestMapping.test_type == TestType.TRAINING,
                )
            )
            test_mapping = test_mapping_result.scalar_one_or_none()
            test_id = test_mapping.test_id if test_mapping else topic.topic_id + 100

            topics.append(
                {
                    "id": topic.topic_id,
                    "title": topic.name,
                    "homework": topic.homework.split("\n") if topic.homework else [],
                    "videoUrl": topic.video_url
                    or "https://www.youtube.com/embed/dQw4w9WgXcQ",
                    "testId": test_id,
                    "block_name": block.name,
                }
            )

    return {
        "id": section.section_id,
        "name": (
            f"Модуль {section.order_number}" if section.order_number else section.name
        ),
        "books": [
            {
                "id": file.file_id,
                "title": file.title,
                "author": file.author,
                "size": file.file_size,
                "format": file.file_format,
                "download_url": file.download_url,
            }
            for file in material_files["books"]
        ],
        "testBooks": [
            {
                "id": file.file_id,
                "title": file.title,
                "author": file.author,
                "size": file.file_size,
                "format": file.file_format,
                "download_url": file.download_url,
            }
            for file in material_files["test_books"]
        ],
        "topics": topics,
    }


async def search_materials_db(
    db: AsyncSession,
    query: str,
    subject_filter: Optional[str] = None,
    section_filter: Optional[int] = None,
) -> List[dict]:
    """Поиск по материалам"""

    results = []

    # Поиск по темам
    topic_query = select(Topic).join(Block).join(Section).join(Subject)

    if subject_filter:
        topic_query = topic_query.filter(Subject.name.ilike(f"%{subject_filter}%"))
    if section_filter:
        topic_query = topic_query.filter(Section.section_id == section_filter)

    topic_query = topic_query.filter(Topic.name.ilike(f"%{query}%"))
    topics_result = await db.execute(topic_query)
    topics = topics_result.scalars().all()

    for topic in topics:
        results.append(
            {
                "type": "topic",
                "id": topic.topic_id,
                "title": topic.name,
                "description": (
                    topic.homework[:100] + "..."
                    if topic.homework and len(topic.homework) > 100
                    else topic.homework
                ),
                "subject_name": topic.block.section.subject.name,
                "section_name": topic.block.section.name,
            }
        )

    # Поиск по разделам
    section_query = select(Section).join(Subject)

    if subject_filter:
        section_query = section_query.filter(Subject.name.ilike(f"%{subject_filter}%"))

    section_query = section_query.filter(Section.name.ilike(f"%{query}%"))
    sections_result = await db.execute(section_query)
    sections = sections_result.scalars().all()

    for section in sections:
        results.append(
            {
                "type": "section",
                "id": section.section_id,
                "title": section.name,
                "description": section.description,
                "subject_name": section.subject.name,
                "section_name": section.name,
            }
        )

    # Поиск по файлам материалов
    file_query = select(MaterialFile).join(Section).join(Subject)

    if subject_filter:
        file_query = file_query.filter(Subject.name.ilike(f"%{subject_filter}%"))
    if section_filter:
        file_query = file_query.filter(Section.section_id == section_filter)

    file_query = file_query.filter(
        or_(
            MaterialFile.title.ilike(f"%{query}%"),
            MaterialFile.author.ilike(f"%{query}%"),
        )
    )
    files_result = await db.execute(file_query)
    files = files_result.scalars().all()

    for file in files:
        results.append(
            {
                "type": "file",
                "id": file.file_id,
                "title": file.title,
                "description": f"Автор: {file.author}, Размер: {file.file_size}",
                "subject_name": file.section.subject.name,
                "section_name": file.section.name,
            }
        )

    return results


async def get_materials_statistics_db(db: AsyncSession) -> dict:
    """Получение статистики материалов"""

    total_subjects_result = await db.execute(select(func.count(Subject.subject_id)))
    total_subjects = total_subjects_result.scalar()

    total_sections_result = await db.execute(select(func.count(Section.section_id)))
    total_sections = total_sections_result.scalar()

    total_topics_result = await db.execute(select(func.count(Topic.topic_id)))
    total_topics = total_topics_result.scalar()

    total_files_result = await db.execute(select(func.count(MaterialFile.file_id)))
    total_files = total_files_result.scalar()

    # Статистика по предметам
    subjects_breakdown = {}
    subjects_result = await db.execute(select(Subject))
    subjects = subjects_result.scalars().all()

    for subject in subjects:
        sections_count_result = await db.execute(
            select(func.count(Section.section_id)).filter(
                Section.subject_id == subject.subject_id
            )
        )
        sections_count = sections_count_result.scalar()
        subjects_breakdown[subject.name] = sections_count

    return {
        "total_subjects": total_subjects,
        "total_sections": total_sections,
        "total_topics": total_topics,
        "total_files": total_files,
        "subjects_breakdown": subjects_breakdown,
    }

# 4. subject_service
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models.academic import Subject, Section, Topic, MaterialFile
from app.services.content.section_service import get_section_with_materials_db

# ===========================================
# EXISTING SUBJECT OPERATIONS (Updated)
# ===========================================


async def add_subject_db(
    db: AsyncSession, name: str, description: Optional[str] = None
) -> Subject:
    """Добавление нового предмета"""

    # Проверяем, что предмет с таким названием не существует
    existing_subject_result = await db.execute(
        select(Subject).filter(Subject.name == name)
    )
    existing_subject = existing_subject_result.scalar_one_or_none()
    if existing_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Предмет с названием '{name}' уже существует",
        )

    new_subject = Subject(name=name, description=description)
    db.add(new_subject)
    await db.commit()
    await db.refresh(new_subject)
    return new_subject


async def delete_subject_db(db: AsyncSession, subject_id: int) -> dict:
    """Удаление предмета"""

    result = await db.execute(select(Subject).filter(Subject.subject_id == subject_id))
    subj = result.scalar_one_or_none()
    if not subj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )
    await db.delete(subj)
    await db.commit()
    return {"status": "Удалён"}


async def find_subject_db(db: AsyncSession, subject_id: int) -> Subject:
    """Поиск предмета по ID"""

    result = await db.execute(select(Subject).filter(Subject.subject_id == subject_id))
    subj = result.scalar_one_or_none()
    if not subj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )
    return subj


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_all_subjects_db(db: AsyncSession) -> List[Subject]:
    """Получение всех предметов"""

    result = await db.execute(select(Subject))
    subjects = result.scalars().all()
    return subjects


async def edit_subject_db(
    db: AsyncSession,
    subject_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Subject:
    """Редактирование предмета"""

    result = await db.execute(select(Subject).filter(Subject.subject_id == subject_id))
    subj = result.scalar_one_or_none()
    if not subj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    # Проверяем уникальность названия, если оно изменяется
    if name is not None and name != subj.name:
        existing_subject_result = await db.execute(
            select(Subject).filter(Subject.name == name)
        )
        existing_subject = existing_subject_result.scalar_one_or_none()
        if existing_subject:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Предмет с названием '{name}' уже существует",
            )
        subj.name = name

    if description is not None:
        subj.description = description

    await db.commit()
    await db.refresh(subj)
    return subj


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_subject_by_name_db(db: AsyncSession, name: str) -> Subject:
    """Получение предмета по названию"""

    result = await db.execute(select(Subject).filter(Subject.name == name))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Предмет с названием '{name}' не найден",
        )
    return subject


async def search_subjects_by_name_db(
    db: AsyncSession, search_name: str
) -> List[Subject]:
    """Поиск предметов по названию"""

    result = await db.execute(
        select(Subject).filter(Subject.name.ilike(f"%{search_name}%"))
    )
    subjects = result.scalars().all()

    if not subjects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Предметы с названием, содержащим '{search_name}', не найдены",
        )

    return subjects


async def get_subjects_count_db(db: AsyncSession) -> int:
    """Получение количества предметов"""

    result = await db.execute(select(func.count(Subject.subject_id)))
    return result.scalar()


async def get_subjects_with_sections_db(db: AsyncSession) -> List[Subject]:
    """Получение предметов, у которых есть разделы"""

    result = await db.execute(select(Subject).filter(Subject.sections.any()))
    subjects = result.scalars().all()
    return subjects


async def get_subjects_without_sections_db(db: AsyncSession) -> List[Subject]:
    """Получение предметов без разделов"""

    result = await db.execute(select(Subject).filter(~Subject.sections.any()))
    subjects = result.scalars().all()
    return subjects


async def update_subject_description_db(
    db: AsyncSession, subject_id: int, description: str
) -> Subject:
    """Обновление описания предмета"""

    result = await db.execute(select(Subject).filter(Subject.subject_id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    subject.description = description
    await db.commit()
    await db.refresh(subject)
    return subject


async def remove_subject_description_db(db: AsyncSession, subject_id: int) -> Subject:
    """Удаление описания предмета"""

    result = await db.execute(select(Subject).filter(Subject.subject_id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден"
        )

    subject.description = None
    await db.commit()
    await db.refresh(subject)
    return subject


async def get_subject_materials_db(db: AsyncSession, subject_name: str) -> dict:
    """Получение всех материалов предмета"""

    # Ищем предмет
    result = await db.execute(
        select(Subject).filter(Subject.name.ilike(f"%{subject_name}%"))
    )
    subject = result.scalar_one_or_none()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Предмет '{subject_name}' не найден",
        )

    # Получаем все разделы предмета
    sections_result = await db.execute(
        select(Section)
        .filter(Section.subject_id == subject.subject_id)
        .order_by(Section.order_number)
    )
    sections = sections_result.scalars().all()

    modules = []
    for section in sections:
        try:
            section_data = await get_section_with_materials_db(db, section.section_id)
            modules.append(section_data)
        except HTTPException:
            # Если не удается получить данные раздела, пропускаем
            continue

    return {"modules": modules}  # Используем "modules" для совместимости с фронтендом


async def get_materials_statistics_db(db: AsyncSession) -> dict:
    """Получение статистики материалов"""

    total_subjects_result = await db.execute(select(func.count(Subject.subject_id)))
    total_subjects = total_subjects_result.scalar()

    total_sections_result = await db.execute(select(func.count(Section.section_id)))
    total_sections = total_sections_result.scalar()

    total_topics_result = await db.execute(select(func.count(Topic.topic_id)))
    total_topics = total_topics_result.scalar()

    total_files_result = await db.execute(select(func.count(MaterialFile.file_id)))
    total_files = total_files_result.scalar()

    # Статистика по предметам
    subjects_breakdown = {}
    subjects_result = await db.execute(select(Subject))
    subjects = subjects_result.scalars().all()

    for subject in subjects:
        sections_count_result = await db.execute(
            select(func.count(Section.section_id)).filter(
                Section.subject_id == subject.subject_id
            )
        )
        sections_count = sections_count_result.scalar()
        subjects_breakdown[subject.name] = sections_count

    return {
        "total_subjects": total_subjects,
        "total_sections": total_sections,
        "total_topics": total_topics,
        "total_files": total_files,
        "subjects_breakdown": subjects_breakdown,
    }

# 5. test_service
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from app.database.models.assessment import Question
from app.database.models.academic import Topic, Block, Section, Subject, Moduls

# ===========================================
# EXISTING TEST FUNCTIONS (from test_service)
# ===========================================


async def get_random_questions_by_topic_db(
    db: AsyncSession, topic_id: int, limit: int = 30
) -> List[Question]:
    """Получить случайные вопросы по определенной теме"""

    result = await db.execute(
        select(Question)
        .filter(Question.topic_id == topic_id)
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_random_questions_by_block_db(
    db: AsyncSession, block_id: int, limit: int = 30
) -> List[Question]:
    """Получить случайные вопросы по определенному блоку"""

    result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .filter(Topic.block_id == block_id)
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_random_questions_by_modul_db(
    db: AsyncSession, modul_id: int, limit_per_subject: int = 30
) -> Dict[str, List[Question]]:
    """Получить случайные вопросы по модулю (по 30 на химию и биологию)"""

    # Получаем информацию о модуле
    modul_result = await db.execute(select(Moduls).filter(Moduls.modul_id == modul_id))
    modul = modul_result.scalar_one_or_none()
    if not modul:
        return {"chemistry": [], "biology": []}

    # Получаем вопросы по химии
    chemistry_result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .join(Subject, Section.subject_id == Subject.subject_id)
        .filter(
            Subject.name.ilike("%химия%"),
            Topic.topic_id >= modul.start_topic_chem,
            Topic.topic_id <= modul.end_topic_chem,
        )
        .order_by(func.random())
        .limit(limit_per_subject)
    )
    chemistry_questions = chemistry_result.scalars().all()

    # Получаем вопросы по биологии
    biology_result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .join(Subject, Section.subject_id == Subject.subject_id)
        .filter(
            Subject.name.ilike("%биология%"),
            Topic.topic_id >= modul.start_topic_bio,
            Topic.topic_id <= modul.end_topic_bio,
        )
        .order_by(func.random())
        .limit(limit_per_subject)
    )
    biology_questions = biology_result.scalars().all()

    return {"chemistry": chemistry_questions, "biology": biology_questions}


async def get_random_questions_by_section_db(
    db: AsyncSession, section_id: int, limit: int = 30
) -> List[Question]:
    """Получить случайные вопросы по определенному разделу"""

    result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .filter(Block.section_id == section_id)
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_random_questions_by_subject_db(
    db: AsyncSession, subject_id: int, limit: int = 30
) -> List[Question]:
    """Получить случайные вопросы по определенному предмету"""

    result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .filter(Section.subject_id == subject_id)
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_questions_count_by_topic_db(db: AsyncSession, topic_id: int) -> int:
    """Получить количество вопросов по теме"""

    result = await db.execute(
        select(func.count(Question.question_id)).filter(Question.topic_id == topic_id)
    )
    count = result.scalar()
    return count


async def get_questions_count_by_block_db(db: AsyncSession, block_id: int) -> int:
    """Получить количество вопросов по блоку"""

    result = await db.execute(
        select(func.count(Question.question_id))
        .join(Topic, Question.topic_id == Topic.topic_id)
        .filter(Topic.block_id == block_id)
    )
    count = result.scalar()
    return count


async def get_questions_count_by_section_db(db: AsyncSession, section_id: int) -> int:
    """Получить количество вопросов по разделу"""

    result = await db.execute(
        select(func.count(Question.question_id))
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .filter(Block.section_id == section_id)
    )
    count = result.scalar()
    return count


async def get_questions_count_by_subject_db(db: AsyncSession, subject_id: int) -> int:
    """Получить количество вопросов по предмету"""

    result = await db.execute(
        select(func.count(Question.question_id))
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .filter(Section.subject_id == subject_id)
    )
    count = result.scalar()
    return count


# ===========================================
# ADDITIONAL HELPER FUNCTIONS
# ===========================================


async def get_questions_by_difficulty_db(
    db: AsyncSession, difficulty_level: str, limit: int = 30
) -> List[Question]:
    """Получить вопросы по уровню сложности (через категории)"""

    result = await db.execute(
        select(Question)
        .filter(Question.category.contains([difficulty_level]))
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_questions_statistics_db(db: AsyncSession) -> Dict[str, int]:
    """Получить статистику вопросов"""

    total_questions_result = await db.execute(select(func.count(Question.question_id)))
    total_questions = total_questions_result.scalar()

    questions_with_explanation_result = await db.execute(
        select(func.count(Question.question_id)).filter(
            Question.explanation.isnot(None)
        )
    )
    questions_with_explanation = questions_with_explanation_result.scalar()

    questions_without_explanation = total_questions - questions_with_explanation

    return {
        "total_questions": total_questions,
        "questions_with_explanation": questions_with_explanation,
        "questions_without_explanation": questions_without_explanation,
    }


async def get_questions_by_multiple_topics_db(
    db: AsyncSession, topic_ids: List[int], limit: int = 30
) -> List[Question]:
    """Получить случайные вопросы по нескольким темам"""

    result = await db.execute(
        select(Question)
        .filter(Question.topic_id.in_(topic_ids))
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_questions_by_category_and_topic_db(
    db: AsyncSession, topic_id: int, category: str, limit: int = 30
) -> List[Question]:
    """Получить вопросы по теме и категории"""

    result = await db.execute(
        select(Question)
        .filter(Question.topic_id == topic_id, Question.category.contains([category]))
        .order_by(func.random())
        .limit(limit)
    )
    questions = result.scalars().all()
    return questions


async def get_mixed_questions_db(
    db: AsyncSession, chemistry_count: int = 15, biology_count: int = 15
) -> Dict[str, List[Question]]:
    """Получить смешанные вопросы по химии и биологии"""

    # Получаем вопросы по химии
    chemistry_result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .join(Subject, Section.subject_id == Subject.subject_id)
        .filter(Subject.name.ilike("%химия%"))
        .order_by(func.random())
        .limit(chemistry_count)
    )
    chemistry_questions = chemistry_result.scalars().all()

    # Получаем вопросы по биологии
    biology_result = await db.execute(
        select(Question)
        .join(Topic, Question.topic_id == Topic.topic_id)
        .join(Block, Topic.block_id == Block.block_id)
        .join(Section, Block.section_id == Section.section_id)
        .join(Subject, Section.subject_id == Subject.subject_id)
        .filter(Subject.name.ilike("%биология%"))
        .order_by(func.random())
        .limit(biology_count)
    )
    biology_questions = biology_result.scalars().all()

    return {
        "chemistry": chemistry_questions,
        "biology": biology_questions,
        "mixed": chemistry_questions + biology_questions,
    }


async def validate_test_parameters_db(
    db: AsyncSession,
    topic_id: int = None,
    block_id: int = None,
    section_id: int = None,
    subject_id: int = None,
    modul_id: int = None,
) -> Dict[str, bool]:
    """Проверить корректность параметров для создания теста"""

    result = {}

    if topic_id:
        topic_result = await db.execute(
            select(Topic).filter(Topic.topic_id == topic_id)
        )
        result["topic_exists"] = topic_result.scalar_one_or_none() is not None

    if block_id:
        block_result = await db.execute(
            select(Block).filter(Block.block_id == block_id)
        )
        result["block_exists"] = block_result.scalar_one_or_none() is not None

    if section_id:
        section_result = await db.execute(
            select(Section).filter(Section.section_id == section_id)
        )
        result["section_exists"] = section_result.scalar_one_or_none() is not None

    if subject_id:
        subject_result = await db.execute(
            select(Subject).filter(Subject.subject_id == subject_id)
        )
        result["subject_exists"] = subject_result.scalar_one_or_none() is not None

    if modul_id:
        modul_result = await db.execute(
            select(Moduls).filter(Moduls.modul_id == modul_id)
        )
        result["modul_exists"] = modul_result.scalar_one_or_none() is not None

    return result

# 6. topic_service
from typing import List, Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.academic import (
    Topic,
    Block,
    SectionMaterial,
    MaterialFileType,
    MaterialFile,
    TestType,
    Section,
    TopicTestMapping,
    Subject,
)

# ===========================================
# EXISTING TOPIC OPERATIONS (Updated)
# ===========================================


async def add_topic_db(
    db: AsyncSession,
    block_id: int,
    name: str,
    homework: Optional[str] = None,
    number: Optional[int] = None,
    additional_material: Optional[str] = None,
) -> Topic:
    """Добавление новой темы"""
    # Проверяем, что блок существует
    block_result = await db.execute(select(Block).filter(Block.block_id == block_id))
    block = block_result.scalar_one_or_none()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Блок не найден"
        )

    new_topic = Topic(
        block_id=block_id,
        name=name,
        homework=homework,
        number=number,
        additional_material=additional_material,
    )
    db.add(new_topic)
    await db.commit()
    await db.refresh(new_topic)
    return new_topic


async def delete_topic_db(db: AsyncSession, topic_id: int) -> dict:
    """Удаление темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    top = result.scalar_one_or_none()
    if not top:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    await db.delete(top)
    await db.commit()
    return {"status": "Удалена"}


async def find_topic_db(db: AsyncSession, topic_id: int) -> Topic:
    """Поиск темы по ID"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    top = result.scalar_one_or_none()
    if not top:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    return top


async def edit_topic_db(
    db: AsyncSession,
    topic_id: int,
    block_id: Optional[int] = None,
    name: Optional[str] = None,
    homework: Optional[str] = None,
    number: Optional[int] = None,
    additional_material: Optional[str] = None,
) -> Topic:
    """Редактирование темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    top = result.scalar_one_or_none()
    if not top:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    if block_id is not None:
        # Проверяем, что новый блок существует
        block_result = await db.execute(
            select(Block).filter(Block.block_id == block_id)
        )
        block = block_result.scalar_one_or_none()
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Блок не найден"
            )
        top.block_id = block_id
    if name is not None:
        top.name = name
    if homework is not None:
        top.homework = homework
    if number is not None:
        top.number = number
    if additional_material is not None:
        top.additional_material = additional_material

    await db.commit()
    await db.refresh(top)
    return top


# ===========================================
# HOMEWORK OPERATIONS
# ===========================================


async def add_homework_db(db: AsyncSession, topic_id: int, homework: str) -> Topic:
    """Добавление домашнего задания к теме"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.homework = homework
    await db.commit()
    await db.refresh(topic)
    return topic


async def delete_homework_db(db: AsyncSession, topic_id: int) -> Topic:
    """Удаление домашнего задания у темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.homework = None
    await db.commit()
    await db.refresh(topic)
    return topic


async def edit_homework_db(db: AsyncSession, topic_id: int, homework: str) -> Topic:
    """Редактирование домашнего задания"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.homework = homework
    await db.commit()
    await db.refresh(topic)
    return topic


# ===========================================
# TOPIC NUMBER OPERATIONS
# ===========================================


async def add_topic_number_db(db: AsyncSession, topic_id: int, number: int) -> Topic:
    """Добавление номера к теме"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.number = number
    await db.commit()
    await db.refresh(topic)
    return topic


async def delete_topic_number_db(db: AsyncSession, topic_id: int) -> Topic:
    """Удаление номера у темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.number = None
    await db.commit()
    await db.refresh(topic)
    return topic


async def edit_topic_number_db(db: AsyncSession, topic_id: int, number: int) -> Topic:
    """Редактирование номера темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.number = number
    await db.commit()
    await db.refresh(topic)
    return topic


# ===========================================
# ADDITIONAL MATERIAL OPERATIONS
# ===========================================


async def add_additional_material_db(
    db: AsyncSession, topic_id: int, additional_material: str
) -> Topic:
    """Добавление дополнительного материала к теме"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.additional_material = additional_material
    await db.commit()
    await db.refresh(topic)
    return topic


async def delete_additional_material_db(db: AsyncSession, topic_id: int) -> Topic:
    """Удаление дополнительного материала у темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.additional_material = None
    await db.commit()
    await db.refresh(topic)
    return topic


async def edit_additional_material_db(
    db: AsyncSession, topic_id: int, additional_material: str
) -> Topic:
    """Редактирование дополнительного материала"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )
    topic.additional_material = additional_material
    await db.commit()
    await db.refresh(topic)
    return topic


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_topics_by_block_db(db: AsyncSession, block_id: int) -> List[Topic]:
    """Получение всех тем по блоку"""

    # Проверяем, что блок существует
    block_result = await db.execute(select(Block).filter(Block.block_id == block_id))
    block = block_result.scalar_one_or_none()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Блок не найден"
        )

    result = await db.execute(
        select(Topic).filter(Topic.block_id == block_id).order_by(Topic.number)
    )
    topics = result.scalars().all()

    if not topics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Темы для блока {block_id} не найдены",
        )

    return topics


async def get_topic_materials_db(db: AsyncSession, topic_id: int) -> dict:
    """Получение всех материалов по теме"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    # Получаем материалы раздела, к которому относится тема
    section_materials_result = await db.execute(
        select(SectionMaterial).filter(
            SectionMaterial.section_id == topic.block.section_id
        )
    )
    section_materials = section_materials_result.scalars().all()

    return {
        "topic_id": topic_id,
        "topic_name": topic.name,
        "homework": topic.homework,
        "additional_material": topic.additional_material,
        "section_materials": [
            {
                "section_material_id": material.section_material_id,
                "material_links": material.material_links,
            }
            for material in section_materials
        ],
    }


async def get_next_topic_db(db: AsyncSession, current_topic_id: int) -> Optional[Topic]:
    """Получение следующей темы"""

    current_topic_result = await db.execute(
        select(Topic).filter(Topic.topic_id == current_topic_id)
    )
    current_topic = current_topic_result.scalar_one_or_none()
    if not current_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Текущая тема не найдена"
        )

    # Ищем следующую тему в том же блоке
    if current_topic.number is not None:
        next_topic_result = await db.execute(
            select(Topic)
            .filter(
                Topic.block_id == current_topic.block_id,
                Topic.number > current_topic.number,
            )
            .order_by(Topic.number)
            .limit(1)
        )
        next_topic = next_topic_result.scalar_one_or_none()
    else:
        # Если у текущей темы нет номера, ищем по topic_id
        next_topic_result = await db.execute(
            select(Topic)
            .filter(
                Topic.block_id == current_topic.block_id,
                Topic.topic_id > current_topic.topic_id,
            )
            .order_by(Topic.topic_id)
            .limit(1)
        )
        next_topic = next_topic_result.scalar_one_or_none()

    return next_topic


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_all_topics_db(db: AsyncSession) -> List[Topic]:
    """Получение всех тем"""

    result = await db.execute(select(Topic).order_by(Topic.block_id, Topic.number))
    topics = result.scalars().all()
    return topics


async def get_topics_with_homework_db(db: AsyncSession) -> List[Topic]:
    """Получение тем с домашними заданиями"""

    result = await db.execute(select(Topic).filter(Topic.homework.isnot(None)))
    topics = result.scalars().all()
    return topics


async def get_topics_without_homework_db(db: AsyncSession) -> List[Topic]:
    """Получение тем без домашних заданий"""

    result = await db.execute(select(Topic).filter(Topic.homework.is_(None)))
    topics = result.scalars().all()
    return topics


async def get_previous_topic_db(
    db: AsyncSession, current_topic_id: int
) -> Optional[Topic]:
    """Получение предыдущей темы"""

    current_topic_result = await db.execute(
        select(Topic).filter(Topic.topic_id == current_topic_id)
    )
    current_topic = current_topic_result.scalar_one_or_none()
    if not current_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Текущая тема не найдена"
        )

    # Ищем предыдущую тему в том же блоке
    if current_topic.number is not None:
        prev_topic_result = await db.execute(
            select(Topic)
            .filter(
                Topic.block_id == current_topic.block_id,
                Topic.number < current_topic.number,
            )
            .order_by(Topic.number.desc())
            .limit(1)
        )
        prev_topic = prev_topic_result.scalar_one_or_none()
    else:
        # Если у текущей темы нет номера, ищем по topic_id
        prev_topic_result = await db.execute(
            select(Topic)
            .filter(
                Topic.block_id == current_topic.block_id,
                Topic.topic_id < current_topic.topic_id,
            )
            .order_by(Topic.topic_id.desc())
            .limit(1)
        )
        prev_topic = prev_topic_result.scalar_one_or_none()

    return prev_topic


async def get_first_topic_in_block_db(
    db: AsyncSession, block_id: int
) -> Optional[Topic]:
    """Получение первой темы в блоке"""

    result = await db.execute(
        select(Topic).filter(Topic.block_id == block_id).order_by(Topic.number).limit(1)
    )
    topic = result.scalar_one_or_none()
    return topic


async def get_last_topic_in_block_db(
    db: AsyncSession, block_id: int
) -> Optional[Topic]:
    """Получение последней темы в блоке"""

    result = await db.execute(
        select(Topic)
        .filter(Topic.block_id == block_id)
        .order_by(Topic.number.desc())
        .limit(1)
    )
    topic = result.scalar_one_or_none()
    return topic


async def search_topics_by_name_db(db: AsyncSession, search_name: str) -> List[Topic]:
    """Поиск тем по названию"""

    result = await db.execute(
        select(Topic)
        .filter(Topic.name.ilike(f"%{search_name}%"))
        .order_by(Topic.block_id, Topic.number)
    )
    topics = result.scalars().all()

    if not topics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Темы с названием, содержащим '{search_name}', не найдены",
        )

    return topics


async def get_topics_count_by_block_db(db: AsyncSession, block_id: int) -> int:
    """Получение количества тем в блоке"""

    result = await db.execute(
        select(func.count(Topic.topic_id)).filter(Topic.block_id == block_id)
    )
    return result.scalar()


async def add_material_file_db(
    db: AsyncSession,
    section_id: int,
    file_type: MaterialFileType,
    title: str,
    author: str,
    file_size: str,
    file_format: str = "PDF",
    download_url: Optional[str] = None,
) -> MaterialFile:
    """Добавление файла материала к разделу"""

    # Проверяем существование раздела
    section_result = await db.execute(
        select(Section).filter(Section.section_id == section_id)
    )
    section = section_result.scalar_one_or_none()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Раздел не найден"
        )

    material_file = MaterialFile(
        section_id=section_id,
        file_type=file_type,
        title=title,
        author=author,
        file_size=file_size,
        file_format=file_format,
        download_url=download_url,
    )

    db.add(material_file)
    await db.commit()
    await db.refresh(material_file)
    return material_file


async def get_material_files_by_section_db(
    db: AsyncSession, section_id: int
) -> Dict[str, List[MaterialFile]]:
    """Получение всех файлов материалов раздела, сгруппированных по типу"""
    result = await db.execute(
        select(MaterialFile).filter(MaterialFile.section_id == section_id)
    )
    files = result.scalars().all()

    result_dict = {"books": [], "test_books": []}

    for file in files:
        if file.file_type == MaterialFileType.BOOK:
            result_dict["books"].append(file)
        elif file.file_type == MaterialFileType.TEST_BOOK:
            result_dict["test_books"].append(file)

    return result_dict


async def update_material_file_db(
    db: AsyncSession,
    file_id: int,
    title: Optional[str] = None,
    author: Optional[str] = None,
    file_size: Optional[str] = None,
    file_format: Optional[str] = None,
    download_url: Optional[str] = None,
) -> MaterialFile:
    """Обновление файла материала"""

    result = await db.execute(
        select(MaterialFile).filter(MaterialFile.file_id == file_id)
    )
    material_file = result.scalar_one_or_none()
    if not material_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Файл материала не найден"
        )

    if title is not None:
        material_file.title = title
    if author is not None:
        material_file.author = author
    if file_size is not None:
        material_file.file_size = file_size
    if file_format is not None:
        material_file.file_format = file_format
    if download_url is not None:
        material_file.download_url = download_url

    await db.commit()
    await db.refresh(material_file)
    return material_file


async def delete_material_file_db(db: AsyncSession, file_id: int) -> dict:
    """Удаление файла материала"""

    result = await db.execute(
        select(MaterialFile).filter(MaterialFile.file_id == file_id)
    )
    material_file = result.scalar_one_or_none()
    if not material_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Файл материала не найден"
        )

    await db.delete(material_file)
    await db.commit()
    return {"status": "Удален"}


async def add_topic_test_mapping_db(
    db: AsyncSession,
    topic_id: int,
    test_id: int,
    test_type: TestType = TestType.TRAINING,
) -> TopicTestMapping:
    """Создание связи темы с тестом"""

    # Проверяем существование темы
    topic_result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = topic_result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    # Проверяем, не существует ли уже такая связь
    existing_result = await db.execute(
        select(TopicTestMapping).filter(
            TopicTestMapping.topic_id == topic_id, TopicTestMapping.test_id == test_id
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Связь темы с тестом уже существует",
        )

    mapping = TopicTestMapping(topic_id=topic_id, test_id=test_id, test_type=test_type)

    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    return mapping


async def get_topic_tests_db(db: AsyncSession, topic_id: int) -> List[TopicTestMapping]:
    """Получение всех тестов для темы"""

    result = await db.execute(
        select(TopicTestMapping).filter(TopicTestMapping.topic_id == topic_id)
    )
    return result.scalars().all()


async def get_test_id_for_topic_db(
    db: AsyncSession, topic_id: int, test_type: TestType = TestType.TRAINING
) -> Optional[int]:
    """Получение ID теста для темы"""

    result = await db.execute(
        select(TopicTestMapping).filter(
            TopicTestMapping.topic_id == topic_id,
            TopicTestMapping.test_type == test_type,
        )
    )
    mapping = result.scalar_one_or_none()
    return mapping.test_id if mapping else None


async def update_topic_video_url_db(
    db: AsyncSession, topic_id: int, video_url: str
) -> Topic:
    """Обновление URL видео для темы"""

    result = await db.execute(select(Topic).filter(Topic.topic_id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    topic.video_url = video_url
    await db.commit()
    await db.refresh(topic)
    return topic


async def get_topic_with_details_db(db: AsyncSession, topic_id: int) -> dict:
    """Получение темы с полной детализацией"""

    # Используем представление для получения данных
    from app.database.models.academic import TopicDetailsView

    result = await db.execute(
        select(TopicDetailsView).filter(TopicDetailsView.topic_id == topic_id)
    )
    topic_view = result.scalar_one_or_none()
    if not topic_view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена"
        )

    # Получаем тесты для темы
    tests = await get_topic_tests_db(db, topic_id)

    return {
        "topic_id": topic_view.topic_id,
        "title": topic_view.topic_name,
        "homework": topic_view.homework.split("\n") if topic_view.homework else [],
        "number": topic_view.topic_number,
        "additional_material": topic_view.additional_material,
        "video_url": topic_view.video_url
        or "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "block_name": topic_view.block_name,
        "section_name": topic_view.section_name,
        "section_id": topic_view.section_id,
        "subject_name": topic_view.subject_name,
        "subject_id": topic_view.subject_id,
        "questions_count": topic_view.questions_count or 0,
        "tests_count": topic_view.tests_count or 0,
        "test_id": tests[0].test_id if tests else topic_view.topic_id + 100,
        "tests": [
            {"test_id": test.test_id, "test_type": test.test_type.value}
            for test in tests
        ],
    }


async def search_materials_db(
    db: AsyncSession,
    query: str,
    subject_filter: Optional[str] = None,
    section_filter: Optional[int] = None,
) -> List[dict]:
    """Поиск по материалам"""

    results = []

    # Поиск по темам
    topic_query = select(Topic).join(Block).join(Section).join(Subject)

    if subject_filter:
        topic_query = topic_query.filter(Subject.name.ilike(f"%{subject_filter}%"))
    if section_filter:
        topic_query = topic_query.filter(Section.section_id == section_filter)

    topic_query = topic_query.filter(Topic.name.ilike(f"%{query}%"))
    topics_result = await db.execute(topic_query)
    topics = topics_result.scalars().all()

    for topic in topics:
        results.append(
            {
                "type": "topic",
                "id": topic.topic_id,
                "title": topic.name,
                "description": (
                    topic.homework[:100] + "..."
                    if topic.homework and len(topic.homework) > 100
                    else topic.homework
                ),
                "subject_name": topic.block.section.subject.name,
                "section_name": topic.block.section.name,
            }
        )

    # Поиск по разделам
    section_query = select(Section).join(Subject)

    if subject_filter:
        section_query = section_query.filter(Subject.name.ilike(f"%{subject_filter}%"))

    section_query = section_query.filter(Section.name.ilike(f"%{query}%"))
    sections_result = await db.execute(section_query)
    sections = sections_result.scalars().all()

    for section in sections:
        results.append(
            {
                "type": "section",
                "id": section.section_id,
                "title": section.name,
                "description": section.description,
                "subject_name": section.subject.name,
                "section_name": section.name,
            }
        )

    # Поиск по файлам материалов
    file_query = select(MaterialFile).join(Section).join(Subject)

    if subject_filter:
        file_query = file_query.filter(Subject.name.ilike(f"%{subject_filter}%"))
    if section_filter:
        file_query = file_query.filter(Section.section_id == section_filter)

    file_query = file_query.filter(
        or_(
            MaterialFile.title.ilike(f"%{query}%"),
            MaterialFile.author.ilike(f"%{query}%"),
        )
    )
    files_result = await db.execute(file_query)
    files = files_result.scalars().all()

    for file in files:
        results.append(
            {
                "type": "file",
                "id": file.file_id,
                "title": file.title,
                "description": f"Автор: {file.author}, Размер: {file.file_size}",
                "subject_name": file.section.subject.name,
                "section_name": file.section.name,
            }
        )

    return results
