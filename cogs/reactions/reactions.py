from discord.ext import commands
import discord
import time
import importlib

from cogs.utils import mongo
from bot import Bitacora


class Reactions(commands.Cog):
    def __init__(self, bot: Bitacora) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        importlib.reload(mongo)

    def format_hours(self, hours) -> str:
        if hours == 1:
            return 'hour'
        else:
            return 'hours'

    def format_minutes(self, minutes) -> str:
        if minutes == 1:
            return 'minute'
        else:
            return 'minutes'

    def format_seconds(self, seconds) -> str:
        if seconds == 1:
            return 'second'
        else:
            return 'seconds'

    def format_time(self, seconds: int) -> str:
        content_list = []
        result = time.gmtime(seconds)

        hours_result = result.tm_hour
        if hours_result:
            text = self.format_hours(hours_result)
            content_list.append(f'{hours_result} {text}')

        minutes_result = result.tm_min
        if minutes_result:
            text = self.format_minutes(minutes_result)
            content_list.append(f'{minutes_result} {text}')

        seconds_result = result.tm_sec
        if seconds_result:
            text = self.format_seconds(seconds_result)
            content_list.append(f'{seconds_result} {text}')

        return ', '.join(content_list)

    async def contact_sender(self, user_id: int, remaining_time: int) -> None:
        user = self.bot.get_user(user_id)
        if not user:
            user = await self.bot.fetch_user(user_id)
        formatted_time = self.format_time(remaining_time)
        try:
            await user.send(
                f'You need to wait {formatted_time} to send another coin via '
                'reaction, but you can tip to the user right clicking his '
                'profile and choosing the option \'Tip to user\' in the '
                'apps section.'
            )
        except Exception:
            pass

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
            return time_difference

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

    def reaction_embed(
        self, payload: discord.RawReactionActionEvent, receiver_id: int
    ) -> discord.Embed:
        embed = discord.Embed(
            title='New Reaction', color=self.bot.color
        )

        embed.add_field(name='Emoji', value=payload.emoji.name, inline=False)
        embed.add_field(
            name='Sender', value=f'<@{payload.user_id}>', inline=False
        )
        embed.add_field(
            name='Receiver', value=f'<@{receiver_id}>', inline=False
        )
        mesasge_link = 'https://discord.com/channels/{}/{}/{}'.format(
            payload.guild_id, payload.channel_id, payload.message_id
        )
        embed.add_field(
            name='Message',
            value=f'[[Click here]]({mesasge_link})',
            inline=False
        )
        return embed

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        guild = mongo.Guild(payload.guild_id)
        guild_config = await guild.check_guild()

        emoji = guild_config.get('emoji', None)
        if payload.emoji.name != emoji:
            return

        sender = mongo.User(payload.guild_id, payload.user_id)
        sender_info = await sender.check_user()

        cooldown = guild_config.get('cooldown', 0)
        current_time = int(time.time())
        cooldown_result = await self.check_cooldown(
            sender_info, cooldown, current_time
        )
        if cooldown_result is not True:
            return await self.contact_sender(
                payload.user_id, cooldown - cooldown_result
            )

        receiver_id = await self.find_receiver(
            payload.channel_id, payload.message_id
        )
        receiver = mongo.User(payload.guild_id, receiver_id)
        receiver_info = await receiver.check_user()

        if sender_info['_id'] == receiver_info['_id']:
            return

        await sender.update_user({'timestamp': current_time})
        balance = receiver_info.get('balance', 0)
        await receiver.update_user({'balance': balance+1})

        logs = guild_config.get('logs', True)
        if not logs:
            return

        channel = await self.find_channel(payload.guild_id)
        content = '||<@{}> <@{}>||'.format(
            sender_info['_id'], receiver_info['_id']
        )
        embed = self.reaction_embed(payload, receiver_info['_id'])
        await channel.send(content=content, embed=embed)
