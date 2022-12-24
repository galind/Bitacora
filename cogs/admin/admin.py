from discord.ext import commands
from discord import app_commands
import discord
import asyncio
import importlib

from cogs.utils import mongo
from bot import Bitacora


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Admin(commands.GroupCog, group_name='admin'):
    """Admin-only commands to configure settings"""

    def __init__(self, bot: Bitacora):
        self.bot = bot

    async def cog_load(self) -> None:
        importlib.reload(mongo)

    @app_commands.command(name='cooldown')
    @app_commands.describe(seconds='Set it to 0 for no cooldown')
    async def cooldown(self, interaction: discord.Interaction, seconds: int):
        """Set the cooldown between reactions"""
        guild = mongo.Guilds(interaction.guild_id)
        await guild.update_guild('cooldown', seconds)
        await interaction.response.send_message(
            f'Cooldown has been updated to {seconds} seconds',
            ephemeral=True
        )

    @app_commands.command(name='emoji')
    async def emoji(self, interaction: discord.Interaction):
        """Choose the emoji that will act as currency"""
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title='React with the emoji you would like to set',
            description=(
                'You can use a default emoji, like 🪙, 💯, etc... '
                'or use a custom emoji from your server. You have '
                '90 seconds before this message auto-deletes.'
            ),
            color=self.bot.color
        )
        message = await interaction.channel.send(embed=embed)

        def check(reaction: discord.Reaction, user: discord.User):
            if (
                user.id == interaction.user.id and
                message.id == reaction.message.id
            ):
                return reaction
            return None

        try:
            reaction = await self.bot.wait_for(
                'reaction_add', check=check, timeout=90.0
            )
        except asyncio.TimeoutError:
            await interaction.followup.send('No reaction was received')
            return await message.delete()

        emoji = str(reaction[0])
        guild = mongo.Guilds(interaction.guild_id)
        await guild.update_guild('emoji', emoji)
        await message.delete()
        await interaction.followup.send(f'Emoji has been updated to {emoji}')

    @app_commands.command(name='logs')
    async def logs(self, interaction: discord.Interaction):
        """Enable/disable receiving event notifications"""
        guild = mongo.Guilds(interaction.guild_id)
        guild_config = await guild.check_guild()

        if 'logs' in guild_config:
            logs = not guild_config['logs']
        else:
            logs = False

        await guild.update_guild('logs', logs)
        if logs:
            content = 'Logs have been enabled'
        else:
            content = 'Logs have been disabled'
        await interaction.response.send_message(content, ephemeral=True)
