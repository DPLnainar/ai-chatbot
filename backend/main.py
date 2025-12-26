"""
FastAPI application for Career Companion chatbot
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import Optional
import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import config
from backend.models.schemas import (
    ChatRequest, ChatResponse, MessageRole, DomainType
)
from backend.services.llm_client import llm_client
from backend.services.session import session_manager
from backend.services.intent_router import intent_router
from backend.services.knowledge_base import knowledge_base
from backend.services.database_service import DatabaseService
from backend.prompts.system_prompts import get_system_prompt, format_conversation_history


# Initialize FastAPI app
app = FastAPI(
    title="Career Companion API",
    description="AI Placement Officer for Engineering Students",
    version="1.0.0"
)

# Initialize database service
db_service = DatabaseService()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        config.validate()
        print("✓ Configuration validated")
        print(f"✓ LLM Provider: {llm_client.provider}")
        print(f"✓ Model: {llm_client.model}")
        
        # Load knowledge base
        stats = knowledge_base.get_collection_stats()
        print(f"✓ Knowledge base loaded: {stats['total_documents']} documents")
        
        # Initialize database
        print("✓ Database initialized")
        
    except Exception as e:
        print(f"✗ Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down Career Companion...")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the chat interface"""
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "chat.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <body>
            <h1>Career Companion API</h1>
            <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Career Companion",
        "version": "1.0.0"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Main chat endpoint
    
    Args:
        request: Chat request with message and optional session_id
        background_tasks: FastAPI background tasks
    
    Returns:
        Chat response with bot's reply
    """
    logger.info(f"=== CHAT ENDPOINT CALLED ===")
    logger.info(f"Message: {request.message}")
    logger.info(f"Session ID: {request.session_id}")
    try:
        logger.info("Step 1: Getting/creating session...")
        # Get or create session
        session_id = request.session_id
        if not session_id:
            session_id = session_manager.create_session()
        
        session = session_manager.get_session(session_id)
        if not session:
            session_id = session_manager.create_session()
            session = session_manager.get_session(session_id)
        
        # Update user context if provided
        if request.user_context:
            session_manager.update_user_context(session_id, **request.user_context)
        
        # Add user message to history
        session_manager.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=request.message
        )
        
        # Classify intent and route to domain (use keyword-only for now to avoid LLM call issues)
        classification = await intent_router.classify_intent(request.message, use_llm=False)
        
        # Search knowledge base for relevant information
        relevant_docs = knowledge_base.search(
            query=request.message,
            top_k=3,
            filter_metadata={"domain": classification.domain.value} if classification.domain != DomainType.GENERAL else None
        )
        
        # Build context from knowledge base
        kb_context = ""
        if relevant_docs:
            kb_context = "\n\n**Relevant Information:**\n"
            for doc in relevant_docs:
                kb_context += f"- {doc.content}\n"
        
        # Get user context
        user_context = session_manager.get_user_context(session_id)
        
        # Generate system prompt with persona
        system_prompt = get_system_prompt(
            domain=classification.domain.value,
            user_context=user_context,
            persona=classification.persona.value
        )
        
        # Add knowledge base context to system prompt
        if kb_context:
            system_prompt += kb_context
        
        # Get conversation history
        history = session_manager.get_conversation_history(session_id, limit=10)
        
        # Generate response
        response_text = await llm_client.generate_response(
            messages=history,
            system_prompt=system_prompt
        )
        
        # Add assistant response to history
        session_manager.add_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=response_text,
            metadata={
                "domain": classification.domain.value,
                "confidence": classification.confidence,
                "intent": classification.intent
            }
        )
        
        # Prepare suggested actions based on domain
        suggested_actions = _get_suggested_actions(classification.domain)
        
        # Prepare sources
        sources = [doc.source for doc in relevant_docs] if relevant_docs else None
        
        # Detect sentiment and log chat to database
        sentiment = db_service.detect_sentiment(request.message)
        student_id = user_context.get("student_id") if user_context else None
        
        background_tasks.add_task(
            db_service.log_chat,
            session_id=session_id,
            user_message=request.message,
            bot_response=response_text,
            student_id=student_id,
            sentiment=sentiment,
            persona=classification.persona.value,
            domain=classification.domain.value,
            intent=classification.intent
        )
        
        # Schedule session cleanup in background
        background_tasks.add_task(session_manager.cleanup_expired_sessions)
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            domain=classification.domain,
            suggested_actions=suggested_actions,
            sources=sources
        )
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "student_name": session.student_name,
        "major": session.major,
        "year": session.year,
        "target_companies": session.target_companies,
        "target_roles": session.target_roles,
        "message_count": len(session.conversation_history),
        "created_at": session.created_at,
        "last_activity": session.last_activity
    }


@app.get("/api/session/{session_id}/history")
async def get_session_history(session_id: str, limit: Optional[int] = None):
    """Get conversation history for a session"""
    history = session_manager.get_conversation_history(session_id, limit=limit)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found or empty")
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in history
        ]
    }


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    success = session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}


@app.get("/api/knowledge/stats")
async def knowledge_stats():
    """Get knowledge base statistics"""
    return knowledge_base.get_collection_stats()


@app.post("/api/knowledge/search")
async def search_knowledge(query: str, top_k: int = 5, domain: Optional[str] = None):
    """Search knowledge base"""
    filter_metadata = {"domain": domain} if domain else None
    docs = knowledge_base.search(query, top_k=top_k, filter_metadata=filter_metadata)
    
    return {
        "query": query,
        "results": [
            {
                "content": doc.content,
                "source": doc.source,
                "relevance_score": doc.relevance_score,
                "metadata": doc.metadata
            }
            for doc in docs
        ]
    }


# Student Profile Management Endpoints
@app.post("/api/students")
async def create_student(
    student_id: str,
    name: str,
    department: str,
    cgpa: Optional[float] = None,
    skills: Optional[str] = None,
    arrears_count: int = 0,
    year: Optional[int] = None,
    target_companies: Optional[str] = None
):
    """Create a new student profile"""
    try:
        student = db_service.create_student(
            student_id=student_id,
            name=name,
            department=department,
            cgpa=cgpa,
            skills=skills,
            arrears_count=arrears_count,
            year=year,
            target_companies=target_companies
        )
        return {
            "message": "Student profile created successfully",
            "student_id": student.student_id,
            "name": student.name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating student: {str(e)}")


@app.get("/api/students/{student_id}")
async def get_student(student_id: str):
    """Get student profile by ID"""
    student = db_service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "student_id": student.student_id,
        "name": student.name,
        "department": student.department,
        "cgpa": student.current_cgpa,
        "skills": student.skills,
        "arrears_count": student.arrears_count,
        "year": student.year,
        "target_companies": student.target_companies,
        "created_at": student.created_at.isoformat(),
        "updated_at": student.updated_at.isoformat()
    }


@app.put("/api/students/{student_id}")
async def update_student(student_id: str, **kwargs):
    """Update student profile"""
    student = db_service.update_student(student_id, **kwargs)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "message": "Student profile updated successfully",
        "student_id": student.student_id
    }


@app.delete("/api/students/{student_id}")
async def delete_student(student_id: str):
    """Delete student profile"""
    success = db_service.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Student profile deleted successfully"}


@app.get("/api/students")
async def list_students(limit: int = 100, offset: int = 0):
    """List all student profiles"""
    students = db_service.list_students(limit=limit, offset=offset)
    return {
        "count": len(students),
        "students": [
            {
                "student_id": s.student_id,
                "name": s.name,
                "department": s.department,
                "cgpa": s.current_cgpa,
                "year": s.year
            }
            for s in students
        ]
    }


# Chat Analytics Endpoints
@app.get("/api/analytics/chat-history")
async def get_chat_history(
    student_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 50
):
    """Get chat history"""
    chats = db_service.get_chat_history(student_id=student_id, session_id=session_id, limit=limit)
    return {
        "count": len(chats),
        "chats": [
            {
                "id": chat.id,
                "student_id": chat.student_id,
                "session_id": chat.session_id,
                "user_message": chat.user_message,
                "bot_response": chat.bot_response,
                "timestamp": chat.timestamp.isoformat(),
                "sentiment": chat.sentiment_detected,
                "persona": chat.persona_used,
                "domain": chat.domain
            }
            for chat in chats
        ]
    }


@app.get("/api/analytics/sentiment-stats")
async def get_sentiment_stats(student_id: Optional[str] = None):
    """Get sentiment statistics"""
    stats = db_service.get_sentiment_stats(student_id=student_id)
    return {
        "student_id": student_id,
        "sentiment_stats": stats
    }


@app.get("/api/analytics/persona-usage")
async def get_persona_usage(student_id: Optional[str] = None):
    """Get persona usage statistics"""
    stats = db_service.get_persona_usage(student_id=student_id)
    return {
        "student_id": student_id,
        "persona_usage": stats
    }


def _get_suggested_actions(domain: DomainType) -> list:
    """Get suggested actions based on domain"""
    actions_map = {
        DomainType.SOFTWARE_DEV: [
            "Review my resume for software roles",
            "Practice coding interview questions",
            "Suggest projects for my portfolio",
            "Explain system design concepts"
        ],
        DomainType.AI_ML: [
            "Review my ML projects",
            "Explain ML algorithms",
            "Suggest AI/ML learning resources",
            "Practice ML interview questions"
        ],
        DomainType.VLSI: [
            "Prepare for VLSI interviews",
            "Explain RTL design concepts",
            "Suggest VLSI projects",
            "Review semiconductor companies"
        ],
        DomainType.EMBEDDED: [
            "Prepare for embedded interviews",
            "Suggest embedded projects",
            "Explain microcontroller concepts",
            "Review IoT companies"
        ],
        DomainType.MECHANICAL: [
            "Review CAD skills needed",
            "Prepare for core mechanical interviews",
            "Suggest mechanical projects",
            "Explain manufacturing processes"
        ],
        DomainType.SOFT_SKILLS: [
            "Practice mock behavioral interview",
            "Improve communication skills",
            "Get feedback on presentation",
            "Develop leadership skills"
        ],
        DomainType.GENERAL: [
            "Review my resume",
            "Research companies",
            "Prepare for interviews",
            "Get career advice"
        ]
    }
    
    return actions_map.get(domain, actions_map[DomainType.GENERAL])


if __name__ == "__main__":
    print("🚀 Starting Career Companion API...")
    print(f"📍 Server: http://{config.HOST}:{config.PORT}")
    print(f"📚 API Docs: http://{config.HOST}:{config.PORT}/docs")
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.ENVIRONMENT == "development"
    )
