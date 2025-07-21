import React, { useState, useMemo } from 'react';
import { Clock, Calendar, CheckCircle, XCircle, AlertTriangle, BookOpen, Play } from 'lucide-react';

const StudentTestsPage = () => {
  const [selectedFilter, setSelectedFilter] = useState('completed');
  const [selectedSubject, setSelectedSubject] = useState('chemistry');
  const [selectedModule, setSelectedModule] = useState('all');

  // Моковые данные тестов
  const mockTests = [
    // Сданные тесты
    {
      id: 1,
      status: 'completed',
      subject: 'chemistry',
      module: 1,
      topic: 'Тема 18. Органическая химия',
      trainingScore: 8.5,
      controlScore: 9.2,
      completedDate: '2024-08-15'
    },
    {
      id: 2,
      status: 'completed',
      subject: 'biology',
      module: 1,
      topic: 'Тема 19. Эндокринная система человека',
      trainingScore: 7.8,
      controlScore: 8.6,
      completedDate: '2024-08-20'
    },
    {
      id: 3,
      status: 'completed',
      subject: 'biology',
      module: 2,
      topic: 'Тема 21. Дыхательная система человека',
      trainingScore: 9.1,
      controlScore: 9.5,
      completedDate: '2024-09-05'
    },

    // Актуальные тесты
    {
      id: 4,
      status: 'current',
      subject: 'biology',
      module: 2,
      topic: 'Тема 22. Выделительная система человека',
      deadline: '2024-09-16 23:59',
      daysLeft: 3
    },
    {
      id: 5,
      status: 'current',
      subject: 'chemistry',
      module: 1,
      topic: 'Тема 23. Неорганическая химия',
      deadline: '2024-09-20 23:59',
      daysLeft: 7
    },
    {
      id: 6,
      status: 'current',
      subject: 'biology',
      module: 3,
      topic: 'Тема 24. Иммунная система человека',
      deadline: '2024-09-25 23:59',
      daysLeft: 12
    },

    // Просроченные тесты
    {
      id: 7,
      status: 'overdue',
      subject: 'biology',
      module: 2,
      topic: 'Тема 20. Сердечно-сосудистая система человека',
      overdueDate: '2024-09-14 23:59',
      daysOverdue: 2
    },
    {
      id: 8,
      status: 'overdue',
      subject: 'chemistry',
      module: 1,
      topic: 'Тема 17. Аналитическая химия',
      overdueDate: '2024-09-10 23:59',
      daysOverdue: 6
    }
  ];

  // Данные модулей
  const modules = [
    { id: 1, name: 'Модуль 1' },
    { id: 2, name: 'Модуль 2' },
    { id: 3, name: 'Модуль 3' },
    { id: 4, name: 'Модуль 4' }
  ];

  // Фильтрация тестов по выбранным критериям
  const filteredTests = useMemo(() => {
    return mockTests.filter(test => {
      const statusMatch = test.status === selectedFilter;
      const subjectMatch = test.subject === selectedSubject;
      const moduleMatch = selectedModule === 'all' || test.module === parseInt(selectedModule);
      
      return statusMatch && subjectMatch && moduleMatch;
    });
  }, [selectedFilter, selectedSubject, selectedModule]);

  // Подсчет тестов для счетчиков с учетом фильтров
  const getTestCounts = useMemo(() => {
    const filteredBySubjectAndModule = mockTests.filter(test => {
      const subjectMatch = test.subject === selectedSubject;
      const moduleMatch = selectedModule === 'all' || test.module === parseInt(selectedModule);
      return subjectMatch && moduleMatch;
    });

    return {
      completed: filteredBySubjectAndModule.filter(t => t.status === 'completed').length,
      current: filteredBySubjectAndModule.filter(t => t.status === 'current').length,
      overdue: filteredBySubjectAndModule.filter(t => t.status === 'overdue').length
    };
  }, [selectedSubject, selectedModule]);

  // Компонент карточки теста
  const TestCard = ({ test }) => {
    const getStatusColor = (status) => {
      switch (status) {
        case 'completed':
          return 'border-green-200 bg-green-50';
        case 'current':
          return 'border-primary-200 bg-primary-50';
        case 'overdue':
          return 'border-red-200 bg-red-50';
        default:
          return 'border-neutral-200 bg-white';
      }
    };

    const renderTestContent = () => {
      switch (test.status) {
        case 'completed':
          return (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <h3 className="text-lg font-semibold text-neutral-900">{test.topic}</h3>
              </div>
              <div className="text-right">
                <div className="text-sm text-neutral-600 mb-1">Оценки:</div>
                <div className="flex gap-4">
                  <div className="text-center">
                    <div className="text-xs text-neutral-500">Тренировочный</div>
                    <div className="text-lg font-bold text-green-600">{test.trainingScore}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-neutral-500">Контрольный</div>
                    <div className="text-lg font-bold text-green-600">{test.controlScore}</div>
                  </div>
                </div>
              </div>
            </div>
          );

        case 'current':
          return (
            <>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Clock className="w-6 h-6 text-primary-600" />
                  <h3 className="text-lg font-semibold text-neutral-900">{test.topic}</h3>
                </div>
                <div className="text-right">
                  <div className="text-sm text-neutral-600 mb-1">Необходимо сдать до:</div>
                  <div className="text-sm font-medium text-primary-700">
                    {new Date(test.deadline).toLocaleDateString('ru-RU', {
                      day: 'numeric',
                      month: 'long',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                  <div className="text-xs text-neutral-500 mt-1">
                    Осталось: {test.daysLeft} {test.daysLeft === 1 ? 'день' : test.daysLeft < 5 ? 'дня' : 'дней'}
                  </div>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-3">
                <a
                  href={`/test/${test.id}/training`}
                  className="flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white font-medium hover:bg-primary-700 transition-colors duration-200 text-sm sm:text-base"
                >
                  <Play className="w-4 h-4" />
                  <span className="hidden sm:inline">Решить тренировочный тест</span>
                  <span className="sm:hidden">Тренировочный</span>
                </a>
                <a
                  href={`/test/${test.id}/control`}
                  className="flex items-center justify-center gap-2 px-4 py-2 bg-secondary-400 text-white font-medium hover:bg-secondary-500 transition-colors duration-200 text-sm sm:text-base"
                >
                  <BookOpen className="w-4 h-4" />
                  <span className="hidden sm:inline">Решить контрольный тест</span>
                  <span className="sm:hidden">Контрольный</span>
                </a>
              </div>
            </>
          );

        case 'overdue':
          return (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <XCircle className="w-6 h-6 text-red-600" />
                <h3 className="text-lg font-semibold text-neutral-900">{test.topic}</h3>
              </div>
              <div className="text-right">
                <div className="text-sm text-neutral-600 mb-1">Просрочено:</div>
                <div className="text-sm font-medium text-red-700">
                  {new Date(test.overdueDate).toLocaleDateString('ru-RU', {
                    day: 'numeric',
                    month: 'long',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
                <div className="text-xs text-red-500 mt-1">
                  {test.daysOverdue} {test.daysOverdue === 1 ? 'день' : test.daysOverdue < 5 ? 'дня' : 'дней'} назад
                </div>
              </div>
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
  const Header = () => (
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
            <h1 className="text-3xl md:text-4xl font-bold text-primary-900">
              Ваши тесты
            </h1>
            <p className="text-neutral-600 mt-2">
              Управляйте своими тестами и отслеживайте прогресс
            </p>
          </div>

          {/* Выбор предмета */}
          <div className="flex flex-wrap justify-center gap-2 mb-6">
            <button
              onClick={() => setSelectedSubject('chemistry')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-3 font-medium transition-all duration-200 text-sm sm:text-base ${
                selectedSubject === 'chemistry'
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
              }`}
            >
              Химия
            </button>
            
            <button
              onClick={() => setSelectedSubject('biology')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-3 font-medium transition-all duration-200 text-sm sm:text-base ${
                selectedSubject === 'biology'
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
              }`}
            >
              Биология
            </button>
          </div>

          {/* Выбор модуля */}
          <div className="flex flex-wrap justify-center gap-2 mb-6">
            <button
              onClick={() => setSelectedModule('all')}
              className={`px-3 sm:px-4 py-2 font-medium transition-all duration-200 text-xs sm:text-sm ${
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
                onClick={() => setSelectedModule(module.id.toString())}
                className={`px-3 sm:px-4 py-2 font-medium transition-all duration-200 text-xs sm:text-sm ${
                  selectedModule === module.id.toString()
                    ? 'bg-secondary-400 text-white shadow-lg'
                    : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                }`}
              >
                {module.name}
              </button>
            ))}
          </div>
          <div className="flex gap-2 mb-8">
            <button
              onClick={() => setSelectedFilter('completed')}
              className={`flex items-center gap-2 px-6 py-3 font-medium transition-all duration-200 ${
                selectedFilter === 'completed'
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
              }`}
            >
              <CheckCircle className="w-4 h-4" />
              Сдано
              <span className={`px-2 py-1 text-xs font-bold ${
                selectedFilter === 'completed' 
                  ? 'bg-white/20 text-white' 
                  : 'bg-green-100 text-green-700'
              }`}>
                {mockTests.filter(t => t.status === 'completed').length}
              </span>
            </button>
            
            <button
              onClick={() => setSelectedFilter('current')}
              className={`flex items-center gap-2 px-6 py-3 font-medium transition-all duration-200 ${
                selectedFilter === 'current'
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
              }`}
            >
              <Clock className="w-4 h-4" />
              Актуально
              <span className={`px-2 py-1 text-xs font-bold ${
                selectedFilter === 'current' 
                  ? 'bg-white/20 text-white' 
                  : 'bg-blue-100 text-blue-700'
              }`}>
                {mockTests.filter(t => t.status === 'current').length}
              </span>
            </button>
            
            <button
              onClick={() => setSelectedFilter('overdue')}
              className={`flex items-center gap-2 px-6 py-3 font-medium transition-all duration-200 ${
                selectedFilter === 'overdue'
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
              }`}
            >
              <AlertTriangle className="w-4 h-4" />
              Просрочено
              <span className={`px-2 py-1 text-xs font-bold ${
                selectedFilter === 'overdue' 
                  ? 'bg-white/20 text-white' 
                  : 'bg-red-100 text-red-700'
              }`}>
                {mockTests.filter(t => t.status === 'overdue').length}
              </span>
            </button>
          </div>

          {/* Список тестов */}
          <div className="space-y-4">
            {filteredTests.length > 0 ? (
              filteredTests.map(test => (
                <TestCard key={test.id} test={test} />
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
                  {selectedFilter === 'completed' && 'Вы пока не сдали ни одного теста'}
                  {selectedFilter === 'current' && 'У вас нет актуальных тестов для сдачи'}
                  {selectedFilter === 'overdue' && 'У вас нет просроченных тестов'}
                </p>
              </div>
            )}
          </div>

          {/* Статистика внизу */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-green-50 border-2 border-green-200 p-6 text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {mockTests.filter(t => t.status === 'completed').length}
              </div>
              <div className="text-green-700 font-medium">Сданных тестов</div>
            </div>
            
            <div className="bg-blue-50 border-2 border-blue-200 p-6 text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {mockTests.filter(t => t.status === 'current').length}
              </div>
              <div className="text-blue-700 font-medium">Доступных тестов</div>
            </div>
            
            <div className="bg-red-50 border-2 border-red-200 p-6 text-center">
              <div className="text-3xl font-bold text-red-600 mb-2">
                {mockTests.filter(t => t.status === 'overdue').length}
              </div>
              <div className="text-red-700 font-medium">Просроченных тестов</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentTestsPage;