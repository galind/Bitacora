from .reactions import Reactions
from bot import Bitacora


async def setup(bot: Bitacora):
    await bot.add_cog(Reactions(bot))
