from typing import List, Optional
from fastapi import HTTPException, status
from app.database import get_db
from app.database.models.academic import Topic, Block, SectionMaterial

# ===========================================
# EXISTING TOPIC OPERATIONS (Updated)
# ===========================================

def add_topic_db(block_id: int, name: str, homework: Optional[str] = None,
                number: Optional[int] = None, additional_material: Optional[str] = None) -> Topic:
    """Добавление новой темы"""
    with next(get_db()) as db:
        # Проверяем, что блок существует
        block = db.query(Block).filter_by(block_id=block_id).first()
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Блок не найден"
            )
        
        new_topic = Topic(
            block_id=block_id,
            name=name,
            homework=homework,
            number=number,
            additional_material=additional_material
        )
        db.add(new_topic)
        db.commit()
        db.refresh(new_topic)
        return new_topic

def delete_topic_db(topic_id: int) -> dict:
    """Удаление темы"""
    with next(get_db()) as db:
        top = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not top:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        db.delete(top)
        db.commit()
        return {"status": "Удалена"}

def find_topic_db(topic_id: int) -> Topic:
    """Поиск темы по ID"""
    with next(get_db()) as db:
        top = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not top:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        return top

def edit_topic_db(topic_id: int, block_id: Optional[int] = None, name: Optional[str] = None,
                 homework: Optional[str] = None, number: Optional[int] = None,
                 additional_material: Optional[str] = None) -> Topic:
    """Редактирование темы"""
    with next(get_db()) as db:
        top = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not top:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        
        if block_id is not None:
            # Проверяем, что новый блок существует
            block = db.query(Block).filter_by(block_id=block_id).first()
            if not block:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Блок не найден"
                )
            top.block_id = block_id
        if name is not None:
            top.name = name
        if homework is not None:
            top.homework = homework
        if number is not None:
            top.number = number
        if additional_material is not None:
            top.additional_material = additional_material
            
        db.commit()
        db.refresh(top)
        return top

# ===========================================
# HOMEWORK OPERATIONS
# ===========================================

def add_homework_db(topic_id: int, homework: str) -> Topic:
    """Добавление домашнего задания к теме"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        topic.homework = homework
        db.commit()
        db.refresh(topic)
        return topic

def delete_homework_db(topic_id: int) -> Topic:
    """Удаление домашнего задания у темы"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        topic.homework = None
        db.commit()
        db.refresh(topic)
        return topic

def edit_homework_db(topic_id: int, homework: str) -> Topic:
    """Редактирование домашнего задания"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        topic.homework = homework
        db.commit()
        db.refresh(topic)
        return topic

# ===========================================
# TOPIC NUMBER OPERATIONS
# ===========================================

def add_topic_number_db(topic_id: int, number: int) -> Topic:
    """Добавление номера к теме"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        topic.number = number
        db.commit()
        db.refresh(topic)
        return topic

def delete_topic_number_db(topic_id: int) -> Topic:
    """Удаление номера у темы"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        topic.number = None
        db.commit()
        db.refresh(topic)
        return topic

def edit_topic_number_db(topic_id: int, number: int) -> Topic:
    """Редактирование номера темы"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        topic.number = number
        db.commit()
        db.refresh(topic)
        return topic

# ===========================================
# ADDITIONAL MATERIAL OPERATIONS
# ===========================================

def add_additional_material_db(topic_id: int, additional_material: str) -> Topic:
    """Добавление дополнительного материала к теме"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        topic.additional_material = additional_material
        db.commit()
        db.refresh(topic)
        return topic

def delete_additional_material_db(topic_id: int) -> Topic:
    """Удаление дополнительного материала у темы"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        topic.additional_material = None
        db.commit()
        db.refresh(topic)
        return topic

def edit_additional_material_db(topic_id: int, additional_material: str) -> Topic:
    """Редактирование дополнительного материала"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        topic.additional_material = additional_material
        db.commit()
        db.refresh(topic)
        return topic

# ===========================================
# NEW FUNCTIONS FROM THE LIST
# ===========================================

def get_topics_by_block_db(block_id: int) -> List[Topic]:
    """Получение всех тем по блоку"""
    with next(get_db()) as db:
        # Проверяем, что блок существует
        block = db.query(Block).filter_by(block_id=block_id).first()
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Блок не найден"
            )
        
        topics = db.query(Topic).filter_by(block_id=block_id).order_by(Topic.number).all()
        
        if not topics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Темы для блока {block_id} не найдены"
            )
        
        return topics

def get_topic_materials_db(topic_id: int) -> dict:
    """Получение всех материалов по теме"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(topic_id=topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тема не найдена"
            )
        
        # Получаем материалы раздела, к которому относится тема
        section_materials = db.query(SectionMaterial).filter_by(
            section_id=topic.block.section_id
        ).all()
        
        return {
            "topic_id": topic_id,
            "topic_name": topic.name,
            "homework": topic.homework,
            "additional_material": topic.additional_material,
            "section_materials": [
                {
                    "section_material_id": material.section_material_id,
                    "material_links": material.material_links
                }
                for material in section_materials
            ]
        }

def get_next_topic_db(current_topic_id: int) -> Optional[Topic]:
    """Получение следующей темы"""
    with next(get_db()) as db:
        current_topic = db.query(Topic).filter_by(topic_id=current_topic_id).first()
        if not current_topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Текущая тема не найдена"
            )
        
        # Ищем следующую тему в том же блоке
        if current_topic.number is not None:
            next_topic = db.query(Topic).filter(
                Topic.block_id == current_topic.block_id,
                Topic.number > current_topic.number
            ).order_by(Topic.number).first()
        else:
            # Если у текущей темы нет номера, ищем по topic_id
            next_topic = db.query(Topic).filter(
                Topic.block_id == current_topic.block_id,
                Topic.topic_id > current_topic.topic_id
            ).order_by(Topic.topic_id).first()
        
        return next_topic

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_all_topics_db() -> List[Topic]:
    """Получение всех тем"""
    with next(get_db()) as db:
        topics = db.query(Topic).order_by(Topic.block_id, Topic.number).all()
        return topics

def get_topics_with_homework_db() -> List[Topic]:
    """Получение тем с домашними заданиями"""
    with next(get_db()) as db:
        topics = db.query(Topic).filter(Topic.homework.isnot(None)).all()
        return topics

def get_topics_without_homework_db() -> List[Topic]:
    """Получение тем без домашних заданий"""
    with next(get_db()) as db:
        topics = db.query(Topic).filter(Topic.homework.is_(None)).all()
        return topics

def get_previous_topic_db(current_topic_id: int) -> Optional[Topic]:
    """Получение предыдущей темы"""
    with next(get_db()) as db:
        current_topic = db.query(Topic).filter_by(topic_id=current_topic_id).first()
        if not current_topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Текущая тема не найдена"
            )
        
        # Ищем предыдущую тему в том же блоке
        if current_topic.number is not None:
            prev_topic = db.query(Topic).filter(
                Topic.block_id == current_topic.block_id,
                Topic.number < current_topic.number
            ).order_by(Topic.number.desc()).first()
        else:
            # Если у текущей темы нет номера, ищем по topic_id
            prev_topic = db.query(Topic).filter(
                Topic.block_id == current_topic.block_id,
                Topic.topic_id < current_topic.topic_id
            ).order_by(Topic.topic_id.desc()).first()
        
        return prev_topic

def get_first_topic_in_block_db(block_id: int) -> Optional[Topic]:
    """Получение первой темы в блоке"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(block_id=block_id).order_by(Topic.number).first()
        return topic

def get_last_topic_in_block_db(block_id: int) -> Optional[Topic]:
    """Получение последней темы в блоке"""
    with next(get_db()) as db:
        topic = db.query(Topic).filter_by(block_id=block_id).order_by(Topic.number.desc()).first()
        return topic

def search_topics_by_name_db(search_name: str) -> List[Topic]:
    """Поиск тем по названию"""
    with next(get_db()) as db:
        topics = db.query(Topic).filter(
            Topic.name.ilike(f"%{search_name}%")
        ).order_by(Topic.block_id, Topic.number).all()
        
        if not topics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Темы с названием, содержащим '{search_name}', не найдены"
            )
        
        return topics

def get_topics_count_by_block_db(block_id: int) -> int:
    """Получение количества тем в блоке"""
    with next(get_db()) as db:
        return db.query(Topic).filter_by(block_id=block_id).count()