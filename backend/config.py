"""Configuration management for Blog Creator API"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # App Configuration
    APP_NAME: str = "Blog Creator API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database URLs
    REDIS_URL: str = "redis://localhost:6379"
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    CHROMADB_PATH: str = "./data/chromadb"

    # LLM Configuration
    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4-turbo-preview"

    # Upload Configuration
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".mp3", ".wav", ".png", ".jpg", ".jpeg", ".md"]
    )
    UPLOAD_DIR: str = "./data/uploads"

    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5

    # GitHub Integration
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # Sentry
    SENTRY_DSN: str = ""


# Global settings instance
settings = Settings()
