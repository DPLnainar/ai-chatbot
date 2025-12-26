# Database Integration Guide

## Overview
Career Companion AI now includes full database support using SQLAlchemy and SQLite for persistent storage of student profiles and chat logs.

## Database Location
- **File**: `data/career_companion.db`
- **Type**: SQLite database
- **Created**: Automatically on first run

## Database Schema

### Student Profiles Table
Stores complete student information for personalized career guidance.

**Table Name**: `student_profiles`

| Column | Type | Description |
|--------|------|-------------|
| student_id | String (Primary Key) | Unique student identifier |
| name | String | Student's full name |
| department | String | Engineering department (CS, ECE, Mechanical, etc.) |
| current_cgpa | Float | Current CGPA (0.0 - 10.0) |
| skills | Text | Comma-separated list of skills |
| arrears_count | Integer | Number of backlogs/arrears |
| year | Integer | Current year (1, 2, 3, 4) |
| target_companies | Text | Comma-separated target companies |
| created_at | DateTime | Profile creation timestamp |
| updated_at | DateTime | Last update timestamp |

### Chat Logs Table
Tracks all conversations with sentiment and persona analytics.

**Table Name**: `chat_logs`

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (Primary Key) | Auto-increment chat ID |
| student_id | String (Foreign Key) | Links to student_profiles |
| session_id | String | Unique session identifier |
| user_message | Text | Student's message |
| bot_response | Text | AI's response |
| timestamp | DateTime | Message timestamp |
| sentiment_detected | String | anxious, technical, neutral, confident |
| persona_used | String | strict_recruiter, supportive_mentor |
| domain | String | software_dev, ai_ml, vlsi, etc. |
| intent | String | Specific intent classification |

## API Endpoints

### Student Profile Management

#### 1. Create Student Profile
```http
POST /api/students
Content-Type: application/json

{
  "student_id": "CS2021001",
  "name": "John Doe",
  "department": "Computer Science",
  "cgpa": 8.5,
  "skills": "Python, Java, React, Node.js",
  "arrears_count": 0,
  "year": 3,
  "target_companies": "Google, Microsoft, Amazon"
}
```

**Response**:
```json
{
  "message": "Student profile created successfully",
  "student_id": "CS2021001",
  "name": "John Doe"
}
```

#### 2. Get Student Profile
```http
GET /api/students/{student_id}
```

**Example**: `GET /api/students/CS2021001`

**Response**:
```json
{
  "student_id": "CS2021001",
  "name": "John Doe",
  "department": "Computer Science",
  "cgpa": 8.5,
  "skills": "Python, Java, React, Node.js",
  "arrears_count": 0,
  "year": 3,
  "target_companies": "Google, Microsoft, Amazon",
  "created_at": "2025-12-24T10:30:00",
  "updated_at": "2025-12-24T10:30:00"
}
```

#### 3. Update Student Profile
```http
PUT /api/students/{student_id}
Content-Type: application/json

{
  "cgpa": 8.7,
  "skills": "Python, Java, React, Node.js, Docker",
  "target_companies": "Google, Microsoft, Amazon, Netflix"
}
```

#### 4. Delete Student Profile
```http
DELETE /api/students/{student_id}
```

#### 5. List All Students
```http
GET /api/students?limit=100&offset=0
```

**Response**:
```json
{
  "count": 25,
  "students": [
    {
      "student_id": "CS2021001",
      "name": "John Doe",
      "department": "Computer Science",
      "cgpa": 8.5,
      "year": 3
    }
  ]
}
```

### Chat Analytics Endpoints

#### 1. Get Chat History
```http
GET /api/analytics/chat-history?student_id=CS2021001&limit=50
```

**Query Parameters**:
- `student_id` (optional): Filter by student
- `session_id` (optional): Filter by session
- `limit` (default: 50): Maximum results

**Response**:
```json
{
  "count": 10,
  "chats": [
    {
      "id": 1,
      "student_id": "CS2021001",
      "session_id": "abc123",
      "user_message": "I'm worried about my coding interview",
      "bot_response": "Don't worry! Let's practice...",
      "timestamp": "2025-12-24T14:30:00",
      "sentiment": "anxious",
      "persona": "supportive_mentor",
      "domain": "software_dev"
    }
  ]
}
```

#### 2. Get Sentiment Statistics
```http
GET /api/analytics/sentiment-stats?student_id=CS2021001
```

**Response**:
```json
{
  "student_id": "CS2021001",
  "sentiment_stats": {
    "anxious": 5,
    "confident": 8,
    "technical": 12,
    "neutral": 3
  }
}
```

#### 3. Get Persona Usage Statistics
```http
GET /api/analytics/persona-usage?student_id=CS2021001
```

**Response**:
```json
{
  "student_id": "CS2021001",
  "persona_usage": {
    "strict_recruiter": 15,
    "supportive_mentor": 13
  }
}
```

## Automatic Chat Logging

All conversations are automatically logged to the database with:
- **Sentiment detection**: Automatically analyzes student's emotional state
- **Persona tracking**: Records which persona (Strict/Supportive) was used
- **Domain classification**: Tracks the technical domain of conversation
- **Student linking**: Associates chats with student profiles if student_id is provided

### Example Chat Request with Student Context
```http
POST /api/chat
Content-Type: application/json

{
  "message": "I need help preparing for Google interviews",
  "session_id": "abc123",
  "user_context": {
    "student_id": "CS2021001",
    "name": "John Doe",
    "department": "Computer Science",
    "cgpa": 8.5,
    "skills": "Python, Java"
  }
}
```

## Sentiment Detection Keywords

The system automatically detects sentiment based on message content:

### Anxious
- worried, anxious, nervous, scared, afraid
- confused, don't know, not sure
- help me, stressed, pressure

### Confident
- ready, prepared, confident, excited
- looking forward, i can, i will
- let's do, bring it on

### Technical
- algorithm, code, programming, technical
- interview question, data structure
- leetcode, coding, debug, implement

### Neutral
- Default when no specific keywords detected

## Database Service API

### Python Integration Example

```python
from backend.services.database_service import DatabaseService

# Initialize service
db_service = DatabaseService()

# Create student
student = db_service.create_student(
    student_id="CS2021001",
    name="John Doe",
    department="Computer Science",
    cgpa=8.5,
    skills="Python, Java, React",
    year=3
)

# Get student
student = db_service.get_student("CS2021001")

# Update student
student = db_service.update_student(
    "CS2021001",
    cgpa=8.7,
    skills="Python, Java, React, Docker"
)

# Log chat
chat = db_service.log_chat(
    session_id="abc123",
    user_message="Tell me about system design",
    bot_response="System design involves...",
    student_id="CS2021001",
    sentiment="technical",
    persona="strict_recruiter",
    domain="software_dev"
)

# Get analytics
sentiment_stats = db_service.get_sentiment_stats("CS2021001")
persona_usage = db_service.get_persona_usage("CS2021001")
```

## Benefits

1. **Persistent Storage**: All data survives server restarts
2. **Student Tracking**: Monitor individual student progress
3. **Sentiment Analysis**: Understand student emotional patterns
4. **Persona Optimization**: See which persona works best
5. **Analytics Dashboard**: Ready for future analytics features
6. **Conversation History**: Full audit trail of all interactions

## Testing the Database

### Using cURL

**Create a student**:
```bash
curl -X POST "http://localhost:8000/api/students" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "CS2021001",
    "name": "Test Student",
    "department": "Computer Science",
    "cgpa": 8.5,
    "skills": "Python, Java",
    "year": 3
  }'
```

**Get student**:
```bash
curl "http://localhost:8000/api/students/CS2021001"
```

**Get chat history**:
```bash
curl "http://localhost:8000/api/analytics/chat-history?student_id=CS2021001"
```

### Using the Web Interface

1. Open http://localhost:8000/docs
2. Try the interactive API documentation
3. All endpoints are testable from the browser

## Database Backup

To backup your database:
```bash
cp data/career_companion.db data/career_companion_backup.db
```

## Migration Notes

- Database schema is automatically created on first run
- No manual SQL setup required
- Compatible with SQLite 3.x
- Can be migrated to PostgreSQL/MySQL for production

## Troubleshooting

**Database not created?**
- Check that `data/` directory exists
- Verify write permissions
- Check server logs for initialization errors

**Foreign key errors?**
- Ensure student profile exists before linking chats
- student_id in chat_logs must match student_profiles.student_id

**Query slow?**
- Database includes indexes on:
  - student_id (both tables)
  - session_id (chat_logs)
  - timestamp (chat_logs)
