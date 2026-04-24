import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://travel:travel123@postgres:5432/travel"
    )
    SECRET_KEY = os.getenv("SECRET_KEY", "1234567890")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30


settings = Settings()
