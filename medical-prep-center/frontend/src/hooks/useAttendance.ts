import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  assessmentAPI, 
  AssessmentAPIError,
  SUBJECTS
} from '../services/api/attendance';
import type { 
  StudentDetails,
  AttendanceCalendar,
  ModulePerformance,
  FinalGrade,
  Comment,
  StudentStatistics,
  Subject,
  PerformanceTopic,
  AttendanceMonth
} from '../services/api/attendance';

// ========== ТИПЫ ==========

interface UseParentDetailsState {
  // Состояние фильтров
  selectedSubject: Subject;
  selectedModule: number | 'all';
  activeTab: 'attendance' | 'performance';
  
  // Данные студента
  studentDetails: StudentDetails | null;
  attendanceCalendar: AttendanceCalendar | null;
  modulePerformance: ModulePerformance[];
  finalGrades: { [key: string]: FinalGrade };
  
  // Состояние загрузки
  isLoading: boolean;
  isValidating: boolean;
  hasError: string | null;
  
  // Обработчики
  handleSubjectChange: (subject: Subject) => void;
  handleModuleChange: (moduleId: number | 'all') => void;
  handleTabChange: (tab: 'attendance' | 'performance') => void;
  handleRefresh: () => void;
  
  // Вычисляемые данные
  modules: Array<{ id: string; name: string }>;
  currentSubjectData: any;
}

interface UseAttendanceCalendarState {
  calendar: AttendanceCalendar | null;
  loading: boolean;
  error: string | null;
}

interface UseAttendanceCalendarReturn extends UseAttendanceCalendarState {
  fetchCalendar: (studentId: number, subject: Subject, moduleId?: number) => Promise<void>;
  refresh: () => void;
  getAttendanceForMonth: (year: number, month: number) => AttendanceMonth | null;
}

interface UsePerformanceState {
  performance: ModulePerformance[];
  loading: boolean;
  error: string | null;
}

interface UsePerformanceReturn extends UsePerformanceState {
  fetchPerformance: (studentId: number, subject: Subject, moduleId?: number) => Promise<void>;
  refresh: () => void;
  getModuleById: (moduleId: number) => ModulePerformance | null;
  getTopicById: (moduleId: number, topicId: number) => PerformanceTopic | null;
}

// ========== ОСНОВНОЙ ХУК ==========

export const useParentDetails = (studentId: number): UseParentDetailsState => {
  // Состояние фильтров
  const [selectedSubject, setSelectedSubject] = useState<Subject>(SUBJECTS.CHEMISTRY);
  const [selectedModule, setSelectedModule] = useState<number | 'all'>('all');
  const [activeTab, setActiveTab] = useState<'attendance' | 'performance'>('attendance');
  
  // Данные
  const [studentDetails, setStudentDetails] = useState<StudentDetails | null>(null);
  const [attendanceCalendar, setAttendanceCalendar] = useState<AttendanceCalendar | null>(null);
  const [modulePerformance, setModulePerformance] = useState<ModulePerformance[]>([]);
  const [finalGrades, setFinalGrades] = useState<{ [key: string]: FinalGrade }>({});
  
  // Состояние загрузки
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [hasError, setHasError] = useState<string | null>(null);
  
  // Кэш для избежания повторных запросов
  const cacheRef = useRef<Map<string, { data: any; timestamp: number }>>(new Map());
  const CACHE_DURATION = 5 * 60 * 1000; // 5 минут
  
  // Текущие параметры для повторных запросов
  const paramsRef = useRef({ studentId, selectedSubject, selectedModule });

  // Функция получения полных данных студента
  const fetchStudentDetails = useCallback(async (force = false) => {
    if (!studentId || studentId <= 0) {
      setHasError('Некорректный ID студента');
      return;
    }

    const cacheKey = `student-details-${studentId}`;
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();

    // Проверяем кэш
    if (!force && cached && (now - cached.timestamp) < CACHE_DURATION) {
      setStudentDetails(cached.data);
      return;
    }

    try {
      setIsLoading(true);
      setHasError(null);

      const details = await assessmentAPI.getStudentDetails(studentId);
      setStudentDetails(details);

      // Кэшируем результат
      cacheRef.current.set(cacheKey, {
        data: details,
        timestamp: now
      });

    } catch (error) {
      console.error('Ошибка загрузки данных студента:', error);
      
      if (error instanceof AssessmentAPIError) {
        setHasError(error.message);
      } else {
        setHasError('Произошла ошибка при загрузке данных студента');
      }
      
      setStudentDetails(null);
    } finally {
      setIsLoading(false);
    }
  }, [studentId]);

  // Функция получения календаря посещаемости
  const fetchAttendanceCalendar = useCallback(async (force = false) => {
    if (!studentId || studentId <= 0) return;

    const moduleFilter = selectedModule === 'all' ? undefined : selectedModule as number;
    const cacheKey = `attendance-${studentId}-${selectedSubject}-${moduleFilter}`;
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();

    // Проверяем кэш
    if (!force && cached && (now - cached.timestamp) < CACHE_DURATION) {
      setAttendanceCalendar(cached.data);
      return;
    }

    try {
      const calendar = await assessmentAPI.getAttendanceCalendar(
        studentId, 
        selectedSubject, 
        moduleFilter
      );
      
      setAttendanceCalendar(calendar);

      // Кэшируем результат
      cacheRef.current.set(cacheKey, {
        data: calendar,
        timestamp: now
      });

    } catch (error) {
      console.error('Ошибка загрузки календаря:', error);
      setAttendanceCalendar(null);
    }
  }, [studentId, selectedSubject, selectedModule]);

  // Функция получения успеваемости
  const fetchModulePerformance = useCallback(async (force = false) => {
    if (!studentId || studentId <= 0) return;

    const moduleFilter = selectedModule === 'all' ? undefined : selectedModule as number;
    const cacheKey = `performance-${studentId}-${selectedSubject}-${moduleFilter}`;
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();

    // Проверяем кэш
    if (!force && cached && (now - cached.timestamp) < CACHE_DURATION) {
      setModulePerformance(cached.data);
      return;
    }

    try {
      const performance = await assessmentAPI.getModulePerformance(
        studentId, 
        selectedSubject, 
        moduleFilter
      );
      
      setModulePerformance(performance);

      // Кэшируем результат
      cacheRef.current.set(cacheKey, {
        data: performance,
        timestamp: now
      });

    } catch (error) {
      console.error('Ошибка загрузки успеваемости:', error);
      setModulePerformance([]);
    }
  }, [studentId, selectedSubject, selectedModule]);

  // Функция получения итоговых оценок
  const fetchFinalGrades = useCallback(async (force = false) => {
    if (!studentId || studentId <= 0) return;

    const cacheKey = `final-grades-${studentId}`;
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();

    // Проверяем кэш
    if (!force && cached && (now - cached.timestamp) < CACHE_DURATION) {
      setFinalGrades(cached.data);
      return;
    }

    try {
      const grades = await assessmentAPI.getFinalGrades(studentId);
      setFinalGrades(grades);

      // Кэшируем результат
      cacheRef.current.set(cacheKey, {
        data: grades,
        timestamp: now
      });

    } catch (error) {
      console.error('Ошибка загрузки итоговых оценок:', error);
      setFinalGrades({});
    }
  }, [studentId]);

  // Функция валидации (фоновое обновление)
  const validateData = useCallback(async () => {
    if (isLoading) return;
    
    try {
      setIsValidating(true);
      
      // Обновляем все данные
      await Promise.all([
        fetchStudentDetails(true),
        fetchAttendanceCalendar(true),
        fetchModulePerformance(true),
        fetchFinalGrades(true)
      ]);
      
    } catch (error) {
      console.warn('Ошибка валидации:', error);
    } finally {
      setIsValidating(false);
    }
  }, [fetchStudentDetails, fetchAttendanceCalendar, fetchModulePerformance, fetchFinalGrades, isLoading]);

  // Обработчики
  const handleSubjectChange = useCallback((subject: Subject) => {
    setSelectedSubject(subject);
    paramsRef.current.selectedSubject = subject;
  }, []);

  const handleModuleChange = useCallback((moduleId: number | 'all') => {
    setSelectedModule(moduleId);
    paramsRef.current.selectedModule = moduleId;
  }, []);

  const handleTabChange = useCallback((tab: 'attendance' | 'performance') => {
    setActiveTab(tab);
  }, []);

  const handleRefresh = useCallback(() => {
    // Очищаем кэш и загружаем заново
    cacheRef.current.clear();
    validateData();
  }, [validateData]);

  // Получение модулей из данных студента
  const modules = useCallback(() => {
    if (!studentDetails) return [];
    
    const subjectData = studentDetails.subjects_data[selectedSubject];
    if (!subjectData?.performance) return [];

    return Object.entries(subjectData.performance).map(([key, module]) => ({
      id: key,
      name: assessmentAPI.getModuleDisplayName(module.module_name, module.module_id)
    }));
  }, [studentDetails, selectedSubject])();

  // Получение данных текущего предмета
  const currentSubjectData = useCallback(() => {
    if (!studentDetails) return null;
    return studentDetails.subjects_data[selectedSubject] || null;
  }, [studentDetails, selectedSubject])();

  // Эффект для загрузки данных при изменении параметров
  useEffect(() => {
    paramsRef.current = { studentId, selectedSubject, selectedModule };
    
    const loadData = async () => {
      await fetchStudentDetails();
      await Promise.all([
        fetchAttendanceCalendar(),
        fetchModulePerformance(),
        fetchFinalGrades()
      ]);
    };

    loadData();
  }, [studentId, selectedSubject, selectedModule, fetchStudentDetails, fetchAttendanceCalendar, fetchModulePerformance, fetchFinalGrades]);

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
    // Состояние
    selectedSubject,
    selectedModule,
    activeTab,
    
    // Данные
    studentDetails,
    attendanceCalendar,
    modulePerformance,
    finalGrades,
    
    // Состояние загрузки
    isLoading,
    isValidating,
    hasError,
    
    // Обработчики
    handleSubjectChange,
    handleModuleChange,
    handleTabChange,
    handleRefresh,
    
    // Вычисляемые данные
    modules,
    currentSubjectData
  };
};

// ========== ХУК ДЛЯ КАЛЕНДАРЯ ПОСЕЩАЕМОСТИ ==========

export const useAttendanceCalendar = (): UseAttendanceCalendarReturn => {
  const [state, setState] = useState<UseAttendanceCalendarState>({
    calendar: null,
    loading: false,
    error: null
  });

  const paramsRef = useRef<{ studentId?: number; subject?: Subject; moduleId?: number }>({});

  const fetchCalendar = useCallback(async (
    studentId: number, 
    subject: Subject, 
    moduleId?: number
  ) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      paramsRef.current = { studentId, subject, moduleId };

      const calendar = await assessmentAPI.getAttendanceCalendar(studentId, subject, moduleId);
      
      setState(prev => ({
        ...prev,
        calendar,
        loading: false
      }));

    } catch (error) {
      console.error('Ошибка загрузки календаря:', error);
      
      const errorMessage = error instanceof AssessmentAPIError 
        ? error.message 
        : 'Ошибка загрузки календаря посещаемости';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
        calendar: null
      }));
    }
  }, []);

  const refresh = useCallback(() => {
    const { studentId, subject, moduleId } = paramsRef.current;
    if (studentId && subject) {
      fetchCalendar(studentId, subject, moduleId);
    }
  }, [fetchCalendar]);

  const getAttendanceForMonth = useCallback((year: number, month: number): AttendanceMonth | null => {
    if (!state.calendar) return null;
    
    return state.calendar.months.find(m => m.year === year && m.month === month) || null;
  }, [state.calendar]);

  return {
    ...state,
    fetchCalendar,
    refresh,
    getAttendanceForMonth
  };
};

// ========== ХУК ДЛЯ УСПЕВАЕМОСТИ ==========

export const usePerformance = (): UsePerformanceReturn => {
  const [state, setState] = useState<UsePerformanceState>({
    performance: [],
    loading: false,
    error: null
  });

  const paramsRef = useRef<{ studentId?: number; subject?: Subject; moduleId?: number }>({});

  const fetchPerformance = useCallback(async (
    studentId: number, 
    subject: Subject, 
    moduleId?: number
  ) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      paramsRef.current = { studentId, subject, moduleId };

      const performance = await assessmentAPI.getModulePerformance(studentId, subject, moduleId);
      
      setState(prev => ({
        ...prev,
        performance,
        loading: false
      }));

    } catch (error) {
      console.error('Ошибка загрузки успеваемости:', error);
      
      const errorMessage = error instanceof AssessmentAPIError 
        ? error.message 
        : 'Ошибка загрузки данных успеваемости';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
        performance: []
      }));
    }
  }, []);

  const refresh = useCallback(() => {
    const { studentId, subject, moduleId } = paramsRef.current;
    if (studentId && subject) {
      fetchPerformance(studentId, subject, moduleId);
    }
  }, [fetchPerformance]);

  const getModuleById = useCallback((moduleId: number): ModulePerformance | null => {
    return state.performance.find(m => m.module_id === moduleId) || null;
  }, [state.performance]);

  const getTopicById = useCallback((moduleId: number, topicId: number): PerformanceTopic | null => {
    const module = getModuleById(moduleId);
    if (!module) return null;
    
    return module.topics.find(t => t.topic_id === topicId) || null;
  }, [getModuleById]);

  return {
    ...state,
    fetchPerformance,
    refresh,
    getModuleById,
    getTopicById
  };
};

// ========== ХУК ДЛЯ СТАТИСТИКИ ==========

export const useStudentStatistics = (studentId: number) => {
  const [statistics, setStatistics] = useState<StudentStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatistics = useCallback(async () => {
    if (!studentId || studentId <= 0) return;

    try {
      setLoading(true);
      setError(null);
      
      const stats = await assessmentAPI.getStudentStatistics(studentId);
      setStatistics(stats);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
      
      const errorMessage = error instanceof AssessmentAPIError 
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

// ========== ХУК ДЛЯ КОММЕНТАРИЕВ ==========

export const useStudentComments = (studentId: number) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComments = useCallback(async (options?: { comment_type?: string; limit?: number }) => {
    if (!studentId || studentId <= 0) return;

    try {
      setLoading(true);
      setError(null);
      
      const commentsData = await assessmentAPI.getStudentComments(studentId, options);
      setComments(commentsData);
    } catch (error) {
      console.error('Ошибка загрузки комментариев:', error);
      
      const errorMessage = error instanceof AssessmentAPIError 
        ? error.message 
        : 'Ошибка загрузки комментариев';
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    fetchComments();
  }, [fetchComments]);

  return {
    comments,
    loading,
    error,
    refresh: fetchComments,
    fetchWithFilters: fetchComments
  };
};

// ========== ХУК ДЛЯ ИТОГОВЫХ ОЦЕНОК ==========

export const useFinalGrades = (studentId: number) => {
  const [finalGrades, setFinalGrades] = useState<{ [key: string]: FinalGrade }>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFinalGrades = useCallback(async () => {
    if (!studentId || studentId <= 0) return;

    try {
      setLoading(true);
      setError(null);
      
      const grades = await assessmentAPI.getFinalGrades(studentId);
      setFinalGrades(grades);
    } catch (error) {
      console.error('Ошибка загрузки итоговых оценок:', error);
      
      const errorMessage = error instanceof AssessmentAPIError 
        ? error.message 
        : 'Ошибка загрузки итоговых оценок';
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    fetchFinalGrades();
  }, [fetchFinalGrades]);

  // Получение оценки по предмету
  const getGradeBySubject = useCallback((subject: Subject): FinalGrade | null => {
    return finalGrades[subject] || null;
  }, [finalGrades]);

  return {
    finalGrades,
    loading,
    error,
    refresh: fetchFinalGrades,
    getGradeBySubject
  };
};

// ========== ЭКСПОРТ ==========

export default useParentDetails;