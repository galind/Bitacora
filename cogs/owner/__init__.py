from .owner import Owner
from bot import Bitacora


async def setup(bot: Bitacora):
    await bot.add_cog(Owner(bot))
