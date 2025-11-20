"""
Main Discord bot class with event handlers.
"""
import asyncio
from typing import Optional
import discord
from discord.ext import commands

from config import settings
from utils.logger import log
from utils.database import db
from utils.cache import cache


class ExtremismMonitorBot(commands.Bot):
    """Custom bot class for extremism monitoring."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        intents.guilds = True

        super().__init__(
            command_prefix=settings.discord_command_prefix,
            intents=intents,
            help_command=None,
        )

        self.start_time: Optional[float] = None
        self.messages_processed: int = 0

    async def setup_hook(self):
        """Setup hook called before bot starts."""
        log.info("Setting up bot...")

        # Connect to database
        try:
            await db.connect()
            log.info("Database connected successfully")
        except Exception as e:
            log.error(f"Failed to connect to database: {e}")
            raise

        # Connect to cache
        try:
            await cache.connect()
            log.info("Cache connected successfully")
        except Exception as e:
            log.error(f"Failed to connect to cache: {e}")
            raise

        # Load cogs
        await self.load_cogs()

        log.info("Bot setup completed")

    async def load_cogs(self):
        """Load all cog modules."""
        cog_modules = [
            "cogs.monitoring",
            "cogs.admin",
            "cogs.events",
        ]

        for module in cog_modules:
            try:
                await self.load_extension(module)
                log.info(f"Loaded cog: {module}")
            except Exception as e:
                log.error(f"Failed to load cog {module}: {e}")

    async def on_ready(self):
        """Event handler called when bot is ready."""
        log.info(f"Bot is ready! Logged in as {self.user.name} (ID: {self.user.id})")
        log.info(f"Connected to {len(self.guilds)} guilds")

        # Set bot presence
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for community safety"
            )
        )

        # Store start time
        import time
        self.start_time = time.time()

        # Register guilds in database
        await self.register_guilds()

    async def on_guild_join(self, guild: discord.Guild):
        """Event handler called when bot joins a guild."""
        log.info(f"Joined guild: {guild.name} (ID: {guild.id})")

        # Register guild in database
        await self.register_guild(guild)

    async def on_guild_remove(self, guild: discord.Guild):
        """Event handler called when bot leaves a guild."""
        log.info(f"Left guild: {guild.name} (ID: {guild.id})")

    async def on_message(self, message: discord.Message):
        """Event handler called for every message."""
        # Ignore bot messages
        if message.author.bot:
            return

        # Track message count
        self.messages_processed += 1

        # Process commands
        await self.process_commands(message)

    async def on_error(self, event_method: str, *args, **kwargs):
        """Event handler called when an error occurs."""
        log.exception(f"Error in {event_method}")

    async def register_guilds(self):
        """Register all guilds in database."""
        for guild in self.guilds:
            await self.register_guild(guild)

    async def register_guild(self, guild: discord.Guild):
        """Register a single guild in database."""
        try:
            query = """
                INSERT INTO servers (discord_server_id, name, owner_id, created_at, updated_at)
                VALUES ($1, $2, $3, NOW(), NOW())
                ON CONFLICT (discord_server_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    updated_at = NOW()
            """
            await db.execute(query, str(guild.id), guild.name, str(guild.owner_id))
            log.info(f"Registered guild: {guild.name}")
        except Exception as e:
            log.error(f"Failed to register guild {guild.name}: {e}")

    async def close(self):
        """Cleanup when bot closes."""
        log.info("Shutting down bot...")

        # Disconnect from database
        await db.disconnect()

        # Disconnect from cache
        await cache.disconnect()

        await super().close()
        log.info("Bot shutdown complete")


def create_bot() -> ExtremismMonitorBot:
    """Factory function to create bot instance."""
    return ExtremismMonitorBot()
