# Flow Architecture: Message → Prompt → Response

## Core Concept

```
Student Message + Context → Generate System Prompt → Call LLM → Return Response
```

## Two Implementations

### 1. Simple Version ([backend/simple_main.py](../backend/simple_main.py))

**Purpose**: Clear, minimal implementation showing the core flow

**Flow**:
```python
# Step 1: Receive message + context
ChatRequest(message, student_name, department, cgpa)

# Step 2: Generate system prompt
system_prompt = get_system_prompt(name, dept, cgpa)

# Step 3: Call OpenAI
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
)

# Step 4: Return response
return {"reply": bot_reply}
```

**Features**:
- ✅ Direct OpenAI API call
- ✅ Modular system prompt with persona logic
- ✅ CGPA-based warnings
- ✅ ~100 lines of code
- ✅ Runs on port 8001

**Use Cases**:
- Quick testing
- Understanding core architecture
- Minimal deployment
- API reference

---

### 2. Full Version ([backend/main.py](../backend/main.py))

**Purpose**: Production-ready with analytics, database, and session management

**Flow**:
```python
# Step 1: Receive message + context
ChatRequest(message, user_context={student_id, name, dept, cgpa})

# Step 2: Session & context management
- Get/create session
- Update user context
- Add message to history

# Step 3: Intent & persona classification
classification = intent_router.classify_intent(message)
# Automatically detects: strict_recruiter vs supportive_mentor

# Step 4: Knowledge base search
relevant_docs = knowledge_base.search(query, domain)

# Step 5: Generate system prompt (modular)
system_prompt = get_system_prompt(domain, user_context, persona)
system_prompt += kb_context  # Add relevant documents

# Step 6: Call OpenAI with conversation history
response = llm_client.generate_response(
    messages=conversation_history,
    system_prompt=system_prompt
)

# Step 7: Log to database (background)
db_service.log_chat(
    message, response, student_id, 
    sentiment, persona, domain
)

# Step 8: Return response + metadata
return ChatResponse(
    response, session_id, domain, 
    suggested_actions, sources
)
```

**Additional Features**:
- ✅ Session-based conversation history
- ✅ Automatic persona detection (Strict/Supportive)
- ✅ Domain classification (Software Dev, AI/ML, VLSI, etc.)
- ✅ Knowledge base with document retrieval
- ✅ Database logging with sentiment analysis
- ✅ Student profile management
- ✅ Analytics (sentiment stats, persona usage)
- ✅ Suggested actions per domain
- ✅ Source attribution
- ✅ Background task processing
- ✅ Runs on port 8000

**Use Cases**:
- Production deployment
- Analytics and reporting
- Multi-session conversations
- Student progress tracking

---

## System Prompt Comparison

### Simple Version
```python
def get_system_prompt(name, dept, cgpa):
    base_identity = f"You are Placement Officer. User is {name}, {dept}, {cgpa} CGPA."
    persona_logic = "STRICT MODE: technical questions / SUPPORTIVE MODE: career guidance"
    industry_standards = "DSA, System Design, Hands-on projects"
    
    return f"{base_identity}\n{persona_logic}\n{industry_standards}"
```

### Full Version
```python
def get_system_prompt(domain, user_context, persona):
    base_identity = f"""
    You are Career Companion AI Placement Officer.
    Student: {name}, {dept}, CGPA {cgpa}, Year {year}
    Skills: {skills}, Arrears: {arrears}
    """
    
    persona_logic = """
    🎯 STRICT RECRUITER MODE (persona='strict_recruiter')
    - Critical evaluation, mock interviews
    - No hints, ask follow-ups
    - CGPA-based eligibility warnings
    
    💚 SUPPORTIVE MENTOR MODE (persona='supportive_mentor')  
    - Empathetic, encouraging
    - Step-by-step roadmaps
    - Build confidence
    """
    
    industry_standards = """
    CS/IT: DSA, Cloud (AWS/Azure), Frameworks (React, Spring Boot)
    Core: IoT, CAD, Automation
    Hands-on skills > Theory
    """
    
    domain_specific = f"Domain: {domain} → specialized guidance"
    
    formatting_rules = """
    - Under 150 words
    - Bullet points
    - Act human, don't mention AI
    """
    
    return combined_prompt
```

---

## Request/Response Examples

### Simple Version

**Request**:
```json
{
  "message": "Can you conduct a mock interview?",
  "student_name": "Rahul",
  "department": "Computer Science",
  "cgpa": 8.5
}
```

**Response**:
```json
{
  "reply": "Sure! Let's start with a technical question...",
  "student": "Rahul",
  "cgpa": 8.5
}
```

### Full Version

**Request**:
```json
{
  "message": "Can you conduct a mock interview?",
  "session_id": "abc123",
  "user_context": {
    "student_id": "CS2021001",
    "name": "Rahul",
    "department": "Computer Science",
    "cgpa": 8.5,
    "skills": "Python, Java, React",
    "year": 3
  }
}
```

**Response**:
```json
{
  "response": "Sure! Let's start with a technical question...",
  "session_id": "abc123",
  "domain": "software_dev",
  "suggested_actions": [
    "Practice coding interview questions",
    "Review system design concepts"
  ],
  "sources": ["Mock Interview Guide", "Technical Questions Bank"]
}
```

---

## Running Both Versions

### Simple Version (Port 8001)
```bash
cd backend
python simple_main.py
```

Test:
```bash
python test_simple_flow.py
```

### Full Version (Port 8000)
```bash
cd backend
python main.py
```

Test via web interface: http://localhost:8000

---

## When to Use Which?

| Use Case | Simple | Full |
|----------|--------|------|
| Quick testing | ✅ | ❌ |
| Learning the architecture | ✅ | ❌ |
| Production deployment | ❌ | ✅ |
| Analytics required | ❌ | ✅ |
| Multi-turn conversations | ❌ | ✅ |
| Student tracking | ❌ | ✅ |
| Minimal dependencies | ✅ | ❌ |
| Database logging | ❌ | ✅ |
| Session management | ❌ | ✅ |

---

## Key Takeaway

**Both versions follow the same core pattern:**

```
Message + Context → System Prompt → LLM Response
```

The **simple version** is the blueprint showing the essential flow.

The **full version** adds production features while maintaining the same core architecture.

You can use the simple version to:
- Understand the flow clearly
- Test prompt changes quickly
- Debug issues
- Teach the architecture

Then deploy the full version for:
- Real-world usage
- Student tracking
- Analytics
- Multi-session conversations
