import os
from typing import List
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "LifeGraph AI")
    VERSION: str = os.getenv("VERSION", "2.4.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # SQLite database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lifegraph.db")

    # Allowed CORS origins
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost,http://localhost:8000,http://127.0.0.1,http://127.0.0.1:8000,http://127.0.0.1:5500,null",
        ).split(",")
        if origin.strip()
    ]

    # Vector Engine Defaults
    VECTOR_MAX_FEATURES: int = int(os.getenv("VECTOR_MAX_FEATURES", "2048"))
    DEFAULT_SIMILARITY_THRESHOLD: float = float(
        os.getenv("DEFAULT_SIMILARITY_THRESHOLD", "0.80")
    )
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "10"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
