from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project metadata
    PROJECT_NAME: str = "KrishiGuard AI"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development")

    # Persistent Database (MongoDB Atlas)
    MONGODB_URI: str = Field(default="mongodb://localhost:27017")
    MONGODB_DATABASE: str = Field(default="krishiguard")
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_MIN_POOL_SIZE: int = 5
    MONGODB_TIMEOUT_MS: int = 15000

    # Redis (Sessions, Caching, Queues, Rate Limiting)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_SOCKET_TIMEOUT: float = 2.0
    REDIS_CONNECT_TIMEOUT: float = 2.0

    # Gemini AI
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash")

    # Weather Integration (Open-Meteo)
    WEATHER_API_BASE_URL: str = Field(default="https://api.open-meteo.com/v1/forecast")
    WEATHER_CACHE_TTL_SECONDS: int = Field(default=900)  # 15 minutes

    # Security & Sessions
    SESSION_SECRET: str = Field(default="krishiguard_super_secret_session_key_32bytes_min")
    SESSION_TTL_SECONDS: int = Field(default=7 * 24 * 3600)  # 7 days
    SESSION_COOKIE_NAME: str = "kg_session_id"
    COOKIE_SECURE: bool = Field(default=False)  # set True in production HTTPS
    COOKIE_SAMESITE: str = Field(default="lax")  # "lax" or "strict"
    COOKIE_HTTPONLY: bool = True
    CSRF_SECRET: str = Field(default="krishiguard_csrf_secret_salt_32bytes_min")
    CSRF_HEADER_NAME: str = "X-CSRF-Token"

    # CORS
    FRONTEND_ORIGIN: str = Field(default="http://localhost:5173")
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    # Image Storage & Limits
    STORAGE_DIR: str = Field(default="./uploads/crop_images")
    ASSESSMENT_MAX_UPLOAD_BYTES: int = Field(default=5 * 1024 * 1024)  # 5 MB
    ASSESSMENT_JOB_TIMEOUT_SECONDS: int = Field(default=180)
    ALLOWED_IMAGE_MIMETYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # Rate Limiting (Redis Lua)
    RATE_LIMIT_LOGIN_MAX_ATTEMPTS: int = Field(default=5)
    RATE_LIMIT_LOGIN_WINDOW_SECONDS: int = Field(default=900)  # 15 min
    RATE_LIMIT_GENERAL_MAX_REQUESTS: int = Field(default=120)
    RATE_LIMIT_GENERAL_WINDOW_SECONDS: int = Field(default=60)
    RATE_LIMIT_ASSESSMENT_MAX: int = Field(default=20)
    RATE_LIMIT_ASSESSMENT_WINDOW_SECONDS: int = Field(default=3600)

settings = Settings()
