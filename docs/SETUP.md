# Career Companion - Setup Guide

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (or Azure OpenAI credentials)
- Git (optional)

---

## Installation Steps

### 1. Clone or Download the Project

```bash
cd "c:\Users\ganes\OneDrive\Desktop\AI botPlacemnt"
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` file with your credentials:

```env
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
```

**To get an OpenAI API key:**
1. Visit https://platform.openai.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new secret key
5. Copy and paste into `.env` file

### 5. Run the Backend Server

```powershell
cd backend
python main.py
```

You should see:
```
🚀 Starting Career Companion API...
📍 Server: http://0.0.0.0:8000
📚 API Docs: http://0.0.0.0:8000/docs
✓ Configuration validated
✓ LLM Provider: openai
✓ Model: gpt-4-turbo-preview
✓ Knowledge base loaded: 10 documents
```

### 6. Access the Chatbot

**Option A: Web Interface**
- Open browser and visit: `http://localhost:8000`
- Start chatting!

**Option B: CLI Interface**

Open a new terminal:

```powershell
cd "c:\Users\ganes\OneDrive\Desktop\AI botPlacemnt"
.\venv\Scripts\Activate.ps1
python frontend/cli_chat.py
```

---

## Usage Examples

### Web Interface
1. Open `http://localhost:8000`
2. Type your question in the input box
3. Press Enter or click Send
4. View response and suggested actions
5. Continue conversation with context

### CLI Interface
1. Run `python frontend/cli_chat.py`
2. Type questions at the prompt
3. Type `quit` to exit
4. Type `history` to view conversation
5. Type `clear` to clear screen

---

## Troubleshooting

### Error: "No LLM API key configured"
- Make sure you've created `.env` file from `.env.example`
- Add your `OPENAI_API_KEY` to `.env`
- Restart the server

### Error: "Could not connect to server"
- Ensure backend is running (`python backend/main.py`)
- Check if port 8000 is available
- Try accessing `http://localhost:8000/health`

### Error: "Module not found"
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`

### Slow Responses
- Check your internet connection
- Verify OpenAI API status
- Consider using a faster model (e.g., `gpt-3.5-turbo`)

---

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

- `POST /api/chat` - Send chat message
- `GET /api/session/{session_id}` - Get session info
- `GET /api/session/{session_id}/history` - Get conversation history
- `GET /api/knowledge/stats` - Knowledge base statistics
- `POST /api/knowledge/search` - Search knowledge base

---

## Adding Custom Knowledge

To add placement resources to the knowledge base:

```python
from backend.services.knowledge_base import knowledge_base

knowledge_base.add_document(
    content="Your placement resource content here",
    source="resource_name",
    metadata={"category": "interview", "domain": "software_development"}
)
```

---

## Customization

### Changing the Base Identity

Edit `backend/prompts/system_prompts.py`:

```python
BASE_IDENTITY = """
Your custom identity here...
"""
```

### Adding New Domains

1. Add domain to `DomainType` enum in `backend/models/schemas.py`
2. Add domain prompt to `DOMAIN_PROMPTS` in `backend/prompts/system_prompts.py`
3. Add keywords to `IntentRouter` in `backend/services/intent_router.py`

### Changing Models

Edit `.env`:
```env
OPENAI_MODEL=gpt-3.5-turbo  # Faster and cheaper
# or
OPENAI_MODEL=gpt-4  # More accurate
```

---

## Production Deployment

### Using Redis for Session Storage

1. Install Redis
2. Update `.env`:
```env
REDIS_URL=redis://localhost:6379
```

3. Modify `backend/services/session.py` to use Redis

### Security Considerations

- Use environment variables for all secrets
- Enable HTTPS in production
- Implement rate limiting
- Add authentication for API endpoints
- Restrict CORS origins

### Deployment Platforms

- **Heroku**: `Procfile` with `web: uvicorn backend.main:app --host=0.0.0.0 --port=${PORT:-8000}`
- **AWS/Azure**: Use container services (ECS, AKS)
- **Vercel/Netlify**: Deploy frontend separately, API as serverless functions

---

## Development

### Running Tests

```powershell
pytest tests/
```

### Code Formatting

```powershell
black backend/
flake8 backend/
```

### Hot Reload

The server runs in development mode with auto-reload by default.

---

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check configuration in `.env`
4. Verify all dependencies are installed

---

## License

MIT License - See LICENSE file for details
