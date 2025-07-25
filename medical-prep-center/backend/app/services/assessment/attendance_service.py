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
