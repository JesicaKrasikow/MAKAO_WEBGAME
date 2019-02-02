from enum import Enum
from enum import IntEnum
from random import *

# Enum for the card
class Rank(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE= 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

# Suit enum for playing card
class Suit(Enum):
    SPADES = 'S'
    CLUBS = 'C'
    HEARTS = 'H'
    DIAMONDS = 'D'

# Class to hold info for playing card
class PlayingCard:
    def __init__(self, card_value, card_suit):
        self.rank = card_value
        self.suit = card_suit

    def __repr__(self):
        name = self.__class__.__name__
        return "%s%s" % (self.rank.value, self.suit.value)

    def  __eq__(self, second):
        if isinstance(second, str):
            return '%d%s' % (self.rank, self.suit) == second
        elif isinstance(second, PlayingCard):
            return self.rank == second.rank and self.suit == second.suit
        # return self.rank == second.rank and self.suit == second.suit

    def __ne__(self, other):
        return not self == other

    # Function to draw single card from deck
    @staticmethod
    def draw_card(deck):
        rand_card = randint(0, len(deck) - 1)
        return deck.pop(rand_card)

    # Function to create full deck of cards
    @staticmethod
    def create_deck():
        deck = []
        for suit in Suit:
            for rank in Rank:
                deck.append(PlayingCard(Rank(rank), Suit(suit)))
        return deck

    # These two functions show last card on stack (second one in flask)
    @staticmethod
    def show_stack(card):
        output_text = "Stack card: %s_%s" % (card.rank.name, card.suit.value)
        print(output_text)

    def show_stack_card(card):
        output_name = str(card.rank.value)
        output_name += str(card.suit.value)
        return output_name


# Class to hold info of player
class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.deck = []

    def __repr__(self):
        name = self.__class__.__name__
        return "%s('%d')" % (name, self.id)

    # Show player's deck
    def show_cards(self):
        # print(self.deck)
        output_text = "Player[%d] cards: " % (self.id)
        card_number = 0
        for card in self.deck:
            output_text += "%d:%s_%s " % (card_number, card.rank.name, card.suit.value)
            card_number += 1
        return output_text

    # Show player's deck in flask
    def f_img_names(self):
        img_names = []
        for card in self.deck:
            img_names.append( "%d%s" % (card.rank.value, card.suit.value))
        return img_names

    # # Choose card
    # def choose_card(self, value):
    #     # print('Wybierz kartę:')
    #     # while True:
    #     #     try:
    #     #         card_number = int(input())
    #     #         break
    #     #     except ValueError:
    #     #         print("Wpisz odpowiednią liczbę!!")
    #     #
    #     # return self.deck[card_number]
    #     card = self.deck[int(value)]
    #     print(self.deck[int(value)])
    #     return card

    # Add new card to player's deck
    def add_card(self, card):
        self.deck.append(card)

    # Remove card from player's deck
    def remove_card(self, card):
        self.deck.remove(card)

    # Deal cards for players
    @staticmethod
    def deal(Player, deck):
        for i in range(5):
            Player.add_card(PlayingCard.draw_card(deck))


