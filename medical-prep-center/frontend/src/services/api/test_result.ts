// ========== КОНСТАНТЫ ==========

export const TEST_TYPES = {
  TRAINING: 'training',
  CONTROL: 'control', 
  FINAL: 'final'
} as const;

export const TEST_STATUSES = {
  COMPLETED: 'completed',
  CURRENT: 'current',
  OVERDUE: 'overdue',
  AVAILABLE: 'available'
} as const;

export const SUBJECTS = {
  CHEMISTRY: 'chemistry',
  BIOLOGY: 'biology'
} as const;

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

// ========== ТИПЫ ==========

export type TestType = typeof TEST_TYPES[keyof typeof TEST_TYPES];
export type TestStatus = typeof TEST_STATUSES[keyof typeof TEST_STATUSES];
export type Subject = typeof SUBJECTS[keyof typeof SUBJECTS];
export type AttendanceStatus = typeof ATTENDANCE_STATUSES[keyof typeof ATTENDANCE_STATUSES];
export type CommentType = typeof COMMENT_TYPES[keyof typeof COMMENT_TYPES];

export interface TestAttempt {
  attempt_id: number;
  score_percentage: number;
  correct_answers: number;
  total_questions: number;
  attempt_date: string;
  time_spent?: string;
  passed: boolean;
}

export interface TestInfo {
  topic_id: number;
  topic_name: string;
  section_id: number;
  section_name: string;
  subject_id: number;
  subject_name: string;
  block_id?: number;
  block_name?: string;
  status: TestStatus;
  deadline?: string;
  training_attempts: TestAttempt[];
  questions_count: number;
  time_limit_minutes?: number;
  max_attempts: number;
}

export interface TestStatistics {
  student_id: number;
  completed_tests: number;
  current_tests: number;
  overdue_tests: number;
  total_tests: number;
  average_score: number;
  total_time_spent_hours: number;
}

export interface TestCounts {
  completed: number;
  current: number;
  overdue: number;
  available: number;
}

export interface TestsListResponse {
  tests: TestInfo[];
  total_count: number;
  statistics: TestStatistics;
  test_counts: TestCounts;
}

export interface QuestionData {
  question_id: number;
  text: string;
  answer_1?: string;
  answer_2?: string;
  answer_3?: string;
  answer_4?: string;
  correct_answers: number;
  explanation?: string;
  category: string[];
  topic_id: number;
}

export interface TestSession {
  session_id: string;
  topic_id: number;
  test_type: TestType;
  questions: QuestionData[];
  current_question: number;
  start_time: string;
  end_time?: string;
  time_limit_minutes?: number;
  is_active: boolean;
}

export interface TestResult {
  session_id: string;
  topic_id: number;
  test_type: TestType;
  score_percentage: number;
  correct_answers: number;
  total_questions: number;
  time_spent_seconds: number;
  passed: boolean;
  answers: Record<number, number>;
}

export interface TestSessionResponse {
  session: TestSession;
  current_question: QuestionData;
  progress: {
    current: number;
    total: number;
    percentage: number;
  };
}

export interface TestResultResponse {
  result: TestResult;
  detailed_results: Array<{
    question_id: number;
    question_text: string;
    user_answer: number;
    correct_answer: number;
    is_correct: boolean;
    explanation?: string;
  }>;
  recommendations: string[];
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

export interface AttendanceStatistics {
  student_id: number;
  subject_id?: number;
  total_lessons: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  attendance_rate: number;
}

export interface Comment {
  comment_id: number;
  teacher_id: number;
  student_id: number;
  comment_text: string;
  comment_date: string;
  comment_type: CommentType;
}

export interface CommentStatistics {
  total_comments: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  positive_percentage: number;
  negative_percentage: number;
  neutral_percentage: number;
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

export class TestsAPIError extends Error implements APIErrorInterface {
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
    this.name = 'TestsAPIError';
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
    if (retries > 0 && error instanceof TestsAPIError && ![404, 400].includes(error.status || 0)) {
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
      
      throw new TestsAPIError(errorMessage, response.status, undefined, details);
    }

    try {
      if (contentType?.includes('application/json')) {
        return await response.json();
      } else {
        const text = await response.text();
        return text as unknown as T;
      }
    } catch (error) {
      throw new TestsAPIError('Некорректный формат ответа от сервера');
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
        throw new TestsAPIError('Превышено время ожидания запроса', 408);
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
        throw new TestsAPIError('Превышено время ожидания запроса', 408);
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
        throw new TestsAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }
}

// ========== TESTS API ==========

export class TestsAPI {
  private client: HTTPClient;

  constructor(baseURL?: string) {
    this.client = new HTTPClient(`${baseURL || API_CONFIG.baseURL}/assessment`);
  }

  // Получение списка тестов студента
  async getStudentTests(
    studentId: number,
    filters?: {
      subject_name?: Subject;
      section_id?: number;
      status_filter?: TestStatus;
      limit?: number;
    }
  ): Promise<TestsListResponse> {
    if (!studentId || studentId <= 0) {
      throw new TestsAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {};
    
    if (filters?.subject_name) {
      params.subject_name = filters.subject_name;
    }
    if (filters?.section_id) {
      params.section_id = filters.section_id;
    }
    if (filters?.status_filter) {
      params.status_filter = filters.status_filter;
    }
    if (filters?.limit && filters.limit > 0) {
      params.limit = Math.min(filters.limit, 200);
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<TestsListResponse>(`/student/${studentId}`, params);
      } catch (error) {
        if (error instanceof TestsAPIError && error.status === 404) {
          return {
            tests: [],
            total_count: 0,
            statistics: {
              student_id: studentId,
              completed_tests: 0,
              current_tests: 0,
              overdue_tests: 0,
              total_tests: 0,
              average_score: 0,
              total_time_spent_hours: 0
            },
            test_counts: {
              completed: 0,
              current: 0,
              overdue: 0,
              available: 0
            }
          };
        }
        throw error;
      }
    });
  }

  // Создание сессии тестирования
  async createTestSession(
    topicId: number,
    testType: TestType = TEST_TYPES.TRAINING,
    questionsLimit: number = 30
  ): Promise<TestSessionResponse> {
    if (!topicId || topicId <= 0) {
      throw new TestsAPIError('Корректный ID темы обязателен');
    }

    if (questionsLimit < 5 || questionsLimit > 50) {
      throw new TestsAPIError('Количество вопросов должно быть от 5 до 50');
    }

    const data = {
      topic_id: topicId,
      test_type: testType,
      questions_limit: questionsLimit
    };

    return retryRequest(async () => {
      return await this.client.post<TestSessionResponse>('/session', data);
    });
  }

  // Получение текущего вопроса
  async getCurrentQuestion(sessionId: string): Promise<QuestionData> {
    if (!sessionId) {
      throw new TestsAPIError('ID сессии обязателен');
    }

    return retryRequest(async () => {
      return await this.client.get<QuestionData>(`/session/${sessionId}/question`);
    });
  }

  // Отправка ответа на вопрос
  async submitAnswer(
    sessionId: string,
    questionId: number,
    answerChoice: number
  ): Promise<{
    status: string;
    question_answered: number;
    current_question: number;
    total_questions: number;
    is_finished: boolean;
    progress_percentage: number;
  }> {
    if (!sessionId) {
      throw new TestsAPIError('ID сессии обязателен');
    }

    if (!questionId || questionId <= 0) {
      throw new TestsAPIError('Корректный ID вопроса обязателен');
    }

    if (answerChoice < 1 || answerChoice > 4) {
      throw new TestsAPIError('Ответ должен быть от 1 до 4');
    }

    const data = {
      session_id: sessionId,
      question_id: questionId,
      answer_choice: answerChoice
    };

    return retryRequest(async () => {
      return await this.client.post(`/session/${sessionId}/answer`, data);
    });
  }

  // Завершение теста
  async finishTest(
    sessionId: string,
    answers: Record<number, number> = {}
  ): Promise<TestResultResponse> {
    if (!sessionId) {
      throw new TestsAPIError('ID сессии обязателен');
    }

    const data = {
      session_id: sessionId,
      answers
    };

    return retryRequest(async () => {
      return await this.client.post<TestResultResponse>(`/session/${sessionId}/finish`, data);
    });
  }

  // Получение результата теста
  async getTestResult(sessionId: string): Promise<TestResultResponse> {
    if (!sessionId) {
      throw new TestsAPIError('ID сессии обязателен');
    }

    return retryRequest(async () => {
      return await this.client.get<TestResultResponse>(`/result/${sessionId}`);
    });
  }

  // Получение статистики студента
  async getStudentStatistics(studentId: number): Promise<TestStatistics> {
    if (!studentId || studentId <= 0) {
      throw new TestsAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      return await this.client.get<TestStatistics>(`/student/${studentId}/statistics`);
    });
  }

  // Получение вопросов по теме
  async getTopicQuestions(
    topicId: number,
    options?: {
      limit?: number;
      random?: boolean;
    }
  ): Promise<QuestionData[]> {
    if (!topicId || topicId <= 0) {
      throw new TestsAPIError('Корректный ID темы обязателен');
    }

    const params: Record<string, string | number> = {};
    
    if (options?.limit && options.limit > 0) {
      params.limit = Math.min(options.limit, 100);
    }
    if (options?.random) {
      params.random = 'true';
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<QuestionData[]>(`/topic/${topicId}/questions`, params);
      } catch (error) {
        if (error instanceof TestsAPIError && error.status === 404) {
          return [];
        }
        throw error;
      }
    });
  }

  // Получение посещаемости студента
  async getStudentAttendance(
    studentId: number,
    subjectId?: number
  ): Promise<AttendanceRecord[]> {
    if (!studentId || studentId <= 0) {
      throw new TestsAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {};
    if (subjectId) {
      params.subject_id = subjectId;
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<AttendanceRecord[]>(`/student/${studentId}/attendance`, params);
      } catch (error) {
        if (error instanceof TestsAPIError && error.status === 404) {
          return [];
        }
        throw error;
      }
    });
  }

  // Получение статистики посещаемости
  async getAttendanceStatistics(
    studentId: number,
    subjectId?: number
  ): Promise<AttendanceStatistics> {
    if (!studentId || studentId <= 0) {
      throw new TestsAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {};
    if (subjectId) {
      params.subject_id = subjectId;
    }

    return retryRequest(async () => {
      return await this.client.get<AttendanceStatistics>(`/student/${studentId}/attendance/statistics`, params);
    });
  }

  // Получение комментариев студента
  async getStudentComments(studentId: number): Promise<Comment[]> {
    if (!studentId || studentId <= 0) {
      throw new TestsAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<Comment[]>(`/student/${studentId}/comments`);
      } catch (error) {
        if (error instanceof TestsAPIError && error.status === 404) {
          return [];
        }
        throw error;
      }
    });
  }

  // Получение статистики комментариев
  async getCommentsStatistics(studentId: number): Promise<CommentStatistics> {
    if (!studentId || studentId <= 0) {
      throw new TestsAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      return await this.client.get<CommentStatistics>(`/student/${studentId}/comments/statistics`);
    });
  }

  // Получение итоговой оценки
  async getFinalGrade(studentId: number, subjectId: number): Promise<FinalGrade> {
    if (!studentId || studentId <= 0) {
      throw new TestsAPIError('Корректный ID студента обязателен');
    }

    if (!subjectId || subjectId <= 0) {
      throw new TestsAPIError('Корректный ID предмета обязателен');
    }

    return retryRequest(async () => {
      return await this.client.get<FinalGrade>(`/student/${studentId}/final-grade/${subjectId}`);
    });
  }

  // Получение активных сессий
  async getActiveSessions(): Promise<{
    active_sessions: number;
    total_sessions: number;
    sessions: Array<{
      session_id: string;
      topic_id: number;
      test_type: TestType;
      is_active: boolean;
      start_time: string;
      current_question: number;
      total_questions: number;
    }>;
  }> {
    return retryRequest(async () => {
      return await this.client.get('/sessions/active');
    });
  }

  // Удаление сессии
  async deleteSession(sessionId: string): Promise<{ status: string; message: string }> {
    if (!sessionId) {
      throw new TestsAPIError('ID сессии обязателен');
    }

    return retryRequest(async () => {
      return await this.client.delete(`/session/${sessionId}`);
    });
  }

  // Проверка здоровья API
  async healthCheck(): Promise<{
    status: string;
    service: string;
    version: string;
    timestamp: string;
    active_sessions: number;
  }> {
    try {
      return await this.client.get('/health');
    } catch (error) {
      throw new TestsAPIError('Сервис тестирования недоступен');
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

  getTestStatusDisplayName(status: TestStatus): string {
    switch (status) {
      case TEST_STATUSES.COMPLETED:
        return 'Сдано';
      case TEST_STATUSES.CURRENT:
        return 'Актуально';
      case TEST_STATUSES.OVERDUE:
        return 'Просрочено';
      case TEST_STATUSES.AVAILABLE:
        return 'Доступно';
      default:
        return status;
    }
  }

  getTestTypeDisplayName(type: TestType): string {
    switch (type) {
      case TEST_TYPES.TRAINING:
        return 'Тренировочный';
      case TEST_TYPES.CONTROL:
        return 'Контрольный';
      case TEST_TYPES.FINAL:
        return 'Экзамен';
      default:
        return type;
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

  calculateTimeLeft = (deadline: string): number => {
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const diffInMs = deadlineDate.getTime() - now.getTime();
    return Math.ceil(diffInMs / (1000 * 60 * 60 * 24)); // дни
  };

  isTestOverdue = (deadline: string): boolean => {
    return this.calculateTimeLeft(deadline) < 0;
  };

  getScoreColor = (percentage: number): string => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  getPassingStatus = (percentage: number): { passed: boolean; text: string } => {
    const passed = percentage >= 60;
    return {
      passed,
      text: passed ? 'Сдан' : 'Не сдан'
    };
  };

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

  formatShortDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  getAttendanceColor = (status: AttendanceStatus): string => {
    switch (status) {
      case ATTENDANCE_STATUSES.PRESENT:
        return 'text-green-600';
      case ATTENDANCE_STATUSES.ABSENT:
        return 'text-red-600';
      case ATTENDANCE_STATUSES.LATE:
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  getCommentColor = (type: CommentType): string => {
    switch (type) {
      case COMMENT_TYPES.POSITIVE:
        return 'text-green-600 bg-green-50 border-green-200';
      case COMMENT_TYPES.NEGATIVE:
        return 'text-red-600 bg-red-50 border-red-200';
      case COMMENT_TYPES.NEUTRAL:
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  calculateAttendanceRate = (present: number, total: number): number => {
    if (total === 0) return 0;
    return Math.round((present / total) * 100);
  };

  getGradeColor = (grade: number): string => {
    if (grade >= 4.5) return 'text-green-600';
    if (grade >= 3.5) return 'text-yellow-600';
    if (grade >= 2.5) return 'text-orange-600';
    return 'text-red-600';
  };

  formatGrade = (grade: number): string => {
    return grade.toFixed(1);
  };

  getTestStatusColor = (status: TestStatus): string => {
    switch (status) {
      case TEST_STATUSES.COMPLETED:
        return 'text-green-600 bg-green-50 border-green-200';
      case TEST_STATUSES.CURRENT:
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case TEST_STATUSES.OVERDUE:
        return 'text-red-600 bg-red-50 border-red-200';
      case TEST_STATUSES.AVAILABLE:
        return 'text-gray-600 bg-gray-50 border-gray-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  getBestAttempt = (attempts: TestAttempt[]): TestAttempt | null => {
    if (attempts.length === 0) return null;
    
    return attempts.reduce((best, current) => {
      return current.score_percentage > best.score_percentage ? current : best;
    });
  };

  getLatestAttempt = (attempts: TestAttempt[]): TestAttempt | null => {
    if (attempts.length === 0) return null;
    
    return attempts.reduce((latest, current) => {
      return new Date(current.attempt_date) > new Date(latest.attempt_date) ? current : latest;
    });
  };

  calculateAverageScore = (attempts: TestAttempt[]): number => {
    if (attempts.length === 0) return 0;
    
    const sum = attempts.reduce((acc, attempt) => acc + attempt.score_percentage, 0);
    return Math.round(sum / attempts.length);
  };

  getProgressColor = (percentage: number): string => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    if (percentage >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  isPassingGrade = (percentage: number): boolean => {
    return percentage >= 60;
  };
}

// ========== ЭКЗЕМПЛЯР API ==========

export const testsAPI = new TestsAPI();
export default testsAPI;