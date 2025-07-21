import React, { useState, useEffect, useMemo } from 'react';
import { ChevronLeft, ChevronRight, Clock, Save, Send } from 'lucide-react';

const ActiveTestPage = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});

  // Моковые данные теста
  const testData = {
    id: 4,
    title: 'Тема 25. Нервная система человека',
    type: 'training', // или 'control'
    totalQuestions: 50,
    questions: Array.from({ length: 50 }, (_, index) => ({
      id: index + 1,
      question: index === 0 
        ? 'С какого позвонка начинается трахея?' 
        : `Вопрос ${index + 1}. Пример вопроса по нервной системе человека?`,
      options: [
        { id: 'A', text: 'С первого шейного позвонка (атлас)' },
        { id: 'B', text: 'С седьмого шейного позвонка' },
        { id: 'C', text: 'С шестого шейного позвонка' },
        { id: 'D', text: 'С пятого шейного позвонка' }
      ]
    }))
  };

  // Загрузка сохраненных ответов из localStorage при загрузке
  useEffect(() => {
    const savedAnswers = localStorage.getItem(`test_${testData.id}_answers`);
    const savedTime = localStorage.getItem(`test_${testData.id}_time`);
    const savedSelected = localStorage.getItem(`test_${testData.id}_selected`);
    
    if (savedAnswers) {
      setAnswers(JSON.parse(savedAnswers));
    }
    if (savedTime) {
      setTimeElapsed(parseInt(savedTime));
    }
    if (savedSelected) {
      setSelectedAnswers(JSON.parse(savedSelected));
    }
  }, [testData.id]);

  // Таймер
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeElapsed(prev => {
        const newTime = prev + 1;
        localStorage.setItem(`test_${testData.id}_time`, newTime.toString());
        return newTime;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [testData.id]);

  // Сохранение ответов в localStorage при изменении
  useEffect(() => {
    localStorage.setItem(`test_${testData.id}_answers`, JSON.stringify(answers));
  }, [answers, testData.id]);

  useEffect(() => {
    localStorage.setItem(`test_${testData.id}_selected`, JSON.stringify(selectedAnswers));
  }, [selectedAnswers, testData.id]);

  // Форматирование времени
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes} мин ${remainingSeconds} сек`;
  };

  // Обработка клика по варианту ответа
  const handleAnswerClick = (questionId, optionId, isCorrect) => {
    const currentSelected = selectedAnswers[questionId] || [];
    
    if (isCorrect) {
      // ПКМ - выбрать как правильный
      if (!currentSelected.includes(optionId)) {
        setSelectedAnswers(prev => ({
          ...prev,
          [questionId]: [...currentSelected, optionId]
        }));
      }
    } else {
      // ЛКМ - убрать из выбранных
      setSelectedAnswers(prev => ({
        ...prev,
        [questionId]: currentSelected.filter(id => id !== optionId)
      }));
    }
  };

  // Обработка ПКМ
  const handleRightClick = (e, questionId, optionId) => {
    e.preventDefault();
    handleAnswerClick(questionId, optionId, true);
  };

  // Финализация ответа для следующего вопроса
  const finalizeAnswer = (questionId) => {
    const selected = selectedAnswers[questionId] || [];
    if (selected.length === 1) {
      setAnswers(prev => ({
        ...prev,
        [questionId]: selected[0]
      }));
    }
  };

  // Получение статуса вопроса
  const getQuestionStatus = (questionIndex) => {
    const questionId = questionIndex + 1;
    const hasAnswer = answers[questionId];
    const hasSelected = selectedAnswers[questionId] && selectedAnswers[questionId].length > 0;
    
    if (hasAnswer) return 'completed';
    if (hasSelected) return 'in-progress';
    return 'not-started';
  };

  // Навигация между вопросами
  const goToQuestion = (index) => {
    if (currentQuestion !== index) {
      finalizeAnswer(currentQuestion + 1);
      setCurrentQuestion(index);
    }
  };

  const nextQuestion = () => {
    if (currentQuestion < testData.totalQuestions - 1) {
      finalizeAnswer(currentQuestion + 1);
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  // Сохранение и завершение
  const saveProgress = () => {
    finalizeAnswer(currentQuestion + 1);
    alert('Прогресс сохранен!');
  };

  const submitTest = () => {
    finalizeAnswer(currentQuestion + 1);
    const unanswered = testData.questions.filter((_, index) => !answers[index + 1]).length;
    
    if (unanswered > 0) {
      if (!confirm(`У вас ${unanswered} неотвеченных вопросов. Отправить тест на проверку?`)) {
        return;
      }
    }
    
    // Очистка localStorage
    localStorage.removeItem(`test_${testData.id}_answers`);
    localStorage.removeItem(`test_${testData.id}_time`);
    localStorage.removeItem(`test_${testData.id}_selected`);
    
    alert('Тест отправлен на проверку!');
    // Редирект на страницу результатов
    window.location.href = '/tests';
  };

  const currentQuestionData = testData.questions[currentQuestion];
  const currentSelected = selectedAnswers[currentQuestion + 1] || [];

  return (
    <div className="min-h-screen bg-neutral-50 flex">
      {/* Левая часть - 75% */}
      <div className="w-3/4 p-8">
        <div className="bg-white border-2 border-neutral-200 p-8 min-h-full">
          {/* Вопрос */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-neutral-900 mb-6">
              Вопрос {currentQuestion + 1}. {currentQuestionData.question}
            </h2>
            
            {/* Варианты ответов */}
            <div className="space-y-4">
              {currentQuestionData.options.map((option) => {
                const isSelected = currentSelected.includes(option.id);
                const isAnswered = answers[currentQuestion + 1] === option.id;
                
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
                    onClick={() => handleAnswerClick(currentQuestion + 1, option.id, false)}
                    onContextMenu={(e) => handleRightClick(e, currentQuestion + 1, option.id)}
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
              onClick={saveProgress}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-yellow-600 text-white font-medium hover:bg-yellow-700 transition-colors duration-200"
            >
              <Save className="w-4 h-4" />
              Закончить позже
            </button>
            
            <button
              onClick={submitTest}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white font-medium hover:bg-green-700 transition-colors duration-200"
            >
              <Send className="w-4 h-4" />
              Отправить на проверку
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
        </div>
      </div>
    </div>
  );
};

export default ActiveTestPage;