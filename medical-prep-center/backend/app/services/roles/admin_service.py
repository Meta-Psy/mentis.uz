from typing import List, Optional, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.database.models.user import Admin, AdminInfo, AdminStatus, User
from app.database.models.academic import Group, Topic, Block, Section, Subject
from app.database.models.assessment import Question
from app.database.models.user import User, Student, Teacher, Admin
from app.database.models.academic import Subject, Section, Block, Topic
from app.schemas.auth.admin import *
from app.services.roles.user_service import *
from app.database.models.assessment import Question
from datetime import datetime, timedelta
from app.database.models.assessment import TopicTest, DtmExam, Attendance, Comments
import csv
import json
from io import StringIO

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



async def get_dashboard_statistics_db(db: AsyncSession) -> AdminDashboardStatistics:
    """Получение статистики для дашборда админки"""
    
    # Общее количество пользователей
    total_users_result = await db.execute(select(func.count(User.user_id)))
    total_users = total_users_result.scalar()
    
    # Активные студенты
    active_students_result = await db.execute(
        select(func.count(Student.student_id))
        .join(User, Student.student_id == User.user_id)
        .filter(User.is_active == True)
    )
    active_students = active_students_result.scalar()
    
    # Активные учителя
    active_teachers_result = await db.execute(
        select(func.count(Teacher.teacher_id))
        .join(User, Teacher.teacher_id == User.user_id)
        .filter(User.is_active == True)
    )
    active_teachers = active_teachers_result.scalar()
    
    # Общее количество предметов
    total_subjects_result = await db.execute(select(func.count(Subject.subject_id)))
    total_subjects = total_subjects_result.scalar()
    
    # Общее количество тем
    total_topics_result = await db.execute(select(func.count(Topic.topic_id)))
    total_topics = total_topics_result.scalar()
    
    # Общее количество вопросов
    total_questions_result = await db.execute(select(func.count(Question.question_id)))
    total_questions = total_questions_result.scalar()
    
    # Общее количество групп
    total_groups_result = await db.execute(select(func.count(Group.group_id)))
    total_groups = total_groups_result.scalar()
    
    # Статистика за последний месяц
    last_month = datetime.now() - timedelta(days=30)
    
    # Новые пользователи за месяц
    new_users_month_result = await db.execute(
        select(func.count(User.user_id))
        .filter(User.registration_date >= last_month)
    )
    new_users_month = new_users_month_result.scalar()
    
    # Новые вопросы за месяц (предполагаем, что у Question есть created_at)
    new_questions_month_result = await db.execute(
        select(func.count(Question.question_id))
    )
    new_questions_month = new_questions_month_result.scalar()  # Заглушка, т.к. нет created_at
    
    # Завершенные тесты за месяц
    completed_tests_month_result = await db.execute(
        select(func.count(TopicTest.topic_test_id))
        .filter(TopicTest.attempt_date >= last_month)
    )
    completed_tests_month = completed_tests_month_result.scalar()
    
    return AdminDashboardStatistics(
        total_users=total_users,
        active_students=active_students,
        active_teachers=active_teachers,
        total_subjects=total_subjects,
        total_topics=total_topics,
        total_questions=total_questions,
        total_groups=total_groups,
        total_universities=0,  # Добавим если нужно
        new_users_month=new_users_month,
        new_questions_month=new_questions_month,
        completed_tests_month=completed_tests_month
    )

async def get_system_health_db(db: AsyncSession) -> SystemHealth:
    """Получение информации о здоровье системы"""
    
    try:
        # Проверяем подключение к БД
        await db.execute(select(1))
        database_status = "connected"
    except:
        database_status = "error"
    
    # Активные сессии (примерная логика)
    active_sessions_result = await db.execute(
        select(func.count(User.user_id))
        .filter(User.is_active == True)
    )
    active_sessions = active_sessions_result.scalar()
    
    return SystemHealth(
        status="healthy" if database_status == "connected" else "unhealthy",
        database_status=database_status,
        active_sessions=active_sessions,
        server_uptime="1d 5h 30m",  # Заглушка
        memory_usage=45.6,  # Заглушка
        cpu_usage=12.3  # Заглушка
    )

# app/services/admin/content_management.py
async def get_content_hierarchy_db(db: AsyncSession, subject_id: Optional[int] = None) -> Dict[str, Any]:
    """Получение иерархии контента (предмет -> раздел -> блок -> тема -> вопросы)"""
    
    query = select(Subject)
    if subject_id:
        query = query.filter(Subject.subject_id == subject_id)
    
    subjects_result = await db.execute(query)
    subjects = subjects_result.scalars().all()
    
    hierarchy = []
    
    for subject in subjects:
        subject_data = {
            "subject_id": subject.subject_id,
            "subject_name": subject.name,
            "sections": []
        }
        
        # Получаем разделы
        sections_result = await db.execute(
            select(Section)
            .filter(Section.subject_id == subject.subject_id)
            .order_by(Section.order_number)
        )
        sections = sections_result.scalars().all()
        
        for section in sections:
            section_data = {
                "section_id": section.section_id,
                "section_name": section.name,
                "blocks": []
            }
            
            # Получаем блоки
            blocks_result = await db.execute(
                select(Block)
                .filter(Block.section_id == section.section_id)
                .order_by(Block.order_number)
            )
            blocks = blocks_result.scalars().all()
            
            for block in blocks:
                block_data = {
                    "block_id": block.block_id,
                    "block_name": block.name,
                    "topics": []
                }
                
                # Получаем темы
                topics_result = await db.execute(
                    select(Topic)
                    .filter(Topic.block_id == block.block_id)
                    .order_by(Topic.number)
                )
                topics = topics_result.scalars().all()
                
                for topic in topics:
                    # Считаем вопросы
                    questions_count_result = await db.execute(
                        select(func.count(Question.question_id))
                        .filter(Question.topic_id == topic.topic_id)
                    )
                    questions_count = questions_count_result.scalar()
                    
                    topic_data = {
                        "topic_id": topic.topic_id,
                        "topic_name": topic.name,
                        "topic_number": topic.number,
                        "questions_count": questions_count
                    }
                    
                    block_data["topics"].append(topic_data)
                
                section_data["blocks"].append(block_data)
            
            subject_data["sections"].append(section_data)
        
        hierarchy.append(subject_data)
    
    return {"subjects": hierarchy}

async def bulk_delete_content_db(db: AsyncSession, content_type: str, item_ids: List[int]) -> Dict[str, Any]:
    """Массовое удаление контента"""
    
    results = {"deleted": [], "errors": []}
    
    for item_id in item_ids:
        try:
            if content_type == "subjects":
                from app.services.content.subject_service import delete_subject_db
                result = await delete_subject_db(db, item_id)
                results["deleted"].append({"id": item_id, "type": content_type})
                
            elif content_type == "sections":
                from app.services.content.section_service import delete_section_db
                result = await delete_section_db(db, item_id)
                results["deleted"].append({"id": item_id, "type": content_type})
                
            elif content_type == "topics":
                from app.services.content.topic_service import delete_topic_db
                result = await delete_topic_db(db, item_id)
                results["deleted"].append({"id": item_id, "type": content_type})
                
            elif content_type == "questions":
                from app.services.content.question_service import delete_question_db
                result = await delete_question_db(db, item_id)
                results["deleted"].append({"id": item_id, "type": content_type})
                
        except Exception as e:
            results["errors"].append({"id": item_id, "error": str(e)})
    
    return results

# app/services/admin/user_management.py
async def get_user_detailed_info_db(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """Получение детальной информации о пользователе для админки"""
    
    user = await get_user_by_id_db(db, user_id)
    
    user_info = {
        "user_id": user.user_id,
        "name": user.name,
        "surname": user.surname,
        "phone": user.phone,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "registration_date": user.registration_date,
        "photo": user.photo,
        "role_specific_info": {}
    }
    
    # Добавляем роль-специфичную информацию
    if user.role.value == "student" and user.student:
        student = user.student
        user_info["role_specific_info"] = {
            "direction": student.direction,
            "group_id": student.group_id,
            "goal": student.goal,
            "status": student.student_status.value,
            "last_login": student.last_login,
        }
        
        # Добавляем дополнительную информацию
        if student.student_info:
            user_info["role_specific_info"].update({
                "hobby": student.student_info.hobby,
                "sex": student.student_info.sex,
                "address": student.student_info.address,
                "birthday": student.student_info.birthday
            })
    
    elif user.role.value == "teacher" and user.teacher:
        teacher = user.teacher
        user_info["role_specific_info"] = {
            "schedule": teacher.teacher_schedule,
            "status": teacher.teacher_status.value,
            "subjects": [subject.name for subject in teacher.subjects],
            "groups_count": len(teacher.groups)
        }
        
        # Добавляем дополнительную информацию
        if teacher.teacher_info:
            user_info["role_specific_info"].update({
                "employment": teacher.teacher_info.teacher_employment,
                "education_background": teacher.teacher_info.education_background,
                "years_experience": teacher.teacher_info.years_experiense,
                "certifications": teacher.teacher_info.certifications,
                "languages": teacher.teacher_info.languages
            })
    
    elif user.role.value == "admin" and user.admin:
        admin = user.admin
        user_info["role_specific_info"] = {
            "schedule": admin.schedule,
            "status": admin.admin_status.value
        }
        
        # Добавляем дополнительную информацию
        if admin.admin_info:
            user_info["role_specific_info"].update({
                "employment": admin.admin_info.employment,
                "hobby": admin.admin_info.admin_hobby
            })
    
    return user_info

async def bulk_user_actions_db(db: AsyncSession, action: str, user_ids: List[int], additional_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Массовые действия с пользователями"""
    
    results = {"processed": [], "errors": []}
    
    for user_id in user_ids:
        try:
            if action == "activate":
                user = await activate_user_db(db, user_id)
                results["processed"].append({"user_id": user_id, "action": "activated"})
                
            elif action == "deactivate":
                user = await deactivate_user_db(db, user_id)
                results["processed"].append({"user_id": user_id, "action": "deactivated"})
                
            elif action == "delete":
                result = await delete_user_db(db, user_id)
                results["processed"].append({"user_id": user_id, "action": "deleted"})
                
            elif action == "assign_group" and additional_data and "group_id" in additional_data:
                # Назначение группы студентам
                from app.services.roles.student_service import update_student_db
                user = await get_user_by_id_db(db, user_id)
                if user.role.value == "student":
                    await update_student_db(db, user_id, group_id=additional_data["group_id"])
                    results["processed"].append({"user_id": user_id, "action": "assigned_to_group"})
                else:
                    results["errors"].append({"user_id": user_id, "error": "User is not a student"})
                    
        except Exception as e:
            results["errors"].append({"user_id": user_id, "error": str(e)})
    
    return results

async def get_users_statistics_db(db: AsyncSession) -> Dict[str, Any]:
    """Получение расширенной статистики пользователей"""
    
    # Общая статистика из существующей функции
    basic_stats = await get_user_statistics_db(db)
    
    # Дополнительная статистика
    # Активность пользователей за последние 30 дней
    last_month = datetime.now() - timedelta(days=30)
    
    # Студенты с последним входом
    active_students_result = await db.execute(
        select(func.count(Student.student_id))
        .filter(and_(
            Student.last_login >= last_month,
            Student.student_status == "active"
        ))
    )
    active_students_last_month = active_students_result.scalar()
    
    # Группировка по статусам
    student_statuses_result = await db.execute(
        select(Student.student_status, func.count(Student.student_id))
        .group_by(Student.student_status)
    )
    student_statuses = dict(student_statuses_result.all())
    
    teacher_statuses_result = await db.execute(
        select(Teacher.teacher_status, func.count(Teacher.teacher_id))
        .group_by(Teacher.teacher_status)
    )
    teacher_statuses = dict(teacher_statuses_result.all())
    
    extended_stats = {
        **basic_stats,
        "active_students_last_month": active_students_last_month,
        "student_statuses": student_statuses,
        "teacher_statuses": teacher_statuses,
        "registration_trends": await get_registration_trends_db(db)
    }
    
    return extended_stats

async def get_registration_trends_db(db: AsyncSession) -> List[Dict[str, Any]]:
    """Получение трендов регистрации по месяцам"""
    
    # Группируем регистрации по месяцам за последний год
    one_year_ago = datetime.now() - timedelta(days=365)
    
    trends_result = await db.execute(
        select(
            func.date_trunc('month', User.registration_date).label('month'),
            func.count(User.user_id).label('count')
        )
        .filter(User.registration_date >= one_year_ago)
        .group_by(func.date_trunc('month', User.registration_date))
        .order_by(func.date_trunc('month', User.registration_date))
    )
    
    trends = []
    for month, count in trends_result.all():
        trends.append({
            "month": month.strftime("%Y-%m"),
            "registrations": count
        })
    
    return trends

# app/services/admin/analytics_service.py
async def get_test_analytics_db(db: AsyncSession, days: int = 30) -> Dict[str, Any]:
    """Аналитика по тестам за указанный период"""
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Общее количество пройденных тестов
    total_tests_result = await db.execute(
        select(func.count(TopicTest.topic_test_id))
        .filter(TopicTest.attempt_date >= start_date)
    )
    total_tests = total_tests_result.scalar()
    
    # Средний балл
    avg_score_result = await db.execute(
        select(func.avg(TopicTest.correct_answers))
        .filter(TopicTest.attempt_date >= start_date)
    )
    avg_score = avg_score_result.scalar() or 0.0
    
    # Распределение по дням
    daily_tests_result = await db.execute(
        select(
            func.date(TopicTest.attempt_date).label('date'),
            func.count(TopicTest.topic_test_id).label('count'),
            func.avg(TopicTest.correct_answers).label('avg_score')
        )
        .filter(TopicTest.attempt_date >= start_date)
        .group_by(func.date(TopicTest.attempt_date))
        .order_by(func.date(TopicTest.attempt_date))
    )
    
    daily_stats = []
    for date, count, avg in daily_tests_result.all():
        daily_stats.append({
            "date": date.isoformat(),
            "tests_count": count,
            "average_score": float(avg) if avg else 0.0
        })
    
    return {
        "period_days": days,
        "total_tests": total_tests,
        "average_score": float(avg_score),
        "daily_statistics": daily_stats
    }

async def get_attendance_analytics_db(db: AsyncSession, days: int = 30) -> Dict[str, Any]:
    """Аналитика по посещаемости"""
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Общая статистика посещаемости
    attendance_stats_result = await db.execute(
        select(
            Attendance.att_status,
            func.count(Attendance.attendance_id).label('count')
        )
        .filter(Attendance.lesson_date_time >= start_date)
        .group_by(Attendance.att_status)
    )
    
    attendance_stats = {}
    total_records = 0
    
    for status, count in attendance_stats_result.all():
        attendance_stats[status.value] = count
        total_records += count
    
    # Вычисляем проценты
    attendance_percentages = {}
    if total_records > 0:
        for status, count in attendance_stats.items():
            attendance_percentages[f"{status}_percentage"] = (count / total_records) * 100
    
    return {
        "period_days": days,
        "total_records": total_records,
        "attendance_counts": attendance_stats,
        "attendance_percentages": attendance_percentages
    }

async def get_comments_analytics_db(db: AsyncSession, days: int = 30) -> Dict[str, Any]:
    """Аналитика по комментариям"""
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Статистика по типам комментариев
    comments_stats_result = await db.execute(
        select(
            Comments.comment_type,
            func.count(Comments.comment_id).label('count')
        )
        .filter(Comments.comment_date >= start_date)
        .group_by(Comments.comment_type)
    )
    
    comments_stats = {}
    total_comments = 0
    
    for comment_type, count in comments_stats_result.all():
        comments_stats[comment_type.value] = count
        total_comments += count
    
    # Самые активные учителя
    active_teachers_result = await db.execute(
        select(
            Comments.teacher_id,
            func.count(Comments.comment_id).label('count')
        )
        .filter(Comments.comment_date >= start_date)
        .group_by(Comments.teacher_id)
        .order_by(func.count(Comments.comment_id).desc())
        .limit(10)
    )
    
    active_teachers = []
    for teacher_id, count in active_teachers_result.all():
        active_teachers.append({
            "teacher_id": teacher_id,
            "comments_count": count
        })
    
    return {
        "period_days": days,
        "total_comments": total_comments,
        "comments_by_type": comments_stats,
        "most_active_teachers": active_teachers
    }

async def get_dtm_analytics_db(db: AsyncSession, days: int = 30) -> Dict[str, Any]:
    """Аналитика по DTM экзаменам"""
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Общая статистика DTM
    dtm_stats_result = await db.execute(
        select(
            func.count(DtmExam.exam_id).label('total_exams'),
            func.avg(DtmExam.total_correct_answers).label('avg_score'),
            func.max(DtmExam.total_correct_answers).label('max_score'),
            func.min(DtmExam.total_correct_answers).label('min_score')
        )
        .filter(DtmExam.exam_date >= start_date)
    )
    
    stats = dtm_stats_result.first()
    
    # Распределение баллов
    score_distribution_result = await db.execute(
        select(
            func.floor(DtmExam.total_correct_answers / 10) * 10,
            func.count(DtmExam.exam_id)
        )
        .filter(DtmExam.exam_date >= start_date)
        .group_by(func.floor(DtmExam.total_correct_answers / 10))
        .order_by(func.floor(DtmExam.total_correct_answers / 10))
    )
    
    score_distribution = []
    for score_range, count in score_distribution_result.all():
        score_distribution.append({
            "score_range": f"{int(score_range)}-{int(score_range) + 9}",
            "count": count
        })
    
    return {
        "period_days": days,
        "total_exams": stats.total_exams or 0,
        "average_score": float(stats.avg_score) if stats.avg_score else 0.0,
        "max_score": float(stats.max_score) if stats.max_score else 0.0,
        "min_score": float(stats.min_score) if stats.min_score else 0.0,
        "score_distribution": score_distribution
    }

# app/services/admin/export_service.py
async def export_users_to_csv_db(db: AsyncSession, role_filter: Optional[str] = None) -> str:
    """Экспорт пользователей в CSV формат"""
    
    users = await get_all_users_db(db)
    
    if role_filter:
        users = [u for u in users if u.role.value == role_filter]
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow([
        'ID', 'Name', 'Surname', 'Phone', 'Email', 'Role', 
        'Is Active', 'Registration Date'
    ])
    
    # Данные
    for user in users:
        writer.writerow([
            user.user_id,
            user.name,
            user.surname,
            user.phone,
            user.email,
            user.role.value,
            user.is_active,
            user.registration_date.isoformat() if user.registration_date else ''
        ])
    
    return output.getvalue()

async def export_content_hierarchy_to_json_db(db: AsyncSession) -> str:
    """Экспорт иерархии контента в JSON"""
    
    from app.services.roles.admin_service import get_content_hierarchy_db
    
    hierarchy = await get_content_hierarchy_db(db)
    
    return json.dumps(hierarchy, ensure_ascii=False, indent=2)

# app/services/admin/validation_service.py
async def validate_content_integrity_db(db: AsyncSession) -> Dict[str, Any]:
    """Проверка целостности контента"""
    
    issues = []
    
    # Проверяем темы без вопросов
    topics_without_questions_result = await db.execute(
        select(Topic.topic_id, Topic.name)
        .outerjoin(Question, Topic.topic_id == Question.topic_id)
        .group_by(Topic.topic_id, Topic.name)
        .having(func.count(Question.question_id) == 0)
    )
    
    for topic_id, topic_name in topics_without_questions_result.all():
        issues.append({
            "type": "topic_without_questions",
            "id": topic_id,
            "name": topic_name,
            "severity": "warning"
        })
    
    # Проверяем вопросы с неправильными ответами
    invalid_questions_result = await db.execute(
        select(Question.question_id, Question.text)
        .filter(or_(
            Question.correct_answers < 1,
            Question.correct_answers > 4,
            Question.text == None,
            Question.text == ""
        ))
    )
    
    for question_id, question_text in invalid_questions_result.all():
        issues.append({
            "type": "invalid_question",
            "id": question_id,
            "text": question_text[:50] + "..." if question_text else "No text",
            "severity": "error"
        })
    
    # Проверяем блоки без тем
    blocks_without_topics_result = await db.execute(
        select(Block.block_id, Block.name)
        .outerjoin(Topic, Block.block_id == Topic.block_id)
        .group_by(Block.block_id, Block.name)
        .having(func.count(Topic.topic_id) == 0)
    )
    
    for block_id, block_name in blocks_without_topics_result.all():
        issues.append({
            "type": "block_without_topics",
            "id": block_id,
            "name": block_name,
            "severity": "warning"
        })
    
    return {
        "total_issues": len(issues),
        "errors": [i for i in issues if i["severity"] == "error"],
        "warnings": [i for i in issues if i["severity"] == "warning"],
        "all_issues": issues
    }