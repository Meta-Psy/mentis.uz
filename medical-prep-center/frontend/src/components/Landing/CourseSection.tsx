import React from 'react';
import { FlaskConical, Dna, Users, Clock, BookOpen, ArrowRight } from 'lucide-react';

const CourseSection = () => {
  const courses = [
    {
      id: 1,
      subject: "БИОЛОГИЯ",
      title: "Полный курс подготовки к ДТМ",
      description: "Комплексная подготовка по биологии с углубленным изучением анатомии, физиологии, генетики и экологии. Подготовка к сертификату и внутренним экзаменам медицинских ВУЗов.",
      icon: <Dna className="w-8 h-8" />,
      format: "Групповой",
      duration: "8 месяцев",
      lessons: "96 занятий",
      features: [
        "Ботаника и зоология",
        "Анатомия и физиология человека", 
        "Генетика и селекция",
        "Экология и эволюция",
        "Практические лабораторные работы"
      ],
      color: "from-secondary-500 to-secondary-600",
      bgColor: "bg-secondary-50",
      borderColor: "border-secondary-200"
    },
    {
      id: 2,
      subject: "ХИМИЯ",
      title: "Полный курс подготовки к ДТМ",
      description: "Интенсивный курс химии с акцентом на органическую и неорганическую химию, биохимию и решение сложных задач. Специальная подготовка для медицинских специальностей.",
      icon: <FlaskConical className="w-8 h-8" />,
      format: "Групповой",
      duration: "8 месяцев", 
      lessons: "96 занятий",
      features: [
        "Неорганическая химия",
        "Органическая химия",
        "Биохимия и молекулярная биология",
        "Решение расчетных задач",
        "Лабораторный практикум"
      ],
      color: "from-primary-500 to-primary-600",
      bgColor: "bg-secondary-50",
      borderColor: "border-primary-200"
    }
  ];

  return (
    <section className="py-20 bg-neutral-50">
      <div className="container mx-auto px-4">
        {/* Заголовок секции */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-neutral-900 mb-6">
            Наши курсы
          </h2>
          <p className="text-xl text-neutral-600 max-w-3xl mx-auto leading-relaxed">
            Специализированные программы подготовки к ДТМ по биологии и химии. 
            Каждый курс разработан с учетом требований ведущих медицинских ВУЗов Узбекистана.
          </p>
        </div>

        {/* Курсы */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {courses.map((course) => (
            <div 
              key={course.id}
              className={`${course.bgColor} p-8 border-2 ${course.borderColor} hover:shadow-xl transition-all duration-300 group hover:-translate-y-2`}
            >
              {/* Заголовок курса */}
              <div className="flex items-center gap-4 mb-6">
                <div className={`inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r ${course.color} text-white group-hover:scale-110 transition-transform duration-300`}>
                  {course.icon}
                </div>
                <div>
                  <div className="text-sm font-bold text-neutral-500 mb-1">
                    {course.subject}
                  </div>
                  <h3 className="text-2xl font-bold text-neutral-900 font-primary">
                    {course.title}
                  </h3>
                </div>
              </div>

              {/* Описание */}
              <p className="text-neutral-700 mb-6 leading-relaxed font-secondary">
                {course.description}
              </p>

              {/* Детали курса */}
              <div className="flex flex-wrap gap-4 mb-6">
                <div className="flex items-center gap-2 text-sm text-neutral-600">
                  <Users className="w-4 h-4" />
                  <span className="font-medium">{course.format}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-neutral-600">
                  <Clock className="w-4 h-4" />
                  <span className="font-medium">{course.duration}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-neutral-600">
                  <BookOpen className="w-4 h-4" />
                  <span className="font-medium">{course.lessons}</span>
                </div>
              </div>

              {/* Что изучаем */}
              <div className="mb-8">
                <h4 className="text-lg font-semibold text-neutral-900 mb-4 font-primary">
                  Что изучаем:
                </h4>
                <ul className="space-y-2">
                  {course.features.map((feature, index) => (
                    <li key={index} className="flex items-center gap-3 text-neutral-700 font-secondary">
                      <div className={`w-2 h-2 bg-gradient-to-r ${course.color} rounded-full`}></div>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Кнопка */}
              <button className={`w-full btn bg-gradient-to-r ${course.color} text-white hover:shadow-lg group-hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-2`}>
                <span className="font-semibold">ПОДРОБНЕЕ О КУРСЕ</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
              </button>
            </div>
          ))}
        </div>

        {/* Дополнительная информация */}
        <div className="mt-16 text-center">
          <div className="bg-white p-8 shadow-soft border border-neutral-200 max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-neutral-900 mb-4 font-primary">
              Комбинированный курс
            </h3>
            <p className="text-lg text-neutral-700 mb-6 font-secondary">
              Изучайте биологию и химию вместе со скидкой 20%. Оптимальный вариант 
              для комплексной подготовки к поступлению в медицинские ВУЗы.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="btn btn-primary">
                УЗНАТЬ О КОМБИНИРОВАННОМ КУРСЕ
              </button>
              <button className="btn btn-outline">
                ЗАПИСАТЬСЯ НА КОНСУЛЬТАЦИЮ
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CourseSection;