from discord.ext import commands
from discord import app_commands
import discord

from cogs.utils import mongo
from bot import Bitacora


class User(commands.Cog):
    def __init__(self, bot: Bitacora):
        self.bot = bot

    @app_commands.command(name='balance')
    async def balance(self, interaction: discord.Interaction):
        """Check your coin balance"""
        user = mongo.User(interaction.guild_id, interaction.user.id)
        user_info = await user.check_user()
        balance = user_info.get('balance', 0)
        await interaction.response.send_message(
            f'Your balance is {balance} coins', ephemeral=True
        )
