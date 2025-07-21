import React, { useState, useEffect } from 'react';
import { Menu, X, Home, BarChart3, Target } from 'lucide-react';

const ParentHeader = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { 
      name: 'Главная', 
      href: '/',
      icon: Home
    },
    { 
      name: 'Успеваемость', 
      href: '/parent/statistics',
      icon: BarChart3
    },
    { 
      name: 'Рекомендации', 
      href: '/parent',
      icon: Target
    },
  ];

  return (
    <header 
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/95 backdrop-blur-lg shadow-soft border-b border-neutral-200' 
          : 'bg-transparent'
      }`}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Логотип */}
          <a href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-primary-600 to-secondary-400 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">M</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-neutral-900 font-primary leading-none">
                Mентис
              </span>
              <span className="text-xs text-neutral-600 font-secondary leading-none">
                Путь к медицине
              </span>
            </div>
          </a>

          {/* Десктопное меню */}
          <nav className="hidden lg:flex items-center space-x-8">
            {navItems.map((item, index) => {
              const IconComponent = item.icon;
              return (
                <a
                  key={index}
                  href={item.href}
                  className="flex items-center gap-2 nav-link text-neutral-700 hover:text-primary-600 transition-colors duration-200 font-medium"
                >
                  <IconComponent className="w-4 h-4" />
                  {item.name}
                </a>
              );
            })}
          </nav>

          {/* Мобильное меню кнопка */}
          <button
            className="lg:hidden p-2 rounded-lg hover:bg-neutral-100 transition-colors duration-200"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? (
              <X className="w-6 h-6 text-neutral-700" />
            ) : (
              <Menu className="w-6 h-6 text-neutral-700" />
            )}
          </button>
        </div>

        {/* Мобильное выпадающее меню */}
        {isMenuOpen && (
          <div className="lg:hidden absolute top-full left-0 right-0 bg-white border-b border-neutral-200 shadow-medium animate-slide-down">
            <nav className="py-6 space-y-1">
              {navItems.map((item, index) => {
                const IconComponent = item.icon;
                return (
                  <a
                    key={index}
                    href={item.href}
                    className="flex items-center gap-3 px-4 py-3 text-neutral-700 hover:bg-neutral-50 hover:text-primary-600 transition-colors duration-200 font-medium"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <IconComponent className="w-4 h-4" />
                    {item.name}
                  </a>
                );
              })}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default ParentHeader;