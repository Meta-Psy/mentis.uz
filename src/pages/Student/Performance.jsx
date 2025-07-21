import React from 'react';
import { User, BookOpen, Clock, Target, TrendingUp, Calendar, Award, AlertCircle, CheckCircle } from 'lucide-react';

const StudentDashboard = () => {
  // Моковые данные студента
  const studentData = {
    name: 'Анна Иванова',
    group: 'Группа 2',
    subjects: ['Химия', 'Биология'],
    averageScore: 8.4,
    attendance: 95,
    completedTests: 247,
    upcomingTests: 3
  };

  // Последние результаты тестов
  const recentTests = [
    { subject: 'Химия', topic: 'Органические соединения', score: 92, date: '2 часа назад', status: 'completed' },
    { subject: 'Биология', topic: 'Анатомия человека', score: 85, date: '1 день назад', status: 'completed' },
    { subject: 'Химия', topic: 'Неорганическая химия', score: 78, date: '2 дня назад', status: 'completed' }
  ];

  // Предстоящие задания
  const upcomingTasks = [
    { type: 'test', subject: 'Биология', topic: 'Генетика', deadline: '2 дня', priority: 'high' },
    { type: 'homework', subject: 'Химия', topic: 'Решение задач', deadline: '4 дня', priority: 'medium' },
    { type: 'test', subject: 'Биология', topic: 'Экология', deadline: '1 неделя', priority: 'low' }
  ];

  // Прогресс по модулям
  const moduleProgress = [
    { subject: 'Химия', module: 'Модуль 3', progress: 75, topics: 12, completed: 9 },
    { subject: 'Биология', module: 'Модуль 2', progress: 90, topics: 10, completed: 9 }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-lg border-b border-gray-200">
        <div className="container py-6">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-gradient-to-br from-green-100 to-blue-100 rounded-2xl flex items-center justify-center">
              <User className="h-8 w-8 text-gray-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{studentData.name}</h1>
              <p className="text-gray-600">{studentData.group} • {studentData.subjects.join(', ')}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="container py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Quick Stats */}
            <div className="grid md:grid-cols-4 gap-6">
              <div className="card card-padding text-center">
                <div className="w-12 h-12 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <div className="text-2xl font-bold text-gray-900">{studentData.averageScore}</div>
                <div className="text-sm text-gray-600">Средний балл</div>
              </div>

              <div className="card card-padding text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                  <Calendar className="h-6 w-6 text-blue-600" />
                </div>
                <div className="text-2xl font-bold text-gray-900">{studentData.attendance}%</div>
                <div className="text-sm text-gray-600">Посещаемость</div>
              </div>

              <div className="card card-padding text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                  <Award className="h-6 w-6 text-purple-600" />
                </div>
                <div className="text-2xl font-bold text-gray-900">{studentData.completedTests}</div>
                <div className="text-sm text-gray-600">Решено тестов</div>
              </div>

              <div className="card card-padding text-center">
                <div className="w-12 h-12 bg-orange-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                  <Clock className="h-6 w-6 text-orange-600" />
                </div>
                <div className="text-2xl font-bold text-gray-900">{studentData.upcomingTests}</div>
                <div className="text-sm text-gray-600">Предстоящие тесты</div>
              </div>
            </div>

            {/* Recent Test Results */}
            <div className="card card-padding">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Последние результаты тестов</h3>
              
              <div className="space-y-4">
                {recentTests.map((test, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                    <div className="flex items-center space-x-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        test.subject === 'Химия' ? 'bg-green-100' : 'bg-blue-100'
                      }`}>
                        <BookOpen className={`h-6 w-6 ${
                          test.subject === 'Химия' ? 'text-green-600' : 'text-blue-600'
                        }`} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{test.topic}</h4>
                        <p className="text-sm text-gray-600">{test.subject} • {test.date}</p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${
                        test.score >= 90 ? 'text-green-600' : 
                        test.score >= 80 ? 'text-blue-600' : 
                        test.score >= 70 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {test.score}
                      </div>
                      <div className="text-sm text-gray-500">баллов</div>
                    </div>
                  </div>
                ))}
              </div>
              
              <button className="btn-outline w-full mt-6">
                Посмотреть все результаты
              </button>
            </div>

            {/* Module Progress */}
            <div className="card card-padding">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Прогресс по модулям</h3>
              
              <div className="space-y-6">
                {moduleProgress.map((module, index) => (
                  <div key={index}>
                    <div className="flex justify-between items-center mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900">{module.subject} - {module.module}</h4>
                        <p className="text-sm text-gray-600">
                          {module.completed} из {module.topics} тем завершено
                        </p>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${
                          module.subject === 'Химия' ? 'text-green-600' : 'text-blue-600'
                        }`}>
                          {module.progress}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className={`h-3 rounded-full transition-all duration-500 ${
                          module.subject === 'Химия' ? 'bg-green-500' : 'bg-blue-500'
                        }`}
                        style={{width: `${module.progress}%`}}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Upcoming Tasks */}
            <div className="card card-padding">
              <h4 className="font-bold text-gray-900 mb-4">Предстоящие задания</h4>
              
              <div className="space-y-3">
                {upcomingTasks.map((task, index) => {
                  const priorityColors = {
                    high: 'border-red-200 bg-red-50',
                    medium: 'border-yellow-200 bg-yellow-50',
                    low: 'border-green-200 bg-green-50'
                  };
                  
                  const priorityIcons = {
                    high: <AlertCircle className="h-4 w-4 text-red-600" />,
                    medium: <Clock className="h-4 w-4 text-yellow-600" />,
                    low: <CheckCircle className="h-4 w-4 text-green-600" />
                  };
                  
                  return (
                    <div key={index} className={`p-3 border rounded-xl ${priorityColors[task.priority]}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            {priorityIcons[task.priority]}
                            <span className="text-sm font-medium text-gray-900 capitalize">
                              {task.type === 'test' ? 'Тест' : 'Домашнее задание'}
                            </span>
                          </div>
                          <h5 className="font-semibold text-gray-900 text-sm">{task.topic}</h5>
                          <p className="text-xs text-gray-600">{task.subject}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-xs font-medium text-gray-900">{task.deadline}</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              <button className="btn-primary w-full mt-4">
                Посмотреть все задания
              </button>
            </div>

            {/* Quick Actions */}
            <div className="card card-padding">
              <h4 className="font-bold text-gray-900 mb-4">Быстрые действия</h4>
              
              <div className="space-y-3">
                <button className="w-full flex items-center space-x-3 p-3 bg-green-50 hover:bg-green-100 rounded-xl transition-colors">
                  <BookOpen className="h-5 w-5 text-green-600" />
                  <span className="text-green-700 font-medium">Начать новый тест</span>
                </button>
                
                <button className="w-full flex items-center space-x-3 p-3 bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors">
                  <Calendar className="h-5 w-5 text-blue-600" />
                  <span className="text-blue-700 font-medium">Посмотреть расписание</span>
                </button>
                
                <button className="w-full flex items-center space-x-3 p-3 bg-purple-50 hover:bg-purple-100 rounded-xl transition-colors">
                  <Target className="h-5 w-5 text-purple-600" />
                  <span className="text-purple-700 font-medium">Моя статистика</span>
                </button>
              </div>
            </div>

            {/* Achievement Badge */}
            <div className="card card-padding bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-200">
              <div className="text-center">
                <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Award className="h-8 w-8 text-yellow-600" />
                </div>
                <h4 className="font-bold text-gray-900 mb-2">Отличная работа!</h4>
                <p className="text-sm text-gray-600 mb-4">
                  Вы решили 10 тестов подряд с результатом выше 85 баллов
                </p>
                <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-xs font-medium">
                  Достижение разблокировано
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;