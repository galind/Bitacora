from discord.ext import commands
from discord import app_commands
import discord
import random
import itertools

from cogs.utils import mongo
from bot import Bitacora

cards = {
    'A': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 10,
    'Q': 10,
    'K': 10,
}

suits = [
    'Spades',
    'Diamonds',
    'Clubs',
    'Hearts'
]


def start_game(name, balance, bet) -> discord.Embed:
    embed = discord.Embed(
        title=f'{name}\'s blackjack game', color=Bitacora().color
    )
    embed.add_field(name='Coins in the wallet', value=balance, inline=False)
    embed.add_field(name='Current bet', value=bet, inline=False)
    return embed


class StartGame(discord.ui.View):
    def __init__(self, bot: Bitacora):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label='Start game', style=discord.ButtonStyle.primary)
    async def start_game(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        pass

    @discord.ui.button(label='Raise bet', style=discord.ButtonStyle.success)
    async def raise_bet(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        pass

    @discord.ui.button(label='Lower bet', style=discord.ButtonStyle.danger)
    async def lower_bet(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        pass


class Blackjack(commands.Cog):
    def __init__(self, bot: Bitacora) -> None:
        self.bot = bot

    def start_game(self) -> discord.Embed:
        embed = discord.Embed()
        embed.title = f'{self.user.name}\'s blackjack game'
        return embed

    @app_commands.command(name='blackjack')
    async def blackjack(self, interaction: discord.Interaction) -> None:
        """Start a blackjack game"""
        user = mongo.User(interaction.guild_id, interaction.user.id)
        user_info = await user.check_user()
        balance = user_info.get('balance', 0)
        if balance == 0:
            return await interaction.response.send_message(
                'Your wallet is empty, you need coins to play', ephemeral=True
            )

        embed = start_game(interaction.user.name, balance, 0)
        view = StartGame(self.bot)
        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )
