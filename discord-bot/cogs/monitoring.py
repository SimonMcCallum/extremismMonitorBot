"""
Message monitoring cog for detecting and analyzing messages.
"""
import asyncio
from datetime import datetime
from typing import Optional
import discord
from discord.ext import commands

from config import settings
from utils.logger import log
from utils.database import db
from utils.cache import cache


class MessageMonitoring(commands.Cog):
    """Cog for monitoring and analyzing messages."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None

    async def cog_load(self):
        """Called when cog is loaded."""
        log.info("Message monitoring cog loaded")
        # Start background message processing
        self.processing_task = asyncio.create_task(self.process_message_queue())

    async def cog_unload(self):
        """Called when cog is unloaded."""
        log.info("Message monitoring cog unloaded")
        # Cancel background task
        if self.processing_task:
            self.processing_task.cancel()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor all messages."""
        # Ignore bot messages
        if message.author.bot:
            return

        # Ignore DMs
        if not message.guild:
            return

        # Only process if monitoring is enabled
        if not settings.enable_risk_monitoring:
            return

        # Add message to processing queue
        await self.message_queue.put(message)

    async def process_message_queue(self):
        """Background task to process messages from queue."""
        log.info("Message processing queue started")

        while True:
            try:
                # Get message from queue
                message = await self.message_queue.get()

                # Store message in database
                await self.store_message(message)

                # Small delay to avoid overwhelming the system
                await asyncio.sleep(settings.analysis_delay_seconds)

            except asyncio.CancelledError:
                log.info("Message processing queue cancelled")
                break
            except Exception as e:
                log.error(f"Error processing message: {e}")
                await asyncio.sleep(1)

    async def store_message(self, message: discord.Message):
        """Store message in database."""
        try:
            # Check if user exists, create if not
            await self.ensure_user_exists(message.author, message.guild)

            # Get user ID from database
            user_id = await db.fetchval(
                "SELECT id FROM users WHERE discord_user_id = $1",
                str(message.author.id)
            )

            # Get server ID from database
            server_id = await db.fetchval(
                "SELECT id FROM servers WHERE discord_server_id = $1",
                str(message.guild.id)
            )

            # Store message
            query = """
                INSERT INTO messages (
                    discord_message_id,
                    server_id,
                    user_id,
                    channel_id,
                    content,
                    attachments,
                    metadata,
                    created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (discord_message_id) DO NOTHING
            """

            attachments = [
                {
                    "filename": att.filename,
                    "url": att.url,
                    "content_type": att.content_type
                }
                for att in message.attachments
            ]

            metadata = {
                "embeds_count": len(message.embeds),
                "mentions_count": len(message.mentions),
                "channel_name": message.channel.name if hasattr(message.channel, "name") else None,
            }

            await db.execute(
                query,
                str(message.id),
                server_id,
                user_id,
                str(message.channel.id),
                message.content,
                attachments,
                metadata,
                message.created_at
            )

            log.debug(f"Stored message {message.id} from user {message.author.name}")

        except Exception as e:
            log.error(f"Failed to store message {message.id}: {e}")

    async def ensure_user_exists(self, user: discord.User, guild: discord.Guild):
        """Ensure user exists in database, create if not."""
        try:
            # Check if user is a member of the guild
            member = guild.get_member(user.id)
            joined_at = member.joined_at if member else None

            query = """
                INSERT INTO users (
                    discord_user_id,
                    username,
                    joined_at,
                    first_seen,
                    last_seen
                )
                VALUES ($1, $2, $3, NOW(), NOW())
                ON CONFLICT (discord_user_id)
                DO UPDATE SET
                    username = EXCLUDED.username,
                    last_seen = NOW()
            """

            await db.execute(
                query,
                str(user.id),
                user.name,
                joined_at
            )

        except Exception as e:
            log.error(f"Failed to ensure user exists {user.id}: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Track when members join."""
        if settings.enable_engagement_tracking:
            await self.track_member_join(member)

    async def track_member_join(self, member: discord.Member):
        """Record member join event."""
        try:
            await self.ensure_user_exists(member, member.guild)
            log.info(f"Member joined: {member.name} in {member.guild.name}")
        except Exception as e:
            log.error(f"Failed to track member join: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Track when members leave."""
        if settings.enable_engagement_tracking:
            await self.track_member_leave(member)

    async def track_member_leave(self, member: discord.Member):
        """Record member leave event."""
        try:
            # Update user last seen
            query = """
                UPDATE users
                SET last_seen = NOW()
                WHERE discord_user_id = $1
            """
            await db.execute(query, str(member.id))

            log.info(f"Member left: {member.name} from {member.guild.name}")
        except Exception as e:
            log.error(f"Failed to track member leave: {e}")


async def setup(bot: commands.Bot):
    """Setup function to add cog to bot."""
    await bot.add_cog(MessageMonitoring(bot))
