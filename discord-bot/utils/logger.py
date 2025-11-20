"""
Logging configuration for the Discord bot.
"""
import sys
from pathlib import Path
from loguru import logger

from config import settings


def setup_logger():
    """Configure loguru logger with appropriate settings."""

    # Remove default handler
    logger.remove()

    # Console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )

    # File handler with rotation
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
        serialize=settings.log_format == "json",
    )

    logger.info(f"Logger initialized - Level: {settings.log_level}, Environment: {settings.environment}")

    return logger


# Initialize logger
log = setup_logger()
