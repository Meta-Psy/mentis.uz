import React from 'react';
import { GraduationCap, Award, Users, Clock } from 'lucide-react';

const TeacherSection = () => {
  const teachers = [
    {
      id: 1,
      name: "Азиза Каримова",
      specialization: "Преподаватель биологии",
      experience: "8 лет",
      education: "НУУз, к.б.н.",
      achievements: [
        "Подготовила 250+ студентов",
        "Автор методических пособий",
        "Призер олимпиад по биологии"
      ],
      image: "../../../teacher_1.jpg",
      stats: {
        students: "250+",
        years: "8",
        secondary: "96%"
      }
    },
    {
      id: 2,
      name: "Бахтиёр Рахимов",
      specialization: "Преподаватель химии",
      experience: "12 лет",
      education: "ТашГУ, к.х.н.",
      achievements: [
        "Эксперт ДТМ по химии",
        "Победитель конкурса 'Лучший преподаватель'",
        "Автор 15+ научных публикаций"
      ],
      image: "../../../teacher_2.jpg",
      stats: {
        students: "400+",
        years: "12",
        secondary: "98%"
      }
    },
    {
      id: 3,
      name: "Дилором Усманова",
      specialization: "Методист и тьютор",
      experience: "6 лет",
      education: "ТашПМИ, магистр",
      achievements: [
        "Разработчик авторских программ",
        "Специалист по профориентации",
        "Психолог-консультант"
      ],
      image: "../../../teacher_3.jpg",
      stats: {
        students: "180+",
        years: "6",
        secondary: "94%"
      }
    },
    {
      id: 4,
      name: "Фарход Ибрагимов",
      specialization: "Преподаватель химии",
      experience: "10 лет",
      education: "СамГУ, к.х.н.",
      achievements: [
        "Заведующий кафедрой",
        "Международный сертификат",
        "Наставник молодых преподавателей"
      ],
      image: "../../../teacher_4.jpg",
      stats: {
        students: "320+",
        years: "10",
        secondary: "97%"
      }
    }
  ];

  return (
    <section className="py-20 bg-white relative overflow-hidden">
      {/* Декоративные элементы */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-primary-100 rounded-full opacity-60"></div>
      <div className="absolute bottom-20 right-10 w-24 h-24 bg-secondary-200 rounded-full opacity-40"></div>
      
      <div className="container mx-auto px-4">
        {/* Заголовок */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-700 text-sm font-medium mb-6">
            <GraduationCap className="w-4 h-4" />
            НАША КОМАНДА
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-neutral-900 mb-6">
            Преподаватели-эксперты
          </h2>
          <p className="text-xl text-neutral-600 max-w-3xl mx-auto leading-relaxed">
            Команда опытных преподавателей с научными степенями и многолетним опытом 
            подготовки к ДТМ и поступлению в медицинские ВУЗы Узбекистана.
          </p>
        </div>

        {/* Карточки преподавателей */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {teachers.map((teacher) => (
            <div 
              key={teacher.id}
              className="group bg-white shadow-card border border-neutral-200 hover:shadow-card-hover transition-all duration-300 hover:-translate-y-2 overflow-hidden"
            >
              {/* Фото */}
              <div className="relative overflow-hidden">
                <img 
                  src={teacher.image} 
                  alt={teacher.name}
                  className="w-full h-80 object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-neutral-900 via-transparent to-transparent opacity-60"></div>
                
                {/* Статистика на фото */}
                <div className="absolute bottom-4 left-4 right-4">
                  <div className="flex justify-between text-white text-sm">
                    <div className="text-center">
                      <div className="font-bold">{teacher.stats.students}</div>
                      <div className="text-xs opacity-80">студентов</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold">{teacher.stats.years}</div>
                      <div className="text-xs opacity-80">лет опыта</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold">{teacher.stats.secondary}</div>
                      <div className="text-xs opacity-80">успех</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Информация */}
              <div className="p-6">
                <h3 className="text-xl font-bold text-neutral-900 mb-2 font-primary">
                  {teacher.name}
                </h3>
                
                <p className="text-primary-600 font-medium mb-2 font-secondary">
                  {teacher.specialization}
                </p>
                
                <div className="flex items-center gap-2 text-sm text-neutral-600 mb-4">
                  <GraduationCap className="w-4 h-4" />
                  <span>{teacher.education}</span>
                </div>

                {/* Достижения */}
                <div className="space-y-2 mb-6">
                  {teacher.achievements.map((achievement, index) => (
                    <div key={index} className="flex items-center gap-2 text-sm text-neutral-700">
                      <Award className="w-3 h-3 text-primary-500 flex-shrink-0" />
                      <span className="font-secondary">{achievement}</span>
                    </div>
                  ))}
                </div>

                {/* Опыт */}
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 text-neutral-600">
                    <Clock className="w-4 h-4" />
                    <span>Опыт: {teacher.experience}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Статистика команды */}
        <div className="mt-20">
          <div className="bg-gradient-to-r from-primary-600 to-primary-400 p-12 text-white text-center">
            <h3 className="text-3xl font-bold mb-8 font-primary">
              Наша команда в цифрах
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="space-y-2">
                <div className="text-4xl font-bold">15+</div>
                <div className="text-secondary-100">Преподавателей</div>
              </div>
              <div className="space-y-2">
                <div className="text-4xl font-bold">1200+</div>
                <div className="text-secondary-100">Выпускников</div>
              </div>
              <div className="space-y-2">
                <div className="text-4xl font-bold">96%</div>
                <div className="text-secondary-100">Поступлений</div>
              </div>
              <div className="space-y-2">
                <div className="text-4xl font-bold">5</div>
                <div className="text-secondary-100">Лет работы</div>
              </div>
            </div>
          </div>
        </div>

        {/* Присоединиться к команде */}
        <div className="mt-16 text-center">
          <div className="bg-neutral-50 p-8 border border-neutral-200 max-w-2xl mx-auto">
            <Users className="w-12 h-12 text-primary-600 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-neutral-900 mb-4 font-primary">
              Хотите присоединиться к нашей команде?
            </h3>
            <p className="text-neutral-700 mb-6 font-secondary">
              Мы всегда ищем талантливых преподавателей, готовых изменить жизни студентов 
              и помочь им достичь своих целей в медицине.
            </p>
            <button className="btn btn-primary">
              ОТПРАВИТЬ РЕЗЮМЕ
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TeacherSection;