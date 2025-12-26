"""
Session management service for conversation context
"""
import uuid
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import json

from backend.models.schemas import SessionContext, ChatMessage, MessageRole
from backend.config import config


class SessionManager:
    """Manages user sessions and conversation history"""
    
    def __init__(self):
        """Initialize session manager with in-memory storage"""
        # In production, use Redis or database
        self._sessions: Dict[str, SessionContext] = {}
        self._cleanup_interval = timedelta(minutes=config.SESSION_EXPIRE_MINUTES)
    
    def create_session(
        self,
        student_name: Optional[str] = None,
        major: Optional[str] = None,
        year: Optional[int] = None
    ) -> str:
        """
        Create a new session
        
        Args:
            student_name: Student's name
            major: Student's major
            year: Student's year
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        session = SessionContext(
            session_id=session_id,
            student_name=student_name,
            major=major,
            year=year
        )
        self._sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Get session by ID
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session context or None if expired/not found
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        # Check expiration
        if datetime.now() - session.last_activity > self._cleanup_interval:
            self.delete_session(session_id)
            return None
        
        return session
    
    def update_session_activity(self, session_id: str):
        """Update last activity timestamp"""
        session = self._sessions.get(session_id)
        if session:
            session.last_activity = datetime.now()
    
    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Add message to conversation history
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional metadata
        
        Returns:
            Success status
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata
        )
        session.conversation_history.append(message)
        self.update_session_activity(session_id)
        return True
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Get conversation history
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return (most recent)
        
        Returns:
            List of chat messages
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        history = session.conversation_history
        if limit:
            return history[-limit:]
        return history
    
    def update_user_context(
        self,
        session_id: str,
        student_name: Optional[str] = None,
        major: Optional[str] = None,
        year: Optional[int] = None,
        target_companies: Optional[List[str]] = None,
        target_roles: Optional[List[str]] = None
    ) -> bool:
        """
        Update user context information
        
        Args:
            session_id: Session identifier
            student_name: Student's name
            major: Student's major
            year: Student's year
            target_companies: List of target companies
            target_roles: List of target roles
        
        Returns:
            Success status
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        if student_name:
            session.student_name = student_name
        if major:
            session.major = major
        if year:
            session.year = year
        if target_companies:
            session.target_companies = target_companies
        if target_roles:
            session.target_roles = target_roles
        
        self.update_session_activity(session_id)
        return True
    
    def get_user_context(self, session_id: str) -> Optional[Dict]:
        """
        Get user context as dictionary
        
        Args:
            session_id: Session identifier
        
        Returns:
            User context dictionary
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "student_name": session.student_name,
            "major": session.major,
            "year": session.year,
            "target_companies": session.target_companies,
            "target_roles": session.target_roles
        }
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Success status
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = [
            sid for sid, session in self._sessions.items()
            if current_time - session.last_activity > self._cleanup_interval
        ]
        
        for sid in expired_sessions:
            self.delete_session(sid)
        
        return len(expired_sessions)
    
    def export_session(self, session_id: str) -> Optional[str]:
        """
        Export session as JSON string
        
        Args:
            session_id: Session identifier
        
        Returns:
            JSON string of session data
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        return session.model_dump_json(indent=2)


# Singleton instance
session_manager = SessionManager()
