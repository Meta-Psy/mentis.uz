import { Star, Quote, GraduationCap, Heart, Award } from 'lucide-react';

const ReviewSection = () => {
  const reviews = [
    {
      id: 1,
      name: "Алишер Хакимов",
      role: "Студент ТашПМИ",
      avatar: "/api/placeholder/80/80",
      rating: 5,
      text: "Благодаря MedPrep я поступил в медицинский институт с высокими баллами. Преподаватели объясняют сложные темы простыми словами, а платформа помогает отслеживать прогресс. Особенно понравились практические занятия по химии.",
      beforeAfter: "ДТМ: 189.2 → 195.8 баллов",
      subject: "Химия, Биология",
      type: "student"
    },
    {
      id: 2,
      name: "Нигора Абдуллаева",
      role: "Мама студентки",
      avatar: "/api/placeholder/80/80",
      rating: 5,
      text: "Дочь занималась в центре целый год. Нам очень понравился индивидуальный подход - каждый месяц получали подробные отчеты о прогрессе. Преподаватели всегда на связи, отвечают на все вопросы. Дочь поступила в НУУз!",
      beforeAfter: "НУУз - бюджет",
      subject: "Родительский отзыв",
      type: "parent"
    },
    {
      id: 3,
      name: "Фарида Рустамова",
      role: "Студентка СамМИ",
      avatar: "/api/placeholder/80/80",
      rating: 5,
      text: "Курс по биологии просто потрясающий! Азиза Каримова - лучший преподаватель, который мне встречался. Благодаря её методикам я не только сдала ДТМ на высокие баллы, но и полюбила биологию. Теперь учусь на педиатра.",
      beforeAfter: "ДТМ: 178.4 → 192.1 баллов",
      subject: "Биология",
      type: "student"
    },
    {
      id: 4,
      name: "Жамшид Каримов",
      role: "Папа студента",
      avatar: "/api/placeholder/80/80",
      rating: 5,
      text: "Сын занимался 8 месяцев. Что мне больше всего понравилось - это прозрачность процесса. Мы всегда знали, на каком уровне находится ребенок и какие у него шансы на поступление. Профориентационные экскурсии помогли сыну определиться со специальностью.",
      beforeAfter: "ТашПМИ - контракт",
      subject: "Комплексная подготовка",
      type: "parent"
    },
    {
      id: 5,
      name: "Дилноза Турсунова",
      role: "Студентка АндМИ",
      avatar: "/api/placeholder/80/80",
      rating: 5,
      text: "MedPrep изменил мое отношение к учебе. Онлайн-платформа с тестами и домашними заданиями очень удобная. Тьютор помогал во всех вопросах. Экскурсия в больницу окончательно убедила меня стать врачом. Сейчас учусь на 2 курсе хирургии!",
      beforeAfter: "ДТМ: 184.7 → 194.3 баллов",
      subject: "Химия, Биология",
      type: "student"
    },
    {
      id: 6,
      name: "Зухра Ахмедова",
      role: "Мама студента",
      avatar: "/api/placeholder/80/80",
      rating: 5,
      text: "Очень довольна результатом! Сын не только поступил в медицинский, но и стал более организованным и ответственным. Преподаватели научили его правильно планировать время и систематично готовиться. Рекомендую всем родителям!",
      beforeAfter: "НУУз - бюджет",
      subject: "Полная подготовка",
      type: "parent"
    }
  ];

  const stats = [
    { number: "96%", label: "Поступлений в ВУЗы", icon: <GraduationCap className="w-6 h-6" /> },
    { number: "1200+", label: "Довольных студентов", icon: <Heart className="w-6 h-6" /> },
    { number: "4.9", label: "Средний рейтинг", icon: <Star className="w-6 h-6" /> },
    { number: "150+", label: "Бюджетных мест", icon: <Award className="w-6 h-6" /> }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-neutral-50 to-primary-50 relative overflow-hidden">
      {/* Декоративные элементы */}
      <div className="absolute top-10 right-10 w-20 h-20 bg-primary-200 rounded-full opacity-40"></div>
      <div className="absolute bottom-20 left-20 w-32 h-32 bg-secondary-200 rounded-full opacity-30"></div>
      
      <div className="container mx-auto px-4">
        {/* Заголовок */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-secondary-100 text-secondary-700 rounded-full text-sm font-medium mb-6">
            <Quote className="w-4 h-4" />
            ОТЗЫВЫ
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-neutral-900 mb-6">
            Что говорят наши студенты
          </h2>
          <p className="text-xl text-neutral-600 max-w-3xl mx-auto leading-relaxed">
            Истории успеха наших выпускников и отзывы родителей о качестве подготовки 
            и персональном подходе к каждому студенту.
          </p>
        </div>

        {/* Статистика */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-16">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-2xl p-6 shadow-card border border-neutral-200 text-center group hover:shadow-card-hover transition-all duration-300">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl text-white mb-4 group-hover:scale-110 transition-transform duration-300">
                {stat.icon}
              </div>
              <div className="stat-value text-primary-600">{stat.number}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Отзывы */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {reviews.map((review) => (
            <div 
              key={review.id}
              className="bg-white rounded-2xl p-6 shadow-card border border-neutral-200 hover:shadow-card-hover transition-all duration-300 group hover:-translate-y-1"
            >
              {/* Заголовок карточки */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <img 
                    src={review.avatar} 
                    alt={review.name}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  <div>
                    <h3 className="font-bold text-neutral-900 font-primary">{review.name}</h3>
                    <p className="text-sm text-neutral-600 font-secondary">{review.role}</p>
                  </div>
                </div>
                
                {/* Тип отзыва */}
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  review.type === 'student' 
                    ? 'bg-primary-100 text-primary-700' 
                    : 'bg-primary-100 text-primary-700'
                }`}>
                  {review.type === 'student' ? 'Студент' : 'Родитель'}
                </div>
              </div>

              {/* Рейтинг */}
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star 
                    key={i}
                    className={`w-4 h-4 ${
                      i < review.rating ? 'text-accent-400 fill-current' : 'text-neutral-300'
                    }`}
                  />
                ))}
              </div>

              {/* Текст отзыва */}
              <div className="relative mb-4">
                <Quote className="w-6 h-6 text-primary-300 absolute -top-2 -left-1" />
                <p className="text-neutral-700 leading-relaxed pl-6 font-secondary">
                  {review.text}
                </p>
              </div>

              {/* Результат */}
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-secondary-500 rounded-full"></div>
                  <span className="text-neutral-600 font-secondary">Предмет: {review.subject}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  <span className="text-neutral-600 font-secondary">Результат: {review.beforeAfter}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Больше отзывов */}
        <div className="text-center mt-16">
          <div className="bg-white rounded-2xl p-8 shadow-card border border-neutral-200 max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-neutral-900 mb-4 font-primary">
              Хотите поделиться своим опытом?
            </h3>
            <p className="text-neutral-700 mb-6 font-secondary">
              Мы будем рады услышать вашу историю успеха и поделиться ею с будущими студентами.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="btn btn-primary">
                ОСТАВИТЬ ОТЗЫВ
              </button>
              <button className="btn btn-outline">
                ЧИТАТЬ ВСЕ ОТЗЫВЫ
              </button>
            </div>
          </div>
        </div>

        {/* Призыв к действию */}
        <div className="mt-16">
          <div className="bg-gradient-to-r from-primary-600 to-secondary-400 rounded-3xl p-12 text-white text-center">
            <h3 className="text-3xl font-bold mb-4 font-primary">
              Станьте частью нашей истории успеха!
            </h3>
            <p className="text-xl text-secondary-100 mb-8 max-w-2xl mx-auto">
              Присоединяйтесь к 1200+ студентам, которые уже достигли своей мечты 
              поступить в медицинский ВУЗ с нашей помощью.
            </p>
            <button className="btn bg-white text-primary-600 hover:bg-neutral-50 btn-lg px-8 py-4 text-lg">
              ЗАПИСАТЬСЯ НА КУРС
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ReviewSection;