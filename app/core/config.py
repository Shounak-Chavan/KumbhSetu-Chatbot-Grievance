import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App
    PROJECT_NAME = os.getenv("APP_NAME")

    # JWT
    JWT_SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Api - Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

settings = Settings()

if not settings.JWT_SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set.")

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

