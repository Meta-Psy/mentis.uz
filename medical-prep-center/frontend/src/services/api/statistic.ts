// ========== КОНСТАНТЫ ==========

export const STATISTIC_TYPES = {
  CURRENT_GRADES: 'current_grades',
  TESTS: 'tests',
  DTM: 'dtm',
  SECTION_EXAMS: 'section_exams',
  BLOCK_EXAMS: 'block_exams'
} as const;

export const TABLE_TYPES = {
  ALL_GROUPS_AVERAGE: 'all_groups_average',
  MY_GROUP_AVERAGE: 'my_group_average',
  DTM_ALL_TIME: 'dtm_all_time',
  DTM_LAST_MONTH: 'dtm_last_month'
} as const;

export const SUBJECTS = {
  CHEMISTRY: 'chemistry',
  BIOLOGY: 'biology'
} as const;

export const PERIODS = {
  MONTHLY: 'monthly',
  WEEKLY: 'weekly',
  DAILY: 'daily'
} as const;

// ========== ТИПЫ ==========

export type StatisticType = typeof STATISTIC_TYPES[keyof typeof STATISTIC_TYPES];
export type TableType = typeof TABLE_TYPES[keyof typeof TABLE_TYPES];
export type Subject = typeof SUBJECTS[keyof typeof SUBJECTS];
export type Period = typeof PERIODS[keyof typeof PERIODS];

export interface GradePoint {
  month: string;
  value: number;
}

export interface StudentRankingInfo {
  student_id: number;
  name: string;
  group_id: number;
  group_name?: string;
  
  // Оценки
  chemistry_avg?: number;
  biology_avg?: number;
  overall_avg?: number;
  
  // ДТМ баллы
  chemistry_dtm?: number;
  biology_dtm?: number;
  general_dtm?: number;
  total_dtm?: number;
  
  // Последние ДТМ результаты
  last_chemistry_dtm?: number;
  last_biology_dtm?: number;
  last_general_dtm?: number;
  last_total_dtm?: number;
  
  // Рейтинг
  rank: number;
}

export interface SubjectStatistics {
  subject_id: number;
  subject_name: string;
  
  // Графики данных
  current_grades: GradePoint[];
  tests: GradePoint[];
  dtm: GradePoint[];
  section_exams: GradePoint[];
  block_exams: GradePoint[];
  
  // Средние значения
  avg_current_grade: number;
  avg_test_score: number;
  avg_dtm_score: number;
  avg_section_score: number;
  avg_block_score: number;
}

export interface OverallStatistics {
  student_id: number;
  
  // Общие показатели
  total_subjects: number;
  completed_tests: number;
  pending_tests: number;
  overdue_tests: number;
  
  // Средние баллы
  overall_average: number;
  chemistry_average: number;
  biology_average: number;
  
  // ДТМ статистика
  total_dtm_attempts: number;
  best_dtm_score: number;
  latest_dtm_score: number;
  
  // Посещаемость
  total_lessons: number;
  attended_lessons: number;
  attendance_rate: number;
}

export interface TournamentTable {
  table_type: TableType;
  title: string;
  students: StudentRankingInfo[];
  current_student_rank: number;
  total_participants: number;
}

export interface StudentStatisticsResponse {
  student_id: number;
  student_name: string;
  group_id: number;
  group_name: string;
  
  // Статистика по предметам
  chemistry: SubjectStatistics;
  biology: SubjectStatistics;
  
  // Общая статистика
  overall: OverallStatistics;
  
  // Турнирные таблицы
  tournament_tables: TournamentTable[];
}

export interface SubjectProgressResponse {
  subject_id: number;
  subject_name: string;
  student_id: number;
  
  // Данные для графика
  progress_data: Record<string, GradePoint[]>;
  
  // Сводная информация
  current_average: number;
  improvement_trend: number;
  last_month_average: number;
}

export interface RankingResponse {
  table_type: TableType;
  title: string;
  students: StudentRankingInfo[];
  current_student?: StudentRankingInfo;
  current_student_rank: number;
  total_participants: number;
  group_filter?: number;
}

export interface TrendAnalysis {
  metric_name: string;
  current_value: number;
  previous_value: number;
  change_percentage: number;
  trend: 'improving' | 'declining' | 'stable';
}

export interface PerformanceInsights {
  student_id: number;
  strengths: string[];
  areas_for_improvement: string[];
  recommendations: string[];
  trends: TrendAnalysis[];
}

export interface DetailedStatisticsResponse {
  student_statistics: StudentStatisticsResponse;
  performance_insights: PerformanceInsights;
  comparison_data: Record<string, any>;
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

export class StatisticsAPIError extends Error implements APIErrorInterface {
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
    this.name = 'StatisticsAPIError';
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
    if (retries > 0 && error instanceof StatisticsAPIError && ![404, 400].includes(error.status || 0)) {
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
      
      throw new StatisticsAPIError(errorMessage, response.status, undefined, details);
    }

    try {
      if (contentType?.includes('application/json')) {
        return await response.json();
      } else {
        const text = await response.text();
        return text as unknown as T;
      }
    } catch (error) {
      throw new StatisticsAPIError('Некорректный формат ответа от сервера');
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
        throw new StatisticsAPIError('Превышено время ожидания запроса', 408);
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
        throw new StatisticsAPIError('Превышено время ожидания запроса', 408);
      }
      throw error;
    }
  }
}

// ========== STATISTICS API ==========

export class StatisticsAPI {
  private client: HTTPClient;

  constructor(baseURL?: string) {
    this.client = new HTTPClient(`${baseURL || API_CONFIG.baseURL}/statistics`);
  }

  // Получение полной статистики студента
  async getStudentStatistics(
    studentId: number,
    options?: {
      period?: Period;
      include_tournaments?: boolean;
    }
  ): Promise<StudentStatisticsResponse> {
    if (!studentId || studentId <= 0) {
      throw new StatisticsAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number | boolean> = {};
    
    if (options?.period) {
      params.period = options.period;
    }
    if (options?.include_tournaments !== undefined) {
      params.include_tournaments = options.include_tournaments;
    }

    return retryRequest(async () => {
      try {
        return await this.client.get<StudentStatisticsResponse>(`/student/${studentId}`, params);
      } catch (error) {
        if (error instanceof StatisticsAPIError && error.status === 404) {
          throw new StatisticsAPIError('Студент не найден');
        }
        throw error;
      }
    });
  }

  // Получение прогресса по предмету
  async getSubjectProgress(
    studentId: number,
    subjectName: Subject,
    options?: {
      metric_type?: StatisticType;
      period?: Period;
    }
  ): Promise<SubjectProgressResponse> {
    if (!studentId || studentId <= 0) {
      throw new StatisticsAPIError('Корректный ID студента обязателен');
    }

    if (!subjectName) {
      throw new StatisticsAPIError('Название предмета обязательно');
    }

    const params: Record<string, string | number> = {};
    
    if (options?.metric_type) {
      params.metric_type = options.metric_type;
    }
    if (options?.period) {
      params.period = options.period;
    }

    return retryRequest(async () => {
      return await this.client.get<SubjectProgressResponse>(
        `/student/${studentId}/subject/${subjectName}`, 
        params
      );
    });
  }

  // Получение турнирной таблицы
  async getRanking(
    tableType: TableType,
    studentId: number,
    options?: {
      group_id?: number;
      limit?: number;
    }
  ): Promise<RankingResponse> {
    if (!tableType) {
      throw new StatisticsAPIError('Тип таблицы обязателен');
    }

    if (!studentId || studentId <= 0) {
      throw new StatisticsAPIError('Корректный ID студента обязателен');
    }

    const params: Record<string, string | number> = {
      student_id: studentId
    };
    
    if (options?.group_id) {
      params.group_id = options.group_id;
    }
    if (options?.limit && options.limit > 0) {
      params.limit = Math.min(options.limit, 200);
    }

    return retryRequest(async () => {
      return await this.client.get<RankingResponse>(`/ranking/${tableType}`, params);
    });
  }

  // Получение детальной аналитики
  async getDetailedInsights(studentId: number): Promise<DetailedStatisticsResponse> {
    if (!studentId || studentId <= 0) {
      throw new StatisticsAPIError('Корректный ID студента обязателен');
    }

    return retryRequest(async () => {
      return await this.client.get<DetailedStatisticsResponse>(`/student/${studentId}/insights`);
    });
  }

  // Проверка здоровья API
  async healthCheck(): Promise<{
    status: string;
    service: string;
    version: string;
    timestamp: string;
    active_calculations: number;
    cache_status: string;
  }> {
    try {
      return await this.client.get('/health');
    } catch (error) {
      throw new StatisticsAPIError('Сервис статистики недоступен');
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

  getTableTypeDisplayName(tableType: TableType): string {
    switch (tableType) {
      case TABLE_TYPES.ALL_GROUPS_AVERAGE:
        return 'По всем группам (средний балл)';
      case TABLE_TYPES.MY_GROUP_AVERAGE:
        return 'Внутри моей группы (средний балл)';
      case TABLE_TYPES.DTM_ALL_TIME:
        return 'ДТМ за все время (по всем группам)';
      case TABLE_TYPES.DTM_LAST_MONTH:
        return 'ДТМ за последний месяц (по всем группам)';
      default:
        return tableType;
    }
  }

  getStatisticTypeDisplayName(type: StatisticType): string {
    switch (type) {
      case STATISTIC_TYPES.CURRENT_GRADES:
        return 'Средние оценки за текущие';
      case STATISTIC_TYPES.TESTS:
        return 'Средняя оценка за тесты';
      case STATISTIC_TYPES.DTM:
        return 'Средняя оценка за ДТМ';
      case STATISTIC_TYPES.SECTION_EXAMS:
        return 'Экзамены по разделам';
      case STATISTIC_TYPES.BLOCK_EXAMS:
        return 'Экзамены по блокам';
      default:
        return type;
    }
  }

  calculateDTMScore(bio: number, chem: number, general: number): number {
    return Number((bio * 3.1 + chem * 2.1 + general * 1.1).toFixed(1));
  }

  getScoreColor = (percentage: number): string => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  getRankIcon = (rank: number): string => {
    switch (rank) {
      case 1:
        return '🏆';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return '';
    }
  };

  formatTrend = (trend: number): { text: string; color: string; icon: string } => {
    if (trend > 5) {
      return {
        text: `+${trend.toFixed(1)}%`,
        color: 'text-green-600',
        icon: '📈'
      };
    } else if (trend < -5) {
      return {
        text: `${trend.toFixed(1)}%`,
        color: 'text-red-600',
        icon: '📉'
      };
    } else {
      return {
        text: 'Стабильно',
        color: 'text-gray-600',
        icon: '➡️'
      };
    }
  };

  getAttendanceStatus = (rate: number): { text: string; color: string } => {
    if (rate >= 90) {
      return { text: 'Отлично', color: 'text-green-600' };
    } else if (rate >= 80) {
      return { text: 'Хорошо', color: 'text-yellow-600' };
    } else if (rate >= 70) {
      return { text: 'Удовлетворительно', color: 'text-orange-600' };
    } else {
      return { text: 'Требует внимания', color: 'text-red-600' };
    }
  };

  getPerformanceLevel = (average: number): { level: string; color: string } => {
    if (average >= 9) {
      return { level: 'Отлично', color: 'text-green-600' };
    } else if (average >= 8) {
      return { level: 'Хорошо', color: 'text-blue-600' };
    } else if (average >= 7) {
      return { level: 'Удовлетворительно', color: 'text-yellow-600' };
    } else if (average >= 6) {
      return { level: 'Зачет', color: 'text-orange-600' };
    } else {
      return { level: 'Требует улучшения', color: 'text-red-600' };
    }
  };

  // Вспомогательные функции для работы с графиками
  getChartMaxValue = (metricType: StatisticType): number => {
    switch (metricType) {
      case STATISTIC_TYPES.DTM:
        return 189;
      case STATISTIC_TYPES.CURRENT_GRADES:
      case STATISTIC_TYPES.TESTS:
      case STATISTIC_TYPES.SECTION_EXAMS:
      case STATISTIC_TYPES.BLOCK_EXAMS:
      default:
        return 10;
    }
  };

  getChartColor = (subject: Subject): string => {
    switch (subject) {
      case SUBJECTS.CHEMISTRY:
        return '#3e588b';
      case SUBJECTS.BIOLOGY:
        return '#22c55e';
      default:
        return '#6b7280';
    }
  };

  // Функции для анализа данных
  calculateImprovement = (data: GradePoint[]): number => {
    if (data.length < 2) return 0;
    
    const firstHalf = data.slice(0, Math.floor(data.length / 2));
    const secondHalf = data.slice(Math.floor(data.length / 2));
    
    const firstAvg = firstHalf.reduce((sum, point) => sum + point.value, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((sum, point) => sum + point.value, 0) / secondHalf.length;
    
    if (firstAvg === 0) return 0;
    
    return ((secondAvg - firstAvg) / firstAvg) * 100;
  };

  getLastMonthAverage = (data: GradePoint[]): number => {
    if (data.length === 0) return 0;
    
    // Берем последние 3 точки данных
    const lastPoints = data.slice(-3);
    return lastPoints.reduce((sum, point) => sum + point.value, 0) / lastPoints.length;
  };

  // Функции для работы с рейтингами
  getStudentPosition = (ranking: StudentRankingInfo[], studentId: number): number => {
    const index = ranking.findIndex(student => student.student_id === studentId);
    return index !== -1 ? index + 1 : 0;
  };

  getTopThree = (ranking: StudentRankingInfo[]): StudentRankingInfo[] => {
    return ranking.slice(0, 3);
  };

  isCurrentStudent = (student: StudentRankingInfo, currentStudentId: number): boolean => {
    return student.student_id === currentStudentId;
  };

  isTopThree = (rank: number): boolean => {
    return rank <= 3;
  };
}

// ========== ЭКЗЕМПЛЯР API ==========

export const statisticsAPI = new StatisticsAPI();
export default statisticsAPI;