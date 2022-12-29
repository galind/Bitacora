from discord.ext import commands
from discord import app_commands
import discord
import random
import itertools

from cogs.utils import mongo
from bot import Bitacora

values = {
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
    'A': 11,
}

suits = [
    'Spades',
    'Diamonds',
    'Clubs',
    'Hearts'
]


def calculate_hand(hand: list) -> int:
    total = 0
    aces = 0
    for card in hand:
        total += values[card[0]]
        if card[0] == 'A':
            aces += 1

    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total


def game_table(dealer: list, player: list) -> discord.Embed:
    embed = discord.Embed(
        title='Blackjack game', color=Bitacora().color
    )

    dealer_hand = ''
    for card in dealer:
        dealer_hand += ' of '.join(card) + '\n'
    hand_value = calculate_hand(dealer)
    embed.add_field(
        name=f'Dealer hand ({hand_value})', value=dealer_hand, inline=False
    )

    player_hand = ''
    for card in player:
        player_hand += ' of '.join(card) + '\n'
    hand_value = calculate_hand(player)
    embed.add_field(
        name=f'Your hand ({hand_value})', value=player_hand, inline=False
    )

    return embed


class HitGameButton(discord.ui.Button):
    def __init__(
        self, bot: Bitacora, deck: list, dealer: list, player: list, bet: int
    ) -> None:
        self.bot = bot
        self.deck = deck
        self.dealer = dealer
        self.player = player
        self.bet = bet
        super().__init__(
            label='Hit',
            style=discord.ButtonStyle.primary,
            disabled=(calculate_hand(player) == 21)
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        card = self.deck.pop()
        self.player.append(card)

        embed = game_table(self.dealer, self.player)
        view = PlayGameView(
            self.bot, self.deck, self.dealer, self.player, self.bet
        )

        hand_value = calculate_hand(self.player)
        if hand_value > 21:
            embed.add_field(name='Result', value='Dealer wins', inline=False)
            view = None

        await interaction.response.edit_message(embed=embed, view=view)


class StandGameButton(discord.ui.Button):
    def __init__(
        self, bot: Bitacora, deck: list, dealer: list, player: list, bet: int
    ) -> None:
        self.bot = bot
        self.deck = deck
        self.dealer = dealer
        self.player = player
        self.bet = bet
        super().__init__(
            label='Stand',
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        player_hand = calculate_hand(self.player)
        dealer_hand = calculate_hand(self.dealer)
        while dealer_hand < 17:
            card = self.deck.pop()
            self.dealer.append(card)
            dealer_hand = calculate_hand(self.dealer)

        embed = game_table(self.dealer, self.player)
        user = mongo.User(interaction.guild_id, interaction.user.id)
        if player_hand > dealer_hand or dealer_hand > 21:
            await user.update_user({'balance': self.bet * 2}, method='inc')
            reward = f'{self.bet * 2} coins'
            embed.add_field(
                name='Result', value=f'Player wins {reward}', inline=False
            )
        elif player_hand == dealer_hand:
            await user.update_user({'balance': self.bet}, method='inc')
            embed.add_field(
                name='Result', value='It\'s a draw', inline=False
            )
        else:
            embed.add_field(
                name='Result', value='Dealer wins', inline=False
            )

        await interaction.response.edit_message(embed=embed, view=None)


class PlayGameView(discord.ui.View):
    def __init__(
        self, bot: Bitacora, deck: list, dealer: list, player: list, bet: int
    ) -> None:
        super().__init__(timeout=None)
        self.add_item(HitGameButton(bot, deck, dealer, player, bet))
        self.add_item(StandGameButton(bot, deck, dealer, player, bet))


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

    def shuffle_deck(self) -> None:
        random.shuffle(self.deck)
        random.shuffle(self.deck)
        random.shuffle(self.deck)

    def get_deck(self) -> None:
        self.deck = list(itertools.product(values, suits))
        self.shuffle_deck()

    async def callback(self, interaction: discord.Interaction) -> None:
        user = mongo.User(interaction.guild_id, interaction.user.id)
        await user.update_user({'balance': -self.bet}, method='inc')

        self.get_deck()
        self.deck.pop()  # Burn card

        dealer = []
        player = []

        card = self.deck.pop()
        player.append(card)
        card = self.deck.pop()
        dealer.append(card)
        card = self.deck.pop()
        player.append(card)

        embed = game_table(dealer, player)
        view = PlayGameView(self.bot, self.deck, dealer, player, self.bet)
        await interaction.response.edit_message(embed=embed, view=view)


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
