# app/schemas/extended.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.schemas.base import BaseResponse

# ===== DASHBOARD SCHEMAS =====

class StudentDashboardResponse(BaseResponse):
    student_info: Dict[str, Any]
    statistics: Dict[str, Any]
    recent_tests: List[Dict[str, Any]]
    module_progress: List[Dict[str, Any]]
    upcoming_tasks: List[Dict[str, Any]]

class TeacherDashboardResponse(BaseResponse):
    teacher_info: Dict[str, Any]
    statistics: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    groups_statistics: List[Dict[str, Any]]

class AdminDashboardResponse(BaseResponse):
    system_statistics: Dict[str, Any]
    users_statistics: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]

class ParentDashboardResponse(BaseResponse):
    student_info: Dict[str, Any]
    performance: Dict[str, Any]
    discipline: Dict[str, Any]
    exams: Dict[str, Any]
    dtm_progress: Dict[str, Any]
    university_admission_chance: int
    schedule: Dict[str, str]

# ===== MATERIALS SCHEMAS =====

class UpdateHomeworkRequest(BaseModel):
    homework: List[str]

class AddVideoLessonRequest(BaseModel):
    topic_id: int
    video_url: str
    title: Optional[str] = None

class UpdateVideoLessonRequest(BaseModel):
    video_url: str
    title: Optional[str] = None

class AddSectionMaterialsRequest(BaseModel):
    links: List[str]
    description: Optional[str] = None

class MaterialFileResponse(BaseResponse):
    file_id: str
    original_name: str
    size: int
    category: str
    module_id: Optional[int]
    topic_id: Optional[int]
    uploaded_by: int
    upload_date: datetime
    download_url: str

# ===== SUBJECT MANAGEMENT SCHEMAS =====

class SubjectBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None

class CreateSubjectRequest(SubjectBase):
    pass

class UpdateSubjectRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None

class SubjectResponse(SubjectBase, BaseResponse):
    subject_id: int

class SubjectDetailResponse(BaseResponse):
    subject: SubjectResponse
    sections: List[Any]  # SectionResponse list
    sections_count: int

# ===== SECTION SCHEMAS =====

class SectionBase(BaseModel):
    name: str = Field(..., max_length=200)
    order_number: Optional[int] = None

class CreateSectionRequest(SectionBase):
    pass

class UpdateSectionRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    order_number: Optional[int] = None

class SectionResponse(SectionBase, BaseResponse):
    section_id: int
    subject_id: int

class SectionDetailResponse(BaseResponse):
    section: SectionResponse
    blocks: List[Any]  # BlockResponse list
    blocks_count: int

# ===== MODULE SCHEMAS =====

class ModuleBase(BaseModel):
    start_topic_chem: int
    start_topic_bio: int
    end_topic_chem: int
    end_topic_bio: int
    order_number: Optional[int] = None
    name: Optional[str] = None

class CreateModuleRequest(ModuleBase):
    pass

class UpdateModuleRequest(BaseModel):
    start_topic_chem: Optional[int] = None
    start_topic_bio: Optional[int] = None
    end_topic_chem: Optional[int] = None
    end_topic_bio: Optional[int] = None
    order_number: Optional[int] = None
    name: Optional[str] = None

class ModuleResponse(ModuleBase, BaseResponse):
    modul_id: int

class ModuleDetailResponse(BaseResponse):
    module: ModuleResponse
    topics_chemistry_range: str
    topics_biology_range: str

# ===== QUESTION SCHEMAS =====

class QuestionBase(BaseModel):
    text: str
    answer_1: str = Field(..., max_length=500)
    answer_2: str = Field(..., max_length=500)
    answer_3: str = Field(..., max_length=500)
    answer_4: str = Field(..., max_length=500)
    correct_answers: int = Field(..., ge=1, le=4)
    explanation: Optional[str] = None
    category: Optional[List[str]] = []

class CreateQuestionRequest(QuestionBase):
    pass

class UpdateQuestionRequest(BaseModel):
    text: Optional[str] = None
    answer_1: Optional[str] = Field(None, max_length=500)
    answer_2: Optional[str] = Field(None, max_length=500)
    answer_3: Optional[str] = Field(None, max_length=500)
    answer_4: Optional[str] = Field(None, max_length=500)
    correct_answers: Optional[int] = Field(None, ge=1, le=4)
    explanation: Optional[str] = None
    category: Optional[List[str]] = None

class QuestionResponse(QuestionBase, BaseResponse):
    question_id: int
    topic_id: int

class QuestionDetailResponse(BaseResponse):
    question: QuestionResponse
    options: List[Dict[str, str]]
    correct_option: str

class BulkImportQuestionsRequest(BaseModel):
    questions: List[Dict[str, Any]]

class BulkUpdateCategoriesRequest(BaseModel):
    updates: Dict[str, List[str]]  # question_id -> categories

# ===== ADMIN SCHEMAS =====

class AdminBase(BaseModel):
    schedule: Optional[str] = None

class AdminResponse(AdminBase, BaseResponse):
    admin_id: int
    admin_status: str

class AdminInfoBase(BaseModel):
    admin_number: Optional[str] = Field(None, max_length=14)
    employment: Optional[str] = Field(None, max_length=100)
    admin_hobby: Optional[str] = Field(None, max_length=100)

class AdminInfoResponse(AdminInfoBase, BaseResponse):
    admin_id: int

class AdminProfileResponse(BaseResponse):
    admin: AdminResponse
    admin_info: Optional[AdminInfoResponse]

# ===== PARENT SPECIFIC SCHEMAS =====

class ParentRecommendationSection(BaseModel):
    id: str
    name: str
    status: str
    data: Dict[str, str]

class ParentRecommendationsResponse(BaseResponse):
    sections: List[ParentRecommendationSection]
    summary: str

class ParentDetailedStatsResponse(BaseResponse):
    currentStudent: Dict[str, Any]
    grades: Dict[str, Dict[str, List[Dict[str, Any]]]]
    allStudents: List[Dict[str, Any]]

class ParentSubjectDetailsResponse(BaseResponse):
    attendance: Dict[str, Any]
    performance: Dict[str, Any]
    final_grades: Dict[str, float]

# ===== STATISTICS SCHEMAS =====

class AttendanceStatistics(BaseModel):
    total_lessons: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_rate: float

class PerformanceStatistics(BaseModel):
    chemistry_average: float
    biology_average: float
    overall_average: float
    test_scores: List[float]
    monthly_progress: List[Dict[str, Any]]

class StudentStatisticsResponse(BaseResponse):
    attendance: AttendanceStatistics
    performance: PerformanceStatistics
    ranking: Dict[str, int]
    dtm_progress: Dict[str, float]

# ===== NOTIFICATION SCHEMAS =====

class NotificationBase(BaseModel):
    type: str
    title: str
    message: str
    action_url: Optional[str] = None

class NotificationResponse(NotificationBase, BaseResponse):
    id: int
    is_read: bool
    created_at: datetime

class NotificationsResponse(BaseResponse):
    notifications: List[NotificationResponse]
    unread_count: int

# ===== QUICK ACTIONS SCHEMAS =====

class QuickAction(BaseModel):
    id: str
    title: str
    icon: str
    url: str
    color: str

class QuickActionsResponse(BaseResponse):
    actions: List[QuickAction]

# ===== SEARCH SCHEMAS =====

class SearchResult(BaseModel):
    id: int
    title: str
    type: str
    description: str
    url: str

class SearchResponse(BaseResponse):
    query: str
    results: List[SearchResult]
    total_found: int

# ===== ERROR SCHEMAS =====

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str
    errors: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ===== PAGINATION SCHEMAS =====

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

# ===== FILE UPLOAD SCHEMAS =====

class FileUploadResponse(BaseResponse):
    file_id: str
    filename: str
    size: int
    download_url: str
    upload_date: datetime

class BulkFileUploadResponse(BaseResponse):
    uploaded_files: List[FileUploadResponse]
    failed_uploads: List[Dict[str, str]]
    total_uploaded: int
    total_failed: int