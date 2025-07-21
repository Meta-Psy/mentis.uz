import React, { useState } from 'react';
import { MapPin, Phone, Mail, Clock, Send, MessageCircle, Navigation, Calendar } from 'lucide-react';

const ContactSection = () => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    subject: '',
    message: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Здесь будет логика отправки формы
    console.log('Form submitted:', formData);
  };

  const contactInfo = [
    {
      icon: <MapPin className="w-6 h-6" />,
      title: "Адрес центра",
      details: [
        "г. Ташкент, ул. Мустакиллик, 45",
        "2 этаж, офис 201",
        "Рядом с метро 'Мустакиллик майдони'"
      ],
      color: "from-primary-500 to-primary-600"
    },
    {
      icon: <Phone className="w-6 h-6" />,
      title: "Телефон",
      details: [
        "+998 90 123-45-67",
        "+998 91 234-56-78",
        "Звонки принимаются с 9:00 до 19:00"
      ],
      color: "from-secondary-500 to-secondary-600"
    },
    {
      icon: <MessageCircle className="w-6 h-6" />,
      title: "Telegram",
      details: [
        "@medprep_uz",
        "@medprep_support",
        "Быстрые ответы 24/7"
      ],
      color: "from-primary-500 to-primary-600"
    },
    {
      icon: <Mail className="w-6 h-6" />,
      title: "Email",
      details: [
        "info@medprep.uz",
        "support@medprep.uz",
        "admissions@medprep.uz"
      ],
      color: "from-secondary-400 to-secondary-500"
    }
  ];

  const workingHours = [
    { day: "Понедельник - Пятница", hours: "9:00 - 19:00" },
    { day: "Суббота", hours: "9:00 - 15:00" },
    { day: "Воскресенье", hours: "Выходной" }
  ];

  const subjects = [
    "Общая консультация",
    "Запись на курс биологии",
    "Запись на курс химии", 
    "Комплексная подготовка",
    "Вопросы по оплате",
    "Техническая поддержка",
    "Партнерство",
    "Другое"
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-neutral-50 to-primary-50 relative overflow-hidden">
      {/* Декоративные элементы */}
      <div className="absolute top-20 right-10 w-32 h-32 bg-secondary-200 rounded-full opacity-30"></div>
      <div className="absolute bottom-20 left-10 w-24 h-24 bg-primary-200 rounded-full opacity-40"></div>
      
      <div className="container mx-auto px-4">
        {/* Заголовок */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-medium mb-6">
            <MessageCircle className="w-4 h-4" />
            СВЯЖИТЕСЬ С НАМИ
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-neutral-900 mb-6">
            Начните свой путь к мечте
          </h2>
          <p className="text-xl text-neutral-600 max-w-3xl mx-auto leading-relaxed">
            Готовы начать подготовку к поступлению в медицинский ВУЗ? Свяжитесь с нами 
            для бесплатной консультации и выбора оптимальной программы обучения.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 max-w-7xl mx-auto">
          {/* Форма обратной связи */}
          <div className="bg-white rounded-3xl p-8 shadow-xl border border-neutral-200">
            <div className="mb-8">
              <h3 className="text-2xl font-bold text-neutral-900 mb-4 font-primary">
                Отправьте нам сообщение
              </h3>
              <p className="text-neutral-600 font-secondary">
                Заполните форму ниже, и мы свяжемся с вами в течение 30 минут в рабочее время.
              </p>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-neutral-900 mb-2">
                    Ваше имя *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="Введите ваше имя"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-neutral-900 mb-2">
                    Номер телефона *
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="input"
                    placeholder="+998 90 123-45-67"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-neutral-900 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="input"
                  placeholder="your.email@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-neutral-900 mb-2">
                  Тема обращения
                </label>
                <select
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  className="input"
                >
                  <option value="">Выберите тему</option>
                  {subjects.map((subject, index) => (
                    <option key={index} value={subject}>
                      {subject}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-neutral-900 mb-2">
                  Сообщение
                </label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  rows={4}
                  className="input resize-none"
                  placeholder="Расскажите подробнее о ваших целях и вопросах..."
                ></textarea>
              </div>

              <button
                onClick={handleSubmit}
                className="w-full btn btn-primary btn-lg flex items-center justify-center gap-2 group"
              >
                <Send className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
                ОТПРАВИТЬ СООБЩЕНИЕ
              </button>

              <p className="text-sm text-neutral-500 text-center">
                Нажимая кнопку, вы соглашаетесь с обработкой персональных данных
              </p>
            </div>
          </div>

          {/* Контактная информация */}
          <div className="space-y-8">
            {/* Контактные данные */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {contactInfo.map((contact, index) => (
                <div 
                  key={index}
                  className="bg-white rounded-2xl p-6 shadow-card border border-neutral-200 hover:shadow-card-hover transition-all duration-300 group"
                >
                  <div className={`inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r ${contact.color} rounded-xl text-white mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    {contact.icon}
                  </div>
                  <h3 className="text-lg font-bold text-neutral-900 mb-3 font-primary">
                    {contact.title}
                  </h3>
                  <div className="space-y-1">
                    {contact.details.map((detail, detailIndex) => (
                      <p key={detailIndex} className="text-sm text-neutral-600 font-secondary">
                        {detail}
                      </p>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Время работы */}
            <div className="bg-white rounded-2xl p-6 shadow-card border border-neutral-200">
              <div className="flex items-center gap-3 mb-4">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl text-white">
                  <Clock className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-neutral-900 font-primary">
                  Время работы
                </h3>
              </div>
              <div className="space-y-2">
                {workingHours.map((schedule, index) => (
                  <div key={index} className="flex justify-between items-center py-1">
                    <span className="text-neutral-700 font-secondary">{schedule.day}</span>
                    <span className="text-neutral-900 font-semibold">{schedule.hours}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Быстрые действия */}
            <div className="space-y-4">
              <h3 className="text-xl font-bold text-neutral-900 font-primary">
                Быстрые действия
              </h3>
              <div className="grid grid-cols-1 gap-3">
                <button className="btn btn-primary flex items-center justify-center gap-2 group">
                  <Calendar className="w-5 h-5" />
                  ЗАПИСАТЬСЯ НА КОНСУЛЬТАЦИЮ
                </button>
                <button className="btn btn-primary flex items-center justify-center gap-2 group">
                  <MessageCircle className="w-5 h-5" />
                  НАПИСАТЬ В TELEGRAM
                </button>
                <button className="btn btn-outline flex items-center justify-center gap-2 group">
                  <Navigation className="w-5 h-5" />
                  ПОСТРОИТЬ МАРШРУТ
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Карта */}
        <div className="mt-16">
          <div className="bg-white rounded-3xl p-6 shadow-xl border border-neutral-200">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-neutral-900 font-primary">
                Как нас найти
              </h3>
              <button className="btn btn-outline btn-sm">
                ОТКРЫТЬ В ЯНДЕКС КАРТАХ
              </button>
            </div>
            
            {/* Placeholder для карты */}
            <div className="w-full h-96 bg-neutral-100 rounded-2xl flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-primary-100 to-secondary-100 opacity-50"></div>
              <div className="relative z-10 text-center">
                <MapPin className="w-16 h-16 text-primary-600 mx-auto mb-4" />
                <h4 className="text-xl font-bold text-neutral-900 mb-2">MedPrep Центр</h4>
                <p className="text-neutral-600">ул. Мустакиллик, 45, Ташкент</p>
                <p className="text-sm text-neutral-500 mt-2">
                  Интерактивная карта будет загружена при реальной интеграции
                </p>
              </div>
            </div>
            
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-center gap-2 text-neutral-600">
                <div className="w-2 h-2 bg-secondary-500 rounded-full"></div>
                <span>5 минут от метро "Мустакиллик майдони"</span>
              </div>
              <div className="flex items-center gap-2 text-neutral-600">
                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span>Бесплатная парковка во дворе</span>
              </div>
              <div className="flex items-center gap-2 text-neutral-600">
                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span>Остановка автобуса "Медицинский центр"</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;