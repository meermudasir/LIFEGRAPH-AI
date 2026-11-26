import os
from typing import List
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "LifeGraph AI")
    VERSION: str = os.getenv("VERSION", "2.4.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()

    # In production, DEBUG defaults to False; in development/test it defaults to True
    _is_prod: bool = os.getenv("ENVIRONMENT", "development").lower() == "production"
    _default_debug: str = "False" if _is_prod else "True"
    DEBUG: bool = os.getenv("DEBUG", _default_debug).lower() in ("true", "1", "t")

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Database URL (SQLite locally, normalized PostgreSQL in production)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lifegraph.db")

    # Allowed CORS origins
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost,http://localhost:8000,http://localhost:5500,http://localhost:3000,http://127.0.0.1,http://127.0.0.1:8000,http://127.0.0.1:5500,http://127.0.0.1:3000,https://lifegraph-ai-1-o6ek.onrender.com,null",
        ).split(",")
        if origin.strip()
    ]

    # Security & JWT Session Management
    DEFAULT_DEV_SECRET_KEY: str = "lifegraph-insecure-dev-secret-key-change-in-production"
    SECRET_KEY: str = os.getenv("SECRET_KEY", DEFAULT_DEV_SECRET_KEY)
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h
    SESSION_COOKIE_NAME: str = os.getenv("SESSION_COOKIE_NAME", "lifegraph_session")
    OAUTH_STATE_COOKIE_NAME: str = os.getenv("OAUTH_STATE_COOKIE_NAME", "lifegraph_oauth_state")

    # Cookie Security Settings
    # Enforces COOKIE_SECURE=True in production, even if COOKIE_SECURE=False is explicitly configured
    _cookie_secure_raw: bool = os.getenv("COOKIE_SECURE", "False").lower() in ("true", "1", "t")
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax").lower()

    @property
    def COOKIE_SECURE(self) -> bool:
        """
        Enforce COOKIE_SECURE=True whenever ENVIRONMENT=production,
        even if COOKIE_SECURE=False is explicitly configured in .env or environment.
        In non-production environments, respects the configured COOKIE_SECURE value.
        """
        if getattr(self, "ENVIRONMENT", "").lower() == "production":
            return True
        return self._cookie_secure_raw

    @COOKIE_SECURE.setter
    def COOKIE_SECURE(self, value: bool) -> None:
        self._cookie_secure_raw = bool(value)

    # Google OAuth 2.0 Credentials
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # Legacy Data Ownership Mapping
    LEGACY_OWNER_EMAIL: str = os.getenv("LEGACY_OWNER_EMAIL", "admin@lifegraph.local")
    LEGACY_OWNER_NAME: str = os.getenv("LEGACY_OWNER_NAME", "Mudasir Reyaz")

    # Vector Engine Defaults
    VECTOR_MAX_FEATURES: int = int(os.getenv("VECTOR_MAX_FEATURES", "2048"))
    DEFAULT_SIMILARITY_THRESHOLD: float = float(
        os.getenv("DEFAULT_SIMILARITY_THRESHOLD", "0.80")
    )
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "10"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def validate_production_security(self) -> None:
        """
        Enforces strict security constraints if running in a production environment:
        1. SECRET_KEY cannot be empty, default dev key, or shorter than 32 characters.
        Raises RuntimeError if requirements are not met.
        """
        if self.ENVIRONMENT == "production":
            if (
                not self.SECRET_KEY
                or self.SECRET_KEY == self.DEFAULT_DEV_SECRET_KEY
                or len(self.SECRET_KEY) < 32
            ):
                raise RuntimeError(
                    "CRITICAL SECURITY CONFIGURATION ERROR: Production startup aborted. "
                    "SECRET_KEY must be explicitly set, cannot use the default development key, "
                    "and must be at least 32 characters long."
                )


settings = Settings()
