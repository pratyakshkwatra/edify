from sqlalchemy import create_engine, Column, String, Integer, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from os import environ

engine = create_engine("sqlite:///database.sqlite")

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

class Onboarding(Base):
    __tablename__ = 'onboardings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    grade_year = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    timestamp = Column(String, nullable=False)
    report_generated = Column(BOOLEAN)
    
class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    onboarding_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    
class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    score = Column(Integer, nullable=False)

class Notes(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    topic_full = Column(String, nullable=False)
    
class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, nullable=False)
    
    question_body = Column(String, nullable=False)
    option1 = Column(String, nullable=False)
    option2 = Column(String, nullable=False)
    option3 = Column(String, nullable=False)
    option4 = Column(String, nullable=False)

class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, nullable=False)
    
    answer_option = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)

Base.metadata.create_all(engine)