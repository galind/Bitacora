from discord.ext import commands
from discord import app_commands
import discord
import importlib

from cogs.utils import mongo
from bot import Bitacora


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Admin(commands.GroupCog, group_name='admin'):
    """Admin-only commands to configure settings"""

    def __init__(self, bot: Bitacora):
        self.bot = bot

    async def cog_load(self) -> None:
        importlib.reload(mongo)

    @app_commands.command(name='cooldown')
    @app_commands.describe(seconds='Set it to 0 for no cooldown')
    async def cooldown(self, interaction: discord.Interaction, seconds: int):
        """Set the cooldown between reactions"""
        guild = mongo.Guilds(interaction.guild_id)
        try:
            await guild.update_guild('cooldown', seconds)
            content = f'Cooldown has been updated to {seconds} seconds'
        except Exception:
            content = 'Something has failed'
        await interaction.response.send_message(content, ephemeral=True)

    @app_commands.command(name='emoji')
    async def emoji(self, interaction: discord.Interaction):
        """Choose the emoji that will act as currency"""
