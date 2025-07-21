import React, { useState, useMemo } from 'react';
import { CheckCircle, XCircle, List, Trophy, Users, User } from 'lucide-react';

const TestResults = () => {
  const [selectedQuestionFilter, setSelectedQuestionFilter] = useState('all');
  const [selectedRankingType, setSelectedRankingType] = useState('overall');

  // Моковые данные результата теста
  const testResult = {
    testId: 4,
    title: 'Тема 21. Дыхательная система',
    totalQuestions: 50,
    correctAnswers: 41,
    incorrectAnswers: 9,
    timeSpent: 2840, // в секундах (47 минут 20 секунд)
    currentStudentId: 1,
    currentStudentGroup: 3,
    currentStudentName: 'Иванов Алексей Игоревич',
    ranking: {
      overall: 10,
      group: 3
    }
  };

  // Моковые данные вопросов с ответами
  const questionResults = Array.from({ length: 50 }, (_, index) => ({
    questionNumber: index + 1,
    questionText: `Вопрос ${index + 1}. Пример вопроса по дыхательной системе человека?`,
    correctAnswer: 'A',
    studentAnswer: index < 41 ? 'A' : 'B', // первые 41 правильные
    isCorrect: index < 41,
    options: {
      A: 'Правильный ответ на вопрос',
      B: 'Неправильный вариант ответа',
      C: 'Еще один неправильный вариант',
      D: 'Последний неправильный вариант'
    }
  }));

  // Моковые данные рейтинга
  const rankingData = {
    overall: [
      { rank: 1, group: 1, name: 'Петрова Мария Сергеевна', score: 48, time: 2100 },
      { rank: 2, group: 2, name: 'Сидоров Дмитрий Александрович', score: 47, time: 2250 },
      { rank: 3, group: 1, name: 'Козлова Анна Викторовна', score: 46, time: 2180 },
      { rank: 4, group: 4, name: 'Николаев Игорь Петрович', score: 45, time: 2300 },
      { rank: 5, group: 2, name: 'Морозова Елена Андреевна', score: 44, time: 2420 },
      { rank: 6, group: 1, name: 'Федоров Максим Игоревич', score: 43, time: 2380 },
      { rank: 7, group: 4, name: 'Волкова София Дмитриевна', score: 42, time: 2500 },
      { rank: 8, group: 2, name: 'Орлов Артем Сергеевич', score: 42, time: 2650 },
      { rank: 9, group: 1, name: 'Лебедева Ксения Александровна', score: 41, time: 2720 },
      { rank: 10, group: 3, name: 'Иванов Алексей Игоревич', score: 41, time: 2840 },
      { rank: 11, group: 3, name: 'Смирнов Владимир Петрович', score: 40, time: 2900 },
      { rank: 12, group: 4, name: 'Попова Екатерина Сергеевна', score: 39, time: 2950 }
    ],
    group: [
      { rank: 1, group: 3, name: 'Васильев Андрей Николаевич', score: 43, time: 2200 },
      { rank: 2, group: 3, name: 'Григорьева Ольга Михайловна', score: 42, time: 2350 },
      { rank: 3, group: 3, name: 'Иванов Алексей Игоревич', score: 41, time: 2840 },
      { rank: 4, group: 3, name: 'Смирнов Владимир Петрович', score: 40, time: 2900 },
      { rank: 5, group: 3, name: 'Кузнецова Татьяна Ивановна', score: 38, time: 3100 },
      { rank: 6, group: 3, name: 'Михайлов Сергей Дмитриевич', score: 37, time: 3200 }
    ]
  };

  // Фильтрация вопросов
  const filteredQuestions = useMemo(() => {
    switch (selectedQuestionFilter) {
      case 'correct':
        return questionResults.filter(q => q.isCorrect);
      case 'incorrect':
        return questionResults.filter(q => !q.isCorrect);
      default:
        return questionResults;
    }
  }, [selectedQuestionFilter]);

  // Круговая диаграмма
  const CircularChart = () => {
    const percentage = Math.round((testResult.correctAnswers / testResult.totalQuestions) * 100);
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
            stroke="#3e588b"
            strokeWidth="8"
            strokeDasharray={strokeDasharray}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-lg lg:text-2xl font-bold text-primary-600">{percentage}%</div>
            <div className="text-xs lg:text-sm text-neutral-600">правильно</div>
          </div>
        </div>
      </div>
    );
  };

  // Компонент карточки вопроса
  const QuestionCard = ({ question }) => (
    <div className={`border-2 p-4 lg:p-6 mb-4 ${
      question.isCorrect 
        ? 'border-green-200 bg-green-50' 
        : 'border-red-200 bg-red-50'
    }`}>
      <div className="flex items-start gap-4">
        <div className={`w-8 h-8 lg:w-10 lg:h-10 border-2 flex items-center justify-center font-bold text-sm lg:text-base ${
          question.isCorrect 
            ? 'border-green-500 bg-green-500 text-white' 
            : 'border-red-500 bg-red-500 text-white'
        }`}>
          {question.questionNumber}
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-neutral-900 mb-3 text-sm lg:text-base">
            {question.questionText}
          </h4>
          <div className="space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2">
              <span className="text-xs lg:text-sm text-neutral-600 font-medium">Правильный ответ:</span>
              <span className="px-3 py-1 bg-green-100 text-green-800 font-medium text-xs lg:text-sm">
                {question.correctAnswer}. {question.options[question.correctAnswer]}
              </span>
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center gap-2">
              <span className="text-xs lg:text-sm text-neutral-600 font-medium">Ваш ответ:</span>
              <span className={`px-3 py-1 font-medium text-xs lg:text-sm ${
                question.isCorrect 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {question.studentAnswer}. {question.options[question.studentAnswer]}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Компонент таблицы рейтинга
  const RankingTable = () => {
    const data = rankingData[selectedRankingType];
    
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
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              {data.map((student) => (
                <tr
                  key={student.rank}
                  className={`transition-colors duration-200 ${
                    student.name === testResult.currentStudentName
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
                      student.name === testResult.currentStudentName ? 'text-primary-700' : 'text-neutral-900'
                    }`}>
                      {student.name}
                    </span>
                  </td>
                  <td className="px-3 lg:px-6 py-3 lg:py-4 text-center">
                    <span className="font-bold text-green-600 text-sm lg:text-base">{student.score}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes} мин ${remainingSeconds} сек`;
  };

  return (
    <div className="min-h-screen bg-neutral-50 p-4 lg:p-8">
      <div className="container mx-auto">
        {/* Заголовок */}
        <div className="text-center mb-8">
          <h1 className="text-2xl lg:text-4xl font-bold text-primary-900 mb-2">
            {testResult.title}
          </h1>
          <p className="text-neutral-600 text-sm lg:text-base">Результаты вашего тестирования</p>
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
                      Балл: {testResult.correctAnswers}/{testResult.totalQuestions}
                    </div>
                    <div className="text-sm lg:text-base text-neutral-600">
                      Время: {formatTime(testResult.timeSpent)}
                    </div>
                    <div className="text-sm lg:text-base text-primary-600 font-medium">
                      Рейтинг: {testResult.ranking.overall} место
                    </div>
                  </div>
                </div>

                {/* Статистика */}
                <div className="flex-1 w-full lg:w-auto">
                  <div className="grid grid-cols-2 gap-4 lg:gap-6">
                    <div className="text-center p-4 bg-green-50 border-2 border-green-200">
                      <div className="text-xl lg:text-2xl font-bold text-green-600 mb-1">
                        {testResult.correctAnswers}
                      </div>
                      <div className="text-xs lg:text-sm text-green-700">Правильных</div>
                    </div>
                    <div className="text-center p-4 bg-red-50 border-2 border-red-200">
                      <div className="text-xl lg:text-2xl font-bold text-red-600 mb-1">
                        {testResult.incorrectAnswers}
                      </div>
                      <div className="text-xs lg:text-sm text-red-700">Неправильных</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

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
                  {testResult.totalQuestions}
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
                  {testResult.correctAnswers}
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
                  {testResult.incorrectAnswers}
                </span>
              </button>
            </div>

            {/* Список вопросов */}
            <div className="space-y-4">
              {filteredQuestions.map((question) => (
                <QuestionCard key={question.questionNumber} question={question} />
              ))}
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
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestResults;