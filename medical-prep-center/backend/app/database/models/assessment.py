from sqlalchemy import (Float, DateTime, Column, Integer, ForeignKey, Text, Boolean,
                        Enum, JSON, String)
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime
from sqlalchemy import func
import enum
from enum import Enum as PyEnum
from sqlalchemy.ext.mutable import MutableList

class AttendanceType(enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class TestType(PyEnum):
    VERIFICATION = 'verification'
    CURRENT = 'current'
    FINAL = 'final'

class CommentType(enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# === ЭКЗАМЕНЫ И ОЦЕНКИ ===

class DtmExam(Base):
    __tablename__ = 'dtm_exams'
    exam_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    common_subject_correct_answers = Column(Float, nullable = False )
    second_subject_correct_answers = Column(Float, nullable = False)
    first_subject_correct_answers = Column(Float, nullable = False)
    total_correct_answers = Column(Float , nullable = False)
    exam_date = Column(DateTime, nullable = True)
    category_correct =  Column(MutableList.as_mutable(JSON),default=list)
    category_mistake =  Column(MutableList.as_mutable(JSON),default=list)
    attempt_number = Column(Integer, nullable=True)
    
    # Связи
    student = relationship("Student", back_populates="dtm_exams")
    subject = relationship("Subject", back_populates="dtm_exams")


class SectionExam(Base):
    __tablename__ = 'section_exams'
    section_exam_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    section_id = Column(Integer, ForeignKey('sections.section_id'))
    correct_answers = Column(Float)
    exam_date = Column(DateTime)
    category_correct =  Column(MutableList.as_mutable(JSON),default=list)
    category_mistake =  Column(MutableList.as_mutable(JSON),default=list)
    time_spent = Column(String)
    passed = Column(Boolean)
    # Максимальное значение из всех попыток студента
    max_correct_answers = Column(Float)
    attempt_count = Column(String, nullable=True)
    
    # Связи
    student = relationship("Student", back_populates="section_exams")
    section = relationship("Section", back_populates="section_exams")

class BlockExam(Base):
    __tablename__ = 'block_exams'
    block_exam_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    block_id = Column(Integer, ForeignKey('blocks.block_id'))
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    correct_answers = Column(Float)
    exam_date = Column(DateTime)
    category_correct =  Column(MutableList.as_mutable(JSON),default=list)
    category_mistake =  Column(MutableList.as_mutable(JSON),default=list)
    time_spent = Column(String)
    passed = Column(Boolean)
    # Максимальное значение из всех попыток студента
    max_correct_answers = Column(Float)
    attempt_count = Column(String, nullable=True)
    time_limit = Column(String, nullable=True)
    
    # Связи
    student = relationship("Student", back_populates="block_exams")
    block = relationship("Block", back_populates="block_exams")
    subject = relationship("Subject", back_populates="block_exams")

class ModulExam(Base):
    __tablename__ = 'modul_exams'
    modul_exam_id = Column(Integer, primary_key=True, autoincrement=True)
    modul_id = Column(Integer, ForeignKey('moduls.modul_id'))
    student_id = Column(Integer, ForeignKey('students.student_id'))
    chem_correct_answers = Column(Float)
    bio_correct_answers = Column(Float)
    exam_date = Column(DateTime)
    category_correct =  Column(MutableList.as_mutable(JSON),default=list)
    category_mistake =  Column(MutableList.as_mutable(JSON),default=list)
    total_questions_chem = Column(Integer)
    total_questions_bio = Column(Integer)
    time_spent_chem = Column(String)
    time_spent_bio = Column(String)
    
    # Связи
    moduls = relationship("Moduls", back_populates="exams")
    student = relationship("Student", back_populates="modul_exams")
    
    
# Оценка за тест относящийся к определённой теме
class TopicTest(Base):
    __tablename__ = 'topic_tests'
    topic_test_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    topic_id = Column(Integer, ForeignKey('topics.topic_id'))
    question_count = Column(Integer)
    correct_answers = Column(Float)
    attempt_date = Column(DateTime)
    time_spent = Column(String)
    
    # Связи
    student = relationship("Student", back_populates="topic_tests")
    topic = relationship("Topic", back_populates="topic_tests")

# Оценка за опрос
class CurrentRating(Base):
    __tablename__ = 'current_ratings'
    rating_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    topic_id = Column(Integer, ForeignKey('topics.topic_id'))
    current_correct_answers = Column(Float)
    second_current_correct_answers = Column(Float)
    last_updated = Column(DateTime, default=datetime.now())
    
    # Связи
    student = relationship("Student", back_populates="current_ratings")
    subject = relationship("Subject", back_populates="current_ratings")
    topic = relationship("Topic", back_populates="current_ratings")

# === СИСТЕМА ТЕСТИРОВАНИЯ ===

class Question(Base):
    __tablename__ = 'questions'
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id'))
    text = Column(Text)
    answer_1 = Column(String(500))
    answer_2 = Column(String(500))
    answer_3 = Column(String(500))
    answer_4 = Column(String(500))
    correct_answers = Column(Integer)
    explanation = Column(Text, nullable = True)
    category =  Column(MutableList.as_mutable(JSON),default=list)
    # Связи
    topic = relationship("Topic", back_populates="questions")

# === ПОСЕЩАЕМОСТЬ И КОММЕНТАРИИ ===

class Attendance(Base):
    __tablename__ = 'attendances'
    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    lesson_date_time = Column(DateTime)
    att_status = Column(Enum(AttendanceType))
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    topic_id = Column(Integer, ForeignKey('topics.topic_id'))
    excuse_reason = Column(String, nullable=True)
    extra_lesson = Column(String, nullable=True)
    
    # Связи
    student = relationship("Student", back_populates="attendances")
    subject = relationship("Subject", back_populates="attendances")
    topic = relationship('Topic', back_populates="attendances")

class Comments(Base):
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'))
    student_id = Column(Integer, ForeignKey('students.student_id'))
    comment_text = Column(Text)
    comment_date = Column(DateTime(timezone=True), server_default=func.now())
    comment_type = Column(Enum(CommentType))
    # Связи
    teacher = relationship("Teacher", back_populates="comments")
    student = relationship("Student", back_populates="comments")
