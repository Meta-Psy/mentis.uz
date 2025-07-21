from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy import func

Base = declarative_base()

# Базовые миксины для переиспользования
class TimestampMixin:
    """Миксин для добавления временных меток"""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class StatusMixin:
    """Миксин для добавления статуса активности"""
    is_active = Column(Boolean, default=True)