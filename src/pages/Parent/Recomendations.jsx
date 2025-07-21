import React, { useState } from 'react';
import ParentHeader from '../../components/layout/Header/parent_header';
import { Clock, BookOpen, Award, Target, FileText, ChevronRight } from 'lucide-react';

const ParentRecommendations = () => {
  const [activeSection, setActiveSection] = useState('summary');

  const getStatusColor = (status) => {
    switch (status) {
      case 'отлично':
        return 'text-success-600 bg-success-100';
      case 'хорошо':
        return 'text-warning-600 bg-warning-100';
      case 'плохо':
        return 'text-error-600 bg-error-100';
      default:
        return 'text-neutral-600 bg-neutral-100';
    }
  };

  const sections = [
    { 
      id: 'discipline', 
      name: 'Дисциплина', 
      icon: Clock,
      status: 'плохо',
      data: {
        currentState: "В настоящее время наблюдается значительное количество пропусков занятий (10 из 30) и несвоевременная сдача домашних заданий (12 из 30 не сданы). Это негативно влияет на общую успеваемость и создает пробелы в знаниях.",
        goals: "Цель - сократить количество пропусков до минимума (не более 2-3 в месяц) и обеспечить своевременную сдачу всех домашних заданий. Для достижения этой цели рекомендуется установить четкий распорядок дня, создать систему напоминаний и мотивации.",
        recommendations: "Рекомендуется ежедневно контролировать выполнение домашних заданий, установить фиксированное время для занятий, исключить отвлекающие факторы во время учебы. Важно также наладить регулярное общение с преподавателями для отслеживания прогресса."
      }
    },
    { 
      id: 'performance', 
      name: 'Успеваемость', 
      icon: BookOpen,
      status: 'хорошо',
      data: {
        currentState: "По химии показывает отличные результаты с высокими оценками по контрольным работам (10/10). По биологии результаты хорошие, но есть потенциал для улучшения, особенно в области опросов (7/10).",
        goals: "Цель - достичь стабильно высоких результатов по обеим дисциплинам. Для биологии необходимо подтянуть теоретическую подготовку и активность на занятиях. Использовать дополнительные материалы и практические задания.",
        recommendations: "Увеличить время на изучение биологии, использовать интерактивные методы обучения, регулярно повторять пройденный материал. Поддерживать высокий уровень по химии через решение дополнительных задач повышенной сложности."
      }
    },
    { 
      id: 'exams', 
      name: 'Экзамены', 
      icon: Award,
      status: 'отлично',
      data: {
        currentState: "Результаты ежемесячных экзаменов показывают стабильно высокие баллы (160/189). Итоговый контроль пройден на максимальный балл (10/10). Демонстрирует хорошую подготовку к экзаменационным форматам.",
        goals: "Цель - поддержать и улучшить текущий уровень, стремиться к результату 170+ баллов на ежемесячных экзаменах. Сосредоточиться на сложных темах и типах заданий, которые вызывают затруднения.",
        recommendations: "Продолжать регулярную подготовку к экзаменам, увеличить количество решаемых тестовых заданий. Анализировать ошибки и работать над слабыми местами. Практиковать решение заданий в условиях ограниченного времени."
      }
    },
    { 
      id: 'dtm', 
      name: 'ДТМ/Поступление', 
      icon: Target,
      status: 'отлично',
      data: {
        currentState: "Текущий балл составляет 180.1 из 189, что значительно превышает необходимый для поступления балл (151.9). Шанс поступления в желаемый ВУЗ оценивается в 90%, что является отличным показателем.",
        goals: "Цель - стабилизировать результат на уровне 180+ баллов и по возможности приблизиться к максимальному результату. Подготовиться к различным сценариям проведения ДТМ и возможным изменениям в заданиях.",
        recommendations: "Поддерживать текущий уровень подготовки, регулярно решать полные варианты ДТМ. Изучить статистику поступления в желаемый ВУЗ за предыдущие годы. Подготовить запасные варианты ВУЗов для подачи документов."
      }
    }
  ];

  const summaryData = {
    title: "Итоговые рекомендации",
    content: "На основе комплексного анализа успеваемости вашего ребенка можно сделать вывод о хорошем уровне подготовки с отличными перспективами поступления. Основные сильные стороны - высокие результаты по экзаменам и достаточный уровень знаний для успешной сдачи ДТМ. Главная область для улучшения - дисциплина и регулярность занятий. Рекомендуется сосредоточить внимание на формировании устойчивых учебных привычек и поддержании мотивации. При соблюдении рекомендаций по каждому разделу, шансы на поступление в желаемый ВУЗ остаются очень высокими."
  };

  const renderContent = () => {
    if (activeSection === 'summary') {
      return (
        <div className="card card-padding">
          <h2 className="text-2xl font-bold text-neutral-900 mb-6 font-primary flex items-center gap-3">
            <FileText className="w-6 h-6 text-primary-600" />
            {summaryData.title}
          </h2>
          <div className="prose prose-neutral max-w-none">
            <p className="text-neutral-700 leading-relaxed text-lg">
              {summaryData.content}
            </p>
          </div>
        </div>
      );
    }

    const section = sections.find(s => s.id === activeSection);
    if (!section) return null;

    return (
      <div className="card card-padding">
        <div className="flex items-center gap-3 mb-6">
          <section.icon className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl font-bold text-neutral-900 font-primary">{section.name}</h2>
          <span className={`badge ${getStatusColor(section.status)}`}>
            {section.status}
          </span>
        </div>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-3 font-primary">
              Текущая ситуация
            </h3>
            <p className="text-neutral-700 leading-relaxed">
              {section.data.currentState}
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-3 font-primary">
              Цели и инструменты
            </h3>
            <p className="text-neutral-700 leading-relaxed">
              {section.data.goals}
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-3 font-primary">
              Рекомендации
            </h3>
            <p className="text-neutral-700 leading-relaxed">
              {section.data.recommendations}
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <ParentHeader />
      
      <div className="pt-20 md:pt-24">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            
            {/* Левая навигационная колонка */}
            <div className="lg:col-span-1">
              <div className="card p-4 sticky top-28">
                <h3 className="text-lg font-bold text-neutral-900 mb-4 font-primary">
                  Разделы рекомендаций
                </h3>
                
                <nav className="space-y-2">
                  <button
                    onClick={() => setActiveSection('summary')}
                    className={`w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center justify-between ${
                      activeSection === 'summary' 
                        ? 'bg-primary-50 text-primary-700 font-semibold' 
                        : 'text-neutral-700 hover:bg-neutral-50 hover:text-primary-600'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="w-4 h-4" />
                      <span className="font-medium">Итоговые рекомендации</span>
                    </div>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                  
                  {sections.map((section) => {
                    const IconComponent = section.icon;
                    return (
                      <button
                        key={section.id}
                        onClick={() => setActiveSection(section.id)}
                        className={`w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center justify-between ${
                          activeSection === section.id 
                            ? 'bg-primary-50 text-primary-700 font-semibold' 
                            : 'text-neutral-700 hover:bg-neutral-50 hover:text-primary-600'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <IconComponent className="w-4 h-4" />
                          <span className="font-medium">{section.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`badge badge-sm ${getStatusColor(section.status)}`}>
                            {section.status}
                          </span>
                          <ChevronRight className="w-4 h-4" />
                        </div>
                      </button>
                    );
                  })}
                </nav>
              </div>
            </div>

            {/* Правая колонка с контентом */}
            <div className="lg:col-span-3">
              {renderContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParentRecommendations;