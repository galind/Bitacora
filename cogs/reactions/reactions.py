from discord.ext import commands
import discord

from bot import Bitacora


class Reactions(commands.Cog):
    """Users can give coins to others by reacting to a message"""

    def __init__(self, bot: Bitacora):
        self.bot = bot

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def reaction_add(self, payload: discord.RawReactionActionEvent):
        pass

    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def reaction_remove(self, payload: discord.RawReactionActionEvent):
        pass
