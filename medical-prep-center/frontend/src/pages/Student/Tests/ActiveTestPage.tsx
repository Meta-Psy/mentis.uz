import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Clock, Save, Send, AlertCircle } from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';
import { useActiveTest } from '../../../hooks/useTest';
import { testsAPI } from '../../../services/api/test';
import type { TestType } from '../../../services/api/test';

interface ActiveTestPageProps {
  testType?: TestType;
}

const ActiveTestPage: React.FC<ActiveTestPageProps> = ({ testType = 'training' }) => {
  const { topicId } = useParams<{ topicId: string }>();
  const navigate = useNavigate();
  
  const [currentQuestion, setCurrentQuestion] = useState(0);
  
  // Используем хук для управления тестом
  const {
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
  } = useActiveTest(parseInt(topicId || '0'), testType);

  // Данные теста (будут загружены через API)
  const [testData, setTestData] = useState<{
    id: number;
    title: string;
    type: TestType;
    totalQuestions: number;
    questions: Array<{
      id: number;
      question: string;
      options: Array<{
        id: string;
        text: string;
      }>;
    }>;
  } | null>(null);

  // Загрузка данных теста
  useEffect(() => {
    const loadTestData = async () => {
      if (!topicId) return;
      
      try {
        // Получаем вопросы по теме
        const questions = await testsAPI.getTopicQuestions(parseInt(topicId), {
          limit: 50,
          random: true
        });

        // Преобразуем в формат для компонента
        const transformedQuestions = questions.map((q) => ({
          id: q.question_id,
          question: q.text,
          options: [
            { id: 'A', text: q.answer_1 || '' },
            { id: 'B', text: q.answer_2 || '' },
            { id: 'C', text: q.answer_3 || '' },
            { id: 'D', text: q.answer_4 || '' }
          ].filter(opt => opt.text) // Убираем пустые варианты
        }));

        setTestData({
          id: parseInt(topicId),
          title: `Тест по теме ${topicId}`, // TODO: получить реальное название темы
          type: testType,
          totalQuestions: transformedQuestions.length,
          questions: transformedQuestions
        });

      } catch (error) {
        console.error('Ошибка загрузки данных теста:', error);
      }
    };

    loadTestData();
  }, [topicId, testType]);

  // Форматирование времени
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes} мин ${remainingSeconds} сек`;
  };

  // Обработка клика по варианту ответа
  const handleAnswerClick = (questionId: number, optionId: string, isCorrect: boolean) => {
    handleAnswerSelection(questionId, optionId, isCorrect);
  };

  // Обработка ПКМ
  const handleRightClick = (e: React.MouseEvent, questionId: number, optionId: string) => {
    e.preventDefault();
    handleAnswerSelection(questionId, optionId, true);
  };

  // Получение статуса вопроса
  const getQuestionStatus = (questionIndex: number) => {
    if (!testData) return 'not-started';
    
    const questionId = testData.questions[questionIndex]?.id;
    if (!questionId) return 'not-started';
    
    const hasAnswer = answers[questionId];
    const hasSelected = selectedAnswers[questionId] && selectedAnswers[questionId].length > 0;
    
    if (hasAnswer) return 'completed';
    if (hasSelected) return 'in-progress';
    return 'not-started';
  };

  // Навигация между вопросами
  const goToQuestion = (index: number) => {
    if (currentQuestion !== index && testData) {
      finalizeAnswer(testData.questions[currentQuestion].id);
      setCurrentQuestion(index);
    }
  };

  const nextQuestion = () => {
    if (testData && currentQuestion < testData.totalQuestions - 1) {
      finalizeAnswer(testData.questions[currentQuestion].id);
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  // Сохранение и завершение
  const handleSaveProgress = () => {
    if (testData) {
      finalizeAnswer(testData.questions[currentQuestion].id);
      saveProgress();
      alert('Прогресс сохранен!');
    }
  };

  const handleSubmitTest = async () => {
    if (!testData) return;
    
    finalizeAnswer(testData.questions[currentQuestion].id);
    
    const unansweredCount = testData.questions.filter(
      (_, index) => !answers[testData.questions[index].id]
    ).length;
    
    if (unansweredCount > 0) {
      const confirm = window.confirm(
        `У вас ${unansweredCount} неотвеченных вопросов. Отправить тест на проверку?`
      );
      if (!confirm) return;
    }
    
    try {
      await submitTest();
      alert('Тест отправлен на проверку!');
      navigate('/tests');
    } catch (error) {
      alert('Ошибка при отправке теста');
    }
  };

  // Обработка завершения теста
  useEffect(() => {
    if (isFinished) {
      navigate('/tests');
    }
  }, [isFinished, navigate]);

  // Показываем загрузку если данные не загружены
  if (loading || !testData) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-lg text-neutral-600">Загрузка теста...</p>
        </div>
      </div>
    );
  }

  // Показываем ошибку если есть
  if (error) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-neutral-900 mb-2">Ошибка загрузки теста</h2>
          <p className="text-neutral-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/tests')}
            className="px-6 py-3 bg-primary-600 text-white font-medium hover:bg-primary-700 transition-colors"
          >
            Вернуться к тестам
          </button>
        </div>
      </div>
    );
  }

  const currentQuestionData = testData.questions[currentQuestion];
  const currentSelected = selectedAnswers[currentQuestionData?.id] || [];

  return (
    <div className="min-h-screen bg-neutral-50 flex">
      {/* Левая часть - 75% */}
      <div className="w-3/4 p-8">
        <div className="bg-white border-2 border-neutral-200 p-8 min-h-full">
          {/* Вопрос */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-neutral-900 mb-6">
              Вопрос {currentQuestion + 1}. {currentQuestionData?.question}
            </h2>
            
            {/* Варианты ответов */}
            <div className="space-y-4">
              {currentQuestionData?.options.map((option) => {
                const isSelected = currentSelected.includes(option.id as any);
                const isAnswered = String(answers[currentQuestionData.id]) === option.id;
                
                return (
                  <div
                    key={option.id}
                    className={`flex items-center p-4 border-2 cursor-pointer transition-all duration-200 ${
                      isAnswered 
                        ? 'border-green-500 bg-green-50' 
                        : isSelected 
                          ? 'border-yellow-500 bg-yellow-50' 
                          : 'border-neutral-300 bg-white hover:border-primary-400 hover:bg-primary-50'
                    }`}
                    onClick={() => handleAnswerClick(currentQuestionData.id, option.id, false)}
                    onContextMenu={(e) => handleRightClick(e, currentQuestionData.id, option.id)}
                  >
                    <div className={`w-10 h-10 border-2 flex items-center justify-center font-bold mr-4 ${
                      isAnswered 
                        ? 'border-green-500 bg-green-500 text-white' 
                        : isSelected 
                          ? 'border-yellow-500 bg-yellow-500 text-white' 
                          : 'border-neutral-400 text-neutral-700'
                    }`}>
                      {option.id}
                    </div>
                    <span className="text-lg text-neutral-800">{option.text}</span>
                  </div>
                );
              })}
            </div>
          </div>
          
          {/* Навигация */}
          <div className="flex justify-between">
            <button
              onClick={prevQuestion}
              disabled={currentQuestion === 0}
              className={`flex items-center gap-2 px-6 py-3 font-medium transition-all duration-200 ${
                currentQuestion === 0
                  ? 'bg-neutral-200 text-neutral-500 cursor-not-allowed'
                  : 'bg-neutral-600 text-white hover:bg-neutral-700'
              }`}
            >
              <ChevronLeft className="w-4 h-4" />
              Назад
            </button>
            
            <button
              onClick={nextQuestion}
              disabled={currentQuestion === testData.totalQuestions - 1}
              className={`flex items-center gap-2 px-6 py-3 font-medium transition-all duration-200 ${
                currentQuestion === testData.totalQuestions - 1
                  ? 'bg-neutral-200 text-neutral-500 cursor-not-allowed'
                  : 'bg-primary-600 text-white hover:bg-primary-700'
              }`}
            >
              Далее
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Правая часть - 25% */}
      <div className="w-1/4 p-8 bg-neutral-100">
        <div className="sticky top-8">
          {/* Информация о тесте */}
          <div className="bg-white border-2 border-neutral-200 p-6 mb-6">
            <h3 className="text-lg font-bold text-neutral-900 mb-4">
              {testData.title}
            </h3>
            
            <div className="flex items-center gap-2 mb-4">
              <Clock className="w-4 h-4 text-primary-600" />
              <span className="text-sm text-neutral-600">Время решения теста:</span>
            </div>
            <div className="text-xl font-bold text-primary-600 mb-4">
              {formatTime(timeElapsed)}
            </div>
          </div>
          
          {/* Карта вопросов */}
          <div className="bg-white border-2 border-neutral-200 p-6 mb-6">
            <h4 className="font-bold text-neutral-900 mb-4">Прогресс</h4>
            <div className="grid grid-cols-5 gap-2">
              {testData.questions.map((_, index) => {
                const status = getQuestionStatus(index);
                const isCurrent = index === currentQuestion;
                
                return (
                  <button
                    key={index}
                    onClick={() => goToQuestion(index)}
                    className={`w-10 h-10 text-sm font-bold border-2 transition-all duration-200 ${
                      isCurrent
                        ? 'border-primary-600 bg-primary-600 text-white'
                        : status === 'completed'
                          ? 'border-green-500 bg-green-500 text-white'
                          : status === 'in-progress'
                            ? 'border-yellow-500 bg-yellow-500 text-white'
                            : 'border-neutral-300 bg-white text-neutral-700 hover:border-primary-400'
                    }`}
                  >
                    {index + 1}
                  </button>
                );
              })}
            </div>
          </div>
          
          {/* Действия */}
          <div className="space-y-3">
            <button
              onClick={handleSaveProgress}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-yellow-600 text-white font-medium hover:bg-yellow-700 disabled:bg-yellow-400 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <Save className="w-4 h-4" />
              {loading ? 'Сохранение...' : 'Закончить позже'}
            </button>
            
            <button
              onClick={handleSubmitTest}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white font-medium hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <Send className="w-4 h-4" />
              {loading ? 'Отправка...' : 'Отправить на проверку'}
            </button>
          </div>
          
          {/* Статистика */}
          <div className="bg-white border-2 border-neutral-200 p-4 mt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {Object.keys(answers).length}
              </div>
              <div className="text-sm text-neutral-600">из {testData.totalQuestions} отвечено</div>
            </div>
          </div>
          
          {/* Инструкции */}
          <div className="bg-blue-50 border-2 border-blue-200 p-4 mt-6">
            <h5 className="font-bold text-blue-900 mb-2">Инструкция:</h5>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• ЛКМ - убрать выбор</li>
              <li>• ПКМ - выбрать ответ</li>
              <li>• Жёлтый - выбранные варианты</li>
              <li>• Зелёный - финальный ответ</li>
            </ul>
          </div>
          
          {/* Показываем ошибки если есть */}
          {error && (
            <div className="bg-red-50 border-2 border-red-200 p-4 mt-6">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-600" />
                <span className="text-sm font-medium text-red-900">Ошибка</span>
              </div>
              <p className="text-sm text-red-800 mt-1">{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ActiveTestPage;