import os
from dotenv import load_dotenv

load_dotenv()
class Settings:
    APP_NAME: str = "AI Code Assistant"
    DEBUG: bool = True
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://aiuser:password@localhost/ai_assistant")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


settings = Settings()

