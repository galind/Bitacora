from discord.ext import commands
from discord import app_commands
import discord
import importlib

from cogs.utils import mongo
from bot import Bitacora


class TipModal(discord.ui.Modal):
    def __init__(
        self, sender: mongo.User, receiver: mongo.User, name: str
    ) -> None:
        self.sender = sender
        self.receiver = receiver
        self.name = name
        super().__init__(title=f'Tip {name}', timeout=None)

    quantity = discord.ui.TextInput(
        label='Quantity',
        style=discord.TextStyle.short,
        placeholder='Only numbers'
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        quantity = int(self.quantity.value)
        sender_info = await self.sender.check_user()

        sender_balance = sender_info.get('balance', 0)

        if quantity > sender_balance:
            return await interaction.response.send_message(
                'You don\'t have enough coins in the wallet', ephemeral=True
            )

        await self.sender.update_user({'balance': -quantity}, method='inc')
        await self.receiver.update_user({'balance': quantity}, method='inc')
        await interaction.response.send_message(
            f'The {quantity} coins tip has been sent to {self.name}',
            ephemeral=True
        )


class User(commands.Cog):
    def __init__(self, bot: Bitacora) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        importlib.reload(mongo)

    @app_commands.command(name='help')
    async def help(self, interaction: discord.Interaction) -> None:
        """Check out how to use the bot"""

    @app_commands.command(name='wallet')
    async def balance(self, interaction: discord.Interaction) -> None:
        """How many coins do you have in the wallet?"""
        user = mongo.User(interaction.guild_id, interaction.user.id)
        user_info = await user.check_user()
        balance = user_info.get('balance', 0)
        await interaction.response.send_message(
            f'You have {balance} coins in the wallet', ephemeral=True
        )

    @app_commands.command(name='tip')
    @app_commands.describe(
        user='The user you want to tip',
        amount='The amount of coins you want to tip'
    )
    async def tip(
        self, interaction: discord.Interaction,
        user: discord.User, amount: int
    ) -> None:
        """Tip coins to another user"""
        if interaction.user.id == user.id:
            return await interaction.response.send_message(
                'You can\'t tip to yourself', ephemeral=True
            )

        sender = mongo.User(interaction.guild_id, interaction.user.id)
        receiver = mongo.User(interaction.guild_id, user.id)

        sender_info = await sender.check_user()
        if amount > sender_info.get('balance', 0):
            return await interaction.response.send_message(
                'You don\'t have enough coins in the wallet', ephemeral=True
            )

        await sender.update_user({'balance': -amount}, method='inc')
        await receiver.update_user({'balance': amount}, method='inc')
        await interaction.response.send_message(
            f'The {amount} coins tip has been sent', ephemeral=True
        )
