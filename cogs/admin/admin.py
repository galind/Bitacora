from discord.ext import commands

from bot import Bitacora


class Admin(commands.GroupCog, group_name='admin'):
    """Admin-only commands to configure settings."""

    def __init__(self, bot: Bitacora):
        self.bot = bot
