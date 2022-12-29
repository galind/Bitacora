from discord.ext import commands

from bot import Bitacora


class Blackjack(commands.Cog):
    def __init__(self, bot: Bitacora) -> None:
        self.bot = bot
