import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  statisticsAPI, 
  StatisticsAPIError,
  STATISTIC_TYPES,
  TABLE_TYPES,
  SUBJECTS
} from '../services/api/statistic';
import type { 
  StudentStatisticsResponse,
  SubjectProgressResponse,
  RankingResponse,
  StudentRankingInfo,
  TournamentTable,
  PerformanceInsights,
  StatisticType,
  TableType,
  Subject,
  GradePoint
} from '../services/api/statistic';

// ========== ТИПЫ ==========

interface UseStatisticsPageState {
  // Состояние фильтров
  selectedSubject: Subject;
  selectedMetric: StatisticType;
  selectedTable: TableType;
  
  // Данные
  studentData: StudentStatisticsResponse | null;
  chartData: GradePoint[];
  tournamentTables: TournamentTable[];
  
  // Состояние загрузки
  isLoading: boolean;
  isValidating: boolean;
  hasError: string | null;
  
  // Обработчики
  handleSubjectChange: (subject: Subject) => void;
  handleMetricChange: (metric: StatisticType) => void;
  handleTableChange: (table: TableType) => void;
  handleRefresh: () => void;
}

interface UseSubjectProgressState {
  progressData: SubjectProgressResponse | null;
  chartData: GradePoint[];
  loading: boolean;
  error: string | null;
}

interface UseSubjectProgressReturn extends UseSubjectProgressState {
  refreshProgress: () => void;
  getChartData: (metricType: StatisticType) => GradePoint[];
}

interface UseTournamentTableState {
  ranking: RankingResponse | null;
  loading: boolean;
  error: string | null;
}

interface UseTournamentTableReturn extends UseTournamentTableState {
  refreshRanking: () => void;
  getStudentRank: () => number;
  getTopThree: () => StudentRankingInfo[];
  getCurrentStudent: () => StudentRankingInfo | null;
}

// ========== ОСНОВНОЙ ХУК ==========

export const useStatisticsPage = (studentId: number): UseStatisticsPageState => {
  // Состояние фильтров
  const [selectedSubject, setSelectedSubject] = useState<Subject>(SUBJECTS.CHEMISTRY);
  const [selectedMetric, setSelectedMetric] = useState<StatisticType>(STATISTIC_TYPES.CURRENT_GRADES);
  const [selectedTable, setSelectedTable] = useState<TableType>(TABLE_TYPES.ALL_GROUPS_AVERAGE);
  
  // Данные
  const [studentData, setStudentData] = useState<StudentStatisticsResponse | null>(null);
  const [chartData, setChartData] = useState<GradePoint[]>([]);
  const [tournamentTables, setTournamentTables] = useState<TournamentTable[]>([]);
  
  // Состояние загрузки
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [hasError, setHasError] = useState<string | null>(null);
  
  // Кэш для избежания повторных запросов
  const cacheRef = useRef<Map<string, { data: any; timestamp: number }>>(new Map());
  const CACHE_DURATION = 5 * 60 * 1000; // 5 минут

  // Функция получения статистики
  const fetchStatistics = useCallback(async (force = false) => {
    if (!studentId || studentId <= 0) {
      setHasError('Некорректный ID студента');
      return;
    }

    const cacheKey = `statistics-${studentId}`;
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();

    // Проверяем кэш
    if (!force && cached && (now - cached.timestamp) < CACHE_DURATION) {
      const cachedData = cached.data;
      setStudentData(cachedData);
      setTournamentTables(cachedData.tournament_tables);
      updateChartData(cachedData, selectedSubject, selectedMetric);
      return;
    }

    try {
      setIsLoading(true);
      setHasError(null);

      const response = await statisticsAPI.getStudentStatistics(studentId, {
        period: 'monthly',
        include_tournaments: true
      });
      
      setStudentData(response);
      setTournamentTables(response.tournament_tables);
      updateChartData(response, selectedSubject, selectedMetric);

      // Кэшируем результат
      cacheRef.current.set(cacheKey, {
        data: response,
        timestamp: now
      });

    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
      
      if (error instanceof StatisticsAPIError) {
        setHasError(error.message);
      } else {
        setHasError('Произошла ошибка при загрузке статистики');
      }
      
      // В случае ошибки показываем пустые данные
      setStudentData(null);
      setChartData([]);
      setTournamentTables([]);
    } finally {
      setIsLoading(false);
    }
  }, [studentId, selectedSubject, selectedMetric]);

  // Функция обновления данных графика
  const updateChartData = useCallback((
    data: StudentStatisticsResponse, 
    subject: Subject, 
    metric: StatisticType
  ) => {
    if (!data) {
      setChartData([]);
      return;
    }

    const subjectData = subject === SUBJECTS.CHEMISTRY ? data.chemistry : data.biology;
    let newChartData: GradePoint[] = [];

    switch (metric) {
      case STATISTIC_TYPES.CURRENT_GRADES:
        newChartData = subjectData.current_grades;
        break;
      case STATISTIC_TYPES.TESTS:
        newChartData = subjectData.tests;
        break;
      case STATISTIC_TYPES.DTM:
        newChartData = subjectData.dtm;
        break;
      case STATISTIC_TYPES.SECTION_EXAMS:
        newChartData = subjectData.section_exams;
        break;
      case STATISTIC_TYPES.BLOCK_EXAMS:
        newChartData = subjectData.block_exams;
        break;
      default:
        newChartData = subjectData.current_grades;
    }

    setChartData(newChartData);
  }, []);

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
  const handleSubjectChange = useCallback((subject: Subject) => {
    setSelectedSubject(subject);
    if (studentData) {
      updateChartData(studentData, subject, selectedMetric);
    }
  }, [studentData, selectedMetric, updateChartData]);

  const handleMetricChange = useCallback((metric: StatisticType) => {
    setSelectedMetric(metric);
    if (studentData) {
      updateChartData(studentData, selectedSubject, metric);
    }
  }, [studentData, selectedSubject, updateChartData]);

  const handleTableChange = useCallback((table: TableType) => {
    setSelectedTable(table);
  }, []);

  const handleRefresh = useCallback(() => {
    fetchStatistics(true);
  }, [fetchStatistics]);

  // Эффект для загрузки данных при изменении студента
  useEffect(() => {
    fetchStatistics();
  }, [fetchStatistics]);

  // Эффект для обновления графика при изменении фильтров
  useEffect(() => {
    if (studentData) {
      updateChartData(studentData, selectedSubject, selectedMetric);
    }
  }, [studentData, selectedSubject, selectedMetric, updateChartData]);

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
    // Состояние
    selectedSubject,
    selectedMetric,
    selectedTable,
    
    // Данные
    studentData,
    chartData,
    tournamentTables,
    
    // Состояние загрузки
    isLoading,
    isValidating,
    hasError,
    
    // Обработчики
    handleSubjectChange,
    handleMetricChange,
    handleTableChange,
    handleRefresh
  };
};

// ========== ХУК ДЛЯ ПРОГРЕССА ПО ПРЕДМЕТУ ==========

export const useSubjectProgress = (
  studentId: number, 
  subject: Subject,
  metricType: StatisticType = STATISTIC_TYPES.CURRENT_GRADES
): UseSubjectProgressReturn => {
  const [state, setState] = useState<UseSubjectProgressState>({
    progressData: null,
    chartData: [],
    loading: false,
    error: null
  });

  const fetchProgress = useCallback(async () => {
    if (!studentId || studentId <= 0) {
      setState(prev => ({ ...prev, error: 'Некорректный ID студента' }));
      return;
    }

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const response = await statisticsAPI.getSubjectProgress(studentId, subject, {
        metric_type: metricType,
        period: 'monthly'
      });

      const chartData = response.progress_data[metricType] || [];

      setState(prev => ({
        ...prev,
        progressData: response,
        chartData,
        loading: false
      }));

    } catch (error) {
      console.error('Ошибка загрузки прогресса:', error);
      
      const errorMessage = error instanceof StatisticsAPIError 
        ? error.message 
        : 'Ошибка загрузки прогресса по предмету';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
    }
  }, [studentId, subject, metricType]);

  const refreshProgress = useCallback(() => {
    fetchProgress();
  }, [fetchProgress]);

  const getChartData = useCallback((metric: StatisticType): GradePoint[] => {
    if (!state.progressData) return [];
    return state.progressData.progress_data[metric] || [];
  }, [state.progressData]);

  useEffect(() => {
    fetchProgress();
  }, [fetchProgress]);

  return {
    ...state,
    refreshProgress,
    getChartData
  };
};

// ========== ХУК ДЛЯ ТУРНИРНОЙ ТАБЛИЦЫ ==========

export const useTournamentTable = (
  tableType: TableType,
  studentId: number,
  groupId?: number
): UseTournamentTableReturn => {
  const [state, setState] = useState<UseTournamentTableState>({
    ranking: null,
    loading: false,
    error: null
  });

  const fetchRanking = useCallback(async () => {
    if (!studentId || studentId <= 0) {
      setState(prev => ({ ...prev, error: 'Некорректный ID студента' }));
      return;
    }

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const response = await statisticsAPI.getRanking(tableType, studentId, {
        group_id: groupId,
        limit: 50
      });

      setState(prev => ({
        ...prev,
        ranking: response,
        loading: false
      }));

    } catch (error) {
      console.error('Ошибка загрузки рейтинга:', error);
      
      const errorMessage = error instanceof StatisticsAPIError 
        ? error.message 
        : 'Ошибка загрузки турнирной таблицы';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
    }
  }, [tableType, studentId, groupId]);

  const refreshRanking = useCallback(() => {
    fetchRanking();
  }, [fetchRanking]);

  const getStudentRank = useCallback((): number => {
    return state.ranking?.current_student_rank || 0;
  }, [state.ranking]);

  const getTopThree = useCallback((): StudentRankingInfo[] => {
    if (!state.ranking) return [];
    return state.ranking.students.slice(0, 3);
  }, [state.ranking]);

  const getCurrentStudent = useCallback((): StudentRankingInfo | null => {
    return state.ranking?.current_student || null;
  }, [state.ranking]);

  useEffect(() => {
    fetchRanking();
  }, [fetchRanking]);

  return {
    ...state,
    refreshRanking,
    getStudentRank,
    getTopThree,
    getCurrentStudent
  };
};

// ========== ХУК ДЛЯ ДЕТАЛЬНОЙ АНАЛИТИКИ ==========

export const usePerformanceInsights = (studentId: number) => {
  const [insights, setInsights] = useState<PerformanceInsights | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInsights = useCallback(async () => {
    if (!studentId || studentId <= 0) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await statisticsAPI.getDetailedInsights(studentId);
      setInsights(response.performance_insights);
    } catch (error) {
      console.error('Ошибка загрузки аналитики:', error);
      
      const errorMessage = error instanceof StatisticsAPIError 
        ? error.message 
        : 'Ошибка загрузки аналитических данных';
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  return {
    insights,
    loading,
    error,
    refresh: fetchInsights
  };
};

// ========== ХУК ДЛЯ СРАВНЕНИЯ СТУДЕНТОВ ==========

export const useStudentComparison = (studentIds: number[]) => {
  const [comparisonData, setComparisonData] = useState<Record<number, StudentStatisticsResponse>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComparisonData = useCallback(async () => {
    if (!studentIds.length) return;

    try {
      setLoading(true);
      setError(null);

      const promises = studentIds.map(id => 
        statisticsAPI.getStudentStatistics(id, { include_tournaments: false })
      );

      const results = await Promise.allSettled(promises);
      const data: Record<number, StudentStatisticsResponse> = {};

      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          data[studentIds[index]] = result.value;
        }
      });

      setComparisonData(data);
    } catch (error) {
      console.error('Ошибка загрузки данных для сравнения:', error);
      setError('Ошибка загрузки данных для сравнения');
    } finally {
      setLoading(false);
    }
  }, [studentIds]);

  useEffect(() => {
    fetchComparisonData();
  }, [fetchComparisonData]);

  const getComparisonMetrics = useCallback(() => {
    const metrics = {
      chemistry_averages: [] as number[],
      biology_averages: [] as number[],
      overall_averages: [] as number[],
      attendance_rates: [] as number[]
    };

    Object.values(comparisonData).forEach(data => {
      metrics.chemistry_averages.push(data.chemistry.avg_current_grade);
      metrics.biology_averages.push(data.biology.avg_current_grade);
      metrics.overall_averages.push(data.overall.overall_average);
      metrics.attendance_rates.push(data.overall.attendance_rate);
    });

    return metrics;
  }, [comparisonData]);

  return {
    comparisonData,
    loading,
    error,
    refresh: fetchComparisonData,
    getComparisonMetrics
  };
};

// ========== ХУК ДЛЯ ГРАФИКОВ ==========

export const useChartData = (
  studentData: StudentStatisticsResponse | null,
  subject: Subject,
  metric: StatisticType
) => {
  const [chartData, setChartData] = useState<GradePoint[]>([]);
  const [maxValue, setMaxValue] = useState<number>(10);

  useEffect(() => {
    if (!studentData) {
      setChartData([]);
      return;
    }

    const subjectData = subject === SUBJECTS.CHEMISTRY ? studentData.chemistry : studentData.biology;
    let data: GradePoint[] = [];

    switch (metric) {
      case STATISTIC_TYPES.CURRENT_GRADES:
        data = subjectData.current_grades;
        setMaxValue(10);
        break;
      case STATISTIC_TYPES.TESTS:
        data = subjectData.tests;
        setMaxValue(10);
        break;
      case STATISTIC_TYPES.DTM:
        data = subjectData.dtm;
        setMaxValue(189);
        break;
      case STATISTIC_TYPES.SECTION_EXAMS:
        data = subjectData.section_exams;
        setMaxValue(10);
        break;
      case STATISTIC_TYPES.BLOCK_EXAMS:
        data = subjectData.block_exams;
        setMaxValue(10);
        break;
      default:
        data = subjectData.current_grades;
        setMaxValue(10);
    }

    setChartData(data);
  }, [studentData, subject, metric]);

  const getChartColor = useCallback(() => {
    return statisticsAPI.getChartColor(subject);
  }, [subject]);

  const calculateTrend = useCallback(() => {
    return statisticsAPI.calculateImprovement(chartData);
  }, [chartData]);

  const getLastMonthAverage = useCallback(() => {
    return statisticsAPI.getLastMonthAverage(chartData);
  }, [chartData]);

  return {
    chartData,
    maxValue,
    getChartColor,
    calculateTrend,
    getLastMonthAverage
  };
};

// ========== ХУК ДЛЯ УВЕДОМЛЕНИЙ О ДОСТИЖЕНИЯХ ==========

export const useAchievements = (studentId: number) => {
  const [achievements, setAchievements] = useState<string[]>([]);
  const [newAchievements, setNewAchievements] = useState<string[]>([]);

  const checkAchievements = useCallback(async (data: StudentStatisticsResponse) => {
    const newAchievements: string[] = [];

    // Проверяем достижения
    if (data.chemistry.avg_current_grade >= 9) {
      newAchievements.push('Отличник по химии');
    }

    if (data.biology.avg_current_grade >= 9) {
      newAchievements.push('Отличник по биологии');
    }

    if (data.overall.attendance_rate >= 95) {
      newAchievements.push('Идеальная посещаемость');
    }

    if (data.overall.best_dtm_score >= 180) {
      newAchievements.push('ДТМ мастер');
    }

    // Проверяем новые достижения
    const truly_new = newAchievements.filter(achievement => 
      !achievements.includes(achievement)
    );

    if (truly_new.length > 0) {
      setNewAchievements(truly_new);
      setAchievements(prev => [...prev, ...truly_new]);
    }
  }, [achievements]);

  const clearNewAchievements = useCallback(() => {
    setNewAchievements([]);
  }, []);

  return {
    achievements,
    newAchievements,
    checkAchievements,
    clearNewAchievements
  };
};

// ========== ХУК ДЛЯ ЭКСПОРТА ДАННЫХ ==========

export const useDataExport = () => {
  const [exporting, setExporting] = useState(false);

  const exportToPDF = useCallback(async (data: StudentStatisticsResponse) => {
    setExporting(true);
    try {
      // Здесь была бы логика экспорта в PDF
      console.log('Экспорт в PDF:', data);
      
      // Имитация асинхронной операции
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Создание blob и скачивание
      const blob = new Blob(['PDF content'], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `statistics_${data.student_name}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Ошибка экспорта:', error);
    } finally {
      setExporting(false);
    }
  }, []);

  const exportToExcel = useCallback(async (data: StudentStatisticsResponse) => {
    setExporting(true);
    try {
      // Здесь была бы логика экспорта в Excel
      console.log('Экспорт в Excel:', data);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const blob = new Blob(['Excel content'], { type: 'application/vnd.ms-excel' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `statistics_${data.student_name}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Ошибка экспорта:', error);
    } finally {
      setExporting(false);
    }
  }, []);

  return {
    exporting,
    exportToPDF,
    exportToExcel
  };
};

// ========== ХУК ДЛЯ НАСТРОЕК ОТОБРАЖЕНИЯ ==========

export const useDisplaySettings = () => {
  const [settings, setSettings] = useState({
    showTrends: true,
    showComparisons: true,
    chartType: 'line' as 'line' | 'bar',
    timeRange: 'all' as 'all' | '6months' | '3months' | '1month'
  });

  const updateSetting = useCallback((key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  const resetSettings = useCallback(() => {
    setSettings({
      showTrends: true,
      showComparisons: true,
      chartType: 'line',
      timeRange: 'all'
    });
  }, []);

  return {
    settings,
    updateSetting,
    resetSettings
  };
};

// ========== ЭКСПОРТ ==========

export default useStatisticsPage;