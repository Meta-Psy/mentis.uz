from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from app.database import get_db
from app.database.models.assessment import Attendance, AttendanceType
from app.database.models.user import Student

# -----------------------
# ADD ATTENDANCE
# -----------------------
def add_attendance_db(student_id: int, lesson_date_time: datetime, att_status: AttendanceType,
                     subject_id: int, topic_id: int, excuse_reason: Optional[str] = None,
                     extra_lesson: Optional[str] = None) -> Attendance:
    """Добавление записи о посещаемости"""
    with next(get_db()) as db:
        new_att = Attendance(
            student_id=student_id, 
            lesson_date_time=lesson_date_time,
            att_status=att_status,
            subject_id=subject_id, 
            topic_id=topic_id,
            excuse_reason=excuse_reason,
            extra_lesson=extra_lesson
        )
        db.add(new_att)
        db.commit()
        db.refresh(new_att)
        return new_att

# -----------------------
# DELETE ATTENDANCE
# -----------------------
def delete_attendance_db(attendance_id: int) -> dict:
    """Удаление записи о посещаемости"""
    with next(get_db()) as db:
        att = db.query(Attendance).filter_by(attendance_id=attendance_id).first()
        if not att:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись о посещаемости не найдена"
            )
        db.delete(att)
        db.commit()
        return {"status": "Удалена"}

# -----------------------
# UPDATE ATTENDANCE
# -----------------------
def update_attendance_db(attendance_id: int, att_status: Optional[AttendanceType] = None,
                        excuse_reason: Optional[str] = None, extra_lesson: Optional[str] = None) -> Attendance:
    """Обновление записи о посещаемости"""
    with next(get_db()) as db:
        att = db.query(Attendance).filter_by(attendance_id=attendance_id).first()
        if not att:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись о посещаемости не найдена"
            )
        
        if att_status is not None:
            att.att_status = att_status
        if excuse_reason is not None:
            att.excuse_reason = excuse_reason
        if extra_lesson is not None:
            att.extra_lesson = extra_lesson
            
        db.commit()
        db.refresh(att)
        return att

# -----------------------
# GET ATTENDANCE BY GROUP & SUBJECT
# -----------------------
def get_attendance_by_group_and_subject_db(group_id: int, subject_id: int) -> List[Attendance]:
    """Получение посещаемости группы по предмету"""
    with next(get_db()) as db:
        records = (db.query(Attendance)
                  .join(Attendance.student)
                  .filter(Student.group_id == group_id, Attendance.subject_id == subject_id)
                  .all())
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Посещаемость группы {group_id} по предмету {subject_id} не найдена"
            )
        return records

# -----------------------
# GET ATTENDANCE BY STUDENT & SUBJECT
# -----------------------
def get_attendance_by_student_and_subject_db(student_id: int, subject_id: int) -> List[Attendance]:
    """Получение посещаемости студента по предмету"""
    with next(get_db()) as db:
        records = (db.query(Attendance)
                  .filter_by(student_id=student_id, subject_id=subject_id)
                  .all())
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Посещаемость студента {student_id} по предмету {subject_id} не найдена"
            )
        return records

# -----------------------
# GET ATTENDANCE BY STUDENT & TOPIC
# -----------------------
def get_attendance_by_student_and_topic_db(student_id: int, topic_id: int) -> Attendance:
    """Получение посещаемости студента по теме"""
    with next(get_db()) as db:
        record = (db.query(Attendance)
                 .filter_by(student_id=student_id, topic_id=topic_id)
                 .first())
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Посещаемость студента {student_id} по теме {topic_id} не найдена"
            )
        return record

# -----------------------
# CHANGE STATUS BY LESSON
# -----------------------
def change_attendance_status_by_lesson_db(student_id: int, topic_id: int,
                                         new_status: AttendanceType) -> Attendance:
    """Изменение статуса посещаемости по уроку"""
    with next(get_db()) as db:
        att = (db.query(Attendance)
               .filter_by(student_id=student_id, topic_id=topic_id)
               .first())
        if not att:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись о посещаемости для данного урока не найдена"
            )
        att.att_status = new_status
        db.commit()
        db.refresh(att)
        return att

# -----------------------
# COUNT MISSED LESSONS
# -----------------------
def count_missed_lessons_db(student_id: int, subject_id: Optional[int] = None) -> int:
    """Подсчет пропущенных уроков студента"""
    with next(get_db()) as db:
        query = db.query(Attendance).filter_by(
            student_id=student_id,
            att_status=AttendanceType.ABSENT
        )
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        return query.count()

# -----------------------
# COUNT LATE ARRIVALS
# -----------------------
def count_late_arrivals_db(student_id: int, subject_id: Optional[int] = None) -> int:
    """Подсчет опозданий студента"""
    with next(get_db()) as db:
        query = db.query(Attendance).filter_by(
            student_id=student_id,
            att_status=AttendanceType.LATE
        )
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        return query.count()

# -----------------------
# GET ATTENDANCE STATISTICS
# -----------------------
def get_attendance_statistics_db(student_id: int, subject_id: Optional[int] = None) -> dict:
    """Получение статистики посещаемости студента"""
    with next(get_db()) as db:
        query = db.query(Attendance).filter_by(student_id=student_id)
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        total_lessons = query.count()
        present_count = query.filter_by(att_status=AttendanceType.PRESENT).count()
        absent_count = query.filter_by(att_status=AttendanceType.ABSENT).count()
        late_count = query.filter_by(att_status=AttendanceType.LATE).count()
        
        attendance_rate = (present_count / total_lessons * 100) if total_lessons > 0 else 0
        
        return {
            "student_id": student_id,
            "subject_id": subject_id,
            "total_lessons": total_lessons,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
            "attendance_rate": round(attendance_rate, 2)
        }

# -----------------------
# GET STUDENTS WITH EXCUSE
# -----------------------
def get_students_with_excuse_db(topic_id: int) -> List[Attendance]:
    """Получение студентов с уважительной причиной отсутствия по теме"""
    with next(get_db()) as db:
        records = (db.query(Attendance)
                  .filter(
                      Attendance.topic_id == topic_id,
                      Attendance.att_status == AttendanceType.ABSENT,
                      Attendance.excuse_reason.isnot(None)
                  )
                  .all())
        return records

# -----------------------
# GET STUDENTS FOR EXTRA LESSON
# -----------------------
def get_students_for_extra_lesson_db(topic_id: int) -> List[Attendance]:
    """Получение студентов, которым назначен дополнительный урок"""
    with next(get_db()) as db:
        records = (db.query(Attendance)
                  .filter(
                      Attendance.topic_id == topic_id,
                      Attendance.extra_lesson.isnot(None)
                  )
                  .all())
        return records