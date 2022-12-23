from discord.ext import commands
import discord
import logging

import config

description = """
Economy system and multi-purpose Discord integration.
"""

log = logging.getLogger(__name__)

initial_extensions = ()


class Bitacora(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions.all()
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=config.prefix,
            allowed_mentions=allowed_mentions,
            intents=intents,
            enable_debug_events=True,
        )

        self.guild_id = config.guild_id

    async def setup_hook(self) -> None:
        self.bot_app_info = await self.application_info()

        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                log.exception(f'Failed to load extension {extension}.')

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_ready(self) -> None:
        log.info(f'Ready: {self.user} (ID: {self.user.id})')

    async def start(self) -> None:
        await super().start(config.token, reconnect=True)

    @property
    def config(self) -> config:
        return __import__('config')
