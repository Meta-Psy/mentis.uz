from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime
from enum import Enum

# ========== ТИПЫ И КОНСТАНТЫ ==========


class TestTypeEnum(str, Enum):
    TRAINING = "training"
    CONTROL = "control"
    FINAL = "final"


class TestStatusEnum(str, Enum):
    COMPLETED = "completed"
    CURRENT = "current"
    OVERDUE = "overdue"
    AVAILABLE = "available"


class AttendanceStatusEnum(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"


class CommentTypeEnum(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# ========== БАЗОВЫЕ МОДЕЛИ ==========


class TestAttemptResponse(BaseModel):
    """Модель попытки прохождения теста"""

    attempt_id: int = Field(..., alias="topic_test_id")
    score_percentage: float
    correct_answers: float = Field(..., alias="correct_answers")
    total_questions: int = Field(..., alias="question_count")
    attempt_date: datetime
    time_spent: Optional[str] = None
    passed: bool

    def __init__(self, **data):
        # Вычисляем score_percentage если его нет
        if (
            "score_percentage" not in data
            and "correct_answers" in data
            and "question_count" in data
        ):
            if data["question_count"] > 0:
                data["score_percentage"] = (
                    data["correct_answers"] / data["question_count"]
                ) * 100
            else:
                data["score_percentage"] = 0.0

        # Определяем passed статус
        if "passed" not in data:
            data["passed"] = data.get("score_percentage", 0) >= 60.0

        super().__init__(**data)

    class Config:
        from_attributes = True
        populate_by_name = True


class QuestionResponse(BaseModel):
    """Модель вопроса"""

    question_id: int
    text: str
    answer_1: Optional[str] = None
    answer_2: Optional[str] = None
    answer_3: Optional[str] = None
    answer_4: Optional[str] = None
    correct_answers: int
    explanation: Optional[str] = None
    category: List[Any] = Field(default_factory=list)
    topic_id: int

    class Config:
        from_attributes = True


class TestInfoResponse(BaseModel):
    """Информация о тесте"""

    topic_id: int
    topic_name: str
    section_id: int
    section_name: str
    subject_id: int
    subject_name: str
    block_id: Optional[int] = None
    block_name: Optional[str] = None
    status: TestStatusEnum
    deadline: Optional[str] = None
    training_attempts: List[TestAttemptResponse] = Field(default_factory=list)
    questions_count: int = 0
    time_limit_minutes: Optional[int] = None
    max_attempts: int = Field(default=999)

    class Config:
        from_attributes = True


class TestSessionResponse(BaseModel):
    """Сессия тестирования"""

    session_id: str
    topic_id: int
    test_type: TestTypeEnum
    questions: List[QuestionResponse]
    current_question: int = 0
    start_time: datetime
    end_time: Optional[datetime] = None
    time_limit_minutes: Optional[int] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class TestResultResponse(BaseModel):
    """Результат теста"""

    session_id: str
    topic_id: int
    test_type: TestTypeEnum
    score_percentage: float
    correct_answers: int
    total_questions: int
    time_spent_seconds: int
    passed: bool
    answers: Dict[int, int] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class TestStatisticsResponse(BaseModel):
    """Статистика тестов студента"""

    student_id: int
    completed_tests: int
    current_tests: int = 0
    overdue_tests: int = 0
    total_tests: int
    average_score: float
    total_time_spent_hours: float

    class Config:
        from_attributes = True


class TestCountsResponse(BaseModel):
    """Количество тестов по статусам"""

    completed: int
    current: int
    overdue: int
    available: int

    class Config:
        from_attributes = True


class TestsListResponse(BaseModel):
    """Список тестов студента"""

    tests: List[TestInfoResponse]
    total_count: int
    statistics: TestStatisticsResponse
    test_counts: TestCountsResponse

    class Config:
        from_attributes = True


class SessionProgressResponse(BaseModel):
    """Прогресс сессии"""

    current: int
    total: int
    percentage: float

    class Config:
        from_attributes = True


class TestSessionFullResponse(BaseModel):
    """Полная информация о сессии"""

    session: TestSessionResponse
    current_question: Optional[QuestionResponse] = None
    progress: SessionProgressResponse

    class Config:
        from_attributes = True


class DetailedTestResultResponse(BaseModel):
    """Детальный результат с объяснениями"""

    question_id: int
    question_text: str
    user_answer: int
    correct_answer: int
    is_correct: bool
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class TestResultFullResponse(BaseModel):
    """Полный результат теста"""

    result: TestResultResponse
    detailed_results: List[DetailedTestResultResponse]
    recommendations: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ========== ЗАПРОСЫ ==========


class CreateTestSessionRequest(BaseModel):
    """Запрос создания сессии"""

    topic_id: int = Field(..., gt=0)
    test_type: TestTypeEnum = TestTypeEnum.TRAINING
    questions_limit: int = Field(default=30, ge=5, le=50)

    class Config:
        from_attributes = True


class SubmitAnswerRequest(BaseModel):
    """Отправка ответа"""

    session_id: str
    question_id: int = Field(..., gt=0)
    answer_choice: int = Field(..., ge=1, le=4)

    class Config:
        from_attributes = True


class FinishTestRequest(BaseModel):
    """Завершение теста"""

    session_id: str
    answers: Dict[int, int] = Field(default_factory=dict)

    class Config:
        from_attributes = True


# ========== ПОСЕЩАЕМОСТЬ ==========


class AttendanceResponse(BaseModel):
    """Посещаемость"""

    attendance_id: int
    student_id: int
    lesson_date_time: datetime
    att_status: AttendanceStatusEnum
    subject_id: int
    topic_id: int
    excuse_reason: Optional[str] = None
    extra_lesson: Optional[str] = None

    class Config:
        from_attributes = True


class AttendanceStatisticsResponse(BaseModel):
    """Статистика посещаемости"""

    student_id: int
    subject_id: Optional[int] = None
    total_lessons: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_rate: float

    class Config:
        from_attributes = True


# ========== КОММЕНТАРИИ ==========


class CommentResponse(BaseModel):
    """Комментарий учителя"""

    comment_id: int
    teacher_id: int
    student_id: int
    comment_text: str
    comment_date: datetime
    comment_type: CommentTypeEnum

    class Config:
        from_attributes = True


class CommentStatisticsResponse(BaseModel):
    """Статистика комментариев"""

    total_comments: int
    positive_count: int
    negative_count: int
    neutral_count: int
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float

    class Config:
        from_attributes = True


# ========== ОЦЕНКИ ==========


class GradeResponse(BaseModel):
    """Оценка"""

    grade_value: float
    max_grade: float
    percentage: float
    exam_date: datetime
    exam_type: str

    class Config:
        from_attributes = True


class FinalGradeResponse(BaseModel):
    """Итоговая оценка"""

    student_id: int
    subject_id: int
    section_average: float
    block_average: float
    current_average: float
    topic_average: float
    final_grade: float
    counts: Dict[str, int]

    class Config:
        from_attributes = True


# ========== ЗДОРОВЬЕ API ==========


class TestsHealthResponse(BaseModel):
    """Здоровье API тестирования"""

    status: str = "healthy"
    service: str = "tests-api"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    active_sessions: int = 0

    class Config:
        from_attributes = True


# ========== ОШИБКИ ==========


class ErrorResponse(BaseModel):
    """Стандартная ошибка"""

    error: str
    detail: str
    status_code: int

    class Config:
        from_attributes = True


class ValidationErrorDetail(BaseModel):
    """Детали ошибки валидации"""

    field: str
    message: str
    value: Any

    class Config:
        from_attributes = True


class ValidationErrorResponse(BaseModel):
    """Ошибка валидации"""

    detail: List[ValidationErrorDetail]

    class Config:
        from_attributes = True
