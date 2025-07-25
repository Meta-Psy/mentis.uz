import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  teacherAPI, 
  TeacherAPIError,
  COMMENT_TYPES
} from '../services/api/teacher_dashboard';
import type { 
  TeacherProfileInfo,
  GroupStudentsResponse,
  StudentDetailInfo,
  GroupScheduleInfo,
  StudentAnalyticsResponse,
  UpdateCommentRequest,
  CommentType,
} from '../services/api/teacher_dashboard';

// ========== ТИПЫ ==========

interface UseTeacherDashboardState {
  // Профиль преподавателя
  teacherProfile: TeacherProfileInfo | null;
  groups: GroupScheduleInfo[];
  totalStudents: number;
  
  // Состояние загрузки
  isLoading: boolean;
  isValidating: boolean;
  hasError: string | null;
  
  // Обработчики
  handleRefresh: () => void;
}

interface UseGroupStudentsState {
  // Данные
  groupData: GroupStudentsResponse | null;
  students: StudentDetailInfo[];
  
  // Фильтры и сортировка
  selectedGroup: number | null;
  includeInactive: boolean;
  sortBy: 'name' | 'score' | 'attendance' | 'last_seen';
  sortOrder: 'asc' | 'desc';
  
  // Расширенные студенты
  expandedStudents: Record<number, boolean>;
  
  // Состояние загрузки
  isLoading: boolean;
  hasError: string | null;
  
  // Обработчики
  handleGroupSelect: (groupId: number | null) => void;
  handleToggleInactive: () => void;
  handleSortChange: (field: 'name' | 'score' | 'attendance' | 'last_seen') => void;
  handleToggleStudent: (studentId: number) => void;
  handleRefresh: () => void;
}

interface UseStudentCommentsState {
  // Комментарии
  comments: Record<number, string>;
  commentTypes: Record<number, CommentType>;
  
  // Состояние сохранения
  savingComments: Record<number, boolean>;
  saveErrors: Record<number, string>;
  
  // Обработчики
  handleCommentChange: (studentId: number, comment: string) => void;
  handleCommentTypeChange: (studentId: number, type: CommentType) => void;
  handleSaveComment: (studentId: number) => Promise<boolean>;
  handleBulkSave: () => Promise<void>;
  initializeComments: (students: StudentDetailInfo[]) => void;
}

interface UseStudentAnalyticsState {
  // Аналитика
  analytics: Record<number, StudentAnalyticsResponse>;
  
  // Состояние загрузки
  loadingAnalytics: Record<number, boolean>;
  analyticsErrors: Record<number, string>;
  
  // Обработчики
  loadStudentAnalytics: (studentId: number) => Promise<void>;
  refreshAnalytics: (studentId: number) => Promise<void>;
  clearAnalytics: (studentId: number) => void;
}

// ========== ОСНОВНОЙ ХУК ДАШБОРДА ==========

export const useTeacherDashboard = (teacherId: number): UseTeacherDashboardState => {
  const [teacherProfile, setTeacherProfile] = useState<TeacherProfileInfo | null>(null);
  const [groups, setGroups] = useState<GroupScheduleInfo[]>([]);
  const [totalStudents, setTotalStudents] = useState(0);
  
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [hasError, setHasError] = useState<string | null>(null);
  
  // Кэш для избежания повторных запросов
  const cacheRef = useRef<Map<string, { data: any; timestamp: number }>>(new Map());
  const CACHE_DURATION = 5 * 60 * 1000; // 5 минут

  // Функция загрузки данных преподавателя
  const fetchTeacherData = useCallback(async (force = false) => {
    if (!teacherId || teacherId <= 0) {
      setHasError('Некорректный ID преподавателя');
      return;
    }

    const cacheKey = `teacher-${teacherId}`;
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();

    // Проверяем кэш
    if (!force && cached && (now - cached.timestamp) < CACHE_DURATION) {
      const { teacher_profile, groups: cachedGroups, total_students } = cached.data;
      setTeacherProfile(teacher_profile);
      setGroups(cachedGroups);
      setTotalStudents(total_students);
      return;
    }

    try {
      setIsLoading(true);
      setHasError(null);

      const response = await teacherAPI.getTeacherProfile(teacherId);
      
      setTeacherProfile(response.teacher_profile);
      setGroups(response.groups);
      setTotalStudents(response.total_students);

      // Кэшируем результат
      cacheRef.current.set(cacheKey, {
        data: response,
        timestamp: now
      });

    } catch (error) {
      console.error('Ошибка загрузки данных преподавателя:', error);
      
      if (error instanceof TeacherAPIError) {
        setHasError(error.message);
      } else {
        setHasError('Произошла ошибка при загрузке данных преподавателя');
      }
      
      // В случае ошибки показываем пустые данные
      setTeacherProfile(null);
      setGroups([]);
      setTotalStudents(0);
    } finally {
      setIsLoading(false);
    }
  }, [teacherId]);

  // Функция валидации (фоновое обновление)
  const validateData = useCallback(async () => {
    if (isLoading) return;
    
    try {
      setIsValidating(true);
      await fetchTeacherData(true);
    } catch (error) {
      // Валидация не должна показывать ошибки пользователю
      console.warn('Ошибка валидации:', error);
    } finally {
      setIsValidating(false);
    }
  }, [fetchTeacherData, isLoading]);

  // Обработчик обновления
  const handleRefresh = useCallback(() => {
    fetchTeacherData(true);
  }, [fetchTeacherData]);

  // Эффект для загрузки данных
  useEffect(() => {
    fetchTeacherData();
  }, [fetchTeacherData]);

  // Эффект для периодической валидации
  useEffect(() => {
    const interval = setInterval(validateData, 60000); // Каждую минуту
    return () => clearInterval(interval);
  }, [validateData]);

  // Очистка кэша при размонтировании
  useEffect(() => {
    return () => {
      cacheRef.current.clear();
    };
  }, []);

  return {
    teacherProfile,
    groups,
    totalStudents,
    isLoading,
    isValidating,
    hasError,
    handleRefresh
  };
};

// ========== ХУК ДЛЯ РАБОТЫ СО СТУДЕНТАМИ ГРУППЫ ==========

export const useGroupStudents = (): UseGroupStudentsState => {
  const [groupData, setGroupData] = useState<GroupStudentsResponse | null>(null);
  const [students, setStudents] = useState<StudentDetailInfo[]>([]);
  
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null);
  const [includeInactive, setIncludeInactive] = useState(false);
  const [sortBy, setSortBy] = useState<'name' | 'score' | 'attendance' | 'last_seen'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  
  const [expandedStudents, setExpandedStudents] = useState<Record<number, boolean>>({});
  
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState<string | null>(null);

  // Кэш
  const cacheRef = useRef<Map<string, { data: any; timestamp: number }>>(new Map());
  const CACHE_DURATION = 3 * 60 * 1000; // 3 минуты

  // Функция получения студентов группы
  const fetchGroupStudents = useCallback(async (groupId: number, force = false) => {
    const cacheKey = `group-${groupId}-${includeInactive}-${sortBy}-${sortOrder}`;
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();

    // Проверяем кэш
    if (!force && cached && (now - cached.timestamp) < CACHE_DURATION) {
      setGroupData(cached.data);
      setStudents(cached.data.students);
      return;
    }

    try {
      setIsLoading(true);
      setHasError(null);

      const response = await teacherAPI.getGroupStudents(groupId, {
        include_inactive: includeInactive,
        sort_by: sortBy,
        sort_order: sortOrder
      });
      
      setGroupData(response);
      setStudents(response.students);

      // Кэшируем результат
      cacheRef.current.set(cacheKey, {
        data: response,
        timestamp: now
      });

    } catch (error) {
      console.error('Ошибка загрузки студентов группы:', error);
      
      if (error instanceof TeacherAPIError) {
        setHasError(error.message);
      } else {
        setHasError('Произошла ошибка при загрузке студентов');
      }
      
      setGroupData(null);
      setStudents([]);
    } finally {
      setIsLoading(false);
    }
  }, [includeInactive, sortBy, sortOrder]);

  // Обработчики
  const handleGroupSelect = useCallback((groupId: number | null) => {
    setSelectedGroup(groupId);
    setExpandedStudents({}); // Сворачиваем всех студентов при смене группы
    
    if (groupId !== null) {
      fetchGroupStudents(groupId);
    } else {
      setGroupData(null);
      setStudents([]);
    }
  }, [fetchGroupStudents]);

  const handleToggleInactive = useCallback(() => {
    setIncludeInactive(prev => !prev);
  }, []);

  const handleSortChange = useCallback((field: 'name' | 'score' | 'attendance' | 'last_seen') => {
    if (sortBy === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  }, [sortBy]);

  const handleToggleStudent = useCallback((studentId: number) => {
    setExpandedStudents(prev => ({
      ...prev,
      [studentId]: !prev[studentId]
    }));
  }, []);

  const handleRefresh = useCallback(() => {
    if (selectedGroup !== null) {
      fetchGroupStudents(selectedGroup, true);
    }
  }, [selectedGroup, fetchGroupStudents]);

  // Эффект для обновления данных при изменении фильтров
  useEffect(() => {
    if (selectedGroup !== null) {
      fetchGroupStudents(selectedGroup);
    }
  }, [selectedGroup, fetchGroupStudents]);

  return {
    groupData,
    students,
    selectedGroup,
    includeInactive,
    sortBy,
    sortOrder,
    expandedStudents,
    isLoading,
    hasError,
    handleGroupSelect,
    handleToggleInactive,
    handleSortChange,
    handleToggleStudent,
    handleRefresh
  };
};

// ========== ХУК ДЛЯ РАБОТЫ С КОММЕНТАРИЯМИ ==========

export const useStudentComments = (teacherId: number): UseStudentCommentsState => {
  const [comments, setComments] = useState<Record<number, string>>({});
  const [commentTypes, setCommentTypes] = useState<Record<number, CommentType>>({});
  
  const [savingComments, setSavingComments] = useState<Record<number, boolean>>({});
  const [saveErrors, setSaveErrors] = useState<Record<number, string>>({});

  // Инициализация комментариев из данных студентов
  const initializeComments = useCallback((students: StudentDetailInfo[]) => {
    const newComments: Record<number, string> = {};
    const newCommentTypes: Record<number, CommentType> = {};
    
    students.forEach(student => {
      newComments[student.id] = student.comment_info.comment_text || '';
      newCommentTypes[student.id] = student.comment_info.comment_type || COMMENT_TYPES.NEUTRAL;
    });
    
    setComments(newComments);
    setCommentTypes(newCommentTypes);
  }, []);

  // Обработчики
  const handleCommentChange = useCallback((studentId: number, comment: string) => {
    setComments(prev => ({
      ...prev,
      [studentId]: comment
    }));
    
    // Очищаем ошибку при изменении комментария
    setSaveErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[studentId];
      return newErrors;
    });
  }, []);

  const handleCommentTypeChange = useCallback((studentId: number, type: CommentType) => {
    setCommentTypes(prev => ({
      ...prev,
      [studentId]: type
    }));
  }, []);

  const handleSaveComment = useCallback(async (studentId: number): Promise<boolean> => {
    if (!teacherId || teacherId <= 0) {
      setSaveErrors(prev => ({
        ...prev,
        [studentId]: 'Некорректный ID преподавателя'
      }));
      return false;
    }

    const commentText = comments[studentId]?.trim() || '';
    const commentType = commentTypes[studentId] || COMMENT_TYPES.NEUTRAL;

    if (!commentText) {
      setSaveErrors(prev => ({
        ...prev,
        [studentId]: 'Комментарий не может быть пустым'
      }));
      return false;
    }

    try {
      setSavingComments(prev => ({ ...prev, [studentId]: true }));
      setSaveErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[studentId];
        return newErrors;
      });

      const request: UpdateCommentRequest = {
        student_id: studentId,
        comment_text: commentText,
        comment_type: commentType
      };

      await teacherAPI.updateStudentComment(teacherId, request);
      
      return true;
    } catch (error) {
      console.error(`Ошибка сохранения комментария для студента ${studentId}:`, error);
      
      const errorMessage = error instanceof TeacherAPIError 
        ? error.message 
        : 'Ошибка сохранения комментария';
      
      setSaveErrors(prev => ({
        ...prev,
        [studentId]: errorMessage
      }));
      
      return false;
    } finally {
      setSavingComments(prev => ({ ...prev, [studentId]: false }));
    }
  }, [teacherId, comments, commentTypes]);

  const handleBulkSave = useCallback(async () => {
    const studentIds = Object.keys(comments).map(Number);
    const results = await Promise.allSettled(
      studentIds.map(id => handleSaveComment(id))
    );
    
    const successCount = results.filter(r => r.status === 'fulfilled' && r.value).length;
    const totalCount = results.length;
    
    if (successCount === totalCount) {
      console.log('Все комментарии сохранены успешно');
    } else {
      console.warn(`Сохранено ${successCount} из ${totalCount} комментариев`);
    }
  }, [comments, handleSaveComment]);

  return {
    comments,
    commentTypes,
    savingComments,
    saveErrors,
    handleCommentChange,
    handleCommentTypeChange,
    handleSaveComment,
    handleBulkSave,
    initializeComments
  };
};

// ========== ХУК ДЛЯ АНАЛИТИКИ СТУДЕНТОВ ==========

export const useStudentAnalytics = (): UseStudentAnalyticsState => {
  const [analytics, setAnalytics] = useState<Record<number, StudentAnalyticsResponse>>({});
  const [loadingAnalytics, setLoadingAnalytics] = useState<Record<number, boolean>>({});
  const [analyticsErrors, setAnalyticsErrors] = useState<Record<number, string>>({});

  // Кэш аналитики
  const analyticsCache = useRef<Map<number, { data: StudentAnalyticsResponse; timestamp: number }>>(new Map());
  const ANALYTICS_CACHE_DURATION = 10 * 60 * 1000; // 10 минут

  const loadStudentAnalytics = useCallback(async (studentId: number) => {
    // Проверяем кэш
    const cached = analyticsCache.current.get(studentId);
    const now = Date.now();
    
    if (cached && (now - cached.timestamp) < ANALYTICS_CACHE_DURATION) {
      setAnalytics(prev => ({
        ...prev,
        [studentId]: cached.data
      }));
      return;
    }

    try {
      setLoadingAnalytics(prev => ({ ...prev, [studentId]: true }));
      setAnalyticsErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[studentId];
        return newErrors;
      });

      const analyticsData = await teacherAPI.getStudentAnalytics(studentId);
      
      setAnalytics(prev => ({
        ...prev,
        [studentId]: analyticsData
      }));

      // Кэшируем результат
      analyticsCache.current.set(studentId, {
        data: analyticsData,
        timestamp: now
      });

    } catch (error) {
      console.error(`Ошибка загрузки аналитики студента ${studentId}:`, error);
      
      const errorMessage = error instanceof TeacherAPIError 
        ? error.message 
        : 'Ошибка загрузки аналитики';
      
      setAnalyticsErrors(prev => ({
        ...prev,
        [studentId]: errorMessage
      }));
    } finally {
      setLoadingAnalytics(prev => ({ ...prev, [studentId]: false }));
    }
  }, []);

  const refreshAnalytics = useCallback(async (studentId: number) => {
    // Удаляем из кэша для принудительного обновления
    analyticsCache.current.delete(studentId);
    await loadStudentAnalytics(studentId);
  }, [loadStudentAnalytics]);

  const clearAnalytics = useCallback((studentId: number) => {
    setAnalytics(prev => {
      const newAnalytics = { ...prev };
      delete newAnalytics[studentId];
      return newAnalytics;
    });
    
    setAnalyticsErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[studentId];
      return newErrors;
    });
    
    analyticsCache.current.delete(studentId);
  }, []);

  return {
    analytics,
    loadingAnalytics,
    analyticsErrors,
    loadStudentAnalytics,
    refreshAnalytics,
    clearAnalytics
  };
};

// ========== КОМПЛЕКСНЫЙ ХУК ДЛЯ СТРАНИЦЫ ПРЕПОДАВАТЕЛЯ ==========

export const useTeacherPage = (teacherId: number) => {
  // Основные хуки
  const dashboard = useTeacherDashboard(teacherId);
  const groupStudents = useGroupStudents();
  const comments = useStudentComments(teacherId);
  const analytics = useStudentAnalytics();

  // Объединенное состояние загрузки
  const isLoading = dashboard.isLoading || groupStudents.isLoading;
  const hasError = dashboard.hasError || groupStudents.hasError;

  // Инициализация комментариев при загрузке студентов
  useEffect(() => {
    if (groupStudents.students.length > 0) {
      comments.initializeComments(groupStudents.students);
    }
  }, [groupStudents.students, comments.initializeComments]);

  // Автоматическая загрузка аналитики для развернутых студентов
  useEffect(() => {
    const expandedStudentIds = Object.keys(groupStudents.expandedStudents)
      .map(Number)
      .filter(id => groupStudents.expandedStudents[id]);

    expandedStudentIds.forEach(studentId => {
      if (!analytics.analytics[studentId] && !analytics.loadingAnalytics[studentId]) {
        analytics.loadStudentAnalytics(studentId);
      }
    });
  }, [groupStudents.expandedStudents, analytics]);

  // Функция полного обновления страницы
  const handleFullRefresh = useCallback(() => {
    dashboard.handleRefresh();
    groupStudents.handleRefresh();
  }, [dashboard.handleRefresh, groupStudents.handleRefresh]);

  return {
    // Данные дашборда
    teacherProfile: dashboard.teacherProfile,
    groups: dashboard.groups,
    totalStudents: dashboard.totalStudents,
    
    // Данные студентов
    selectedGroup: groupStudents.selectedGroup,
    students: groupStudents.students,
    expandedStudents: groupStudents.expandedStudents,
    
    // Комментарии
    comments: comments.comments,
    commentTypes: comments.commentTypes,
    savingComments: comments.savingComments,
    saveErrors: comments.saveErrors,
    
    // Аналитика
    analytics: analytics.analytics,
    loadingAnalytics: analytics.loadingAnalytics,
    analyticsErrors: analytics.analyticsErrors,
    
    // Состояние загрузки
    isLoading,
    isValidating: dashboard.isValidating,
    hasError,
    
    // Обработчики группы
    handleGroupSelect: groupStudents.handleGroupSelect,
    handleToggleStudent: groupStudents.handleToggleStudent,
    
    // Обработчики комментариев
    handleCommentChange: comments.handleCommentChange,
    handleCommentTypeChange: comments.handleCommentTypeChange,
    handleSaveComment: comments.handleSaveComment,
    
    // Обработчики аналитики
    loadStudentAnalytics: analytics.loadStudentAnalytics,
    refreshAnalytics: analytics.refreshAnalytics,
    
    // Общие обработчики
    handleRefresh: handleFullRefresh
  };
};

// ========== ХУК ДЛЯ СТАТИСТИКИ ПРЕПОДАВАТЕЛЯ ==========

export const useTeacherStatistics = () => {
  const [statistics, setStatistics] = useState<{
    totalGroups: number;
    totalStudents: number;
    averageScore: number;
    averageAttendance: number;
    activeStudents: number;
    pendingComments: number;
  } | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calculateStatistics = useCallback((
    groups: GroupScheduleInfo[],
    allStudents: StudentDetailInfo[]
  ) => {
    const totalGroups = groups.length;
    const totalStudents = allStudents.length;
    
    const averageScore = totalStudents > 0 
      ? allStudents.reduce((sum, s) => sum + s.test_statistics.average_score, 0) / totalStudents
      : 0;
    
    const averageAttendance = totalStudents > 0
      ? allStudents.reduce((sum, s) => sum + s.attendance_info.attendance_rate, 0) / totalStudents
      : 0;
    
    const activeStudents = allStudents.filter(s => s.student_status === 'active').length;
    const pendingComments = allStudents.filter(s => !s.comment_info.comment_text.trim()).length;

    const newStats = {
      totalGroups,
      totalStudents,
      averageScore,
      averageAttendance,
      activeStudents,
      pendingComments
    };

    setStatistics(newStats);
    return newStats;
  }, []);

  const updateStatistics = useCallback((
    groups: GroupScheduleInfo[],
    allStudents: StudentDetailInfo[]
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const stats = calculateStatistics(groups, allStudents);
      setStatistics(stats);
    } catch (err) {
      setError('Ошибка расчета статистики');
      console.error('Statistics calculation error:', err);
    } finally {
      setLoading(false);
    }
  }, [calculateStatistics]);

  return {
    statistics,
    loading,
    error,
    calculateStatistics,
    updateStatistics
  };
};

// ========== ЭКСПОРТ ==========

export default useTeacherPage;