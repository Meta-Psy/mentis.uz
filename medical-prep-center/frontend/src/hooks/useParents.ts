import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { 
  parentStatsAPI, 
  ParentStatsAPIError,
  PERFORMANCE_STATUSES,
  NOTIFICATION_TYPES
} from '../services/api/parent_dashboard';
import type { 
  ParentStatisticsData,
  DetailedPerformanceData,
  DetailedDisciplineData,
  DetailedExamsData,
  RecommendationsData,
  StudentInfo,
  SubjectGrades,
  DisciplineStatistics,
  ExamStatistics,
  AdmissionChance,
  PerformanceStatus,
  CommentRecord,
  NotificationItem
} from '../services/api/parent_dashboard';

// ========== ТИПЫ ==========

interface UseParentStatisticsState {
  // Данные
  studentInfo: StudentInfo | null;
  performance: Record<string, SubjectGrades>;
  discipline: DisciplineStatistics | null;
  exams: ExamStatistics | null;
  admissionChance: AdmissionChance | null;
  recentComments: CommentRecord[];
  
  // Состояние загрузки
  isLoading: boolean;
  isValidating: boolean;
  hasError: string | null;
  
  // Обработчики
  handleRefresh: () => void;
  handleToggleBlock: (blockName: string) => void;
  
  // Состояние интерфейса
  expandedBlocks: Record<string, boolean>;
}

interface UseParentStatisticsReturn extends UseParentStatisticsState {
  // Дополнительные данные
  notifications: UseNotificationsReturn;
  detailedViews: UseDetailedViewsReturn;
}

interface UseNotificationsState {
  notifications: NotificationItem[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
}

interface UseNotificationsReturn extends UseNotificationsState {
  refresh: () => void;
  markAsRead: (notificationId: string) => void;
  markAllAsRead: () => void;
  filterByType: (type: string) => NotificationItem[];
}

interface UseDetailedViewsState {
  performance: DetailedPerformanceData | null;
  discipline: DetailedDisciplineData | null;
  exams: DetailedExamsData | null;
  loadingStates: {
    performance: boolean;
    discipline: boolean;
    exams: boolean;
  };
  errors: {
    performance: string | null;
    discipline: string | null;
    exams: string | null;
  };
}

interface UseDetailedViewsReturn extends UseDetailedViewsState {
  loadPerformanceDetails: (subjectId?: number) => Promise<void>;
  loadDisciplineDetails: (filters?: any) => Promise<void>;
  loadExamDetails: (filters?: any) => Promise<void>;
  clearDetails: () => void;
}

// ========== ОСНОВНОЙ ХУК ==========

export const useParentStatistics = (studentId: number): UseParentStatisticsReturn => {
  // Основное состояние
  const [studentInfo, setStudentInfo] = useState<StudentInfo | null>(null);
  const [performance, setPerformance] = useState<Record<string, SubjectGrades>>({});
  const [discipline, setDiscipline] = useState<DisciplineStatistics | null>(null);
  const [exams, setExams] = useState<ExamStatistics | null>(null);
  const [admissionChance, setAdmissionChance] = useState<AdmissionChance | null>(null);
  const [recentComments, setRecentComments] = useState<CommentRecord[]>([]);
  
  // Состояние загрузки
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [hasError, setHasError] = useState<string | null>(null);
  
  // Состояние интерфейса
  const [expandedBlocks, setExpandedBlocks] = useState({
    performance: false,
    discipline: false,
    exams: false,
  });

  // Кэш для избежания повторных запросов
  const cacheRef = useRef<Map<string, { data: any; timestamp: number }>>(new Map());
  const CACHE_DURATION = 5 * 60 * 1000; // 5 минут

  // Дополнительные хуки
  const notifications = useNotifications(studentId);
  const detailedViews = useDetailedViews(studentId);

  // Функция получения статистики
  const fetchStatistics = useCallback(async (force = false) => {
    if (!studentId || studentId <= 0) {
      setHasError('Некорректный ID студента');
      return;
    }

    const cacheKey = `parent-stats-${studentId}`;
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();

    // Проверяем кэш
    if (!force && cached && (now - cached.timestamp) < CACHE_DURATION) {
      const data = cached.data as ParentStatisticsData;
      setStudentInfo(data.student_info);
      setPerformance(data.performance);
      setDiscipline(data.discipline);
      setExams(data.exams);
      setAdmissionChance(data.admission_chance);
      setRecentComments(data.recent_comments);
      return;
    }

    try {
      setIsLoading(true);
      setHasError(null);

      const data = await parentStatsAPI.getStudentStatistics(studentId, {
        include_comments: true,
        comments_limit: 5
      });

      setStudentInfo(data.student_info);
      setPerformance(data.performance);
      setDiscipline(data.discipline);
      setExams(data.exams);
      setAdmissionChance(data.admission_chance);
      setRecentComments(data.recent_comments);

      // Кэшируем результат
      cacheRef.current.set(cacheKey, {
        data,
        timestamp: now
      });

    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
      
      if (error instanceof ParentStatsAPIError) {
        setHasError(error.message);
      } else {
        setHasError('Произошла ошибка при загрузке статистики');
      }
      
      // В случае ошибки показываем пустые данные
      setStudentInfo(null);
      setPerformance({});
      setDiscipline(null);
      setExams(null);
      setAdmissionChance(null);
      setRecentComments([]);
    } finally {
      setIsLoading(false);
    }
  }, [studentId]);

  // Функция валидации (фоновое обновление)
  const validateData = useCallback(async () => {
    if (isLoading) return;
    
    try {
      setIsValidating(true);
      await fetchStatistics(true);
    } catch (error) {
      // Валидация не должна показывать ошибки пользователю
      console.warn('Ошибка валидации:', error);
    } finally {
      setIsValidating(false);
    }
  }, [fetchStatistics, isLoading]);

  // Обработчики
  const handleRefresh = useCallback(() => {
    fetchStatistics(true);
    notifications.refresh();
  }, [fetchStatistics, notifications]);

  const handleToggleBlock = useCallback((blockName: string) => {
    setExpandedBlocks(prev => ({
      ...prev,
      [blockName]: !prev[blockName]
    }));
  }, []);

  // Эффект для загрузки данных
  useEffect(() => {
    fetchStatistics();
  }, [fetchStatistics]);

  // Эффект для периодической валидации
  useEffect(() => {
    const interval = setInterval(validateData, 30000); // Каждые 30 секунд
    return () => clearInterval(interval);
  }, [validateData]);

  // Очистка кэша при размонтировании
  useEffect(() => {
    return () => {
      cacheRef.current.clear();
    };
  }, []);

  return {
    // Основные данные
    studentInfo,
    performance,
    discipline,
    exams,
    admissionChance,
    recentComments,
    
    // Состояние загрузки
    isLoading,
    isValidating,
    hasError,
    
    // Обработчики
    handleRefresh,
    handleToggleBlock,
    
    // Состояние интерфейса
    expandedBlocks,
    
    // Дополнительные хуки
    notifications,
    detailedViews
  };
};

// ========== ХУК ДЛЯ УВЕДОМЛЕНИЙ ==========

export const useNotifications = (studentId: number): UseNotificationsReturn => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = useCallback(async () => {
    if (!studentId || studentId <= 0) return;

    try {
      setLoading(true);
      setError(null);
      
      const data = await parentStatsAPI.getNotifications(studentId, {
        limit: 20,
        unread_only: false
      });
      
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch (error) {
      console.error('Ошибка загрузки уведомлений:', error);
      
      const errorMessage = error instanceof ParentStatsAPIError 
        ? error.message 
        : 'Ошибка загрузки уведомлений';
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  const markAsRead = useCallback((notificationId: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.notification_id === notificationId 
          ? { ...notification, is_read: true }
          : notification
      )
    );
    
    setUnreadCount(prev => Math.max(0, prev - 1));
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, is_read: true }))
    );
    setUnreadCount(0);
  }, []);

  const filterByType = useCallback((type: string) => {
    return notifications.filter(notification => notification.type === type);
  }, [notifications]);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  return {
    notifications,
    unreadCount,
    loading,
    error,
    refresh: fetchNotifications,
    markAsRead,
    markAllAsRead,
    filterByType
  };
};

// ========== ХУК ДЛЯ ДЕТАЛЬНЫХ ПРЕДСТАВЛЕНИЙ ==========

export const useDetailedViews = (studentId: number): UseDetailedViewsReturn => {
  const [performance, setPerformance] = useState<DetailedPerformanceData | null>(null);
  const [discipline, setDiscipline] = useState<DetailedDisciplineData | null>(null);
  const [exams, setExams] = useState<DetailedExamsData | null>(null);
  
  const [loadingStates, setLoadingStates] = useState({
    performance: false,
    discipline: false,
    exams: false
  });
  
  const [errors, setErrors] = useState({
    performance: null as string | null,
    discipline: null as string | null,
    exams: null as string | null
  });

  const loadPerformanceDetails = useCallback(async (subjectId?: number) => {
    try {
      setLoadingStates(prev => ({ ...prev, performance: true }));
      setErrors(prev => ({ ...prev, performance: null }));
      
      const data = await parentStatsAPI.getDetailedPerformance(studentId, subjectId);
      setPerformance(data);
    } catch (error) {
      console.error('Ошибка загрузки детальной успеваемости:', error);
      
      const errorMessage = error instanceof ParentStatsAPIError 
        ? error.message 
        : 'Ошибка загрузки детальной успеваемости';
      
      setErrors(prev => ({ ...prev, performance: errorMessage }));
    } finally {
      setLoadingStates(prev => ({ ...prev, performance: false }));
    }
  }, [studentId]);

  const loadDisciplineDetails = useCallback(async (filters?: any) => {
    try {
      setLoadingStates(prev => ({ ...prev, discipline: true }));
      setErrors(prev => ({ ...prev, discipline: null }));
      
      const data = await parentStatsAPI.getDetailedDiscipline(studentId, filters);
      setDiscipline(data);
    } catch (error) {
      console.error('Ошибка загрузки детальной дисциплины:', error);
      
      const errorMessage = error instanceof ParentStatsAPIError 
        ? error.message 
        : 'Ошибка загрузки детальной дисциплины';
      
      setErrors(prev => ({ ...prev, discipline: errorMessage }));
    } finally {
      setLoadingStates(prev => ({ ...prev, discipline: false }));
    }
  }, [studentId]);

  const loadExamDetails = useCallback(async (filters?: any) => {
    try {
      setLoadingStates(prev => ({ ...prev, exams: true }));
      setErrors(prev => ({ ...prev, exams: null }));
      
      const data = await parentStatsAPI.getDetailedExams(studentId, filters);
      setExams(data);
    } catch (error) {
      console.error('Ошибка загрузки детальных экзаменов:', error);
      
      const errorMessage = error instanceof ParentStatsAPIError 
        ? error.message 
        : 'Ошибка загрузки детальных экзаменов';
      
      setErrors(prev => ({ ...prev, exams: errorMessage }));
    } finally {
      setLoadingStates(prev => ({ ...prev, exams: false }));
    }
  }, [studentId]);

  const clearDetails = useCallback(() => {
    setPerformance(null);
    setDiscipline(null);
    setExams(null);
    setErrors({
      performance: null,
      discipline: null,
      exams: null
    });
  }, []);

  return {
    performance,
    discipline,
    exams,
    loadingStates,
    errors,
    loadPerformanceDetails,
    loadDisciplineDetails,
    loadExamDetails,
    clearDetails
  };
};

// ========== ХУК ДЛЯ РЕКОМЕНДАЦИЙ ==========

export const useRecommendations = (studentId: number) => {
  const [recommendations, setRecommendations] = useState<RecommendationsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = useCallback(async () => {
    if (!studentId || studentId <= 0) return;

    try {
      setLoading(true);
      setError(null);
      
      const data = await parentStatsAPI.getRecommendations(studentId);
      setRecommendations(data);
    } catch (error) {
      console.error('Ошибка загрузки рекомендаций:', error);
      
      const errorMessage = error instanceof ParentStatsAPIError 
        ? error.message 
        : 'Ошибка загрузки рекомендаций';
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  return {
    recommendations,
    loading,
    error,
    refresh: fetchRecommendations
  };
};

// ========== ХУК ДЛЯ СТАТИСТИКИ УСПЕВАЕМОСТИ ==========

export const usePerformanceStats = (performance: Record<string, SubjectGrades>) => {
  const stats = useMemo(() => {
    const subjects = Object.values(performance);
    
    if (subjects.length === 0) {
      return {
        totalSubjects: 0,
        averageScore: 0,
        excellentCount: 0,
        goodCount: 0,
        satisfactoryCount: 0,
        poorCount: 0,
        overallStatus: PERFORMANCE_STATUSES.POOR as PerformanceStatus
      };
    }

    const totalScore = subjects.reduce((sum, subject) => sum + subject.average_score, 0);
    const averageScore = totalScore / subjects.length;

    const statusCounts = subjects.reduce((counts, subject) => {
      counts[subject.status] = (counts[subject.status] || 0) + 1;
      return counts;
    }, {} as Record<PerformanceStatus, number>);

    // Определяем общий статус
    let overallStatus: PerformanceStatus;
    if (averageScore >= 8.5) {
      overallStatus = PERFORMANCE_STATUSES.EXCELLENT;
    } else if (averageScore >= 7.0) {
      overallStatus = PERFORMANCE_STATUSES.GOOD;
    } else if (averageScore >= 5.0) {
      overallStatus = PERFORMANCE_STATUSES.SATISFACTORY;
    } else {
      overallStatus = PERFORMANCE_STATUSES.POOR;
    }

    return {
      totalSubjects: subjects.length,
      averageScore: Math.round(averageScore * 100) / 100,
      excellentCount: statusCounts[PERFORMANCE_STATUSES.EXCELLENT] || 0,
      goodCount: statusCounts[PERFORMANCE_STATUSES.GOOD] || 0,
      satisfactoryCount: statusCounts[PERFORMANCE_STATUSES.SATISFACTORY] || 0,
      poorCount: statusCounts[PERFORMANCE_STATUSES.POOR] || 0,
      overallStatus
    };
  }, [performance]);

  return stats;
};

// ========== ХУК ДЛЯ АНАЛИЗА ДИСЦИПЛИНЫ ==========

export const useDisciplineAnalysis = (discipline: DisciplineStatistics | null) => {
  const analysis = useMemo(() => {
    if (!discipline) {
      return {
        attendancePercentage: 0,
        homeworkPercentage: 0,
        pollsPercentage: 0,
        isAttendanceCritical: false,
        isHomeworkCritical: false,
        isPollsCritical: false,
        overallRisk: 'low' as 'low' | 'medium' | 'high'
      };
    }

    const attendancePercentage = parentStatsAPI.calculateAttendancePercentage(discipline);
    const homeworkPercentage = parentStatsAPI.calculateHomeworkPercentage(discipline);
    const pollsPercentage = discipline.total_polls > 0 
      ? Math.round(((discipline.total_polls - discipline.missed_polls) / discipline.total_polls) * 100)
      : 100;

    const isAttendanceCritical = attendancePercentage < 75;
    const isHomeworkCritical = homeworkPercentage < 70;
    const isPollsCritical = pollsPercentage < 70;

    // Определяем общий риск
    let overallRisk: 'low' | 'medium' | 'high' = 'low';
    
    if (isAttendanceCritical && isHomeworkCritical && discipline.teacher_remarks > 3) {
      overallRisk = 'high';
    } else if (isAttendanceCritical || isHomeworkCritical || discipline.teacher_remarks > 1) {
      overallRisk = 'medium';
    }

    return {
      attendancePercentage,
      homeworkPercentage,
      pollsPercentage,
      isAttendanceCritical,
      isHomeworkCritical,
      isPollsCritical,
      overallRisk
    };
  }, [discipline]);

  return analysis;
};

// ========== ХУК ДЛЯ АНАЛИЗА ЭКЗАМЕНОВ ==========

export const useExamAnalysis = (exams: ExamStatistics | null) => {
  const analysis = useMemo(() => {
    if (!exams) {
      return {
        passRate: 0,
        averagePerformance: 0,
        lastExamTrend: 'stable' as 'up' | 'down' | 'stable',
        isImproving: false,
        needsAttention: false
      };
    }

    const passRate = exams.total_exams > 0 
      ? Math.round((exams.passed_exams / exams.total_exams) * 100)
      : 0;

    const averagePerformance = Math.round(exams.average_score);

    // Анализ тренда (упрощенный)
    let lastExamTrend: 'up' | 'down' | 'stable' = 'stable';
    let isImproving = false;

    if (exams.last_monthly_exam) {
      if (exams.last_monthly_exam.percentage >= 80) {
        lastExamTrend = 'up';
        isImproving = true;
      } else if (exams.last_monthly_exam.percentage < 60) {
        lastExamTrend = 'down';
      }
    }

    const needsAttention = passRate < 70 || averagePerformance < 60;

    return {
      passRate,
      averagePerformance,
      lastExamTrend,
      isImproving,
      needsAttention
    };
  }, [exams]);

  return analysis;
};

// ========== ХУК ДЛЯ МОНИТОРИНГА ПРОГРЕССА ==========

export const useProgressMonitoring = (studentId: number) => {
  const [progressHistory, setProgressHistory] = useState<Array<{
    date: string;
    performance_score: number;
    attendance_rate: number;
    exam_average: number;
  }>>([]);

  const [trends, setTrends] = useState({
    performance: 'stable' as 'up' | 'down' | 'stable',
    attendance: 'stable' as 'up' | 'down' | 'stable',
    exams: 'stable' as 'up' | 'down' | 'stable'
  });

  // Здесь можно добавить логику для отслеживания исторических данных
  // В реальном приложении это будет запрос к API для получения истории

  useEffect(() => {
    // Заглушка для исторических данных
    const mockHistory = [
      {
        date: '2024-01-01',
        performance_score: 7.5,
        attendance_rate: 85,
        exam_average: 75
      },
      {
        date: '2024-02-01',
        performance_score: 7.8,
        attendance_rate: 82,
        exam_average: 78
      },
      {
        date: '2024-03-01',
        performance_score: 8.1,
        attendance_rate: 88,
        exam_average: 82
      }
    ];

    setProgressHistory(mockHistory);

    // Анализ трендов
    if (mockHistory.length >= 2) {
      const recent = mockHistory.slice(-2);
      const [prev, curr] = recent;

      setTrends({
        performance: curr.performance_score > prev.performance_score ? 'up' : 
                    curr.performance_score < prev.performance_score ? 'down' : 'stable',
        attendance: curr.attendance_rate > prev.attendance_rate ? 'up' : 
                   curr.attendance_rate < prev.attendance_rate ? 'down' : 'stable',
        exams: curr.exam_average > prev.exam_average ? 'up' : 
               curr.exam_average < prev.exam_average ? 'down' : 'stable'
      });
    }
  }, [studentId]);

  return {
    progressHistory,
    trends
  };
};

// ========== ХУК ДЛЯ АВТОМАТИЧЕСКИХ УВЕДОМЛЕНИЙ ==========

export const useAutoNotifications = (
  studentInfo: StudentInfo | null,
  discipline: DisciplineStatistics | null,
  performance: Record<string, SubjectGrades>
) => {
  const [autoNotifications, setAutoNotifications] = useState<NotificationItem[]>([]);

  useEffect(() => {
    if (!studentInfo || !discipline) return;

    const notifications: NotificationItem[] = [];

    // Проверка посещаемости
    const attendanceRate = parentStatsAPI.calculateAttendancePercentage(discipline);
    if (attendanceRate < 75) {
      notifications.push({
        notification_id: `auto-attendance-${Date.now()}`,
        type: NOTIFICATION_TYPES.WARNING,
        title: 'Низкая посещаемость',
        message: `Посещаемость ${attendanceRate}% - требует внимания`,
        created_at: new Date().toISOString(),
        is_read: false,
        priority: 'high'
      });
    }

    // Проверка успеваемости
    const subjects = Object.values(performance);
    const poorSubjects = subjects.filter(s => s.status === PERFORMANCE_STATUSES.POOR);
    
    if (poorSubjects.length > 0) {
      notifications.push({
        notification_id: `auto-performance-${Date.now()}`,
        type: NOTIFICATION_TYPES.ERROR,
        title: 'Проблемы с успеваемостью',
        message: `Низкие оценки по ${poorSubjects.length} предмету(ам)`,
        created_at: new Date().toISOString(),
        is_read: false,
        priority: 'high'
      });
    }

    // Проверка замечаний
    if (discipline.teacher_remarks > 3) {
      notifications.push({
        notification_id: `auto-remarks-${Date.now()}`,
        type: NOTIFICATION_TYPES.WARNING,
        title: 'Много замечаний',
        message: `Получено ${discipline.teacher_remarks} замечаний от учителей`,
        created_at: new Date().toISOString(),
        is_read: false,
        priority: 'medium'
      });
    }

    setAutoNotifications(notifications);
  }, [studentInfo, discipline, performance]);

  return autoNotifications;
};

// ========== ХУК ДЛЯ СРАВНЕНИЯ ДАННЫХ ==========

export const useDataComparison = (
  currentData: ParentStatisticsData | null,
  previousData: ParentStatisticsData | null
) => {
  const comparison = useMemo(() => {
    if (!currentData || !previousData) {
      return {
        performanceChange: 0,
        attendanceChange: 0,
        dtmScoreChange: 0,
        hasImprovement: false,
        hasDecline: false
      };
    }

    // Сравнение среднего балла успеваемости
    const currentAvg = Object.values(currentData.performance)
      .reduce((sum, subject) => sum + subject.average_score, 0) / Object.values(currentData.performance).length;
    
    const previousAvg = Object.values(previousData.performance)
      .reduce((sum, subject) => sum + subject.average_score, 0) / Object.values(previousData.performance).length;
    
    const performanceChange = currentAvg - previousAvg;

    // Сравнение посещаемости
    const currentAttendance = parentStatsAPI.calculateAttendancePercentage(currentData.discipline);
    const previousAttendance = parentStatsAPI.calculateAttendancePercentage(previousData.discipline);
    const attendanceChange = currentAttendance - previousAttendance;

    // Сравнение DTM баллов
    const dtmScoreChange = currentData.admission_chance.current_score - previousData.admission_chance.current_score;

    const hasImprovement = performanceChange > 0 || attendanceChange > 0 || dtmScoreChange > 0;
    const hasDecline = performanceChange < -0.5 || attendanceChange < -5 || dtmScoreChange < -5;

    return {
      performanceChange: Math.round(performanceChange * 100) / 100,
      attendanceChange: Math.round(attendanceChange),
      dtmScoreChange: Math.round(dtmScoreChange * 10) / 10,
      hasImprovement,
      hasDecline
    };
  }, [currentData, previousData]);

  return comparison;
};

// ========== ХУК ДЛЯ ЭКСПОРТА ДАННЫХ ==========

export const useDataExport = () => {
  const exportToCSV = useCallback((data: ParentStatisticsData, filename: string = 'student-statistics.csv') => {
    const csvData = [];
    
    // Заголовки
    csvData.push(['Показатель', 'Значение', 'Дата']);
    
    // Основная информация
    csvData.push(['Имя студента', `${data.student_info.name} ${data.student_info.surname}`, new Date().toLocaleDateString()]);
    csvData.push(['Направление', data.student_info.direction, '']);
    
    // Успеваемость
    Object.entries(data.performance).forEach(([subject, grades]) => {
      csvData.push([`${subject} - Средний балл`, grades.average_score.toString(), '']);
      csvData.push([`${subject} - Статус`, grades.status, '']);
    });
    
    // Дисциплина
    const attendanceRate = parentStatsAPI.calculateAttendancePercentage(data.discipline);
    csvData.push(['Посещаемость (%)', attendanceRate.toString(), '']);
    csvData.push(['Пропуски', data.discipline.total_absences.toString(), '']);
    csvData.push(['Замечания', data.discipline.teacher_remarks.toString(), '']);
    
    // DTM
    csvData.push(['DTM балл', data.admission_chance.current_score.toString(), '']);
    csvData.push(['Шанс поступления (%)', data.admission_chance.probability_percentage.toString(), '']);
    
    // Преобразуем в CSV формат
    const csvContent = csvData.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    
    // Создаем и скачиваем файл
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, []);

  const exportToPDF = useCallback(async (data: ParentStatisticsData, filename: string = 'student-statistics.pdf') => {
    // Здесь можно использовать библиотеку для генерации PDF, например jsPDF
    // Для простоты реализации создаем HTML и печатаем
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const attendanceRate = parentStatsAPI.calculateAttendancePercentage(data.discipline);

    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Статистика студента</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .section { margin-bottom: 20px; }
            .section h3 { color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; }
            .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .info-item { margin-bottom: 10px; }
            .label { font-weight: bold; }
            .value { color: #666; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>Статистика успеваемости</h1>
            <h2>${data.student_info.name} ${data.student_info.surname}</h2>
            <p>Дата формирования: ${new Date().toLocaleDateString('ru-RU')}</p>
          </div>

          <div class="section">
            <h3>Основная информация</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">Направление:</span>
                <span class="value">${data.student_info.direction}</span>
              </div>
              <div class="info-item">
                <span class="label">Цель:</span>
                <span class="value">${data.student_info.goal || 'Не указана'}</span>
              </div>
            </div>
          </div>

          <div class="section">
            <h3>Успеваемость</h3>
            <table>
              <thead>
                <tr>
                  <th>Предмет</th>
                  <th>Средний балл</th>
                  <th>Статус</th>
                  <th>Тесты</th>
                  <th>Опросы</th>
                </tr>
              </thead>
              <tbody>
                ${Object.entries(data.performance).map(([subject, grades]) => `
                  <tr>
                    <td>${subject}</td>
                    <td>${grades.average_score.toFixed(1)}</td>
                    <td>${grades.status}</td>
                    <td>${grades.tests_score.toFixed(1)} (${grades.tests_total})</td>
                    <td>${grades.polls_score.toFixed(1)} (${grades.polls_total})</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>

          <div class="section">
            <h3>Дисциплина</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">Посещаемость:</span>
                <span class="value">${attendanceRate}%</span>
              </div>
              <div class="info-item">
                <span class="label">Пропуски:</span>
                <span class="value">${data.discipline.total_absences} из ${data.discipline.total_lessons}</span>
              </div>
              <div class="info-item">
                <span class="label">Замечания:</span>
                <span class="value">${data.discipline.teacher_remarks}</span>
              </div>
              <div class="info-item">
                <span class="label">Статус:</span>
                <span class="value">${data.discipline.status}</span>
              </div>
            </div>
          </div>

          <div class="section">
            <h3>DTM и поступление</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">Текущий балл:</span>
                <span class="value">${data.admission_chance.current_score.toFixed(1)} из 189</span>
              </div>
              <div class="info-item">
                <span class="label">Необходимый балл:</span>
                <span class="value">${data.admission_chance.required_score.toFixed(1)} из 189</span>
              </div>
              <div class="info-item">
                <span class="label">Шанс поступления:</span>
                <span class="value">${data.admission_chance.probability_percentage.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          ${data.recent_comments.length > 0 ? `
            <div class="section">
              <h3>Последние комментарии</h3>
              ${data.recent_comments.map(comment => `
                <div class="info-item" style="margin-bottom: 15px; padding: 10px; border-left: 3px solid #ddd;">
                  <div style="font-size: 12px; color: #666; margin-bottom: 5px;">
                    ${parentStatsAPI.formatDateTime(comment.comment_date)} - ${comment.comment_type}
                  </div>
                  <div>${comment.comment_text}</div>
                </div>
              `).join('')}
            </div>
          ` : ''}
        </body>
      </html>
    `;

    printWindow.document.write(htmlContent);
    printWindow.document.close();
    printWindow.focus();
    
    // Ждем загрузки и печатаем
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 500);
  }, []);

  return {
    exportToCSV,
    exportToPDF
  };
};

// ========== ХУК ДЛЯ ФИЛЬТРАЦИИ ДАННЫХ ==========

export const useDataFilters = () => {
  const [filters, setFilters] = useState({
    dateRange: {
      start: null as Date | null,
      end: null as Date | null
    },
    subjects: [] as string[],
    examTypes: [] as string[],
    commentTypes: [] as string[],
    performanceStatus: [] as PerformanceStatus[]
  });

  const applyFilters = useCallback((
    data: ParentStatisticsData,
    filterOptions: typeof filters
  ) => {
    let filteredData = { ...data };

    // Фильтр по предметам
    if (filterOptions.subjects.length > 0) {
      const filteredPerformance: Record<string, SubjectGrades> = {};
      filterOptions.subjects.forEach(subject => {
        if (data.performance[subject]) {
          filteredPerformance[subject] = data.performance[subject];
        }
      });
      filteredData.performance = filteredPerformance;
    }

    // Фильтр по статусу успеваемости
    if (filterOptions.performanceStatus.length > 0) {
      const filteredPerformance: Record<string, SubjectGrades> = {};
      Object.entries(data.performance).forEach(([subject, grades]) => {
        if (filterOptions.performanceStatus.includes(grades.status)) {
          filteredPerformance[subject] = grades;
        }
      });
      filteredData.performance = filteredPerformance;
    }

    // Фильтр комментариев по типу
    if (filterOptions.commentTypes.length > 0) {
      filteredData.recent_comments = data.recent_comments.filter(comment =>
        filterOptions.commentTypes.includes(comment.comment_type)
      );
    }

    // Фильтр по датам (для комментариев)
    if (filterOptions.dateRange.start && filterOptions.dateRange.end) {
      filteredData.recent_comments = data.recent_comments.filter(comment => {
        const commentDate = new Date(comment.comment_date);
        return commentDate >= filterOptions.dateRange.start! && 
               commentDate <= filterOptions.dateRange.end!;
      });
    }

    return filteredData;
  }, []);

  const resetFilters = useCallback(() => {
    setFilters({
      dateRange: { start: null, end: null },
      subjects: [],
      examTypes: [],
      commentTypes: [],
      performanceStatus: []
    });
  }, []);

  const updateFilter = useCallback(<K extends keyof typeof filters>(
    key: K,
    value: typeof filters[K]
  ) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  return {
    filters,
    applyFilters,
    resetFilters,
    updateFilter
  };
};

// ========== ХУК ДЛЯ НАСТРОЕК ПОЛЬЗОВАТЕЛЯ ==========

export const useUserPreferences = () => {
  const [preferences, setPreferences] = useState({
    theme: 'light' as 'light' | 'dark',
    notifications: {
      email: true,
      push: true,
      sms: false
    },
    dashboard: {
      autoRefresh: true,
      refreshInterval: 30000, // 30 секунд
      expandedSections: ['performance', 'discipline'] as string[]
    },
    display: {
      showPhotos: true,
      compactMode: false,
      showTrends: true
    }
  });

  // Загрузка настроек из localStorage
  useEffect(() => {
    const savedPreferences = localStorage.getItem('parent-dashboard-preferences');
    if (savedPreferences) {
      try {
        const parsed = JSON.parse(savedPreferences);
        setPreferences(prev => ({ ...prev, ...parsed }));
      } catch (error) {
        console.warn('Ошибка загрузки настроек:', error);
      }
    }
  }, []);

  // Сохранение настроек в localStorage
  const updatePreferences = useCallback(<K extends keyof typeof preferences>(
    key: K,
    value: typeof preferences[K]
  ) => {
    setPreferences(prev => {
      const newPreferences = { ...prev, [key]: value };
      localStorage.setItem('parent-dashboard-preferences', JSON.stringify(newPreferences));
      return newPreferences;
    });
  }, []);

  const resetPreferences = useCallback(() => {
    const defaultPreferences = {
      theme: 'light' as const,
      notifications: { email: true, push: true, sms: false },
      dashboard: { autoRefresh: true, refreshInterval: 30000, expandedSections: ['performance', 'discipline'] },
      display: { showPhotos: true, compactMode: false, showTrends: true }
    };
    setPreferences(defaultPreferences);
    localStorage.removeItem('parent-dashboard-preferences');
  }, []);

  return {
    preferences,
    updatePreferences,
    resetPreferences
  };
};

// ========== ХУК ДЛЯ ПОИСКА ==========

export const useSearch = (data: ParentStatisticsData | null) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<{
    subjects: Array<{ name: string; type: 'subject'; data: SubjectGrades }>;
    comments: Array<{ text: string; type: 'comment'; data: CommentRecord }>;
    recommendations: Array<{ text: string; type: 'recommendation'; data: any }>;
  }>({
    subjects: [],
    comments: [],
    recommendations: []
  });

  const performSearch = useCallback((query: string) => {
    if (!data || !query.trim()) {
      setSearchResults({ subjects: [], comments: [], recommendations: [] });
      return;
    }

    const lowerQuery = query.toLowerCase();
    const results = {
      subjects: [] as Array<{ name: string; type: 'subject'; data: SubjectGrades }>,
      comments: [] as Array<{ text: string; type: 'comment'; data: CommentRecord }>,
      recommendations: [] as Array<{ text: string; type: 'recommendation'; data: any }>
    };

    // Поиск по предметам
    Object.entries(data.performance).forEach(([subjectName, subjectData]) => {
      if (subjectName.toLowerCase().includes(lowerQuery) || 
          subjectData.status.toLowerCase().includes(lowerQuery)) {
        results.subjects.push({
          name: subjectName,
          type: 'subject',
          data: subjectData
        });
      }
    });

    // Поиск по комментариям
    data.recent_comments.forEach(comment => {
      if (comment.comment_text.toLowerCase().includes(lowerQuery) ||
          comment.comment_type.toLowerCase().includes(lowerQuery)) {
        results.comments.push({
          text: comment.comment_text,
          type: 'comment',
          data: comment
        });
      }
    });

    // Поиск по рекомендациям
    if (data.admission_chance.recommendations) {
      data.admission_chance.recommendations.forEach(recommendation => {
        if (recommendation.toLowerCase().includes(lowerQuery)) {
          results.recommendations.push({
            text: recommendation,
            type: 'recommendation',
            data: recommendation
          });
        }
      });
    }

    setSearchResults(results);
  }, [data]);

  useEffect(() => {
    performSearch(searchQuery);
  }, [searchQuery, performSearch]);

  const clearSearch = useCallback(() => {
    setSearchQuery('');
    setSearchResults({ subjects: [], comments: [], recommendations: [] });
  }, []);

  return {
    searchQuery,
    setSearchQuery,
    searchResults,
    clearSearch,
    hasResults: searchResults.subjects.length > 0 || 
                searchResults.comments.length > 0 || 
                searchResults.recommendations.length > 0
  };
};

// ========== ХУК ДЛЯ ВЕБЕРНЫХ УВЕДОМЛЕНИЙ ==========

export const useWebNotifications = () => {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    setIsSupported('Notification' in window);
    if ('Notification' in window) {
      setPermission(Notification.permission);
    }
  }, []);

  const requestPermission = useCallback(async () => {
    if (!isSupported) return false;

    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      return result === 'granted';
    } catch (error) {
      console.error('Ошибка запроса разрешения на уведомления:', error);
      return false;
    }
  }, [isSupported]);

  const showNotification = useCallback((
    title: string,
    options?: {
      body?: string;
      icon?: string;
      badge?: string;
      tag?: string;
      requireInteraction?: boolean;
    }
  ) => {
    if (!isSupported || permission !== 'granted') return null;

    try {
      const notification = new Notification(title, {
        body: options?.body,
        icon: options?.icon || '/favicon.ico',
        badge: options?.badge,
        tag: options?.tag,
        requireInteraction: options?.requireInteraction || false
      });

      // Автоматически закрываем через 5 секунд
      setTimeout(() => {
        notification.close();
      }, 5000);

      return notification;
    } catch (error) {
      console.error('Ошибка показа уведомления:', error);
      return null;
    }
  }, [isSupported, permission]);

  return {
    isSupported,
    permission,
    requestPermission,
    showNotification,
    canShowNotifications: isSupported && permission === 'granted'
  };
};

// ========== ЭКСПОРТ ==========

export default useParentStatistics;