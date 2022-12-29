from .blackjack import Blackjack
from bot import Bitacora


async def setup(bot: Bitacora):
    await bot.add_cog(Blackjack(bot))
