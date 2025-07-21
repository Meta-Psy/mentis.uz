# Medical Prep Center

Система подготовки к поступлению в медицинские ВУЗы.

## Структура проекта

- `backend/` - FastAPI сервер
- `frontend/` - React + TypeScript приложение

## Установка и запуск

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Функциональность

- Управление студентами, учителями и родителями
- Система тестирования и оценок
- Аналитика успеваемости
- Управление учебными материалами
