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


def choose_bet(balance: int, bet: int = 0) -> discord.Embed:
    embed = discord.Embed(
        title='Blackjack game', color=Bitacora().color
    )
    embed.add_field(name='Coins in the wallet', value=balance, inline=False)
    embed.add_field(name='Current bet', value=bet, inline=False)
    return embed


class RaiseBetButton(discord.ui.Button):
    def __init__(self, bot: Bitacora, balance: int, bet: int) -> None:
        self.bot = bot
        self.balance = balance
        self.bet = bet
        super().__init__(
            label='Raise bet',
            style=discord.ButtonStyle.success,
            disabled=(bet == balance),
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        self.bet += 1
        embed = choose_bet(self.balance, self.bet)
        view = ChooseBetView(self.bot, self.balance, self.bet)
        await interaction.response.edit_message(embed=embed, view=view)


class LowerBetButton(discord.ui.Button):
    def __init__(self, bot: Bitacora, balance: int, bet: int) -> None:
        self.bot = bot
        self.balance = balance
        self.bet = bet
        super().__init__(
            label='Lower bet',
            style=discord.ButtonStyle.danger,
            disabled=(bet == 0)
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        self.bet -= 1
        embed = choose_bet(self.balance, self.bet)
        view = ChooseBetView(self.bot, self.balance, self.bet)
        await interaction.response.edit_message(embed=embed, view=view)


class StartGameButton(discord.ui.Button):
    def __init__(self, bot: Bitacora, balance: int, bet: int) -> None:
        self.bot = bot
        self.balance = balance
        self.bet = bet
        super().__init__(
            label='Start game',
            style=discord.ButtonStyle.primary,
            disabled=(bet == 0)
        )


class ChooseBetView(discord.ui.View):
    def __init__(self, bot: Bitacora, balance: int, bet: int = 0):
        super().__init__(timeout=None)
        self.add_item(RaiseBetButton(bot, balance, bet))
        self.add_item(LowerBetButton(bot, balance, bet))
        self.add_item(StartGameButton(bot, balance, bet))


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

        embed = choose_bet(balance)
        view = ChooseBetView(self.bot, balance)
        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )
