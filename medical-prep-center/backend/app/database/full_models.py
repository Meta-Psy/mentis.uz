# academic.py
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base
from datetime import datetime
import enum

class UniversityType(enum.Enum):
    STATE = "state"
    PRIVATE = "private"

class MaterialFileType(enum.Enum):
    BOOK = "book"
    TEST_BOOK = "test_book"

class TestType(enum.Enum):
    TRAINING = "training"
    CONTROL = "control"
    FINAL = "final"

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
    material_files = relationship("MaterialFile", back_populates="section", cascade="all, delete-orphan")



class SectionMaterial(Base):
    __tablename__ = 'section_materials'
    section_material_id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('sections.section_id'))
    material_links = Column(Text)
    
    # Связи
    section = relationship("Section", back_populates="section_materials")

class SectionMaterialsView(Base):
    __tablename__ = 'v_section_materials'
    
    section_id = Column(Integer, primary_key=True)
    section_name = Column(String(200))
    section_order = Column(Integer)
    section_description = Column(Text)
    subject_name = Column(String(200))
    books_count = Column(Integer)
    test_books_count = Column(Integer)
    topics_count = Column(Integer)

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
    video_url = Column(String, nullable=True)
    number = Column(Integer)
    additional_material = Column(Text, nullable=True) 
    
    # Связи
    block = relationship("Block", back_populates="topics")
    questions = relationship("Question", back_populates="topic")
    topic_tests = relationship("TopicTest", back_populates="topic")
    attendances = relationship("Attendance", back_populates="topic")
    current_ratings = relationship("CurrentRating", back_populates="topic")
    group_progress = relationship("GroupProgress", back_populates="topic")
    test_mappings = relationship("TopicTestMapping", back_populates="topic", cascade="all, delete-orphan")


class TopicDetailsView(Base):
    __tablename__ = 'v_topic_details'
    
    topic_id = Column(Integer, primary_key=True)
    topic_name = Column(String(200))
    homework = Column(Text)
    topic_number = Column(Integer)
    additional_material = Column(Text)
    video_url = Column(String(500))
    block_name = Column(String(200))
    section_name = Column(String(200))
    section_id = Column(Integer)
    subject_name = Column(String(200))
    subject_id = Column(Integer)
    questions_count = Column(Integer)
    tests_count = Column(Integer)
    
    
class MaterialFile(Base):
    __tablename__ = 'material_files'
    
    file_id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('sections.section_id'))
    file_type = Column(Enum(MaterialFileType))
    title = Column(String(300))
    author = Column(String(200))
    file_size = Column(String(50))
    file_format = Column(String(10), default='PDF')
    download_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.now())
    updated_at = Column(DateTime(timezone=True), server_default=datetime.now(), onupdate=datetime.now())
    
    # Связи
    section = relationship("Section", back_populates="material_files")
    
    
class TopicTestMapping(Base):
    __tablename__ = 'topic_tests_mapping'
    
    mapping_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.topic_id'))
    test_id = Column(Integer)
    test_type = Column(Enum(TestType), default=TestType.TRAINING)
    created_at = Column(DateTime(timezone=True), server_default=datetime.now())
    
    # Связи
    topic = relationship("Topic", back_populates="test_mappings")
    

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
    
# assessment.py
from sqlalchemy import (Float, DateTime, Column, Integer, ForeignKey, Text, Boolean,
                        Enum, JSON, String)
from sqlalchemy.orm import relationship
from app.database.base import Base
from sqlalchemy import func
import enum
from sqlalchemy.ext.mutable import MutableList

class AttendanceType(enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

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
    last_updated = Column(DateTime, default=func.now())
    
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

# user.py 
from sqlalchemy import (Column, Integer, DateTime, String, Boolean,
                        Enum, Text, ForeignKey, Date, Table)
from sqlalchemy.orm import relationship
from app.database.base import Base
from sqlalchemy import func
import enum
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import JSON
import pytz

tashkent_tz = pytz.timezone("Asia/Tashkent")

class UserRole(enum.Enum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"

class StudentStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class TeacherStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class AdminStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# Связующие таблицы
teacher_subject_table = Table(
    'teacher_subject',
    Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.teacher_id'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.subject_id'), primary_key=True))

student_university_table = Table(
    'student_university',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.student_id'), primary_key=True),
    Column('university_id', Integer, ForeignKey('universities.university_id'), primary_key=True),
    Column('priority_order', Integer))


# === ОСНОВНЫЕ МОДЕЛИ ПОЛЬЗОВАТЕЛЕЙ ===

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    surname = Column(String(100))
    phone = Column(String(20), unique=True)
    email = Column(String(150), unique=True, nullable=True)
    password = Column(String(255))
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    photo = Column(String(255), nullable=True)
    
    # Полиморфные связи
    student = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    parent = relationship("ParentInfo", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan")
    admin = relationship("Admin", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = 'students'
    student_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    direction = Column(String(200))
    student_status = Column(Enum(StudentStatus), default=StudentStatus.ACTIVE)
    group_id = Column(Integer, ForeignKey('groups.group_id'))
    last_login = Column(DateTime)
    goal = Column(String, nullable=True)
    # Связи
    user = relationship("User", back_populates="student", uselist=False)
    group = relationship("Group", back_populates="students")
    universities = relationship("University", secondary=student_university_table, back_populates="students")
    student_info = relationship("StudentInfo", back_populates="student", uselist=False)
    # Связи с экзаменами и оценками
    modul_exams = relationship("ModulExam", back_populates="student", cascade="all, delete-orphan")
    dtm_exams = relationship("DtmExam", back_populates="student", cascade="all, delete-orphan")
    section_exams = relationship("SectionExam", back_populates="student", cascade="all, delete-orphan")
    block_exams = relationship("BlockExam", back_populates="student", cascade="all, delete-orphan")
    topic_tests = relationship("TopicTest", back_populates="student", cascade="all, delete-orphan")
    current_ratings = relationship("CurrentRating", back_populates="student", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="student",cascade="all, delete-orphan")
    comments = relationship("Comments", back_populates="student", cascade="all, delete-orphan")
    student_skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")


class StudentInfo(Base):
    __tablename__ = 'student_info'
    student_id = Column(Integer, ForeignKey("students.student_id"), primary_key=True)
    hobby = Column(String(500))
    sex = Column(String(10))
    address = Column(Text)
    birthday = Column(Date)
    
    # Связи
    student = relationship("Student", back_populates="student_info")


class StudentSkill(Base):
    __tablename__ = 'student_skills'
    student_skill_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    correct = Column(MutableList.as_mutable(JSON),default=list)
    mistakes = Column(MutableList.as_mutable(JSON), default=list)
    
    # Связи
    student = relationship("Student", back_populates="student_skills")


class Teacher(Base):
    __tablename__ = 'teachers'
    teacher_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    teacher_schedule = Column(Text)
    teacher_status = Column(Enum(TeacherStatus), default=TeacherStatus.ACTIVE)
    
    # Связи
    user = relationship("User", back_populates="teacher")
    subjects = relationship("Subject", secondary=teacher_subject_table, back_populates="teachers")
    groups = relationship("Group", back_populates="teacher")
    comments = relationship("Comments", back_populates="teacher")
    teacher_info = relationship("TeacherInfo", back_populates="teacher", uselist=False)


class TeacherInfo(Base):
    __tablename__ = 'teacher_info'
    teacher_info_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id", ondelete='CASCADE'))
    teacher_employment = Column(String(100))
    teacher_number = Column(String(15))
    dop_info = Column(String(100))
    education_background = Column(String, nullable=True)
    years_experiense = Column(Integer, nullable=True)
    certifications = Column(String, nullable=True)
    availability = Column(String, nullable=True)
    languages = Column(String, nullable=True)
    
    # Связи
    teacher = relationship("Teacher", back_populates='teacher_info')


class Admin(Base):
    __tablename__ = 'admins'
    admin_id = Column(Integer, ForeignKey('users.user_id' ), primary_key=True)
    schedule = Column(Text)
    admin_status = Column(Enum(AdminStatus), default=AdminStatus.ACTIVE)
    
    # Связи
    user = relationship("User", back_populates="admin")
    admin_info = relationship("AdminInfo", back_populates="admin", uselist=False)


class AdminInfo(Base):
    __tablename__ = 'admin_info'
    admin_id = Column(Integer, ForeignKey('admins.admin_id'), primary_key=True)
    admin_number = Column(String(14))
    employment = Column(String(100), nullable=True)
    admin_hobby = Column(String(100), nullable=True)
    
    # Связи
    admin = relationship("Admin", back_populates="admin_info")

class ParentInfo(Base):
    __tablename__ = 'parent_info'
    parent_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    profession = Column(String(200), nullable=True)
    parent_phone = Column(String(15), nullable=True)
    workplace = Column(String, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="parent")
    