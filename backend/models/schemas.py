from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PersonaType(str, Enum):
    """Chatbot persona modes"""
    STRICT_RECRUITER = "strict_recruiter"
    SUPPORTIVE_MENTOR = "supportive_mentor"


class DomainType(str, Enum):
    """Student query domain classification"""
    SOFTWARE_DEV = "software_development"
    AI_ML = "ai_ml"
    VLSI = "vlsi"
    EMBEDDED = "embedded"
    MECHANICAL = "mechanical"
    SOFT_SKILLS = "soft_skills"
    GENERAL = "general"


class MessageRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Single chat message"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Incoming chat request"""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chatbot response"""
    response: str
    session_id: str
    domain: Optional[DomainType] = None
    suggested_actions: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SessionContext(BaseModel):
    """User session context"""
    session_id: str
    student_name: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    target_companies: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    conversation_history: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)


class IntentClassification(BaseModel):
    """Intent classification result"""
    domain: DomainType
    confidence: float
    intent: str
    persona: PersonaType = PersonaType.SUPPORTIVE_MENTOR
    entities: Dict[str, Any] = {}


class KnowledgeDocument(BaseModel):
    """Knowledge base document"""
    content: str
    source: str
    metadata: Dict[str, Any] = {}
    relevance_score: Optional[float] = None
