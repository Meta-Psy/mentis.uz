from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import or_, desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.assessment import CommentType, Comments


# -----------------------
# ADD COMMENT
# -----------------------
async def add_comment_db(
    db: AsyncSession,
    teacher_id: int,
    student_id: int,
    comment_text: str,
    comment_type: CommentType,
) -> Comments:
    """Добавление комментария"""

    new_comment = Comments(
        teacher_id=teacher_id,
        student_id=student_id,
        comment_text=comment_text,
        comment_type=comment_type,
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


# -----------------------
# DELETE COMMENT
# -----------------------
async def delete_comment_db(db: AsyncSession, comment_id: int) -> dict:
    """Удаление комментария"""

    result = await db.execute(
        select(Comments).filter(Comments.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден"
        )
    await db.delete(comment)
    await db.commit()
    return {"status": "Удалён"}


# -----------------------
# EDIT COMMENT TEXT
# -----------------------
async def edit_comment_text_db(
    db: AsyncSession, comment_id: int, new_text: str
) -> Comments:
    """Редактирование текста комментария"""

    result = await db.execute(
        select(Comments).filter(Comments.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден"
        )
    comment.comment_text = new_text
    await db.commit()
    await db.refresh(comment)
    return comment


# -----------------------
# EDIT COMMENT TYPE
# -----------------------
async def edit_comment_type_db(
    db: AsyncSession, comment_id: int, new_type: CommentType
) -> Comments:
    """Редактирование типа комментария"""

    result = await db.execute(
        select(Comments).filter(Comments.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден"
        )
    comment.comment_type = new_type
    await db.commit()
    await db.refresh(comment)
    return comment


# -----------------------
# UPDATE COMMENT
# -----------------------
async def update_comment_db(
    db: AsyncSession,
    comment_id: int,
    comment_text: Optional[str] = None,
    comment_type: Optional[CommentType] = None,
) -> Comments:
    """Обновление комментария"""

    result = await db.execute(
        select(Comments).filter(Comments.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден"
        )

    if comment_text is not None:
        comment.comment_text = comment_text
    if comment_type is not None:
        comment.comment_type = comment_type

    await db.commit()
    await db.refresh(comment)
    return comment


# -----------------------
# GET COMMENTS BY STUDENT & TYPE
# -----------------------
async def get_negative_comments_by_student_db(
    db: AsyncSession, student_id: int
) -> List[Comments]:
    """Получение негативных комментариев студента"""

    result = await db.execute(
        select(Comments)
        .filter(
            Comments.student_id == student_id,
            Comments.comment_type == CommentType.NEGATIVE,
        )
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Негативные комментарии для студента {student_id} не найдены",
        )
    return records


async def get_positive_comments_by_student_db(
    db: AsyncSession, student_id: int
) -> List[Comments]:
    """Получение позитивных комментариев студента"""

    result = await db.execute(
        select(Comments)
        .filter(
            Comments.student_id == student_id,
            Comments.comment_type == CommentType.POSITIVE,
        )
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Позитивные комментарии для студента {student_id} не найдены",
        )
    return records


async def get_neutral_comments_by_student_db(
    db: AsyncSession, student_id: int
) -> List[Comments]:
    """Получение нейтральных комментариев студента"""

    result = await db.execute(
        select(Comments)
        .filter(
            Comments.student_id == student_id,
            Comments.comment_type == CommentType.NEUTRAL,
        )
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Нейтральные комментарии для студента {student_id} не найдены",
        )
    return records


async def get_all_comments_by_student_db(
    db: AsyncSession, student_id: int
) -> List[Comments]:
    """Получение всех комментариев студента"""

    result = await db.execute(
        select(Comments)
        .filter(Comments.student_id == student_id)
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комментарии для студента {student_id} не найдены",
        )
    return records


# -----------------------
# GET COMMENTS BY TEACHER
# -----------------------
async def get_comments_by_teacher_db(
    db: AsyncSession, teacher_id: int
) -> List[Comments]:
    """Получение всех комментариев учителя"""

    result = await db.execute(
        select(Comments)
        .filter(Comments.teacher_id == teacher_id)
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комментарии учителя {teacher_id} не найдены",
        )
    return records


# -----------------------
# SEARCH COMMENTS
# -----------------------
async def search_comments_by_text_db(
    db: AsyncSession, search_text: str
) -> List[Comments]:
    """Поиск комментариев по тексту"""

    result = await db.execute(
        select(Comments)
        .filter(Comments.comment_text.ilike(f"%{search_text}%"))
        .order_by(desc(Comments.comment_date))
    )
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комментариев, содержащих «{search_text}», не найдено",
        )
    return records


# -----------------------
# GET RECENT COMMENTS
# -----------------------
async def get_recent_comments_db(
    db: AsyncSession,
    student_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    limit: int = 10,
) -> List[Comments]:
    """Получение последних комментариев"""

    query = select(Comments)

    if student_id:
        query = query.filter(Comments.student_id == student_id)
    if teacher_id:
        query = query.filter(Comments.teacher_id == teacher_id)

    query = query.order_by(desc(Comments.comment_date)).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()
    return records


# -----------------------
# GET COMMENTS BY DATE RANGE
# -----------------------
async def get_comments_by_date_range_db(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    student_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
) -> List[Comments]:
    """Получение комментариев за период"""

    query = select(Comments).filter(
        Comments.comment_date >= start_date, Comments.comment_date <= end_date
    )

    if student_id:
        query = query.filter(Comments.student_id == student_id)
    if teacher_id:
        query = query.filter(Comments.teacher_id == teacher_id)

    query = query.order_by(desc(Comments.comment_date))
    result = await db.execute(query)
    records = result.scalars().all()
    return records


# -----------------------
# GET COMMENT STATISTICS
# -----------------------
async def get_comment_statistics_db(
    db: AsyncSession, student_id: Optional[int] = None, teacher_id: Optional[int] = None
) -> dict:
    """Получение статистики комментариев"""

    query = select(Comments)

    if student_id:
        query = query.filter(Comments.student_id == student_id)
    if teacher_id:
        query = query.filter(Comments.teacher_id == teacher_id)

    # Общее количество комментариев
    result = await db.execute(query)
    all_comments = result.scalars().all()
    total_comments = len(all_comments)

    # Подсчет по типам
    positive_count = len(
        [c for c in all_comments if c.comment_type == CommentType.POSITIVE]
    )
    negative_count = len(
        [c for c in all_comments if c.comment_type == CommentType.NEGATIVE]
    )
    neutral_count = len(
        [c for c in all_comments if c.comment_type == CommentType.NEUTRAL]
    )

    return {
        "total_comments": total_comments,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "positive_percentage": round(
            (positive_count / total_comments * 100) if total_comments > 0 else 0, 2
        ),
        "negative_percentage": round(
            (negative_count / total_comments * 100) if total_comments > 0 else 0, 2
        ),
        "neutral_percentage": round(
            (neutral_count / total_comments * 100) if total_comments > 0 else 0, 2
        ),
    }
