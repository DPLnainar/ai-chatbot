import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Google Gemini Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # Azure OpenAI (optional)
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    
    # Application Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Session Configuration
    SESSION_EXPIRE_MINUTES = int(os.getenv("SESSION_EXPIRE_MINUTES", 60))
    REDIS_URL = os.getenv("REDIS_URL", "")
    
    # Knowledge Base
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "./data/knowledge_base")
    
    # Model Parameters
    TEMPERATURE = 0.7
    MAX_TOKENS = 1500
    TOP_P = 0.9
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY and not cls.AZURE_OPENAI_API_KEY and not cls.GOOGLE_API_KEY:
            print(f"⚠️  API Key Status: OPENAI_API_KEY={'SET' if cls.OPENAI_API_KEY else 'MISSING'}")
            print(f"⚠️  API Key Status: GOOGLE_API_KEY={'SET' if cls.GOOGLE_API_KEY else 'MISSING'}")
            print(f"⚠️  .env file location: {env_path}")
            print(f"⚠️  .env file exists: {env_path.exists()}")
            raise ValueError("Either OPENAI_API_KEY, AZURE_OPENAI_API_KEY, or GOOGLE_API_KEY must be set")
        
        if cls.OPENAI_API_KEY:
            print(f"✓ OpenAI API Key loaded: {cls.OPENAI_API_KEY[:10]}...{cls.OPENAI_API_KEY[-5:]}")
        if cls.GOOGLE_API_KEY:
            print(f"✓ Google API Key loaded: {cls.GOOGLE_API_KEY[:10]}...{cls.GOOGLE_API_KEY[-5:]}")
            
        return True


config = Config()
