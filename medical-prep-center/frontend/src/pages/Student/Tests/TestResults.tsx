import { useState, useMemo, useEffect } from 'react';
import { CheckCircle, XCircle, List, Trophy, Users, User, Clock, Award, TrendingUp } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useTestResults, useAssessmentPage } from '../../../hooks/useTestResult';
import { testsAPI } from '../../../services/api/test_result';

// Типы для компонента
interface TestResultsProps {
  sessionId?: string;
  studentId?: number;
}

interface QuestionResult {
  question_id: number;
  question_text: string;
  user_answer: number;
  correct_answer: number;
  is_correct: boolean;
  explanation?: string;
}

interface RankingStudent {
  rank: number;
  group: number;
  name: string;
  score: number;
  time: number;
}

interface RankingData {
  overall: RankingStudent[];
  group: RankingStudent[];
}

interface StatisticsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color?: 'primary' | 'green' | 'red' | 'blue';
}

const TestResults: React.FC<TestResultsProps> = ({ sessionId, studentId = 1 }) => {
  const [selectedQuestionFilter, setSelectedQuestionFilter] = useState<'all' | 'correct' | 'incorrect'>('all');
  const [selectedRankingType, setSelectedRankingType] = useState<keyof RankingData>('overall');

  // Используем реальные хуки для получения данных
  const { result, detailedResults, recommendations, loading, error } = useTestResults(sessionId);
  const { statistics } = useAssessmentPage(studentId);

  // Загружаем дополнительные данные при монтировании
  useEffect(() => {
    if (result?.topic_id) {
      // Можно загрузить дополнительную информацию о теме
      fetchTopicInfo(result.topic_id);
    }
  }, [result]);

  const fetchTopicInfo = async (topicId: number): Promise<void> => {
    try {
      // Здесь можно получить информацию о теме из API материалов
      console.log('Загрузка информации о теме:', topicId);
    } catch (error) {
      console.error('Ошибка загрузки информации о теме:', error);
    }
  };

  // Фильтрация вопросов на основе реальных данных
  const filteredQuestions = useMemo(() => {
    if (!detailedResults) return [];
    
    switch (selectedQuestionFilter) {
      case 'correct':
        return detailedResults.filter((q: QuestionResult) => q.is_correct);
      case 'incorrect':
        return detailedResults.filter((q: QuestionResult) => !q.is_correct);
      default:
        return detailedResults;
    }
  }, [detailedResults, selectedQuestionFilter]);

  // Показываем загрузку
  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-neutral-600">Загрузка результатов...</p>
        </div>
      </div>
    );
  }

  // Показываем ошибку
  if (error) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-neutral-900 mb-2">Ошибка загрузки</h2>
          <p className="text-neutral-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
          >
            Обновить страницу
          </button>
        </div>
      </div>
    );
  }

  // Если нет результата, показываем сообщение
  if (!result) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <List className="w-16 h-16 text-neutral-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-neutral-900 mb-2">Результат не найден</h2>
          <p className="text-neutral-600">Результат теста недоступен или еще не готов</p>
        </div>
      </div>
    );
  }

  // Круговая диаграмма
  const CircularChart: React.FC = () => {
    const percentage = Math.round(result.score_percentage);
    const circumference = 2 * Math.PI * 45;
    const strokeDasharray = `${(percentage / 100) * circumference} ${circumference}`;

    return (
      <div className="relative w-32 h-32 lg:w-40 lg:h-40 mx-auto mb-6">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Фоновый круг */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="8"
          />
          {/* Прогресс */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke={result.passed ? "#10b981" : "#ef4444"}
            strokeWidth="8"
            strokeDasharray={strokeDasharray}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={`text-lg lg:text-2xl font-bold ${result.passed ? 'text-green-600' : 'text-red-600'}`}>
              {percentage}%
            </div>
            <div className="text-xs lg:text-sm text-neutral-600">правильно</div>
          </div>
        </div>
      </div>
    );
  };

  // Компонент карточки вопроса
  const QuestionCard: React.FC<{ question: QuestionResult; index: number }> = ({ question, index }) => (
    <div className={`border-2 p-4 lg:p-6 mb-4 ${
      question.is_correct 
        ? 'border-green-200 bg-green-50' 
        : 'border-red-200 bg-red-50'
    }`}>
      <div className="flex items-start gap-4">
        <div className={`w-8 h-8 lg:w-10 lg:h-10 border-2 flex items-center justify-center font-bold text-sm lg:text-base ${
          question.is_correct 
            ? 'border-green-500 bg-green-500 text-white' 
            : 'border-red-500 bg-red-500 text-white'
        }`}>
          {index + 1}
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-neutral-900 mb-3 text-sm lg:text-base">
            {question.question_text}
          </h4>
          <div className="space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2">
              <span className="text-xs lg:text-sm text-neutral-600 font-medium">Правильный ответ:</span>
              <span className="px-3 py-1 bg-green-100 text-green-800 font-medium text-xs lg:text-sm">
                Вариант {question.correct_answer}
              </span>
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center gap-2">
              <span className="text-xs lg:text-sm text-neutral-600 font-medium">Ваш ответ:</span>
              <span className={`px-3 py-1 font-medium text-xs lg:text-sm ${
                question.is_correct 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                Вариант {question.user_answer}
              </span>
            </div>
            {question.explanation && (
              <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                <p className="text-sm text-blue-800">
                  <strong>Объяснение:</strong> {question.explanation}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  // Компонент таблицы рейтинга (пока с моковыми данными)
  const RankingTable: React.FC = () => {
    // Используем моковые данные для рейтинга, так как API для этого пока нет
    const mockRankingData: RankingData = {
      overall: [
        { rank: 1, group: 1, name: 'Петрова Мария Сергеевна', score: Math.min(result.total_questions, result.correct_answers + 7), time: result.time_spent_seconds - 740 },
        { rank: 2, group: 2, name: 'Сидоров Дмитрий Александрович', score: Math.min(result.total_questions, result.correct_answers + 6), time: result.time_spent_seconds - 590 },
        { rank: 3, group: 1, name: 'Козлова Анна Викторовна', score: Math.min(result.total_questions, result.correct_answers + 5), time: result.time_spent_seconds - 660 },
        { rank: 4, group: 4, name: 'Николаев Игорь Петрович', score: Math.min(result.total_questions, result.correct_answers + 4), time: result.time_spent_seconds - 540 },
        { rank: 5, group: 2, name: 'Морозова Елена Андреевна', score: Math.min(result.total_questions, result.correct_answers + 3), time: result.time_spent_seconds - 420 },
        { rank: 6, group: 1, name: 'Федоров Максим Игоревич', score: Math.min(result.total_questions, result.correct_answers + 2), time: result.time_spent_seconds - 460 },
        { rank: 7, group: 4, name: 'Волкова София Дмитриевна', score: Math.min(result.total_questions, result.correct_answers + 1), time: result.time_spent_seconds - 340 },
        { rank: 8, group: 2, name: 'Орлов Артем Сергеевич', score: result.correct_answers + 1, time: result.time_spent_seconds - 190 },
        { rank: 9, group: 1, name: 'Лебедева Ксения Александровна', score: result.correct_answers, time: result.time_spent_seconds - 120 },
        { rank: 10, group: 3, name: 'Текущий студент', score: result.correct_answers, time: result.time_spent_seconds },
      ],
      group: [
        { rank: 1, group: 3, name: 'Васильев Андрей Николаевич', score: Math.min(result.total_questions, result.correct_answers + 2), time: result.time_spent_seconds - 640 },
        { rank: 2, group: 3, name: 'Григорьева Ольга Михайловна', score: Math.min(result.total_questions, result.correct_answers + 1), time: result.time_spent_seconds - 490 },
        { rank: 3, group: 3, name: 'Текущий студент', score: result.correct_answers, time: result.time_spent_seconds },
        { rank: 4, group: 3, name: 'Смирнов Владимир Петрович', score: Math.max(0, result.correct_answers - 1), time: result.time_spent_seconds + 60 },
        { rank: 5, group: 3, name: 'Кузнецова Татьяна Ивановна', score: Math.max(0, result.correct_answers - 3), time: result.time_spent_seconds + 260 },
        { rank: 6, group: 3, name: 'Михайлов Сергей Дмитриевич', score: Math.max(0, result.correct_answers - 4), time: result.time_spent_seconds + 360 }
      ]
    };
    
    const data = mockRankingData[selectedRankingType];
    
    return (
      <div className="bg-white border-2 border-neutral-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-primary-600 text-white">
              <tr>
                <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">№</th>
                <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">Группа</th>
                <th className="px-3 lg:px-6 py-3 lg:py-4 text-left font-semibold text-sm lg:text-base">Ф.И.О.</th>
                <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">Балл</th>
                <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">Время</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {data.map((student: RankingStudent) => (
                <tr
                  key={student.rank}
                  className={`transition-colors duration-200 ${
                    student.name === 'Текущий студент'
                      ? 'bg-primary-50 border-primary-200 border-2'
                      : 'hover:bg-neutral-50'
                  }`}
                >
                  <td className="px-3 lg:px-6 py-3 lg:py-4 text-center">
                    <div className="flex items-center justify-center gap-2">
                      {student.rank <= 3 && (
                        <Trophy className={`w-4 h-4 ${
                          student.rank === 1 ? 'text-yellow-500' : 
                          student.rank === 2 ? 'text-gray-400' : 'text-amber-600'
                        }`} />
                      )}
                      <span className="font-bold text-primary-700 text-sm lg:text-base">{student.rank}</span>
                    </div>
                  </td>
                  <td className="px-3 lg:px-6 py-3 lg:py-4 text-center">
                    <span className="px-2 py-1 bg-secondary-100 text-secondary-700 text-xs lg:text-sm font-medium">
                      {student.group}
                    </span>
                  </td>
                  <td className="px-3 lg:px-6 py-3 lg:py-4">
                    <span className={`font-medium text-sm lg:text-base ${
                      student.name === 'Текущий студент' ? 'text-primary-700' : 'text-neutral-900'
                    }`}>
                      {student.name}
                    </span>
                  </td>
                  <td className="px-3 lg:px-6 py-3 lg:py-4 text-center">
                    <span className="font-bold text-green-600 text-sm lg:text-base">{student.score}</span>
                  </td>
                  <td className="px-3 lg:px-6 py-3 lg:py-4 text-center">
                    <span className="text-neutral-600 text-xs lg:text-sm">
                      {testsAPI.formatTime(student.time)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  // Компонент статистики
  const StatisticsCard: React.FC<StatisticsCardProps> = ({ title, value, icon: Icon, color = 'primary' }) => (
    <div className={`p-4 rounded-lg border-2 ${
      color === 'green' ? 'bg-green-50 border-green-200' :
      color === 'red' ? 'bg-red-50 border-red-200' :
      color === 'blue' ? 'bg-blue-50 border-blue-200' :
      'bg-neutral-50 border-neutral-200'
    }`}>
      <div className="flex items-center gap-3">
        <Icon className={`w-6 h-6 ${
          color === 'green' ? 'text-green-600' :
          color === 'red' ? 'text-red-600' :
          color === 'blue' ? 'text-blue-600' :
          'text-neutral-600'
        }`} />
        <div>
          <div className={`text-xl font-bold ${
            color === 'green' ? 'text-green-600' :
            color === 'red' ? 'text-red-600' :
            color === 'blue' ? 'text-blue-600' :
            'text-neutral-600'
          }`}>
            {value}
          </div>
          <div className="text-sm text-neutral-600">{title}</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-neutral-50 p-4 lg:p-8">
      <div className="container mx-auto">
        {/* Заголовок */}
        <div className="text-center mb-8">
          <h1 className="text-2xl lg:text-4xl font-bold text-primary-900 mb-2">
            Результаты тестирования
          </h1>
          <p className="text-neutral-600 text-sm lg:text-base">
            Тест по теме {result.topic_id} • {result.test_type === 'training' ? 'Тренировочный' : 'Контрольный'}
          </p>
          {result.passed ? (
            <div className="inline-flex items-center gap-2 mt-2 px-4 py-2 bg-green-100 text-green-800 rounded-full">
              <CheckCircle className="w-4 h-4" />
              <span className="font-medium">Тест сдан</span>
            </div>
          ) : (
            <div className="inline-flex items-center gap-2 mt-2 px-4 py-2 bg-red-100 text-red-800 rounded-full">
              <XCircle className="w-4 h-4" />
              <span className="font-medium">Тест не сдан</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 lg:gap-8">
          {/* Левая часть - результаты */}
          <div className="xl:col-span-2">
            {/* Блок результата */}
            <div className="bg-white border-2 border-neutral-200 p-6 lg:p-8 mb-6 lg:mb-8">
              <h2 className="text-xl lg:text-2xl font-bold text-neutral-900 mb-6 text-center lg:text-left">
                Ваш результат
              </h2>
              
              <div className="flex flex-col lg:flex-row items-center gap-6 lg:gap-8">
                {/* Круговая диаграмма */}
                <div className="text-center">
                  <CircularChart />
                  <div className="space-y-2">
                    <div className="text-lg lg:text-xl font-bold text-neutral-900">
                      Балл: {result.correct_answers}/{result.total_questions}
                    </div>
                    <div className="text-sm lg:text-base text-neutral-600">
                      Время: {testsAPI.formatTime(result.time_spent_seconds)}
                    </div>
                  </div>
                </div>

                {/* Статистика */}
                <div className="flex-1 w-full lg:w-auto">
                  <div className="grid grid-cols-2 gap-4 lg:gap-6 mb-4">
                    <StatisticsCard
                      title="Правильных"
                      value={result.correct_answers}
                      icon={CheckCircle}
                      color="green"
                    />
                    <StatisticsCard
                      title="Неправильных"
                      value={result.total_questions - result.correct_answers}
                      icon={XCircle}
                      color="red"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 lg:gap-6">
                    <StatisticsCard
                      title="Время"
                      value={testsAPI.formatTime(result.time_spent_seconds)}
                      icon={Clock}
                      color="blue"
                    />
                    <StatisticsCard
                      title="Процент"
                      value={`${Math.round(result.score_percentage)}%`}
                      icon={TrendingUp}
                      color={result.passed ? 'green' : 'red'}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Рекомендации */}
            {recommendations && recommendations.length > 0 && (
              <div className="bg-blue-50 border-2 border-blue-200 p-4 lg:p-6 mb-6 lg:mb-8">
                <h3 className="text-lg font-bold text-blue-900 mb-3 flex items-center gap-2">
                  <Award className="w-5 h-5" />
                  Рекомендации
                </h3>
                <ul className="space-y-2">
                  {recommendations.map((recommendation, index) => (
                    <li key={index} className="text-blue-800 flex items-start gap-2">
                      <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                      {recommendation}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Фильтры вопросов */}
            <div className="flex flex-wrap justify-center gap-2 mb-6">
              <button
                onClick={() => setSelectedQuestionFilter('all')}
                className={`flex items-center gap-2 px-4 lg:px-6 py-2 lg:py-3 font-medium transition-all duration-200 text-sm lg:text-base ${
                  selectedQuestionFilter === 'all'
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                }`}
              >
                <List className="w-4 h-4" />
                <span className="hidden sm:inline">Все вопросы</span>
                <span className="sm:hidden">Все</span>
                <span className={`px-2 py-1 text-xs font-bold rounded ${
                  selectedQuestionFilter === 'all' 
                    ? 'bg-white/20 text-white' 
                    : 'bg-neutral-100 text-neutral-700'
                }`}>
                  {result.total_questions}
                </span>
              </button>
              
              <button
                onClick={() => setSelectedQuestionFilter('correct')}
                className={`flex items-center gap-2 px-4 lg:px-6 py-2 lg:py-3 font-medium transition-all duration-200 text-sm lg:text-base ${
                  selectedQuestionFilter === 'correct'
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                }`}
              >
                <CheckCircle className="w-4 h-4" />
                <span className="hidden sm:inline">Правильные</span>
                <span className="sm:hidden">✓</span>
                <span className={`px-2 py-1 text-xs font-bold rounded ${
                  selectedQuestionFilter === 'correct' 
                    ? 'bg-white/20 text-white' 
                    : 'bg-green-100 text-green-700'
                }`}>
                  {result.correct_answers}
                </span>
              </button>
              
              <button
                onClick={() => setSelectedQuestionFilter('incorrect')}
                className={`flex items-center gap-2 px-4 lg:px-6 py-2 lg:py-3 font-medium transition-all duration-200 text-sm lg:text-base ${
                  selectedQuestionFilter === 'incorrect'
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
                }`}
              >
                <XCircle className="w-4 h-4" />
                <span className="hidden sm:inline">Неправильные</span>
                <span className="sm:hidden">✗</span>
                <span className={`px-2 py-1 text-xs font-bold rounded ${
                  selectedQuestionFilter === 'incorrect' 
                    ? 'bg-white/20 text-white' 
                    : 'bg-red-100 text-red-700'
                }`}>
                  {result.total_questions - result.correct_answers}
                </span>
              </button>
            </div>

            {/* Список вопросов */}
            <div className="space-y-4">
              {filteredQuestions.length > 0 ? (
                filteredQuestions.map((question, index) => (
                  <QuestionCard key={question.question_id} question={question} index={index} />
                ))
              ) : (
                <div className="text-center py-8 text-neutral-500">
                  <List className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Нет вопросов для отображения</p>
                </div>
              )}
            </div>
          </div>

          {/* Правая часть - рейтинг */}
          <div className="xl:col-span-1">
            <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6">
              <h3 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
                Рейтинг
              </h3>
              
              {/* Кнопки выбора рейтинга */}
              <div className="flex gap-2 mb-4 lg:mb-6">
                <button
                  onClick={() => setSelectedRankingType('overall')}
                  className={`flex items-center gap-2 px-3 lg:px-4 py-2 font-medium transition-all duration-200 text-sm lg:text-base flex-1 justify-center ${
                    selectedRankingType === 'overall'
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
                  }`}
                >
                  <Users className="w-4 h-4" />
                  <span className="hidden sm:inline">Общий</span>
                  <span className="sm:hidden">Общий</span>
                </button>
                
                <button
                  onClick={() => setSelectedRankingType('group')}
                  className={`flex items-center gap-2 px-3 lg:px-4 py-2 font-medium transition-all duration-200 text-sm lg:text-base flex-1 justify-center ${
                    selectedRankingType === 'group'
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
                  }`}
                >
                  <User className="w-4 h-4" />
                  <span className="hidden sm:inline">Моя группа</span>
                  <span className="sm:hidden">Группа</span>
                </button>
              </div>
              
              {/* Таблица рейтинга */}
              <RankingTable />

              {/* Статистика */}
              {statistics && (
                <div className="mt-6 p-4 bg-neutral-50 border border-neutral-200 rounded">
                  <h4 className="font-semibold text-neutral-900 mb-3">Ваша статистика</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Всего тестов:</span>
                      <span className="font-medium">{statistics.completed_tests}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Средний балл:</span>
                      <span className="font-medium">{statistics.average_score.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Время изучения:</span>
                      <span className="font-medium">{statistics.total_time_spent_hours.toFixed(1)}ч</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Кнопки действий */}
        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => window.history.back()}
            className="px-6 py-3 bg-neutral-200 text-neutral-700 font-medium rounded-lg hover:bg-neutral-300 transition-colors"
          >
            Вернуться к тестам
          </button>
          
          {result.test_type === 'training' && !result.passed && (
            <button
              onClick={() => {
                // Логика повторного прохождения теста
                const newSessionUrl = `/test/${result.topic_id}`;
                window.location.href = newSessionUrl;
              }}
              className="px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
            >
              Пройти еще раз
            </button>
          )}
          
          <button
            onClick={() => {
              // Логика перехода к материалам темы
              const materialsUrl = `/materials/topic/${result.topic_id}`;
              window.location.href = materialsUrl;
            }}
            className="px-6 py-3 bg-secondary-600 text-white font-medium rounded-lg hover:bg-secondary-700 transition-colors"
          >
            Изучить материал
          </button>
        </div>
      </div>
    </div>
  );
};

export default TestResults;