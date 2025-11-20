"""
Configuration management for backend API.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "Extremism Monitor API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_password: str = ""

    # Authentication
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Anthropic Claude
    anthropic_api_key: str
    claude_model: str = "claude-3-sonnet-20240229"
    claude_max_tokens: int = 4096

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60

    # ML Models
    ml_model_path: str = "./models"
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_db_path: str = "./data/vectordb"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Monitoring
    enable_prometheus: bool = True
    prometheus_port: int = 9090

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/api.log"


# Global settings instance
settings = Settings()
