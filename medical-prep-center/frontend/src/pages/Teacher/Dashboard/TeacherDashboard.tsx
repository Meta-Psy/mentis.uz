import React from 'react';
import { 
  ChevronDown, 
  ChevronUp, 
  User, 
  Clock, 
  Users, 
  TrendingUp,
  MessageSquare,
  Save,
  BarChart3,
  AlertCircle,
} from 'lucide-react';
import { useTeacherPage } from '../../../hooks/useTeachers';
import { teacherAPI, COMMENT_TYPES } from '../../../services/api/teacher_dashboard';
import type { CommentType, CriterionAnalysis } from '../../../services/api/teacher_dashboard';

// Константы для критериев
const CRITERION_NAMES = [
  'Критерий 1',
  'Критерий 2', 
  'Критерий 3',
  'Критерий 4',
  'Критерий 5',
  'Критерий 6',
  'Критерий 7',
  'Критерий 8'
];

const CRITERION_COLORS = [
  '#3e588b', '#22c55e', '#f59e0b', '#ef4444',
  '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
];

interface TeacherDashboardProps {
  teacherId: number;
}

const TeacherDashboard: React.FC<TeacherDashboardProps> = ({ teacherId }) => {
  const {
    // Данные
    teacherProfile,
    groups,
    selectedGroup,
    students,
    expandedStudents,
    
    // Комментарии
    comments,
    commentTypes,
    savingComments,
    saveErrors,
    
    // Аналитика
    analytics,
    loadingAnalytics,
    analyticsErrors,
    
    // Состояние
    isLoading,
    hasError,
    
    // Обработчики
    handleGroupSelect,
    handleToggleStudent,
    handleCommentChange,
    handleCommentTypeChange,
    handleSaveComment,
    loadStudentAnalytics,
    handleRefresh
  } = useTeacherPage(teacherId);

  // Компонент круговой диаграммы для критериев
  const CriterionChart: React.FC<{ 
    analysis: CriterionAnalysis[]; 
    title: string;
    type: 'pie' | 'bar';
  }> = ({ analysis, title, type }) => {
    if (type === 'bar') {
      return (
        <div className="text-center">
          <h5 className="font-semibold text-neutral-900 mb-3 text-sm">{title}</h5>
          <div className="space-y-2">
            {analysis.slice(0, 8).map((criterion, index) => {
              const accuracy = criterion.accuracy_percentage;
              const color = CRITERION_COLORS[index];
              
              return (
                <div key={criterion.criterion_number} className="flex items-center gap-2">
                  <div className="w-16 text-xs text-neutral-600 text-left">
                    {CRITERION_NAMES[index]}
                  </div>
                  <div className="flex-1 bg-neutral-200 rounded-full h-3 relative overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-300"
                      style={{ 
                        width: `${Math.max(accuracy, 2)}%`,
                        backgroundColor: color
                      }}
                    />
                  </div>
                  <div className="w-12 text-xs font-medium text-neutral-700 text-right">
                    {accuracy.toFixed(0)}%
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      );
    }

    // Круговая диаграмма (упрощенная версия для общих показателей)
    const totalCorrect = analysis.reduce((sum, c) => sum + c.correct_count, 0);
    const totalIncorrect = analysis.reduce((sum, c) => sum + c.incorrect_count, 0);
    const total = totalCorrect + totalIncorrect;
    
    if (total === 0) {
      return (
        <div className="text-center">
          <h5 className="font-semibold text-neutral-900 mb-2 text-sm">{title}</h5>
          <div className="w-24 h-24 mx-auto mb-2 bg-neutral-100 rounded-full flex items-center justify-center">
            <span className="text-xs text-neutral-500">Нет данных</span>
          </div>
        </div>
      );
    }

    const correctPercentage = (totalCorrect / total) * 100;
    const incorrectPercentage = (totalIncorrect / total) * 100;

    return (
      <div className="text-center">
        <h5 className="font-semibold text-neutral-900 mb-2 text-sm">{title}</h5>
        <div className="relative w-24 h-24 mx-auto mb-2">
          <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="#ef4444"
              strokeWidth="20"
              strokeDasharray={`${incorrectPercentage * 2.51} ${(100 - incorrectPercentage) * 2.51}`}
            />
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="#22c55e"
              strokeWidth="20"
              strokeDasharray={`${correctPercentage * 2.51} ${(100 - correctPercentage) * 2.51}`}
              strokeDashoffset={`${-incorrectPercentage * 2.51}`}
            />
          </svg>
        </div>
        <div className="space-y-1">
          <div className="flex items-center justify-center gap-2 text-xs">
            <div className="w-3 h-3 rounded bg-green-500"></div>
            <span>Правильно: {correctPercentage.toFixed(0)}%</span>
          </div>
          <div className="flex items-center justify-center gap-2 text-xs">
            <div className="w-3 h-3 rounded bg-red-500"></div>
            <span>Неправильно: {incorrectPercentage.toFixed(0)}%</span>
          </div>
        </div>
      </div>
    );
  };

  // Компонент студента
  const StudentCard: React.FC<{ student: any }> = ({ student }) => {
    const isExpanded = expandedStudents[student.id];
    const studentAnalytics = analytics[student.id];
    const isLoadingAnalytics = loadingAnalytics[student.id];
    const analyticsError = analyticsErrors[student.id];
    
    // Загружаем аналитику при разворачивании
    React.useEffect(() => {
      if (isExpanded && !studentAnalytics && !isLoadingAnalytics) {
        loadStudentAnalytics(student.id);
      }
    }, [isExpanded, student.id, studentAnalytics, isLoadingAnalytics]);
    
    return (
      <div className="bg-white border-2 border-neutral-200 mb-4">
        {/* Основная информация */}
        <div 
          className="p-4 lg:p-6 cursor-pointer hover:bg-neutral-50 transition-colors duration-200"
          onClick={() => handleToggleStudent(student.id)}
        >
          <div className="grid grid-cols-1 lg:grid-cols-7 gap-4 items-center">
            {/* Фотография */}
            <div className="lg:col-span-1 flex justify-center lg:justify-start">
              <div className="w-12 h-12 bg-primary-100 border-2 border-primary-200 flex items-center justify-center">
                {student.photo ? (
                  <img src={student.photo} alt={student.name} className="w-full h-full object-cover rounded" />
                ) : (
                  <User className="w-6 h-6 text-primary-600" />
                )}
              </div>
            </div>
            
            {/* Ф.И.О. */}
            <div className="lg:col-span-2 text-center lg:text-left">
              <h4 className="font-semibold text-neutral-900 text-sm lg:text-base">
                {student.name}
              </h4>
              <div className="text-xs text-neutral-500 mt-1">
                {teacherAPI.formatLastSeen(student.last_seen)}
              </div>
            </div>
            
            {/* Тесты не сдано */}
            <div className="lg:col-span-1 text-center">
              <div className="text-xs text-neutral-600">Не сдано тестов</div>
              <div className={`font-bold text-sm ${
                student.test_statistics.pending_tests > 0 ? 'text-red-600' : 'text-green-600'
              }`}>
                {student.test_statistics.pending_tests}
              </div>
            </div>
            
            {/* Посещаемость */}
            <div className="lg:col-span-1 text-center">
              <div className="text-xs text-neutral-600">Посещаемость</div>
              <div className={`font-medium text-sm ${
                teacherAPI.getAttendanceColor(student.attendance_info.attendance_rate)
              }`}>
                {(student.attendance_info.attendance_rate * 100).toFixed(0)}%
              </div>
            </div>
            
            {/* Средний балл */}
            <div className="lg:col-span-1 text-center">
              <div className="text-xs text-neutral-600">Средний балл</div>
              <div className={`font-bold text-sm ${
                teacherAPI.getScoreColor(student.test_statistics.average_score)
              }`}>
                {student.test_statistics.average_score.toFixed(1)}
              </div>
            </div>
            
            {/* ДТМ балл */}
            <div className="lg:col-span-1 text-center flex items-center justify-center lg:justify-between">
              <div>
                <div className="text-xs text-neutral-600">ДТМ балл</div>
                <div className="font-bold text-sm text-green-600">
                  {student.test_statistics.dtm_score?.toFixed(1) || 'Н/Д'}
                </div>
              </div>
              {isExpanded ? (
                <ChevronUp className="w-5 h-5 text-neutral-500 ml-2" />
              ) : (
                <ChevronDown className="w-5 h-5 text-neutral-500 ml-2" />
              )}
            </div>
          </div>
        </div>

        {/* Расширенная информация */}
        {isExpanded && (
          <div className="border-t border-neutral-200 p-4 lg:p-6 bg-neutral-50">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Аналитика по критериям */}
              <div className="lg:col-span-3">
                <h5 className="font-bold text-neutral-900 mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Анализ успеваемости по критериям
                </h5>
                
                {isLoadingAnalytics && (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                    <span className="ml-2 text-neutral-600">Загрузка аналитики...</span>
                  </div>
                )}
                
                {analyticsError && (
                  <div className="flex items-center justify-center py-8 text-red-600">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    <span>{analyticsError}</span>
                  </div>
                )}
                
                {studentAnalytics && !isLoadingAnalytics && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    {/* Детальный анализ по критериям */}
                    <CriterionChart 
                      analysis={studentAnalytics.criteria_analysis}
                      title="Анализ по критериям"
                      type="bar"
                    />
                    
                    {/* Общая статистика */}
                    <CriterionChart 
                      analysis={studentAnalytics.criteria_analysis}
                      title="Общая успеваемость"
                      type="pie"
                    />
                  </div>
                )}
              </div>

              {/* Комментарии */}
              <div className="lg:col-span-1">
                <h5 className="font-bold text-neutral-900 mb-4 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Комментарии
                </h5>
                <div className="space-y-3">
                  {/* Тип комментария */}
                  <div>
                    <label className="block text-xs font-medium text-neutral-700 mb-2">
                      Тип комментария
                    </label>
                    <select
                      value={commentTypes[student.id] || COMMENT_TYPES.NEUTRAL}
                      onChange={(e) => handleCommentTypeChange(student.id, e.target.value as CommentType)}
                      className="w-full p-2 border border-neutral-300 text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                    >
                      <option value={COMMENT_TYPES.POSITIVE}>Положительный</option>
                      <option value={COMMENT_TYPES.NEUTRAL}>Нейтральный</option>
                      <option value={COMMENT_TYPES.NEGATIVE}>Отрицательный</option>
                    </select>
                  </div>
                  
                  {/* Текст комментария */}
                  <textarea
                    value={comments[student.id] || ''}
                    onChange={(e) => handleCommentChange(student.id, e.target.value)}
                    placeholder="Добавьте комментарий об ученике..."
                    className="w-full p-3 border border-neutral-300 text-sm resize-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                    rows={4}
                  />
                  
                  {/* Ошибка сохранения */}
                  {saveErrors[student.id] && (
                    <div className="text-red-600 text-xs flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {saveErrors[student.id]}
                    </div>
                  )}
                  
                  {/* Кнопка сохранения */}
                  <button
                    onClick={() => handleSaveComment(student.id)}
                    disabled={savingComments[student.id] || !comments[student.id]?.trim()}
                    className={`w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium transition-colors duration-200 ${
                      savingComments[student.id]
                        ? 'bg-neutral-400 text-white cursor-not-allowed'
                        : 'bg-primary-600 text-white hover:bg-primary-700'
                    }`}
                  >
                    {savingComments[student.id] ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Сохранение...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        Сохранить
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-neutral-600">Загрузка данных преподавателя...</p>
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-neutral-900 mb-2">Ошибка загрузки</h2>
          <p className="text-neutral-600 mb-4">{hasError}</p>
          <button
            onClick={handleRefresh}
            className="px-6 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  if (!teacherProfile) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <User className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-neutral-900 mb-2">Преподаватель не найден</h2>
          <p className="text-neutral-600">Проверьте правильность ID преподавателя</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 p-4 lg:p-8">
      <div className="container mx-auto">
        {/* Заголовок */}
        <div className="mb-6 lg:mb-8">
          <h1 className="text-2xl lg:text-3xl font-bold text-primary-900 mb-2">
            Профиль учителя
          </h1>
          <p className="text-neutral-600 text-sm lg:text-base">
            {teacherProfile.name} • {teacherProfile.subjects.join(', ')}
          </p>
        </div>

        {/* Расписание групп */}
        <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6 mb-6 lg:mb-8">
          <h2 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6 flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Расписание групп
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-primary-600 text-white">
                <tr>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    Группа
                  </th>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    День 1
                  </th>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    День 2
                  </th>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    День 3
                  </th>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    Время
                  </th>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    Учеников
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {groups.map((group) => (
                  <tr key={group.group_id} className="hover:bg-neutral-50">
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center">
                      <span className="px-3 py-1 bg-primary-100 text-primary-700 font-bold text-sm">
                        {group.group_id}
                      </span>
                    </td>
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center font-medium text-sm lg:text-base">
                      {group.days[0] || '-'}
                    </td>
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center font-medium text-sm lg:text-base">
                      {group.days[1] || '-'}
                    </td>
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center font-medium text-sm lg:text-base">
                      {group.days[2] || '-'}
                    </td>
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center font-medium text-sm lg:text-base">
                      {group.start_time}
                    </td>
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center">
                      <div className="flex items-center justify-center gap-1">
                        <Users className="w-4 h-4 text-neutral-500" />
                        <span className="font-medium text-sm lg:text-base">{group.student_count}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Кнопки групп */}
        <div className="flex flex-wrap justify-center gap-2 lg:gap-4 mb-6 lg:mb-8">
          {groups.map((group) => (
            <button
              key={group.group_id}
              onClick={() => handleGroupSelect(selectedGroup === group.group_id ? null : group.group_id)}
              className={`flex items-center gap-2 px-4 lg:px-6 py-3 font-medium transition-all duration-200 text-sm lg:text-base ${
                selectedGroup === group.group_id
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
              }`}
            >
              <Users className="w-4 h-4" />
              Группа {group.group_id}
              <span className={`px-2 py-1 text-xs font-bold rounded ${
                selectedGroup === group.group_id 
                  ? 'bg-white/20 text-white' 
                  : 'bg-primary-100 text-primary-700'
              }`}>
                {group.student_count}
              </span>
            </button>
          ))}
        </div>

        {/* Список студентов */}
        {selectedGroup && (
          <div>
            <div className="flex items-center justify-between mb-4 lg:mb-6">
              <h3 className="text-lg lg:text-xl font-bold text-neutral-900">
                Студенты группы {selectedGroup}
              </h3>
              <button
                onClick={handleRefresh}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-neutral-100 text-neutral-700 hover:bg-neutral-200 transition-colors duration-200"
              >
                <TrendingUp className="w-4 h-4" />
                Обновить
              </button>
            </div>
            
            <div className="space-y-4">
              {students.length > 0 ? (
                students
                  .sort((a, b) => b.test_statistics.average_score - a.test_statistics.average_score)
                  .map((student) => (
                    <StudentCard key={student.id} student={student} />
                  ))
              ) : (
                <div className="text-center py-12 bg-white border-2 border-neutral-200">
                  <Users className="w-16 h-16 text-neutral-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-neutral-700 mb-2">
                    Студенты не найдены
                  </h3>
                  <p className="text-neutral-500">
                    В данной группе пока нет студентов
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {!selectedGroup && (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-neutral-700 mb-2">
              Выберите группу
            </h3>
            <p className="text-neutral-500">
              Нажмите на кнопку группы, чтобы просмотреть список студентов
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherDashboard;