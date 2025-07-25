// ========== КОНСТАНТЫ ==========

export const COMMENT_TYPES = {
  POSITIVE: 'positive',
  NEGATIVE: 'negative',
  NEUTRAL: 'neutral'
} as const;

export const ATTENDANCE_STATUS = {
  PRESENT: 'present',
  ABSENT: 'absent',
  LATE: 'late'
} as const;

export const STUDENT_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive'
} as const;

// ========== ТИПЫ ==========

export type CommentType = typeof COMMENT_TYPES[keyof typeof COMMENT_TYPES];
export type AttendanceStatus = typeof ATTENDANCE_STATUS[keyof typeof ATTENDANCE_STATUS];
export type StudentStatus = typeof STUDENT_STATUS[keyof typeof STUDENT_STATUS];

export interface StudentSkillAnalysis {
  correct_answers: number[];
  incorrect_answers: number[];
}

export interface StudentAttendanceInfo {
  total_lessons: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  attendance_rate: number;
  last_attendance_date?: string;
}

export interface StudentTestStatistics {
  total_tests: number;
  completed_tests: number;
  pending_tests: number;
  average_score: number;
  best_score: number;
  dtm_score?: number;
  last_test_date?: string;
}

export interface StudentCommentInfo {
  comment_id?: number;
  comment_text: string;
  comment_type: CommentType;
  last_updated?: string;
}

export interface StudentDetailInfo {
  id: number;
  name: string;
  photo?: string;
  email?: string;
  phone?: string;
  test_statistics: StudentTestStatistics;
  attendance_info: StudentAttendanceInfo;
  skill_analysis: StudentSkillAnalysis;
  comment_info: StudentCommentInfo;
  student_status: StudentStatus;
  last_seen?: string;
}

export interface GroupScheduleInfo {
  group_id: number;
  group_name: string;
  days: string[];
  start_time: string;
  student_count: number;
  subject_name: string;
}

export interface TeacherProfileInfo {
  teacher_id: number;
  name: string;
  surname: string;
  email?: string;
  phone?: string;
  photo?: string;
  education_background?: string;
  years_experience?: number;
  certifications?: string;
  languages?: string;
  subjects: string[];
  schedule: GroupScheduleInfo[];
}

export interface TeacherDashboardResponse {
  teacher_profile: TeacherProfileInfo;
  groups: GroupScheduleInfo[];
  total_students: number;
}

export interface GroupStudentsResponse {
  group_id: number;
  group_name: string;
  students: StudentDetailInfo[];
  total_count: number;
}

export interface CriterionAnalysis {
  criterion_number: number;
  correct_count: number;
  incorrect_count: number;
  total_count: number;
  accuracy_percentage: number;
}

export interface StudentAnalyticsResponse {
  student_id: number;
  criteria_analysis: CriterionAnalysis[];
  overall_accuracy: number;
  total_questions: number;
  last_updated?: string;
}

export interface UpdateCommentRequest {
  student_id: number;
  comment_text: string;
  comment_type: CommentType;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface TeacherAPIError {
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

export class TeacherAPIError extends Error implements TeacherAPIError {
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
    this.name = 'TeacherAPIError';
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
    if (retries > 0 && error instanceof TeacherAPIError && ![404, 400].includes(error.status || 0)) {
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
      
      throw new TeacherAPIError(errorMessage, response.status, undefined, details);
    }

    try {
      if (contentType?.includes('application/json')) {
        return await response.json();
      } else {
        const text = await response.text();
        return text as unknown as T;
      }
    } catch (error) {
      throw new TeacherAPIError('Некорректный формат ответа от сервера');
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
        throw new TeacherAPIError('Превышено время ожидания запроса', 408);
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
        throw new TeacherAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }
}

// ========== TEACHER API ==========

export class TeacherAPI {
  private client: HTTPClient;

  constructor(baseURL?: string) {
    this.client = new HTTPClient(`${baseURL || API_CONFIG.baseURL}/teacher`);
  }

  // Получение профиля преподавателя
  async getTeacherProfile(teacherId: number): Promise<TeacherDashboardResponse> {
    if (!teacherId || teacherId <= 0) {
      throw new TeacherAPIError('Корректный ID преподавателя обязателен');
    }

    return retryRequest(async () => {
      return await this.client.get<TeacherDashboardResponse>(`/profile/${teacherId}`);
    });
  }

  // Получение студентов группы
  async getGroupStudents(
    groupId: number,
    options?: {
      include_inactive?: boolean;
      sort_by?: 'name' | 'score' | 'attendance' | 'last_seen';
      sort_order?: 'asc' | 'desc';
    }
  ): Promise<GroupStudentsResponse> {
    if (!groupId || groupId <= 0) {
      throw new TeacherAPIError('Корректный ID группы обязателен');
    }

    const params: Record<string, string | number | boolean> = {};
    
    if (options?.include_inactive !== undefined) {
      params.include_inactive = options.include_inactive;
    }
    if (options?.sort_by) {
      params.sort_by = options.sort_by;
    }
    if (options?.sort_order) {
      params.sort_order = options.sort_order;
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<GroupStudentsResponse>(`/group/${groupId}/students`, params);
      } catch (error) {
        if (error instanceof TeacherAPIError && error.status === 404) {
          return {
            group_id: groupId,
            group_name: '',
            students: [],
            total_count: 0
          };
        }
        throw error;
      }
    });
  }

  // Обновление комментария студента
  async updateStudentComment(
    teacherId: number,
    request: UpdateCommentRequest
  ): Promise<{ status: string; message: string }> {
    if (!teacherId || teacherId <= 0) {
      throw new TeacherAPIError('Корректный ID преподавателя обязателен');
    }

    if (!request.student_id || request.student_id <= 0) {
      throw new TeacherAPIError('Корректный ID студента обязателен');
    }

    if (!request.comment_text.trim()) {
      throw new TeacherAPIError('Текст комментария не может быть пустым');
    }

    return retryRequest(async () => {
      return await this.client.post(`/student/comment?teacher_id=${teacherId}`, request);
    });
  }

  // Получение аналитики студента
  async getStudentAnalytics(studentId: number): Promise<StudentAnalyticsResponse> {
    if (!studentId || studentId <= 0) {
      throw new TeacherAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<StudentAnalyticsResponse>(`/student/${studentId}/analytics`);
      } catch (error) {
        if (error instanceof TeacherAPIError && error.status === 404) {
          return {
            student_id: studentId,
            criteria_analysis: Array.from({ length: 8 }, (_, i) => ({
              criterion_number: i + 1,
              correct_count: 0,
              incorrect_count: 0,
              total_count: 0,
              accuracy_percentage: 0
            })),
            overall_accuracy: 0,
            total_questions: 0,
            last_updated: new Date().toISOString()
          };
        }
        throw error;
      }
    });
  }

  // Проверка здоровья API
  async healthCheck(): Promise<{
    status: string;
    service: string;
    version: string;
    timestamp: string;
    active_teachers: number;
    total_groups: number;
  }> {
    try {
      return await this.client.get('/health');
    } catch (error) {
      throw new TeacherAPIError('Сервис преподавателя недоступен');
    }
  }

  // Утилиты
  getCommentTypeDisplayName(type: CommentType): string {
    switch (type) {
      case COMMENT_TYPES.POSITIVE:
        return 'Положительный';
      case COMMENT_TYPES.NEGATIVE:
        return 'Отрицательный';
      case COMMENT_TYPES.NEUTRAL:
        return 'Нейтральный';
      default:
        return type;
    }
  }

  getStudentStatusDisplayName(status: StudentStatus): string {
    switch (status) {
      case STUDENT_STATUS.ACTIVE:
        return 'Активный';
      case STUDENT_STATUS.INACTIVE:
        return 'Неактивный';
      default:
        return status;
    }
  }

  formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}ч ${minutes}м ${secs}с`;
    } else if (minutes > 0) {
      return `${minutes}м ${secs}с`;
    } else {
      return `${secs}с`;
    }
  };

  formatLastSeen = (lastSeen?: string): string => {
    if (!lastSeen) return 'Никогда';

    const now = new Date();
    const lastSeenDate = new Date(lastSeen);
    const diffInMs = now.getTime() - lastSeenDate.getTime();
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) return 'Сегодня';
    if (diffInDays === 1) return '1 день назад';
    if (diffInDays < 7) return `${diffInDays} дня назад`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} недель назад`;
    
    return `${Math.floor(diffInDays / 30)} месяцев назад`;
  };

  getScoreColor = (score: number): string => {
    if (score >= 8.5) return 'text-green-600';
    if (score >= 7.0) return 'text-yellow-600';
    if (score >= 5.0) return 'text-orange-600';
    return 'text-red-600';
  };

  getAttendanceColor = (rate: number): string => {
    if (rate >= 0.9) return 'text-green-600';
    if (rate >= 0.7) return 'text-yellow-600';
    if (rate >= 0.5) return 'text-orange-600';
    return 'text-red-600';
  };

  getCriterionAccuracy = (analysis: StudentSkillAnalysis, criterionIndex: number): number => {
    if (criterionIndex < 0 || criterionIndex >= 8) return 0;
    
    const correct = analysis.correct_answers[criterionIndex] || 0;
    const incorrect = analysis.incorrect_answers[criterionIndex] || 0;
    const total = correct + incorrect;
    
    return total > 0 ? (correct / total) * 100 : 0;
  };

  getTotalAccuracy = (analysis: StudentSkillAnalysis): number => {
    const totalCorrect = analysis.correct_answers.reduce((sum, val) => sum + val, 0);
    const totalIncorrect = analysis.incorrect_answers.reduce((sum, val) => sum + val, 0);
    const total = totalCorrect + totalIncorrect;
    
    return total > 0 ? (totalCorrect / total) * 100 : 0;
  };

  generateCriterionChartData = (analysis: StudentSkillAnalysis) => {
    return Array.from({ length: 8 }, (_, i) => ({
      criterion: `Критерий ${i + 1}`,
      correct: analysis.correct_answers[i] || 0,
      incorrect: analysis.incorrect_answers[i] || 0,
      accuracy: this.getCriterionAccuracy(analysis, i)
    }));
  };
}

// ========== ЭКЗЕМПЛЯР API ==========

export const teacherAPI = new TeacherAPI();
export default teacherAPI;