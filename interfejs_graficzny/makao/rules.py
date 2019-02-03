from enum import IntFlag
from .objects import *
from flask import render_template, redirect, request, flash, url_for


# Class with all the requests from the players
class GameState:
    def __init__(self, players_num):
        self.request_suit = ""

        self.request_rank = 0
        self.request_counter = 0
        self.last_given_jack = 0
        self.war_counter = 0
        self.stop_turn_counter = 0
        self.stop_turn_players = []

        for i in range(players_num):
            self.stop_turn_players.append(0)


class Result(IntFlag):
    INIT = 0
    NO_CARD = 1
    OK = 2
    WRONG_CARD = 3
    REQUEST_FOUR = 4
    GAME_OVER = 5
    CHANGE_SUIT = 6
    CHANGE_RANK = 7


class Rules:
    # If player does not have enough cards, they have to take new card from deck
    @staticmethod
    def take_cards(deck, stack, player, num_cards):
        print('Musisz dobrać kartę.')
        for card in range(num_cards):
            if len(deck) <= 0:
                deck = stack[0:len(stack) - 2]
                stack = [stack[-1]]
                print('Skończyła się talia kart. Dobrano karty ze sterty i przetasowano.')
            player.add_card(PlayingCard.draw_card(deck))

    # For the nonfunctional cards and queens
    @staticmethod
    def standard_hand(player, stack, deck, status, chosed):
        print("standard hand")
        stack_card = stack[-1]

        # Check if player has proper cards
        proper_cards = []
        for card in player.deck:
            if card.rank.value == stack_card.rank.value  or card.suit.value  == stack_card.suit.value : #or card.rank == Rank.QUEEN
                proper_cards.append(card)

        if len(proper_cards) == 0:
            Rules.take_cards(deck, stack, player, 1)
            print("Musisz dobrać kartę")
            return

        # Player has proper cards, so they can choose card to play
        while True:
            print(proper_cards)
            print(chosed)
            print(player.deck[int(chosed)])
            chosen_card = player.deck[int(chosed)]
            # temp = chosen_card[-1]
            # temp2 = chosen_card[:-1]

            # chosen_card = player.choose_card()
            # chosen_card = player.choose_card(card)
            # print(chosen_card in proper_cards)
            #             # test_cards = []
            #             # for card in proper_cards:
            #             #     test_cards.append(str(card))

            if chosen_card in proper_cards:
                # Checking if player puts war card on stack (it begins war)
                if chosen_card.rank == Rank.TWO:
                    status.war_counter += 2
                elif chosen_card.rank == Rank.THREE:
                    status.war_counter += 3
                if chosen_card.rank == Rank.KING and (chosen_card.suit == Suit.SPADES or chosen_card.suit == Suit.HEARTS):
                    status.war_counter += 5

                # Checking if player puts FOUR on stack (it stops next player for one turn)
                if chosen_card.rank == Rank.FOUR:
                    status.stop_turn_counter += 1

                player.remove_card(chosen_card)
                stack.append(chosen_card)
                return Result.OK
            else:
                print('Zła karta!')
                return Result.WRONG_CARD

    # If player chooses to play ACE, they can change the suit
    @staticmethod
    def change_suit(player, status, new_suit):
        print("change suit")

        suits = ['S', 'C', 'H', 'D']
        print("To jest nowy suit:")
        print(new_suit)
        players_card_suits = []

        for card in player.deck:
            players_card_suits.append(card.suit.value)

        if new_suit in players_card_suits:
            print("Kolejny gracz musi dać kartę z suit: %s." % (new_suit))
            status.request_suit = new_suit
            return True
        else:
            print('Wybierz kolor, który masz!')
            print('Wybierz nowy suit: S, C, H, D')
            return False


    # If there is a requested suit from the other player's ACE
    @staticmethod
    def request_ace(player, stack, deck, status):
        print("request ace")

        stack_card = stack[-1]

        # Check if player has proper cards
        proper_cards = []
        for card in player.deck:
            if card.rank == stack_card.rank or card.suit.value == status.request_suit:
                proper_cards.append(card)

        if len(proper_cards) == 0:
            Rules.take_cards(deck, stack, player, 1)
            return

        # Player has proper cards, so they can choose card to play
        while True:
            chosen_card = player.choose_card()
            if chosen_card in proper_cards:

                # Checking if player puts war card on stack (it begins war)
                if chosen_card.rank == Rank.TWO:
                    status.war_counter += 2
                elif chosen_card.rank == Rank.THREE:
                    status.war_counter += 3
                if chosen_card.rank == Rank.KING and (chosen_card.suit == Suit.SPADES or chosen_card.suit == Suit.HEARTS):
                    status.war_counter += 5

                # Checking if player puts FOUR on stack (it stops next player for one turn)
                if chosen_card.rank == Rank.FOUR:
                    status.stop_turn_counter += 1

                player.remove_card(chosen_card)
                stack.append(chosen_card)
                status.request_suit = ""
                return Result.OK

            else:
                print('Zła karta!')

    @staticmethod
    def change_rank(player, status, number_of_players, stack, new_rank):

        status.last_given_jack = stack[-1] #It remembers the last given card (JACK) to see when the new JACK requests comes to game
        print("change rank")

        # If player chooses to play JACK, they can change the rank
        ranks = [Rank.FIVE.value, Rank.SIX.value, Rank.SEVEN.value, Rank.EIGHT.value, Rank.NINE.value, Rank.TEN.value]
        players_card_ranks = []

        for card in player.deck:
            players_card_ranks.append(card.rank.value)

        if [i for i in players_card_ranks if i in ranks]:
            # print('Wybierz nowy rank: 5, 6, 7, 8, 9, 10')
            # new_rank = int(input())
            # print(new_rank)
            print("Wybrany rank:")
            print(new_rank)
            print(type(new_rank))
            if new_rank in players_card_ranks:
                print("Kolejny gracz musi dać kartę z rank: %d." % (new_rank))
                status.request_rank = new_rank
                status.request_counter = number_of_players
                return True
            else:
                print('Wybierz kartę, którą masz!')
                print('Wybierz nowy rank: 5, 6, 7, 8, 9, 10')
                return False
                # new_rank = int(input())
        else:
            print('Nie możesz żądać żadnej karty, bo nie masz kart niefunkcyjnych.')
            return True

    # If there is requested rank from the others player's JACK
    @staticmethod
    def request_jack(player, stack, deck, status):
        print("request jack")

        stack_card = stack[-1]

        # Check if player has proper cards
        proper_cards = []
        for card in player.deck:
            if card.rank == status.request_rank: #player has requested card (in the requested rank)
                proper_cards.append(card)
            elif card.suit.value == stack_card.suit.value: #player has another jack
                if card.rank == Rank.JACK:
                    proper_cards.append(card)

        status.request_counter -= 1

        if len(proper_cards) == 0:
            Rules.take_cards(deck, stack, player, 1)
            return

        # Player has proper cards, so they can choose card to play
        while True:
            chosen_card = player.choose_card()
            if chosen_card in proper_cards:
                player.remove_card(chosen_card)
                stack.append(chosen_card)

                if status.request_counter <= 0:
                    status.request_rank = 0
                    status.last_given_jack = 0
                return Result.OK
            else:
                print('Zła karta!')

    # If player draws KING
    @staticmethod
    def request_war(player, stack, deck, status):
        print("request war")
        print("Counter: %d" % (status.war_counter))

        stack_card = stack[-1]

        war_cards = [2, 3]

        # Check if player has proper cards
        proper_cards = []

        if stack_card.rank == Rank.KING:
            for card in player.deck:
                if card.rank == stack_card.rank and (card.suit == Suit.SPADES or card.suit == Suit.HEARTS):
                    proper_cards.append(card)
                elif card.rank.value in war_cards and card.suit == stack_card.suit:
                    proper_cards.append(card)

        else:
            for card in player.deck:
                if card.rank == Rank.KING and (card.suit == Suit.SPADES or card.suit == Suit.HEARTS) and card.suit == stack_card.suit:
                    proper_cards.append(card)
                elif card.rank == stack_card.rank:
                    proper_cards.append(card)
                elif card.suit == stack_card.suit and card.rank.value in war_cards:
                    proper_cards.append(card)


        if len(proper_cards) == 0:
            Rules.take_cards(deck, stack, player, status.war_counter)
            status.war_counter = 0
            return

        # Player has proper cards, so they can begin a war
        while True:
            chosen_card = player.choose_card()
            if chosen_card in proper_cards:
                player.remove_card(chosen_card)
                stack.append(chosen_card)
                if chosen_card.rank == Rank.TWO:
                    status.war_counter += 2
                elif chosen_card.rank == Rank.THREE:
                    status.war_counter += 3
                else:
                    status.war_counter += 5
                return Result.OK
            else:
                print('Zła karta!')


   # If player draws FOUR
    @staticmethod
    def request_four(player, stack, deck, status):
        print("request four")
        print("Counter: %d" % (status.stop_turn_counter))

        stack_card = stack[-1]

        # Check if player has proper cards
        proper_cards = []

        for card in player.deck:
            if card.rank == Rank.FOUR:
                proper_cards.append(card)

        if len(proper_cards) == 0:
            status.stop_turn_players[player.id] = status.stop_turn_counter
            status.stop_turn_counter = 0
            return

        # Player has proper cards, so they can begin a war
        while True:
            chosen_card = player.choose_card()
            if chosen_card in proper_cards:
                player.remove_card(chosen_card)
                stack.append(chosen_card)
                status.stop_turn_counter += 1
                return Result.OK
            else:
                print('Zła karta!')

