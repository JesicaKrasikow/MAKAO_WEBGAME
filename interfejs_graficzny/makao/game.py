from .objects import *
from .rules import *


class Game():

    def __init__(self):

        # How many players
        self.players_number = 2

        # Create full deck of shuffled cards
        self.current_deck = PlayingCard.create_deck()

        # Create players with their decks of cards
        self.players_list = []
        for id in range(self.players_number):
            self.players_list.append(Player(id))
            Player.deal(self.players_list[id], self.current_deck)
        # print(players_list[id].deck)

        # Hold used cards
        self.card_stack = []

        # Choose beggining card
        self.card_stack.append(PlayingCard.draw_card(self.current_deck))

        # Id of the current player changes after every move
        self.current_player_id = 0
        self.current_player = self.players_list[self.current_player_id]

        # Check if beggining card is functional, if so - change it
        functional_cards = [2, 3, 4, 11, 13, 14]
        while True:
            if self.card_stack[-1].rank.value in functional_cards:
                self.card_stack.append(PlayingCard.draw_card(self.current_deck))
            else:
                break

        # Game starts on turn number 0
        self.turn = 0
        # List of winners
        self.winners_list = []
        # Variable which tells if there is any request from the card on the stack
        self.game_status = GameState(self.players_number)

        self.proper_cards = []


    # Function checks if in player's deck is any proper card to put on the stack
    def check_player_cards(self):
        stack_card = self.card_stack[-1]
        proper_cards = []

        #Checks if there is any suit request
        if self.game_status.request_suit != "":
            # Check if player has proper cards
            for card in self.current_player.deck:
                if card.rank == stack_card.rank or card.suit.value == self.game_status.request_suit:
                    proper_cards.append(card)

            if len(proper_cards) == 0:
                Rules.take_cards(self.current_deck, self.card_stack, self.current_player, 1)
                print("Musisz dobrać kartę")

        #Checks if there is any rank request
        elif self.game_status.request_rank != 0:
            # Check if player has proper cards
            for card in self.current_player.deck:
                if card.rank == self.game_status.request_rank:  # player has requested card (in the requested rank)
                    proper_cards.append(card)
                elif card.suit.value == stack_card.suit.value:  # player has another jack
                    if card.rank == Rank.JACK:
                        proper_cards.append(card)

            self.game_status.request_counter -= 1

            if len(proper_cards) == 0:
                Rules.take_cards(self.current_deck, self.card_stack, self.current_player, 1)
                print("Musisz dobrać kartę")

        # Check if there is any war
        elif self.game_status.war_counter != 0:
            # Check if player has proper cards
            war_cards = [2, 3]

            if stack_card.rank == Rank.KING:
                for card in self.current_player.deck:
                    if card.rank == stack_card.rank and (card.suit == Suit.SPADES or card.suit == Suit.HEARTS):
                        proper_cards.append(card)
                    elif card.rank.value in war_cards and card.suit == stack_card.suit:
                        proper_cards.append(card)

            else:
                for card in self.current_player.deck:
                    if card.rank == Rank.KING and (
                            card.suit == Suit.SPADES or card.suit == Suit.HEARTS) and card.suit == stack_card.suit:
                        proper_cards.append(card)
                    elif card.rank == stack_card.rank:
                        proper_cards.append(card)
                    elif card.suit == stack_card.suit and card.rank.value in war_cards:
                        proper_cards.append(card)

            if len(proper_cards) == 0:
                Rules.take_cards(self.current_deck, self.card_stack, self.current_player, self.game_status.war_counter)
                print("Musisz dobrać kartę")
                self.game_status.war_counter = 0

        # Check if there is any request to stop player's turn
        elif self.game_status.stop_turn_counter != 0:
            # Check if player has proper cards

            for card in self.current_player.deck:
                if card.rank == Rank.FOUR:
                    proper_cards.append(card)

            if len(proper_cards) == 0:
                self.game_status.stop_turn_players[self.current_player.id] = self.game_status.stop_turn_counter
                self.game_status.stop_turn_counter = 0

        else:
            for card in self.current_player.deck:
                if card.rank.value == stack_card.rank.value or card.suit.value == stack_card.suit.value:
                    proper_cards.append(card)

            if len(proper_cards) == 0:
                Rules.take_cards(self.current_deck, self.card_stack, self.current_player, 1)
                print("Musisz dobrać kartę")

        print("Wypisuję proper_cards:")
        print(proper_cards)
        return proper_cards



    def next_player(self):
        # Next player
        if self.card_stack[-1].rank == Rank.KING and self.card_stack[-1].suit == Suit.SPADES and self.game_status.war_counter != 0:

            if self.current_player_id == 0:
                self.current_player_id = self.players_number - 1
            else:
                self.current_player_id -= 1

        else:
            self.current_player_id += 1

        if self.current_player_id >= self.players_number:
            self.current_player_id = 0

            self.turn += 1

        self.current_player = self.players_list[self.current_player_id]



    # Function checks if the choosen card is in proper_cards list
    def if_card_is_proper(self, chosen_card, proper_cards):

        status = self.game_status
        player = self.current_player
        stack = self.card_stack

        # Checks if there is any suit request
        if self.game_status.request_suit != "":
            if chosen_card in proper_cards:

                # Checking if player puts war card on stack (it begins war)
                if chosen_card.rank == Rank.TWO:
                    status.war_counter += 2
                elif chosen_card.rank == Rank.THREE:
                    status.war_counter += 3
                if chosen_card.rank == Rank.KING and (
                        chosen_card.suit == Suit.SPADES or chosen_card.suit == Suit.HEARTS):
                    status.war_counter += 5

                # Checking if player puts FOUR on stack (it stops next player for one turn)
                if chosen_card.rank == Rank.FOUR:
                    status.stop_turn_counter += 1

                player.remove_card(chosen_card)
                stack.append(chosen_card)
                status.request_suit = ""

            else:
                return False


        # Checks if there is any rank request
        elif self.game_status.request_rank != 0:
            if chosen_card in proper_cards:
                player.remove_card(chosen_card)
                stack.append(chosen_card)

                if status.request_counter <= 0:
                    status.request_rank = 0
                    status.last_given_jack = 0
            else:
                return False


        # Check if there is any war
        elif self.game_status.war_counter != 0:
            # Check if player has proper cards
            war_cards = [2, 3]
            # Player has proper cards, so they can begin a war
            if chosen_card in proper_cards:
                player.remove_card(chosen_card)
                stack.append(chosen_card)
                if chosen_card.rank == Rank.TWO:
                    status.war_counter += 2
                elif chosen_card.rank == Rank.THREE:
                    status.war_counter += 3
                else:
                    status.war_counter += 5
            else:
                return False


        # Check if there is any request to stop player's turn
        elif self.game_status.stop_turn_counter != 0:
            if chosen_card in proper_cards:
                player.remove_card(chosen_card)
                stack.append(chosen_card)
                status.stop_turn_counter += 1
            else:
                return False

        # Standard hand
        else:
            if chosen_card in proper_cards:
                # Checking if player puts war card on stack (it begins war)
                if chosen_card.rank == Rank.TWO:
                    status.war_counter += 2
                elif chosen_card.rank == Rank.THREE:
                    status.war_counter += 3
                if chosen_card.rank == Rank.KING and (
                        chosen_card.suit == Suit.SPADES or chosen_card.suit == Suit.HEARTS):
                    status.war_counter += 5

                # Checking if player puts FOUR on stack (it stops next player for one turn)
                if chosen_card.rank == Rank.FOUR:
                    status.stop_turn_counter += 1

                player.remove_card(chosen_card)
                stack.append(chosen_card)
            else:
                print('Zła karta!')
                return False


        return True


    def give_chosen_card(self, card):

        if card.rank == Rank.FOUR:
            self.game_status.stop_turn_counter += 1
        elif card.rank == Rank.TWO:
            self.game_status.war_counter += 2
        elif card.rank == Rank.THREE:
            self.game_status.war_counter += 3
        elif card.rank == Rank.KING and (card.suit == Suit.SPADES or card.suit == Suit.HEARTS):
            self.game_status.war_counter += 5

        self.current_player.remove_card(card)
        self.card_stack.append(card)


    def if_player_stop_turn(self):

        # Check if current player is able to play (stop_turn_players[id] > 0)
        if self.game_status.stop_turn_players[self.current_player.id] > 0:
            self.game_status.stop_turn_players[self.current_player.id] -= 1
            return True

        return False

    #Game is on!
    def begin_turn(self, chosen_cards):
        print("BEGIN TURN\n")

        print("Karta na stacku: %s" % (self.card_stack[-1]))

        if self.current_player_id == 0:
            print('#########################################################')
            print('Obecna tura: %d \n' % (self.turn))


        found_proper_card = False

        for card in chosen_cards:
            if self.if_card_is_proper(card, self.proper_cards) == True:
                chosen_cards.remove(card)
                found_proper_card = True
                break

        if found_proper_card == False:
            print("Zła karta. Musisz wybrac jeszcze raz")
            return Result.WRONG_CARD

        for card in chosen_cards:
            self.give_chosen_card(card)

        PlayingCard.show_stack(self.card_stack[-1])

        self.current_player.show_cards()
        print(self.current_player.show_cards())

        # Check if current_player has any cards
        if len(self.current_player.deck) == 0:
            self.winners_list.append(self.current_player_id)
            print("Wygrał gracz nr %d!" % (self.current_player_id))
            del self.players_list[self.current_player_id]
            # players_list.del(current_player_id)
            self.players_number -= 1
            if self.players_number <= 1:
                self.winners_list.append(self.players_list[0])
                return Result.GAME_OVER

        if self.game_status.request_suit == "" and self.card_stack[-1].rank == Rank.ACE:
            return Result.CHANGE_SUIT
            # Rules.change_suit(self.current_player, self.game_status)
        elif self.card_stack[-1].rank == Rank.JACK and self.game_status.last_given_jack != self.card_stack[-1]:
            return Result.CHANGE_RANK
            # Rules.change_rank(self.current_player, self.game_status, self.players_number, self.card_stack)


        return Result.OK

