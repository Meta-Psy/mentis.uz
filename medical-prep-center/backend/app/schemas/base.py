# app/schemas/base.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# ===== БАЗОВЫЕ ENUMS =====

class UserRoleEnum(str, Enum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"

class StudentStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class TeacherStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class AttendanceStatusEnum(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class CommentTypeEnum(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class UniversityTypeEnum(str, Enum):
    STATE = "state"
    PRIVATE = "private"

# ===== БАЗОВЫЕ СХЕМЫ =====

class BaseResponse(BaseModel):
    """Базовая схема ответа"""
    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    """Схема для пагинированных ответов"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# ===== USER СХЕМЫ =====

class UserBase(BaseModel):
    name: str = Field(..., max_length=100)
    surname: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20)
    email: Optional[str] = Field(None, max_length=150)
    photo: Optional[str] = Field(None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRoleEnum
    # Дополнительные поля для студентов
    direction: Optional[str] = None
    group_id: Optional[int] = None
    goal: Optional[str] = None
    # Дополнительные поля для учителей
    teacher_schedule: Optional[str] = None
    # Дополнительные поля для администраторов
    admin_schedule: Optional[str] = None

class UserResponse(UserBase, BaseResponse):
    user_id: int
    role: UserRoleEnum
    is_active: bool
    registration_date: datetime
    created_at: datetime
    updated_at: datetime

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    surname: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=150)
    photo: Optional[str] = Field(None, max_length=255)

# ===== AUTH СХЕМЫ =====

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str

class UserLogin(BaseModel):
    phone: str
    password: str

# ===== STUDENT СХЕМЫ =====

class StudentBase(BaseModel):
    direction: str = Field(..., max_length=200)
    group_id: int
    goal: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    direction: Optional[str] = Field(None, max_length=200)
    goal: Optional[str] = None

class StudentResponse(StudentBase, BaseResponse):
    student_id: int
    student_status: StudentStatusEnum
    last_login: Optional[datetime]

class StudentInfoBase(BaseModel):
    hobby: Optional[str] = Field(None, max_length=500)
    sex: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = None
    birthday: Optional[datetime] = None

class StudentInfoResponse(StudentInfoBase, BaseResponse):
    student_id: int

class StudentProfileResponse(BaseResponse):
    student_info: StudentResponse
    chemistry_average: float
    biology_average: float
    attendance_rate: float
    overdue_tests: Dict[str, Any]
    upcoming_tests: Dict[str, Any]

# ===== TEACHER СХЕМЫ =====

class TeacherBase(BaseModel):
    teacher_schedule: Optional[str] = None

class TeacherUpdate(TeacherBase):
    pass

class TeacherResponse(TeacherBase, BaseResponse):
    teacher_id: int
    teacher_status: TeacherStatusEnum

class TeacherInfoBase(BaseModel):
    teacher_employment: Optional[str] = Field(None, max_length=100)
    teacher_number: Optional[str] = Field(None, max_length=15)
    dop_info: Optional[str] = Field(None, max_length=100)
    education_background: Optional[str] = None
    years_experiense: Optional[int] = None
    certifications: Optional[str] = None
    availability: Optional[str] = None
    languages: Optional[str] = None

class TeacherInfoResponse(TeacherInfoBase, BaseResponse):
    teacher_info_id: int
    teacher_id: int

class TeacherProfileResponse(BaseResponse):
    teacher: TeacherResponse
    teacher_info: Optional[TeacherInfoResponse]
    subjects: List[Dict[str, Any]]

# ===== ATTENDANCE СХЕМЫ =====

class AttendanceBase(BaseModel):
    lesson_date_time: datetime
    att_status: AttendanceStatusEnum
    subject_id: int
    topic_id: int
    excuse_reason: Optional[str] = None
    extra_lesson: Optional[str] = None

class CreateAttendanceRequest(AttendanceBase):
    student_id: int

class UpdateAttendanceRequest(BaseModel):
    att_status: Optional[AttendanceStatusEnum] = None
    excuse_reason: Optional[str] = None
    extra_lesson: Optional[str] = None

class AttendanceResponse(AttendanceBase, BaseResponse):
    attendance_id: int
    student_id: int

# ===== COMMENT СХЕМЫ =====

class CommentBase(BaseModel):
    comment_text: str
    comment_type: CommentTypeEnum

class CreateCommentRequest(CommentBase):
    student_id: int

class UpdateCommentRequest(BaseModel):
    comment_text: Optional[str] = None
    comment_type: Optional[CommentTypeEnum] = None

class CommentResponse(CommentBase, BaseResponse):
    comment_id: int
    teacher_id: int
    student_id: int
    comment_date: datetime

# ===== GRADE СХЕМЫ =====

class CurrentRatingBase(BaseModel):
    subject_id: int
    topic_id: int
    current_correct_answers: float
    second_current_correct_answers: float

class CreateCurrentRatingRequest(CurrentRatingBase):
    student_id: int

class UpdateCurrentRatingRequest(BaseModel):
    current_correct_answers: Optional[float] = None
    second_current_correct_answers: Optional[float] = None

class CurrentRatingResponse(CurrentRatingBase, BaseResponse):
    rating_id: int
    student_id: int
    last_updated: datetime

# ===== TEST СХЕМЫ =====

class StartTestRequest(BaseModel):
    test_id: int
    category: str = Field(..., pattern="^(topic|block|section|module|dtm)$")
    category_id: int
    questions_limit: int = Field(30, ge=10, le=50)

class SaveProgressRequest(BaseModel):
    answers: Dict[str, str]
    time_elapsed: int

class SubmitTestRequest(BaseModel):
    answers: Dict[str, str]
    time_elapsed: int

class TestSessionResponse(BaseResponse):
    session_id: str
    student_id: int
    test_id: int
    category: str
    category_id: int
    questions: List[Dict[str, Any]]
    answers: Dict[str, str]
    start_time: str
    time_elapsed: int
    is_completed: bool

class TestResultResponse(BaseResponse):
    test_id: int
    student_id: int
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    time_spent: int
    percentage: float
    ranking: Dict[str, int]
    question_results: List[Dict[str, Any]]

class AvailableTestResponse(BaseResponse):
    id: int
    title: str
    subject: str
    type: str
    questions_count: int
    estimated_time: int
    topic_id: int
    is_available: bool
    required_topics: List[int]

class TestHistoryItem(BaseResponse):
    id: int
    title: str
    subject: str
    score: int
    max_score: int
    percentage: float
    date: datetime
    time_spent: int
    test_type: str

class DetailedTestResultResponse(BaseResponse):
    # Детальная информация о результатах теста
    pass

# ===== GROUP СХЕМЫ =====

class GroupBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    max_student: Optional[int] = None

class GroupResponse(GroupBase, BaseResponse):
    group_id: int
    subject_id: int