from typing import Optional

from bot import Bitacora

bot = Bitacora()
database = bot.database


class Guild:
    def __init__(self, guild: int):
        self.guild = database[str(guild)]
        self.query = {'_id': 'config'}

    async def new_guild(self) -> None:
        await self.guild.insert_one(self.query)

    async def find_guild(self) -> Optional[dict]:
        return await self.guild.find_one(self.query)

    async def check_guild(self) -> dict:
        guild_settings = await self.find_guild()
        if not guild_settings:
            await self.new_guild()
            guild_settings = await self.find_guild()
        return guild_settings

    async def update_guild(self, query: dict) -> None:
        set_query = {'$set': query}
        await self.guild.update_one(self.query, set_query, upsert=True)


class User:
    def __init__(self, guild: int, user: int):
        self.guild = database[str(guild)]
        self.query = {'_id': user}

    async def new_user(self) -> None:
        await self.guild.insert_one(self.query)

    async def find_user(self) -> Optional[dict]:
        return await self.guild.find_one(self.query)

    async def check_user(self) -> dict:
        user_info = await self.find_user()
        if not user_info:
            await self.new_user()
            user_info = await self.find_user()
        return user_info

    async def update_user(self, query: dict) -> None:
        set_query = {'$set': query}
        await self.guild.update_one(self.query, set_query, upsert=True)
