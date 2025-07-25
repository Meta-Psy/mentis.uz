from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models.academic import Moduls

# ===========================================
# EXISTING MODULE OPERATIONS (Updated)
# ===========================================


async def add_modul_db(
    db: AsyncSession,
    start_topic_chem: int,
    start_topic_bio: int,
    end_topic_chem: int,
    end_topic_bio: int,
    order_number: Optional[int] = None,
    name: Optional[str] = None,
) -> Moduls:
    """Добавление нового модуля"""

    new_modul = Moduls(
        start_topic_chem=start_topic_chem,
        start_topic_bio=start_topic_bio,
        end_topic_chem=end_topic_chem,
        end_topic_bio=end_topic_bio,
        order_number=order_number,
        name=name,
    )
    db.add(new_modul)
    await db.commit()
    await db.refresh(new_modul)
    return new_modul


async def delete_modul_db(db: AsyncSession, modul_id: int) -> dict:
    """Удаление модуля"""

    result = await db.execute(select(Moduls).filter(Moduls.modul_id == modul_id))
    modul = result.scalar_one_or_none()
    if not modul:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Модуль не найден"
        )
    await db.delete(modul)
    await db.commit()
    return {"status": "Удалён"}


async def find_modul_db(db: AsyncSession, modul_id: int) -> Moduls:
    """Поиск модуля по ID"""

    result = await db.execute(select(Moduls).filter(Moduls.modul_id == modul_id))
    modul = result.scalar_one_or_none()
    if not modul:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Модуль не найден"
        )
    return modul


async def edit_modul_db(
    db: AsyncSession,
    modul_id: int,
    start_topic_chem: Optional[int] = None,
    start_topic_bio: Optional[int] = None,
    end_topic_chem: Optional[int] = None,
    end_topic_bio: Optional[int] = None,
    order_number: Optional[int] = None,
    name: Optional[str] = None,
) -> Moduls:
    """Редактирование модуля"""

    result = await db.execute(select(Moduls).filter(Moduls.modul_id == modul_id))
    modul = result.scalar_one_or_none()
    if not modul:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Модуль не найден"
        )

    if start_topic_chem is not None:
        modul.start_topic_chem = start_topic_chem
    if start_topic_bio is not None:
        modul.start_topic_bio = start_topic_bio
    if end_topic_chem is not None:
        modul.end_topic_chem = end_topic_chem
    if end_topic_bio is not None:
        modul.end_topic_bio = end_topic_bio
    if order_number is not None:
        modul.order_number = order_number
    if name is not None:
        modul.name = name

    await db.commit()
    await db.refresh(modul)
    return modul


# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================


async def get_all_modules_db(db: AsyncSession) -> List[Moduls]:
    """Получение всех модулей"""

    result = await db.execute(select(Moduls).order_by(Moduls.order_number))
    modules = result.scalars().all()
    return modules


async def get_modules_by_subject_db(
    db: AsyncSession, subject_name: str
) -> List[Moduls]:
    """Получение модулей по предмету (химия или биология)"""

    if subject_name.lower() in ["химия", "chemistry", "chem"]:
        # Возвращаем модули, которые включают темы по химии
        result = await db.execute(
            select(Moduls)
            .filter(
                Moduls.start_topic_chem.isnot(None), Moduls.end_topic_chem.isnot(None)
            )
            .order_by(Moduls.order_number)
        )
        modules = result.scalars().all()
    elif subject_name.lower() in ["биология", "biology", "bio"]:
        # Возвращаем модули, которые включают темы по биологии
        result = await db.execute(
            select(Moduls)
            .filter(
                Moduls.start_topic_bio.isnot(None), Moduls.end_topic_bio.isnot(None)
            )
            .order_by(Moduls.order_number)
        )
        modules = result.scalars().all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверное название предмета. Используйте 'химия' или 'биология'",
        )

    if not modules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модули по предмету '{subject_name}' не найдены",
        )

    return modules


# ===========================================
# HELPER FUNCTIONS
# ===========================================


async def get_module_by_order_db(db: AsyncSession, order_number: int) -> Moduls:
    """Получение модуля по порядковому номеру"""

    result = await db.execute(
        select(Moduls).filter(Moduls.order_number == order_number)
    )
    modul = result.scalar_one_or_none()
    if not modul:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модуль с порядковым номером {order_number} не найден",
        )
    return modul


async def get_modules_count_db(db: AsyncSession) -> int:
    """Получение количества модулей"""

    result = await db.execute(select(func.count(Moduls.modul_id)))
    return result.scalar()


async def get_modules_by_topic_range_db(
    db: AsyncSession, subject_type: str, start_topic: int, end_topic: int
) -> List[Moduls]:
    """Получение модулей по диапазону тем"""

    if subject_type.lower() in ["химия", "chemistry", "chem"]:
        result = await db.execute(
            select(Moduls)
            .filter(
                Moduls.start_topic_chem <= end_topic,
                Moduls.end_topic_chem >= start_topic,
            )
            .order_by(Moduls.order_number)
        )
        modules = result.scalars().all()
    elif subject_type.lower() in ["биология", "biology", "bio"]:
        result = await db.execute(
            select(Moduls)
            .filter(
                Moduls.start_topic_bio <= end_topic, Moduls.end_topic_bio >= start_topic
            )
            .order_by(Moduls.order_number)
        )
        modules = result.scalars().all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный тип предмета"
        )

    return modules
