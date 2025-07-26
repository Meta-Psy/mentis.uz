# app/schemas/admin.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime, date
from enum import Enum

# ========== ТИПЫ И КОНСТАНТЫ ==========

class UserRoleEnum(str, Enum):
    STUDENT = "STUDENT"
    PARENT = "PARENT" 
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"

class StudentStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class TeacherStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class AdminStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UniversityTypeEnum(str, Enum):
    STATE = "state"
    PRIVATE = "private"

class MaterialFileTypeEnum(str, Enum):
    BOOK = "book"
    TEST_BOOK = "test_book"

class TestTypeEnum(str, Enum):
    TRAINING = "training"
    CONTROL = "control"
    FINAL = "final"

class AttendanceTypeEnum(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class CommentTypeEnum(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

# ========== БАЗОВЫЕ ОТВЕТЫ ==========

class AdminUserResponse(BaseModel):
    """Полная информация о пользователе для админки"""
    user_id: int
    name: str
    surname: str
    phone: str
    email: Optional[str] = None
    role: UserRoleEnum
    is_active: bool
    registration_date: datetime
    photo: Optional[str] = None
    
    # Роль-специфичная информация
    role_info: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class AdminSubjectResponse(BaseModel):
    """Предмет в админке"""
    subject_id: int
    name: str
    description: Optional[str] = None
    sections_count: int = 0
    teachers_count: int = 0
    students_count: int = 0
    
    class Config:
        from_attributes = True

class AdminSectionResponse(BaseModel):
    """Раздел в админке"""
    section_id: int
    subject_id: int
    subject_name: str
    name: str
    order_number: Optional[int] = None
    blocks_count: int = 0
    topics_count: int = 0
    files_count: int = 0
    
    class Config:
        from_attributes = True

class AdminBlockResponse(BaseModel):
    """Блок в админке"""
    block_id: int
    section_id: int
    section_name: str
    subject_name: str
    name: str
    order_number: Optional[int] = None
    description: Optional[str] = None
    topics_count: int = 0
    
    class Config:
        from_attributes = True

class AdminTopicResponse(BaseModel):
    """Тема в админке"""
    topic_id: int
    block_id: int
    block_name: str
    section_name: str
    subject_name: str
    name: str
    number: Optional[int] = None
    homework: Optional[str] = None
    video_url: Optional[str] = None
    additional_material: Optional[str] = None
    questions_count: int = 0
    
    class Config:
        from_attributes = True

class AdminQuestionResponse(BaseModel):
    """Вопрос в админке"""
    question_id: int
    topic_id: int
    topic_name: str
    subject_name: str
    text: str
    answer_1: Optional[str] = None
    answer_2: Optional[str] = None
    answer_3: Optional[str] = None
    answer_4: Optional[str] = None
    correct_answers: int
    explanation: Optional[str] = None
    category: List[Any] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

class AdminGroupResponse(BaseModel):
    """Группа в админке"""
    group_id: int
    subject_id: int
    subject_name: str
    teacher_id: int
    teacher_name: str
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    max_student: Optional[int] = None
    students_count: int = 0
    
    class Config:
        from_attributes = True

class AdminUniversityResponse(BaseModel):
    """Университет в админке"""
    university_id: int
    name: str
    type: UniversityTypeEnum
    entrance_score: Optional[float] = None
    location: str
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    contact_phone: Optional[str] = None
    faculties_count: int = 0
    students_count: int = 0
    
    class Config:
        from_attributes = True

class AdminMaterialFileResponse(BaseModel):
    """Файл материала в админке"""
    file_id: int
    section_id: int
    section_name: str
    subject_name: str
    file_type: MaterialFileTypeEnum
    title: str
    author: str
    file_size: str
    file_format: str
    download_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ========== СОЗДАНИЕ И ОБНОВЛЕНИЕ ==========

class CreateUserRequest(BaseModel):
    """Создание пользователя"""
    name: str = Field(..., min_length=1, max_length=100)
    surname: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)
    role: UserRoleEnum
    photo: Optional[str] = None
    
    # Роль-специфичные параметры
    direction: Optional[str] = None  # для студента
    group_id: Optional[int] = None  # для студента
    goal: Optional[str] = None  # для студента
    teacher_schedule: Optional[str] = None  # для учителя
    admin_schedule: Optional[str] = None  # для админа

class UpdateUserRequest(BaseModel):
    """Обновление пользователя"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    surname: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: Optional[str] = Field(None, min_length=6)
    photo: Optional[str] = None
    is_active: Optional[bool] = None

class CreateSubjectRequest(BaseModel):
    """Создание предмета"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

class UpdateSubjectRequest(BaseModel):
    """Обновление предмета"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

class CreateSectionRequest(BaseModel):
    """Создание раздела"""
    subject_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=200)
    order_number: Optional[int] = None

class UpdateSectionRequest(BaseModel):
    """Обновление раздела"""
    subject_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    order_number: Optional[int] = None

class CreateBlockRequest(BaseModel):
    """Создание блока"""
    section_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=200)
    order_number: Optional[int] = None
    description: Optional[str] = None

class UpdateBlockRequest(BaseModel):
    """Обновление блока"""
    section_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    order_number: Optional[int] = None
    description: Optional[str] = None

class CreateTopicRequest(BaseModel):
    """Создание темы"""
    block_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=200)
    number: Optional[int] = None
    homework: Optional[str] = None
    video_url: Optional[str] = None
    additional_material: Optional[str] = None

class UpdateTopicRequest(BaseModel):
    """Обновление темы"""
    block_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    number: Optional[int] = None
    homework: Optional[str] = None
    video_url: Optional[str] = None
    additional_material: Optional[str] = None

class CreateQuestionRequest(BaseModel):
    """Создание вопроса"""
    topic_id: int = Field(..., gt=0)
    text: str = Field(..., min_length=10)
    answer_1: Optional[str] = None
    answer_2: Optional[str] = None
    answer_3: Optional[str] = None
    answer_4: Optional[str] = None
    correct_answers: int = Field(..., ge=1, le=4)
    explanation: Optional[str] = None
    category: Optional[List] = None

class UpdateQuestionRequest(BaseModel):
    """Обновление вопроса"""
    topic_id: Optional[int] = Field(None, gt=0)
    text: Optional[str] = Field(None, min_length=10)
    answer_1: Optional[str] = None
    answer_2: Optional[str] = None
    answer_3: Optional[str] = None
    answer_4: Optional[str] = None
    correct_answers: Optional[int] = Field(None, ge=1, le=4)
    explanation: Optional[str] = None
    category: Optional[List] = None

class CreateGroupRequest(BaseModel):
    """Создание группы"""
    subject_id: int = Field(..., gt=0)
    teacher_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    max_student: Optional[int] = Field(None, ge=1)

class UpdateGroupRequest(BaseModel):
    """Обновление группы"""
    subject_id: Optional[int] = Field(None, gt=0)
    teacher_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_student: Optional[int] = Field(None, ge=1)

class CreateUniversityRequest(BaseModel):
    """Создание университета"""
    name: str = Field(..., min_length=1, max_length=300)
    type: UniversityTypeEnum
    entrance_score: Optional[float] = Field(None, ge=0.0)
    location: str = Field(..., min_length=1, max_length=200)
    website_url: Optional[str] = Field(None, max_length=300)
    logo_url: Optional[str] = None
    contact_phone: Optional[str] = None

class UpdateUniversityRequest(BaseModel):
    """Обновление университета"""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    type: Optional[UniversityTypeEnum] = None
    entrance_score: Optional[float] = Field(None, ge=0.0)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    website_url: Optional[str] = Field(None, max_length=300)
    logo_url: Optional[str] = None
    contact_phone: Optional[str] = None

class CreateMaterialFileRequest(BaseModel):
    """Создание файла материала"""
    section_id: int = Field(..., gt=0)
    file_type: MaterialFileTypeEnum
    title: str = Field(..., min_length=1, max_length=300)
    author: str = Field(..., min_length=1, max_length=200)
    file_size: str = Field(..., max_length=50)
    file_format: str = Field(default="PDF", max_length=10)
    download_url: Optional[str] = Field(None, max_length=500)

class UpdateMaterialFileRequest(BaseModel):
    """Обновление файла материала"""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    file_size: Optional[str] = Field(None, max_length=50)
    file_format: Optional[str] = Field(None, max_length=10)
    download_url: Optional[str] = Field(None, max_length=500)

# ========== ФИЛЬТРЫ И ПОИСК ==========

class UsersFilterRequest(BaseModel):
    """Фильтры пользователей"""
    role: Optional[UserRoleEnum] = None
    is_active: Optional[bool] = None
    registration_from: Optional[datetime] = None
    registration_to: Optional[datetime] = None
    search: Optional[str] = None
    limit: int = Field(default=50, le=200)
    offset: int = Field(default=0, ge=0)

class ContentFilterRequest(BaseModel):
    """Фильтры контента"""
    subject_id: Optional[int] = None
    search: Optional[str] = None
    limit: int = Field(default=50, le=200)
    offset: int = Field(default=0, ge=0)

class BulkActionRequest(BaseModel):
    """Массовые действия"""
    action: Literal["delete", "activate", "deactivate", "assign"]
    item_ids: List[int] = Field(..., min_items=1, max_items=100)
    additional_data: Optional[Dict[str, Any]] = None

# ========== СТАТИСТИКА АДМИНКИ ==========

class AdminDashboardStatistics(BaseModel):
    """Статистика для дашборда админки"""
    total_users: int = 0
    active_students: int = 0
    active_teachers: int = 0
    total_subjects: int = 0
    total_topics: int = 0
    total_questions: int = 0
    total_groups: int = 0
    total_universities: int = 0
    
    # Активность за последний месяц
    new_users_month: int = 0
    new_questions_month: int = 0
    completed_tests_month: int = 0
    
    class Config:
        from_attributes = True

class SystemHealth(BaseModel):
    """Здоровье системы"""
    status: str = "healthy"
    database_status: str = "connected"
    active_sessions: int = 0
    server_uptime: str = "0d 0h 0m"
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    
    class Config:
        from_attributes = True

# ========== ОТВЕТЫ СПИСКОВ ==========

class PaginatedResponse(BaseModel):
    """Базовая пагинированная модель"""
    items: List[Any]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool

class AdminUsersListResponse(PaginatedResponse):
    """Список пользователей"""
    items: List[AdminUserResponse]

class AdminSubjectsListResponse(PaginatedResponse):
    """Список предметов"""
    items: List[AdminSubjectResponse]

class AdminSectionsListResponse(PaginatedResponse):
    """Список разделов"""
    items: List[AdminSectionResponse]

class AdminBlocksListResponse(PaginatedResponse):
    """Список блоков"""
    items: List[AdminBlockResponse]

class AdminTopicsListResponse(PaginatedResponse):
    """Список тем"""
    items: List[AdminTopicResponse]

class AdminQuestionsListResponse(PaginatedResponse):
    """Список вопросов"""
    items: List[AdminQuestionResponse]

class AdminGroupsListResponse(PaginatedResponse):
    """Список групп"""
    items: List[AdminGroupResponse]

class AdminUniversitiesListResponse(PaginatedResponse):
    """Список университетов"""
    items: List[AdminUniversityResponse]

class AdminMaterialFilesListResponse(PaginatedResponse):
    """Список файлов материалов"""
    items: List[AdminMaterialFileResponse]

# ========== ОШИБКИ ==========

class AdminErrorResponse(BaseModel):
    """Ошибка админки"""
    error: str
    detail: str
    status_code: int
    context: Optional[Dict[str, Any]] = None

class ValidationErrorDetail(BaseModel):
    """Детали ошибки валидации"""
    field: str
    message: str
    value: Any

class AdminValidationErrorResponse(BaseModel):
    """Ошибка валидации в админке"""
    detail: List[ValidationErrorDetail]

# ========== ЗДОРОВЬЕ АДМИНКИ ==========

class AdminHealthResponse(BaseModel):
    """Здоровье админки"""
    status: str = "healthy"
    service: str = "admin-api"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    dashboard_stats: AdminDashboardStatistics
    system_health: SystemHealth
    
    class Config:
        from_attributes = True