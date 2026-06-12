import random
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'super-secret-key-for-blackjack'

def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return [{'suit': s, 'rank': r} for s in suits for r in ranks]

def card_value(card):
    if card['rank'] in ['J', 'Q', 'K']: return 10
    if card['rank'] == 'A': return 11
    return int(card['rank'])

def calculate_score(hand):
    score = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card['rank'] == 'A')
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score

@app.route('/')
def home():
    if 'balance' not in session:
        session['balance'] = 1000
    return render_template('index.html', balance=session['balance'])

@app.route('/bet', methods=['POST'])
def bet():
    bet_amount = int(request.form['bet'])
    if bet_amount <= 0 or bet_amount > session.get('balance', 0):
        return redirect(url_for('home'))
        
    session['bet'] = bet_amount
    deck = create_deck()
    random.shuffle(deck)
    
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    
    session['deck'] = deck
    session['player_hand'] = player_hand
    session['dealer_hand'] = dealer_hand
    session['game_over'] = False
    
    return redirect(url_for('game'))

@app.route('/game')
def game():
    if 'player_hand' not in session:
        return redirect(url_for('home'))
        
    player_score = calculate_score(session['player_hand'])
    dealer_score = calculate_score(session['dealer_hand'])
    
    return render_template(
        'game.html',
        player_hand=session['player_hand'],
        dealer_hand=session['dealer_hand'],
        player_score=player_score,
        dealer_score=dealer_score,
        game_over=session['game_over'],
        result=session.get('result')
    )

@app.route('/hit')
def hit():
    session['player_hand'].append(session['deck'].pop())
    score = calculate_score(session['player_hand'])
    if score > 21:
        session['game_over'] = True
        session['result'] = 'Bust! You lose.'
        session['balance'] -= session['bet']
    session.modified = True
    return redirect(url_for('game'))

@app.route('/stand')
def stand():
    dealer_hand = session['dealer_hand']
    deck = session['deck']
    while calculate_score(dealer_hand) < 17:
        dealer_hand.append(deck.pop())
    
    player_score = calculate_score(session['player_hand'])
    dealer_score = calculate_score(dealer_hand)
    
    if dealer_score > 21 or player_score > dealer_score:
        session['result'] = 'You win!'
        session['balance'] += session['bet']
    elif player_score < dealer_score:
        session['result'] = 'Dealer wins.'
        session['balance'] -= session['bet']
    else:
        session['result'] = 'Push.'
        
    session['dealer_hand'] = dealer_hand
    session['game_over'] = True
    session.modified = True
    return redirect(url_for('game'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
