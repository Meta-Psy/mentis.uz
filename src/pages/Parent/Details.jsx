import React, { useState } from 'react';
import ParentHeader from "../../components/layout/Header/parent_header";
import { Calendar, BookOpen, Check, X, Clock, Award, Trophy } from 'lucide-react';

const ParentDetails = () => {
  const [selectedSubject, setSelectedSubject] = useState('chemistry');
  const [activeTab, setActiveTab] = useState('attendance');
  const [selectedModule, setSelectedModule] = useState('all');

  // Данные модулей
  const modules = [
    { id: 'module1', name: 'Модуль I' },
    { id: 'module2', name: 'Модуль II' },
    { id: 'module3', name: 'Модуль III' },
    { id: 'module4', name: 'Модуль IV' },
    { id: 'module5', name: 'Модуль V' },
  ];

  // Данные посещаемости (пример для одного модуля)
  const attendanceData = {
    module1: {
      months: [
        {
          name: 'Сентябрь 2024',
          days: [
            { date: 2, status: 'present', lesson: 'Введение в органическую химию' },
            { date: 4, status: 'late', lesson: 'Углеводороды' },
            { date: 6, status: 'absent', lesson: 'Алканы и их свойства' },
            { date: 9, status: 'present', lesson: 'Алкены и алкины' },
            { date: 11, status: 'present', lesson: 'Ароматические соединения' },
            { date: 13, status: 'exam', lesson: 'Промежуточный контроль' },
            { date: 16, status: 'present', lesson: 'Спирты и фенолы' },
            { date: 18, status: 'late', lesson: 'Альдегиды и кетоны' },
            { date: 20, status: 'present', lesson: 'Карбоновые кислоты' },
            { date: 23, status: 'present', lesson: 'Эфиры и жиры' },
            { date: 25, status: 'future', lesson: 'Углеводы' },
            { date: 27, status: 'holiday', lesson: 'Выходной день' },
            { date: 30, status: 'future', lesson: 'Белки и аминокислоты' },
          ]
        },
        {
          name: 'Октябрь 2024',
          days: [
            { date: 2, status: 'future', lesson: 'Нуклеиновые кислоты' },
            { date: 4, status: 'future', lesson: 'Повторение материала' },
            { date: 7, status: 'exam', lesson: 'Итоговый контроль модуля' },
          ]
        }
      ]
    }
  };

  // Данные успеваемости
  const performanceData = {
    module1: {
      topics: [
        { 
          number: 1, 
          listened: true, 
          firstTry: 8, 
          secondTry: null, 
          average: 8 
        },
        { 
          number: 2, 
          listened: true, 
          firstTry: null, 
          secondTry: 7, 
          average: 7 
        },
        { 
          number: 3, 
          listened: false, 
          firstTry: null, 
          secondTry: null, 
          average: 0 
        },
        { 
          number: 4, 
          listened: true, 
          firstTry: 9, 
          secondTry: null, 
          average: 9 
        },
        { 
          number: 5, 
          listened: true, 
          firstTry: 6, 
          secondTry: 8, 
          average: 7 
        },
      ]
    }
  };

  const getAttendanceStatusStyle = (status) => {
    switch (status) {
      case 'present':
        return 'bg-white border-2 border-success-300 text-neutral-900 shadow-sm hover:shadow-card';
      case 'late':
        return 'bg-white border-2 border-warning-400 text-neutral-900 shadow-sm hover:shadow-card';
      case 'absent':
        return 'bg-white border-2 border-error-300 text-neutral-900 shadow-sm hover:shadow-card';
      case 'exam':
        return 'bg-gradient-to-br from-primary-500 to-primary-600 border-2 border-primary-600 text-white shadow-card hover:shadow-card-hover';
      case 'holiday':
        return 'bg-neutral-200 border-2 border-neutral-300 text-neutral-500';
      case 'future':
        return 'bg-neutral-50 border-2 border-neutral-200 text-neutral-400';
      default:
        return 'bg-neutral-50 border-2 border-neutral-200 text-neutral-400';
    }
  };

  const getAttendanceFlag = (status) => {
    switch (status) {
      case 'present':
        return <div className="w-3 h-3 bg-success-500 rounded-full border border-white shadow-sm"></div>;
      case 'late':
        return <div className="w-3 h-3 bg-warning-500 rounded-full border border-white shadow-sm"></div>;
      case 'absent':
        return <div className="w-3 h-3 bg-error-500 rounded-full border border-white shadow-sm"></div>;
      case 'exam':
        return <Trophy className="w-4 h-4 text-white" />;
      default:
        return null;
    }
  };

  const renderAttendanceCalendar = () => {
    const moduleData = attendanceData[selectedModule] || attendanceData.module1;
    
    return (
      <div className="space-y-8">
        {moduleData.months.map((month, monthIndex) => (
          <div key={monthIndex} className="card card-padding">
            <h4 className="text-xl font-bold text-neutral-900 mb-6 font-primary flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary-600" />
              {month.name}
            </h4>
            
            <div className="grid grid-cols-7 gap-4 max-w-4xl">
              {month.days.map((day, dayIndex) => (
                <div
                  key={dayIndex}
                  className={`relative p-6 rounded-xl transition-all duration-200 cursor-pointer group ${getAttendanceStatusStyle(day.status)}`}
                  title={day.lesson}
                >
                  <div className="text-center">
                    <span className="text-2xl font-bold font-primary">{day.date}</span>
                  </div>
                  
                  {day.status !== 'future' && day.status !== 'holiday' && (
                    <div className="absolute top-3 right-3">
                      {getAttendanceFlag(day.status)}
                    </div>
                  )}
                  
                  {/* Tooltip */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-neutral-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-10 pointer-events-none">
                    {day.lesson}
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-neutral-900"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderPerformanceTable = () => {
    const moduleData = performanceData[selectedModule] || performanceData.module1;
    
    return (
      <div className="card shadow-card">
        <div className="card-padding border-b border-neutral-200 bg-gradient-to-r from-primary-50 to-secondary-50">
          <h4 className="text-xl font-bold text-neutral-900 font-primary flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-primary-600" />
            {modules.find(m => m.id === selectedModule)?.name || 'Все модули'}
          </h4>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-neutral-50 to-neutral-100">
              <tr>
                <th className="px-6 py-4 text-left font-semibold text-neutral-800 font-primary">№ темы</th>
                <th className="px-6 py-4 text-center font-semibold text-neutral-800 font-primary">Прослушана</th>
                <th className="px-6 py-4 text-center font-semibold text-neutral-800 font-primary">1-й опрос</th>
                <th className="px-6 py-4 text-center font-semibold text-neutral-800 font-primary">2-й опрос</th>
                <th className="px-6 py-4 text-center font-semibold text-neutral-800 font-primary">Ср. балл</th>
              </tr>
            </thead>
            <tbody>
              {moduleData.topics.map((topic, index) => (
                <tr key={index} className="border-b border-neutral-200 hover:bg-gradient-to-r hover:from-primary-25 hover:to-secondary-25 transition-all duration-200">
                  <td className="px-6 py-4 font-bold text-lg text-neutral-900 font-primary">{topic.number}</td>
                  <td className="px-6 py-4 text-center">
                    {topic.listened ? (
                      <div className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-success-500 to-success-600 text-white rounded-full font-bold text-lg shadow-sm">
                        П
                      </div>
                    ) : (
                      <div className="inline-flex items-center justify-center w-10 h-10 bg-neutral-200 text-neutral-500 rounded-full shadow-sm">
                        <X className="w-5 h-5" />
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-center">
                    {topic.firstTry !== null ? (
                      <span className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-full font-bold text-lg shadow-sm">
                        {topic.firstTry}
                      </span>
                    ) : (
                      <X className="w-5 h-5 text-neutral-400 mx-auto" />
                    )}
                  </td>
                  <td className="px-6 py-4 text-center">
                    {topic.secondTry !== null ? (
                      <span className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-secondary-400 to-secondary-500 text-white rounded-full font-bold text-lg shadow-sm">
                        {topic.secondTry}
                      </span>
                    ) : (
                      <X className="w-5 h-5 text-neutral-400 mx-auto" />
                    )}
                  </td>
                  <td className="px-6 py-4 text-center font-bold text-xl text-neutral-900 font-primary">
                    {topic.average}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <ParentHeader />
      
      <div className="pt-20 md:pt-24">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          
          {/* Выбор предмета - центрированный */}
          <div className="mb-12 flex justify-center">
            <div className="grid grid-cols-2 gap-6 w-full max-w-md">
              <button
                onClick={() => setSelectedSubject('chemistry')}
                className={`btn btn-lg ${selectedSubject === 'chemistry' ? 'btn-primary' : 'btn-outline'} font-semibold`}
              >
                Химия
              </button>
              <button
                onClick={() => setSelectedSubject('biology')}
                className={`btn btn-lg ${selectedSubject === 'biology' ? 'btn-primary' : 'btn-outline'} font-semibold`}
              >
                Биология
              </button>
            </div>
          </div>

          {/* Активное окно */}
          <div className="card shadow-strong">
            {/* Вкладки посещаемость/успеваемость - полная ширина */}
            <div className="border-b border-neutral-200 bg-gradient-to-r from-neutral-25 to-neutral-50">
              <div className="flex justify-center">
                <div className="flex">
                  <button
                    onClick={() => setActiveTab('attendance')}
                    className={`px-8 py-5 font-semibold transition-all duration-200 border-b-3 ${
                      activeTab === 'attendance'
                        ? 'border-primary-600 text-primary-600 bg-white'
                        : 'border-transparent text-neutral-600 hover:text-primary-600 hover:bg-neutral-50'
                    }`}
                  >
                    <Calendar className="w-5 h-5 inline mr-3" />
                    Посещаемость
                  </button>
                  <button
                    onClick={() => setActiveTab('performance')}
                    className={`px-8 py-5 font-semibold transition-all duration-200 border-b-3 ${
                      activeTab === 'performance'
                        ? 'border-primary-600 text-primary-600 bg-white'
                        : 'border-transparent text-neutral-600 hover:text-primary-600 hover:bg-neutral-50'
                    }`}
                  >
                    <BookOpen className="w-5 h-5 inline mr-3" />
                    Успеваемость
                  </button>
                </div>
              </div>
            </div>

            {/* Выбор модуля - центрированный и равномерно распределенный */}
            <div className="card-padding border-b border-neutral-200 bg-gradient-to-r from-primary-25 to-secondary-25">
              <div className="flex justify-center">
                <div className="flex flex-wrap gap-3 justify-center max-w-4xl">
                  <button
                    onClick={() => setSelectedModule('all')}
                    className={`btn ${selectedModule === 'all' ? 'btn-primary' : 'btn-outline'} font-medium px-6`}
                  >
                    Все модули
                  </button>
                  {modules.map((module) => (
                    <button
                      key={module.id}
                      onClick={() => setSelectedModule(module.id)}
                      className={`btn ${selectedModule === module.id ? 'btn-primary' : 'btn-outline'} font-medium px-6`}
                    >
                      {module.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Контент - полная ширина */}
            <div className="card-padding">
              {activeTab === 'attendance' ? renderAttendanceCalendar() : renderPerformanceTable()}
            </div>
          </div>

          {/* Итоговые оценки - полная ширина и красивое распределение */}
          <div className="mt-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              <div className="card card-padding text-center shadow-card hover:shadow-card-hover transition-all duration-200 bg-gradient-to-br from-primary-50 to-primary-100">
                <div className="flex items-center justify-center gap-3 mb-4">
                  <div className="p-3 bg-primary-600 rounded-full">
                    <Award className="w-6 h-6 text-white" />
                  </div>
                  <span className="font-semibold text-neutral-800 text-lg">ПК (ср. балл)</span>
                </div>
                <div className="text-4xl font-bold text-primary-600 font-primary">10</div>
              </div>
              
              <div className="card card-padding text-center shadow-card hover:shadow-card-hover transition-all duration-200 bg-gradient-to-br from-secondary-50 to-secondary-100">
                <div className="flex items-center justify-center gap-3 mb-4">
                  <div className="p-3 bg-secondary-400 rounded-full">
                    <Award className="w-6 h-6 text-white" />
                  </div>
                  <span className="font-semibold text-neutral-800 text-lg">ИК (ср. балл)</span>
                </div>
                <div className="text-4xl font-bold text-secondary-400 font-primary">9.2</div>
              </div>
              
              <div className="card card-padding text-center shadow-card hover:shadow-card-hover transition-all duration-200 bg-gradient-to-br from-success-50 to-success-100">
                <div className="flex items-center justify-center gap-3 mb-4">
                  <div className="p-3 bg-success-600 rounded-full">
                    <Trophy className="w-6 h-6 text-white" />
                  </div>
                  <span className="font-semibold text-neutral-800 text-lg">Итоговая оценка</span>
                </div>
                <div className="text-4xl font-bold text-success-600 font-primary">9.6</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParentDetails;