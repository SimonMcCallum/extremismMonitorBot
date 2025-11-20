"""
Main entry point for the Discord bot.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from bot import create_bot
from utils.logger import log


async def main():
    """Main function to run the bot."""
    log.info("=" * 60)
    log.info(f"Starting {settings.app_name}")
    log.info(f"Environment: {settings.environment}")
    log.info(f"Debug Mode: {settings.debug}")
    log.info("=" * 60)

    # Create bot instance
    bot = create_bot()

    try:
        # Start bot
        log.info("Starting bot...")
        async with bot:
            await bot.start(settings.discord_bot_token)

    except KeyboardInterrupt:
        log.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        log.exception(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        log.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Shutdown complete")
