import { useMemo } from "react";
import ParentHeader from "../../../components/Landing/Header";
import { ChevronDown, Trophy, Medal, Award, TrendingUp, AlertCircle, RefreshCw } from "lucide-react";
import { useStatisticsPage, useTournamentTable } from "../../../hooks/useStatistic";
import { statisticsAPI, SUBJECTS, STATISTIC_TYPES, TABLE_TYPES } from "../../../services/api/statistic";
import type { StatisticType, StudentRankingInfo } from "../../../services/api/statistic";

const ParentStatistics = () => {
  // Получаем ID студента (в реальном приложении из контекста/роутера)
  const studentId = 1; // TODO: получить из контекста пользователя

  // Используем основной хук для статистики
  const {
    selectedSubject,
    selectedMetric,
    selectedTable,
    studentData,
    chartData,
    tournamentTables,
    isLoading,
    isValidating,
    hasError,
    handleSubjectChange,
    handleMetricChange,
    handleTableChange,
    handleRefresh
  } = useStatisticsPage(studentId);

  // Используем хук для текущей турнирной таблицы
  const {
    ranking: currentRanking,
    getStudentRank,
    getTopThree,
    getCurrentStudent
  } = useTournamentTable(selectedTable, studentId, selectedTable === TABLE_TYPES.MY_GROUP_AVERAGE ? studentData?.group_id : undefined);

  // Определение максимального значения для оси Y графика
  const maxValue = useMemo(() => {
    return statisticsAPI.getChartMaxValue(selectedMetric);
  }, [selectedMetric]);

  // Получение цвета для графика
  const chartColor = useMemo(() => {
    return statisticsAPI.getChartColor(selectedSubject);
  }, [selectedSubject]);

  // Функция для отрисовки графика
  const renderChart = () => {
    if (!chartData.length) {
      return (
        <div className="bg-white rounded-xl p-6 shadow-soft flex items-center justify-center h-96">
          <div className="text-center text-gray-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-4" />
            <p>Нет данных для отображения</p>
          </div>
        </div>
      );
    }

    const width = 800;
    const height = 400;
    const padding = 60;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;

    // Создание точек для линии
    const points = chartData
      .map((point, index) => {
        const x = padding + (index * chartWidth) / (chartData.length - 1);
        const y = height - padding - (point.value / maxValue) * chartHeight;
        return `${x},${y}`;
      })
      .join(" ");

    return (
      <div className="bg-white rounded-xl p-6 shadow-soft">
        {isValidating && (
          <div className="flex items-center gap-2 mb-4 text-blue-600 text-sm">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>Обновление данных...</span>
          </div>
        )}
        
        <svg width={width} height={height} className="w-full h-auto">
          {/* Сетка по Y */}
          {Array.from({ length: 11 }, (_, i) => (
            <g key={`grid-y-${i}`}>
              <line
                x1={padding}
                y1={padding + (i * chartHeight) / 10}
                x2={width - padding}
                y2={padding + (i * chartHeight) / 10}
                stroke="#e2e8f0"
                strokeWidth="1"
              />
              <text
                x={padding - 10}
                y={padding + (i * chartHeight) / 10 + 5}
                textAnchor="end"
                fontSize="12"
                fill="#64748b"
              >
                {Math.round(maxValue - (i * maxValue) / 10)}
              </text>
            </g>
          ))}

          {/* Сетка по X */}
          {chartData.map((point, index) => (
            <g key={`grid-x-${index}`}>
              <line
                x1={padding + (index * chartWidth) / (chartData.length - 1)}
                y1={padding}
                x2={padding + (index * chartWidth) / (chartData.length - 1)}
                y2={height - padding}
                stroke="#e2e8f0"
                strokeWidth="1"
              />
              <text
                x={padding + (index * chartWidth) / (chartData.length - 1)}
                y={height - padding + 20}
                textAnchor="middle"
                fontSize="12"
                fill="#64748b"
              >
                {point.month}
              </text>
            </g>
          ))}

          {/* Оси */}
          <line
            x1={padding}
            y1={padding}
            x2={padding}
            y2={height - padding}
            stroke="#1e293b"
            strokeWidth="2"
          />
          <line
            x1={padding}
            y1={height - padding}
            x2={width - padding}
            y2={height - padding}
            stroke="#1e293b"
            strokeWidth="2"
          />

          {/* Линия графика */}
          <polyline
            points={points}
            fill="none"
            stroke={chartColor}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Точки на графике */}
          {chartData.map((point, index) => {
            const x = padding + (index * chartWidth) / (chartData.length - 1);
            const y = height - padding - (point.value / maxValue) * chartHeight;
            return (
              <g key={`point-${index}`}>
                <circle
                  cx={x}
                  cy={y}
                  r="6"
                  fill={chartColor}
                  stroke="white"
                  strokeWidth="2"
                />
                <text
                  x={x}
                  y={y - 15}
                  textAnchor="middle"
                  fontSize="12"
                  fill="#1e293b"
                  fontWeight="600"
                >
                  {point.value}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    );
  };

  // Компонент турнирной таблицы
  const TournamentTableSection = () => {
    const currentTable = tournamentTables.find(table => table.table_type === selectedTable);
    const students = currentTable?.students || [];
    const currentStudentRank = getStudentRank();
    const topThree = getTopThree();
    const currentStudentData = getCurrentStudent();

    const getRankIcon = (rank: number) => {
      switch (rank) {
        case 1:
          return <Trophy className="w-5 h-5 text-yellow-500" />;
        case 2:
          return <Medal className="w-5 h-5 text-gray-400" />;
        case 3:
          return <Award className="w-5 h-5 text-amber-600" />;
        default:
          return null;
      }
    };

    const getTableColumns = () => {
      switch (selectedTable) {
        case TABLE_TYPES.ALL_GROUPS_AVERAGE:
        case TABLE_TYPES.MY_GROUP_AVERAGE:
          return ["№", "Ф.И.О.", "Группа", "Биология", "Химия"];
        case TABLE_TYPES.DTM_ALL_TIME:
        case TABLE_TYPES.DTM_LAST_MONTH:
          return ["№", "Ф.И.О.", "Группа", "Биология", "Химия", "Общие", "Итого"];
        default:
          return [];
      }
    };

    const renderRow = (student: StudentRankingInfo, isCurrentStudent = false) => {
      const rowClass = isCurrentStudent
        ? "bg-primary-50 border-primary-200 border-2"
        : student.rank <= 3
        ? "bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200"
        : "hover:bg-neutral-50";

      return (
        <tr
          key={student.student_id}
          className={`${rowClass} transition-colors duration-200`}
        >
          <td className="px-6 py-4 text-center">
            <div className="flex items-center justify-center gap-2">
              {getRankIcon(student.rank)}
              <span className="font-bold text-primary-700">
                {student.rank}
              </span>
            </div>
          </td>
          <td className="px-6 py-4">
            <span
              className={`font-medium ${
                isCurrentStudent ? "text-primary-700" : "text-neutral-900"
              }`}
            >
              {student.name}
            </span>
          </td>
          <td className="px-6 py-4 text-center">
            <span className="px-2 py-1 bg-secondary-100 text-secondary-700 rounded-full text-sm font-medium">
              {student.group_id}
            </span>
          </td>

          {selectedTable.includes('average') ? (
            <>
              <td className="px-6 py-4 text-center font-medium text-neutral-700">
                {student.biology_avg?.toFixed(1) || '0.0'}
              </td>
              <td className="px-6 py-4 text-center font-medium text-neutral-700">
                {student.chemistry_avg?.toFixed(1) || '0.0'}
              </td>
            </>
          ) : (
            <>
              <td className="px-6 py-4 text-center font-medium text-neutral-700">
                {selectedTable === TABLE_TYPES.DTM_ALL_TIME
                  ? student.biology_dtm || 0
                  : student.last_biology_dtm || 0}
              </td>
              <td className="px-6 py-4 text-center font-medium text-neutral-700">
                {selectedTable === TABLE_TYPES.DTM_ALL_TIME
                  ? student.chemistry_dtm || 0
                  : student.last_chemistry_dtm || 0}
              </td>
              <td className="px-6 py-4 text-center font-medium text-neutral-700">
                {selectedTable === TABLE_TYPES.DTM_ALL_TIME
                  ? student.general_dtm || 0
                  : student.last_general_dtm || 0}
              </td>
              <td className="px-6 py-4 text-center">
                <span className="font-bold text-primary-600 text-lg">
                  {selectedTable === TABLE_TYPES.DTM_ALL_TIME
                    ? student.total_dtm?.toFixed(1) || '0.0'
                    : student.last_total_dtm?.toFixed(1) || '0.0'}
                </span>
              </td>
            </>
          )}
        </tr>
      );
    };

    const renderTournamentTable = () => {
      if (!students.length) {
        return (
          <div className="bg-white rounded-xl shadow-soft p-8 text-center">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-500">Нет данных для отображения турнирной таблицы</p>
          </div>
        );
      }

      return (
        <div className="bg-white rounded-xl shadow-soft overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-primary-600 text-white">
                <tr>
                  {getTableColumns().map((column, index) => (
                    <th
                      key={index}
                      className="px-6 py-4 text-center font-semibold"
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {/* Топ 3 места */}
                {topThree.map((student) =>
                  renderRow(student, student.student_id === studentId)
                )}

                {/* Разрыв если текущий студент не в топ 3 */}
                {currentStudentRank > 3 && currentStudentData && (
                  <>
                    <tr>
                      <td
                        colSpan={getTableColumns().length}
                        className="px-6 py-3 text-center text-neutral-400"
                      >
                        <div className="flex items-center justify-center gap-2">
                          <div className="h-px bg-neutral-300 flex-1"></div>
                          <span className="text-sm">...</span>
                          <div className="h-px bg-neutral-300 flex-1"></div>
                        </div>
                      </td>
                    </tr>
                    {/* Текущий студент */}
                    {renderRow(currentStudentData, true)}
                  </>
                )}
              </tbody>
            </table>
          </div>
        </div>
      );
    };

    return (
      <div className="card card-padding">
        <div className="flex items-center gap-3 mb-6">
          <Trophy className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl font-bold text-neutral-900 font-primary">
            Турнирные таблицы
          </h2>
        </div>

        {/* Кнопки фильтров таблиц */}
        <div className="flex flex-wrap gap-2 mb-6">
          {Object.values(TABLE_TYPES).map((tableType) => (
            <button
              key={tableType}
              onClick={() => handleTableChange(tableType)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 text-sm ${
                selectedTable === tableType
                  ? "bg-primary-600 text-white shadow-md"
                  : "bg-neutral-200 text-neutral-700 hover:bg-neutral-300"
              }`}
            >
              {statisticsAPI.getTableTypeDisplayName(tableType)}
            </button>
          ))}
        </div>

        {/* Таблица */}
        {renderTournamentTable()}
      </div>
    );
  };

  // Отображение ошибки
  if (hasError) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <ParentHeader />
        <div className="pt-20 md:pt-24">
          <div className="container mx-auto px-4 py-8">
            <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
              <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
              <h2 className="text-xl font-semibold text-red-800 mb-2">Ошибка загрузки данных</h2>
              <p className="text-red-600 mb-4">{hasError}</p>
              <button
                onClick={handleRefresh}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin inline mr-2" />
                    Загрузка...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4 inline mr-2" />
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

  // Отображение загрузки
  if (isLoading && !studentData) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <ParentHeader />
        <div className="pt-20 md:pt-24">
          <div className="container mx-auto px-4 py-8">
            <div className="animate-pulse">
              {/* Заголовок */}
              <div className="h-8 bg-gray-200 rounded w-64 mb-8"></div>
              
              {/* График */}
              <div className="bg-white rounded-xl p-6 shadow-soft mb-8">
                <div className="h-6 bg-gray-200 rounded w-32 mb-6"></div>
                <div className="h-96 bg-gray-100 rounded"></div>
                <div className="flex gap-4 mt-6">
                  <div className="h-10 bg-gray-200 rounded w-24"></div>
                  <div className="h-10 bg-gray-200 rounded w-24"></div>
                  <div className="h-10 bg-gray-200 rounded w-48"></div>
                </div>
              </div>
              
              {/* Турнирная таблица */}
              <div className="bg-white rounded-xl p-6 shadow-soft">
                <div className="h-6 bg-gray-200 rounded w-48 mb-6"></div>
                <div className="space-y-4">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="h-12 bg-gray-100 rounded"></div>
                  ))}
                </div>
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
          {/* Заголовок */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-primary-900 font-primary">
                  Статистика
                </h1>
                <p className="text-neutral-600 mt-2">
                  Детальная аналитика успеваемости и рейтинги
                  {studentData && (
                    <span className="ml-2 text-primary-600 font-medium">
                      - {studentData.student_name}
                    </span>
                  )}
                </p>
              </div>
              
              {/* Кнопка обновления */}
              <button
                onClick={handleRefresh}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-200"
                disabled={isLoading || isValidating}
              >
                <RefreshCw className={`w-4 h-4 ${(isLoading || isValidating) ? 'animate-spin' : ''}`} />
                Обновить
              </button>
            </div>
            
            {/* Общая статистика */}
            {studentData?.overall && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-primary-600">
                    {studentData.overall.overall_average.toFixed(1)}
                  </div>
                  <div className="text-sm text-gray-600">Общий балл</div>
                </div>
                
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-green-600">
                    {studentData.overall.attendance_rate.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Посещаемость</div>
                </div>
                
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-blue-600">
                    {studentData.overall.completed_tests}
                  </div>
                  <div className="text-sm text-gray-600">Тестов пройдено</div>
                </div>
                
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-purple-600">
                    {studentData.overall.best_dtm_score.toFixed(0)}
                  </div>
                  <div className="text-sm text-gray-600">Лучший ДТМ</div>
                </div>
              </div>
            )}
          </div>

          {/* Блок с графиком */}
          <div className="bg-white rounded-xl p-6 shadow-soft mb-8">
            <div className="flex items-center gap-3 mb-6">
              <TrendingUp className="w-6 h-6 text-primary-600" />
              <h2 className="text-2xl font-bold text-neutral-900 font-primary">
                Прогресс
              </h2>
              
              {/* Показываем тренд если есть данные */}
              {chartData.length > 0 && (
                <div className="ml-auto text-sm">
                  {(() => {
                    const trend = statisticsAPI.calculateImprovement(chartData);
                    const trendInfo = statisticsAPI.formatTrend(trend);
                    return (
                      <span className={`${trendInfo.color} font-medium`}>
                        {trendInfo.icon} {trendInfo.text}
                      </span>
                    );
                  })()}
                </div>
              )}
            </div>

            {/* График */}
            {renderChart()}

            {/* Фильтры */}
            <div className="flex flex-wrap items-center gap-4 mt-6">
              {/* Кнопки предметов */}
              <div className="flex gap-2">
                {Object.values(SUBJECTS).map((subject) => (
                  <button
                    key={subject}
                    onClick={() => handleSubjectChange(subject)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                      selectedSubject === subject
                        ? subject === SUBJECTS.CHEMISTRY
                          ? "bg-primary-600 text-white shadow-md"
                          : "bg-green-600 text-white shadow-md"
                        : "bg-neutral-200 text-neutral-700 hover:bg-neutral-300"
                    }`}
                  >
                    {statisticsAPI.getSubjectDisplayName(subject)}
                  </button>
                ))}
              </div>

              {/* Выпадающий список метрик */}
              <div className="relative">
                <select
                  value={selectedMetric}
                  onChange={(e) => handleMetricChange(e.target.value as StatisticType)}
                  className="appearance-none bg-white border border-neutral-300 rounded-lg px-4 py-2 pr-10 text-neutral-700 font-medium hover:border-primary-400 focus:border-primary-600 focus:ring-2 focus:ring-primary-200 transition-colors duration-200"
                >
                  {Object.values(STATISTIC_TYPES).map((type) => (
                    <option key={type} value={type}>
                      {statisticsAPI.getStatisticTypeDisplayName(type)}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-500 pointer-events-none" />
              </div>
            </div>
          </div>

          {/* Турнирные таблицы */}
          <TournamentTableSection />
        </div>
      </div>
    </div>
  );
};

export default ParentStatistics;