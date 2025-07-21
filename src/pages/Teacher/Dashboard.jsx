import React, { useState } from 'react';
import { 
  ChevronDown, 
  ChevronUp, 
  User, 
  Clock, 
  Users, 
  TrendingUp,
  MessageSquare,
  Save
} from 'lucide-react';

const TeacherDashboard = () => {
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [expandedStudents, setExpandedStudents] = useState({});
  const [comments, setComments] = useState({});

  // Моковые данные учителя
  const teacherData = {
    name: 'Петрова Анна Сергеевна',
    subject: 'Биология',
    
    // Расписание групп
    schedule: [
      {
        groupNumber: 1,
        days: ['Пн', 'Ср', 'Пт'],
        startTime: '16:00',
        studentCount: 15
      },
      {
        groupNumber: 3,
        days: ['Вт', 'Чт', 'Сб'],
        startTime: '14:00',
        studentCount: 12
      },
      {
        groupNumber: 6,
        days: ['Пн', 'Ср', 'Пт'],
        startTime: '18:00',
        studentCount: 18
      }
    ],

    // Студенты по группам
    groups: {
      1: [
        {
          id: 1,
          name: 'Иванов Алексей Игоревич',
          photo: '/api/placeholder/40/40',
          unseenTests: 3,
          lastSeen: '2 дня назад',
          averageScore: 8.7,
          dtmScore: 145.2,
          analytics: {
            objects: { value1: 40, value2: 60 },
            motions: { value1: 30, value2: 20, value3: 50 },
            skills: { value1: 10, value2: 30, value3: 60 }
          },
          comment: 'Отличный ученик, но нужно больше внимания к деталям'
        },
        {
          id: 2,
          name: 'Петрова Мария Сергеевна',
          photo: '/api/placeholder/40/40',
          unseenTests: 1,
          lastSeen: '1 день назад',
          averageScore: 9.2,
          dtmScore: 156.8,
          analytics: {
            objects: { value1: 65, value2: 35 },
            motions: { value1: 45, value2: 25, value3: 30 },
            skills: { value1: 20, value2: 40, value3: 40 }
          },
          comment: 'Очень способная ученица, показывает отличные результаты'
        }
      ],
      3: [
        {
          id: 3,
          name: 'Сидоров Дмитрий Александрович',
          photo: '/api/placeholder/40/40',
          unseenTests: 5,
          lastSeen: '4 дня назад',
          averageScore: 7.3,
          dtmScore: 128.5,
          analytics: {
            objects: { value1: 35, value2: 65 },
            motions: { value1: 25, value2: 35, value3: 40 },
            skills: { value1: 15, value2: 25, value3: 60 }
          },
          comment: 'Нужно улучшить посещаемость и активнее участвовать в занятиях'
        }
      ],
      6: [
        {
          id: 4,
          name: 'Козлова Анна Викторовна',
          photo: '/api/placeholder/40/40',
          unseenTests: 0,
          lastSeen: 'сегодня',
          averageScore: 8.9,
          dtmScore: 148.7,
          analytics: {
            objects: { value1: 55, value2: 45 },
            motions: { value1: 40, value2: 30, value3: 30 },
            skills: { value1: 25, value2: 35, value3: 40 }
          },
          comment: 'Стабильно хорошие результаты, продолжать в том же духе'
        }
      ]
    }
  };

  // Инициализация комментариев
  React.useEffect(() => {
    const initialComments = {};
    Object.values(teacherData.groups).flat().forEach(student => {
      initialComments[student.id] = student.comment;
    });
    setComments(initialComments);
  }, []);

  const toggleStudent = (studentId) => {
    setExpandedStudents(prev => ({
      ...prev,
      [studentId]: !prev[studentId]
    }));
  };

  const handleCommentChange = (studentId, newComment) => {
    setComments(prev => ({
      ...prev,
      [studentId]: newComment
    }));
  };

  const saveComment = (studentId) => {
    // Здесь будет отправка на сервер
    console.log(`Saving comment for student ${studentId}:`, comments[studentId]);
    alert('Комментарий сохранен!');
  };

  // Компонент круговой диаграммы
  const CircularChart = ({ data, title, colors }) => {
    const values = Object.values(data);
    const total = values.reduce((sum, val) => sum + val, 0);
    
    let currentAngle = 0;
    const segments = values.map((value, index) => {
      const angle = (value / total) * 360;
      const startAngle = currentAngle;
      currentAngle += angle;
      
      const x1 = 50 + 40 * Math.cos((startAngle * Math.PI) / 180);
      const y1 = 50 + 40 * Math.sin((startAngle * Math.PI) / 180);
      const x2 = 50 + 40 * Math.cos((currentAngle * Math.PI) / 180);
      const y2 = 50 + 40 * Math.sin((currentAngle * Math.PI) / 180);
      
      const largeArcFlag = angle > 180 ? 1 : 0;
      
      return {
        path: `M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`,
        color: colors[index],
        percentage: Math.round((value / total) * 100)
      };
    });

    return (
      <div className="text-center">
        <h5 className="font-semibold text-neutral-900 mb-2 text-sm">{title}</h5>
        <div className="relative w-24 h-24 mx-auto mb-2">
          <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
            {segments.map((segment, index) => (
              <path
                key={index}
                d={segment.path}
                fill={segment.color}
                stroke="white"
                strokeWidth="1"
              />
            ))}
          </svg>
        </div>
        <div className="space-y-1">
          {segments.map((segment, index) => (
            <div key={index} className="flex items-center justify-center gap-2 text-xs">
              <div 
                className="w-3 h-3 rounded" 
                style={{ backgroundColor: segment.color }}
              ></div>
              <span>{segment.percentage}%</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Компонент студента
  const StudentCard = ({ student }) => {
    const isExpanded = expandedStudents[student.id];
    
    return (
      <div className="bg-white border-2 border-neutral-200 mb-4">
        {/* Основная информация */}
        <div 
          className="p-4 lg:p-6 cursor-pointer hover:bg-neutral-50 transition-colors duration-200"
          onClick={() => toggleStudent(student.id)}
        >
          <div className="grid grid-cols-1 lg:grid-cols-7 gap-4 items-center">
            {/* Фотография */}
            <div className="lg:col-span-1 flex justify-center lg:justify-start">
              <div className="w-12 h-12 bg-primary-100 border-2 border-primary-200 flex items-center justify-center">
                <User className="w-6 h-6 text-primary-600" />
              </div>
            </div>
            
            {/* Ф.И.О. */}
            <div className="lg:col-span-2 text-center lg:text-left">
              <h4 className="font-semibold text-neutral-900 text-sm lg:text-base">
                {student.name}
              </h4>
            </div>
            
            {/* Тесты не сдано */}
            <div className="lg:col-span-1 text-center">
              <div className="text-xs text-neutral-600">Не сдано тестов</div>
              <div className={`font-bold text-sm ${student.unseenTests > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {student.unseenTests}
              </div>
            </div>
            
            {/* Последнее посещение */}
            <div className="lg:col-span-1 text-center">
              <div className="text-xs text-neutral-600">Был на платформе</div>
              <div className="font-medium text-sm text-neutral-700">
                {student.lastSeen}
              </div>
            </div>
            
            {/* Средний балл */}
            <div className="lg:col-span-1 text-center">
              <div className="text-xs text-neutral-600">Средний балл</div>
              <div className="font-bold text-sm text-primary-600">
                {student.averageScore}
              </div>
            </div>
            
            {/* ДТМ балл */}
            <div className="lg:col-span-1 text-center flex items-center justify-center lg:justify-between">
              <div>
                <div className="text-xs text-neutral-600">ДТМ балл</div>
                <div className="font-bold text-sm text-green-600">
                  {student.dtmScore}
                </div>
              </div>
              {isExpanded ? (
                <ChevronUp className="w-5 h-5 text-neutral-500 ml-2" />
              ) : (
                <ChevronDown className="w-5 h-5 text-neutral-500 ml-2" />
              )}
            </div>
          </div>
        </div>

        {/* Расширенная информация */}
        {isExpanded && (
          <div className="border-t border-neutral-200 p-4 lg:p-6 bg-neutral-50">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Круговые диаграммы */}
              <div className="lg:col-span-3">
                <h5 className="font-bold text-neutral-900 mb-4">Аналитика успеваемости</h5>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                  <CircularChart 
                    data={student.analytics.objects}
                    title="Objects"
                    colors={['#3e588b', '#96aedd']}
                  />
                  <CircularChart 
                    data={student.analytics.motions}
                    title="Motions"
                    colors={['#22c55e', '#f59e0b', '#ef4444']}
                  />
                  <CircularChart 
                    data={student.analytics.skills}
                    title="Skills"
                    colors={['#8b5cf6', '#06b6d4', '#84cc16']}
                  />
                </div>
              </div>

              {/* Комментарии */}
              <div className="lg:col-span-1">
                <h5 className="font-bold text-neutral-900 mb-4 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Комментарии
                </h5>
                <div className="space-y-3">
                  <textarea
                    value={comments[student.id] || ''}
                    onChange={(e) => handleCommentChange(student.id, e.target.value)}
                    placeholder="Добавьте комментарий об ученике..."
                    className="w-full p-3 border border-neutral-300 text-sm resize-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                    rows={4}
                  />
                  <button
                    onClick={() => saveComment(student.id)}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium hover:bg-primary-700 transition-colors duration-200"
                  >
                    <Save className="w-4 h-4" />
                    Сохранить
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-neutral-50 p-4 lg:p-8">
      <div className="container mx-auto">
        {/* Заголовок */}
        <div className="mb-6 lg:mb-8">
          <h1 className="text-2xl lg:text-3xl font-bold text-primary-900 mb-2">
            Профиль учителя
          </h1>
          <p className="text-neutral-600 text-sm lg:text-base">
            {teacherData.name} • {teacherData.subject}
          </p>
        </div>

        {/* Расписание групп */}
        <div className="bg-white border-2 border-neutral-200 p-4 lg:p-6 mb-6 lg:mb-8">
          <h2 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
            Расписание групп
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-primary-600 text-white">
                <tr>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    Группа
                  </th>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    День 1
                  </th>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    День 2
                  </th>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    День 3
                  </th>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    Время
                  </th>
                  <th className="px-3 lg:px-6 py-3 lg:py-4 text-center font-semibold text-sm lg:text-base">
                    Учеников
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {teacherData.schedule.map((group) => (
                  <tr key={group.groupNumber} className="hover:bg-neutral-50">
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center">
                      <span className="px-3 py-1 bg-primary-100 text-primary-700 font-bold text-sm">
                        {group.groupNumber}
                      </span>
                    </td>
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center font-medium text-sm lg:text-base">
                      {group.days[0]}
                    </td>
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center font-medium text-sm lg:text-base">
                      {group.days[1]}
                    </td>
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center font-medium text-sm lg:text-base">
                      {group.days[2]}
                    </td>
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center font-medium text-sm lg:text-base">
                      {group.startTime}
                    </td>
                    <td className="px-3 lg:px-6 py-3 lg:py-4 text-center">
                      <div className="flex items-center justify-center gap-1">
                        <Users className="w-4 h-4 text-neutral-500" />
                        <span className="font-medium text-sm lg:text-base">{group.studentCount}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Кнопки групп */}
        <div className="flex flex-wrap justify-center gap-2 lg:gap-4 mb-6 lg:mb-8">
          {Object.keys(teacherData.groups).map((groupNumber) => (
            <button
              key={groupNumber}
              onClick={() => setSelectedGroup(selectedGroup === groupNumber ? null : groupNumber)}
              className={`flex items-center gap-2 px-4 lg:px-6 py-3 font-medium transition-all duration-200 text-sm lg:text-base ${
                selectedGroup === groupNumber
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-300'
              }`}
            >
              <Users className="w-4 h-4" />
              Группа {groupNumber}
              <span className={`px-2 py-1 text-xs font-bold rounded ${
                selectedGroup === groupNumber 
                  ? 'bg-white/20 text-white' 
                  : 'bg-primary-100 text-primary-700'
              }`}>
                {teacherData.groups[groupNumber].length}
              </span>
            </button>
          ))}
        </div>

        {/* Список студентов */}
        {selectedGroup && (
          <div>
            <h3 className="text-lg lg:text-xl font-bold text-neutral-900 mb-4 lg:mb-6">
              Студенты группы {selectedGroup}
            </h3>
            <div className="space-y-4">
              {teacherData.groups[selectedGroup]
                .sort((a, b) => b.averageScore - a.averageScore)
                .map((student) => (
                  <StudentCard key={student.id} student={student} />
                ))}
            </div>
          </div>
        )}

        {!selectedGroup && (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-neutral-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-neutral-700 mb-2">
              Выберите группу
            </h3>
            <p className="text-neutral-500">
              Нажмите на кнопку группы, чтобы просмотреть список студентов
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherDashboard;