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
