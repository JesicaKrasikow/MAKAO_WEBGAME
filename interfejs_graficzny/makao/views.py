from flask import render_template, redirect, request, flash, url_for
from makao import app
from makao.objects import *
from .game import *
from .rules import *
from .objects import *
from flask import redirect
import time

global game, result

@app.route('/')
def index():
    global game, result
    game = Game()
    result = Result.INIT
    return render_template('index.html')

@app.route('/game/move', methods=['POST'])
def move():
    global game, result
    result = Result.OK
    # card = request.form['card']
    cards = request.form.getlist('card')
    chosen_cards = []
    for card in cards:
        chosen_cards.append(game.current_player.deck[int(card)])

    # chosen_card = game.current_player.deck[int(card)]
    if len(chosen_cards) > 1:
        card_for_compare = chosen_cards[0]
        for card in chosen_cards:
            if card.rank != card_for_compare.rank:
                result = Result.WRONG_CARD
                print("Wybrano karty z różnymi figurami. Spróbuj jeszcze raz.")
                break

    if result != Result.WRONG_CARD:
        result = game.begin_turn(chosen_cards)

    return redirect(url_for('game'))

@app.route('/game/nocard', methods=['POST'])
def nocard():
    global game, result
    result = Result.OK
    understood = request.form['nocard']
    if understood == "OK":
        return redirect(url_for('game'))

@app.route('/game/stopturn', methods=['POST'])
def stopturn():
    global game, result
    result = Result.OK
    understood = request.form['stopturn']
    if understood == "OK":
        return redirect(url_for('game'))

@app.route('/game/changesuit', methods=['POST'])
def changesuit():
    global game, result
    new_suit = request.form['new_suit']
    if new_suit == "":
        flash("Wybierz kolor karty, który masz w swojej talii!")
        return redirect(url_for('game'))

    if Rules.change_suit(game.current_player, game.game_status, new_suit) == False:
        flash("Wybierz kolor karty, który masz w swojej talii!")
    else:
        result = Result.OK

    return redirect(url_for('game'))

@app.route('/game/changerank', methods=['POST'])
def changerank():
    global game, result
    new_rank = int(request.form['new_rank'])
    if new_rank == 0:
        flash("Wybierz figurę, którą masz w swojej talii!")
        return redirect(url_for('game'))
    if Rules.change_rank(game.current_player, game.game_status, game.players_number, game.card_stack, new_rank) == False:
        flash("Wybierz figurę, którą masz w swojej talii!")
    else:
        result = Result.OK

    return redirect(url_for('game'))

@app.route('/game')
def game():
    global game, result
    nocardmessage = 0
    print("Result: %s" % (result))

    if result == Result.GAME_OVER:
        return render_template('gameover.html',winners = game.winners_list)

    if result != Result.INIT and (result == Result.OK or result == Result.NO_CARD):
        print("zmiana gracza")
        game.next_player()

    turn = game.turn
    card_on_stack = game.card_stack[-1].show_stack_card()
    current_player = game.current_player
    current_player_cards = game.current_player.f_img_names()
    print("Wypisuję karty gracza:")
    print(current_player_cards)

    if game.if_player_stop_turn() == True:
        nocardmessage = 4
        return render_template('game.html', nocardmessage=nocardmessage, current_player_cards=current_player_cards,
                               card_on_stack=card_on_stack, current_player=current_player, turn=turn)

    if result == Result.CHANGE_RANK:
        nocardmessage = 2
        return render_template('game.html', nocardmessage=nocardmessage, current_player_cards=current_player_cards,
                               card_on_stack=card_on_stack, current_player=current_player, turn=turn)

    elif result == Result.CHANGE_SUIT:
        nocardmessage = 3
        return render_template('game.html', nocardmessage=nocardmessage, current_player_cards=current_player_cards,
                               card_on_stack=card_on_stack, current_player=current_player, turn=turn)

    if result == Result.WRONG_CARD:
        flash("Wybrałeś złą kartę. Spróbuj jeszcze raz.")

    print("gra teraz gracz numer %d" % current_player.id)
    game.proper_cards = game.check_player_cards()

    # check if there is any request to inform player
    if game.game_status.request_rank != 0:
        flash("Zażądano konkretnej wartości karty: %d!" % game.game_status.request_rank)
        print("Zażądano konkretnej wartości karty: %d!" % game.game_status.request_rank)
    elif game.game_status.request_suit != "":
        if game.game_status.request_suit == "C":
            flash("Zmieniono kolor karty: TREFL!")
            print("Zmieniono kolor karty: %s !" % game.game_status.request_suit)
        if game.game_status.request_suit == "D":
            flash("Zmieniono kolor karty: KARO!")
            print("Zmieniono kolor karty: %s !" % game.game_status.request_suit)
        if game.game_status.request_suit == "H":
            flash("Zmieniono kolor karty: KIER!")
            print("Zmieniono kolor karty: %s !" % game.game_status.request_suit)
        if game.game_status.request_suit == "S":
            flash("Zmieniono kolor karty: PIK!")
            print("Zmieniono kolor karty: %s !" % game.game_status.request_suit)
    elif game.game_status.war_counter != 0:
        flash("Toczy się wojna!")
        print("Toczy się wojna!")
    elif game.game_status.stop_turn_counter != 0:
        flash("Gracze starają się siebie zablokować!")
        print("Gracze starają się siebie zablokować!")

    if len(game.proper_cards) == 0:
        result = Result.NO_CARD
        nocardmessage = 1


    return render_template('game.html', nocardmessage=nocardmessage, current_player_cards=current_player_cards,
                           card_on_stack=card_on_stack, current_player=current_player, turn=turn)






