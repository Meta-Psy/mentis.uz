import React from 'react';
import { 
  FlaskConical, 
  Microscope, 
  Calendar, 
  FileText, 
  Clock, 
  TrendingUp, 
  Book, 
  AlertTriangle,
  Play,
  ArrowRight
} from 'lucide-react';

const StudentProfilePage = () => {
  // Моковые данные студента
  const studentData = {
    name: 'Иванов Алексей Игоревич',
    group: 3,
    chemistryAverage: 8.7,
    biologyAverage: 8.3,
    attendance: 90,
    testsCompleted: 47,
    
    // Последние результаты тестов
    recentTests: [
      {
        id: 1,
        title: 'Тема 23. Органические соединения',
        subject: 'Химия',
        score: 42,
        maxScore: 50,
        timeAgo: '2 дня назад'
      },
      {
        id: 2,
        title: 'Тема 21. Дыхательная система',
        subject: 'Биология',
        score: 38,
        maxScore: 45,
        timeAgo: '5 дней назад'
      },
      {
        id: 3,
        title: 'Тема 22. Неорганическая химия',
        subject: 'Химия',
        score: 44,
        maxScore: 50,
        timeAgo: '1 неделю назад'
      }
    ],

    // Прогресс по модулям
    moduleProgress: {
      chemistry: {
        currentModule: 4,
        completedTopics: 9,
        totalTopics: 12
      },
      biology: {
        currentModule: 3,
        completedTopics: 6,
        totalTopics: 13
      }
    },

    // Домашние задания
    homework: {
      chemistry: {
        topic: 'Тема 41. Алканы',
        tasks: [
          'Методичка: стр 41 - 56 читать',
          'Anki прорешать 100 карточек',
          'Тесты решить'
        ]
      },
      biology: {
        topic: 'Тема 41. Генная инженерия',
        tasks: [
          'Биология 10 кл: стр 67 - 89 читать',
          'Anki прорешать 100 карточек',
          'Тесты решить'
        ]
      }
    },

    // Просроченные тесты
    overdueTests: [
      {
        id: 1,
        module: 3,
        topicNumber: 20,
        title: 'Сердечно-сосудистая система',
        daysOverdue: 3,
        subject: 'Биология'
      },
      {
        id: 2,
        module: 4,
        topicNumber: 24,
        title: 'Окислительно-восстановительные реакции',
        daysOverdue: 1,
        subject: 'Химия'
      }
    ]
  };

  // Компонент статистической карточки
  const StatCard = ({ icon: Icon, value, label, color = 'primary' }) => (
    <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6 text-center hover:shadow-md transition-shadow duration-200">
      <div className={`w-12 h-12 lg:w-16 lg:h-16 mx-auto mb-3 lg:mb-4 bg-${color}-100 border-2 border-${color}-200 flex items-center justify-center`}>
        <Icon className={`w-6 h-6 lg:w-8 lg:h-8 text-${color}-600`} />
      </div>
      <div className="text-xl lg:text-2xl font-bold text-neutral-900 mb-1 lg:mb-2">
        {value}
      </div>
      <div className="text-xs lg:text-sm text-neutral-600 font-medium">
        {label}
      </div>
    </div>
  );

  // Компонент карточки последнего теста
  const RecentTestCard = ({ test }) => (
    <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start gap-3 lg:gap-4">
        <div className={`w-10 h-10 lg:w-12 lg:h-12 border-2 flex items-center justify-center ${
          test.subject === 'Химия' 
            ? 'border-primary-200 bg-primary-100' 
            : 'border-green-200 bg-green-100'
        }`}>
          {test.subject === 'Химия' 
            ? <FlaskConical className="w-5 h-5 lg:w-6 lg:h-6 text-primary-600" />
            : <Microscope className="w-5 h-5 lg:w-6 lg:h-6 text-green-600" />
          }
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-neutral-900 mb-2 text-sm lg:text-base">
            {test.title}
          </h4>
          <div className="flex items-center justify-between text-xs lg:text-sm text-neutral-600">
            <span>{test.subject} • {test.timeAgo}</span>
            <span className="font-bold text-primary-600">
              {test.score}/{test.maxScore}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  // Компонент прогресса модуля
  const ModuleProgressCard = ({ subject, data, icon: Icon, color }) => {
    const percentage = Math.round((data.completedTopics / data.totalTopics) * 100);
    
    return (
      <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className={`w-8 h-8 lg:w-10 lg:h-10 bg-${color}-100 border-2 border-${color}-200 flex items-center justify-center`}>
            <Icon className={`w-4 h-4 lg:w-5 lg:h-5 text-${color}-600`} />
          </div>
          <div>
            <h4 className="font-bold text-neutral-900 text-sm lg:text-base">{subject}</h4>
            <p className="text-xs lg:text-sm text-neutral-600">Модуль {data.currentModule}</p>
          </div>
        </div>
        
        <div className="mb-3">
          <div className="flex justify-between text-xs lg:text-sm text-neutral-600 mb-2">
            <span>{data.completedTopics} из {data.totalTopics} тем завершено</span>
            <span>{percentage}%</span>
          </div>
          <div className="w-full bg-neutral-200 h-2 lg:h-3">
            <div 
              className={`bg-${color}-600 h-full transition-all duration-300`}
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
        </div>
      </div>
    );
  };

  // Компонент домашнего задания
  const HomeworkCard = ({ subject, data, icon: Icon, color }) => (
    <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6 mb-4">
      <div className="flex items-center gap-3 mb-3 lg:mb-4">
        <div className={`w-8 h-8 lg:w-10 lg:h-10 bg-${color}-100 border-2 border-${color}-200 flex items-center justify-center`}>
          <Icon className={`w-4 h-4 lg:w-5 lg:h-5 text-${color}-600`} />
        </div>
        <h4 className="font-bold text-neutral-900 text-sm lg:text-base">{subject}</h4>
      </div>
      
      <h5 className="font-semibold text-neutral-800 mb-3 text-sm lg:text-base">
        {data.topic}
      </h5>
      
      <ul className="space-y-2">
        {data.tasks.map((task, index) => (
          <li key={index} className="flex items-start gap-2 text-xs lg:text-sm text-neutral-700">
            <div className="w-1.5 h-1.5 bg-neutral-400 mt-2 flex-shrink-0"></div>
            {task}
          </li>
        ))}
      </ul>
    </div>
  );

  // Компонент просроченного теста
  const OverdueTestCard = ({ test }) => (
    <div className="bg-red-50 border-2 border-red-200 p-4 mb-3">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
        <div className="flex-1">
          <div className="text-xs text-red-600 font-medium mb-1">
            Модуль {test.module} • Тема {test.topicNumber}
          </div>
          <h5 className="font-semibold text-red-900 mb-2 text-sm">
            {test.title}
          </h5>
          <div className="text-xs text-red-700 mb-3">
            Просрочено на {test.daysOverdue} {test.daysOverdue === 1 ? 'день' : test.daysOverdue < 5 ? 'дня' : 'дней'}
          </div>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-red-600 text-white text-xs font-medium hover:bg-red-700 transition-colors duration-200">
            <Play className="w-3 h-3" />
            Решить тест
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-neutral-50 p-4 lg:p-8">
      <div className="container mx-auto">
        {/* Заголовок */}
        <div className="mb-6 lg:mb-8">
          <h1 className="text-2xl lg:text-3xl font-bold text-primary-900 mb-2">
            Профиль студента
          </h1>
          <p className="text-neutral-600 text-sm lg:text-base">
            {studentData.name} • Группа {studentData.group}
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 lg:gap-8">
          {/* Левая часть - 75% */}
          <div className="xl:col-span-3 space-y-6 lg:space-y-8">
            {/* Статистические карточки */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
              <StatCard 
                icon={FlaskConical}
                value={studentData.chemistryAverage}
                label="Балл химии"
                color="primary"
              />
              <StatCard 
                icon={Microscope}
                value={studentData.biologyAverage}
                label="Балл биологии"
                color="green"
              />
              <StatCard 
                icon={Calendar}
                value={`${studentData.attendance}%`}
                label="Посещаемость"
                color="blue"
              />
              <StatCard 
                icon={FileText}
                value={studentData.testsCompleted}
                label="Решено тестов"
                color="purple"
              />
            </div>

            {/* Последние результаты тестов */}
            <div>
              <h3 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
                Последние результаты тестов
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6 mb-4 lg:mb-6">
                {studentData.recentTests.map((test) => (
                  <RecentTestCard key={test.id} test={test} />
                ))}
              </div>
              <div className="text-center">
                <a
                  href="/students/tests"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium hover:bg-primary-700 transition-colors duration-200 text-sm lg:text-base"
                >
                  Просмотреть все результаты
                  <ArrowRight className="w-4 h-4" />
                </a>
              </div>
            </div>

            {/* Прогресс по блокам */}
            <div>
              <h3 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
                Прогресс по блокам
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
                <ModuleProgressCard 
                  subject="Химия"
                  data={studentData.moduleProgress.chemistry}
                  icon={FlaskConical}
                  color="primary"
                />
                <ModuleProgressCard 
                  subject="Биология"
                  data={studentData.moduleProgress.biology}
                  icon={Microscope}
                  color="green"
                />
              </div>
            </div>
          </div>

          {/* Правая часть - 25% */}
          <div className="xl:col-span-1 space-y-6">
            {/* Предстоящие задания */}
            <div>
              <h3 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
                Предстоящие задания
              </h3>
              
              <HomeworkCard 
                subject="Химия"
                data={studentData.homework.chemistry}
                icon={FlaskConical}
                color="primary"
              />
              
              <HomeworkCard 
                subject="Биология"
                data={studentData.homework.biology}
                icon={Microscope}
                color="green"
              />
            </div>

            {/* Просроченные тесты */}
            {studentData.overdueTests.length > 0 && (
              <div>
                <h4 className="text-base lg:text-lg font-bold text-red-900 mb-4">
                  Просроченные тесты
                </h4>
                {studentData.overdueTests.map((test) => (
                  <OverdueTestCard key={test.id} test={test} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentProfilePage;