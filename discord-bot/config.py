"""
Configuration management for Discord bot.
"""
from typing import List, Optional
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
    app_name: str = "Extremism Monitor Bot"
    environment: str = "development"
    debug: bool = True

    # Discord Configuration
    discord_bot_token: str
    discord_client_id: str
    discord_command_prefix: str = "!"

    # Backend API
    api_base_url: str = "http://localhost:8000"
    api_key: Optional[str] = None

    # Database
    database_url: str = "postgresql://extremism_user:password@localhost:5432/extremism_monitor"
    database_pool_size: int = 10
    database_max_overflow: int = 5

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None

    # Anthropic Claude AI
    anthropic_api_key: str
    claude_model: str = "claude-3-sonnet-20240229"
    claude_max_tokens: int = 4096

    # Risk Assessment Thresholds
    risk_low_threshold: int = 30
    risk_medium_threshold: int = 60
    risk_high_threshold: int = 85
    risk_critical_threshold: int = 95

    # Feature Flags
    enable_risk_monitoring: bool = True
    enable_engagement_tracking: bool = True
    enable_auto_alerts: bool = True
    enable_ml_predictions: bool = True

    # Performance Settings
    message_batch_size: int = 100
    analysis_delay_seconds: float = 2.0
    max_concurrent_analyses: int = 5
    message_cache_size: int = 1000
    message_cache_ttl_seconds: int = 3600

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/bot.log"
    log_format: str = "json"
    log_rotation: str = "1 day"
    log_retention: str = "30 days"

    # Bot Behavior
    command_cooldown_seconds: float = 3.0
    max_message_length: int = 2000

    # Testing
    dev_mock_discord: bool = False
    dev_mock_claude_api: bool = False


# Global settings instance
settings = Settings()
