// ========== КОНСТАНТЫ ==========

export const ATTENDANCE_STATUSES = {
  PRESENT: 'present',
  ABSENT: 'absent',
  LATE: 'late',
  EXAM: 'exam',
  HOLIDAY: 'holiday',
  FUTURE: 'future'
} as const;

export const COMMENT_TYPES = {
  POSITIVE: 'positive',
  NEGATIVE: 'negative', 
  NEUTRAL: 'neutral'
} as const;

export const SUBJECTS = {
  CHEMISTRY: 'chemistry',
  BIOLOGY: 'biology'
} as const;

// ========== ТИПЫ ==========

export type AttendanceStatus = typeof ATTENDANCE_STATUSES[keyof typeof ATTENDANCE_STATUSES];
export type CommentType = typeof COMMENT_TYPES[keyof typeof COMMENT_TYPES];
export type Subject = typeof SUBJECTS[keyof typeof SUBJECTS];

export interface AttendanceRecord {
  attendance_id: number;
  student_id: number;
  lesson_date_time: string;
  att_status: AttendanceStatus;
  subject_id: number;
  topic_id: number;
  excuse_reason?: string;
  extra_lesson?: string;
  topic_name?: string;
  subject_name?: string;
}

export interface AttendanceDay {
  date: number;
  status: AttendanceStatus;
  lesson: string;
  topic_id?: number;
  attendance_id?: number;
}

export interface AttendanceMonth {
  name: string;
  year: number;
  month: number;
  days: AttendanceDay[];
}

export interface AttendanceCalendar {
  student_id: number;
  subject_id: number;
  months: AttendanceMonth[];
}

export interface AttendanceStatistics {
  student_id: number;
  subject_id?: number;
  total_lessons: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  attendance_rate: number;
}

export interface PerformanceTopic {
  number: number;
  topic_id: number;
  topic_name: string;
  listened: boolean;
  first_try?: number;
  second_try?: number;
  average: number;
}

export interface ModulePerformance {
  module_id: number;
  module_name: string;
  topics: PerformanceTopic[];
  average_grade: number;
}

export interface Comment {
  comment_id: number;
  teacher_id: number;
  student_id: number;
  comment_text: string;
  comment_date: string;
  comment_type: CommentType;
  teacher_name?: string;
  teacher_surname?: string;
}

export interface FinalGrade {
  student_id: number;
  subject_id: number;
  section_average: number;
  block_average: number;
  current_average: number;
  topic_average: number;
  final_grade: number;
  counts: {
    section_exams: number;
    block_exams: number;
    current_ratings: number;
    topic_tests: number;
  };
}

export interface StudentDetails {
  student_id: number;
  student_name: string;
  student_surname: string;
  subjects_data: {
    [key: string]: {
      attendance: {
        records: AttendanceRecord[];
        statistics: AttendanceStatistics;
      };
      performance: {
        [key: string]: {
          module_id: number;
          module_name: string;
          topics: PerformanceTopic[];
        };
      };
      final_grades: FinalGrade;
    };
  };
}

export interface StudentStatistics {
  student_id: number;
  attendance_stats: { [key: string]: AttendanceStatistics };
  performance_stats: { [key: string]: FinalGrade };
  comments_count: { [key: string]: number };
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

export class AssessmentAPIError extends Error implements APIErrorInterface {
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
    this.name = 'AssessmentAPIError';
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
    if (retries > 0 && error instanceof AssessmentAPIError && ![404, 400].includes(error.status || 0)) {
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
      
      throw new AssessmentAPIError(errorMessage, response.status, undefined, details);
    }

    try {
      if (contentType?.includes('application/json')) {
        return await response.json();
      } else {
        const text = await response.text();
        return text as unknown as T;
      }
    } catch (error) {
      throw new AssessmentAPIError('Некорректный формат ответа от сервера');
    }
  }

  private createAbortController(): AbortController {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    
    controller.signal.addEventListener('abort', () => clearTimeout(timeoutId));
    
    return controller;
  }

  async get<T>(endpoint: string, params?: Record<string, string | number>): Promise<T> {
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
        throw new AssessmentAPIError('Превышено время ожидания запроса', 408);
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
        throw new AssessmentAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    const controller = this.createAbortController();

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'PUT',
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
        throw new AssessmentAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }

  async delete<T>(endpoint: string): Promise<T> {
    const controller = this.createAbortController();

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'DELETE',
        headers: {
          'Accept': 'application/json',
        },
        signal: controller.signal,
      });

      return this.handleResponse<T>(response);
    } catch (error: unknown) {
      if ((error as any)?.name === 'AbortError') {
        throw new AssessmentAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }
}

// ========== ASSESSMENT API ==========

export class AssessmentAPI {
  private client: HTTPClient;

  constructor(baseURL?: string) {
    this.client = new HTTPClient(`${baseURL || API_CONFIG.baseURL}/assessment`);
  }

  // Получение полной информации о студенте
  async getStudentDetails(studentId: number): Promise<StudentDetails> {
    if (!studentId || studentId <= 0) {
      throw new AssessmentAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<StudentDetails>(`/student/${studentId}/details`);
      } catch (error) {
        if (error instanceof AssessmentAPIError && error.status === 404) {
          throw new AssessmentAPIError('Студент не найден');
        }
        throw error;
      }
    });
  }

  // Получение календаря посещаемости
  async getAttendanceCalendar(
    studentId: number,
    subjectName: Subject,
    moduleId?: number
  ): Promise<AttendanceCalendar> {
    if (!studentId || studentId <= 0) {
      throw new AssessmentAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {
      subject_name: subjectName
    };

    if (moduleId) {
      params.module_id = moduleId;
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<AttendanceCalendar>(
          `/student/${studentId}/attendance/calendar`,
          params
        );
      } catch (error) {
        if (error instanceof AssessmentAPIError && error.status === 404) {
          return {
            student_id: studentId,
            subject_id: 0,
            months: []
          };
        }
        throw error;
      }
    });
  }

  // Получение успеваемости по модулям
  async getModulePerformance(
    studentId: number,
    subjectName: Subject,
    moduleId?: number
  ): Promise<ModulePerformance[]> {
    if (!studentId || studentId <= 0) {
      throw new AssessmentAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {
      subject_name: subjectName
    };

    if (moduleId) {
      params.module_id = moduleId;
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<ModulePerformance[]>(
          `/student/${studentId}/performance/module`,
          params
        );
      } catch (error) {
        if (error instanceof AssessmentAPIError && error.status === 404) {
          return [];
        }
        throw error;
      }
    });
  }

  // Получение итоговых оценок
  async getFinalGrades(studentId: number): Promise<{ [key: string]: FinalGrade }> {
    if (!studentId || studentId <= 0) {
      throw new AssessmentAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<{ [key: string]: FinalGrade }>(
          `/student/${studentId}/final-grades`
        );
      } catch (error) {
        if (error instanceof AssessmentAPIError && error.status === 404) {
          return {};
        }
        throw error;
      }
    });
  }

  // Получение комментариев студента
  async getStudentComments(
    studentId: number,
    options?: {
      comment_type?: CommentType;
      limit?: number;
    }
  ): Promise<Comment[]> {
    if (!studentId || studentId <= 0) {
      throw new AssessmentAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {};
    
    if (options?.comment_type) {
      params.comment_type = options.comment_type;
    }
    if (options?.limit && options.limit > 0) {
      params.limit = Math.min(options.limit, 200);
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<Comment[]>(`/student/${studentId}/comments`, params);
      } catch (error) {
        if (error instanceof AssessmentAPIError && error.status === 404) {
          return [];
        }
        throw error;
      }
    });
  }

  // Получение статистики студента
  async getStudentStatistics(studentId: number): Promise<StudentStatistics> {
    if (!studentId || studentId <= 0) {
      throw new AssessmentAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<StudentStatistics>(`/student/${studentId}/statistics`);
      } catch (error) {
        if (error instanceof AssessmentAPIError && error.status === 404) {
          return {
            student_id: studentId,
            attendance_stats: {},
            performance_stats: {},
            comments_count: { positive: 0, negative: 0, neutral: 0 }
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
    active_students?: number;
  }> {
    try {
      return await this.client.get('/health');
    } catch (error) {
      throw new AssessmentAPIError('Сервис оценок недоступен');
    }
  }

  // Утилиты
  getSubjectDisplayName(subject: Subject): string {
    switch (subject) {
      case SUBJECTS.CHEMISTRY:
        return 'Химия';
      case SUBJECTS.BIOLOGY:
        return 'Биология';
      default:
        return subject;
    }
  }

  getAttendanceStatusDisplayName(status: AttendanceStatus): string {
    switch (status) {
      case ATTENDANCE_STATUSES.PRESENT:
        return 'Присутствовал';
      case ATTENDANCE_STATUSES.ABSENT:
        return 'Отсутствовал';
      case ATTENDANCE_STATUSES.LATE:
        return 'Опоздал';
      case ATTENDANCE_STATUSES.EXAM:
        return 'Экзамен';
      case ATTENDANCE_STATUSES.HOLIDAY:
        return 'Выходной';
      case ATTENDANCE_STATUSES.FUTURE:
        return 'Будущее';
      default:
        return status;
    }
  }

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

  formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  formatDateTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  getGradeColor = (grade: number): string => {
    if (grade >= 9) return 'text-green-600';
    if (grade >= 7) return 'text-yellow-600';
    if (grade >= 5) return 'text-orange-600';
    return 'text-red-600';
  };

  getAttendanceRateColor = (rate: number): string => {
    if (rate >= 90) return 'text-green-600';
    if (rate >= 75) return 'text-yellow-600';
    if (rate >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  calculateAttendancePercentage = (statistics: AttendanceStatistics): number => {
    if (statistics.total_lessons === 0) return 0;
    return Math.round((statistics.present_count / statistics.total_lessons) * 100);
  };

  getModuleDisplayName = (moduleName: string, moduleId: number): string => {
    if (moduleName.toLowerCase().includes('модуль')) {
      return moduleName;
    }
    return `Модуль ${moduleId}`;
  };
}

// ========== ЭКЗЕМПЛЯР API ==========

export const assessmentAPI = new AssessmentAPI();
export default assessmentAPI;