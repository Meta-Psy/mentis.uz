from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import or_, and_
from app.database import get_db
from app.database.models.user import (
    User, UserRole, Student, Teacher, Admin, ParentInfo,
    StudentStatus, TeacherStatus, AdminStatus
)

# ===========================================
# EXISTING USER OPERATIONS (Updated)
# ===========================================

def create_user_db(name: str, surname: str, phone: str, password: str, role: UserRole,
                  email: Optional[str] = None, photo: Optional[str] = None,
                  # Параметры для студента
                  direction: Optional[str] = None, group_id: Optional[int] = None, goal: Optional[str] = None,
                  # Параметры для учителя
                  teacher_schedule: Optional[str] = None,
                  # Параметры для администратора
                  admin_schedule: Optional[str] = None) -> User:
    """Создание нового пользователя с соответствующей ролевой записью"""
    with next(get_db()) as db:
        # Проверяем уникальность телефона
        existing_user = db.query(User).filter_by(phone=phone).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким номером телефона уже существует"
            )
        
        # Проверяем уникальность email, если он указан
        if email:
            existing_email = db.query(User).filter_by(email=email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже существует"
                )

        new_user = User(
            name=name,
            surname=surname,
            phone=phone,
            email=email,
            password=password,
            role=role,
            photo=photo
        )
        db.add(new_user)
        db.flush()  # Получаем ID пользователя без коммита
        
        # Создаем соответствующую ролевую запись
        if role == UserRole.STUDENT:
            if not group_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Для студента обязательно указать group_id"
                )
            student = Student(
                student_id=new_user.user_id,
                direction=direction or "",
                group_id=group_id,
                goal=goal,
                student_status=StudentStatus.ACTIVE
            )
            db.add(student)
            
        elif role == UserRole.TEACHER:
            teacher = Teacher(
                teacher_id=new_user.user_id,
                teacher_schedule=teacher_schedule,
                teacher_status=TeacherStatus.ACTIVE
            )
            db.add(teacher)
            
        elif role == UserRole.ADMIN:
            admin = Admin(
                admin_id=new_user.user_id,
                schedule=admin_schedule,
                admin_status=AdminStatus.ACTIVE
            )
            db.add(admin)
            
        elif role == UserRole.PARENT:
            parent = ParentInfo(
                parent_id=new_user.user_id
            )
            db.add(parent)
        
        db.commit()
        db.refresh(new_user)
        return new_user

def get_user_by_id_db(user_id: int) -> User:
    """Получение пользователя по ID"""
    with next(get_db()) as db:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        return user

def get_user_by_phone_db(phone: str) -> User:
    """Получение пользователя по номеру телефона"""
    with next(get_db()) as db:
        user = db.query(User).filter_by(phone=phone).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь с таким номером телефона не найден"
            )
        return user

def update_user_db(user_id: int, name: Optional[str] = None, surname: Optional[str] = None,
                  phone: Optional[str] = None, email: Optional[str] = None,
                  password: Optional[str] = None, photo: Optional[str] = None,
                  is_active: Optional[bool] = None) -> User:
    """Обновление данных пользователя"""
    with next(get_db()) as db:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Проверяем уникальность телефона, если он изменяется
        if phone and phone != user.phone:
            existing_phone = db.query(User).filter_by(phone=phone).first()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким номером телефона уже существует"
                )

        # Проверяем уникальность email, если он изменяется
        if email and email != user.email:
            existing_email = db.query(User).filter_by(email=email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже существует"
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
        db.commit()
        db.refresh(user)
        return user

def delete_user_db(user_id: int) -> dict:
    """Удаление пользователя"""
    with next(get_db()) as db:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        db.delete(user)
        db.commit()
        return {"status": "Удален"}

# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================

def get_users_by_role_db(role: UserRole) -> List[User]:
    """Получение пользователей по роли"""
    with next(get_db()) as db:
        users = db.query(User).filter_by(role=role).all()
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователи с ролью {role.value} не найдены"
            )
        return users

def search_users_db(search_query: str) -> List[User]:
    """Поиск пользователей по имени, фамилии, телефону или email"""
    with next(get_db()) as db:
        users = db.query(User).filter(
            or_(
                User.name.ilike(f"%{search_query}%"),
                User.surname.ilike(f"%{search_query}%"),
                User.phone.ilike(f"%{search_query}%"),
                User.email.ilike(f"%{search_query}%") if search_query else False
            )
        ).all()
        
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователи, соответствующие запросу '{search_query}', не найдены"
            )
        return users

def update_last_login_time_db(user_id: int) -> User:
    """Обновление времени последнего входа"""
    with next(get_db()) as db:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Обновляем время последнего входа в зависимости от роли
        if user.role == UserRole.STUDENT and user.student:
            user.student.last_login = datetime.now()
        
        user.updated_at = datetime.now()
        db.commit()
        db.refresh(user)
        return user

def get_inactive_users_db(role: Optional[UserRole] = None) -> List[User]:
    """Получение неактивных пользователей"""
    with next(get_db()) as db:
        query = db.query(User).filter_by(is_active=False)
        
        if role:
            query = query.filter_by(role=role)
            
        users = query.all()
        
        if not users:
            role_filter = f" с ролью {role.value}" if role else ""
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Неактивные пользователи{role_filter} не найдены"
            )
        return users

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_all_users_db() -> List[User]:
    """Получение всех пользователей"""
    with next(get_db()) as db:
        users = db.query(User).all()
        return users

def get_active_users_db(role: Optional[UserRole] = None) -> List[User]:
    """Получение активных пользователей"""
    with next(get_db()) as db:
        query = db.query(User).filter_by(is_active=True)
        
        if role:
            query = query.filter_by(role=role)
            
        users = query.all()
        return users

def deactivate_user_db(user_id: int) -> User:
    """Деактивация пользователя"""
    with next(get_db()) as db:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        user.is_active = False
        user.updated_at = datetime.now()
        db.commit()
        db.refresh(user)
        return user

def activate_user_db(user_id: int) -> User:
    """Активация пользователя"""
    with next(get_db()) as db:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        user.is_active = True
        user.updated_at = datetime.now()
        db.commit()
        db.refresh(user)
        return user

def get_user_statistics_db() -> dict:
    """Получение статистики пользователей"""
    with next(get_db()) as db:
        total_users = db.query(User).count()
        active_users = db.query(User).filter_by(is_active=True).count()
        inactive_users = db.query(User).filter_by(is_active=False).count()
        
        students_count = db.query(User).filter_by(role=UserRole.STUDENT).count()
        teachers_count = db.query(User).filter_by(role=UserRole.TEACHER).count()
        admins_count = db.query(User).filter_by(role=UserRole.ADMIN).count()
        parents_count = db.query(User).filter_by(role=UserRole.PARENT).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "users_by_role": {
                "students": students_count,
                "teachers": teachers_count,
                "admins": admins_count,
                "parents": parents_count
            }
        }