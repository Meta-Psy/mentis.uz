import React from 'react';
import { Users, BookOpen, FlaskConical, UserCheck, Building2 } from 'lucide-react';

const AdvantagesSection = () => {
  const advantages = [
    {
      icon: <Users className="w-12 h-12" />,
      title: "ОПЫТНЫЕ ПРЕПОДАВАТЕЛИ",
      description: "Команда экспертов с многолетним опытом подготовки к ДТМ и глубоким знанием медицинских специальностей."
    },
    {
      icon: <BookOpen className="w-12 h-12" />,
      title: "АВТОРСКИЕ ПРОГРАММЫ",
      description: "Собственная платформа с уникальными методиками и персонализированным подходом к каждому ученику."
    },
    {
      icon: <FlaskConical className="w-12 h-12" />,
      title: "УГЛУБЛЕННАЯ ПОДГОТОВКА",
      description: "Интенсивное изучение химии и биологии с акцентом на практические навыки и решение сложных задач."
    },
    {
      icon: <UserCheck className="w-12 h-12" />,
      title: "ИНДИВИДУАЛЬНЫЙ ПОДХОД",
      description: "Персональный тьютор для каждого студента, который отслеживает прогресс и корректирует учебный план."
    },
    {
      icon: <Building2 className="w-12 h-12" />,
      title: "ПРОФОРИЕНТАЦИЯ",
      description: "Экскурсии в ведущие клиники и медицинские ВУЗы Узбекистана для осознанного выбора специальности."
    }
  ];

  return (
    <section className="py-20 bg-primary-600 relative overflow-hidden">
      {/* Декоративные элементы */}
      <div className="absolute top-10 left-10 w-20 h-20 bg-white bg-opacity-10 rounded-full"></div>
      <div className="absolute bottom-20 right-20 w-32 h-32 bg-secondary-200 bg-opacity-20 rounded-full"></div>
      <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-accent-400 bg-opacity-20 rounded-full"></div>
      
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Наши преимущества
          </h2>
          <p className="text-xl text-secondary-100 max-w-3xl mx-auto">
            Комплексный подход к подготовке, который гарантирует успешное поступление 
            в медицинские ВУЗы Узбекистана
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-8">
          {advantages.map((advantage, index) => (
            <div 
              key={index}
              className="group bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 border-opacity-20 hover:bg-opacity-20 transition-all duration-300 hover:-translate-y-2"
            >
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-white bg-opacity-20 rounded-full mb-6 group-hover:bg-accent-400 group-hover:text-white transition-all duration-300">
                  {React.cloneElement(advantage.icon, { 
                    className: "w-10 h-10 text-white group-hover:text-white" 
                  })}
                </div>
                
                <h3 className="text-xl font-bold text-white mb-4 font-primary text-left  tracking-widest">
                  {advantage.title}
                </h3>
                
                <p className="text-secondary-100 leading-relaxed font-secondary text-left  tracking-wide">
                  {advantage.description}
                </p>
              </div>
            </div>
          ))}
        </div>
        
        {/* Центральная карточка "Наша миссия" */}
        <div className="mt-16 max-w-4xl mx-auto">
          <div className="bg-white bg-opacity-15 backdrop-blur-lg rounded-3xl p-12 border border-white border-opacity-30 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-secondary-400 rounded-full mb-6">
              <Building2 className="w-8 h-8 text-white" />
            </div>
            
            <h3 className="text-2xl font-bold text-white mb-4 font-primary tracking-widest">
              НАША МИССИЯ
            </h3>
            
            <p className="text-lg text-secondary-100 leading-relaxed max-w-2xl mx-auto font-secondary tracking-widest">
              Превратить мечту о медицинской карьере в реальность через качественную подготовку, 
              современные методики и персональный подход к каждому студенту. Мы готовим не просто 
              к экзаменам, а к успешной профессиональной деятельности в медицине.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AdvantagesSection;