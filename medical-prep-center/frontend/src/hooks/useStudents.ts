import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  studentProfileAPI, 
  StudentProfileAPIError
} from '../services/api/student_dashboard';
import type { 
  StudentProfile,
  TestResult,
  AttendanceRecord,
  Comment,
  University,
  StudentStatistics,
  Subject,
  CommentType,
  AttendanceStatus
} from '../services/api/student_dashboard';

// ========== ТИПЫ ==========

interface UseStudentProfileState {
  // Данные профиля
  profile: StudentProfile | null;
  
  // Состояние загрузки
  isLoading: boolean;
  isValidating: boolean;
  hasError: string | null;
  
  // Обработчики
  refreshProfile: () => void;
  updateStudentInfo: (data: UpdateStudentInfoData) => Promise<boolean>;
  updateGoal: (goal: string) => Promise<boolean>;
  addUniversity: (universityId: number, priority: number) => Promise<boolean>;
  removeUniversity: (universityId: number) => Promise<boolean>;
}

interface UseStudentTestsState {
  tests: TestResult[];
  statistics: {
    total_count: number;
    average_score: number;
    passed_count: number;
    failed_count: number;
  };
  isLoading: boolean;
  hasError: string | null;
}

interface UseStudentTestsReturn extends UseStudentTestsState {
  loadTests: (filters?: TestsFilter) => void;
  refreshTests: () => void;
}

interface UseStudentAttendanceState {
  attendanceRecords: AttendanceRecord[];
  statistics: {
    total_count: number;
    attendance_rate: number;
    present_count: number;
    absent_count: number;
    late_count: number;
  };
  isLoading: boolean;
  hasError: string | null;
}

interface UseStudentAttendanceReturn extends UseStudentAttendanceState {
  loadAttendance: (filters?: AttendanceFilter) => void;
  refreshAttendance: () => void;
}

interface UseStudentCommentsState {
  comments: Comment[];
  statistics: {
    total_count: number;
    positive_count: number;
    negative_count: number;
    neutral_count: number;
  };
  isLoading: boolean;
  hasError: string | null;
}

interface UseStudentCommentsReturn extends UseStudentCommentsState {
  loadComments: (filters?: CommentsFilter) => void;
  refreshComments: () => void;
}

// Типы для фильтров
interface TestsFilter {
  subject_name?: Subject;
  test_type?: string;
  passed_only?: boolean;
  limit?: number;
}

interface AttendanceFilter {
  subject_name?: Subject;
  limit?: number;
}

interface CommentsFilter {
  comment_type?: CommentType;
  limit?: number;
}

interface UpdateStudentInfoData {
  hobby?: string;
  sex?: string;
  address?: string;
  birthday?: string;
  goal?: string;
}

// ========== ОСНОВНОЙ ХУК ПРОФИЛЯ ==========

export const useStudentProfile = (studentId: number): UseStudentProfileState => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [hasError, setHasError] = useState<string | null>(null);
  
  // Кэш для избежания повторных запросов
  const cacheRef = useRef<Map<string, { data: StudentProfile; timestamp: number }>>(new Map());
  const CACHE_DURATION = 5 * 60 * 1000; // 5 минут

  // Функция загрузки профиля
  const loadProfile = useCallback(async (force = false) => {
    if (!studentId || studentId <= 0) {
      setHasError('Некорректный ID студента');
      return;
    }

    const cacheKey = `profile-${studentId}`;
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();

    // Проверяем кэш
    if (!force && cached && (now - cached.timestamp) < CACHE_DURATION) {
      setProfile(cached.data);
      return;
    }

    try {
      setIsLoading(true);
      setHasError(null);

      const profileData = await studentProfileAPI.getStudentProfile(studentId);
      
      setProfile(profileData);

      // Кэшируем результат
      cacheRef.current.set(cacheKey, {
        data: profileData,
        timestamp: now
      });

    } catch (error) {
      console.error('Ошибка загрузки профиля:', error);
      
      if (error instanceof StudentProfileAPIError) {
        setHasError(error.message);
      } else {
        setHasError('Произошла ошибка при загрузке профиля');
      }
      
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  }, [studentId]);

  // Функция валидации (фоновое обновление)
  const validateProfile = useCallback(async () => {
    if (isLoading) return;
    
    try {
      setIsValidating(true);
      await loadProfile(true);
    } catch (error) {
      // Валидация не должна показывать ошибки пользователю
      console.warn('Ошибка валидации профиля:', error);
    } finally {
      setIsValidating(false);
    }
  }, [loadProfile, isLoading]);

  // Обновление информации о студенте
  const updateStudentInfo = useCallback(async (data: UpdateStudentInfoData): Promise<boolean> => {
    if (!studentId || studentId <= 0) return false;

    try {
      const updatedInfo = await studentProfileAPI.updateStudentInfo(studentId, data);
      
      // Обновляем профиль в состоянии
      if (profile) {
        setProfile(prev => prev ? {
          ...prev,
          student_info: {
            ...prev.student_info,
            ...updatedInfo
          }
        } : null);
      }

      // Инвалидируем кэш
      cacheRef.current.delete(`profile-${studentId}`);
      
      return true;
    } catch (error) {
      console.error('Ошибка обновления информации:', error);
      return false;
    }
  }, [studentId, profile]);

  // Обновление цели студента
  const updateGoal = useCallback(async (goal: string): Promise<boolean> => {
    if (!studentId || studentId <= 0) return false;

    try {
      await studentProfileAPI.updateStudentGoal(studentId, goal);
      
      // Обновляем профиль в состоянии
      if (profile) {
        setProfile(prev => prev ? {
          ...prev,
          student_info: {
            ...prev.student_info,
            goal
          }
        } : null);
      }

      // Инвалидируем кэш
      cacheRef.current.delete(`profile-${studentId}`);
      
      return true;
    } catch (error) {
      console.error('Ошибка обновления цели:', error);
      return false;
    }
  }, [studentId, profile]);

  // Добавление университета
  const addUniversity = useCallback(async (universityId: number, priority: number): Promise<boolean> => {
    if (!studentId || studentId <= 0) return false;

    try {
      await studentProfileAPI.addUniversityToStudent(studentId, universityId, priority);
      
      // Перезагружаем профиль
      await loadProfile(true);
      
      return true;
    } catch (error) {
      console.error('Ошибка добавления университета:', error);
      return false;
    }
  }, [studentId, loadProfile]);

  // Удаление университета
  const removeUniversity = useCallback(async (universityId: number): Promise<boolean> => {
    if (!studentId || studentId <= 0) return false;

    try {
      await studentProfileAPI.removeUniversityFromStudent(studentId, universityId);
      
      // Перезагружаем профиль
      await loadProfile(true);
      
      return true;
    } catch (error) {
      console.error('Ошибка удаления университета:', error);
      return false;
    }
  }, [studentId, loadProfile]);

  // Обновление профиля
  const refreshProfile = useCallback(() => {
    loadProfile(true);
  }, [loadProfile]);

  // Эффект для загрузки данных при монтировании
  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  // Эффект для периодической валидации
  useEffect(() => {
    const interval = setInterval(validateProfile, 30000); // Каждые 30 секунд
    return () => clearInterval(interval);
  }, [validateProfile]);

  // Очистка кэша при размонтировании
  useEffect(() => {
    return () => {
      cacheRef.current.clear();
    };
  }, []);

  return {
    profile,
    isLoading,
    isValidating,
    hasError,
    refreshProfile,
    updateStudentInfo,
    updateGoal,
    addUniversity,
    removeUniversity
  };
};

// ========== ХУК ДЛЯ ТЕСТОВ СТУДЕНТА ==========

export const useStudentTests = (studentId: number): UseStudentTestsReturn => {
  const [state, setState] = useState<UseStudentTestsState>({
    tests: [],
    statistics: {
      total_count: 0,
      average_score: 0,
      passed_count: 0,
      failed_count: 0
    },
    isLoading: false,
    hasError: null
  });

  const currentFiltersRef = useRef<TestsFilter>({});

  // Загрузка тестов
  const loadTests = useCallback(async (filters: TestsFilter = {}) => {
    if (!studentId || studentId <= 0) {
      setState(prev => ({ ...prev, hasError: 'Некорректный ID студента' }));
      return;
    }

    currentFiltersRef.current = filters;

    try {
      setState(prev => ({ ...prev, isLoading: true, hasError: null }));

      const response = await studentProfileAPI.getStudentTests(studentId, filters);
      
      setState(prev => ({
        ...prev,
        tests: response.tests,
        statistics: {
          total_count: response.total_count,
          average_score: response.average_score,
          passed_count: response.passed_count,
          failed_count: response.failed_count
        },
        isLoading: false
      }));

    } catch (error) {
      console.error('Ошибка загрузки тестов:', error);
      
      const errorMessage = error instanceof StudentProfileAPIError 
        ? error.message 
        : 'Произошла ошибка при загрузке тестов';
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        hasError: errorMessage,
        tests: [],
        statistics: {
          total_count: 0,
          average_score: 0,
          passed_count: 0,
          failed_count: 0
        }
      }));
    }
  }, [studentId]);

  // Обновление тестов
  const refreshTests = useCallback(() => {
    loadTests(currentFiltersRef.current);
  }, [loadTests]);

  // Загрузка при монтировании
  useEffect(() => {
    loadTests();
  }, [loadTests]);

  return {
    ...state,
    loadTests,
    refreshTests
  };
};

// ========== ХУК ДЛЯ ПОСЕЩАЕМОСТИ СТУДЕНТА ==========

export const useStudentAttendance = (studentId: number): UseStudentAttendanceReturn => {
  const [state, setState] = useState<UseStudentAttendanceState>({
    attendanceRecords: [],
    statistics: {
      total_count: 0,
      attendance_rate: 0,
      present_count: 0,
      absent_count: 0,
      late_count: 0
    },
    isLoading: false,
    hasError: null
  });

  const currentFiltersRef = useRef<AttendanceFilter>({});

  // Загрузка посещаемости
  const loadAttendance = useCallback(async (filters: AttendanceFilter = {}) => {
    if (!studentId || studentId <= 0) {
      setState(prev => ({ ...prev, hasError: 'Некорректный ID студента' }));
      return;
    }

    currentFiltersRef.current = filters;

    try {
      setState(prev => ({ ...prev, isLoading: true, hasError: null }));

      const response = await studentProfileAPI.getStudentAttendance(studentId, filters);
      
      setState(prev => ({
        ...prev,
        attendanceRecords: response.attendance_records,
        statistics: {
          total_count: response.total_count,
          attendance_rate: response.attendance_rate,
          present_count: response.present_count,
          absent_count: response.absent_count,
          late_count: response.late_count
        },
        isLoading: false
      }));

    } catch (error) {
      console.error('Ошибка загрузки посещаемости:', error);
      
      const errorMessage = error instanceof StudentProfileAPIError 
        ? error.message 
        : 'Произошла ошибка при загрузке посещаемости';
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        hasError: errorMessage,
        attendanceRecords: [],
        statistics: {
          total_count: 0,
          attendance_rate: 0,
          present_count: 0,
          absent_count: 0,
          late_count: 0
        }
      }));
    }
  }, [studentId]);

  // Обновление посещаемости
  const refreshAttendance = useCallback(() => {
    loadAttendance(currentFiltersRef.current);
  }, [loadAttendance]);

  // Загрузка при монтировании
  useEffect(() => {
    loadAttendance();
  }, [loadAttendance]);

  return {
    ...state,
    loadAttendance,
    refreshAttendance
  };
};

// ========== ХУК ДЛЯ КОММЕНТАРИЕВ О СТУДЕНТЕ ==========

export const useStudentComments = (studentId: number): UseStudentCommentsReturn => {
  const [state, setState] = useState<UseStudentCommentsState>({
    comments: [],
    statistics: {
      total_count: 0,
      positive_count: 0,
      negative_count: 0,
      neutral_count: 0
    },
    isLoading: false,
    hasError: null
  });

  const currentFiltersRef = useRef<CommentsFilter>({});

  // Загрузка комментариев
  const loadComments = useCallback(async (filters: CommentsFilter = {}) => {
    if (!studentId || studentId <= 0) {
      setState(prev => ({ ...prev, hasError: 'Некорректный ID студента' }));
      return;
    }

    currentFiltersRef.current = filters;

    try {
      setState(prev => ({ ...prev, isLoading: true, hasError: null }));

      const response = await studentProfileAPI.getStudentComments(studentId, filters);
      
      setState(prev => ({
        ...prev,
        comments: response.comments,
        statistics: {
          total_count: response.total_count,
          positive_count: response.positive_count,
          negative_count: response.negative_count,
          neutral_count: response.neutral_count
        },
        isLoading: false
      }));

    } catch (error) {
      console.error('Ошибка загрузки комментариев:', error);
      
      const errorMessage = error instanceof StudentProfileAPIError 
        ? error.message 
        : 'Произошла ошибка при загрузке комментариев';
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        hasError: errorMessage,
        comments: [],
        statistics: {
          total_count: 0,
          positive_count: 0,
          negative_count: 0,
          neutral_count: 0
        }
      }));
    }
  }, [studentId]);

  // Обновление комментариев
  const refreshComments = useCallback(() => {
    loadComments(currentFiltersRef.current);
  }, [loadComments]);

  // Загрузка при монтировании
  useEffect(() => {
    loadComments();
  }, [loadComments]);

  return {
    ...state,
    loadComments,
    refreshComments
  };
};

// ========== ХУК ДЛЯ СТАТИСТИКИ СТУДЕНТА ==========

export const useStudentStatistics = (studentId: number) => {
  const [statistics, setStatistics] = useState<StudentStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatistics = useCallback(async () => {
    if (!studentId || studentId <= 0) return;

    try {
      setLoading(true);
      setError(null);
      
      const stats = await studentProfileAPI.getStudentStatistics(studentId);
      setStatistics(stats);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
      
      const errorMessage = error instanceof StudentProfileAPIError 
        ? error.message 
        : 'Ошибка загрузки статистики';
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    fetchStatistics();
  }, [fetchStatistics]);

  return {
    statistics,
    loading,
    error,
    refresh: fetchStatistics
  };
};

// ========== ХУК ДЛЯ АНАЛИТИКИ УСПЕВАЕМОСТИ ==========

export const useStudentAnalytics = (profile: StudentProfile | null) => {
  const [analytics, setAnalytics] = useState<{
    objects: { value1: number; value2: number };
    motions: { value1: number; value2: number; value3: number };
    skills: { value1: number; value2: number; value3: number };
  } | null>(null);

  useEffect(() => {
    if (!profile?.analytics) {
      setAnalytics(null);
      return;
    }

    const { correct_by_category, mistakes_by_category } = profile.analytics;
    
    // Конвертируем аналитику в формат для круговых диаграмм
    // Это упрощенная логика - в реальности нужно мапить категории правильно
    
    const totalCorrect = Object.values(correct_by_category).reduce((sum, val) => sum + val, 0);
    const totalMistakes = Object.values(mistakes_by_category).reduce((sum, val) => sum + val, 0);
    
    // Objects (правильные/неправильные)
    const objects = {
      value1: totalCorrect || 40,
      value2: totalMistakes || 60
    };
    
    // Motions (разбиваем на 3 категории)
    const categories = Object.keys(correct_by_category);
    const motions = {
      value1: correct_by_category[categories[0]] || 30,
      value2: correct_by_category[categories[1]] || 20,
      value3: correct_by_category[categories[2]] || 50
    };
    
    // Skills (навыки)
    const skills = {
      value1: Math.round(profile.analytics.accuracy_percentage * 0.1) || 10,
      value2: Math.round(profile.analytics.accuracy_percentage * 0.3) || 30,
      value3: Math.round(profile.analytics.accuracy_percentage * 0.6) || 60
    };

    setAnalytics({ objects, motions, skills });
    
  }, [profile]);

  return analytics;
};

// ========== ХУК ДЛЯ УПРАВЛЕНИЯ УНИВЕРСИТЕТАМИ ==========

export const useStudentUniversities = (studentId: number) => {
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUniversities = useCallback(async () => {
    if (!studentId || studentId <= 0) return;

    try {
      setLoading(true);
      setError(null);
      
      const unis = await studentProfileAPI.getStudentUniversities(studentId);
      setUniversities(unis);
    } catch (error) {
      console.error('Ошибка загрузки университетов:', error);
      
      const errorMessage = error instanceof StudentProfileAPIError 
        ? error.message 
        : 'Ошибка загрузки университетов';
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  const addUniversity = useCallback(async (universityId: number, priority: number): Promise<boolean> => {
    try {
      await studentProfileAPI.addUniversityToStudent(studentId, universityId, priority);
      await fetchUniversities(); // Перезагружаем список
      return true;
    } catch (error) {
      console.error('Ошибка добавления университета:', error);
      return false;
    }
  }, [studentId, fetchUniversities]);

  const removeUniversity = useCallback(async (universityId: number): Promise<boolean> => {
    try {
      await studentProfileAPI.removeUniversityFromStudent(studentId, universityId);
      await fetchUniversities(); // Перезагружаем список
      return true;
    } catch (error) {
      console.error('Ошибка удаления университета:', error);
      return false;
    }
  }, [studentId, fetchUniversities]);

  useEffect(() => {
    fetchUniversities();
  }, [fetchUniversities]);

  return {
    universities,
    loading,
    error,
    addUniversity,
    removeUniversity,
    refresh: fetchUniversities
  };
};

// ========== ХУК ДЛЯ ФИЛЬТРАЦИИ И ПОИСКА ==========

export const useStudentDataFilters = () => {
  const [filters, setFilters] = useState({
    subject: 'all' as Subject | 'all',
    testType: 'all' as string,
    attendanceStatus: 'all' as AttendanceStatus | 'all',
    commentType: 'all' as CommentType | 'all',
    dateRange: {
      from: '',
      to: ''
    },
    searchQuery: ''
  });

  const updateFilter = useCallback((key: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters({
      subject: 'all',
      testType: 'all',
      attendanceStatus: 'all',
      commentType: 'all',
      dateRange: { from: '', to: '' },
      searchQuery: ''
    });
  }, []);

  // Функции для фильтрации данных
  const filterTests = useCallback((tests: TestResult[]) => {
    return tests.filter(test => {
      if (filters.subject !== 'all' && test.subject_name.toLowerCase() !== filters.subject) {
        return false;
      }
      if (filters.testType !== 'all' && test.test_type !== filters.testType) {
        return false;
      }
      if (filters.searchQuery && !test.topic_name.toLowerCase().includes(filters.searchQuery.toLowerCase())) {
        return false;
      }
      return true;
    });
  }, [filters]);

  const filterAttendance = useCallback((records: AttendanceRecord[]) => {
    return records.filter(record => {
      if (filters.subject !== 'all' && record.subject_name.toLowerCase() !== filters.subject) {
        return false;
      }
      if (filters.attendanceStatus !== 'all' && record.att_status !== filters.attendanceStatus) {
        return false;
      }
      if (filters.searchQuery && record.topic_name && !record.topic_name.toLowerCase().includes(filters.searchQuery.toLowerCase())) {
        return false;
      }
      return true;
    });
  }, [filters]);

  const filterComments = useCallback((comments: Comment[]) => {
    return comments.filter(comment => {
      if (filters.commentType !== 'all' && comment.comment_type !== filters.commentType) {
        return false;
      }
      if (filters.searchQuery && !comment.comment_text.toLowerCase().includes(filters.searchQuery.toLowerCase())) {
        return false;
      }
      return true;
    });
  }, [filters]);

  return {
    filters,
    updateFilter,
    resetFilters,
    filterTests,
    filterAttendance,
    filterComments
  };
};

// ========== ХУК ДЛЯ УПРАВЛЕНИЯ СОСТОЯНИЕМ СТРАНИЦЫ ==========

export const useStudentDashboard = (studentId: number) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'tests' | 'attendance' | 'comments' | 'universities'>('overview');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [isEditing, setIsEditing] = useState(false);

  // Получаем все данные
  const profile = useStudentProfile(studentId);
  const tests = useStudentTests(studentId);
  const attendance = useStudentAttendance(studentId);
  const comments = useStudentComments(studentId);
  const analytics = useStudentAnalytics(profile.profile);
  const filters = useStudentDataFilters();

  // Управление разворачиванием секций
  const toggleSection = useCallback((sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  }, []);

  // Переключение режима редактирования
  const toggleEditing = useCallback(() => {
    setIsEditing(prev => !prev);
  }, []);

  // Сохранение изменений
  const saveChanges = useCallback(async (data: UpdateStudentInfoData): Promise<boolean> => {
    const success = await profile.updateStudentInfo(data);
    if (success) {
      setIsEditing(false);
    }
    return success;
  }, [profile]);

  // Обновление всех данных
  const refreshAllData = useCallback(() => {
    profile.refreshProfile();
    tests.refreshTests();
    attendance.refreshAttendance();
    comments.refreshComments();
  }, [profile, tests, attendance, comments]);

  return {
    // Состояние страницы
    activeTab,
    setActiveTab,
    expandedSections,
    toggleSection,
    isEditing,
    toggleEditing,
    
    // Данные
    profile: profile.profile,
    tests: tests.tests,
    attendance: attendance.attendanceRecords,
    comments: comments.comments,
    analytics,
    
    // Статистика
    testStatistics: tests.statistics,
    attendanceStatistics: attendance.statistics,
    commentStatistics: comments.statistics,
    
    // Состояние загрузки
    isLoading: profile.isLoading || tests.isLoading || attendance.isLoading || comments.isLoading,
    hasError: profile.hasError || tests.hasError || attendance.hasError || comments.hasError,
    
    // Действия
    saveChanges,
    refreshAllData,
    updateGoal: profile.updateGoal,
    addUniversity: profile.addUniversity,
    removeUniversity: profile.removeUniversity,
    
    // Фильтры
    filters: filters.filters,
    updateFilter: filters.updateFilter,
    resetFilters: filters.resetFilters,
    filterTests: filters.filterTests,
    filterAttendance: filters.filterAttendance,
    filterComments: filters.filterComments,
    
    // Загрузка с фильтрами
    loadTests: tests.loadTests,
    loadAttendance: attendance.loadAttendance,
    loadComments: comments.loadComments
  };
};

// ========== ЭКСПОРТ ==========

export default useStudentProfile;