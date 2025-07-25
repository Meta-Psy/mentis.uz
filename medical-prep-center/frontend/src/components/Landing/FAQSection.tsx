import { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle, Clock, MapPin, DollarSign, BookOpen, Users } from 'lucide-react';

const FAQSection = () => {
  const [openItems, setOpenItems] = useState(new Set([0]));

  const toggleItem = (index) => {
    const newOpenItems = new Set(openItems);
    if (newOpenItems.has(index)) {
      newOpenItems.delete(index);
    } else {
      newOpenItems.add(index);
    }
    setOpenItems(newOpenItems);
  };

  const faqs = [
    {
      question: "Нужно ли сдавать вступительные экзамены в ВУЗ после ДТМ?",
      answer: "В большинстве медицинских ВУЗов Узбекистана для поступления достаточно результатов ДТМ. Однако некоторые престижные учебные заведения могут проводить дополнительные внутренние экзамены или собеседования. Мы готовим студентов ко всем форматам испытаний и предоставляем актуальную информацию о требованиях каждого ВУЗа.",
      icon: <BookOpen className="w-5 h-5" />,
      category: "Поступление"
    },
    {
      question: "Можно ли совмещать подготовку в центре с учебой в школе?",
      answer: "Конечно! Наша программа специально разработана для школьников. Занятия проходят 3 раза в неделю в удобное время (после уроков), а домашние задания выполняются на нашей онлайн-платформе в комфортном темпе. Мы учитываем школьное расписание и помогаем правильно распределить нагрузку.",
      icon: <Clock className="w-5 h-5" />,
      category: "Расписание"
    },
    {
      question: "Где проходят занятия?",
      answer: "Основные занятия проходят в нашем центре в Ташкенте (адрес: ул. Мустакиллик, 45). Также доступны онлайн-занятия для студентов из других регионов. Наши аудитории оснащены современным оборудованием, интерактивными досками и лабораторией для практических работ по химии и биологии.",
      icon: <MapPin className="w-5 h-5" />,
      category: "Место"
    },
    {
      question: "Какова стоимость курсов?",
      answer: "Стоимость зависит от выбранной программы: отдельный предмет (химия или биология) - 800,000 сум/месяц, комплексная подготовка по двум предметам - 1,400,000 сум/месяц (скидка 20%). В стоимость входят все материалы, доступ к платформе, тестирования и консультации тьютора. Возможна рассрочка платежа.",
      icon: <DollarSign className="w-5 h-5" />,
      category: "Оплата"
    },
    {
      question: "Сколько студентов в группе?",
      answer: "Мы работаем с малыми группами до 12 человек, что позволяет преподавателю уделить внимание каждому студенту. Это оптимальное количество для эффективного обучения - достаточно для групповых дискуссий и соревновательного момента, но не слишком много для индивидуального подхода.",
      icon: <Users className="w-5 h-5" />,
      category: "Группы"
    },
    {
      question: "Как проходит контроль знаний и что включает отчетность для родителей?",
      answer: "Каждые 2 недели проводится промежуточное тестирование, в конце месяца - полный пробный ДТМ. Родители получают подробный отчет с анализом сильных и слабых сторон, динамикой прогресса, рекомендациями и прогнозом баллов ДТМ. Также доступна онлайн-платформа для отслеживания посещаемости и домашних заданий.",
      icon: <HelpCircle className="w-5 h-5" />,
      category: "Контроль"
    },
    {
      question: "Что включают профориентационные экскурсии?",
      answer: "Мы организуем посещения ведущих медицинских ВУЗов (НУУз, ТашПМИ, СамМИ) и клиник Ташкента. Студенты знакомятся с учебным процессом, лабораториями, встречаются с преподавателями и студентами старших курсов. Также проводим мастер-классы практикующих врачей разных специальностей для осознанного выбора будущей профессии.",
      icon: <MapPin className="w-5 h-5" />,
      category: "Профориентация"
    },
    {
      question: "Какая поддержка предоставляется слабым студентам?",
      answer: "Для студентов с низким начальным уровнем предусмотрены дополнительные консультации с тьютором, индивидуальные занятия по проблемным темам и адаптированные домашние задания. Мы никого не оставляем позади - каждый студент получает необходимую поддержку для достижения своих целей.",
      icon: <Users className="w-5 h-5" />,
      category: "Поддержка"
    }
  ];

  const categories = [...new Set(faqs.map(faq => faq.category))];

  return (
    <section className="py-20 bg-white relative overflow-hidden">
      {/* Декоративные элементы */}
      <div className="absolute top-20 left-10 w-24 h-24 bg-primary-100 rounded-full opacity-60"></div>
      <div className="absolute bottom-20 right-10 w-32 h-32 bg-secondary-200 rounded-full opacity-40"></div>
      <div className="absolute top-1/2 right-1/4 w-16 h-16 bg-primary-200 rounded-full opacity-30"></div>
      
      <div className="container mx-auto px-4">
        {/* Заголовок */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-700 text-sm font-medium mb-6">
            <HelpCircle className="w-4 h-4" />
            ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-neutral-900 mb-6">
            Ответы на ваши вопросы
          </h2>
          <p className="text-xl text-neutral-600 max-w-3xl mx-auto leading-relaxed">
            Собрали самые популярные вопросы от студентов и родителей о процессе обучения, 
            поступлении в медицинские ВУЗы и особенностях нашей программы подготовки.
          </p>
        </div>

        {/* Категории (опционально для навигации) */}
        <div className="hidden md:flex justify-center gap-4 mb-12 flex-wrap">
          {categories.map((category, index) => (
            <div key={index} className="px-4 py-2 bg-neutral-100 text-neutral-700 text-sm font-medium">
              {category}
            </div>
          ))}
        </div>

        {/* FAQ Items */}
        <div className="max-w-4xl mx-auto space-y-4">
          {faqs.map((faq, index) => (
            <div 
              key={index}
              className="bg-neutral-50 border border-neutral-200 overflow-hidden hover:shadow-card transition-all duration-300"
            >
              <button
                onClick={() => toggleItem(index)}
                className="w-full px-6 py-6 text-left flex items-center justify-between hover:bg-neutral-100 transition-colors duration-200"
              >
                <div className="flex items-center gap-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-primary-100 flex items-center justify-center text-primary-600">
                    {faq.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-neutral-900 font-primary">
                    {faq.question}
                  </h3>
                </div>
                <div className="flex-shrink-0 ml-4">
                  {openItems.has(index) ? (
                    <ChevronUp className="w-5 h-5 text-neutral-600" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-neutral-600" />
                  )}
                </div>
              </button>
              
              {openItems.has(index) && (
                <div className="px-6 pb-6 animate-fade-in">
                  <div className="pl-14">
                    <p className="text-neutral-700 leading-relaxed font-secondary">
                      {faq.answer}
                    </p>
                    <div className="mt-4 inline-flex items-center gap-2 px-3 py-1 bg-white text-xs font-medium text-neutral-600 border border-neutral-200">
                      <div className="w-2 h-2 bg-primary-400 "></div>
                      {faq.category}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Дополнительная помощь */}
        <div className="mt-16">
          <div className="bg-gradient-to-r from-primary-50 to-secondary-50 p-8 border border-primary-200 text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 text-white mb-6">
              <HelpCircle className="w-8 h-8" />
            </div>
            
            <h3 className="text-2xl font-bold text-neutral-900 mb-4 font-primary">
              Не нашли ответ на свой вопрос?
            </h3>
            
            <p className="text-lg text-neutral-700 mb-8 font-secondary">
              Наши консультанты с радостью ответят на все ваши вопросы и помогут выбрать 
              оптимальную программу подготовки для поступления в медицинский ВУЗ.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4">
              <button className="btn btn-primary btn-lg">
                ЗАДАТЬ ВОПРОС
              </button>
              <button className="btn btn-outline btn-lg">
                ЗАПИСАТЬСЯ НА КОНСУЛЬТАЦИЮ
              </button>
            </div>
          </div>
        </div>

        {/* Контактная информация */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="text-center p-6 bg-white shadow-card border border-neutral-200">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 text-primary-600 mb-4">
              <Clock className="w-6 h-6" />
            </div>
            <h4 className="font-semibold text-neutral-900 mb-2 font-primary">Режим работы</h4>
            <p className="text-sm text-neutral-600 font-secondary">
              Пн-Пт: 9:00-19:00<br />
              Сб: 9:00-15:00<br />
              Вс: выходной
            </p>
          </div>
          
          <div className="text-center p-6 bg-white shadow-card border border-neutral-200">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-secondary-100 text-secondary-600 mb-4">
              <MapPin className="w-6 h-6" />
            </div>
            <h4 className="font-semibold text-neutral-900 mb-2 font-primary">Адрес</h4>
            <p className="text-sm text-neutral-600 font-secondary">
              г. Ташкент<br />
              ул. Мустакиллик, 45<br />
              2 этаж
            </p>
          </div>
          
          <div className="text-center p-6 bg-white shadow-card border border-neutral-200">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 text-primary-600 mb-4">
              <HelpCircle className="w-6 h-6" />
            </div>
            <h4 className="font-semibold text-neutral-900 mb-2 font-primary">Поддержка</h4>
            <p className="text-sm text-neutral-600 font-secondary">
              +998 90 123-45-67<br />
              @medprep_uz<br />
              info@medprep.uz
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FAQSection;