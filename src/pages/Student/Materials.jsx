import React, { useState } from 'react';
import { 
  FlaskConical, 
  Microscope, 
  ChevronDown, 
  ChevronUp,
  Download,
  FileText,
  BookOpen,
  Play,
  ExternalLink,
  CheckSquare,
  Video
} from 'lucide-react';

const StudentMaterials = () => {
  const [selectedSubject, setSelectedSubject] = useState('chemistry');
  const [selectedModule, setSelectedModule] = useState(null);
  const [expandedSections, setExpandedSections] = useState({});

  // Моковые данные материалов
  const materialsData = {
    chemistry: {
      modules: [
        {
          id: 1,
          name: 'Модуль 1',
          books: [
            { id: 1, title: 'Общая химия. Основы', author: 'Петров А.И.', size: '15.2 МБ', format: 'PDF' },
            { id: 2, title: 'Неорганическая химия', author: 'Сидоров В.П.', size: '22.8 МБ', format: 'PDF' }
          ],
          testBooks: [
            { id: 1, title: 'Сборник тестов по общей химии', author: 'Иванова М.К.', size: '8.4 МБ', format: 'PDF' },
            { id: 2, title: 'Задачи по неорганической химии', author: 'Козлов Д.А.', size: '12.1 МБ', format: 'PDF' }
          ],
          topics: [
            {
              id: 1,
              title: 'Тема 3. Строение атома',
              homework: [
                'Решить тесты по теме 3',
                'Химия 10 кл. Выучить параграфы 4 - 7',
                'Конспект по строению атома'
              ],
              videoUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
              testId: 103
            },
            {
              id: 2,
              title: 'Тема 4. Периодическая система',
              homework: [
                'Решить тесты по теме 4',
                'Химия 10 кл. Выучить параграфы 8 - 11',
                'Выучить периодическую таблицу'
              ],
              videoUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
              testId: 104
            }
          ]
        },
        {
          id: 2,
          name: 'Модуль 2',
          books: [
            { id: 3, title: 'Органическая химия. Часть 1', author: 'Морозова Л.С.', size: '18.7 МБ', format: 'PDF' }
          ],
          testBooks: [
            { id: 3, title: 'Тесты по органической химии', author: 'Федоров К.Н.', size: '9.8 МБ', format: 'PDF' }
          ],
          topics: [
            {
              id: 3,
              title: 'Тема 5. Углеводороды',
              homework: [
                'Решить тесты по теме 5',
                'Органическая химия. Выучить главы 1 - 3',
                'Написать формулы алканов'
              ],
              videoUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
              testId: 105
            }
          ]
        }
      ]
    },
    biology: {
      modules: [
        {
          id: 1,
          name: 'Модуль 1',
          books: [
            { id: 4, title: 'Общая биология', author: 'Захаров В.Б.', size: '25.3 МБ', format: 'PDF' },
            { id: 5, title: 'Клеточная биология', author: 'Альберт Б.', size: '45.2 МБ', format: 'PDF' }
          ],
          testBooks: [
            { id: 4, title: 'Тесты по цитологии', author: 'Каменский А.А.', size: '7.2 МБ', format: 'PDF' }
          ],
          topics: [
            {
              id: 4,
              title: 'Тема 3. Цитология',
              homework: [
                'Решить тесты по теме 5',
                'Биология 10. Выучить параграфы 6 - 9',
                'Конспект'
              ],
              videoUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
              testId: 203
            }
          ]
        }
      ]
    }
  };

  const toggleSection = (sectionId) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  // Компонент файла для скачивания
  const DownloadableFile = ({ file }) => (
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
      <button className="flex items-center gap-2 px-3 lg:px-4 py-2 bg-primary-600 text-white text-xs lg:text-sm font-medium hover:bg-primary-700 transition-colors duration-200">
        <Download className="w-3 h-3 lg:w-4 lg:h-4" />
        <span className="hidden sm:inline">Скачать</span>
      </button>
    </div>
  );

  // Компонент видеоурока
  const VideoLesson = ({ videoUrl }) => (
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
  const TopicCard = ({ topic, moduleId }) => {
    const sectionId = `topic-${moduleId}-${topic.id}`;
    const isExpanded = expandedSections[sectionId];

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
              <a
                href={`/test/${topic.testId}/training`}
                className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white font-medium hover:bg-green-700 transition-colors duration-200 text-sm lg:text-base"
              >
                <Play className="w-4 h-4" />
                Пройти тест
              </a>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Компонент модуля
  const ModuleContent = ({ module }) => {
    const booksSectionId = `books-${module.id}`;
    const testBooksSectionId = `testBooks-${module.id}`;
    
    return (
      <div className="space-y-6">
        {/* Актуальные материалы для обучения */}
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
            </div>
            {expandedSections[booksSectionId] ? (
              <ChevronUp className="w-5 h-5 text-neutral-500" />
            ) : (
              <ChevronDown className="w-5 h-5 text-neutral-500" />
            )}
          </div>
          
          {expandedSections[booksSectionId] && (
            <div className="border-t border-neutral-200 p-4 lg:p-6 space-y-3">
              {module.books.map((book) => (
                <DownloadableFile key={book.id} file={book} />
              ))}
            </div>
          )}
        </div>

        {/* Актуальные сборники тестов */}
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
            </div>
            {expandedSections[testBooksSectionId] ? (
              <ChevronUp className="w-5 h-5 text-neutral-500" />
            ) : (
              <ChevronDown className="w-5 h-5 text-neutral-500" />
            )}
          </div>
          
          {expandedSections[testBooksSectionId] && (
            <div className="border-t border-neutral-200 p-4 lg:p-6 space-y-3">
              {module.testBooks.map((book) => (
                <DownloadableFile key={book.id} file={book} />
              ))}
            </div>
          )}
        </div>

        {/* Темы */}
        <div>
          <h3 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
            Темы модуля
          </h3>
          {module.topics.map((topic) => (
            <TopicCard key={topic.id} topic={topic} moduleId={module.id} />
          ))}
        </div>
      </div>
    );
  };

  const currentData = materialsData[selectedSubject];
  const selectedModuleData = selectedModule ? currentData.modules.find(m => m.id === selectedModule) : null;

  return (
    <div className="min-h-screen bg-neutral-50 p-4 lg:p-8">
      <div className="container mx-auto">
        {/* Заголовок */}
        <div className="mb-6 lg:mb-8">
          <h1 className="text-2xl lg:text-4xl font-bold text-primary-900 mb-2">
            Материалы
          </h1>
          <p className="text-neutral-600 text-sm lg:text-base">
            Учебные материалы, тесты и видеоуроки для изучения предметов
          </p>
        </div>

        {/* Выбор предмета */}
        <div className="flex flex-wrap justify-center gap-2 lg:gap-4 mb-6 lg:mb-8">
          <button
            onClick={() => {
              setSelectedSubject('chemistry');
              setSelectedModule(null);
            }}
            className={`flex items-center gap-2 px-4 lg:px-6 py-3 font-medium transition-all duration-200 text-sm lg:text-base ${
              selectedSubject === 'chemistry'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
            }`}
          >
            <FlaskConical className="w-4 h-4 lg:w-5 lg:h-5" />
            Химия
          </button>
          
          <button
            onClick={() => {
              setSelectedSubject('biology');
              setSelectedModule(null);
            }}
            className={`flex items-center gap-2 px-4 lg:px-6 py-3 font-medium transition-all duration-200 text-sm lg:text-base ${
              selectedSubject === 'biology'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
            }`}
          >
            <Microscope className="w-4 h-4 lg:w-5 lg:h-5" />
            Биология
          </button>
        </div>

        {/* Выбор модуля */}
        {!selectedModule && (
          <div>
            <h2 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
              Выберите модуль
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3 lg:gap-4">
              {currentData.modules.map((module) => (
                <button
                  key={module.id}
                  onClick={() => setSelectedModule(module.id)}
                  className="p-4 lg:p-6 bg-white border-2 border-neutral-200 hover:border-primary-400 hover:bg-primary-50 transition-all duration-200 text-center"
                >
                  <div className="font-bold text-neutral-900 text-sm lg:text-base">
                    {module.name}
                  </div>
                </button>
              ))}
              <button
                onClick={() => setSelectedModule('all')}
                className="p-4 lg:p-6 bg-secondary-100 border-2 border-secondary-300 hover:border-secondary-400 hover:bg-secondary-200 transition-all duration-200 text-center"
              >
                <div className="font-bold text-secondary-700 text-sm lg:text-base">
                  Все модули
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Содержимое модуля */}
        {selectedModule && selectedModule !== 'all' && selectedModuleData && (
          <div>
            <div className="flex items-center gap-4 mb-6 lg:mb-8">
              <button
                onClick={() => setSelectedModule(null)}
                className="px-4 py-2 bg-neutral-200 text-neutral-700 hover:bg-neutral-300 transition-colors duration-200 text-sm lg:text-base"
              >
                ← Назад
              </button>
              <h2 className="text-lg lg:text-xl font-bold text-neutral-900">
                {selectedModuleData.name}
              </h2>
            </div>
            <ModuleContent module={selectedModuleData} />
          </div>
        )}

        {/* Все модули */}
        {selectedModule === 'all' && (
          <div>
            <div className="flex items-center gap-4 mb-6 lg:mb-8">
              <button
                onClick={() => setSelectedModule(null)}
                className="px-4 py-2 bg-neutral-200 text-neutral-700 hover:bg-neutral-300 transition-colors duration-200 text-sm lg:text-base"
              >
                ← Назад
              </button>
              <h2 className="text-lg lg:text-xl font-bold text-neutral-900">
                Все модули
              </h2>
            </div>
            <div className="space-y-8 lg:space-y-12">
              {currentData.modules.map((module) => (
                <div key={module.id}>
                  <h3 className="text-lg lg:text-xl font-bold text-primary-900 mb-4 lg:mb-6">
                    {module.name}
                  </h3>
                  <ModuleContent module={module} />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentMaterials;