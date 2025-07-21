import React, { useState } from "react";
import ParentHeader from "../../components/layout/Header/parent_header";
import {
  ChevronDown,
  ChevronUp,
  Calendar,
  Clock,
  BookOpen,
  Award,
  Target,
  TrendingUp,
} from "lucide-react";
const ParentStatistics = () => {
  const [expandedBlocks, setExpandedBlocks] = useState({
    performance: false,
    discipline: false,
    exams: false,
  });

  const toggleBlock = (blockName) => {
    setExpandedBlocks((prev) => ({
      ...prev,
      [blockName]: !prev[blockName],
    }));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "отлично":
        return "text-success-600 bg-success-100";
      case "хорошо":
        return "text-warning-600 bg-warning-100";
      case "плохо":
        return "text-error-600 bg-error-100";
      default:
        return "text-neutral-600 bg-neutral-100";
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <ParentHeader />

      <div className="pt-20 md:pt-24">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Левая колонка */}
            <div className="lg:col-span-1 space-y-6">
              {/* Фотография ученика */}
              <div className="card card-padding text-center">
                <div className="w-32 h-32 mx-auto mb-4 rounded-full bg-gradient-to-r from-primary-600 to-secondary-400 flex items-center justify-center">
                  <span className="text-4xl text-white font-bold">АИ</span>
                </div>
              </div>

              {/* Информация об ученике */}
              <div className="card card-padding">
                <h3 className="text-xl font-bold text-neutral-900 mb-4 font-primary">
                  Иванов Алексей Игоревич
                </h3>

                <div className="space-y-4">
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
              <div className="card card-padding">
                <h4 className="font-bold text-neutral-900 mb-4 font-primary text-lg">
                  ДТМ
                </h4>

                <div className="space-y-3">
                  <div>
                    <span className="text-sm text-neutral-600">
                      Текущий балл:
                    </span>
                    <div className="text-2xl font-bold text-primary-600 font-primary">
                      180.1
                      <span className="text-sm text-neutral-500">/189</span>
                    </div>
                  </div>

                  <div>
                    <span className="text-sm text-neutral-600">
                      Необходимый балл:
                    </span>
                    <div className="text-2xl font-bold text-secondary-400 font-primary">
                      151.9
                      <span className="text-sm text-neutral-500">/189</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Правая колонка */}
            <div className="lg:col-span-2 space-y-6">
              {/* Блок Успеваемость */}
              <div className="card">
                <div
                  className="card-padding border-b border-neutral-200 cursor-pointer flex items-center justify-between hover:bg-neutral-50 transition-colors duration-200"
                  onClick={() => toggleBlock("performance")}
                >
                  <div className="flex items-center gap-3">
                    <BookOpen className="w-5 h-5 text-primary-600" />
                    <h3 className="text-xl font-bold text-neutral-900 font-primary">
                      Успеваемость
                    </h3>
                    <span className={`badge ${getStatusColor("хорошо")}`}>
                      хорошо
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
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <span className="font-medium text-neutral-900">
                            Химия
                          </span>
                          <span
                            className={`badge ${getStatusColor("отлично")}`}
                          >
                            отлично
                          </span>
                        </div>
                        <div className="ml-4 space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-neutral-700">Опросы:</span>
                            <span className="font-medium text-neutral-900">
                              8 из 10
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-neutral-700">Тесты:</span>
                            <span className="font-medium text-neutral-900">
                              7 из 10
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-neutral-700">
                              Контрольные работы:
                            </span>
                            <span className="font-medium text-neutral-900">
                              10 из 10
                            </span>
                          </div>
                        </div>
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <span className="font-medium text-neutral-900">
                            Биология
                          </span>
                          <span className={`badge ${getStatusColor("хорошо")}`}>
                            хорошо
                          </span>
                        </div>
                        <div className="ml-4 space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-neutral-700">Опросы:</span>
                            <span className="font-medium text-neutral-900">
                              7 из 10
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-neutral-700">Тесты:</span>
                            <span className="font-medium text-neutral-900">
                              8 из 10
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-neutral-700">
                              Контрольные работы:
                            </span>
                            <span className="font-medium text-neutral-900">
                              8 из 10
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <button className="btn btn-primary btn-sm">
                      Подробнее
                    </button>
                  </div>
                )}
              </div>

              {/* Блок Дисциплина */}
              <div className="card">
                <div
                  className="card-padding border-b border-neutral-200 cursor-pointer flex items-center justify-between hover:bg-neutral-50 transition-colors duration-200"
                  onClick={() => toggleBlock("discipline")}
                >
                  <div className="flex items-center gap-3">
                    <Clock className="w-5 h-5 text-primary-600" />
                    <h3 className="text-xl font-bold text-neutral-900 font-primary">
                      Дисциплина
                    </h3>
                    <span className={`badge ${getStatusColor("плохо")}`}>
                      плохо
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
                        <span className="font-medium text-error-600">
                          10 из 30 занятий
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-neutral-700">
                          Не сданные домашние задания
                        </span>
                        <span className="font-medium text-error-600">
                          12 из 30 заданий
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-neutral-700">
                          Не сданные опросы
                        </span>
                        <span className="font-medium text-error-600">
                          15 из 30
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-neutral-700">
                          Замечания от учителя
                        </span>
                        <span className="font-medium text-warning-600">
                          2 замечания
                        </span>
                      </div>
                    </div>

                    <button className="btn btn-primary btn-sm">
                      Подробнее
                    </button>
                  </div>
                )}
              </div>

              {/* Блок Экзамены */}
              <div className="card">
                <div
                  className="card-padding border-b border-neutral-200 cursor-pointer flex items-center justify-between hover:bg-neutral-50 transition-colors duration-200"
                  onClick={() => toggleBlock("exams")}
                >
                  <div className="flex items-center gap-3">
                    <Award className="w-5 h-5 text-primary-600" />
                    <h3 className="text-xl font-bold text-neutral-900 font-primary">
                      Экзамены
                    </h3>
                    <span className={`badge ${getStatusColor("отлично")}`}>
                      отлично
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
                      <div className="flex items-center justify-between">
                        <span className="text-neutral-700">
                          Ежемесячный экзамен (последний)
                        </span>
                        <span className="font-medium text-success-600">
                          160 из 189
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-neutral-700">
                          Итоговый контроль (последний)
                        </span>
                        <span className="font-medium text-success-600">
                          10 из 10 баллов
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-neutral-700">
                          Промежуточный контроль (последний)
                        </span>
                        <span className="font-medium text-neutral-600">
                          не проводились
                        </span>
                      </div>
                    </div>

                    <button className="btn btn-primary btn-sm">
                      Подробнее
                    </button>
                  </div>
                )}
              </div>

              {/* Блок шанс поступления */}
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

                <div className="text-4xl font-bold text-success-600 font-primary mb-4">
                  90%
                </div>

                <div className="progress-bar mb-6">
                  <div
                    className="progress-fill progress-biology"
                    style={{ width: "90%" }}
                  ></div>
                </div>
              </div>

              {/* Кнопка рекомендации */}
              <div className="text-center">
                <a
                  href="/parent"
                  className="btn btn-primary btn-lg items-center gap-2 inline-flex"
                >
                  <TrendingUp className="w-5 h-5" />
                  Рекомендации для вас
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParentStatistics;
