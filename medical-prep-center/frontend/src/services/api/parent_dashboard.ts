// ========== КОНСТАНТЫ ==========

export const PERFORMANCE_STATUSES = {
  EXCELLENT: 'отлично',
  GOOD: 'хорошо', 
  SATISFACTORY: 'удовлетворительно',
  POOR: 'плохо'
} as const;

export const COMMENT_TYPES = {
  POSITIVE: 'positive',
  NEGATIVE: 'negative',
  NEUTRAL: 'neutral'
} as const;

export const ATTENDANCE_STATUSES = {
  PRESENT: 'present',
  ABSENT: 'absent',
  LATE: 'late'
} as const;

export const NOTIFICATION_TYPES = {
  WARNING: 'warning',
  INFO: 'info',
  SUCCESS: 'success',
  ERROR: 'error'
} as const;

// ========== ТИПЫ ==========

export type PerformanceStatus = typeof PERFORMANCE_STATUSES[keyof typeof PERFORMANCE_STATUSES];
export type CommentType = typeof COMMENT_TYPES[keyof typeof COMMENT_TYPES];
export type AttendanceStatus = typeof ATTENDANCE_STATUSES[keyof typeof ATTENDANCE_STATUSES];
export type NotificationType = typeof NOTIFICATION_TYPES[keyof typeof NOTIFICATION_TYPES];

export interface StudentInfo {
  student_id: number;
  name: string;
  surname: string;
  photo?: string;
  direction: string;
  goal?: string;
  group_id?: number;
  hobby?: string;
  sex?: string;
  address?: string;
  birthday?: string;
}

export interface ScheduleItem {
  subject_name: string;
  days: string[];
  time: string;
  teacher_name?: string;
}

export interface StudentSchedule {
  student_id: number;
  chemistry_schedule?: ScheduleItem;
  biology_schedule?: ScheduleItem;
}

export interface DtmScore {
  current_score: number;
  max_score: number;
  required_score: number;
  exam_date?: string;
}

export interface SubjectGrades {
  subject_name: string;
  average_score: number;
  total_assessments: number;
  passed_assessments: number;
  failed_assessments: number;
  status: PerformanceStatus;
  
  // Детализация по типам
  polls_score: number;
  tests_score: number;
  control_works_score: number;
  polls_total: number;
  tests_total: number;
  control_works_total: number;
}

export interface DisciplineStatistics {
  student_id: number;
  total_absences: number;
  total_lessons: number;
  missed_homeworks: number;
  total_homeworks: number;
  missed_polls: number;
  total_polls: number;
  teacher_remarks: number;
  status: PerformanceStatus;
}

export interface GradeRecord {
  score: number;
  max_score: number;
  percentage: number;
  exam_date: string;
  exam_type: string;
  subject_name: string;
}

export interface ExamStatistics {
  student_id: number;
  last_monthly_exam?: GradeRecord;
  last_final_control?: GradeRecord;
  last_intermediate_control?: GradeRecord;
  total_exams: number;
  passed_exams: number;
  average_score: number;
  status: PerformanceStatus;
}

export interface AdmissionChance {
  student_id: number;
  probability_percentage: number;
  target_university?: string;
  current_score: number;
  required_score: number;
  recommendations: string[];
}

export interface CommentRecord {
  comment_id: number;
  teacher_id: number;
  student_id: number;
  comment_text: string;
  comment_date: string;
  comment_type: CommentType;
}

export interface AttendanceRecord {
  attendance_id: number;
  student_id: number;
  lesson_date_time: string;
  att_status: AttendanceStatus;
  subject_id: number;
  topic_id: number;
  excuse_reason?: string;
  extra_lesson?: string;
}

export interface ParentStatisticsData {
  student_info: StudentInfo;
  schedule: StudentSchedule;
  dtm_score: DtmScore;
  performance: Record<string, SubjectGrades>;
  overall_performance_status: PerformanceStatus;
  discipline: DisciplineStatistics;
  exams: ExamStatistics;
  admission_chance: AdmissionChance;
  recent_comments: CommentRecord[];
}

export interface DetailedPerformanceData {
  student_id: number;
  subjects: SubjectGrades[];
  recent_grades: GradeRecord[];
  grade_trends: Record<string, number[]>;
}

export interface DetailedDisciplineData {
  student_id: number;
  attendance_records: AttendanceRecord[];
  attendance_statistics: {
    student_id: number;
    subject_id?: number;
    total_lessons: number;
    present_count: number;
    absent_count: number;
    late_count: number;
    attendance_rate: number;
  };
  missed_assignments: Array<{
    assignment_id: number;
    subject_name: string;
    topic_name: string;
    due_date: string;
    type: string;
  }>;
  teacher_comments: CommentRecord[];
}

export interface DetailedExamsData {
  student_id: number;
  dtm_exams: GradeRecord[];
  section_exams: GradeRecord[];
  block_exams: GradeRecord[];
  module_exams: GradeRecord[];
  exam_trends: Record<string, number[]>;
}

export interface NotificationItem {
  notification_id: string;
  type: NotificationType;
  title: string;
  message: string;
  created_at: string;
  is_read: boolean;
  priority: 'low' | 'medium' | 'high';
}

export interface ParentNotificationsData {
  student_id: number;
  notifications: NotificationItem[];
  unread_count: number;
}

export interface RecommendationItem {
  category: string;
  priority: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  actions: string[];
}

export interface RecommendationsData {
  student_id: number;
  recommendations: RecommendationItem[];
  generated_at: string;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface APIErrorInterface {
  status?: number;
  code?: string;
  message: string;
}

// ========== КОНФИГУРАЦИЯ ==========

const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    const envVar = (window as any).env?.REACT_APP_API_URL;
    if (envVar) return envVar;
  }
  return 'http://localhost:8000/api';
};

const API_CONFIG = {
  baseURL: getApiBaseUrl(),
  timeout: 30000,
  retries: 2,
  retryDelay: 1000
};

// ========== ОШИБКИ ==========

export class ParentStatsAPIError extends Error implements APIErrorInterface {
  public status?: number;
  public code?: string;
  public details?: any;

  constructor(
    message: string,
    status?: number,
    code?: string,
    details?: any
  ) {
    super(message);
    this.name = 'ParentStatsAPIError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

// ========== УТИЛИТЫ ==========

const delay = (ms: number): Promise<void> => 
  new Promise(resolve => setTimeout(resolve, ms));

const retryRequest = async <T>(
  fn: () => Promise<T>,
  retries: number = API_CONFIG.retries,
  retryDelay: number = API_CONFIG.retryDelay
): Promise<T> => {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0 && error instanceof ParentStatsAPIError && ![404, 400].includes(error.status || 0)) {
      await delay(retryDelay);
      return retryRequest(fn, retries - 1, retryDelay * 1.5);
    }
    throw error;
  }
};

// ========== HTTP КЛИЕНТ ==========

class HTTPClient {
  private baseURL: string;
  private timeout: number;

  constructor(baseURL: string, timeout: number = API_CONFIG.timeout) {
    this.baseURL = baseURL;
    this.timeout = timeout;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let details = null;
      
      try {
        if (contentType?.includes('application/json')) {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
          details = errorData;
        } else {
          errorMessage = await response.text() || errorMessage;
        }
      } catch {
        // Игнорируем ошибки парсинга
      }
      
      throw new ParentStatsAPIError(errorMessage, response.status, undefined, details);
    }

    try {
      if (contentType?.includes('application/json')) {
        return await response.json();
      } else {
        const text = await response.text();
        return text as unknown as T;
      }
    } catch (error) {
      throw new ParentStatsAPIError('Некорректный формат ответа от сервера');
    }
  }

  private createAbortController(): AbortController {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    
    controller.signal.addEventListener('abort', () => clearTimeout(timeoutId));
    
    return controller;
  }

  async get<T>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<T> {
    const url = new URL(`${this.baseURL}${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const controller = this.createAbortController();

    try {
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        signal: controller.signal,
      });

      return this.handleResponse<T>(response);
    } catch (error: unknown) {
      if ((error as any)?.name === 'AbortError') {
        throw new ParentStatsAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    const controller = this.createAbortController();

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
      });

      return this.handleResponse<T>(response);
    } catch (error: unknown) {
      if ((error as any)?.name === 'AbortError') {
        throw new ParentStatsAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }
}

// ========== PARENT STATISTICS API ==========

export class ParentStatisticsAPI {
  private client: HTTPClient;

  constructor(baseURL?: string) {
    this.client = new HTTPClient(`${baseURL || API_CONFIG.baseURL}/parent-statistics`);
  }

  // Получение основной статистики студента
  async getStudentStatistics(
    studentId: number,
    options?: {
      include_comments?: boolean;
      comments_limit?: number;
    }
  ): Promise<ParentStatisticsData> {
    if (!studentId || studentId <= 0) {
      throw new ParentStatsAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number | boolean> = {};
    
    if (options?.include_comments !== undefined) {
      params.include_comments = options.include_comments;
    }
    if (options?.comments_limit && options.comments_limit > 0) {
      params.comments_limit = Math.min(options.comments_limit, 20);
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<ParentStatisticsData>(`/student/${studentId}`, params);
      } catch (error) {
        if (error instanceof ParentStatsAPIError && error.status === 404) {
          throw new ParentStatsAPIError('Студент не найден');
        }
        throw error;
      }
    });
  }

  // Получение детальной успеваемости
  async getDetailedPerformance(
    studentId: number,
    subjectId?: number
  ): Promise<DetailedPerformanceData> {
    if (!studentId || studentId <= 0) {
      throw new ParentStatsAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {};
    if (subjectId && subjectId > 0) {
      params.subject_id = subjectId;
    }

    return retryRequest(async () => {
      return await this.client.get<DetailedPerformanceData>(`/student/${studentId}/performance`, params);
    });
  }

  // Получение детальной дисциплины
  async getDetailedDiscipline(
    studentId: number,
    filters?: {
      subject_id?: number;
      start_date?: string;
      end_date?: string;
    }
  ): Promise<DetailedDisciplineData> {
    if (!studentId || studentId <= 0) {
      throw new ParentStatsAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {};
    
    if (filters?.subject_id && filters.subject_id > 0) {
      params.subject_id = filters.subject_id;
    }
    if (filters?.start_date) {
      params.start_date = filters.start_date;
    }
    if (filters?.end_date) {
      params.end_date = filters.end_date;
    }

    return retryRequest(async () => {
      return await this.client.get<DetailedDisciplineData>(`/student/${studentId}/discipline`, params);
    });
  }

  // Получение детальных экзаменов
  async getDetailedExams(
    studentId: number,
    filters?: {
      exam_type?: string;
      start_date?: string;
      end_date?: string;
    }
  ): Promise<DetailedExamsData> {
    if (!studentId || studentId <= 0) {
      throw new ParentStatsAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {};
    
    if (filters?.exam_type) {
      params.exam_type = filters.exam_type;
    }
    if (filters?.start_date) {
      params.start_date = filters.start_date;
    }
    if (filters?.end_date) {
      params.end_date = filters.end_date;
    }

    return retryRequest(async () => {
      return await this.client.get<DetailedExamsData>(`/student/${studentId}/exams`, params);
    });
  }

  // Получение уведомлений
  async getNotifications(
    studentId: number,
    options?: {
      limit?: number;
      unread_only?: boolean;
    }
  ): Promise<ParentNotificationsData> {
    if (!studentId || studentId <= 0) {
      throw new ParentStatsAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number | boolean> = {};
    
    if (options?.limit && options.limit > 0) {
      params.limit = Math.min(options.limit, 50);
    }
    if (options?.unread_only) {
      params.unread_only = options.unread_only;
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<ParentNotificationsData>(`/student/${studentId}/notifications`, params);
      } catch (error) {
        if (error instanceof ParentStatsAPIError && error.status === 404) {
          return {
            student_id: studentId,
            notifications: [],
            unread_count: 0
          };
        }
        throw error;
      }
    });
  }

  // Получение рекомендаций
  async getRecommendations(studentId: number): Promise<RecommendationsData> {
    if (!studentId || studentId <= 0) {
      throw new ParentStatsAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      return await this.client.get<RecommendationsData>(`/student/${studentId}/recommendations`);
    });
  }

  // Проверка здоровья API
  async healthCheck(): Promise<{
    status: string;
    service: string;
    version: string;
    timestamp: string;
    active_students: number;
  }> {
    try {
      return await this.client.get('/health');
    } catch (error) {
      throw new ParentStatsAPIError('Сервис родительской статистики недоступен');
    }
  }

  // ========== УТИЛИТЫ ==========

  // Получение цвета статуса
  getStatusColor(status: PerformanceStatus): string {
    switch (status) {
      case PERFORMANCE_STATUSES.EXCELLENT:
        return 'text-success-600 bg-success-100';
      case PERFORMANCE_STATUSES.GOOD:
        return 'text-warning-600 bg-warning-100';
      case PERFORMANCE_STATUSES.SATISFACTORY:
        return 'text-neutral-600 bg-neutral-100';
      case PERFORMANCE_STATUSES.POOR:
        return 'text-error-600 bg-error-100';
      default:
        return 'text-neutral-600 bg-neutral-100';
    }
  }

  // Получение отображаемого названия статуса
  getStatusDisplayName(status: PerformanceStatus): string {
    return status;
  }

  // Получение цвета для типа комментария
  getCommentTypeColor(type: CommentType): string {
    switch (type) {
      case COMMENT_TYPES.POSITIVE:
        return 'text-success-600';
      case COMMENT_TYPES.NEGATIVE:
        return 'text-error-600';
      case COMMENT_TYPES.NEUTRAL:
        return 'text-neutral-600';
      default:
        return 'text-neutral-600';
    }
  }

  // Получение цвета для уведомлений
  getNotificationColor(type: NotificationType): string {
    switch (type) {
      case NOTIFICATION_TYPES.SUCCESS:
        return 'bg-success-100 border-success-200 text-success-800';
      case NOTIFICATION_TYPES.WARNING:
        return 'bg-warning-100 border-warning-200 text-warning-800';
      case NOTIFICATION_TYPES.ERROR:
        return 'bg-error-100 border-error-200 text-error-800';
      case NOTIFICATION_TYPES.INFO:
        return 'bg-primary-100 border-primary-200 text-primary-800';
      default:
        return 'bg-neutral-100 border-neutral-200 text-neutral-800';
    }
  }

  // Форматирование даты
  formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Форматирование времени
  formatTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Форматирование даты и времени
  formatDateTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Форматирование расписания
  formatSchedule = (schedule: ScheduleItem): string => {
    const days = schedule.days.join(', ');
    return `${days} - ${schedule.time}`;
  };

  // Форматирование DTM балла
  formatDtmScore = (score: DtmScore): string => {
    return `${score.current_score}/${score.max_score}`;
  };

  // Проверка, сдан ли DTM
  isDtmPassing = (score: DtmScore): boolean => {
    return score.current_score >= score.required_score;
  };

  // Расчет процента посещаемости
  calculateAttendancePercentage = (discipline: DisciplineStatistics): number => {
    if (discipline.total_lessons === 0) return 0;
    const attended = discipline.total_lessons - discipline.total_absences;
    return Math.round((attended / discipline.total_lessons) * 100);
  };

  // Расчет процента выполнения домашних заданий
  calculateHomeworkPercentage = (discipline: DisciplineStatistics): number => {
    if (discipline.total_homeworks === 0) return 100;
    const completed = discipline.total_homeworks - discipline.missed_homeworks;
    return Math.round((completed / discipline.total_homeworks) * 100);
  };

  // Получение текста для шанса поступления
  getAdmissionChanceText = (percentage: number): string => {
    if (percentage >= 80) return 'Высокий шанс';
    if (percentage >= 60) return 'Средний шанс';
    if (percentage >= 40) return 'Низкий шанс';
    return 'Очень низкий шанс';
  };

  // Получение цвета для шанса поступления
  getAdmissionChanceColor = (percentage: number): string => {
    if (percentage >= 80) return 'text-success-600';
    if (percentage >= 60) return 'text-warning-600';
    if (percentage >= 40) return 'text-orange-600';
    return 'text-error-600';
  };

  // Получение приоритета рекомендации
  getRecommendationPriorityColor = (priority: 'low' | 'medium' | 'high'): string => {
    switch (priority) {
      case 'high':
        return 'border-l-error-500 bg-error-50';
      case 'medium':
        return 'border-l-warning-500 bg-warning-50';
      case 'low':
        return 'border-l-success-500 bg-success-50';
      default:
        return 'border-l-neutral-500 bg-neutral-50';
    }
  };

  // Получение инициалов для аватара
  getInitials = (name: string, surname: string): string => {
    return `${name.charAt(0)}${surname.charAt(0)}`.toUpperCase();
  };

  // Проверка, является ли оценка проходной
  isGradePassing = (grade: GradeRecord): boolean => {
    return grade.percentage >= 60;
  };

  // Получение цвета для оценки
  getGradeColor = (percentage: number): string => {
    if (percentage >= 85) return 'text-success-600';
    if (percentage >= 70) return 'text-warning-600';
    if (percentage >= 60) return 'text-orange-600';
    return 'text-error-600';
  };

  // Получение относительного времени
  getRelativeTime = (dateString: string): string => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInMinutes < 1) return 'только что';
    if (diffInMinutes < 60) return `${diffInMinutes} мин назад`;
    if (diffInHours < 24) return `${diffInHours} ч назад`;
    if (diffInDays < 7) return `${diffInDays} дн назад`;
    
    return this.formatDate(dateString);
  };

  // Группировка уведомлений по типу
  groupNotificationsByType = (notifications: NotificationItem[]): Record<NotificationType, NotificationItem[]> => {
    const grouped: Record<string, NotificationItem[]> = {};
    
    Object.values(NOTIFICATION_TYPES).forEach(type => {
      grouped[type] = [];
    });

    notifications.forEach(notification => {
      if (grouped[notification.type]) {
        grouped[notification.type].push(notification);
      }
    });

    return grouped as Record<NotificationType, NotificationItem[]>;
  };

  // Сортировка рекомендаций по приоритету
  sortRecommendationsByPriority = (recommendations: RecommendationItem[]): RecommendationItem[] => {
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    
    return [...recommendations].sort((a, b) => {
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  };

  // Получение тренда оценок
  getGradeTrend = (grades: number[]): 'up' | 'down' | 'stable' => {
    if (grades.length < 2) return 'stable';
    
    const recent = grades.slice(-3);
    const first = recent[0];
    const last = recent[recent.length - 1];
    
    if (last > first + 0.5) return 'up';
    if (last < first - 0.5) return 'down';
    return 'stable';
  };

  // Получение цвета тренда
  getTrendColor = (trend: 'up' | 'down' | 'stable'): string => {
    switch (trend) {
      case 'up':
        return 'text-success-600';
      case 'down':
        return 'text-error-600';
      case 'stable':
        return 'text-neutral-600';
      default:
        return 'text-neutral-600';
    }
  };
}

// ========== ЭКЗЕМПЛЯР API ==========

export const parentStatsAPI = new ParentStatisticsAPI();
export default parentStatsAPI;