from discord.ext import commands
import discord
import time

from cogs.utils import mongo
from bot import Bitacora


class Reactions(commands.Cog):
    """Users can give coins to others by reacting to a message"""

    def __init__(self, bot: Bitacora):
        self.bot = bot

    async def find_receiver(self, channel_id: int, message_id: int) -> int:
        channel = self.bot.get_channel(channel_id)
        if not channel:
            channel = await self.bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        return message.author.id

    async def check_cooldown(
        self, sender_info: dict, cooldown: int, current_time: int
    ) -> bool:
        if cooldown == 0:
            return True

        last_reaction = sender_info.get('timestamp', None)
        if not last_reaction:
            return True

        time_difference = current_time - last_reaction
        if time_difference >= cooldown:
            return True
        else:
            return False

    async def find_guild(self, guild_id: int) -> discord.Guild:
        guild = self.bot.get_guild(guild_id)
        if not guild:
            guild = await self.bot.fetch_guild(guild_id)
        return guild

    async def create_channel(
        self, guild: discord.Guild
    ) -> discord.TextChannel:
        channel = await guild.create_text_channel(
            name='bitacora-logs',
            overwrites={
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=False
                )
            }
        )
        return channel

    async def find_channel(self, guild_id: int) -> discord.TextChannel:
        guild = await self.find_guild(guild_id)
        channel = discord.utils.get(guild.channels, name='bitacora-logs')
        if not channel:
            channel = await self.create_channel(guild)
        return channel

    def add_embed(
        self, emoji: str, sender_id: int, receiver_id: int
    ) -> discord.Embed:
        embed = discord.Embed(
            title='New Reaction', color=self.bot.color
        )

        embed.add_field(name='Emoji', value=emoji, inline=False)
        embed.add_field(
            name='Sender', value=f'<@{sender_id}>', inline=False
        )
        embed.add_field(
            name='Receiver', value=f'<@{receiver_id}>', inline=False
        )

        return embed

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def reaction_add(self, payload: discord.RawReactionActionEvent):
        guild = mongo.Guilds(payload.guild_id)
        guild_config = await guild.check_guild()

        emoji = guild_config.get('emoji', None)
        if payload.emoji.name != emoji:
            return

        sender = mongo.Users(payload.guild_id, payload.user_id)
        sender_info = await sender.check_user()

        cooldown = guild_config.get('cooldown', 0)
        current_time = int(time.time())
        cooldown_result = await self.check_cooldown(
            sender_info, cooldown, current_time
        )
        if cooldown_result is False:
            return

        receiver_id = await self.find_receiver(
            payload.channel_id, payload.message_id
        )
        receiver = mongo.Users(payload.guild_id, receiver_id)
        receiver_info = await receiver.check_user()

        if sender_info['_id'] == receiver_info['_id']:
            pass

        await sender.update_user({'timestamp': current_time})
        balance = receiver_info.get('balance', 0)
        await receiver.update_user({'balance': balance+1})

        logs = guild_config.get('logs', True)
        if not logs:
            return

        channel = await self.find_channel(payload.guild_id)
        embed = self.add_embed(
            payload.emoji.name, sender_info['_id'], receiver_info['_id']
        )
        await channel.send(embed=embed)

    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def reaction_remove(self, payload: discord.RawReactionActionEvent):
        pass
