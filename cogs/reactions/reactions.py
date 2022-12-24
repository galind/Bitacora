from discord.ext import commands

from bot import Bitacora


class Reactions(commands.Cog):
    """Users can give coins to others reacting or tipping"""

    def __init__(self, bot: Bitacora):
        self.bot = bot
