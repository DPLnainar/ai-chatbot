"""
Database models for Career Companion AI
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class StudentProfile(Base):
    """Student profile model for tracking student information"""
    __tablename__ = "student_profiles"
    
    student_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    current_cgpa = Column(Float, nullable=True)
    skills = Column(Text, nullable=True)  # Comma-separated skills
    arrears_count = Column(Integer, default=0)
    year = Column(Integer, nullable=True)  # 1, 2, 3, 4
    target_companies = Column(Text, nullable=True)  # Comma-separated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to chat logs
    chat_logs = relationship("ChatLog", back_populates="student")
    
    def __repr__(self):
        return f"<StudentProfile(student_id='{self.student_id}', name='{self.name}', cgpa={self.current_cgpa})>"


class ChatLog(Base):
    """Chat log model for tracking conversation history"""
    __tablename__ = "chat_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("student_profiles.student_id"), nullable=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    sentiment_detected = Column(String, nullable=True)  # anxious, technical, neutral, confident
    persona_used = Column(String, nullable=True)  # strict_recruiter, supportive_mentor
    domain = Column(String, nullable=True)  # career_guidance, mock_interview, resume_review, etc.
    intent = Column(String, nullable=True)  # Specific intent classification
    
    # Relationship to student profile
    student = relationship("StudentProfile", back_populates="chat_logs")
    
    def __repr__(self):
        return f"<ChatLog(id={self.id}, student_id='{self.student_id}', timestamp={self.timestamp})>"


# Database setup functions
def get_engine(database_url: str = "sqlite:///./data/career_companion.db"):
    """Create and return database engine"""
    return create_engine(database_url, connect_args={"check_same_thread": False})


def get_session_maker(engine):
    """Create and return session maker"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database(database_url: str = "sqlite:///./data/career_companion.db"):
    """Initialize database and create all tables"""
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine
