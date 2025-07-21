from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import or_, desc
from app.database import get_db
from app.database.models.assessment import CommentType, Comments

# -----------------------
# ADD COMMENT
# -----------------------
def add_comment_db(teacher_id: int, student_id: int, comment_text: str,
                   comment_type: CommentType) -> Comments:
    """Добавление комментария"""
    with next(get_db()) as db:
        new_comment = Comments(
            teacher_id=teacher_id, 
            student_id=student_id,
            comment_text=comment_text,
            comment_type=comment_type
        )
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        return new_comment

# -----------------------
# DELETE COMMENT
# -----------------------
def delete_comment_db(comment_id: int) -> dict:
    """Удаление комментария"""
    with next(get_db()) as db:
        comment = db.query(Comments).filter_by(comment_id=comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комментарий не найден"
            )
        db.delete(comment)
        db.commit()
        return {"status": "Удалён"}

# -----------------------
# EDIT COMMENT TEXT
# -----------------------
def edit_comment_text_db(comment_id: int, new_text: str) -> Comments:
    """Редактирование текста комментария"""
    with next(get_db()) as db:
        comment = db.query(Comments).filter_by(comment_id=comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комментарий не найден"
            )
        comment.comment_text = new_text
        db.commit()
        db.refresh(comment)
        return comment

# -----------------------
# EDIT COMMENT TYPE
# -----------------------
def edit_comment_type_db(comment_id: int, new_type: CommentType) -> Comments:
    """Редактирование типа комментария"""
    with next(get_db()) as db:
        comment = db.query(Comments).filter_by(comment_id=comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комментарий не найден"
            )
        comment.comment_type = new_type
        db.commit()
        db.refresh(comment)
        return comment

# -----------------------
# UPDATE COMMENT
# -----------------------
def update_comment_db(comment_id: int, comment_text: Optional[str] = None,
                     comment_type: Optional[CommentType] = None) -> Comments:
    """Обновление комментария"""
    with next(get_db()) as db:
        comment = db.query(Comments).filter_by(comment_id=comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комментарий не найден"
            )
        
        if comment_text is not None:
            comment.comment_text = comment_text
        if comment_type is not None:
            comment.comment_type = comment_type
            
        db.commit()
        db.refresh(comment)
        return comment

# -----------------------
# GET COMMENTS BY STUDENT & TYPE
# -----------------------
def get_negative_comments_by_student_db(student_id: int) -> List[Comments]:
    """Получение негативных комментариев студента"""
    with next(get_db()) as db:
        records = db.query(Comments).filter_by(
            student_id=student_id,
            comment_type=CommentType.NEGATIVE
        ).order_by(desc(Comments.comment_date)).all()
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Негативные комментарии для студента {student_id} не найдены"
            )
        return records

def get_positive_comments_by_student_db(student_id: int) -> List[Comments]:
    """Получение позитивных комментариев студента"""
    with next(get_db()) as db:
        records = db.query(Comments).filter_by(
            student_id=student_id, 
            comment_type=CommentType.POSITIVE
        ).order_by(desc(Comments.comment_date)).all()
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Позитивные комментарии для студента {student_id} не найдены"
            )
        return records

def get_neutral_comments_by_student_db(student_id: int) -> List[Comments]:
    """Получение нейтральных комментариев студента"""
    with next(get_db()) as db:
        records = db.query(Comments).filter_by(
            student_id=student_id, 
            comment_type=CommentType.NEUTRAL
        ).order_by(desc(Comments.comment_date)).all()
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Нейтральные комментарии для студента {student_id} не найдены"
            )
        return records

def get_all_comments_by_student_db(student_id: int) -> List[Comments]:
    """Получение всех комментариев студента"""
    with next(get_db()) as db:
        records = db.query(Comments).filter_by(
            student_id=student_id
        ).order_by(desc(Comments.comment_date)).all()
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Комментарии для студента {student_id} не найдены"
            )
        return records

# -----------------------
# GET COMMENTS BY TEACHER
# -----------------------
def get_comments_by_teacher_db(teacher_id: int) -> List[Comments]:
    """Получение всех комментариев учителя"""
    with next(get_db()) as db:
        records = db.query(Comments).filter_by(
            teacher_id=teacher_id
        ).order_by(desc(Comments.comment_date)).all()
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Комментарии учителя {teacher_id} не найдены"
            )
        return records

# -----------------------
# SEARCH COMMENTS
# -----------------------
def search_comments_by_text_db(search_text: str) -> List[Comments]:
    """Поиск комментариев по тексту"""
    with next(get_db()) as db:
        records = db.query(Comments).filter(
            Comments.comment_text.ilike(f"%{search_text}%")
        ).order_by(desc(Comments.comment_date)).all()
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Комментариев, содержащих «{search_text}», не найдено"
            )
        return records

# -----------------------
# GET RECENT COMMENTS
# -----------------------
def get_recent_comments_db(student_id: Optional[int] = None, 
                          teacher_id: Optional[int] = None,
                          limit: int = 10) -> List[Comments]:
    """Получение последних комментариев"""
    with next(get_db()) as db:
        query = db.query(Comments)
        
        if student_id:
            query = query.filter_by(student_id=student_id)
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
            
        records = query.order_by(desc(Comments.comment_date)).limit(limit).all()
        return records

# -----------------------
# GET COMMENTS BY DATE RANGE
# -----------------------
def get_comments_by_date_range_db(start_date: datetime, end_date: datetime,
                                 student_id: Optional[int] = None,
                                 teacher_id: Optional[int] = None) -> List[Comments]:
    """Получение комментариев за период"""
    with next(get_db()) as db:
        query = db.query(Comments).filter(
            Comments.comment_date >= start_date,
            Comments.comment_date <= end_date
        )
        
        if student_id:
            query = query.filter_by(student_id=student_id)
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
            
        records = query.order_by(desc(Comments.comment_date)).all()
        return records

# -----------------------
# GET COMMENT STATISTICS
# -----------------------
def get_comment_statistics_db(student_id: Optional[int] = None,
                             teacher_id: Optional[int] = None) -> dict:
    """Получение статистики комментариев"""
    with next(get_db()) as db:
        query = db.query(Comments)
        
        if student_id:
            query = query.filter_by(student_id=student_id)
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
            
        total_comments = query.count()
        positive_count = query.filter_by(comment_type=CommentType.POSITIVE).count()
        negative_count = query.filter_by(comment_type=CommentType.NEGATIVE).count()
        neutral_count = query.filter_by(comment_type=CommentType.NEUTRAL).count()
        
        return {
            "total_comments": total_comments,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_percentage": round((positive_count / total_comments * 100) if total_comments > 0 else 0, 2),
            "negative_percentage": round((negative_count / total_comments * 100) if total_comments > 0 else 0, 2),
            "neutral_percentage": round((neutral_count / total_comments * 100) if total_comments > 0 else 0, 2)
        }