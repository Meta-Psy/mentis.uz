import React from 'react';
import { Clock, CheckCircle, XCircle, AlertTriangle, BookOpen, Play, Loader2, RefreshCw } from 'lucide-react';
import { useTestsPage } from '../../../hooks/useTests';
import { TEST_TYPES, TEST_STATUSES, SUBJECTS } from '../../../services/api/tests';
import type { TestInfo } from '../../../services/api/tests';

const StudentTestsPage = () => {
  // TODO: Получить ID студента из контекста авторизации
  const studentId = 1; // Заглушка - должно приходать из контекста пользователя

  const {
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
    
    // Сессия тестирования
    testSession
  } = useTestsPage(studentId);

  // Данные модулей из тестов
  const modules = React.useMemo(() => {
    const uniqueModules = new Map<number, { id: number; name: string }>();
    
    tests.forEach(test => {
      if (!uniqueModules.has(test.section_id)) {
        uniqueModules.set(test.section_id, {
          id: test.section_id,
          name: test.section_name
        });
      }
    });
    
    return Array.from(uniqueModules.values()).sort((a, b) => a.id - b.id);
  }, [tests]);

  // Компонент ошибки
  const ErrorMessage = ({ error, onRetry }: { error: string; onRetry: () => void }): JSX.Element => (
    <div className="bg-red-50 border border-red-200 p-4 lg:p-6 text-center">
      <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
      <p className="text-red-700 mb-4">{error}</p>
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white hover:bg-red-700 transition-colors duration-200"
      >
        <RefreshCw className="w-4 h-4" />
        Попробовать снова
      </button>
    </div>
  );

  // Компонент загрузки
  const LoadingSpinner = ({ message = 'Загрузка...' }: { message?: string }): JSX.Element => (
    <div className="flex items-center justify-center p-8 lg:p-12">
      <div className="text-center">
        <Loader2 className="w-8 h-8 text-primary-600 animate-spin mx-auto mb-2" />
        <p className="text-neutral-600">{message}</p>
      </div>
    </div>
  );

  // Компонент карточки теста
  const TestCard = ({ test }: { test: TestInfo }): JSX.Element => {
    const getStatusColor = (status: string) => {
      switch (status) {
        case TEST_STATUSES.COMPLETED:
          return 'border-green-200 bg-green-50';
        case TEST_STATUSES.CURRENT:
          return 'border-primary-200 bg-primary-50';
        case TEST_STATUSES.OVERDUE:
          return 'border-red-200 bg-red-50';
        default:
          return 'border-neutral-200 bg-white';
      }
    };

    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    const getBestTrainingScore = () => {
      if (!test.training_attempts || test.training_attempts.length === 0) return null;
      return Math.max(...test.training_attempts.map(attempt => attempt.score_percentage));
    };

    const getExamScore = () => {
      if (!test.exam_attempts || test.exam_attempts.length === 0) return null;
      return test.exam_attempts[0].score_percentage;
    };

    const canTakeExam = () => {
      return test.exam_attempts.length === 0; // Экзамен можно сдать только один раз
    };

    const handleStartTest = async (testType: 'training' | 'exam') => {
      try {
        const session = await testSession.createSession(
          test.topic_id, 
          testType === 'training' ? TEST_TYPES.TRAINING : TEST_TYPES.FINAL
        );
        
        if (session) {
          // Перенаправляем на страницу прохождения теста
          window.location.href = `/test/${session.session_id}`;
        }
      } catch (error) {
        console.error('Ошибка создания сессии:', error);
      }
    };

    const renderTestContent = () => {
      switch (test.status) {
        case TEST_STATUSES.COMPLETED:
          const bestTraining = getBestTrainingScore();
          const examScore = getExamScore();
          
          return (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <div>
                  <h3 className="text-lg font-semibold text-neutral-900">{test.topic_name}</h3>
                  <p className="text-sm text-neutral-600">{test.section_name} • {test.subject_name}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-neutral-600 mb-1">Оценки:</div>
                <div className="flex gap-4">
                  {bestTraining && (
                    <div className="text-center">
                      <div className="text-xs text-neutral-500">Лучший тренировочный</div>
                      <div className="text-lg font-bold text-green-600">{bestTraining.toFixed(1)}%</div>
                    </div>
                  )}
                  {examScore && (
                    <div className="text-center">
                      <div className="text-xs text-neutral-500">Экзаменационный</div>
                      <div className="text-lg font-bold text-green-600">{examScore.toFixed(1)}%</div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );

        case TEST_STATUSES.CURRENT:
          return (
            <>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Clock className="w-6 h-6 text-primary-600" />
                  <div>
                    <h3 className="text-lg font-semibold text-neutral-900">{test.topic_name}</h3>
                    <p className="text-sm text-neutral-600">{test.section_name} • {test.subject_name}</p>
                    <p className="text-xs text-neutral-500 mt-1">{test.questions_count} вопросов</p>
                  </div>
                </div>
                {test.deadline && (
                  <div className="text-right">
                    <div className="text-sm text-neutral-600 mb-1">Необходимо сдать до:</div>
                    <div className="text-sm font-medium text-primary-700">
                      {formatDate(test.deadline)}
                    </div>
                    {test.days_left !== undefined && (
                      <div className="text-xs text-neutral-500 mt-1">
                        Осталось: {test.days_left} {test.days_left === 1 ? 'день' : test.days_left < 5 ? 'дня' : 'дней'}
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => handleStartTest('training')}
                  disabled={testSession.loading}
                  className="flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors duration-200 text-sm sm:text-base"
                >
                  <Play className="w-4 h-4" />
                  {testSession.loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <span className="hidden sm:inline">Тренировочный тест ({test.questions_count} вопросов)</span>
                      <span className="sm:hidden">Тренировочный</span>
                    </>
                  )}
                </button>
                
                {canTakeExam() && (
                  <button
                    onClick={() => handleStartTest('exam')}
                    disabled={testSession.loading}
                    className="flex items-center justify-center gap-2 px-4 py-2 bg-secondary-400 text-white font-medium hover:bg-secondary-500 disabled:opacity-50 transition-colors duration-200 text-sm sm:text-base"
                  >
                    <BookOpen className="w-4 h-4" />
                    {testSession.loading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <span className="hidden sm:inline">Экзамен ({test.questions_count} вопросов, {test.time_limit_minutes || 45} мин)</span>
                        <span className="sm:hidden">Экзамен</span>
                      </>
                    )}
                  </button>
                )}
                
                {!canTakeExam() && (
                  <div className="flex items-center gap-2 px-4 py-2 bg-neutral-300 text-neutral-600 text-sm">
                    <CheckCircle className="w-4 h-4" />
                    Экзамен уже сдан
                  </div>
                )}
              </div>
              
              {/* Показываем информацию о предыдущих попытках */}
              {test.training_attempts && test.training_attempts.length > 0 && (
                <div className="mt-3 pt-3 border-t border-neutral-200">
                  <div className="text-xs text-neutral-500">
                    Тренировочных попыток: {test.training_attempts.length} • 
                    Лучший результат: {getBestTrainingScore()?.toFixed(1)}%
                  </div>
                </div>
              )}
            </>
          );

        case TEST_STATUSES.OVERDUE:
          return (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <XCircle className="w-6 h-6 text-red-600" />
                <div>
                  <h3 className="text-lg font-semibold text-neutral-900">{test.topic_name}</h3>
                  <p className="text-sm text-neutral-600">{test.section_name} • {test.subject_name}</p>
                </div>
              </div>
              {test.deadline && (
                <div className="text-right">
                  <div className="text-sm text-neutral-600 mb-1">Просрочено:</div>
                  <div className="text-sm font-medium text-red-700">
                    {formatDate(test.deadline)}
                  </div>
                  {test.days_overdue !== undefined && (
                    <div className="text-xs text-red-500 mt-1">
                      {test.days_overdue} {test.days_overdue === 1 ? 'день' : test.days_overdue < 5 ? 'дня' : 'дней'} назад
                    </div>
                  )}
                </div>
              )}
            </div>
          );

        default:
          return null;
      }
    };

    return (
      <div className={`border-2 ${getStatusColor(test.status)} p-6 mb-4 transition-all duration-200 hover:shadow-md`}>
        {renderTestContent()}
      </div>
    );
  };

  // Компонент Header (упрощенный)
  const Header = (): JSX.Element => (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-lg shadow-lg border-b border-neutral-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16 md:h-20">
          <a href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-primary-600 to-secondary-400 flex items-center justify-center">
              <span className="text-white font-bold text-lg">M</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-neutral-900 leading-none">
                Mентис
              </span>
              <span className="text-xs text-neutral-600 leading-none">
                Путь к медицине
              </span>
            </div>
          </a>
          <nav className="hidden lg:flex items-center space-x-8">
            <a href="/" className="text-neutral-700 hover:text-primary-600 transition-colors duration-200 font-medium">
              Главная
            </a>
            <a href="/tests" className="text-neutral-700 hover:text-primary-600 transition-colors duration-200 font-medium">
              Тесты
            </a>
            <a href="/progress" className="text-neutral-700 hover:text-primary-600 transition-colors duration-200 font-medium">
              Прогресс
            </a>
          </nav>
        </div>
      </div>
    </header>
  );

  return (
    <div className="min-h-screen bg-neutral-50">
      <Header />
      
      <div className="pt-20 md:pt-24">
        <div className="container mx-auto px-4 py-8">
          {/* Заголовок */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-primary-900">
                  Ваши тесты
                </h1>
                <p className="text-neutral-600 mt-2">
                  Управляйте своими тестами и отслеживайте прогресс
                </p>
              </div>
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-neutral-200 text-neutral-700 hover:bg-neutral-300 disabled:opacity-50 transition-colors duration-200"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">Обновить</span>
              </button>
            </div>
          </div>

          {/* Обработка ошибок */}
          {hasError && (
            <ErrorMessage error={hasError} onRetry={handleRefresh} />
          )}

          {/* Обработка загрузки */}
          {isLoading && !tests.length && (
            <LoadingSpinner message="Загрузка тестов..." />
          )}

          {!isLoading && !hasError && (
            <>
              {/* Выбор предмета */}
              <div className="flex flex-wrap justify-center gap-2 mb-6">
                <button
                  onClick={() => handleSubjectChange(SUBJECTS.CHEMISTRY)}
                  disabled={isLoading}
                  className={`flex items-center gap-2 px-4 sm:px-6 py-3 font-medium transition-all duration-200 text-sm sm:text-base disabled:opacity-50 ${
                    selectedSubject === SUBJECTS.CHEMISTRY
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                  }`}
                >
                  Химия
                </button>
                
                <button
                  onClick={() => handleSubjectChange(SUBJECTS.BIOLOGY)}
                  disabled={isLoading}
                  className={`flex items-center gap-2 px-4 sm:px-6 py-3 font-medium transition-all duration-200 text-sm sm:text-base disabled:opacity-50 ${
                    selectedSubject === SUBJECTS.BIOLOGY
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                  }`}
                >
                  Биология
                </button>
              </div>

              {/* Выбор модуля */}
              {modules.length > 0 && (
                <div className="flex flex-wrap justify-center gap-2 mb-6">
                  <button
                    onClick={() => handleModuleChange('all')}
                    disabled={isLoading}
                    className={`px-3 sm:px-4 py-2 font-medium transition-all duration-200 text-xs sm:text-sm disabled:opacity-50 ${
                      selectedModule === 'all'
                        ? 'bg-secondary-400 text-white shadow-lg'
                        : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                    }`}
                  >
                    Все модули
                  </button>
                  
                  {modules.map(module => (
                    <button
                      key={module.id}
                      onClick={() => handleModuleChange(module.id)}
                      disabled={isLoading}
                      className={`px-3 sm:px-4 py-2 font-medium transition-all duration-200 text-xs sm:text-sm disabled:opacity-50 ${
                        selectedModule === module.id
                          ? 'bg-secondary-400 text-white shadow-lg'
                          : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                      }`}
                    >
                      {module.name}
                    </button>
                  ))}
                </div>
              )}

              {/* Фильтры статусов */}
              <div className="flex flex-wrap gap-2 mb-8">
                <button
                  onClick={() => handleFilterChange(TEST_STATUSES.COMPLETED)}
                  disabled={isLoading}
                  className={`flex items-center gap-2 px-4 sm:px-6 py-3 font-medium transition-all duration-200 disabled:opacity-50 text-sm sm:text-base ${
                    selectedFilter === TEST_STATUSES.COMPLETED
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                  }`}
                >
                  <CheckCircle className="w-4 h-4" />
                  Сдано
                  <span className={`px-2 py-1 text-xs font-bold ${
                    selectedFilter === TEST_STATUSES.COMPLETED 
                      ? 'bg-white/20 text-white' 
                      : 'bg-green-100 text-green-700'
                  }`}>
                    {testCounts.completed}
                  </span>
                </button>
                
                <button
                  onClick={() => handleFilterChange(TEST_STATUSES.CURRENT)}
                  disabled={isLoading}
                  className={`flex items-center gap-2 px-4 sm:px-6 py-3 font-medium transition-all duration-200 disabled:opacity-50 text-sm sm:text-base ${
                    selectedFilter === TEST_STATUSES.CURRENT
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                  }`}
                >
                  <Clock className="w-4 h-4" />
                  Актуально
                  <span className={`px-2 py-1 text-xs font-bold ${
                    selectedFilter === TEST_STATUSES.CURRENT 
                      ? 'bg-white/20 text-white' 
                      : 'bg-blue-100 text-blue-700'
                  }`}>
                    {testCounts.current}
                  </span>
                </button>
                
                <button
                  onClick={() => handleFilterChange(TEST_STATUSES.OVERDUE)}
                  disabled={isLoading}
                  className={`flex items-center gap-2 px-4 sm:px-6 py-3 font-medium transition-all duration-200 disabled:opacity-50 text-sm sm:text-base ${
                    selectedFilter === TEST_STATUSES.OVERDUE
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                  }`}
                >
                  <AlertTriangle className="w-4 h-4" />
                  Просрочено
                  <span className={`px-2 py-1 text-xs font-bold ${
                    selectedFilter === TEST_STATUSES.OVERDUE 
                      ? 'bg-white/20 text-white' 
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {testCounts.overdue}
                  </span>
                </button>
              </div>

              {/* Список тестов */}
              <div className="space-y-4">
                {tests.length > 0 ? (
                  tests.map(test => (
                    <TestCard key={test.topic_id} test={test} />
                  ))
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 mx-auto mb-4 bg-neutral-200 flex items-center justify-center">
                      <BookOpen className="w-8 h-8 text-neutral-500" />
                    </div>
                    <h3 className="text-lg font-medium text-neutral-700 mb-2">
                      Нет тестов в данной категории
                    </h3>
                    <p className="text-neutral-500">
                      {selectedFilter === TEST_STATUSES.COMPLETED && 'Вы пока не сдали ни одного теста'}
                      {selectedFilter === TEST_STATUSES.CURRENT && 'У вас нет актуальных тестов для сдачи'}
                      {selectedFilter === TEST_STATUSES.OVERDUE && 'У вас нет просроченных тестов'}
                    </p>
                  </div>
                )}
              </div>

              {/* Статистика внизу */}
              {statistics && (
                <div className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="bg-green-50 border-2 border-green-200 p-6 text-center">
                    <div className="text-3xl font-bold text-green-600 mb-2">
                      {statistics.completed_tests}
                    </div>
                    <div className="text-green-700 font-medium">Сданных тестов</div>
                  </div>
                  
                  <div className="bg-blue-50 border-2 border-blue-200 p-6 text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {statistics.current_tests}
                    </div>
                    <div className="text-blue-700 font-medium">Доступных тестов</div>
                  </div>
                  
                  <div className="bg-red-50 border-2 border-red-200 p-6 text-center">
                    <div className="text-3xl font-bold text-red-600 mb-2">
                      {statistics.overdue_tests}
                    </div>
                    <div className="text-red-700 font-medium">Просроченных тестов</div>
                  </div>

                  <div className="bg-purple-50 border-2 border-purple-200 p-6 text-center">
                    <div className="text-3xl font-bold text-purple-600 mb-2">
                      {statistics.average_score.toFixed(1)}%
                    </div>
                    <div className="text-purple-700 font-medium">Средний балл</div>
                  </div>
                </div>
              )}
            </>
          )}

          {/* Индикатор валидации */}
          {isValidating && (
            <div className="fixed bottom-4 right-4 bg-white border border-neutral-200 shadow-lg p-4 flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-primary-600 animate-spin" />
              <span className="text-sm text-neutral-600">Обновление...</span>
            </div>
          )}

          {/* Ошибка сессии тестирования */}
          {testSession.error && (
            <div className="fixed bottom-4 left-4 bg-red-50 border border-red-200 shadow-lg p-4 max-w-sm">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                <span className="text-sm font-medium text-red-800">Ошибка тестирования</span>
              </div>
              <p className="text-sm text-red-700">{testSession.error}</p>
              <button
                onClick={() => testSession.clearSession()}
                className="mt-2 text-xs text-red-600 hover:text-red-800 underline"
              >
                Закрыть
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentTestsPage;