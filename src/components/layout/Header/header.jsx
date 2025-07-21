import React, { useState, useEffect } from 'react';
import { Menu, X, User, ChevronDown } from 'lucide-react';

const Header = () => {
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
      name: 'О нас', 
      href: '#about',
      dropdown: [
        { name: 'Наша история', href: '#history' },
        { name: 'Команда', href: '#team' },
        { name: 'Миссия и ценности', href: '#mission' }
      ]
    },
    { 
      name: 'Курсы', 
      href: '#courses',
      dropdown: [
        { name: 'Биология', href: '#biology' },
        { name: 'Химия', href: '#chemistry' },
        { name: 'Комплексная подготовка', href: '#complex' },
        { name: 'Пробные тесты', href: '#tests' }
      ]
    },
    { name: 'Преподаватели', href: '#teachers' },
    { name: 'Отзывы', href: '#reviews' },
    { name: 'Контакты', href: '#contacts' }
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
          <div className="flex items-center gap-3">
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
          </div>

          {/* Десктопное меню */}
          <nav className="hidden lg:flex items-center space-x-8">
            {navItems.map((item, index) => (
              <div key={index} className="relative group">
                <a
                  href={item.href}
                  className="flex items-center gap-1 nav-link text-neutral-700 hover:text-primary-600 transition-colors duration-200 font-medium"
                >
                  {item.name}
                  {item.dropdown && <ChevronDown className="w-4 h-4" />}
                </a>
                
                {/* Dropdown меню */}
                {item.dropdown && (
                  <div className="dropdown opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    {item.dropdown.map((subItem, subIndex) => (
                      <a
                        key={subIndex}
                        href={subItem.href}
                        className="dropdown-item"
                      >
                        {subItem.name}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>

          {/* Кнопка входа в аккаунт */}
          <div className="hidden md:flex items-center gap-4">
            <button className="btn btn-ghost flex items-center gap-2 text-neutral-700 hover:text-primary-600">
              <User className="w-4 h-4" />
              <span className="font-medium">Войти в аккаунт</span>
            </button>
          </div>

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
              {navItems.map((item, index) => (
                <div key={index}>
                  <a
                    href={item.href}
                    className="block px-4 py-3 text-neutral-700 hover:bg-neutral-50 hover:text-primary-600 transition-colors duration-200 font-medium"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {item.name}
                  </a>
                  
                  {/* Мобильные подпункты */}
                  {item.dropdown && (
                    <div className="pl-6 py-2 space-y-1 bg-neutral-50">
                      {item.dropdown.map((subItem, subIndex) => (
                        <a
                          key={subIndex}
                          href={subItem.href}
                          className="block px-4 py-2 text-sm text-neutral-600 hover:text-primary-600 transition-colors duration-200"
                          onClick={() => setIsMenuOpen(false)}
                        >
                          {subItem.name}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              
              {/* Мобильные кнопки */}
              <div className="px-4 pt-4 space-y-3 border-t border-neutral-200">
                <button 
                  className="w-full btn btn-ghost flex items-center justify-center gap-2"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <User className="w-4 h-4" />
                  Войти в аккаунт
                </button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;