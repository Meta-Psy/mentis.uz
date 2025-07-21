import React from 'react';

const HeroSection = () => {
  return (
    <section className="relative min-h-screen bg-gradient-to-br from-primary-50 to-secondary-100 overflow-hidden">
      {/* Декоративные элементы */}
      <div className="absolute top-20 right-10 w-32 h-32 bg-secondary-200 rounded-full opacity-60"></div>
      <div className="absolute bottom-20 left-10 w-24 h-24 bg-accent-200 rounded-full opacity-40"></div>
      <div className="absolute top-1/2 right-1/4 w-16 h-16 bg-primary-200 rounded-full opacity-30"></div>
      
      <div className="container mx-auto px-4 py-20 flex items-center min-h-screen">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center w-full">
          {/* Левая колонка с текстом */}
          <div className="space-y-8 animate-fade-in">
            {/* Бейдж */}
            <div className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-full text-sm font-medium">
              СОВРЕМЕННЫЙ И ЦЕЛЕУСТРЕМЛЕННЫЙ
            </div>
            
            {/* Заголовок */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-primary-900 leading-tight">
              ПОДГОТОВКА В<br/>
              МЕДИЦИНСКИЕ<br/>
              <span className="text-primary-600">ВУЗЫ</span>
            </h1>
            
            {/* Подзаголовок */}
            <p className="text-lg md:text-xl text-neutral-700 leading-relaxed max-w-xl">
              Мы — первые, кто превращает подготовку к экзаменам в точную и измеримую систему. 
              Мы показываем родителям и ученикам где они сейчас, и описываем ясные шаги к поступлению 
              в "тот самый" ВУЗ из тысячи доступных.
            </p>
            
            {/* Кредиты */}
            <p className="text-sm text-neutral-500">
              Подготовка к ДТМ от{' '}
              <span className="text-primary-600 font-medium">Ментис</span>
            </p>
            
            {/* Кнопка */}
            <div className="pt-4">
              <button className="btn btn-primary btn-lg px-8 py-4 text-lg font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300">
                УЗНАТЬ ПОДРОБНЕЕ
              </button>
            </div>
          </div>
          
          {/* Правая колонка с изображением */}
          <div className="relative animate-slide-up">
            <div className="relative z-10">
              <img 
                src="../../../../hero_section.jpg" 
                alt="Счастливый студент с наушниками" 
                className="w-full max-w-md mx-auto shadow-2xl"
              />
            </div>
            
            {/* Декоративные элементы вокруг изображения */}
            <div className="absolute -top-6 -right-6 w-20 h-20 bg-accent-400 rounded-full opacity-80 animate-bounce" style={{animationDelay: '1s'}}></div>
            <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-secondary-400 rounded-full opacity-70 animate-bounce" style={{animationDelay: '2s'}}></div>
            <div className="absolute top-1/4 -left-8 w-12 h-12 bg-primary-400 rounded-full opacity-60 animate-bounce" style={{animationDelay: '0.5s'}}></div>
          </div>
        </div>
      </div>
      
      {/* Волновой переход к следующей секции */}
      <div className="absolute bottom-0 left-0 w-full">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative block w-full h-16">
          <path d="M985.66,92.83C906.67,72,823.78,31,743.84,14.19c-82.26-17.34-168.06-16.33-250.45.39-57.84,11.73-114,31.07-172,41.86A600.21,600.21,0,0,1,0,27.35V120H1200V95.8C1132.19,118.92,1055.71,111.31,985.66,92.83Z" className="fill-white"></path>
        </svg>
      </div>
    </section>
  );
};

export default HeroSection;