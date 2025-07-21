import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Home, BarChart3, BookOpen, FileText, User, LogOut } from 'lucide-react';

const StudentNavigation = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Главная', href: '/student', icon: Home },
    { name: 'Успеваемость', href: '/student/performance', icon: BarChart3 },
    { name: 'Материалы', href: '/student/materials', icon: BookOpen },
    { name: 'Тесты', href: '/student/tests', icon: FileText },
  ];

  const isActive = (href) => {
    if (href === '/student') {
      return location.pathname === href;
    }
    return location.pathname.startsWith(href);
  };

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="container">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/student" className="flex items-center space-x-3 py-4">
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-500 rounded-xl flex items-center justify-center">
              <User className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-lg text-gray-900">Студент</h2>
              <p className="text-xs text-gray-600">Анна Иванова</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const IconComponent = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    isActive(item.href)
                      ? 'bg-green-100 text-green-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <IconComponent className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
              <LogOut className="h-5 w-5" />
            </Link>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden pb-4">
          <div className="flex space-x-1 overflow-x-auto">
            {navigation.map((item) => {
              const IconComponent = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                    isActive(item.href)
                      ? 'bg-green-100 text-green-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <IconComponent className="h-4 w-4" />
                  <span className="text-sm">{item.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default StudentNavigation;