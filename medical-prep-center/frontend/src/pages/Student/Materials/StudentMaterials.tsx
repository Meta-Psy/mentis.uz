import {
  FlaskConical,
  Microscope,
  ChevronDown,
  ChevronUp,
  Download,
  FileText,
  BookOpen,
  Play,
  CheckSquare,
  Video,
  Loader2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { useMaterialsPage } from "../../../hooks/useMaterials";
import type {
  DownloadableFile,
  Topic,
  Section,
} from "../../../services/api/materials";

const StudentMaterials = () => {
  const {
    // Состояние
    uiState,
    currentData,
    selectedModuleData,
    isLoading,
    hasError,

    // Обработчики
    handleSubjectChange,
    handleModuleSelect,
    handleBackToModules,
    handleAllModules,
    handleRefresh,
    toggleSection,
  } = useMaterialsPage();

  // Компонент ошибки
  const ErrorMessage = ({
    error,
    onRetry,
  }: {
    error: string;
    onRetry: () => void;
  }) => (
    <div className="bg-red-50 border border-red-200 p-4 lg:p-6 text-center">
      <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
      <p className="text-red-700 mb-4">{error}</p>
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white hover:bg-red-700 transition-colors duration-200"
      >
        <RefreshCw className="w-4 h-4" />
        Попробовать снова
      </button>
    </div>
  );

  // Компонент загрузки
  const LoadingSpinner = ({
    message = "Загрузка...",
  }: {
    message?: string;
  }) => (
    <div className="flex items-center justify-center p-8 lg:p-12">
      <div className="text-center">
        <Loader2 className="w-8 h-8 text-primary-600 animate-spin mx-auto mb-2" />
        <p className="text-neutral-600">{message}</p>
      </div>
    </div>
  );

  // Компонент файла для скачивания
  const DownloadableFileComponent = ({ file }: { file: DownloadableFile }) => (
    <div className="flex items-center justify-between p-3 lg:p-4 bg-neutral-50 border border-neutral-200 hover:bg-neutral-100 transition-colors duration-200">
      <div className="flex items-center gap-3 flex-1">
        <div className="w-10 h-10 lg:w-12 lg:h-12 bg-primary-100 border-2 border-primary-200 flex items-center justify-center">
          <FileText className="w-5 h-5 lg:w-6 lg:h-6 text-primary-600" />
        </div>
        <div className="flex-1 min-w-0">
          <h5 className="font-semibold text-neutral-900 text-sm lg:text-base truncate">
            {file.title}
          </h5>
          <p className="text-xs lg:text-sm text-neutral-600">
            {file.author} • {file.size} • {file.format}
          </p>
        </div>
      </div>
      <button
        onClick={() => {
          if (file.download_url) {
            window.open(file.download_url, "_blank");
          } else {
            console.log("Скачивание файла:", file.id);
          }
        }}
        className="flex items-center gap-2 px-3 lg:px-4 py-2 bg-primary-600 text-white text-xs lg:text-sm font-medium hover:bg-primary-700 transition-colors duration-200"
      >
        <Download className="w-3 h-3 lg:w-4 lg:h-4" />
        <span className="hidden sm:inline">Скачать</span>
      </button>
    </div>
  );

  // Компонент видеоурока
  const VideoLesson = ({ videoUrl }: { videoUrl: string }) => (
    <div className="bg-neutral-900 aspect-video w-full max-w-md mx-auto lg:mx-0">
      <iframe
        src={videoUrl}
        title="Видеоурок"
        className="w-full h-full"
        frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      ></iframe>
    </div>
  );

  // Компонент темы
  const TopicCard = ({
    topic,
    moduleId,
  }: {
    topic: Topic;
    moduleId: number;
  }) => {
    const sectionId = `topic-${moduleId}-${topic.id}`;
    const isExpanded = uiState.expandedSections[sectionId];

    return (
      <div className="bg-white border-2 border-neutral-200 mb-4">
        <div
          className="flex items-center justify-between p-4 lg:p-6 cursor-pointer hover:bg-neutral-50 transition-colors duration-200"
          onClick={() => toggleSection(sectionId)}
        >
          <h4 className="font-bold text-neutral-900 text-sm lg:text-base">
            {topic.title}
          </h4>
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-neutral-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-neutral-500" />
          )}
        </div>

        {isExpanded && (
          <div className="border-t border-neutral-200 p-4 lg:p-6 space-y-6">
            {/* Домашнее задание */}
            {topic.homework && topic.homework.length > 0 && (
              <div>
                <h5 className="font-semibold text-neutral-900 mb-3 text-sm lg:text-base">
                  Домашнее задание:
                </h5>
                <ul className="space-y-2">
                  {topic.homework.map((task, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <CheckSquare className="w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm lg:text-base text-neutral-700">
                        Задание {index + 1}: {task}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Видеоурок */}
            <div>
              <h5 className="font-semibold text-neutral-900 mb-3 text-sm lg:text-base flex items-center gap-2">
                <Video className="w-4 h-4 text-primary-600" />
                Видеоурок:
              </h5>
              <VideoLesson videoUrl={topic.videoUrl} />
            </div>

            {/* Кнопка теста */}
            <div className="text-center lg:text-left">
              <button
                onClick={() => {
                  // Исправлено: используем правильный роутинг или обработчик
                  // Вместо прямой ссылки используем обработчик
                  console.log(
                    `Переход к тесту ${topic.testId} для темы ${topic.id}`
                  );
                  // Здесь должна быть логика навигации к тесту
                  window.location.href = `/test/${topic.testId}/training`;
                }}
                className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white font-medium hover:bg-green-700 transition-colors duration-200 text-sm lg:text-base"
              >
                <Play className="w-4 h-4" />
                Пройти тест
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Компонент модуля
  const ModuleContent = ({ module }: { module: Section }) => {
    const booksSectionId = `books-${module.id}`;
    const testBooksSectionId = `testBooks-${module.id}`;

    return (
      <div className="space-y-6">
        {/* Актуальные материалы для обучения */}
        {module.books && module.books.length > 0 && (
          <div className="bg-white border-2 border-neutral-200">
            <div
              className="flex items-center justify-between p-4 lg:p-6 cursor-pointer hover:bg-neutral-50 transition-colors duration-200"
              onClick={() => toggleSection(booksSectionId)}
            >
              <div className="flex items-center gap-3">
                <BookOpen className="w-5 h-5 text-primary-600" />
                <h3 className="font-bold text-neutral-900 text-sm lg:text-base">
                  Актуальные материалы для обучения
                </h3>
                <span className="text-xs text-neutral-500">
                  ({module.books.length})
                </span>
              </div>
              {uiState.expandedSections[booksSectionId] ? (
                <ChevronUp className="w-5 h-5 text-neutral-500" />
              ) : (
                <ChevronDown className="w-5 h-5 text-neutral-500" />
              )}
            </div>

            {uiState.expandedSections[booksSectionId] && (
              <div className="border-t border-neutral-200 p-4 lg:p-6 space-y-3">
                {module.books.map((book) => (
                  <DownloadableFileComponent key={book.id} file={book} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Актуальные сборники тестов */}
        {module.testBooks && module.testBooks.length > 0 && (
          <div className="bg-white border-2 border-neutral-200">
            <div
              className="flex items-center justify-between p-4 lg:p-6 cursor-pointer hover:bg-neutral-50 transition-colors duration-200"
              onClick={() => toggleSection(testBooksSectionId)}
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-green-600" />
                <h3 className="font-bold text-neutral-900 text-sm lg:text-base">
                  Актуальные сборники тестов
                </h3>
                <span className="text-xs text-neutral-500">
                  ({module.testBooks.length})
                </span>
              </div>
              {uiState.expandedSections[testBooksSectionId] ? (
                <ChevronUp className="w-5 h-5 text-neutral-500" />
              ) : (
                <ChevronDown className="w-5 h-5 text-neutral-500" />
              )}
            </div>

            {uiState.expandedSections[testBooksSectionId] && (
              <div className="border-t border-neutral-200 p-4 lg:p-6 space-y-3">
                {module.testBooks.map((book) => (
                  <DownloadableFileComponent key={book.id} file={book} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Темы */}
        {module.topics && module.topics.length > 0 && (
          <div>
            <h3 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
              Темы модуля ({module.topics.length})
            </h3>
            {module.topics.map((topic) => (
              <TopicCard key={topic.id} topic={topic} moduleId={module.id} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-neutral-50 p-4 lg:p-8">
      <div className="container mx-auto">
        {/* Заголовок */}
        <div className="mb-6 lg:mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl lg:text-4xl font-bold text-primary-900 mb-2">
                Материалы
              </h1>
              <p className="text-neutral-600 text-sm lg:text-base">
                Учебные материалы, тесты и видеоуроки для изучения предметов
              </p>
            </div>
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-neutral-200 text-neutral-700 hover:bg-neutral-300 disabled:opacity-50 transition-colors duration-200 text-sm lg:text-base"
            >
              <RefreshCw
                className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`}
              />
              <span className="hidden sm:inline">Обновить</span>
            </button>
          </div>
        </div>

        {/* Выбор предмета */}
        <div className="flex flex-wrap justify-center gap-2 lg:gap-4 mb-6 lg:mb-8">
          <button
            onClick={() => handleSubjectChange("chemistry")}
            disabled={isLoading}
            className={`flex items-center gap-2 px-4 lg:px-6 py-3 font-medium transition-all duration-200 text-sm lg:text-base disabled:opacity-50 ${
              uiState.selectedSubject === "chemistry"
                ? "bg-primary-600 text-white shadow-lg"
                : "bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300"
            }`}
          >
            <FlaskConical className="w-4 h-4 lg:w-5 lg:h-5" />
            Химия
          </button>

          <button
            onClick={() => handleSubjectChange("biology")}
            disabled={isLoading}
            className={`flex items-center gap-2 px-4 lg:px-6 py-3 font-medium transition-all duration-200 text-sm lg:text-base disabled:opacity-50 ${
              uiState.selectedSubject === "biology"
                ? "bg-primary-600 text-white shadow-lg"
                : "bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300"
            }`}
          >
            <Microscope className="w-4 h-4 lg:w-5 lg:h-5" />
            Биология
          </button>
        </div>

        {/* Контент */}
        {hasError && <ErrorMessage error={hasError} onRetry={handleRefresh} />}

        {isLoading && !currentData && (
          <LoadingSpinner message="Загрузка материалов..." />
        )}

        {!isLoading && !hasError && currentData && (
          <>
            {/* Выбор модуля */}
            {!uiState.selectedModule && (
              <div>
                <h2 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
                  Выберите модуль
                </h2>
                {currentData.modules && currentData.modules.length > 0 ? (
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3 lg:gap-4">
                    {currentData.modules.map((module) => (
                      <button
                        key={module.id}
                        onClick={() => handleModuleSelect(module.id)}
                        className="p-4 lg:p-6 bg-white border-2 border-neutral-200 hover:border-primary-400 hover:bg-primary-50 transition-all duration-200 text-center"
                      >
                        <div className="font-bold text-neutral-900 text-sm lg:text-base">
                          {module.name}
                        </div>
                        <div className="text-xs text-neutral-500 mt-1">
                          {module.topics?.length || 0} тем
                        </div>
                      </button>
                    ))}
                    <button
                      onClick={handleAllModules}
                      className="p-4 lg:p-6 bg-secondary-100 border-2 border-secondary-300 hover:border-secondary-400 hover:bg-secondary-200 transition-all duration-200 text-center"
                    >
                      <div className="font-bold text-secondary-700 text-sm lg:text-base">
                        Все модули
                      </div>
                      <div className="text-xs text-secondary-600 mt-1">
                        {currentData.modules.length} модулей
                      </div>
                    </button>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-neutral-600">
                      Модули для этого предмета пока не загружены
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Содержимое выбранного модуля */}
            {uiState.selectedModule &&
              uiState.selectedModule !== "all" &&
              selectedModuleData && (
                <div>
                  <div className="flex items-center gap-4 mb-6 lg:mb-8">
                    <button
                      onClick={handleBackToModules}
                      className="px-4 py-2 bg-neutral-200 text-neutral-700 hover:bg-neutral-300 transition-colors duration-200 text-sm lg:text-base"
                    >
                      ← Назад
                    </button>
                    <h2 className="text-lg lg:text-xl font-bold text-neutral-900">
                      {selectedModuleData.name}
                    </h2>
                    {selectedModuleData.description && (
                      <span className="text-sm text-neutral-600">
                        • {selectedModuleData.description}
                      </span>
                    )}
                  </div>
                  <ModuleContent module={selectedModuleData} />
                </div>
              )}

            {/* Все модули */}
            {uiState.selectedModule === "all" && (
              <div>
                <div className="flex items-center gap-4 mb-6 lg:mb-8">
                  <button
                    onClick={handleBackToModules}
                    className="px-4 py-2 bg-neutral-200 text-neutral-700 hover:bg-neutral-300 transition-colors duration-200 text-sm lg:text-base"
                  >
                    ← Назад
                  </button>
                  <h2 className="text-lg lg:text-xl font-bold text-neutral-900">
                    Все модули •{" "}
                    {uiState.selectedSubject === "chemistry"
                      ? "Химия"
                      : "Биология"}
                  </h2>
                </div>

                {currentData.modules && currentData.modules.length > 0 ? (
                  <div className="space-y-8 lg:space-y-12">
                    {currentData.modules.map((module) => (
                      <div
                        key={module.id}
                        className="border-b border-neutral-200 pb-8 last:border-b-0"
                      >
                        <div className="flex items-center justify-between mb-4 lg:mb-6">
                          <h3 className="text-lg lg:text-xl font-bold text-primary-900">
                            {module.name}
                          </h3>
                          <button
                            onClick={() => handleModuleSelect(module.id)}
                            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                          >
                            Открыть отдельно →
                          </button>
                        </div>
                        <ModuleContent module={module} />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-neutral-600">
                      Модули для этого предмета пока не загружены
                    </p>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Пустое состояние */}
        {!isLoading && !hasError && !currentData && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-neutral-200 rounded-full flex items-center justify-center mx-auto mb-4">
              <BookOpen className="w-8 h-8 text-neutral-400" />
            </div>
            <p className="text-neutral-600 mb-4">Материалы пока не загружены</p>
            <button
              onClick={handleRefresh}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white hover:bg-primary-700 transition-colors duration-200"
            >
              <RefreshCw className="w-4 h-4" />
              Попробовать снова
            </button>
          </div>
        )}

        {/* Индикатор загрузки при обновлении */}
        {isLoading && currentData && (
          <div className="fixed bottom-4 right-4 bg-white border border-neutral-200 shadow-lg p-4 flex items-center gap-2">
            <Loader2 className="w-4 h-4 text-primary-600 animate-spin" />
            <span className="text-sm text-neutral-600">Обновление...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentMaterials;
