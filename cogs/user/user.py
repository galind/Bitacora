from discord.ext import commands

from bot import Bitacora


class User(commands.Cog):
    def __init__(self, bot: Bitacora):
        self.bot = bot
