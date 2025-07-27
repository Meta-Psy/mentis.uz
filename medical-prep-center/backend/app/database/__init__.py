from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from app.config import settings
from sqlalchemy.exc import SQLAlchemyError
from app.database.base import Base 

DATABASE_URL = settings.database_url

async_engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        
        
async def init_db():
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except SQLAlchemyError as e:
        print(f"Ошибка инициализации базы: {e}")
        raise

# Функция для закрытия соединений
async def close_db():
    await async_engine.dispose()