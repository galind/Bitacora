from .admin import Admin
from bot import Bitacora


async def setup(bot: Bitacora):
    await bot.add_cog(Admin(bot))
