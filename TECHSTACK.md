# 🛠️ Tech Stack: Elite Career Companion

This document outlines the technologies used to build the Elite Career Companion bot.

## 🎨 Frontend
- **[Streamlit](https://streamlit.io/):** Main interactive dashboard for Resume Review, Mock Interviews, and Career Planning.
- **[React](https://reactjs.org/):** Used for the `ChatWidget.jsx` component to provide a modern chat interface.
- **HTML5 / CSS3 / JavaScript:** Custom styling and interactive elements for the web interface.

## ⚙️ Backend
- **[FastAPI](https://fastapi.tiangolo.com/):** High-performance Python web framework for the core API.
- **[Uvicorn](https://www.uvicorn.org/):** Lightning-fast ASGI server implementation for Python.
- **[SQLAlchemy](https://www.sqlalchemy.org/):** SQL Toolkit and Object Relational Mapper for database management.
- **[Pydantic](https://docs.pydantic.dev/):** Data validation and settings management using Python type hints.

## 🧠 Artificial Intelligence & LLM
- **[Google Gemini API](https://ai.google.dev/):** Powered by `gemini-flash-latest` for intelligent interview coaching and career guidance.
- **[LangChain](https://www.langchain.com/):** Framework for developing applications powered by language models.
- **[OpenAI API](https://openai.com/api/):** Integrated for additional NLP capabilities.

## 📄 Data Processing
- **[PyPDF2](https://pypdf2.readthedocs.io/):** Library for extracting text and data from PDF resumes.
- **Regex (Regular Expressions):** Used for advanced text analysis, filler word detection, and keyword matching.

## 🛠️ Utilities & DevOps
- **[Python-dotenv](https://github.com/theskumar/python-dotenv):** Management of environment variables and API keys.
- **[Requests](https://requests.readthedocs.io/) / [Aiohttp](https://docs.aiohttp.org/):** Synchronous and asynchronous HTTP requests.
- **[Tenacity](https://tenacity.readthedocs.io/):** Retrying library for robust API connections.
- **[Git](https://git-scm.com/):** Version control system.
