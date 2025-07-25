import React, { useState } from 'react';
import { 
  User,
  TrendingUp,
  MessageSquare,
  BookOpen,
  Calendar,
  Award,
  Target,
  Edit3,
  X,
  Check,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { useStudentDashboard } from '../../../hooks/useStudents';

// Получаем ID студента из контекста или props
// В реальном приложении это может быть из роутера или контекста аутентификации
const CURRENT_STUDENT_ID = 1; // Заглушка

const StudentDashboard = () => {
  const {
    // Состояние страницы
    activeTab,
    setActiveTab,
    isEditing,
    toggleEditing,
    
    // Данные
    profile,
    tests,
    attendance,
    comments,
    analytics,
    
    // Статистика
    testStatistics,
    attendanceStatistics,
    commentStatistics,
    
    // Состояние загрузки
    isLoading,
    hasError,
    
    // Действия
    saveChanges,
    refreshAllData,
    // Фильтры
    filters,
    updateFilter,
    filterTests,
    filterComments
  } = useStudentDashboard(CURRENT_STUDENT_ID);

  // Локальное состояние для редактирования
  const [editForm, setEditForm] = useState({
    goal: '',
    hobby: '',
    address: ''
  });

  // Инициализация формы при входе в режим редактирования
  React.useEffect(() => {
    if (isEditing && profile) {
      setEditForm({
        goal: profile.student_info.goal || '',
        hobby: profile.student_info.hobby || '',
        address: profile.student_info.address || ''
      });
    }
  }, [isEditing, profile]);

  // Обработка сохранения
  const handleSave = async () => {
    const success = await saveChanges(editForm);
    if (success) {
      console.log('Данные успешно сохранены');
    }
  };

  // Обработка отмены
  const handleCancel = () => {
    toggleEditing();
    if (profile) {
      setEditForm({
        goal: profile.student_info.goal || '',
        hobby: profile.student_info.hobby || '',
        address: profile.student_info.address || ''
      });
    }
  };

  // Компонент круговой диаграммы
  const CircularChart = ({ data, title, colors }: {
    data: { [key: string]: number };
    title: string;
    colors: string[];
  }) => {
    const values = Object.values(data);
    const total = values.reduce((sum, val) => sum + val, 0);
    
    if (total === 0) {
      return (
        <div className="text-center">
          <h5 className="font-semibold text-neutral-900 mb-2 text-sm">{title}</h5>
          <div className="w-24 h-24 mx-auto mb-2 bg-neutral-200 rounded-full flex items-center justify-center">
            <span className="text-neutral-500 text-xs">Нет данных</span>
          </div>
        </div>
      );
    }
    
    let currentAngle = 0;
    const segments = values.map((value, index) => {
      const angle = (value / total) * 360;
      const startAngle = currentAngle;
      currentAngle += angle;
      
      const x1 = 50 + 40 * Math.cos((startAngle * Math.PI) / 180);
      const y1 = 50 + 40 * Math.sin((startAngle * Math.PI) / 180);
      const x2 = 50 + 40 * Math.cos((currentAngle * Math.PI) / 180);
      const y2 = 50 + 40 * Math.sin((currentAngle * Math.PI) / 180);
      
      const largeArcFlag = angle > 180 ? 1 : 0;
      
      return {
        path: `M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`,
        color: colors[index % colors.length],
        percentage: Math.round((value / total) * 100)
      };
    });

    return (
      <div className="text-center">
        <h5 className="font-semibold text-neutral-900 mb-2 text-sm">{title}</h5>
        <div className="relative w-24 h-24 mx-auto mb-2">
          <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
            {segments.map((segment, index) => (
              <path
                key={index}
                d={segment.path}
                fill={segment.color}
                stroke="white"
                strokeWidth="1"
              />
            ))}
          </svg>
        </div>
        <div className="space-y-1">
          {segments.map((segment, index) => (
            <div key={index} className="flex items-center justify-center gap-2 text-xs">
              <div 
                className="w-3 h-3 rounded" 
                style={{ backgroundColor: segment.color }}
              ></div>
              <span>{segment.percentage}%</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Если данные загружаются
  if (isLoading && !profile) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-neutral-600">Загрузка профиля...</p>
        </div>
      </div>
    );
  }

  // Если произошла ошибка
  if (hasError && !profile) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-neutral-900 mb-2">Ошибка загрузки</h2>
          <p className="text-neutral-600 mb-4">{hasError}</p>
          <button 
            onClick={refreshAllData}
            className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  // Если профиль не найден
  if (!profile) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <User className="w-16 h-16 text-neutral-400 mx-auto mb-4" />
          <h2 className="text-xl font-medium text-neutral-700">Профиль не найден</h2>
        </div>
      </div>
    );
  }

  const studentInfo = profile.student_info;
  const statistics = profile.statistics;

  return (
    <div className="min-h-screen bg-neutral-50 p-4 lg:p-8">
      <div className="container mx-auto">
        {/* Заголовок с действиями */}
        <div className="flex justify-between items-start mb-6 lg:mb-8">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-primary-900 mb-2">
              Профиль студента
            </h1>
            <p className="text-neutral-600 text-sm lg:text-base">
              {studentInfo.name} {studentInfo.surname}
              {studentInfo.group_id && ` • Группа ${studentInfo.group_id}`}
            </p>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={refreshAllData}
              disabled={isLoading}
              className="p-2 text-neutral-600 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors disabled:opacity-50"
              title="Обновить данные"
            >
              <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            
            {!isEditing ? (
              <button
                onClick={toggleEditing}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
              >
                <Edit3 className="w-4 h-4" />
                Редактировать
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={handleCancel}
                  className="flex items-center gap-2 px-4 py-2 bg-neutral-500 text-white rounded hover:bg-neutral-600 transition-colors"
                >
                  <X className="w-4 h-4" />
                  Отмена
                </button>
                <button
                  onClick={handleSave}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                >
                  <Check className="w-4 h-4" />
                  Сохранить
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Основная информация */}
        <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6 mb-6 lg:mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 lg:gap-6">
            {/* Фотография */}
            <div className="flex justify-center">
              <div className="w-24 h-24 lg:w-32 lg:h-32 bg-primary-100 border-2 border-primary-200 flex items-center justify-center">
                {studentInfo.photo ? (
                  <img 
                    src={studentInfo.photo} 
                    alt="Фото студента" 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <User className="w-12 h-12 lg:w-16 lg:h-16 text-primary-600" />
                )}
              </div>
            </div>
            
            {/* Основная информация */}
            <div className="lg:col-span-2 space-y-4">
              <div>
                <h3 className="font-bold text-lg lg:text-xl text-neutral-900 mb-2">
                  {studentInfo.name} {studentInfo.surname}
                </h3>
                <div className="space-y-1 text-sm text-neutral-600">
                  {studentInfo.phone && <p>Телефон: {studentInfo.phone}</p>}
                  {studentInfo.email && <p>Email: {studentInfo.email}</p>}
                  {studentInfo.direction && <p>Направление: {studentInfo.direction}</p>}
                  {studentInfo.birthday && <p>Дата рождения: {new Date(studentInfo.birthday).toLocaleDateString('ru-RU')}</p>}
                </div>
              </div>
              
              {/* Цель */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  <Target className="w-4 h-4 inline mr-1" />
                  Цель
                </label>
                {isEditing ? (
                  <textarea
                    value={editForm.goal}
                    onChange={(e) => setEditForm(prev => ({ ...prev, goal: e.target.value }))}
                    placeholder="Опишите свою цель..."
                    className="w-full p-3 border border-neutral-300 rounded text-sm resize-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                    rows={3}
                  />
                ) : (
                  <p className="text-sm text-neutral-700 bg-neutral-50 p-3 rounded">
                    {studentInfo.goal || 'Цель не указана'}
                  </p>
                )}
              </div>
            </div>
            
            {/* Статистика */}
            <div className="space-y-4">
              <div className="bg-primary-50 p-4 rounded">
                <h4 className="font-semibold text-primary-900 mb-3">Статистика</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Тестов сдано:</span>
                    <span className="font-medium">{statistics.total_tests_completed}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Средний балл:</span>
                    <span className="font-medium text-primary-600">
                      {statistics.average_score.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Посещаемость:</span>
                    <span className={`font-medium ${statistics.attendance_rate >= 80 ? 'text-green-600' : statistics.attendance_rate >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {statistics.attendance_rate.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Прогресс:</span>
                    <span className="font-medium text-blue-600">
                      {statistics.progress_percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Дополнительная информация в режиме редактирования */}
          {isEditing && (
            <div className="mt-6 pt-6 border-t border-neutral-200">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Хобби
                  </label>
                  <input
                    type="text"
                    value={editForm.hobby}
                    onChange={(e) => setEditForm(prev => ({ ...prev, hobby: e.target.value }))}
                    placeholder="Ваши увлечения..."
                    className="w-full p-3 border border-neutral-300 rounded text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Адрес
                  </label>
                  <input
                    type="text"
                    value={editForm.address}
                    onChange={(e) => setEditForm(prev => ({ ...prev, address: e.target.value }))}
                    placeholder="Ваш адрес..."
                    className="w-full p-3 border border-neutral-300 rounded text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Навигационные табы */}
        <div className="bg-white border-2 border-neutral-200 mb-6">
          <div className="flex overflow-x-auto">
            {[
              { id: 'overview', label: 'Обзор', icon: TrendingUp },
              { id: 'tests', label: 'Тесты', icon: BookOpen },
              { id: 'attendance', label: 'Посещаемость', icon: Calendar },
              { id: 'comments', label: 'Комментарии', icon: MessageSquare },
              { id: 'universities', label: 'Университеты', icon: Award }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`flex items-center gap-2 px-4 lg:px-6 py-3 lg:py-4 font-medium whitespace-nowrap transition-colors border-b-2 ${
                  activeTab === id
                    ? 'border-primary-600 text-primary-600 bg-primary-50'
                    : 'border-transparent text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Содержимое табов */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Аналитика успеваемости */}
            {analytics && (
              <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6">
                <h3 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
                  Аналитика успеваемости
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                  <CircularChart 
                    data={analytics.objects}
                    title="Objects"
                    colors={['#3e588b', '#96aedd']}
                  />
                  <CircularChart 
                    data={analytics.motions}
                    title="Motions"
                    colors={['#22c55e', '#f59e0b', '#ef4444']}
                  />
                  <CircularChart 
                    data={analytics.skills}
                    title="Skills"
                    colors={['#8b5cf6', '#06b6d4', '#84cc16']}
                  />
                </div>
              </div>
            )}

            {/* Последние тесты */}
            <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-neutral-900">Последние тесты</h3>
                <button
                  onClick={() => setActiveTab('tests')}
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                  Посмотреть все
                </button>
              </div>
              
              {profile.recent_tests.length > 0 ? (
                <div className="space-y-3">
                  {profile.recent_tests.slice(0, 5).map((test) => (
                    <div key={test.test_id} className="flex items-center justify-between p-3 bg-neutral-50 rounded">
                      <div>
                        <h4 className="font-medium text-neutral-900">{test.topic_name}</h4>
                        <p className="text-sm text-neutral-600">{test.subject_name}</p>
                      </div>
                      <div className="text-right">
                        <div className={`font-bold ${test.score_percentage >= 80 ? 'text-green-600' : test.score_percentage >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                          {test.score_percentage.toFixed(1)}%
                        </div>
                        <div className="text-xs text-neutral-500">
                          {new Date(test.attempt_date).toLocaleDateString('ru-RU')}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-neutral-500 text-center py-8">Тестов пока нет</p>
              )}
            </div>

            {/* Последние комментарии */}
            <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-neutral-900">Последние комментарии</h3>
                <button
                  onClick={() => setActiveTab('comments')}
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                  Посмотреть все
                </button>
              </div>
              
              {profile.recent_comments.length > 0 ? (
                <div className="space-y-3">
                  {profile.recent_comments.slice(0, 3).map((comment) => (
                    <div key={comment.comment_id} className="p-3 bg-neutral-50 rounded">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-sm text-neutral-900">
                          {comment.teacher_name}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded ${
                          comment.comment_type === 'positive' ? 'bg-green-100 text-green-700' :
                          comment.comment_type === 'negative' ? 'bg-red-100 text-red-700' :
                          'bg-neutral-100 text-neutral-700'
                        }`}>
                          {comment.comment_type === 'positive' ? 'Положительный' :
                           comment.comment_type === 'negative' ? 'Отрицательный' : 'Нейтральный'}
                        </span>
                      </div>
                      <p className="text-sm text-neutral-700">{comment.comment_text}</p>
                      <p className="text-xs text-neutral-500 mt-2">
                        {new Date(comment.comment_date).toLocaleDateString('ru-RU')}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-neutral-500 text-center py-8">Комментариев пока нет</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'tests' && (
          <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-neutral-900">Результаты тестов</h3>
              <div className="flex gap-2">
                <select
                  value={filters.subject}
                  onChange={(e) => updateFilter('subject', e.target.value)}
                  className="px-3 py-2 border border-neutral-300 rounded text-sm"
                >
                  <option value="all">Все предметы</option>
                  <option value="chemistry">Химия</option>
                  <option value="biology">Биология</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded">
                <div className="text-2xl font-bold text-blue-600">{testStatistics.total_count}</div>
                <div className="text-sm text-blue-700">Всего тестов</div>
              </div>
              <div className="bg-green-50 p-4 rounded">
                <div className="text-2xl font-bold text-green-600">{testStatistics.passed_count}</div>
                <div className="text-sm text-green-700">Сдано</div>
              </div>
              <div className="bg-red-50 p-4 rounded">
                <div className="text-2xl font-bold text-red-600">{testStatistics.failed_count}</div>
                <div className="text-sm text-red-700">Не сдано</div>
              </div>
              <div className="bg-purple-50 p-4 rounded">
                <div className="text-2xl font-bold text-purple-600">{testStatistics.average_score.toFixed(1)}%</div>
                <div className="text-sm text-purple-700">Средний балл</div>
              </div>
            </div>

            {filterTests(tests).length > 0 ? (
              <div className="space-y-3">
                {filterTests(tests).map((test) => (
                  <div key={test.test_id} className="p-4 border border-neutral-200 rounded">
                    <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 items-center">
                      <div className="lg:col-span-2">
                        <h4 className="font-medium text-neutral-900">{test.topic_name}</h4>
                        <p className="text-sm text-neutral-600">{test.subject_name}</p>
                      </div>
                      <div className="text-center">
                        <div className={`text-lg font-bold ${test.score_percentage >= 80 ? 'text-green-600' : test.score_percentage >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                          {test.score_percentage.toFixed(1)}%
                        </div>
                        <div className="text-xs text-neutral-500">
                          {test.correct_answers}/{test.total_questions}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-neutral-700">
                          {new Date(test.attempt_date).toLocaleDateString('ru-RU')}
                        </div>
                        {test.time_spent && (
                          <div className="text-xs text-neutral-500">{test.time_spent}</div>
                        )}
                      </div>
                      <div className="text-center">
                        <span className={`px-3 py-1 rounded text-sm font-medium ${
                          test.passed ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }`}>
                          {test.passed ? 'Сдан' : 'Не сдан'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-neutral-500 text-center py-8">Тестов не найдено</p>
            )}
          </div>
        )}

        {activeTab === 'attendance' && (
          <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6">
            <h3 className="text-lg font-bold text-neutral-900 mb-4">Посещаемость</h3>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
              <div className="bg-green-50 p-4 rounded">
                <div className="text-2xl font-bold text-green-600">{attendanceStatistics.present_count}</div>
                <div className="text-sm text-green-700">Присутствовал</div>
              </div>
              <div className="bg-red-50 p-4 rounded">
                <div className="text-2xl font-bold text-red-600">{attendanceStatistics.absent_count}</div>
                <div className="text-sm text-red-700">Отсутствовал</div>
              </div>
              <div className="bg-yellow-50 p-4 rounded">
                <div className="text-2xl font-bold text-yellow-600">{attendanceStatistics.late_count}</div>
                <div className="text-sm text-yellow-700">Опоздал</div>
              </div>
              <div className="bg-blue-50 p-4 rounded">
                <div className="text-2xl font-bold text-blue-600">{attendanceStatistics.attendance_rate.toFixed(1)}%</div>
                <div className="text-sm text-blue-700">Посещаемость</div>
              </div>
            </div>

            {attendance.length > 0 ? (
              <div className="space-y-3">
                {attendance.slice(0, 10).map((record) => (
                  <div key={record.attendance_id} className="p-4 border border-neutral-200 rounded">
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 items-center">
                      <div>
                        <h4 className="font-medium text-neutral-900">
                          {record.topic_name || 'Занятие'}
                        </h4>
                        <p className="text-sm text-neutral-600">{record.subject_name}</p>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-neutral-700">
                          {new Date(record.lesson_date_time).toLocaleDateString('ru-RU')}
                        </div>
                        <div className="text-xs text-neutral-500">
                          {new Date(record.lesson_date_time).toLocaleTimeString('ru-RU', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </div>
                      </div>
                      <div className="text-center">
                        <span className={`px-3 py-1 rounded text-sm font-medium ${
                          record.att_status === 'present' ? 'bg-green-100 text-green-700' :
                          record.att_status === 'absent' ? 'bg-red-100 text-red-700' :
                          'bg-yellow-100 text-yellow-700'
                        }`}>
                          {record.att_status === 'present' ? 'Присутствовал' :
                           record.att_status === 'absent' ? 'Отсутствовал' : 'Опоздал'}
                        </span>
                      </div>
                      <div className="text-center">
                        {record.excuse_reason && (
                          <p className="text-xs text-blue-600">Уважительная причина</p>
                        )}
                        {record.extra_lesson && (
                          <p className="text-xs text-orange-600">Доп. занятие</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-neutral-500 text-center py-8">Записей о посещаемости нет</p>
            )}
          </div>
        )}

        {activeTab === 'comments' && (
          <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-neutral-900">Комментарии учителей</h3>
              <select
                value={filters.commentType}
                onChange={(e) => updateFilter('commentType', e.target.value)}
                className="px-3 py-2 border border-neutral-300 rounded text-sm"
              >
                <option value="all">Все комментарии</option>
                <option value="positive">Положительные</option>
                <option value="negative">Отрицательные</option>
                <option value="neutral">Нейтральные</option>
              </select>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded">
                <div className="text-2xl font-bold text-gray-600">{commentStatistics.total_count}</div>
                <div className="text-sm text-gray-700">Всего</div>
              </div>
              <div className="bg-green-50 p-4 rounded">
                <div className="text-2xl font-bold text-green-600">{commentStatistics.positive_count}</div>
                <div className="text-sm text-green-700">Положительные</div>
              </div>
              <div className="bg-red-50 p-4 rounded">
                <div className="text-2xl font-bold text-red-600">{commentStatistics.negative_count}</div>
                <div className="text-sm text-red-700">Отрицательные</div>
              </div>
              <div className="bg-blue-50 p-4 rounded">
                <div className="text-2xl font-bold text-blue-600">{commentStatistics.neutral_count}</div>
                <div className="text-sm text-blue-700">Нейтральные</div>
              </div>
            </div>

            {filterComments(comments).length > 0 ? (
              <div className="space-y-4">
                {filterComments(comments).map((comment) => (
                  <div key={comment.comment_id} className={`p-4 border-l-4 ${
                    comment.comment_type === 'positive' ? 'border-green-400 bg-green-50' :
                    comment.comment_type === 'negative' ? 'border-red-400 bg-red-50' :
                    'border-blue-400 bg-blue-50'
                  }`}>
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-neutral-900">{comment.teacher_name}</h4>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 text-xs rounded ${
                          comment.comment_type === 'positive' ? 'bg-green-100 text-green-700' :
                          comment.comment_type === 'negative' ? 'bg-red-100 text-red-700' :
                          'bg-blue-100 text-blue-700'
                        }`}>
                          {comment.comment_type === 'positive' ? 'Положительный' :
                           comment.comment_type === 'negative' ? 'Отрицательный' : 'Нейтральный'}
                        </span>
                        <span className="text-xs text-neutral-500">
                          {new Date(comment.comment_date).toLocaleDateString('ru-RU')}
                        </span>
                      </div>
                    </div>
                    <p className="text-neutral-700">{comment.comment_text}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-neutral-500 text-center py-8">Комментариев не найдено</p>
            )}
          </div>
        )}

        {activeTab === 'universities' && (
          <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6">
            <h3 className="text-lg font-bold text-neutral-900 mb-4">Выбранные университеты</h3>
            
            {profile.universities.length > 0 ? (
              <div className="space-y-4">
                {profile.universities
                  .sort((a, b) => (a.priority_order || 999) - (b.priority_order || 999))
                  .map((university) => (
                  <div key={university.university_id} className="p-4 border border-neutral-200 rounded">
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 items-start">
                      <div className="lg:col-span-2">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="bg-primary-100 text-primary-700 px-2 py-1 rounded text-sm font-medium">
                            #{university.priority_order}
                          </span>
                          <h4 className="font-medium text-neutral-900">{university.name}</h4>
                        </div>
                        <p className="text-sm text-neutral-600 mb-1">{university.location}</p>
                        <p className="text-sm text-neutral-500">
                          Тип: {university.type === 'state' ? 'Государственный' : 'Частный'}
                        </p>
                      </div>
                      <div className="text-center">
                        {university.entrance_score && (
                          <>
                            <div className="text-lg font-bold text-primary-600">
                              {university.entrance_score}
                            </div>
                            <div className="text-xs text-neutral-500">Проходной балл</div>
                          </>
                        )}
                      </div>
                      <div className="text-right">
                        {university.website_url && (
                          <a
                            href={university.website_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary-600 hover:text-primary-700 text-sm"
                          >
                            Сайт университета
                          </a>
                        )}
                        {university.contact_phone && (
                          <p className="text-sm text-neutral-600 mt-1">
                            {university.contact_phone}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Award className="w-16 h-16 text-neutral-400 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-neutral-700 mb-2">
                  Университеты не выбраны
                </h4>
                <p className="text-neutral-500">
                  Выберите университеты, в которые планируете поступать
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentDashboard;