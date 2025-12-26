# Career Companion - AI Placement Officer

An intelligent chatbot system designed to prepare engineering students for corporate placements. The Career Companion provides personalized guidance across software development, core engineering domains, and soft skills with **persistent database tracking** and **analytics**.

## ✨ Features

### Core Capabilities
- **Dual Persona System**: 
  - 🎯 **Strict Recruiter**: Mock interviews, technical assessments, resume critiques
  - 💚 **Supportive Mentor**: Career guidance, confidence building, study planning
- **Multi-Domain Expertise**: Software Development (Full Stack, AI/ML), Core Engineering (VLSI, Embedded, Mechanical)
- **Industry Standards**: Emphasizes hands-on skills over theory
- **Smart Formatting**: Concise responses under 150 words, bullet points, human-like interaction

### Database & Analytics 🗄️
- **Student Profiles**: Track CGPA, skills, arrears, target companies
- **Chat History**: Complete conversation logs with timestamps
- **Sentiment Analysis**: Automatic detection (anxious, confident, technical, neutral)
- **Persona Tracking**: Monitor which persona is most effective
- **Progress Analytics**: View sentiment trends and engagement patterns

### Placement Preparation
- Resume reviews and feedback
- Mock technical interviews
- Coding practice guidance
- Soft skills coaching
- Company-specific insights

## 🚀 Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **LLM**: OpenAI GPT-4 Turbo
- **Database**: SQLAlchemy + SQLite
- **Knowledge Base**: In-memory vector search
- **Session Store**: In-memory (production: Redis)
- **Frontend**: HTML/JS chat interface + CLI tool

## Setup

1. Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

3. Run the backend server:
```bash
cd backend
python main.py
```

4. Access the chat interface:
- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **CLI**: `python frontend/cli_chat.py`

## 📊 Database Features

All conversations are automatically logged with sentiment analysis and persona tracking!

### Quick Database Commands
```powershell
# Create student profile
Invoke-RestMethod -Uri "http://localhost:8000/api/students" -Method Post -Body (@{
    student_id = "CS2021001"; name = "John Doe"; department = "CS"; cgpa = 8.5
} | ConvertTo-Json) -ContentType "application/json"

# View analytics
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/sentiment-stats?student_id=CS2021001"
```

**See [QUICKSTART.md](QUICKSTART.md) for detailed examples and [docs/DATABASE.md](docs/DATABASE.md) for complete API documentation.**

## Project Structure

```
AI botPlacemnt/
├── backend/
│   ├── main.py                 # FastAPI with 15+ API endpoints
│   ├── config.py               # Configuration management
│   ├── models/
│   │   ├── schemas.py          # Pydantic models
│   │   └── database.py         # SQLAlchemy ORM models ✨
│   ├── services/
│   │   ├── llm_client.py       # OpenAI GPT-4 integration
│   │   ├── session.py          # Session management
│   │   ├── intent_router.py    # Domain & persona routing
│   │   ├── knowledge_base.py   # Knowledge retrieval
│   │   └── database_service.py # Database operations ✨
│   └── prompts/
│       └── system_prompts.py   # Dual persona system prompts
├── frontend/
│   ├── chat.html               # Web interface
│   └── cli_chat.py             # CLI tool
├── data/
│   └── career_companion.db     # SQLite database ✨
├── docs/
│   ├── DATABASE.md             # Database documentation ✨
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── conversation-design.md
└── QUICKSTART.md               # Quick reference ✨
```

## 🎯 Key Features

- **Automatic Chat Logging**: Every conversation saved with sentiment and persona
- **Student Tracking**: CGPA, skills, arrears, target companies
- **Analytics**: Sentiment trends, persona effectiveness, conversation patterns
- **REST API**: 15+ endpoints for profiles, chats, and analytics
- **Smart Personas**: Auto-switches between Strict Recruiter and Supportive Mentor

## Usage

Ask the Career Companion about:
- Resume improvement tips
- Mock interview practice
- Technical skill development
- Company-specific preparation
- Soft skills coaching
- Career path guidance

## License

MIT
