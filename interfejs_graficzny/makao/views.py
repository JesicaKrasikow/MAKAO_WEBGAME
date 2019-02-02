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
    global game
    understood = request.form['nocard']
    if understood == "OK":
        return redirect(url_for('game'))

@app.route('/game')
def game():
    # with open('write.pickle', 'rb') as handle:
    #     game = pickle.load(handle)
    global game, result
    nocardmessage = 0

    if result != Result.INIT and (result == Result.OK or result == Result.NO_CARD):
        game.next_player()

    turn = game.turn
    card_on_stack = game.card_stack[-1].show_stack_card()
    current_player = game.current_player
    current_player_cards = game.current_player.f_img_names()

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
    elif game.game_status.request_suit != "":
        flash("Zażądano konkretnego koloru karty: %s !" % game.game_status.request_suit)
    elif game.game_status.war_counter != 0:
        flash("Toczy się wojna!")
    elif game.game_status.stop_turn_counter != 0:
        flash("Gracze starają się siebie zablokować!")

    if len(game.proper_cards) == 0:
        result = Result.NO_CARD
        nocardmessage = 1

    return render_template('game.html', nocardmessage=nocardmessage, current_player_cards=current_player_cards, card_on_stack=card_on_stack, current_player=current_player, turn=turn)

# @app.route('/game/nocard')
# def nocard():
#     flash("Nie masz karty, musisz dobrać ze stosu.")
#
#     ok = request.form['OK']
#     if ok == 1:
#         return redirect(url_for('game'))
#     # time.sleep(5)
#     return redirect(url_for('nocard'))
#     # return render_template('nocard.html')




