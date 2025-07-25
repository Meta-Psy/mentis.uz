import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  testsAPI, 
  TestsAPIError,
  TEST_STATUSES,
  SUBJECTS
} from '../services/api/test_result';
import type { 
  TestInfo,
  TestStatistics,
  TestCounts,
  TestSession,
  TestResult,
  QuestionData,
  TestType,
  TestStatus,
  Subject,
  AttendanceRecord,
  AttendanceStatistics,
  Comment,
  CommentStatistics,
  FinalGrade
} from '../services/api/test_result';

// ========== ТИПЫ ==========

interface UseAssessmentPageState {
  // Состояние фильтров
  selectedSubject: Subject;
  selectedModule: number | 'all';
  selectedFilter: TestStatus;
  
  // Данные
  tests: TestInfo[];
  statistics: TestStatistics | null;
  testCounts: TestCounts;
  
  // Состояние загрузки
  isLoading: boolean;
  isValidating: boolean;
  hasError: string | null;
  
  // Обработчики
  handleSubjectChange: (subject: Subject) => void;
  handleModuleChange: (moduleId: number | 'all') => void;
  handleFilterChange: (filter: TestStatus) => void;
  handleRefresh: () => void;
  
  // Сессия тестирования
  testSession: UseTestSessionReturn;
  
  // Дополнительные данные
  attendance: UseAttendanceReturn;
  comments: UseCommentsReturn;
  finalGrades: UseFinalGradesReturn;
}

interface UseTestSessionState {
  session: TestSession | null;
  currentQuestion: QuestionData | null;
  answers: Record<number, number>;
  timeLeft: number | null;
  progress: {
    current: number;
    total: number;
    percentage: number;
  };
  loading: boolean;
  error: string | null;
}

interface UseTestSessionReturn extends UseTestSessionState {
  createSession: (topicId: number, testType: TestType) => Promise<TestSession | null>;
  submitAnswer: (questionId: number, answer: number) => Promise<boolean>;
  finishTest: () => Promise<TestResult | null>;
  clearSession: () => void;
  getNextQuestion: () => Promise<QuestionData | null>;
}

interface UseAttendanceState {
  records: AttendanceRecord[];
  statistics: AttendanceStatistics | null;
  loading: boolean;
  error: string | null;
}

interface UseAttendanceReturn extends UseAttendanceState {
  fetchAttendance: (studentId: number, subjectId?: number) => Promise<void>;
  fetchStatistics: (studentId: number, subjectId?: number) => Promise<void>;
  refresh: () => void;
}

interface UseCommentsState {
  comments: Comment[];
  statistics: CommentStatistics | null;
  loading: boolean;
  error: string | null;
}

interface UseCommentsReturn extends UseCommentsState {
  fetchComments: (studentId: number) => Promise<void>;
  fetchStatistics: (studentId: number) => Promise<void>;
  refresh: () => void;
}

interface UseFinalGradesState {
  grades: Record<number, FinalGrade>;
  loading: boolean;
  error: string | null;
}

interface UseFinalGradesReturn extends UseFinalGradesState {
  fetchGrade: (studentId: number, subjectId: number) => Promise<void>;
  refresh: () => void;
}

// ========== ОСНОВНОЙ ХУК ==========

export const useAssessmentPage = (studentId: number): UseAssessmentPageState => {
  // Состояние фильтров
  const [selectedSubject, setSelectedSubject] = useState<Subject>(SUBJECTS.CHEMISTRY);
  const [selectedModule, setSelectedModule] = useState<number | 'all'>('all');
  const [selectedFilter, setSelectedFilter] = useState<TestStatus>(TEST_STATUSES.CURRENT);
  
  // Данные
  const [tests, setTests] = useState<TestInfo[]>([]);
  const [statistics, setStatistics] = useState<TestStatistics | null>(null);
  const [testCounts, setTestCounts] = useState<TestCounts>({
    completed: 0,
    current: 0,
    overdue: 0,
    available: 0
  });
  
  // Состояние загрузки
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [hasError, setHasError] = useState<string | null>(null);
  
  // Кэш для избежания повторных запросов
  const cacheRef = useRef<Map<string, { data: any; timestamp: number }>>(new Map());
  const CACHE_DURATION = 5 * 60 * 1000; // 5 минут
  
  // Дополнительные хуки
  const testSession = useTestSession();
  const attendance = useAttendance();
  const comments = useComments();
  const finalGrades = useFinalGrades();

  // Функция получения тестов
  const fetchTests = useCallback(async (force = false) => {
    if (!studentId || studentId <= 0) {
      setHasError('Некорректный ID студента');
      return;
    }

    const cacheKey = `tests-${studentId}-${selectedSubject}-${selectedModule}-${selectedFilter}`;
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();

    // Проверяем кэш
    if (!force && cached && (now - cached.timestamp) < CACHE_DURATION) {
      const { tests: cachedTests, statistics: cachedStats, test_counts } = cached.data;
      setTests(cachedTests);
      setStatistics(cachedStats);
      setTestCounts(test_counts);
      return;
    }

    try {
      setIsLoading(true);
      setHasError(null);

      const filters: any = {
        subject_name: selectedSubject,
        status_filter: selectedFilter,
        limit: 100
      };

      // Добавляем фильтр по модулю если выбран конкретный
      if (selectedModule !== 'all') {
        filters.section_id = selectedModule;
      }

      const response = await testsAPI.getStudentTests(studentId, filters);
      
      setTests(response.tests);
      setStatistics(response.statistics);
      setTestCounts(response.test_counts);

      // Кэшируем результат
      cacheRef.current.set(cacheKey, {
        data: response,
        timestamp: now
      });

    } catch (error) {
      console.error('Ошибка загрузки тестов:', error);
      
      if (error instanceof TestsAPIError) {
        setHasError(error.message);
      } else {
        setHasError('Произошла ошибка при загрузке тестов');
      }
      
      // В случае ошибки показываем пустые данные
      setTests([]);
      setStatistics(null);
      setTestCounts({
        completed: 0,
        current: 0,
        overdue: 0,
        available: 0
      });
    } finally {
      setIsLoading(false);
    }
  }, [studentId, selectedSubject, selectedModule, selectedFilter]);

  // Функция валидации (фоновое обновление)
  const validateData = useCallback(async () => {
    if (isLoading) return;
    
    try {
      setIsValidating(true);
      await fetchTests(true);
    } catch (error) {
      // Валидация не должна показывать ошибки пользователю
      console.warn('Ошибка валидации:', error);
    } finally {
      setIsValidating(false);
    }
  }, [fetchTests, isLoading]);

  // Обработчики
  const handleSubjectChange = useCallback((subject: Subject) => {
    setSelectedSubject(subject);
  }, []);

  const handleModuleChange = useCallback((moduleId: number | 'all') => {
    setSelectedModule(moduleId);
  }, []);

  const handleFilterChange = useCallback((filter: TestStatus) => {
    setSelectedFilter(filter);
  }, []);

  const handleRefresh = useCallback(() => {
    fetchTests(true);
  }, [fetchTests]);

  // Эффект для загрузки данных при изменении фильтров
  useEffect(() => {
    fetchTests();
  }, [fetchTests]);

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
    selectedModule,
    selectedFilter,
    
    // Данные
    tests,
    statistics,
    testCounts,
    
    // Состояние загрузки
    isLoading,
    isValidating,
    hasError,
    
    // Обработчики
    handleSubjectChange,
    handleModuleChange,
    handleFilterChange,
    handleRefresh,
    
    // Дополнительные данные
    testSession,
    attendance,
    comments,
    finalGrades
  };
};

// ========== ХУК ДЛЯ СЕССИИ ТЕСТИРОВАНИЯ ==========

export const useTestSession = (): UseTestSessionReturn => {
  const [state, setState] = useState<UseTestSessionState>({
    session: null,
    currentQuestion: null,
    answers: {},
    timeLeft: null,
    progress: {
      current: 0,
      total: 0,
      percentage: 0
    },
    loading: false,
    error: null
  });

  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Таймер для отслеживания времени
  const startTimer = useCallback((timeLimit: number) => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    const endTime = Date.now() + (timeLimit * 60 * 1000);
    
    timerRef.current = setInterval(() => {
      const remaining = Math.max(0, endTime - Date.now());
      const remainingSeconds = Math.floor(remaining / 1000);
      
      setState(prev => ({
        ...prev,
        timeLeft: remainingSeconds
      }));

      if (remaining <= 0) {
        clearInterval(timerRef.current!);
        // Автоматически завершаем тест при истечении времени
        finishTest();
      }
    }, 1000);
  }, []);

  // Создание сессии
  const createSession = useCallback(async (
    topicId: number, 
    testType: TestType
  ): Promise<TestSession | null> => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const response = await testsAPI.createTestSession(topicId, testType, 30);
      const { session, current_question, progress } = response;

      setState(prev => ({
        ...prev,
        session,
        currentQuestion: current_question,
        answers: {},
        progress,
        loading: false
      }));

      // Запускаем таймер если есть лимит времени
      if (session.time_limit_minutes) {
        startTimer(session.time_limit_minutes);
      }

      return session;
    } catch (error) {
      console.error('Ошибка создания сессии:', error);
      
      const errorMessage = error instanceof TestsAPIError 
        ? error.message 
        : 'Ошибка создания сессии тестирования';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      
      return null;
    }
  }, [startTimer]);

  // Получение следующего вопроса
  const getNextQuestion = useCallback(async (): Promise<QuestionData | null> => {
    if (!state.session?.session_id) return null;

    try {
      const question = await testsAPI.getCurrentQuestion(state.session.session_id);
      
      setState(prev => ({
        ...prev,
        currentQuestion: question
      }));

      return question;
    } catch (error) {
      console.error('Ошибка получения вопроса:', error);
      return null;
    }
  }, [state.session?.session_id]);

  // Отправка ответа
  const submitAnswer = useCallback(async (
    questionId: number, 
    answer: number
  ): Promise<boolean> => {
    if (!state.session?.session_id) return false;

    try {
      const response = await testsAPI.submitAnswer(
        state.session.session_id, 
        questionId, 
        answer
      );

      // Обновляем состояние
      setState(prev => ({
        ...prev,
        answers: {
          ...prev.answers,
          [questionId]: answer
        },
        progress: {
          current: response.current_question,
          total: response.total_questions,
          percentage: response.progress_percentage
        }
      }));

      // Если тест не завершен, получаем следующий вопрос
      if (!response.is_finished) {
        await getNextQuestion();
      }

      return true;
    } catch (error) {
      console.error('Ошибка отправки ответа:', error);
      
      const errorMessage = error instanceof TestsAPIError 
        ? error.message 
        : 'Ошибка отправки ответа';
      
      setState(prev => ({
        ...prev,
        error: errorMessage
      }));
      
      return false;
    }
  }, [state.session?.session_id, getNextQuestion]);

  // Завершение теста
  const finishTest = useCallback(async (): Promise<TestResult | null> => {
    if (!state.session?.session_id) return null;

    try {
      setState(prev => ({ ...prev, loading: true }));

      // Останавливаем таймер
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      const response = await testsAPI.finishTest(state.session.session_id, state.answers);
      
      // Очищаем сессию
      setState(prev => ({
        ...prev,
        session: null,
        currentQuestion: null,
        answers: {},
        timeLeft: null,
        progress: {
          current: 0,
          total: 0,
          percentage: 0
        },
        loading: false
      }));

      return response.result;
    } catch (error) {
      console.error('Ошибка завершения теста:', error);
      
      const errorMessage = error instanceof TestsAPIError 
        ? error.message 
        : 'Ошибка завершения теста';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      
      return null;
    }
  }, [state.session?.session_id, state.answers]);

  // Очистка сессии
  const clearSession = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    setState({
      session: null,
      currentQuestion: null,
      answers: {},
      timeLeft: null,
      progress: {
        current: 0,
        total: 0,
        percentage: 0
      },
      loading: false,
      error: null
    });
  }, []);

  // Очистка при размонтировании
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  return {
    ...state,
    createSession,
    submitAnswer,
    finishTest,
    clearSession,
    getNextQuestion
  };
};

// ========== ХУК ДЛЯ ПОСЕЩАЕМОСТИ ==========

export const useAttendance = (): UseAttendanceReturn => {
  const [state, setState] = useState<UseAttendanceState>({
    records: [],
    statistics: null,
    loading: false,
    error: null
  });

  const fetchAttendance = useCallback(async (studentId: number, subjectId?: number) => {
    if (!studentId || studentId <= 0) return;

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const records = await testsAPI.getStudentAttendance(studentId, subjectId);
      
      setState(prev => ({
        ...prev,
        records,
        loading: false
      }));
    } catch (error) {
      console.error('Ошибка загрузки посещаемости:', error);
      
      const errorMessage = error instanceof TestsAPIError 
        ? error.message 
        : 'Ошибка загрузки посещаемости';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
        records: []
      }));
    }
  }, []);

  const fetchStatistics = useCallback(async (studentId: number, subjectId?: number) => {
    if (!studentId || studentId <= 0) return;

    try {
      const statistics = await testsAPI.getAttendanceStatistics(studentId, subjectId);
      
      setState(prev => ({
        ...prev,
        statistics
      }));
    } catch (error) {
      console.error('Ошибка загрузки статистики посещаемости:', error);
      
      setState(prev => ({
        ...prev,
        statistics: null
      }));
    }
  }, []);

  const refresh = useCallback(() => {
    // Обновить данные при следующем вызове fetchAttendance
    setState(prev => ({ ...prev, records: [], statistics: null }));
  }, []);

  return {
    ...state,
    fetchAttendance,
    fetchStatistics,
    refresh
  };
};

// ========== ХУК ДЛЯ КОММЕНТАРИЕВ ==========

export const useComments = (): UseCommentsReturn => {
  const [state, setState] = useState<UseCommentsState>({
    comments: [],
    statistics: null,
    loading: false,
    error: null
  });

  const fetchComments = useCallback(async (studentId: number) => {
    if (!studentId || studentId <= 0) return;

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const comments = await testsAPI.getStudentComments(studentId);
      
      setState(prev => ({
        ...prev,
        comments,
        loading: false
      }));
    } catch (error) {
      console.error('Ошибка загрузки комментариев:', error);
      
      const errorMessage = error instanceof TestsAPIError 
        ? error.message 
        : 'Ошибка загрузки комментариев';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
        comments: []
      }));
    }
  }, []);

  const fetchStatistics = useCallback(async (studentId: number) => {
    if (!studentId || studentId <= 0) return;

    try {
      const statistics = await testsAPI.getCommentsStatistics(studentId);
      
      setState(prev => ({
        ...prev,
        statistics
      }));
    } catch (error) {
      console.error('Ошибка загрузки статистики комментариев:', error);
      
      setState(prev => ({
        ...prev,
        statistics: null
      }));
    }
  }, []);

  const refresh = useCallback(() => {
    // Обновить данные при следующем вызове fetchComments
    setState(prev => ({ ...prev, comments: [], statistics: null }));
  }, []);

  return {
    ...state,
    fetchComments,
    fetchStatistics,
    refresh
  };
};

// ========== ХУК ДЛЯ ИТОГОВЫХ ОЦЕНОК ==========

export const useFinalGrades = (): UseFinalGradesReturn => {
  const [state, setState] = useState<UseFinalGradesState>({
    grades: {},
    loading: false,
    error: null
  });

  const fetchGrade = useCallback(async (studentId: number, subjectId: number) => {
    if (!studentId || studentId <= 0 || !subjectId || subjectId <= 0) return;

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const grade = await testsAPI.getFinalGrade(studentId, subjectId);
      
      setState(prev => ({
        ...prev,
        grades: {
          ...prev.grades,
          [subjectId]: grade
        },
        loading: false
      }));
    } catch (error) {
      console.error('Ошибка загрузки итоговой оценки:', error);
      
      const errorMessage = error instanceof TestsAPIError 
        ? error.message 
        : 'Ошибка загрузки итоговой оценки';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
    }
  }, []);

  const refresh = useCallback(() => {
    // Очистить кэш оценок
    setState(prev => ({ ...prev, grades: {} }));
  }, []);

  return {
    ...state,
    fetchGrade,
    refresh
  };
};

// ========== ХУК ДЛЯ СТАТИСТИКИ ==========

export const useTestStatistics = (studentId: number) => {
  const [statistics, setStatistics] = useState<TestStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatistics = useCallback(async () => {
    if (!studentId || studentId <= 0) return;

    try {
      setLoading(true);
      setError(null);
      
      const stats = await testsAPI.getStudentStatistics(studentId);
      setStatistics(stats);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
      
      const errorMessage = error instanceof TestsAPIError 
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

// ========== ХУК ДЛЯ АКТИВНОГО ТЕСТА ==========

export const useActiveTest = (topicId: number, testType: TestType = 'training') => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<QuestionData | null>(null);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number[]>>({});
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isFinished, setIsFinished] = useState(false);

  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Инициализация теста
  const initializeTest = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await testsAPI.createTestSession(topicId, testType);
      
      setSessionId(response.session.session_id);
      setCurrentQuestion(response.current_question);
      
      // Загружаем сохраненные данные из localStorage
      const savedAnswers = localStorage.getItem(`test_${topicId}_answers`);
      const savedTime = localStorage.getItem(`test_${topicId}_time`);
      const savedSelected = localStorage.getItem(`test_${topicId}_selected`);
      
      if (savedAnswers) {
        setAnswers(JSON.parse(savedAnswers));
      }
      if (savedTime) {
        setTimeElapsed(parseInt(savedTime));
      }
      if (savedSelected) {
        setSelectedAnswers(JSON.parse(savedSelected));
      }

      // Запускаем таймер
      timerRef.current = setInterval(() => {
        setTimeElapsed(prev => {
          const newTime = prev + 1;
          localStorage.setItem(`test_${topicId}_time`, newTime.toString());
          return newTime;
        });
      }, 1000);

    } catch (error) {
      console.error('Ошибка инициализации теста:', error);
      setError(error instanceof TestsAPIError ? error.message : 'Ошибка инициализации теста');
    } finally {
      setLoading(false);
    }
  }, [topicId, testType]);

  // Сохранение прогресса
  const saveProgress = useCallback(() => {
    localStorage.setItem(`test_${topicId}_answers`, JSON.stringify(answers));
    localStorage.setItem(`test_${topicId}_selected`, JSON.stringify(selectedAnswers));
  }, [topicId, answers, selectedAnswers]);

  // Завершение теста
  const submitTest = useCallback(async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      await testsAPI.finishTest(sessionId, answers);
      
      // Очищаем localStorage
      localStorage.removeItem(`test_${topicId}_answers`);
      localStorage.removeItem(`test_${topicId}_time`);
      localStorage.removeItem(`test_${topicId}_selected`);
      
      setIsFinished(true);
      
    } catch (error) {
      console.error('Ошибка завершения теста:', error);
      setError(error instanceof TestsAPIError ? error.message : 'Ошибка завершения теста');
    } finally {
      setLoading(false);
    }
  }, [sessionId, answers, topicId]);

  // Обработка выбора ответа
  const handleAnswerSelection = useCallback((questionId: number, optionId: string, isCorrect: boolean) => {
    setSelectedAnswers(prev => {
      const currentSelected = prev[questionId] || [];
      
      if (isCorrect) {
        // Добавляем к выбранным
        if (!currentSelected.includes(optionId as any)) {
          return {
            ...prev,
            [questionId]: [...currentSelected, optionId as any]
          };
        }
      } else {
        // Убираем из выбранных
        return {
          ...prev,
          [questionId]: currentSelected.filter(id => id !== Number(optionId))
        };
      }
      
      return prev;
    });
  }, []);

  // Финализация ответа
  const finalizeAnswer = useCallback((questionId: number) => {
    const selected = selectedAnswers[questionId] || [];
    if (selected.length === 1) {
      setAnswers(prev => ({
        ...prev,
        [questionId]: selected[0]
      }));
    }
  }, [selectedAnswers]);

  useEffect(() => {
    initializeTest();
    
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [initializeTest]);

  // Автосохранение
  useEffect(() => {
    const autoSaveInterval = setInterval(saveProgress, 30000); // Каждые 30 секунд
    return () => clearInterval(autoSaveInterval);
  }, [saveProgress]);

  return {
    sessionId,
    currentQuestion,
    answers,
    selectedAnswers,
    timeElapsed,
    loading,
    error,
    isFinished,
    handleAnswerSelection,
    finalizeAnswer,
    saveProgress,
    submitTest
  };
};

// ========== ХУК ДЛЯ РЕЗУЛЬТАТОВ ТЕСТА ==========

export const useTestResults = (sessionId?: string) => {
  const [result, setResult] = useState<TestResult | null>(null);
  const [detailedResults, setDetailedResults] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchResults = useCallback(async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      setError(null);

      const response = await testsAPI.getTestResult(sessionId);
      
      setResult(response.result);
      setDetailedResults(response.detailed_results);
      setRecommendations(response.recommendations);
    } catch (error) {
      console.error('Ошибка загрузки результатов:', error);
      
      const errorMessage = error instanceof TestsAPIError 
        ? error.message 
        : 'Ошибка загрузки результатов теста';
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    if (sessionId) {
      fetchResults();
    }
  }, [fetchResults, sessionId]);

  return {
    result,
    detailedResults,
    recommendations,
    loading,
    error,
    refresh: fetchResults
  };
};

// ========== ХУК ДЛЯ ЗДОРОВЬЯ API ==========

export const useAPIHealth = () => {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const healthData = await testsAPI.healthCheck();
      setHealth(healthData);
    } catch (error) {
      console.error('Ошибка проверки здоровья API:', error);
      
      const errorMessage = error instanceof TestsAPIError 
        ? error.message 
        : 'API недоступен';
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    
    // Проверяем здоровье каждые 5 минут
    const interval = setInterval(checkHealth, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return {
    health,
    loading,
    error,
    refresh: checkHealth
  };
};

// ========== ЭКСПОРТ ==========

export default useAssessmentPage;