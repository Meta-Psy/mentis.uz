import { Monitor, TrendingUp, MessageSquare, Target, BarChart3, CheckCircle } from 'lucide-react';

const PlatformSection = () => {
  const features = [
    {
      icon: <Target className="w-6 h-6" />,
      title: "Контроль навыков",
      description: "Отслеживание всех необходимых для поступления компетенций",
      gradient: "from-primary-500 to-primary-600"
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Мониторинг прогресса",
      description: "Детальная аналитика успеваемости и посещаемости",
      gradient: "from-secondary-500 to-secondary-600"
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: "Обратная связь",
      description: "Комментарии и персональные рекомендации от наставников",
      gradient: "from-secondary-500 to-secondary-600"
    }
  ];

  const platformScreenshots = [
    {
      title: "Личный кабинет ученика",
      description: "Интуитивный интерфейс для отслеживания своих достижений",
      image: "../../../../platform_1.jpg",
      features: ["Текущий прогресс", "Расписание занятий", "Домашние задания", "Результаты тестов"]
    },
    {
      title: "Аналитика для родителей",
      description: "Подробные отчеты о успехах вашего ребенка",
      image: "../../../../platform_2.jpg", 
      features: ["Ежемесячные отчеты", "Рекомендации", "Связь с преподавателями", "Прогноз поступления"]
    },
    {
      title: "Инструменты преподавателя",
      description: "Профессиональные инструменты для эффективного обучения",
      image: "../../../../platform_3.jpg",
      features: ["Управление группами", "Создание тестов", "Отслеживание прогресса", "Коммуникация"]
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-neutral-50 to-primary-50 relative overflow-hidden">
      {/* Декоративные элементы */}
      <div className="absolute top-20 right-10 w-32 h-32 bg-secondary-200 rounded-full opacity-30"></div>
      <div className="absolute bottom-20 left-10 w-24 h-24 bg-secondary-200 rounded-full opacity-40"></div>
      
      <div className="container mx-auto px-4">
        {/* Заголовок */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-700 text-sm font-primary mb-6 tracking-widest">
            <Monitor className="w-4 h-4" />
            НАША ПЛАТФОРМА
          </div>
          <h2 className="text-4xl md:text-5xl neutral-900 mb-6 tracking-wider">
            Технологии на службе образования
          </h2>
          <p className="text-xl text-neutral-600 max-w-3xl mx-auto leading-relaxed">
            Собственная образовательная платформа для полного контроля учебного процесса, 
            отслеживания прогресса и персонализированного подхода к каждому студенту.
          </p>
        </div>

        {/* Основные возможности */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <div key={index} className="text-center group">
              <div className={`inline-flex items-center justify-center w-16 h-16 bg-[#3e588b] rounded-full text-white mb-6 group-hover:scale-110 transition-transform duration-300`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-neutral-900 mb-3 font-primary">
                {feature.title}
              </h3>
              <p className="text-neutral-600 font-secondary leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Скриншоты платформы */}
        <div className="space-y-16">
          {platformScreenshots.map((screenshot, index) => (
            <div 
              key={index} 
              className={`flex flex-col ${index % 2 === 1 ? 'lg:flex-row-reverse' : 'lg:flex-row'} items-center gap-12`}
            >
              {/* Изображение */}
              <div className="lg:w-1/2">
                <div className="relative group">
                  <div className="absolute -inset-4 bg-gradient-to-r from-primary-600 to-secondary-400 blur-lg opacity-20 group-hover:opacity-30 transition-opacity duration-300"></div>
                  <div className="relative bg-white p-4 shadow-xl">
                    <img 
                      src={screenshot.image} 
                      alt={screenshot.title}
                      className="w-full rounded-lg"
                    />
                  </div>
                </div>
              </div>

              {/* Контент */}
              <div className="lg:w-1/2 space-y-6">
                <div>
                  <h3 className="text-3xl font-bold text-neutral-900 mb-4 font-primary">
                    {screenshot.title}
                  </h3>
                  <p className="text-lg text-neutral-700 leading-relaxed font-secondary">
                    {screenshot.description}
                  </p>
                </div>

                {/* Список возможностей */}
                <div className="space-y-3">
                  {screenshot.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-primary-500 flex-shrink-0" />
                      <span className="text-neutral-700 font-secondary">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Статистика */}
        <div className="mt-20">
          <div className="bg-white p-8 shadow-xl border border-neutral-200">
            <div className="text-center mb-12">
              <h3 className="text-3xl font-bold text-neutral-900 mb-4 font-primary">
                Результаты нашей платформы
              </h3>
              <p className="text-lg text-neutral-600 font-secondary">
                Цифры, которые говорят о качестве нашего подхода
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full text-white mb-4">
                  <BarChart3 className="w-8 h-8" />
                </div>
                <div className="stat-value text-primary-600">94%</div>
                <div className="stat-label">Успешных поступлений</div>
              </div>
              
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full text-white mb-4">
                  <TrendingUp className="w-8 h-8" />
                </div>
                <div className="stat-value text-primary-600">+47%</div>
                <div className="stat-label">Улучшение результатов</div>
              </div>
              
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full text-white mb-4">
                  <Target className="w-8 h-8" />
                </div>
                <div className="stat-value text-primary-600">1200+</div>
                <div className="stat-label">Выпускников</div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-16">
          <button className="btn btn-primary btn-lg px-8 py-4 text-lg font-semibold shadow-lg hover:shadow-xl">
            ПОПРОБОВАТЬ ПЛАТФОРМУ
          </button>
        </div>
      </div>
    </section>
  );
};

export default PlatformSection;