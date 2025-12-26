"""
Database service for managing student profiles and chat logs
"""
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.database import StudentProfile, ChatLog, get_session_maker, init_database


class DatabaseService:
    """Service for handling database operations"""
    
    def __init__(self, database_url: str = "sqlite:///./data/career_companion.db"):
        """Initialize database service"""
        self.engine = init_database(database_url)
        self.SessionLocal = get_session_maker(self.engine)
    
    def get_db(self):
        """Get database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Student Profile Operations
    def create_student(self, student_id: str, name: str, department: str, 
                      cgpa: Optional[float] = None, skills: Optional[str] = None,
                      arrears_count: int = 0, year: Optional[int] = None,
                      target_companies: Optional[str] = None) -> StudentProfile:
        """Create a new student profile"""
        db = self.SessionLocal()
        try:
            student = StudentProfile(
                student_id=student_id,
                name=name,
                department=department,
                current_cgpa=cgpa,
                skills=skills,
                arrears_count=arrears_count,
                year=year,
                target_companies=target_companies
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            return student
        finally:
            db.close()
    
    def get_student(self, student_id: str) -> Optional[StudentProfile]:
        """Get student profile by ID"""
        db = self.SessionLocal()
        try:
            return db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
        finally:
            db.close()
    
    def update_student(self, student_id: str, **kwargs) -> Optional[StudentProfile]:
        """Update student profile"""
        db = self.SessionLocal()
        try:
            student = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
            if student:
                for key, value in kwargs.items():
                    if hasattr(student, key) and value is not None:
                        setattr(student, key, value)
                student.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(student)
            return student
        finally:
            db.close()
    
    def delete_student(self, student_id: str) -> bool:
        """Delete student profile"""
        db = self.SessionLocal()
        try:
            student = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
            if student:
                db.delete(student)
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    def list_students(self, limit: int = 100, offset: int = 0) -> List[StudentProfile]:
        """List all student profiles"""
        db = self.SessionLocal()
        try:
            return db.query(StudentProfile).offset(offset).limit(limit).all()
        finally:
            db.close()
    
    # Chat Log Operations
    def log_chat(self, session_id: str, user_message: str, bot_response: str,
                 student_id: Optional[str] = None, sentiment: Optional[str] = None,
                 persona: Optional[str] = None, domain: Optional[str] = None,
                 intent: Optional[str] = None) -> ChatLog:
        """Log a chat interaction"""
        db = self.SessionLocal()
        try:
            chat_log = ChatLog(
                student_id=student_id,
                session_id=session_id,
                user_message=user_message,
                bot_response=bot_response,
                sentiment_detected=sentiment,
                persona_used=persona,
                domain=domain,
                intent=intent
            )
            db.add(chat_log)
            db.commit()
            db.refresh(chat_log)
            return chat_log
        finally:
            db.close()
    
    def get_chat_history(self, student_id: Optional[str] = None, 
                        session_id: Optional[str] = None,
                        limit: int = 50) -> List[ChatLog]:
        """Get chat history by student or session"""
        db = self.SessionLocal()
        try:
            query = db.query(ChatLog)
            if student_id:
                query = query.filter(ChatLog.student_id == student_id)
            if session_id:
                query = query.filter(ChatLog.session_id == session_id)
            return query.order_by(ChatLog.timestamp.desc()).limit(limit).all()
        finally:
            db.close()
    
    def get_sentiment_stats(self, student_id: Optional[str] = None) -> Dict[str, int]:
        """Get sentiment statistics"""
        db = self.SessionLocal()
        try:
            query = db.query(ChatLog)
            if student_id:
                query = query.filter(ChatLog.student_id == student_id)
            
            chats = query.all()
            stats = {}
            for chat in chats:
                sentiment = chat.sentiment_detected or "neutral"
                stats[sentiment] = stats.get(sentiment, 0) + 1
            return stats
        finally:
            db.close()
    
    def get_persona_usage(self, student_id: Optional[str] = None) -> Dict[str, int]:
        """Get persona usage statistics"""
        db = self.SessionLocal()
        try:
            query = db.query(ChatLog)
            if student_id:
                query = query.filter(ChatLog.student_id == student_id)
            
            chats = query.all()
            stats = {}
            for chat in chats:
                persona = chat.persona_used or "unknown"
                stats[persona] = stats.get(persona, 0) + 1
            return stats
        finally:
            db.close()
    
    def detect_sentiment(self, message: str) -> str:
        """Simple sentiment detection based on keywords"""
        message_lower = message.lower()
        
        # Anxious keywords
        anxious_keywords = ["worried", "anxious", "nervous", "scared", "afraid", "confused", 
                          "don't know", "not sure", "help me", "stressed", "pressure"]
        if any(keyword in message_lower for keyword in anxious_keywords):
            return "anxious"
        
        # Confident keywords
        confident_keywords = ["ready", "prepared", "confident", "excited", "looking forward",
                            "i can", "i will", "let's do", "bring it on"]
        if any(keyword in message_lower for keyword in confident_keywords):
            return "confident"
        
        # Technical keywords
        technical_keywords = ["algorithm", "code", "programming", "technical", "interview question",
                            "data structure", "leetcode", "coding", "debug", "implement"]
        if any(keyword in message_lower for keyword in technical_keywords):
            return "technical"
        
        return "neutral"
