from discord.ext import commands
from discord import app_commands
import discord

from bot import Bitacora


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Admin(commands.GroupCog, group_name='admin'):
    """Admin-only commands to configure settings"""

    def __init__(self, bot: Bitacora):
        self.bot = bot

    @app_commands.command(name='cooldown')
    async def cooldown(self, interaction: discord.Interaction):
        """Set the cooldown between currency reactions"""

    @app_commands.command(name='emoji')
    async def emoji(self, interaction: discord.Interaction):
        """Choose the emoji that will act as currency"""
