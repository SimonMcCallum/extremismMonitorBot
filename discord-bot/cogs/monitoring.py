"""
Message monitoring cog for detecting and analyzing messages.
"""
import asyncio
from datetime import datetime
from typing import Optional, List, Dict
import discord
from discord.ext import commands

from config import settings
from utils.logger import log
from utils.database import db
from utils.cache import cache
from services.risk_assessment import risk_service


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

                # Store message in database and get its ID
                message_db_id = await self.store_message(message)

                # Perform risk assessment if message was stored successfully
                if message_db_id and settings.enable_risk_monitoring:
                    await self.analyze_message_risk(message, message_db_id)

                # Small delay to avoid overwhelming the system
                await asyncio.sleep(settings.analysis_delay_seconds)

            except asyncio.CancelledError:
                log.info("Message processing queue cancelled")
                break
            except Exception as e:
                log.error(f"Error processing message: {e}")
                await asyncio.sleep(1)

    async def store_message(self, message: discord.Message) -> Optional[int]:
        """
        Store message in database.

        Returns:
            Database ID of stored message, or None if failed
        """
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

            # Store message and get its ID
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
                RETURNING id
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

            message_db_id = await db.fetchval(
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

            # Increment user message count
            if message_db_id:
                await db.execute(
                    "UPDATE users SET total_messages = total_messages + 1 WHERE id = $1",
                    user_id
                )

            return message_db_id

        except Exception as e:
            log.error(f"Failed to store message {message.id}: {e}")
            return None

    async def analyze_message_risk(
        self,
        message: discord.Message,
        message_db_id: int
    ):
        """
        Analyze message for risk indicators.

        Args:
            message: Discord message object
            message_db_id: Database ID of the message
        """
        try:
            # Get database IDs
            user_id = await db.fetchval(
                "SELECT id FROM users WHERE discord_user_id = $1",
                str(message.author.id)
            )

            server_id = await db.fetchval(
                "SELECT id FROM servers WHERE discord_server_id = $1",
                str(message.guild.id)
            )

            # Get context messages (previous messages in channel)
            context = await self.get_message_context(message)

            # Perform risk assessment
            assessment = await risk_service.assess_message(
                message_id=message_db_id,
                message_content=message.content or "",
                user_id=user_id,
                server_id=server_id,
                context_messages=context
            )

            log.debug(
                f"Risk assessment complete for message {message.id}: "
                f"score={assessment.get('risk_score', 0):.1f}"
            )

        except Exception as e:
            log.error(f"Error analyzing message risk: {e}")

    async def get_message_context(
        self,
        message: discord.Message,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get previous messages from the same channel for context.

        Args:
            message: Current message
            limit: Number of previous messages to retrieve

        Returns:
            List of previous messages as dicts
        """
        context = []

        try:
            # Get previous messages from the channel
            async for prev_msg in message.channel.history(
                limit=limit,
                before=message,
                oldest_first=False
            ):
                if not prev_msg.author.bot:  # Skip bot messages
                    context.append({
                        "author": prev_msg.author.name,
                        "content": prev_msg.content,
                        "timestamp": prev_msg.created_at.isoformat()
                    })

            # Reverse to get chronological order
            context.reverse()

        except Exception as e:
            log.error(f"Error getting message context: {e}")

        return context

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
