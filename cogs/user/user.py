from discord.ext import commands
from discord import app_commands
import discord

from cogs.utils import mongo
from bot import Bitacora


class TipModal(discord.ui.Modal):
    def __init__(
        self, sender: mongo.User, receiver: mongo.User, name: str
    ) -> None:
        self.sender = sender
        self.receiver = receiver
        super().__init__(title=f'Tip {name}', timeout=None)

    quantity = discord.ui.TextInput(
        label='Quantity',
        style=discord.TextStyle.short,
        placeholder='Only numbers'
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        quantity = int(self.quantity.value)
        sender_info = await self.sender.check_user()
        receiver_info = await self.receiver.check_user()

        sender_balance = sender_info.get('balance', 0)
        receiver_balance = receiver_info.get('balance', 0)

        if quantity > sender_balance:
            return await interaction.response.send_message(
                'You don\'t have enough coins in the wallet', ephemeral=True
            )

        await self.sender.update_user({'balance': sender_balance - quantity})
        await self.receiver.update_user(
            {'balance': receiver_balance + quantity}
        )
        await interaction.response.send_message(
            'The tip has been sent', ephemeral=True
        )


class User(commands.Cog):
    def __init__(self, bot: Bitacora) -> None:
        self.bot = bot
        self.tip_ctx = app_commands.ContextMenu(
            name='Tip to user', callback=self.tip
        )
        self.bot.tree.add_command(self.tip_ctx)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.tip_ctx.name, type=self.tip_ctx.type)

    @app_commands.command(name='wallet')
    async def balance(self, interaction: discord.Interaction) -> None:
        """How many coins do you have in the wallet?"""
        user = mongo.User(interaction.guild_id, interaction.user.id)
        user_info = await user.check_user()
        balance = user_info.get('balance', 0)
        await interaction.response.send_message(
            f'You have {balance} coins in the wallet', ephemeral=True
        )

    async def tip(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        """Tip coins to another user"""
        if interaction.user.id != member.id:
            return await interaction.response.send_message(
                'You can\'t tip to yourself', ephemeral=True
            )

        guild_id = interaction.guild_id
        sender = mongo.User(guild_id, interaction.user.id)
        receiver = mongo.User(guild_id, member.id)

        receiver_name = f'{member.name}#{member.discriminator}'
        modal = TipModal(sender, receiver, receiver_name)
        await interaction.response.send_modal(modal)
