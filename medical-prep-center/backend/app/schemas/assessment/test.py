from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

# ========== ТИПЫ И КОНСТАНТЫ ==========

TestType = Literal["training", "control", "final"]
TestStatus = Literal["completed", "current", "overdue", "available"]
AttendanceStatus = Literal["present", "absent", "late"]
CommentType = Literal["positive", "negative", "neutral"]

# ========== БАЗОВЫЕ МОДЕЛИ ==========

class QuestionResponse(BaseModel):
    """Модель вопроса для тестирования"""
    
    question_id: int
    text: str
    answer_1: Optional[str] = None
    answer_2: Optional[str] = None
    answer_3: Optional[str] = None
    answer_4: Optional[str] = None
    correct_answers: int = Field(..., ge=1, le=4)
    explanation: Optional[str] = None
    category: List[str] = Field(default_factory=list)
    topic_id: int
    
    class Config:
        from_attributes = True

class TestAttempt(BaseModel):
    """Модель попытки теста"""
    
    attempt_id: int
    score_percentage: float = Field(..., ge=0.0, le=100.0)
    correct_answers: float
    total_questions: int
    attempt_date: datetime
    time_spent: Optional[str] = None
    passed: bool = False
    
    class Config:
        from_attributes = True

class TestInfo(BaseModel):
    """Информация о тесте по теме"""
    
    topic_id: int
    topic_name: str
    section_id: int
    section_name: str
    subject_id: int
    subject_name: str
    block_id: Optional[int] = None
    block_name: Optional[str] = None
    
    # Статус теста
    status: TestStatus
    deadline: Optional[datetime] = None
    
    # Попытки
    training_attempts: List[TestAttempt] = Field(default_factory=list)
    
    # Метаданные
    questions_count: int = 0
    time_limit_minutes: Optional[int] = None
    max_attempts: int = Field(default=999)
    
    class Config:
        from_attributes = True

class TestSession(BaseModel):
    """Сессия тестирования"""
    
    session_id: str
    topic_id: int
    test_type: TestType
    questions: List[QuestionResponse]
    current_question: int = 0
    start_time: datetime
    end_time: Optional[datetime] = None
    time_limit_minutes: Optional[int] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True

class TestResult(BaseModel):
    """Результат теста"""
    
    session_id: str
    topic_id: int
    test_type: TestType
    score_percentage: float = Field(..., ge=0.0, le=100.0)
    correct_answers: int
    total_questions: int
    time_spent_seconds: int
    passed: bool
    answers: Dict[int, int] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True

# ========== СТАТИСТИКА ==========

class TestStatistics(BaseModel):
    """Статистика тестов студента"""
    
    student_id: int
    completed_tests: int = 0
    current_tests: int = 0
    overdue_tests: int = 0
    total_tests: int = 0
    
    # Средние показатели
    average_score: float = 0.0
    total_time_spent_hours: float = 0.0
    
    class Config:
        from_attributes = True

class TestCounts(BaseModel):
    """Счетчики тестов"""
    
    completed: int = 0
    current: int = 0
    overdue: int = 0
    available: int = 0
    
    class Config:
        from_attributes = True

# ========== ЗАПРОСЫ ==========

class CreateTestSessionRequest(BaseModel):
    """Запрос создания сессии тестирования"""
    
    topic_id: int = Field(..., gt=0)
    test_type: TestType = "training"
    questions_limit: int = Field(default=30, ge=5, le=50)
    
    class Config:
        from_attributes = True

class SubmitAnswerRequest(BaseModel):
    """Запрос отправки ответа"""
    
    session_id: str
    question_id: int = Field(..., gt=0)
    answer_choice: int = Field(..., ge=1, le=4)
    
    class Config:
        from_attributes = True

class FinishTestRequest(BaseModel):
    """Запрос завершения теста"""
    
    session_id: str
    answers: Dict[int, int] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True

# ========== ОТВЕТЫ API ==========

class TestsListResponse(BaseModel):
    """Ответ списка тестов"""
    
    tests: List[TestInfo]
    total_count: int
    statistics: TestStatistics
    test_counts: TestCounts
    
    class Config:
        from_attributes = True

class TestSessionResponse(BaseModel):
    """Ответ создания сессии"""
    
    session: TestSession
    current_question: QuestionResponse
    progress: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True

class TestResultResponse(BaseModel):
    """Ответ результата теста"""
    
    result: TestResult
    detailed_results: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

# ========== ОШИБКИ ==========

class TestErrorResponse(BaseModel):
    """Ошибка тестирования"""
    
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# ========== ЗДОРОВЬЕ СЕРВИСА ==========

class TestsHealthResponse(BaseModel):
    """Проверка здоровья сервиса тестов"""
    
    status: str = "healthy"
    service: str = "tests-api"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    active_sessions: int = 0
    
    class Config:
        from_attributes = True