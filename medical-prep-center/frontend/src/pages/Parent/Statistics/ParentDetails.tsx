import ParentHeader from "../../../components/Landing/Header";
import { Calendar, BookOpen, X, Award, Trophy, Loader2, RefreshCw } from 'lucide-react';
import { useParentDetails } from '../../../hooks/useAttendance';
import { SUBJECTS, ATTENDANCE_STATUSES } from '../../../services/api/attendance';
import type { AttendanceDay, PerformanceTopic } from '../../../services/api/attendance';

const ParentDetails = () => {
  // Получаем ID студента (в реальном приложении из контекста аутентификации)
  const studentId = 1; // TODO: получить из контекста пользователя
  
  const {
    selectedSubject,
    selectedModule,
    activeTab,
    studentDetails,
    attendanceCalendar,
    modulePerformance,
    finalGrades,
    isLoading,
    isValidating,
    hasError,
    handleSubjectChange,
    handleModuleChange,
    handleTabChange,
    handleRefresh,
    modules,
    currentSubjectData
  } = useParentDetails(studentId);

  // Функции для определения стилей посещаемости
  const getAttendanceStatusStyle = (status: string) => {
    switch (status) {
      case ATTENDANCE_STATUSES.PRESENT:
        return 'bg-white border-2 border-success-300 text-neutral-900 shadow-sm hover:shadow-card';
      case ATTENDANCE_STATUSES.LATE:
        return 'bg-white border-2 border-warning-400 text-neutral-900 shadow-sm hover:shadow-card';
      case ATTENDANCE_STATUSES.ABSENT:
        return 'bg-white border-2 border-error-300 text-neutral-900 shadow-sm hover:shadow-card';
      case ATTENDANCE_STATUSES.EXAM:
        return 'bg-gradient-to-br from-primary-500 to-primary-600 border-2 border-primary-600 text-white shadow-card hover:shadow-card-hover';
      case ATTENDANCE_STATUSES.HOLIDAY:
        return 'bg-neutral-200 border-2 border-neutral-300 text-neutral-500';
      case ATTENDANCE_STATUSES.FUTURE:
        return 'bg-neutral-50 border-2 border-neutral-200 text-neutral-400';
      default:
        return 'bg-neutral-50 border-2 border-neutral-200 text-neutral-400';
    }
  };

  const getAttendanceFlag = (status: string) => {
    switch (status) {
      case ATTENDANCE_STATUSES.PRESENT:
        return <div className="w-3 h-3 bg-success-500 rounded-full border border-white shadow-sm"></div>;
      case ATTENDANCE_STATUSES.LATE:
        return <div className="w-3 h-3 bg-warning-500 rounded-full border border-white shadow-sm"></div>;
      case ATTENDANCE_STATUSES.ABSENT:
        return <div className="w-3 h-3 bg-error-500 rounded-full border border-white shadow-sm"></div>;
      case ATTENDANCE_STATUSES.EXAM:
        return <Trophy className="w-4 h-4 text-white" />;
      default:
        return null;
    }
  };

  // Рендер календаря посещаемости
  const renderAttendanceCalendar = () => {
    if (!attendanceCalendar || !attendanceCalendar.months.length) {
      return (
        <div className="text-center py-12">
          <Calendar className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <p className="text-neutral-500 text-lg">Нет данных о посещаемости</p>
          <p className="text-neutral-400 text-sm mt-2">
            Данные будут доступны после начала занятий
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-8">
        {attendanceCalendar.months.map((month, monthIndex) => (
          <div key={monthIndex} className="card card-padding">
            <h4 className="text-xl font-bold text-neutral-900 mb-6 font-primary flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary-600" />
              {month.name}
            </h4>
            
            <div className="grid grid-cols-7 gap-4 max-w-4xl">
              {month.days.map((day: AttendanceDay, dayIndex: number) => (
                <div
                  key={dayIndex}
                  className={`relative p-6 rounded-xl transition-all duration-200 cursor-pointer group ${getAttendanceStatusStyle(day.status)}`}
                  title={day.lesson}
                >
                  <div className="text-center">
                    <span className="text-2xl font-bold font-primary">{day.date}</span>
                  </div>
                  
                  {day.status !== ATTENDANCE_STATUSES.FUTURE && day.status !== ATTENDANCE_STATUSES.HOLIDAY && (
                    <div className="absolute top-3 right-3">
                      {getAttendanceFlag(day.status)}
                    </div>
                  )}
                  
                  {/* Tooltip */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-neutral-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-10 pointer-events-none">
                    {day.lesson}
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-neutral-900"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Рендер таблицы успеваемости
  const renderPerformanceTable = () => {
    const currentModuleData = selectedModule === 'all' 
      ? modulePerformance 
      : modulePerformance.filter(m => m.module_id === selectedModule);

    if (!currentModuleData.length) {
      return (
        <div className="text-center py-12">
          <BookOpen className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <p className="text-neutral-500 text-lg">Нет данных об успеваемости</p>
          <p className="text-neutral-400 text-sm mt-2">
            Данные будут доступны после первых опросов
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {currentModuleData.map((module) => (
          <div key={module.module_id} className="card shadow-card">
            <div className="card-padding border-b border-neutral-200 bg-gradient-to-r from-primary-50 to-secondary-50">
              <h4 className="text-xl font-bold text-neutral-900 font-primary flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-primary-600" />
                {module.module_name}
              </h4>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-neutral-50 to-neutral-100">
                  <tr>
                    <th className="px-6 py-4 text-left font-semibold text-neutral-800 font-primary">№ темы</th>
                    <th className="px-6 py-4 text-center font-semibold text-neutral-800 font-primary">Прослушана</th>
                    <th className="px-6 py-4 text-center font-semibold text-neutral-800 font-primary">1-й опрос</th>
                    <th className="px-6 py-4 text-center font-semibold text-neutral-800 font-primary">2-й опрос</th>
                    <th className="px-6 py-4 text-center font-semibold text-neutral-800 font-primary">Ср. балл</th>
                  </tr>
                </thead>
                <tbody>
                  {module.topics.map((topic: PerformanceTopic) => (
                    <tr key={topic.topic_id} className="border-b border-neutral-200 hover:bg-gradient-to-r hover:from-primary-25 hover:to-secondary-25 transition-all duration-200">
                      <td className="px-6 py-4 font-bold text-lg text-neutral-900 font-primary">{topic.number}</td>
                      <td className="px-6 py-4 text-center">
                        {topic.listened ? (
                          <div className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-success-500 to-success-600 text-white rounded-full font-bold text-lg shadow-sm">
                            П
                          </div>
                        ) : (
                          <div className="inline-flex items-center justify-center w-10 h-10 bg-neutral-200 text-neutral-500 rounded-full shadow-sm">
                            <X className="w-5 h-5" />
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {topic.first_try !== null && topic.first_try !== undefined ? (
                          <span className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-full font-bold text-lg shadow-sm">
                            {Math.round(topic.first_try)}
                          </span>
                        ) : (
                          <X className="w-5 h-5 text-neutral-400 mx-auto" />
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {topic.second_try !== null && topic.second_try !== undefined ? (
                          <span className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-secondary-400 to-secondary-500 text-white rounded-full font-bold text-lg shadow-sm">
                            {Math.round(topic.second_try)}
                          </span>
                        ) : (
                          <X className="w-5 h-5 text-neutral-400 mx-auto" />
                        )}
                      </td>
                      <td className="px-6 py-4 text-center font-bold text-xl text-neutral-900 font-primary">
                        {topic.average.toFixed(1)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Рендер итоговых оценок
  const renderFinalGrades = () => {
    const currentGrades = finalGrades[selectedSubject];
    
    if (!currentGrades) {
      return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="card card-padding text-center shadow-card bg-gradient-to-br from-neutral-50 to-neutral-100">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="p-3 bg-neutral-400 rounded-full">
                <Award className="w-6 h-6 text-white" />
              </div>
              <span className="font-semibold text-neutral-800 text-lg">ПК (ср. балл)</span>
            </div>
            <div className="text-4xl font-bold text-neutral-400 font-primary">-</div>
          </div>
          
          <div className="card card-padding text-center shadow-card bg-gradient-to-br from-neutral-50 to-neutral-100">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="p-3 bg-neutral-400 rounded-full">
                <Award className="w-6 h-6 text-white" />
              </div>
              <span className="font-semibold text-neutral-800 text-lg">ИК (ср. балл)</span>
            </div>
            <div className="text-4xl font-bold text-neutral-400 font-primary">-</div>
          </div>
          
          <div className="card card-padding text-center shadow-card bg-gradient-to-br from-neutral-50 to-neutral-100">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="p-3 bg-neutral-400 rounded-full">
                <Trophy className="w-6 h-6 text-white" />
              </div>
              <span className="font-semibold text-neutral-800 text-lg">Итоговая оценка</span>
            </div>
            <div className="text-4xl font-bold text-neutral-400 font-primary">-</div>
          </div>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
        <div className="card card-padding text-center shadow-card hover:shadow-card-hover transition-all duration-200 bg-gradient-to-br from-primary-50 to-primary-100">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-primary-600 rounded-full">
              <Award className="w-6 h-6 text-white" />
            </div>
            <span className="font-semibold text-neutral-800 text-lg">ПК (ср. балл)</span>
          </div>
          <div className="text-4xl font-bold text-primary-600 font-primary">
            {currentGrades.current_average.toFixed(1)}
          </div>
        </div>
        
        <div className="card card-padding text-center shadow-card hover:shadow-card-hover transition-all duration-200 bg-gradient-to-br from-secondary-50 to-secondary-100">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-secondary-400 rounded-full">
              <Award className="w-6 h-6 text-white" />
            </div>
            <span className="font-semibold text-neutral-800 text-lg">ИК (ср. балл)</span>
          </div>
          <div className="text-4xl font-bold text-secondary-400 font-primary">
            {currentGrades.block_average.toFixed(1)}
          </div>
        </div>
        
        <div className="card card-padding text-center shadow-card hover:shadow-card-hover transition-all duration-200 bg-gradient-to-br from-success-50 to-success-100">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-success-600 rounded-full">
              <Trophy className="w-6 h-6 text-white" />
            </div>
            <span className="font-semibold text-neutral-800 text-lg">Итоговая оценка</span>
          </div>
          <div className="text-4xl font-bold text-success-600 font-primary">
            {currentGrades.final_grade.toFixed(1)}
          </div>
        </div>
      </div>
    );
  };

  // Обработка ошибок
  if (hasError) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <ParentHeader />
        
        <div className="pt-20 md:pt-24">
          <div className="container mx-auto px-4 py-8 max-w-7xl">
            <div className="text-center py-12">
              <div className="text-red-500 text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold text-neutral-900 mb-4">Ошибка загрузки данных</h2>
              <p className="text-neutral-600 mb-6">{hasError}</p>
              <button
                onClick={handleRefresh}
                className="btn btn-primary"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Загрузка...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Попробовать снова
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      <ParentHeader />
      
      <div className="pt-20 md:pt-24">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          
          {/* Индикатор загрузки */}
          {isLoading && (
            <div className="fixed top-4 right-4 z-50">
              <div className="bg-white rounded-lg shadow-lg p-4 flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin text-primary-600" />
                <span className="text-sm text-neutral-700">Загрузка данных...</span>
              </div>
            </div>
          )}

          {/* Индикатор валидации */}
          {isValidating && !isLoading && (
            <div className="fixed top-4 right-4 z-50">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm text-blue-700">Обновление...</span>
              </div>
            </div>
          )}

          {/* Заголовок с информацией о студенте */}
          {studentDetails && (
            <div className="mb-8 text-center">
              <h1 className="text-3xl font-bold text-neutral-900 mb-2">
                {studentDetails.student_name} {studentDetails.student_surname}
              </h1>
              <p className="text-neutral-600">Успеваемость и посещаемость</p>
            </div>
          )}
          
          {/* Выбор предмета - центрированный */}
          <div className="mb-12 flex justify-center">
            <div className="grid grid-cols-2 gap-6 w-full max-w-md">
              <button
                onClick={() => handleSubjectChange(SUBJECTS.CHEMISTRY)}
                className={`btn btn-lg ${selectedSubject === SUBJECTS.CHEMISTRY ? 'btn-primary' : 'btn-outline'} font-semibold`}
                disabled={isLoading}
              >
                Химия
              </button>
              <button
                onClick={() => handleSubjectChange(SUBJECTS.BIOLOGY)}
                className={`btn btn-lg ${selectedSubject === SUBJECTS.BIOLOGY ? 'btn-primary' : 'btn-outline'} font-semibold`}
                disabled={isLoading}
              >
                Биология
              </button>
            </div>
          </div>

          {/* Активное окно */}
          <div className="card shadow-strong">
            {/* Вкладки посещаемость/успеваемость - полная ширина */}
            <div className="border-b border-neutral-200 bg-gradient-to-r from-neutral-25 to-neutral-50">
              <div className="flex justify-center">
                <div className="flex">
                  <button
                    onClick={() => handleTabChange('attendance')}
                    className={`px-8 py-5 font-semibold transition-all duration-200 border-b-3 ${
                      activeTab === 'attendance'
                        ? 'border-primary-600 text-primary-600 bg-white'
                        : 'border-transparent text-neutral-600 hover:text-primary-600 hover:bg-neutral-50'
                    }`}
                    disabled={isLoading}
                  >
                    <Calendar className="w-5 h-5 inline mr-3" />
                    Посещаемость
                  </button>
                  <button
                    onClick={() => handleTabChange('performance')}
                    className={`px-8 py-5 font-semibold transition-all duration-200 border-b-3 ${
                      activeTab === 'performance'
                        ? 'border-primary-600 text-primary-600 bg-white'
                        : 'border-transparent text-neutral-600 hover:text-primary-600 hover:bg-neutral-50'
                    }`}
                    disabled={isLoading}
                  >
                    <BookOpen className="w-5 h-5 inline mr-3" />
                    Успеваемость
                  </button>
                </div>
              </div>
            </div>

            {/* Выбор модуля - центрированный и равномерно распределенный */}
            <div className="card-padding border-b border-neutral-200 bg-gradient-to-r from-primary-25 to-secondary-25">
              <div className="flex justify-center">
                <div className="flex flex-wrap gap-3 justify-center max-w-4xl">
                  <button
                    onClick={() => handleModuleChange('all')}
                    className={`btn ${selectedModule === 'all' ? 'btn-primary' : 'btn-outline'} font-medium px-6`}
                    disabled={isLoading}
                  >
                    Все модули
                  </button>
                  {modules.map((module) => {
                    const moduleId = parseInt(module.id.replace('module_', ''));
                    return (
                      <button
                        key={module.id}
                        onClick={() => handleModuleChange(moduleId)}
                        className={`btn ${selectedModule === moduleId ? 'btn-primary' : 'btn-outline'} font-medium px-6`}
                        disabled={isLoading}
                      >
                        {module.name}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Контент - полная ширина */}
            <div className="card-padding">
              {isLoading ? (
                <div className="text-center py-12">
                  <Loader2 className="w-12 h-12 animate-spin text-primary-600 mx-auto mb-4" />
                  <p className="text-neutral-600">Загрузка данных...</p>
                </div>
              ) : (
                activeTab === 'attendance' ? renderAttendanceCalendar() : renderPerformanceTable()
              )}
            </div>
          </div>

          {/* Итоговые оценки - полная ширина и красивое распределение */}
          <div className="mt-12">
            {renderFinalGrades()}
          </div>

          {/* Кнопка обновления */}
          <div className="mt-8 text-center">
            <button
              onClick={handleRefresh}
              className="btn btn-outline btn-sm"
              disabled={isLoading || isValidating}
            >
              {isValidating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Обновление...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Обновить данные
                </>
              )}
            </button>
          </div>

          {/* Дополнительная информация */}
          {studentDetails && (
            <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Статистика посещаемости */}
              <div className="card card-padding">
                <h3 className="text-lg font-bold text-neutral-900 mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-primary-600" />
                  Статистика посещаемости
                </h3>
                {currentSubjectData?.attendance?.statistics ? (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Всего уроков:</span>
                      <span className="font-semibold">{currentSubjectData.attendance.statistics.total_lessons}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Присутствовал:</span>
                      <span className="font-semibold text-success-600">{currentSubjectData.attendance.statistics.present_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Опоздал:</span>
                      <span className="font-semibold text-warning-600">{currentSubjectData.attendance.statistics.late_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Отсутствовал:</span>
                      <span className="font-semibold text-error-600">{currentSubjectData.attendance.statistics.absent_count}</span>
                    </div>
                    <div className="flex justify-between border-t pt-3">
                      <span className="text-neutral-900 font-semibold">Посещаемость:</span>
                      <span className="font-bold text-lg text-primary-600">
                        {currentSubjectData.attendance.statistics.attendance_rate.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ) : (
                  <p className="text-neutral-500">Нет данных</p>
                )}
              </div>

              {/* Статистика успеваемости */}
              <div className="card card-padding">
                <h3 className="text-lg font-bold text-neutral-900 mb-4 flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-primary-600" />
                  Статистика успеваемости
                </h3>
                {finalGrades[selectedSubject] ? (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Ср. по разделам:</span>
                      <span className="font-semibold">{finalGrades[selectedSubject].section_average.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Ср. по блокам:</span>
                      <span className="font-semibold">{finalGrades[selectedSubject].block_average.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Ср. по темам:</span>
                      <span className="font-semibold">{finalGrades[selectedSubject].topic_average.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-600">Текущий рейтинг:</span>
                      <span className="font-semibold">{finalGrades[selectedSubject].current_average.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between border-t pt-3">
                      <span className="text-neutral-900 font-semibold">Итоговая оценка:</span>
                      <span className="font-bold text-lg text-success-600">
                        {finalGrades[selectedSubject].final_grade.toFixed(1)}
                      </span>
                    </div>
                  </div>
                ) : (
                  <p className="text-neutral-500">Нет данных</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ParentDetails;