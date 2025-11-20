"""
Admin commands cog for bot management and configuration.
"""
from datetime import datetime, timedelta
import discord
from discord import app_commands
from discord.ext import commands

from config import settings
from utils.logger import log
from utils.database import db


class AdminCommands(commands.Cog):
    """Cog for administrative commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        """Called when cog is loaded."""
        log.info("Admin commands cog loaded")

    @app_commands.command(name="status", description="Get bot status and statistics")
    @app_commands.default_permissions(administrator=True)
    async def status(self, interaction: discord.Interaction):
        """Display bot status and statistics."""
        try:
            # Calculate uptime
            if hasattr(self.bot, 'start_time') and self.bot.start_time:
                import time
                uptime_seconds = time.time() - self.bot.start_time
                uptime = str(timedelta(seconds=int(uptime_seconds)))
            else:
                uptime = "Unknown"

            # Get statistics from database
            total_messages = await db.fetchval("SELECT COUNT(*) FROM messages")
            total_users = await db.fetchval("SELECT COUNT(*) FROM users")
            total_servers = await db.fetchval("SELECT COUNT(*) FROM servers")

            # Create embed
            embed = discord.Embed(
                title="🤖 Bot Status",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )

            embed.add_field(name="Uptime", value=uptime, inline=True)
            embed.add_field(name="Guilds", value=total_servers or 0, inline=True)
            embed.add_field(name="Users Tracked", value=total_users or 0, inline=True)
            embed.add_field(name="Messages Stored", value=total_messages or 0, inline=True)
            embed.add_field(name="Environment", value=settings.environment.upper(), inline=True)
            embed.add_field(
                name="Risk Monitoring",
                value="✅ Enabled" if settings.enable_risk_monitoring else "❌ Disabled",
                inline=True
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            log.error(f"Error in status command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while fetching status.",
                ephemeral=True
            )

    @app_commands.command(name="risk-report", description="Get risk report for a user")
    @app_commands.describe(user="The user to check")
    @app_commands.default_permissions(administrator=True)
    async def risk_report(self, interaction: discord.Interaction, user: discord.Member):
        """Display risk report for a specific user."""
        try:
            await interaction.response.defer(ephemeral=True)

            # Get user from database
            user_data = await db.fetchrow(
                """
                SELECT id, discord_user_id, username, risk_score,
                       total_messages, first_seen, last_seen
                FROM users
                WHERE discord_user_id = $1
                """,
                str(user.id)
            )

            if not user_data:
                await interaction.followup.send(
                    f"No data found for user {user.mention}",
                    ephemeral=True
                )
                return

            # Get recent risk assessments
            recent_assessments = await db.fetch(
                """
                SELECT risk_score, risk_category, created_at, flagged
                FROM risk_assessments
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT 5
                """,
                user_data['id']
            )

            # Create embed
            embed = discord.Embed(
                title=f"📊 Risk Report: {user.display_name}",
                color=self.get_risk_color(user_data['risk_score'] or 0),
                timestamp=datetime.utcnow()
            )

            embed.set_thumbnail(url=user.display_avatar.url)

            embed.add_field(
                name="Current Risk Score",
                value=f"{user_data['risk_score'] or 0:.1f}/100",
                inline=True
            )
            embed.add_field(
                name="Total Messages",
                value=user_data['total_messages'] or 0,
                inline=True
            )
            embed.add_field(
                name="Member Since",
                value=user_data['first_seen'].strftime("%Y-%m-%d") if user_data['first_seen'] else "Unknown",
                inline=True
            )

            # Add recent assessments
            if recent_assessments:
                assessment_text = "\n".join([
                    f"{'🔴' if a['flagged'] else '🟢'} {a['risk_score']:.1f} - {a['risk_category'] or 'Unknown'} ({a['created_at'].strftime('%Y-%m-%d')})"
                    for a in recent_assessments
                ])
                embed.add_field(
                    name="Recent Assessments",
                    value=assessment_text,
                    inline=False
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            log.error(f"Error in risk-report command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while generating the risk report.",
                ephemeral=True
            )

    @app_commands.command(name="engagement-stats", description="View community engagement statistics")
    @app_commands.default_permissions(administrator=True)
    async def engagement_stats(self, interaction: discord.Interaction):
        """Display community engagement statistics."""
        try:
            await interaction.response.defer(ephemeral=True)

            # Get server ID
            server_id = await db.fetchval(
                "SELECT id FROM servers WHERE discord_server_id = $1",
                str(interaction.guild.id)
            )

            if not server_id:
                await interaction.followup.send(
                    "Server not found in database.",
                    ephemeral=True
                )
                return

            # Get engagement statistics
            stats = await db.fetchrow(
                """
                SELECT
                    COUNT(DISTINCT user_id) as active_users,
                    COUNT(*) as total_messages,
                    AVG(LENGTH(content)) as avg_message_length
                FROM messages
                WHERE server_id = $1
                  AND created_at >= NOW() - INTERVAL '7 days'
                """,
                server_id
            )

            # Get today's message count
            today_messages = await db.fetchval(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE server_id = $1
                  AND created_at >= CURRENT_DATE
                """,
                server_id
            )

            # Create embed
            embed = discord.Embed(
                title="📈 Engagement Statistics",
                description=f"Statistics for {interaction.guild.name}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )

            embed.add_field(
                name="Active Users (7 days)",
                value=stats['active_users'] or 0,
                inline=True
            )
            embed.add_field(
                name="Messages (7 days)",
                value=stats['total_messages'] or 0,
                inline=True
            )
            embed.add_field(
                name="Messages Today",
                value=today_messages or 0,
                inline=True
            )
            embed.add_field(
                name="Avg Message Length",
                value=f"{stats['avg_message_length']:.0f} chars" if stats['avg_message_length'] else "N/A",
                inline=True
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            log.error(f"Error in engagement-stats command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while fetching engagement statistics.",
                ephemeral=True
            )

    @app_commands.command(name="sync", description="Sync slash commands")
    @app_commands.default_permissions(administrator=True)
    async def sync(self, interaction: discord.Interaction):
        """Sync slash commands with Discord."""
        try:
            await interaction.response.defer(ephemeral=True)

            synced = await self.bot.tree.sync(guild=interaction.guild)

            await interaction.followup.send(
                f"✅ Synced {len(synced)} commands to this guild.",
                ephemeral=True
            )

            log.info(f"Synced {len(synced)} commands to guild {interaction.guild.id}")

        except Exception as e:
            log.error(f"Error syncing commands: {e}")
            await interaction.followup.send(
                "❌ An error occurred while syncing commands.",
                ephemeral=True
            )

    def get_risk_color(self, risk_score: float) -> discord.Color:
        """Get color based on risk score."""
        if risk_score >= settings.risk_critical_threshold:
            return discord.Color.dark_red()
        elif risk_score >= settings.risk_high_threshold:
            return discord.Color.red()
        elif risk_score >= settings.risk_medium_threshold:
            return discord.Color.orange()
        elif risk_score >= settings.risk_low_threshold:
            return discord.Color.yellow()
        else:
            return discord.Color.green()


async def setup(bot: commands.Bot):
    """Setup function to add cog to bot."""
    await bot.add_cog(AdminCommands(bot))
