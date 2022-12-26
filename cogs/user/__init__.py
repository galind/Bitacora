from .user import User
from bot import Bitacora


async def setup(bot: Bitacora):
    await bot.add_cog(User(bot))
