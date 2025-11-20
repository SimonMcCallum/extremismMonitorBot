"""
General event handlers cog.
"""
import discord
from discord.ext import commands

from utils.logger import log


class EventHandlers(commands.Cog):
    """Cog for general event handlers."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        """Called when cog is loaded."""
        log.info("Event handlers cog loaded")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command.")
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ This command is on cooldown. Try again in {error.retry_after:.1f}s")
            return

        # Log unexpected errors
        log.error(f"Command error in {ctx.command}: {error}", exc_info=error)
        await ctx.send("❌ An unexpected error occurred while executing this command.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Track reaction additions for engagement metrics."""
        if user.bot:
            return

        log.debug(f"Reaction added: {reaction.emoji} by {user.name}")

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        """Track voice channel activity for engagement metrics."""
        if before.channel != after.channel:
            if after.channel:
                log.debug(f"{member.name} joined voice channel: {after.channel.name}")
            elif before.channel:
                log.debug(f"{member.name} left voice channel: {before.channel.name}")


async def setup(bot: commands.Bot):
    """Setup function to add cog to bot."""
    await bot.add_cog(EventHandlers(bot))
