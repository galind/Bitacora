from discord.ext import commands
from discord import app_commands
import discord
import random

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


class Blackjack(commands.Cog):
    def __init__(self, bot: Bitacora) -> None:
        self.bot = bot

    def shuffle_deck(self, deck: list) -> list:
        random.shuffle(deck)
        random.shuffle(deck)
        random.shuffle(deck)
        return deck

    def get_deck(self) -> list:
        deck = []
        for s in suits:
            for c in cards:
                deck.append(f'{c} of {s}')
        return self.shuffle_deck(deck)

    @app_commands.command(name='blackjack')
    async def blackjack(self, interaction: discord.Interaction) -> None:
        """Start a blackjack game"""
