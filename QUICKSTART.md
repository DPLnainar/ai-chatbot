# 🚀 Quick Start Guide - Database Features

## Server Status
✅ **Running at**: http://localhost:8000  
✅ **API Docs**: http://localhost:8000/docs  
✅ **Database**: SQLite at `data/career_companion.db`

## Quick Test Commands

### 1. Create a Student Profile
```powershell
$body = @{
    student_id = "CS2021001"
    name = "John Doe"
    department = "Computer Science"
    cgpa = 8.5
    skills = "Python, Java, React, Node.js"
    arrears_count = 0
    year = 3
    target_companies = "Google, Microsoft, Amazon"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/students" -Method Post -Body $body -ContentType "application/json"
```

### 2. Get Student Info
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/students/CS2021001"
```

### 3. Chat with Student Context
```powershell
$chatBody = @{
    message = "I'm worried about my coding interview preparation"
    user_context = @{
        student_id = "CS2021001"
        name = "John Doe"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $chatBody -ContentType "application/json"
```

### 4. View Chat History
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/chat-history?student_id=CS2021001"
```

### 5. Get Sentiment Statistics
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/sentiment-stats?student_id=CS2021001"
```

### 6. Get Persona Usage
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/persona-usage?student_id=CS2021001"
```

## Features Automatically Active

### ✅ Every Chat Message is Logged With:
- User message and bot response
- Timestamp
- Sentiment detection (anxious, confident, technical, neutral)
- Persona used (strict_recruiter, supportive_mentor)
- Domain classification (software_dev, ai_ml, etc.)
- Student ID (if provided)

### ✅ Sentiment Keywords Detected:
- **Anxious**: worried, nervous, confused, help me, don't know
- **Confident**: ready, prepared, excited, I can, let's do
- **Technical**: algorithm, code, data structure, debugging
- **Neutral**: Everything else

### ✅ Database Tables Created:
1. `student_profiles` - Student information
2. `chat_logs` - All conversations with analytics

## Using the Web Interface

1. **Open Browser**: http://localhost:8000
2. **Chat Interface**: Fully functional, automatically logs to database
3. **API Docs**: http://localhost:8000/docs for interactive testing

## Using the CLI

```powershell
cd "c:\Users\ganes\OneDrive\Desktop\AI botPlacemnt"
.\venv\Scripts\Activate.ps1
python frontend\cli_chat.py
```

## View Database Directly

Using any SQLite browser or command:
```powershell
# Install sqlite if needed
# Then open database
sqlite3 data\career_companion.db

# Query students
SELECT * FROM student_profiles;

# Query recent chats
SELECT user_message, bot_response, sentiment_detected, persona_used 
FROM chat_logs 
ORDER BY timestamp DESC 
LIMIT 10;
```

## Python API Usage

```python
from backend.services.database_service import DatabaseService

db = DatabaseService()

# Create student
student = db.create_student(
    student_id="CS2021001",
    name="John Doe",
    department="CS",
    cgpa=8.5
)

# Log chat
chat = db.log_chat(
    session_id="abc123",
    user_message="I need help",
    bot_response="Sure, let's work on it!",
    student_id="CS2021001",
    sentiment="anxious"
)

# Get analytics
stats = db.get_sentiment_stats("CS2021001")
print(stats)  # {'anxious': 5, 'confident': 3, ...}
```

## Common Use Cases

### Track Student Progress
1. Create student profile with initial CGPA and skills
2. Have multiple chat sessions
3. View sentiment trends to see confidence growth
4. Update profile as skills improve

### Monitor Chatbot Effectiveness
1. Check persona usage statistics
2. Analyze which persona is used more
3. Review sentiment distribution
4. Identify areas where students need more support

### Generate Reports
1. Export chat history for specific students
2. Analyze sentiment patterns over time
3. Track which domains students ask about most
4. Measure student engagement

## Quick Reference: All Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Chat with AI (auto-logs to DB) |
| POST | `/api/students` | Create student profile |
| GET | `/api/students/{id}` | Get student info |
| PUT | `/api/students/{id}` | Update student |
| DELETE | `/api/students/{id}` | Delete student |
| GET | `/api/students` | List all students |
| GET | `/api/analytics/chat-history` | View conversations |
| GET | `/api/analytics/sentiment-stats` | Sentiment breakdown |
| GET | `/api/analytics/persona-usage` | Persona statistics |

## Troubleshooting

**Database not found?**
- Check `data/` directory exists
- Server creates it automatically on startup

**Chat not logging?**
- Ensure server is running
- Check terminal for errors
- Verify student_id in user_context

**API errors?**
- Visit http://localhost:8000/docs
- Try endpoints interactively
- Check request format matches examples

## Documentation Files

- `docs/DATABASE.md` - Complete database documentation
- `docs/IMPLEMENTATION_SUMMARY.md` - What was implemented
- `docs/SETUP.md` - Initial setup instructions
- `docs/conversation-design.md` - Conversation design guide

## Support

Server logs show all operations:
```
✓ Configuration validated
✓ LLM Provider: openai
✓ Model: gpt-4-turbo-preview
✓ Knowledge base loaded: 10 documents
✓ Database initialized
INFO: Application startup complete.
```

If you see all ✓ marks, everything is working!

---

**🎉 Database integration is fully functional and ready to use!**
