// ========== КОНСТАНТЫ ==========

export const ATTENDANCE_STATUSES = {
  PRESENT: 'present',
  ABSENT: 'absent',
  LATE: 'late'
} as const;

export const COMMENT_TYPES = {
  POSITIVE: 'positive',
  NEGATIVE: 'negative',
  NEUTRAL: 'neutral'
} as const;

export const STUDENT_STATUSES = {
  ACTIVE: 'active',
  INACTIVE: 'inactive'
} as const;

export const SUBJECTS = {
  CHEMISTRY: 'chemistry',
  BIOLOGY: 'biology'
} as const;

// ========== ТИПЫ ==========

export type AttendanceStatus = typeof ATTENDANCE_STATUSES[keyof typeof ATTENDANCE_STATUSES];
export type CommentType = typeof COMMENT_TYPES[keyof typeof COMMENT_TYPES];
export type StudentStatus = typeof STUDENT_STATUSES[keyof typeof STUDENT_STATUSES];
export type Subject = typeof SUBJECTS[keyof typeof SUBJECTS];

export interface StudentInfo {
  student_id: number;
  name: string;
  surname: string;
  phone?: string;
  email?: string;
  photo?: string;
  direction?: string;
  goal?: string;
  group_id?: number;
  student_status: StudentStatus;
  last_login?: string;
  hobby?: string;
  sex?: string;
  address?: string;
  birthday?: string;
}

export interface University {
  university_id: number;
  name: string;
  type: string;
  entrance_score?: number;
  location: string;
  website_url?: string;
  logo_url?: string;
  contact_phone?: string;
  priority_order?: number;
}

export interface Faculty {
  faculty_id: number;
  name: string;
  annual_cost?: string;
  available_place?: string;
  description?: string;
  entrance_score?: number;
  code?: string;
}

export interface TestResult {
  test_id: number;
  test_type: string;
  topic_name: string;
  subject_name: string;
  score_percentage: number;
  correct_answers: number;
  total_questions: number;
  attempt_date: string;
  time_spent?: string;
  passed: boolean;
}

export interface AttendanceRecord {
  attendance_id: number;
  lesson_date_time: string;
  att_status: AttendanceStatus;
  topic_name?: string;
  subject_name: string;
  excuse_reason?: string;
  extra_lesson?: string;
}

export interface Comment {
  comment_id: number;
  teacher_name: string;
  comment_text: string;
  comment_date: string;
  comment_type: CommentType;
}

export interface ExamScore {
  exam_type: string;
  subject_name?: string;
  section_name?: string;
  block_name?: string;
  score: number;
  max_score?: number;
  exam_date: string;
  passed?: boolean;
}

export interface StudentStatistics {
  total_tests_completed: number;
  average_score: number;
  total_time_studied_hours: number;
  attendance_rate: number;
  total_lessons: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  subject_averages: Record<string, number>;
  completed_topics: number;
  total_topics: number;
  progress_percentage: number;
}

export interface StudentAnalytics {
  correct_by_category: Record<string, number>;
  mistakes_by_category: Record<string, number>;
  total_correct: number;
  total_mistakes: number;
  accuracy_percentage: number;
  weak_categories: string[];
  strong_categories: string[];
}

export interface StudentProgress {
  topic_id: number;
  topic_name: string;
  subject_name: string;
  section_name: string;
  block_name: string;
  is_completed: boolean;
  test_score?: number;
  attendance?: AttendanceStatus;
  last_activity?: string;
}

export interface StudentProfile {
  student_info: StudentInfo;
  universities: University[];
  recent_tests: TestResult[];
  attendance_summary: {
    attendance_rate: number;
    total_lessons: number;
    missed_lessons: number;
    late_arrivals: number;
  };
  recent_comments: Comment[];
  exam_scores: ExamScore[];
  statistics: StudentStatistics;
  analytics: StudentAnalytics;
  progress: StudentProgress[];
}

export interface TestsResponse {
  tests: TestResult[];
  total_count: number;
  average_score: number;
  passed_count: number;
  failed_count: number;
}

export interface AttendanceResponse {
  attendance_records: AttendanceRecord[];
  total_count: number;
  attendance_rate: number;
  present_count: number;
  absent_count: number;
  late_count: number;
}

export interface CommentsResponse {
  comments: Comment[];
  total_count: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
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

export class StudentProfileAPIError extends Error implements APIErrorInterface {
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
    this.name = 'StudentProfileAPIError';
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
    if (retries > 0 && error instanceof StudentProfileAPIError && ![404, 400].includes(error.status || 0)) {
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
      
      throw new StudentProfileAPIError(errorMessage, response.status, undefined, details);
    }

    try {
      if (contentType?.includes('application/json')) {
        return await response.json();
      } else {
        const text = await response.text();
        return text as unknown as T;
      }
    } catch (error) {
      throw new StudentProfileAPIError('Некорректный формат ответа от сервера');
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
        throw new StudentProfileAPIError('Превышено время ожидания запроса', 408);
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
        throw new StudentProfileAPIError('Превышено время ожидания запроса', 408);
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
        throw new StudentProfileAPIError('Превышено время ожидания запроса', 408);
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
        throw new StudentProfileAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }
}

// ========== STUDENT PROFILE API ==========

export class StudentProfileAPI {
  private client: HTTPClient;

  constructor(baseURL?: string) {
    this.client = new HTTPClient(`${baseURL || API_CONFIG.baseURL}/student/profile`);
  }

  // Получение полного профиля студента
  async getStudentProfile(studentId: number): Promise<StudentProfile> {
    if (!studentId || studentId <= 0) {
      throw new StudentProfileAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<StudentProfile>(`/${studentId}`);
      } catch (error) {
        if (error instanceof StudentProfileAPIError && error.status === 404) {
          throw new StudentProfileAPIError('Студент не найден');
        }
        throw error;
      }
    });
  }

  // Обновление информации о студенте
  async updateStudentInfo(
    studentId: number,
    data: {
      hobby?: string;
      sex?: string;
      address?: string;
      birthday?: string;
      goal?: string;
    }
  ): Promise<StudentInfo> {
    if (!studentId || studentId <= 0) {
      throw new StudentProfileAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      return await this.client.put<StudentInfo>(`/${studentId}/info`, data);
    });
  }

  // Получение тестов студента
  async getStudentTests(
    studentId: number,
    filters?: {
      subject_name?: Subject;
      test_type?: string;
      passed_only?: boolean;
      limit?: number;
    }
  ): Promise<TestsResponse> {
    if (!studentId || studentId <= 0) {
      throw new StudentProfileAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {};
    
    if (filters?.subject_name) {
      params.subject_name = filters.subject_name;
    }
    if (filters?.test_type) {
      params.test_type = filters.test_type;
    }
    if (filters?.passed_only !== undefined) {
      params.passed_only = filters.passed_only ? 'true' : 'false';
    }
    if (filters?.limit && filters.limit > 0) {
      params.limit = Math.min(filters.limit, 100);
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<TestsResponse>(`/${studentId}/tests`, params);
      } catch (error) {
        if (error instanceof StudentProfileAPIError && error.status === 404) {
          return {
            tests: [],
            total_count: 0,
            average_score: 0,
            passed_count: 0,
            failed_count: 0
          };
        }
        throw error;
      }
    });
  }

  // Получение посещаемости студента
  async getStudentAttendance(
    studentId: number,
    filters?: {
      subject_name?: Subject;
      limit?: number;
    }
  ): Promise<AttendanceResponse> {
    if (!studentId || studentId <= 0) {
      throw new StudentProfileAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {};
    
    if (filters?.subject_name) {
      params.subject_name = filters.subject_name;
    }
    if (filters?.limit && filters.limit > 0) {
      params.limit = Math.min(filters.limit, 200);
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<AttendanceResponse>(`/${studentId}/attendance`, params);
      } catch (error) {
        if (error instanceof StudentProfileAPIError && error.status === 404) {
          return {
            attendance_records: [],
            total_count: 0,
            attendance_rate: 0,
            present_count: 0,
            absent_count: 0,
            late_count: 0
          };
        }
        throw error;
      }
    });
  }

  // Получение комментариев о студенте
  async getStudentComments(
    studentId: number,
    filters?: {
      comment_type?: CommentType;
      limit?: number;
    }
  ): Promise<CommentsResponse> {
    if (!studentId || studentId <= 0) {
      throw new StudentProfileAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {};
    
    if (filters?.comment_type) {
      params.comment_type = filters.comment_type;
    }
    if (filters?.limit && filters.limit > 0) {
      params.limit = Math.min(filters.limit, 100);
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<CommentsResponse>(`/${studentId}/comments`, params);
      } catch (error) {
        if (error instanceof StudentProfileAPIError && error.status === 404) {
          return {
            comments: [],
            total_count: 0,
            positive_count: 0,
            negative_count: 0,
            neutral_count: 0
          };
        }
        throw error;
      }
    });
  }

  // Получение статистики студента
  async getStudentStatistics(studentId: number): Promise<StudentStatistics> {
    if (!studentId || studentId <= 0) {
      throw new StudentProfileAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      return await this.client.get<StudentStatistics>(`/${studentId}/statistics`);
    });
  }

  // Получение университетов студента
  async getStudentUniversities(studentId: number): Promise<University[]> {
    if (!studentId || studentId <= 0) {
      throw new StudentProfileAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<University[]>(`/${studentId}/universities`);
      } catch (error) {
        if (error instanceof StudentProfileAPIError && error.status === 404) {
          return [];
        }
        throw error;
      }
    });
  }

  // Добавление университета студенту
  async addUniversityToStudent(
    studentId: number,
    universityId: number,
    priorityOrder: number
  ): Promise<{ status: string; message: string }> {
    if (!studentId || studentId <= 0) {
      throw new StudentProfileAPIError('Корректный ID студента обязателен');
    }

    if (!universityId || universityId <= 0) {
      throw new StudentProfileAPIError('Корректный ID университета обязателен');
    }

    if (priorityOrder < 1 || priorityOrder > 10) {
      throw new StudentProfileAPIError('Приоритет должен быть от 1 до 10');
    }

    const data = {
      university_id: universityId,
      priority_order: priorityOrder
    };

    return retryRequest(async () => {
      return await this.client.post(`/${studentId}/universities`, data);
    });
  }

  // Удаление университета у студента
  async removeUniversityFromStudent(
    studentId: number,
    universityId: number
  ): Promise<{ status: string; message: string }> {
    if (!studentId || studentId <= 0) {
      throw new StudentProfileAPIError('Корректный ID студента обязателен');
    }

    if (!universityId || universityId <= 0) {
      throw new StudentProfileAPIError('Корректный ID университета обязателен');
    }

    return retryRequest(async () => {
      return await this.client.delete(`/${studentId}/universities/${universityId}`);
    });
  }

  // Обновление цели студента
  async updateStudentGoal(
    studentId: number,
    goal: string
  ): Promise<{ status: string; message: string }> {
    if (!studentId || studentId <= 0) {
      throw new StudentProfileAPIError('Корректный ID студента обязателен');
    }

    if (!goal || goal.trim().length === 0) {
      throw new StudentProfileAPIError('Цель не может быть пустой');
    }

    if (goal.length > 500) {
      throw new StudentProfileAPIError('Цель не может быть длиннее 500 символов');
    }

    const data = { goal: goal.trim() };

    return retryRequest(async () => {
      return await this.client.put(`/${studentId}/goal`, data);
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
      throw new StudentProfileAPIError('Сервис профиля студента недоступен');
    }
  }

  // Утилиты
  getAttendanceStatusDisplayName(status: AttendanceStatus): string {
    switch (status) {
      case ATTENDANCE_STATUSES.PRESENT:
        return 'Присутствовал';
      case ATTENDANCE_STATUSES.ABSENT:
        return 'Отсутствовал';
      case ATTENDANCE_STATUSES.LATE:
        return 'Опоздал';
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

  formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  formatDateShort = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  formatTime = (timeString?: string): string => {
    if (!timeString) return '0с';
    
    // Парсим время в формате "30s" или "1m 30s" и т.д.
    const timeMatch = timeString.match(/(\d+)([smh])/g);
    if (!timeMatch) return timeString;
    
    let totalSeconds = 0;
    
    timeMatch.forEach(match => {
      const value = parseInt(match.slice(0, -1));
      const unit = match.slice(-1);
      
      switch (unit) {
        case 's':
          totalSeconds += value;
          break;
        case 'm':
          totalSeconds += value * 60;
          break;
        case 'h':
          totalSeconds += value * 3600;
          break;
      }
    });
    
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    if (hours > 0) {
      return `${hours}ч ${minutes}м ${seconds}с`;
    } else if (minutes > 0) {
      return `${minutes}м ${seconds}с`;
    } else {
      return `${seconds}с`;
    }
  };

  getScoreColor = (percentage: number): string => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  getAttendanceColor = (rate: number): string => {
    if (rate >= 90) return 'text-green-600';
    if (rate >= 75) return 'text-yellow-600';
    return 'text-red-600';
  };

  getPassingStatus = (percentage: number): { passed: boolean; text: string; color: string } => {
    const passed = percentage >= 60;
    return {
      passed,
      text: passed ? 'Сдан' : 'Не сдан',
      color: passed ? 'text-green-600' : 'text-red-600'
    };
  };

  calculateGPA = (tests: TestResult[]): number => {
    if (tests.length === 0) return 0;
    
    const totalScore = tests.reduce((sum, test) => sum + test.score_percentage, 0);
    return Math.round((totalScore / tests.length) * 100) / 100;
  };

  getRecentActivity = (profile: StudentProfile): string => {
    const activities = [
      ...profile.recent_tests.map(test => ({
        date: new Date(test.attempt_date),
        type: 'test',
        description: `Тест по теме "${test.topic_name}"`
      })),
      ...profile.attendance_summary ? [] : [], // заглушка для посещаемости
      ...profile.recent_comments.map(comment => ({
        date: new Date(comment.comment_date),
        type: 'comment',
        description: `Комментарий от ${comment.teacher_name}`
      }))
    ];

    activities.sort((a, b) => b.date.getTime() - a.date.getTime());
    
    if (activities.length === 0) return 'Нет активности';
    
    const mostRecent = activities[0];
    const now = new Date();
    const diffTime = now.getTime() - mostRecent.date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Сегодня';
    if (diffDays === 1) return 'Вчера';
    if (diffDays < 7) return `${diffDays} дней назад`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} недель назад`;
    
    return `${Math.floor(diffDays / 30)} месяцев назад`;
  };

  // Группировка тестов по предметам
  groupTestsBySubject = (tests: TestResult[]): Record<string, TestResult[]> => {
    return tests.reduce((groups, test) => {
      const subject = test.subject_name;
      if (!groups[subject]) {
        groups[subject] = [];
      }
      groups[subject].push(test);
      return groups;
    }, {} as Record<string, TestResult[]>);
  };

  // Получение статистики по предметам
  getSubjectStatistics = (tests: TestResult[], subject: string) => {
    const subjectTests = tests.filter(test => test.subject_name === subject);
    
    if (subjectTests.length === 0) {
      return {
        totalTests: 0,
        averageScore: 0,
        passedTests: 0,
        failedTests: 0,
        bestScore: 0,
        worstScore: 0
      };
    }

    const scores = subjectTests.map(test => test.score_percentage);
    const passedTests = subjectTests.filter(test => test.passed).length;

    return {
      totalTests: subjectTests.length,
      averageScore: Math.round((scores.reduce((sum, score) => sum + score, 0) / scores.length) * 100) / 100,
      passedTests,
      failedTests: subjectTests.length - passedTests,
      bestScore: Math.max(...scores),
      worstScore: Math.min(...scores)
    };
  };
}

// ========== ЭКЗЕМПЛЯР API ==========

export const studentProfileAPI = new StudentProfileAPI();
export default studentProfileAPI;