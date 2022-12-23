from bot import Bitacora

bot = Bitacora()
database = bot.database


class Guilds:
    def __init__(self, guild: int):
        self.guild = database[str(guild)]
        self.query = {'_id': 'config'}

    async def new_guild(self):
        await self.guild.insert_one(self.query)

    async def find_guild(self):
        return await self.guild.find_one(self.query)

    async def check_guild(self):
        guild_config = await self.find_guild()
        if not guild_config:
            await self.new_guild()
            guild_config = await self.find_guild()
        return guild_config

    async def update_guild(self, key, value):
        set_query = {'$set': {key: value}}
        await self.guild.update_one(self.query, set_query, upsert=True)
