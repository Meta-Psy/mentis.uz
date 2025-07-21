import React, { useState, useMemo } from "react";
import ParentHeader from "../../components/layout/Header/parent_header";
import { ChevronDown, Trophy, Medal, Award, TrendingUp } from "lucide-react";

const ParentStatistics = () => {
  // Состояния для фильтров
  const [selectedSubject, setSelectedSubject] = useState("chemistry");
  const [selectedMetric, setSelectedMetric] = useState("current_grades");
  const [selectedTable, setSelectedTable] = useState("all_groups_average");

  // Моковые данные - в реальном приложении будут приходить из API
  const mockData = {
    currentStudent: {
      id: 1,
      name: "Иванов Алексей Игоревич",
      group: 3,
    },

    // Данные по оценкам для графика
    grades: {
      chemistry: {
        current_grades: [
          { month: "сент.", value: 7.5 },
          { month: "окт.", value: 8.2 },
          { month: "нояб.", value: 8.8 },
          { month: "дек.", value: 9.1 },
          { month: "янв.", value: 8.7 },
          { month: "февр.", value: 9.3 },
          { month: "март", value: 9.0 },
          { month: "апр.", value: 9.5 },
          { month: "май", value: 9.2 },
          { month: "июнь", value: 9.7 },
          { month: "июль", value: 9.4 },
        ],
        tests: [
          { month: "сент.", value: 6.8 },
          { month: "окт.", value: 7.5 },
          { month: "нояб.", value: 8.0 },
          { month: "дек.", value: 8.5 },
          { month: "янв.", value: 8.2 },
          { month: "февр.", value: 8.8 },
          { month: "март", value: 8.6 },
          { month: "апр.", value: 9.0 },
          { month: "май", value: 8.9 },
          { month: "июнь", value: 9.2 },
          { month: "июль", value: 9.1 },
        ],
        dtm: [
          { month: "сент.", value: 25 },
          { month: "окт.", value: 22 },
          { month: "нояб.", value: 28 },
          { month: "дек.", value: 25 },
          { month: "янв.", value: 20 },
          { month: "февр.", value: 28 },
          { month: "март", value: 25 },
          { month: "апр.", value: 22 },
          { month: "май", value: 28 },
          { month: "июнь", value: 25 },
          { month: "июль", value: 22 },
        ],
      },
      biology: {
        current_grades: [
          { month: "сент.", value: 6.8 },
          { month: "окт.", value: 7.3 },
          { month: "нояб.", value: 7.9 },
          { month: "дек.", value: 8.2 },
          { month: "янв.", value: 8.0 },
          { month: "февр.", value: 8.5 },
          { month: "март", value: 8.3 },
          { month: "апр.", value: 8.7 },
          { month: "май", value: 8.9 },
          { month: "июнь", value: 9.1 },
          { month: "июль", value: 8.8 },
        ],
        tests: [
          { month: "сент.", value: 6.2 },
          { month: "окт.", value: 6.8 },
          { month: "нояб.", value: 7.2 },
          { month: "дек.", value: 7.7 },
          { month: "янв.", value: 7.5 },
          { month: "февр.", value: 8.1 },
          { month: "март", value: 7.9 },
          { month: "апр.", value: 8.3 },
          { month: "май", value: 8.5 },
          { month: "июнь", value: 8.8 },
          { month: "июль", value: 8.6 },
        ],
        dtm: [
          { month: "сент.", value: 25 },
          { month: "окт.", value: 22 },
          { month: "нояб.", value: 28 },
          { month: "дек.", value: 25 },
          { month: "янв.", value: 28 },
          { month: "февр.", value: 25 },
          { month: "март", value: 28 },
          { month: "апр.", value: 25 },
          { month: "май", value: 22 },
          { month: "июнь", value: 28 },
          { month: "июль", value: 22 },
        ],
      },
    },

    // Данные всех студентов для турнирных таблиц
    allStudents: [
      {
        id: 1,
        name: "Иванов Алексей Игоревич",
        group: 3,
        chemistry: 9.4,
        biology: 8.8,
        chemistryDTM: 22,
        biologyDTM: 22,
        generalDTM: 25,
        lastChemistryDTM: 28,
        lastBiologyDTM: 28,
        lastGeneralDTM: 22,
      },
      {
        id: 2,
        name: "Петрова Мария Сергеевна",
        group: 1,
        chemistry: 9.8,
        biology: 9.5,
        chemistryDTM: 25,
        biologyDTM: 28,
        generalDTM: 22,
        lastChemistryDTM: 22,
        lastBiologyDTM: 25,
        lastGeneralDTM: 28,
      },
      {
        id: 3,
        name: "Сидоров Дмитрий Александрович",
        group: 2,
        chemistry: 9.2,
        biology: 9.0,
        chemistryDTM: 28,
        biologyDTM: 25,
        generalDTM: 28,
        lastChemistryDTM: 25,
        lastBiologyDTM: 22,
        lastGeneralDTM: 25,
      },
      {
        id: 4,
        name: "Козлова Анна Викторовна",
        group: 3,
        chemistry: 8.9,
        biology: 9.2,
        chemistryDTM: 23,
        biologyDTM: 22,
        generalDTM: 21,
        lastChemistryDTM: 20,
        lastBiologyDTM: 28,
        lastGeneralDTM: 28,
      },
      {
        id: 5,
        name: "Николаев Игорь Петрович",
        group: 1,
        chemistry: 9.6,
        biology: 9.3,
        chemistryDTM: 28,
        biologyDTM: 25,
        generalDTM: 27,
        lastChemistryDTM: 25,
        lastBiologyDTM: 22,
        lastGeneralDTM: 24,
      },
      {
        id: 6,
        name: "Морозова Елена Андреевна",
        group: 2,
        chemistry: 8.7,
        biology: 8.5,
        chemistryDTM: 25,
        biologyDTM: 25,
        generalDTM: 28,
        lastChemistryDTM: 22,
        lastBiologyDTM: 22,
        lastGeneralDTM: 25,
      },
      {
        id: 7,
        name: "Федоров Максим Игоревич",
        group: 3,
        chemistry: 8.5,
        biology: 8.3,
        chemistryDTM: 25,
        biologyDTM: 25,
        generalDTM: 28,
        lastChemistryDTM: 22,
        lastBiologyDTM: 22,
        lastGeneralDTM: 25,
      },
      {
        id: 8,
        name: "Волкова София Дмитриевна",
        group: 1,
        chemistry: 9.1,
        biology: 8.9,
        chemistryDTM: 25,
        biologyDTM: 25,
        generalDTM: 28,
        lastChemistryDTM: 22,
        lastBiologyDTM: 22,
        lastGeneralDTM: 25,
      },
      {
        id: 9,
        name: "Орлов Артем Сергеевич",
        group: 2,
        chemistry: 8.3,
        biology: 8.1,
        chemistryDTM: 25,
        biologyDTM: 25,
        generalDTM: 28,
        lastChemistryDTM: 22,
        lastBiologyDTM: 22,
        lastGeneralDTM: 25,
      },
      {
        id: 10,
        name: "Лебедева Ксения Александровна",
        group: 3,
        chemistry: 8.1,
        biology: 7.9,
        chemistryDTM: 25,
        biologyDTM: 25,
        generalDTM: 28,
        lastChemistryDTM: 22,
        lastBiologyDTM: 22,
        lastGeneralDTM: 25,
      },
    ],
  };

  // Получение данных для графика
  const chartData = useMemo(() => {
    return mockData.grades[selectedSubject][selectedMetric];
  }, [selectedSubject, selectedMetric]);

  // Определение максимального значения для оси Y графика
  const maxValue = useMemo(() => {
    if (selectedMetric === "dtm") return 189;
    return 10;
  }, [selectedMetric]);

  // Функция для отрисовки графика
  const renderChart = () => {
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
        <svg width={width} height={height} className="w-full h-auto">
          {/* Сетка */}
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
                {maxValue - (i * maxValue) / 10}
              </text>
            </g>
          ))}

          {chartData.map((_, index) => (
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
                {chartData[index].month}
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
            stroke={selectedSubject === "chemistry" ? "#3e588b" : "#22c55e"}
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
                  fill={selectedSubject === "chemistry" ? "#3e588b" : "#22c55e"}
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

  const TournamentTableSection = ({
    mockData,
    selectedTable,
    setSelectedTable,
  }) => {
    // Функция расчета ДТМ балла
    const calculateDTMScore = (bio, chem, general) => {
      return (bio * 3.1 + chem * 2.1 + general * 1.1).toFixed(1);
    };

    // Вычисление данных для турнирных таблиц
    const tournamentData = useMemo(() => {
      const students = mockData.allStudents;
      const currentStudent = mockData.currentStudent;

      switch (selectedTable) {
        case "all_groups_average": {
          const sorted = [...students].sort((a, b) => {
            const avgA = (a.chemistry + a.biology) / 2;
            const avgB = (b.chemistry + b.biology) / 2;
            return avgB - avgA;
          });
          return sorted.map((student, index) => ({
            ...student,
            rank: index + 1,
            avgScore: ((student.chemistry + student.biology) / 2).toFixed(1),
          }));
        }

        case "my_group_average": {
          const groupStudents = students.filter(
            (s) => s.group === currentStudent.group
          );
          const sorted = [...groupStudents].sort((a, b) => {
            const avgA = (a.chemistry + a.biology) / 2;
            const avgB = (b.chemistry + b.biology) / 2;
            return avgB - avgA;
          });
          return sorted.map((student, index) => ({
            ...student,
            rank: index + 1,
            avgScore: ((student.chemistry + student.biology) / 2).toFixed(1),
          }));
        }

        case "dtm_all_time": {
          const sorted = [...students].sort((a, b) => {
            const scoreA = parseFloat(
              calculateDTMScore(a.biologyDTM, a.chemistryDTM, a.generalDTM)
            );
            const scoreB = parseFloat(
              calculateDTMScore(b.biologyDTM, b.chemistryDTM, b.generalDTM)
            );
            return scoreB - scoreA;
          });
          return sorted.map((student, index) => ({
            ...student,
            rank: index + 1,
            dtmScore: calculateDTMScore(
              student.biologyDTM,
              student.chemistryDTM,
              student.generalDTM
            ),
          }));
        }

        case "dtm_last_month": {
          const sorted = [...students].sort((a, b) => {
            const scoreA = parseFloat(
              calculateDTMScore(
                a.lastBiologyDTM,
                a.lastChemistryDTM,
                a.lastGeneralDTM
              )
            );
            const scoreB = parseFloat(
              calculateDTMScore(
                b.lastBiologyDTM,
                b.lastChemistryDTM,
                b.lastGeneralDTM
              )
            );
            return scoreB - scoreA;
          });
          return sorted.map((student, index) => ({
            ...student,
            rank: index + 1,
            lastDtmScore: calculateDTMScore(
              student.lastBiologyDTM,
              student.lastChemistryDTM,
              student.lastGeneralDTM
            ),
          }));
        }

        default:
          return [];
      }
    }, [selectedTable, mockData.allStudents, mockData.currentStudent]);

    // Функция для отрисовки турнирной таблицы
    const renderTournamentTable = () => {
      const currentStudentId = mockData.currentStudent.id;
      const currentStudentRank =
        tournamentData.findIndex((s) => s.id === currentStudentId) + 1;
      const topThree = tournamentData.slice(0, 3);
      const currentStudentData = tournamentData.find(
        (s) => s.id === currentStudentId
      );

      const getRankIcon = (rank) => {
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
          case "all_groups_average":
          case "my_group_average":
            return ["№", "Ф.И.О.", "Группа", "Биология", "Химия"];
          case "dtm_all_time":
          case "dtm_last_month":
            return [
              "№",
              "Ф.И.О.",
              "Группа",
              "Биология",
              "Химия",
              "Общие",
              "Итого",
            ];
          default:
            return [];
        }
      };

      const renderRow = (student, isCurrentStudent = false) => {
        const rowClass = isCurrentStudent
          ? "bg-primary-50 border-primary-200 border-2"
          : student.rank <= 3
          ? "bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200"
          : "hover:bg-neutral-50";

        return (
          <tr
            key={student.id}
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
                {student.group}
              </span>
            </td>

            {selectedTable.includes("average") ? (
              <>
                <td className="px-6 py-4 text-center font-medium text-neutral-700">
                  {student.biology}
                </td>
                <td className="px-6 py-4 text-center font-medium text-neutral-700">
                  {student.chemistry}
                </td>
              </>
            ) : (
              <>
                <td className="px-6 py-4 text-center font-medium text-neutral-700">
                  {selectedTable === "dtm_all_time"
                    ? student.biologyDTM
                    : student.lastBiologyDTM}
                </td>
                <td className="px-6 py-4 text-center font-medium text-neutral-700">
                  {selectedTable === "dtm_all_time"
                    ? student.chemistryDTM
                    : student.lastChemistryDTM}
                </td>
                <td className="px-6 py-4 text-center font-medium text-neutral-700">
                  {selectedTable === "dtm_all_time"
                    ? student.generalDTM
                    : student.lastGeneralDTM}
                </td>
                <td className="px-6 py-4 text-center">
                  <span className="font-bold text-primary-600 text-lg">
                    {selectedTable === "dtm_all_time"
                      ? student.dtmScore
                      : student.lastDtmScore}
                  </span>
                </td>
              </>
            )}
          </tr>
        );
      };

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
                  renderRow(student, student.id === currentStudentId)
                )}

                {/* Разрыв если текущий студент не в топ 3 */}
                {currentStudentRank > 3 && (
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
          <button
            onClick={() => setSelectedTable("all_groups_average")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 text-sm ${
              selectedTable === "all_groups_average"
                ? "bg-primary-600 text-white shadow-md"
                : "bg-neutral-200 text-neutral-700 hover:bg-neutral-300"
            }`}
          >
            По всем группам (средний балл)
          </button>
          <button
            onClick={() => setSelectedTable("my_group_average")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 text-sm ${
              selectedTable === "my_group_average"
                ? "bg-primary-600 text-white shadow-md"
                : "bg-neutral-200 text-neutral-700 hover:bg-neutral-300"
            }`}
          >
            Внутри моей группы (средний балл)
          </button>
          <button
            onClick={() => setSelectedTable("dtm_all_time")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 text-sm ${
              selectedTable === "dtm_all_time"
                ? "bg-primary-600 text-white shadow-md"
                : "bg-neutral-200 text-neutral-700 hover:bg-neutral-300"
            }`}
          >
            ДТМ за все время (по всем группам)
          </button>
          <button
            onClick={() => setSelectedTable("dtm_last_month")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 text-sm ${
              selectedTable === "dtm_last_month"
                ? "bg-primary-600 text-white shadow-md"
                : "bg-neutral-200 text-neutral-700 hover:bg-neutral-300"
            }`}
          >
            ДТМ за последний месяц (по всем группам)
          </button>
        </div>

        {/* Таблица */}
        {renderTournamentTable()}
      </div>
    );
  };
  return (
    <div className="min-h-screen bg-neutral-50">
      <ParentHeader />

      <div className="pt-20 md:pt-24">
        <div className="container mx-auto px-4 py-8">
          {/* Заголовок */}
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-primary-900 font-primary">
              Статистика
            </h1>
            <p className="text-neutral-600 mt-2">
              Детальная аналитика успеваемости и рейтинги
            </p>
          </div>

          {/* Блок с графиком */}
          <div className="bg-white rounded-xl p-6 shadow-soft mb-8">
            <div className="flex items-center gap-3 mb-6">
              <TrendingUp className="w-6 h-6 text-primary-600" />
              <h2 className="text-2xl font-bold text-neutral-900 font-primary">
                Прогресс
              </h2>
            </div>

            {/* График */}
            {renderChart()}

            {/* Фильтры */}
            <div className="flex flex-wrap items-center gap-4 mt-6">
              {/* Кнопки предметов */}
              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedSubject("chemistry")}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                    selectedSubject === "chemistry"
                      ? "bg-primary-600 text-white shadow-md"
                      : "bg-neutral-200 text-neutral-700 hover:bg-neutral-300"
                  }`}
                >
                  Химия
                </button>
                <button
                  onClick={() => setSelectedSubject("biology")}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                    selectedSubject === "biology"
                      ? "bg-green-600 text-white shadow-md"
                      : "bg-neutral-200 text-neutral-700 hover:bg-neutral-300"
                  }`}
                >
                  Биология
                </button>
              </div>

              {/* Выпадающий список */}
              <div className="relative">
                <select
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value)}
                  className="appearance-none bg-white border border-neutral-300 rounded-lg px-4 py-2 pr-10 text-neutral-700 font-medium hover:border-primary-400 focus:border-primary-600 focus:ring-2 focus:ring-primary-200 transition-colors duration-200"
                >
                  <option value="current_grades">
                    Средние оценки за текущие
                  </option>
                  <option value="tests">Средняя оценка за тесты</option>
                  <option value="dtm">Средняя оценка за ДТМ</option>
                </select>
                <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-500 pointer-events-none" />
              </div>
            </div>
          </div>

          {/* Турнирные таблицы */}
          <TournamentTableSection
            mockData={mockData}
            selectedTable={selectedTable}
            setSelectedTable={setSelectedTable}
          />
        </div>
      </div>
    </div>
  );
};

export default ParentStatistics;
