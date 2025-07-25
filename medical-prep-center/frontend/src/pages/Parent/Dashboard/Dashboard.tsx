import React from "react";
import ParentHeader from "../../../components/Landing/Header";
import {
  ChevronDown,
  ChevronUp,
  Calendar,
  Clock,
  BookOpen,
  Award,
  Target,
  TrendingUp,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  User,
  Bell,
  MessageSquare,
} from "lucide-react";
import { 
  useParentStatistics, 
  usePerformanceStats, 
  useDisciplineAnalysis, 
  useExamAnalysis 
} from "../../../hooks/useParents";
import { parentStatsAPI } from "../../../services/api/parent_dashboard";

// Получаем ID студента (в реальном приложении из роутера или контекста)
const STUDENT_ID = 1; // Заглушка

const ParentStatistics: React.FC = () => {
  const {
    studentInfo,
    performance,
    discipline,
    exams,
    admissionChance,
    recentComments,
    isLoading,
    isValidating,
    hasError,
    handleRefresh,
    handleToggleBlock,
    expandedBlocks,
    notifications
  } = useParentStatistics(STUDENT_ID);

  const performanceStats = usePerformanceStats(performance);
  const disciplineAnalysis = useDisciplineAnalysis(discipline);
  const examAnalysis = useExamAnalysis(exams);

  // Компонент загрузки
  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <ParentHeader />
        <div className="pt-20 md:pt-24">
          <div className="container mx-auto px-4 py-8">
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <RefreshCw className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-4" />
                <p className="text-neutral-600">Загрузка статистики...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Компонент ошибки
  if (hasError) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <ParentHeader />
        <div className="pt-20 md:pt-24">
          <div className="container mx-auto px-4 py-8">
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <AlertTriangle className="w-8 h-8 text-error-600 mx-auto mb-4" />
                <p className="text-error-600 mb-4">{hasError}</p>
                <button 
                  onClick={handleRefresh}
                  className="btn btn-primary btn-sm"
                >
                  Попробовать снова
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Проверка наличия данных студента
  if (!studentInfo) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <ParentHeader />
        <div className="pt-20 md:pt-24">
          <div className="container mx-auto px-4 py-8">
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <User className="w-8 h-8 text-neutral-400 mx-auto mb-4" />
                <p className="text-neutral-600">Данные студента не найдены</p>
                <button 
                  onClick={handleRefresh}
                  className="btn btn-secondary btn-sm mt-4"
                >
                  Обновить
                </button>
              </div>
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
        <div className="container mx-auto px-4 py-8">
          {/* Заголовок с кнопкой обновления */}
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-neutral-900 font-primary">
              Статистика успеваемости
            </h1>
            <div className="flex items-center gap-3">
              {/* Индикатор уведомлений */}
              {notifications.unreadCount > 0 && (
                <div className="relative">
                  <Bell className="w-5 h-5 text-warning-600" />
                  <span className="absolute -top-2 -right-2 bg-error-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {notifications.unreadCount}
                  </span>
                </div>
              )}
              
              {/* Кнопка обновления */}
              <button
                onClick={handleRefresh}
                disabled={isValidating}
                className="btn btn-secondary btn-sm flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${isValidating ? 'animate-spin' : ''}`} />
                Обновить
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Левая колонка */}
            <div className="lg:col-span-1 space-y-6">
              {/* Фотография ученика */}
              <div className="card card-padding text-center">
                {studentInfo.photo ? (
                  <img
                    src={studentInfo.photo}
                    alt={`${studentInfo.name} ${studentInfo.surname}`}
                    className="w-32 h-32 mx-auto mb-4 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-32 h-32 mx-auto mb-4 rounded-full bg-gradient-to-r from-primary-600 to-secondary-400 flex items-center justify-center">
                    <span className="text-4xl text-white font-bold">
                      {parentStatsAPI.getInitials(studentInfo.name, studentInfo.surname)}
                    </span>
                  </div>
                )}
              </div>

              {/* Информация об ученике */}
              <div className="card card-padding">
                <h3 className="text-xl font-bold text-neutral-900 mb-4 font-primary">
                  {studentInfo.name} {studentInfo.surname}
                </h3>

                <div className="space-y-4">
                  {/* Направление */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <User className="w-4 h-4 text-primary-600" />
                      <span className="font-medium text-neutral-700">
                        Направление
                      </span>
                    </div>
                    <p className="text-sm text-neutral-600 ml-6">
                      {studentInfo.direction}
                    </p>
                  </div>

                  {/* Цель */}
                  {studentInfo.goal && (
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Target className="w-4 h-4 text-primary-600" />
                        <span className="font-medium text-neutral-700">
                          Цель
                        </span>
                      </div>
                      <p className="text-sm text-neutral-600 ml-6">
                        {studentInfo.goal}
                      </p>
                    </div>
                  )}

                  {/* Расписание по химии */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Calendar className="w-4 h-4 text-primary-600" />
                      <span className="font-medium text-neutral-700">
                        Расписание по химии
                      </span>
                    </div>
                    <p className="text-sm text-neutral-600 ml-6">
                      Пн, Ср, Пт - 16:00-17:30
                    </p>
                  </div>

                  {/* Расписание по биологии */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Calendar className="w-4 h-4 text-secondary-400" />
                      <span className="font-medium text-neutral-700">
                        Расписание по биологии
                      </span>
                    </div>
                    <p className="text-sm text-neutral-600 ml-6">
                      Вт, Чт, Сб - 14:00-15:30
                    </p>
                  </div>
                </div>
              </div>

              {/* ДТМ баллы */}
              {admissionChance && (
                <div className="card card-padding">
                  <h4 className="font-bold text-neutral-900 mb-4 font-primary text-lg">
                    ДТМ
                  </h4>

                  <div className="space-y-3">
                    {/* Текущий балл */}
                    <div>
                      <span className="text-sm text-neutral-600">
                        Текущий балл:
                      </span>
                      <div className="text-2xl font-bold text-primary-600 font-primary">
                        {admissionChance.current_score.toFixed(1)}
                        <span className="text-sm text-neutral-500">/189</span>
                      </div>
                    </div>

                    {/* Необходимый балл */}
                    <div>
                      <span className="text-sm text-neutral-600">
                        Необходимый балл:
                      </span>
                      <div className="text-2xl font-bold text-secondary-400 font-primary">
                        {admissionChance.required_score.toFixed(1)}
                        <span className="text-sm text-neutral-500">/189</span>
                      </div>
                    </div>

                    {/* Статус */}
                    <div className="mt-4">
                      {admissionChance.current_score >= admissionChance.required_score ? (
                        <div className="flex items-center gap-2 text-success-600">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm font-medium">Проходной балл достигнут</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 text-warning-600">
                          <AlertTriangle className="w-4 h-4" />
                          <span className="text-sm font-medium">
                            До проходного: {(admissionChance.required_score - admissionChance.current_score).toFixed(1)} балла
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Правая колонка */}
            <div className="lg:col-span-2 space-y-6">
              {/* Блок Успеваемость */}
              <div className="card">
                <div
                  className="card-padding border-b border-neutral-200 cursor-pointer flex items-center justify-between hover:bg-neutral-50 transition-colors duration-200"
                  onClick={() => handleToggleBlock("performance")}
                >
                  <div className="flex items-center gap-3">
                    <BookOpen className="w-5 h-5 text-primary-600" />
                    <h3 className="text-xl font-bold text-neutral-900 font-primary">
                      Успеваемость
                    </h3>
                    <span className={`badge ${parentStatsAPI.getStatusColor(performanceStats.overallStatus)}`}>
                      {performanceStats.overallStatus}
                    </span>
                  </div>
                  {expandedBlocks.performance ? (
                    <ChevronUp className="w-5 h-5 text-neutral-500" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-neutral-500" />
                  )}
                </div>

                {expandedBlocks.performance && (
                  <div className="card-padding space-y-4 animate-slide-down">
                    <div className="space-y-4">
                      {Object.entries(performance).map(([subjectName, subjectGrades]) => (
                        <div key={subjectName}>
                          <div className="flex items-center justify-between mb-3">
                            <span className="font-medium text-neutral-900">
                              {subjectName}
                            </span>
                            <span className={`badge ${parentStatsAPI.getStatusColor(subjectGrades.status)}`}>
                              {subjectGrades.status}
                            </span>
                          </div>
                          <div className="ml-4 space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-neutral-700">Опросы:</span>
                              <span className="font-medium text-neutral-900">
                                {subjectGrades.polls_score.toFixed(1)} (из {subjectGrades.polls_total})
                              </span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-neutral-700">Тесты:</span>
                              <span className="font-medium text-neutral-900">
                                {subjectGrades.tests_score.toFixed(1)} (из {subjectGrades.tests_total})
                              </span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-neutral-700">
                                Контрольные работы:
                              </span>
                              <span className="font-medium text-neutral-900">
                                {subjectGrades.control_works_score.toFixed(1)} (из {subjectGrades.control_works_total})
                              </span>
                            </div>
                            <div className="flex items-center justify-between border-t pt-2">
                              <span className="text-neutral-700 font-medium">
                                Средний балл:
                              </span>
                              <span className={`font-bold ${parentStatsAPI.getGradeColor(subjectGrades.average_score * 10)}`}>
                                {subjectGrades.average_score.toFixed(1)}/10
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    <button className="btn btn-primary btn-sm">
                      Подробнее
                    </button>
                  </div>
                )}
              </div>

              {/* Блок Дисциплина */}
              {discipline && (
                <div className="card">
                  <div
                    className="card-padding border-b border-neutral-200 cursor-pointer flex items-center justify-between hover:bg-neutral-50 transition-colors duration-200"
                    onClick={() => handleToggleBlock("discipline")}
                  >
                    <div className="flex items-center gap-3">
                      <Clock className="w-5 h-5 text-primary-600" />
                      <h3 className="text-xl font-bold text-neutral-900 font-primary">
                        Дисциплина
                      </h3>
                      <span className={`badge ${parentStatsAPI.getStatusColor(discipline.status)}`}>
                        {discipline.status}
                      </span>
                    </div>
                    {expandedBlocks.discipline ? (
                      <ChevronUp className="w-5 h-5 text-neutral-500" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-neutral-500" />
                    )}
                  </div>

                  {expandedBlocks.discipline && (
                    <div className="card-padding space-y-4 animate-slide-down">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-neutral-700">
                            Количество пропусков
                          </span>
                          <span className={`font-medium ${disciplineAnalysis.isAttendanceCritical ? 'text-error-600' : 'text-neutral-900'}`}>
                            {discipline.total_absences} из {discipline.total_lessons} занятий
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-neutral-700">
                            Посещаемость
                          </span>
                          <span className={`font-medium ${disciplineAnalysis.isAttendanceCritical ? 'text-error-600' : 'text-success-600'}`}>
                            {disciplineAnalysis.attendancePercentage}%
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-neutral-700">
                            Не сданные домашние задания
                          </span>
                          <span className={`font-medium ${disciplineAnalysis.isHomeworkCritical ? 'text-error-600' : 'text-neutral-900'}`}>
                            {discipline.missed_homeworks} из {discipline.total_homeworks} заданий
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-neutral-700">
                            Не сданные опросы
                          </span>
                          <span className={`font-medium ${disciplineAnalysis.isPollsCritical ? 'text-error-600' : 'text-neutral-900'}`}>
                            {discipline.missed_polls} из {discipline.total_polls}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-neutral-700">
                            Замечания от учителя
                          </span>
                          <span className={`font-medium ${discipline.teacher_remarks > 3 ? 'text-error-600' : discipline.teacher_remarks > 0 ? 'text-warning-600' : 'text-success-600'}`}>
                            {discipline.teacher_remarks} замечаний
                          </span>
                        </div>

                        {/* Общий статус дисциплины */}
                        <div className="mt-4 p-3 rounded-lg bg-neutral-50">
                          <div className="flex items-center gap-2 mb-2">
                            {disciplineAnalysis.overallRisk === 'high' && (
                              <XCircle className="w-4 h-4 text-error-600" />
                            )}
                            {disciplineAnalysis.overallRisk === 'medium' && (
                              <AlertTriangle className="w-4 h-4 text-warning-600" />
                            )}
                            {disciplineAnalysis.overallRisk === 'low' && (
                              <CheckCircle className="w-4 h-4 text-success-600" />
                            )}
                            <span className="text-sm font-medium text-neutral-900">
                              Уровень риска: {
                                disciplineAnalysis.overallRisk === 'high' ? 'Высокий' :
                                disciplineAnalysis.overallRisk === 'medium' ? 'Средний' : 'Низкий'
                              }
                            </span>
                          </div>
                          {disciplineAnalysis.overallRisk !== 'low' && (
                            <p className="text-xs text-neutral-600">
                              {disciplineAnalysis.overallRisk === 'high' 
                                ? 'Требуется немедленное внимание к посещаемости и выполнению заданий'
                                : 'Рекомендуется усилить контроль за учебной дисциплиной'
                              }
                            </p>
                          )}
                        </div>
                      </div>

                      <button className="btn btn-primary btn-sm">
                        Подробнее
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Блок Экзамены */}
              {exams && (
                <div className="card">
                  <div
                    className="card-padding border-b border-neutral-200 cursor-pointer flex items-center justify-between hover:bg-neutral-50 transition-colors duration-200"
                    onClick={() => handleToggleBlock("exams")}
                  >
                    <div className="flex items-center gap-3">
                      <Award className="w-5 h-5 text-primary-600" />
                      <h3 className="text-xl font-bold text-neutral-900 font-primary">
                        Экзамены
                      </h3>
                      <span className={`badge ${parentStatsAPI.getStatusColor(exams.status)}`}>
                        {exams.status}
                      </span>
                    </div>
                    {expandedBlocks.exams ? (
                      <ChevronUp className="w-5 h-5 text-neutral-500" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-neutral-500" />
                    )}
                  </div>

                  {expandedBlocks.exams && (
                    <div className="card-padding space-y-4 animate-slide-down">
                      <div className="space-y-3">
                        {exams.last_monthly_exam && (
                          <div className="flex items-center justify-between">
                            <span className="text-neutral-700">
                              Ежемесячный экзамен (последний)
                            </span>
                            <span className={`font-medium ${parentStatsAPI.getGradeColor(exams.last_monthly_exam.percentage)}`}>
                              {exams.last_monthly_exam.score.toFixed(1)} из {exams.last_monthly_exam.max_score}
                            </span>
                          </div>
                        )}

                        {exams.last_final_control && (
                          <div className="flex items-center justify-between">
                            <span className="text-neutral-700">
                              Итоговый контроль (последний)
                            </span>
                            <span className={`font-medium ${parentStatsAPI.getGradeColor(exams.last_final_control.percentage)}`}>
                              {exams.last_final_control.score} из {exams.last_final_control.max_score} баллов
                            </span>
                          </div>
                        )}

                        <div className="flex items-center justify-between">
                          <span className="text-neutral-700">
                            Промежуточный контроль (последний)
                          </span>
                          <span className="font-medium text-neutral-600">
                            {exams.last_intermediate_control ? 
                              `${exams.last_intermediate_control.score} из ${exams.last_intermediate_control.max_score} баллов` :
                              'не проводились'
                            }
                          </span>
                        </div>

                        {/* Статистика экзаменов */}
                        <div className="mt-4 grid grid-cols-2 gap-4">
                          <div className="text-center p-3 bg-neutral-50 rounded-lg">
                            <div className="text-2xl font-bold text-primary-600">
                              {examAnalysis.passRate}%
                            </div>
                            <div className="text-xs text-neutral-600">
                              Успешность сдачи
                            </div>
                          </div>
                          <div className="text-center p-3 bg-neutral-50 rounded-lg">
                            <div className="text-2xl font-bold text-secondary-400">
                              {examAnalysis.averagePerformance}
                            </div>
                            <div className="text-xs text-neutral-600">
                              Средний балл
                            </div>
                          </div>
                        </div>

                        {/* Тренд */}
                        {examAnalysis.isImproving && (
                          <div className="flex items-center gap-2 text-success-600 bg-success-50 p-2 rounded">
                            <TrendingUp className="w-4 h-4" />
                            <span className="text-sm">Положительная динамика</span>
                          </div>
                        )}

                        {examAnalysis.needsAttention && (
                          <div className="flex items-center gap-2 text-warning-600 bg-warning-50 p-2 rounded">
                            <AlertTriangle className="w-4 h-4" />
                            <span className="text-sm">Требует внимания</span>
                          </div>
                        )}
                      </div>

                      <button className="btn btn-primary btn-sm">
                        Подробнее
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Блок шанс поступления */}
              {admissionChance && (
                <div className="card card-padding">
                  <div className="flex items-center gap-3 mb-4">
                    <Target className="w-5 h-5 text-primary-600" />
                    <h3 className="text-xl font-bold text-neutral-900 font-primary">
                      Шанс на поступление
                    </h3>
                  </div>

                  <p className="text-neutral-700 mb-4">
                    Исходя из последних экзаменов, шанс поступить в желаемый ВУЗ:
                  </p>

                  <div className={`text-4xl font-bold font-primary mb-2 ${parentStatsAPI.getAdmissionChanceColor(admissionChance.probability_percentage)}`}>
                    {Math.round(admissionChance.probability_percentage)}%
                  </div>

                  <div className="text-sm text-neutral-600 mb-4">
                    {parentStatsAPI.getAdmissionChanceText(admissionChance.probability_percentage)}
                  </div>

                  <div className="progress-bar mb-6">
                    <div
                      className={`progress-fill ${admissionChance.probability_percentage >= 80 ? 'bg-success-500' : 
                        admissionChance.probability_percentage >= 60 ? 'bg-warning-500' :
                        admissionChance.probability_percentage >= 40 ? 'bg-orange-500' : 'bg-error-500'}`}
                      style={{ width: `${admissionChance.probability_percentage}%` }}
                    ></div>
                  </div>

                  {/* Рекомендации */}
                  {admissionChance.recommendations.length > 0 && (
                    <div className="space-y-2">
                      <h5 className="font-medium text-neutral-900 text-sm">Рекомендации:</h5>
                      <ul className="space-y-1">
                        {(admissionChance.recommendations.slice(0, 3) as string[]).map((recommendation, index) => (
                          <li key={index} className="text-xs text-neutral-600 flex items-start gap-2">
                            <span className="w-1 h-1 bg-neutral-400 rounded-full mt-2 flex-shrink-0"></span>
                            {recommendation}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Последние комментарии */}
              {recentComments.length > 0 && (
                <div className="card card-padding">
                  <div className="flex items-center gap-3 mb-4">
                    <MessageSquare className="w-5 h-5 text-primary-600" />
                    <h4 className="font-bold text-neutral-900 font-primary text-lg">
                      Последние комментарии учителей
                    </h4>
                  </div>
                  
                  <div className="space-y-3">
                    {recentComments.map((comment) => (
                      <div key={comment.comment_id} className="border-l-4 pl-4 py-2 border-l-neutral-200">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`w-2 h-2 rounded-full ${
                            comment.comment_type === 'positive' ? 'bg-success-500' :
                            comment.comment_type === 'negative' ? 'bg-error-500' : 'bg-neutral-400'
                          }`}></span>
                          <span className="text-xs text-neutral-500">
                            {parentStatsAPI.formatDateTime(comment.comment_date)}
                          </span>
                          <span className={`text-xs font-medium ${parentStatsAPI.getCommentTypeColor(comment.comment_type)}`}>
                            {comment.comment_type === 'positive' ? 'Положительный' :
                             comment.comment_type === 'negative' ? 'Замечание' : 'Нейтральный'}
                          </span>
                        </div>
                        <p className="text-sm text-neutral-700">
                          {comment.comment_text}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Уведомления */}
              {notifications.notifications.length > 0 && (
                <div className="card card-padding">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <Bell className="w-5 h-5 text-primary-600" />
                      <h4 className="font-bold text-neutral-900 font-primary text-lg">
                        Уведомления
                      </h4>
                    </div>
                    {notifications.unreadCount > 0 && (
                      <span className="bg-error-100 text-error-800 text-xs px-2 py-1 rounded-full">
                        {notifications.unreadCount} новых
                      </span>
                    )}
                  </div>
                  
                  <div className="space-y-3">
                    {notifications.notifications.slice(0, 3).map((notification) => (
                      <div 
                        key={notification.notification_id} 
                        className={`p-3 rounded-lg border ${parentStatsAPI.getNotificationColor(notification.type)}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h5 className="font-medium text-sm">{notification.title}</h5>
                              {notification.priority === 'high' && (
                                <span className="bg-error-500 text-white text-xs px-1 py-0.5 rounded">
                                  Важно
                                </span>
                              )}
                            </div>
                            <p className="text-xs opacity-80">{notification.message}</p>
                            <div className="text-xs opacity-60 mt-2">
                              {parentStatsAPI.getRelativeTime(notification.created_at)}
                            </div>
                          </div>
                          {!notification.is_read && (
                            <div className="w-2 h-2 bg-current rounded-full flex-shrink-0 mt-1 ml-2"></div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {notifications.notifications.length > 3 && (
                    <div className="mt-3 text-center">
                      <button className="text-primary-600 text-sm hover:text-primary-700">
                        Показать все уведомления ({notifications.notifications.length})
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Кнопка рекомендации */}
              <div className="text-center">
                <a
                  href="/parent/recommendations"
                  className="btn btn-primary btn-lg items-center gap-2 inline-flex"
                >
                  <TrendingUp className="w-5 h-5" />
                  Рекомендации для вас
                </a>
              </div>
            </div>
          </div>

          {/* Дополнительная информация */}
          {(performanceStats.totalSubjects > 0 || disciplineAnalysis.attendancePercentage > 0) && (
            <div className="mt-8 bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
              <h3 className="text-lg font-bold text-neutral-900 mb-4 font-primary">
                Краткая сводка
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Общая успеваемость */}
                {performanceStats.totalSubjects > 0 && (
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary-600 mb-1">
                      {performanceStats.averageScore.toFixed(1)}
                    </div>
                    <div className="text-sm text-neutral-600">
                      Средний балл по {performanceStats.totalSubjects} предметам
                    </div>
                  </div>
                )}

                {/* Посещаемость */}
                {disciplineAnalysis.attendancePercentage > 0 && (
                  <div className="text-center">
                    <div className={`text-2xl font-bold mb-1 ${
                      disciplineAnalysis.attendancePercentage >= 90 ? 'text-success-600' :
                      disciplineAnalysis.attendancePercentage >= 75 ? 'text-warning-600' : 'text-error-600'
                    }`}>
                      {disciplineAnalysis.attendancePercentage}%
                    </div>
                    <div className="text-sm text-neutral-600">
                      Посещаемость занятий
                    </div>
                  </div>
                )}

                {/* Шанс поступления */}
                {admissionChance && (
                  <div className="text-center">
                    <div className={`text-2xl font-bold mb-1 ${parentStatsAPI.getAdmissionChanceColor(admissionChance.probability_percentage)}`}>
                      {Math.round(admissionChance.probability_percentage)}%
                    </div>
                    <div className="text-sm text-neutral-600">
                      Шанс поступления
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ParentStatistics;