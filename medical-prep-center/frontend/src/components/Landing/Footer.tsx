import { 
  MapPin, 
  Phone, 
  Clock, 
  MessageCircle, 
  Instagram, 
  Facebook, 
  Youtube,
  ArrowUp,
  GraduationCap,
  Award,
  Users
} from 'lucide-react';

const Footer = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const footerSections = [
    {
      title: "Курсы",
      links: [
        { name: "Биология", href: "#biology" },
        { name: "Химия", href: "#chemistry" },
        { name: "Комплексная подготовка", href: "#complex" },
        { name: "Пробные тесты ДТМ", href: "#tests" },
        { name: "Онлайн курсы", href: "#online" }
      ]
    },
    {
      title: "О центре",
      links: [
        { name: "Наша история", href: "#history" },
        { name: "Преподаватели", href: "#teachers" },
        { name: "Методики обучения", href: "#methods" },
        { name: "Партнеры", href: "#partners" },
        { name: "Вакансии", href: "#careers" }
      ]
    },
    {
      title: "Поддержка",
      links: [
        { name: "Часто задаваемые вопросы", href: "#faq" },
        { name: "Техническая поддержка", href: "#support" },
        { name: "Личный кабинет", href: "#account" },
        { name: "Отзывы", href: "#reviews" },
        { name: "Контакты", href: "#contacts" }
      ]
    }
  ];

  const achievements = [
    { icon: <GraduationCap className="w-5 h-5" />, number: "1200+", label: "Выпускников" },
    { icon: <Award className="w-5 h-5" />, number: "96%", label: "Поступлений" },
    { icon: <Users className="w-5 h-5" />, number: "15+", label: "Преподавателей" }
  ];

  return (
    <footer className="bg-gradient-to-br from-neutral-900 to-primary-900 text-white relative overflow-hidden">
      {/* Декоративные элементы */}
      <div className="absolute top-10 right-20 w-32 h-32 bg-secondary-400 bg-opacity-10 rounded-full"></div>
      <div className="absolute bottom-20 left-10 w-24 h-24 bg-primary-400 bg-opacity-10 rounded-full"></div>
      
      <div className="container mx-auto px-4">
        {/* Основной контент футера */}
        <div className="pt-16 pb-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-12">
            {/* Информация о компании */}
            <div className="lg:col-span-1">
              {/* Логотип */}
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-secondary-400 rounded-xl flex items-center justify-center">
                  <span className="text-white font-bold text-xl">M</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-2xl font-bold text-white font-primary leading-none">
                    MedPrep
                  </span>
                  <span className="text-sm text-neutral-300 font-secondary leading-none">
                    Путь к медицине
                  </span>
                </div>
              </div>
              
              <p className="text-neutral-300 leading-relaxed mb-6 font-secondary">
                Первый центр в Узбекистане, который превращает подготовку к ДТМ 
                в точную и измеримую систему для поступления в медицинские ВУЗы.
              </p>

              {/* Достижения */}
              <div className="space-y-3 mb-6">
                {achievements.map((achievement, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-primary-600 flex items-center justify-center">
                      {achievement.icon}
                    </div>
                    <div>
                      <span className="font-bold text-lg">{achievement.number}</span>
                      <span className="text-neutral-300 text-sm ml-2">{achievement.label}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Социальные сети */}
              <div className="flex items-center gap-4">
                <a 
                  href="#" 
                  className="w-10 h-10 bg-white bg-opacity-10 flex items-center justify-center hover:bg-primary-600 transition-colors duration-300"
                >
                  <Instagram className="w-5 h-5" />
                </a>
                <a 
                  href="#" 
                  className="w-10 h-10 bg-white bg-opacity-10 flex items-center justify-center hover:bg-primary-600 transition-colors duration-300"
                >
                  <Facebook className="w-5 h-5" />
                </a>
                <a 
                  href="#" 
                  className="w-10 h-10 bg-white bg-opacity-10 flex items-center justify-center hover:bg-primary-600 transition-colors duration-300"
                >
                  <Youtube className="w-5 h-5" />
                </a>
                <a 
                  href="#" 
                  className="w-10 h-10 bg-white bg-opacity-10 flex items-center justify-center hover:bg-primary-500 transition-colors duration-300"
                >
                  <MessageCircle className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Ссылки */}
            {footerSections.map((section, index) => (
              <div key={index}>
                <h3 className="text-lg font-bold text-white mb-6 font-primary">
                  {section.title}
                </h3>
                <ul className="space-y-3">
                  {section.links.map((link, linkIndex) => (
                    <li key={linkIndex}>
                      <a
                        href={link.href}
                        className="text-neutral-300 hover:text-white transition-colors duration-200 font-secondary"
                      >
                        {link.name}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Контактная информация */}
        <div className="border-t border-white border-opacity-20 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 flex items-center justify-center">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <p className="text-white font-semibold font-primary">Адрес</p>
                <p className="text-neutral-300 text-sm font-secondary">ул. Мустакиллик, 45</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 flex items-center justify-center">
                <Phone className="w-5 h-5" />
              </div>
              <div>
                <p className="text-white font-semibold font-primary">Телефон</p>
                <p className="text-neutral-300 text-sm font-secondary">+998 90 123-45-67</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 flex items-center justify-center">
                <MessageCircle className="w-5 h-5" />
              </div>
              <div>
                <p className="text-white font-semibold font-primary">Telegram</p>
                <p className="text-neutral-300 text-sm font-secondary">@medprep_uz</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 flex items-center justify-center">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <p className="text-white font-semibold font-primary">Режим работы</p>
                <p className="text-neutral-300 text-sm font-secondary">Пн-Пт: 9:00-19:00</p>
              </div>
            </div>
          </div>
        </div>

        {/* Призыв к действию */}
        <div className="border-t border-white border-opacity-20 py-8">
          <div className="bg-gradient-to-r from-primary-600 to-secondary-400 rounded-2xl p-8 text-center">
            <h3 className="text-2xl font-bold text-white mb-4 font-primary">
              Готовы начать путь к мечте?
            </h3>
            <p className="text-secondary-100 mb-6 font-secondary">
              Запишитесь на бесплатную консультацию и узнайте, как поступить в медицинский ВУЗ
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="btn bg-white text-primary-600 hover:bg-neutral-50">
                БЕСПЛАТНАЯ КОНСУЛЬТАЦИЯ
              </button>
              <button className="btn btn-outline border-white text-white hover:bg-white hover:text-primary-600">
                ЗАПИСАТЬСЯ НА КУРС
              </button>
            </div>
          </div>
        </div>

        {/* Нижняя часть */}
        <div className="border-t border-white border-opacity-20 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex flex-wrap items-center gap-6 text-sm text-neutral-400">
              <span>© 2024 MedPrep. Все права защищены.</span>
              <a href="#" className="hover:text-white transition-colors duration-200">
                Политика конфиденциальности
              </a>
              <a href="#" className="hover:text-white transition-colors duration-200">
                Пользовательское соглашение
              </a>
            </div>
            
            <button
              onClick={scrollToTop}
              className="w-10 h-10 bg-primary-600 flex items-center justify-center hover:bg-primary-700 transition-colors duration-300 group"
            >
              <ArrowUp className="w-5 h-5 group-hover:-translate-y-1 transition-transform duration-300" />
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;