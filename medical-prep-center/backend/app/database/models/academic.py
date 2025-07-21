from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum

class UniversityType(enum.Enum):
    STATE = "state"
    PRIVATE = "private"

# === УЧЕБНАЯ СТРУКТУРА ===

class Subject(Base):
    __tablename__ = 'subjects'
    subject_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))
    description = Column(Text)
    
    # Связи
    teachers = relationship("Teacher", secondary="teacher_subject", back_populates="subjects")
    sections = relationship("Section", back_populates="subject", cascade="all, delete-orphan")
    groups = relationship("Group", back_populates="subject")
    dtm_exams = relationship("DtmExam", back_populates="subject")
    current_ratings = relationship("CurrentRating", back_populates="subject")
    attendances = relationship("Attendance", back_populates="subject")
    block_exams = relationship("BlockExam", back_populates="subject")


class Section(Base):
    __tablename__ = 'sections'
    section_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    name = Column(String(200))
    order_number = Column(Integer)
    
    # Связи
    subject = relationship("Subject", back_populates="sections")
    blocks = relationship("Block", back_populates="section")
    section_exams = relationship("SectionExam", back_populates="section", cascade="all, delete-orphan")
    section_materials = relationship('SectionMaterial', back_populates="section", cascade="all, delete-orphan")


class SectionMaterial(Base):
    __tablename__ = 'section_materials'
    section_material_id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('sections.section_id'))
    material_links = Column(Text)
    
    # Связи
    section = relationship("Section", back_populates="section_materials")


class Block(Base):
    __tablename__ = 'blocks'
    block_id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('sections.section_id'))
    name = Column(String(200))
    order_number = Column(Integer)
    description = Column(Text, nullable=True)
    
    # Связи
    section = relationship("Section", back_populates="blocks")
    topics = relationship("Topic", back_populates="block", cascade="all, delete-orphan")
    block_exams = relationship("BlockExam", back_populates="block")


class Topic(Base):
    __tablename__ = 'topics'
    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    block_id = Column(Integer, ForeignKey('blocks.block_id'))
    name = Column(String(200))
    homework = Column(Text)
    number = Column(Integer)
    additional_material = Column(Text, nullable=True) 
    
    # Связи
    block = relationship("Block", back_populates="topics")
    questions = relationship("Question", back_populates="topic")
    topic_tests = relationship("TopicTest", back_populates="topic")
    attendances = relationship("Attendance", back_populates="topic")
    current_ratings = relationship("CurrentRating", back_populates="topic")
    group_progress = relationship("GroupProgress", back_populates="topic")


class Group(Base):
    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'))
    name = Column(String(100))
    description = Column(String(500))
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    max_student = Column(Integer, nullable=True)
    
    # Связи
    subject = relationship("Subject", back_populates="groups")
    teacher = relationship("Teacher", back_populates="groups")
    students = relationship("Student", back_populates="group")
    group_progress = relationship("GroupProgress", back_populates="group")


class GroupProgress(Base):
    __tablename__ = 'group_progress'
    group_progress_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    topic_id = Column(Integer, ForeignKey('topics.topic_id'))
    data = Column(Text)
    average_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Связи
    group = relationship("Group", back_populates="group_progress")
    topic = relationship("Topic", back_populates="group_progress")


class Moduls(Base):
    __tablename__ = 'moduls'
    modul_id = Column(Integer, primary_key=True, autoincrement=True)
    start_topic_chem = Column(Integer)
    start_topic_bio = Column(Integer)
    end_topic_chem = Column(Integer)
    end_topic_bio = Column(Integer)
    order_number = Column(Integer)
    name = Column(String, nullable=True)
    
    
    # Связи
    exams = relationship("ModulExam", back_populates="moduls")
    

# === Университеты ===

class University(Base):
    __tablename__ = 'universities'
    university_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(300))
    type = Column(Enum(UniversityType))
    entrance_score = Column(Float)
    location = Column(String(200))
    website_url = Column(String(300))
    logo_url = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    
    # Связи
    students = relationship("Student", secondary="student_university", back_populates="universities")
    faculties = relationship("Faculty", back_populates="university")


class Faculty(Base):
    __tablename__ = 'faculties'
    faculty_id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey('universities.university_id'))
    name = Column(String(200))
    annual_cost = Column(String, nullable=True)
    available_place = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    entrance_score = Column(Float, nullable=True)
    code = Column(String, nullable=True)
    
    # Связи
    university = relationship("University", back_populates="faculties")
    