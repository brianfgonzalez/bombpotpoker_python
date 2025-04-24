from flask import Flask, render_template, request, jsonify
import random
from itertools import combinations

app = Flask(__name__)

# Helper functions
def create_deck():
    suits = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return [{'suit': suits[suit], 'rank': rank} for suit in suits for rank in ranks]

def shuffle_deck():
    deck = create_deck()  # Create a standard deck of cards
    random.shuffle(deck)  # Shuffle the deck
    return deck

def evaluate_hand(cards):
    suits = [card['suit'] for card in cards]
    ranks = [card['rank'] for card in cards]
    rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    rank_counts = {rank: ranks.count(rank) for rank in ranks}
    unique_suits = set(suits)

    # Mapping of hand scores to hand types
    hand_types = {
        0: "High Card",
        1: "One Pair",
        2: "Two Pair",
        3: "Three of a Kind",
        6: "Flush",
        7: "Four of a Kind"
    }

    # Helper to sort cards by rank
    def card_sort_key(card):
        return rank_order.index(card['rank'])

    # Check for flush
    if len(unique_suits) == 1:
        return (6, hand_types[6], sorted(cards, key=card_sort_key, reverse=True))  # Flush

    # Check for pairs, three of a kind, four of a kind
    if 4 in rank_counts.values():
        return (7, hand_types[7], sorted(cards, key=lambda card: rank_counts[card['rank']], reverse=True))  # Four of a Kind
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        return (6, "Full House", sorted(cards, key=lambda card: rank_counts[card['rank']], reverse=True))  # Full House
    if 3 in rank_counts.values():
        return (3, hand_types[3], sorted(cards, key=lambda card: rank_counts[card['rank']], reverse=True))  # Three of a Kind
    if list(rank_counts.values()).count(2) == 2:
        return (2, hand_types[2], sorted(cards, key=lambda card: rank_counts[card['rank']], reverse=True))  # Two Pair
    if 2 in rank_counts.values():
        return (1, hand_types[1], sorted(cards, key=lambda card: rank_counts[card['rank']], reverse=True))  # One Pair

    # Default to high card
    return (0, hand_types[0], sorted(cards, key=card_sort_key, reverse=True))  # High Card

def determine_winner(hand1, hand2, flop):
    # Define rank order for comparing card ranks
    rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    # Generate all valid combinations of 2 player cards + 3 flop cards
    player1_combinations = [
        list(comb) for comb in combinations(hand1 + flop, 5)
        if sum(1 for card in comb if card in hand1) == 2  # Ensure exactly 2 cards are from Player 1's hand
    ]
    player2_combinations = [
        list(comb) for comb in combinations(hand2 + flop, 5)
        if sum(1 for card in comb if card in hand2) == 2  # Ensure exactly 2 cards are from Player 2's hand
    ]

    # Evaluate all combinations and find the best hand
    player1_best = max(player1_combinations, key=lambda hand: evaluate_hand(hand)[0])
    player2_best = max(player2_combinations, key=lambda hand: evaluate_hand(hand)[0])

    player1_score, player1_type, player1_hand = evaluate_hand(player1_best)
    player2_score, player2_type, player2_hand = evaluate_hand(player2_best)

    # Debugging: Print the evaluated hands
    print("Player 1 Evaluated Hand:", player1_hand, "Type:", player1_type, "Score:", player1_score)
    print("Player 2 Evaluated Hand:", player2_hand, "Type:", player2_type, "Score:", player2_score)

    if player1_score > player2_score:
        return "Player 1", player1_type, player1_hand
    elif player2_score > player1_score:
        return "Player 2", player2_type, player2_hand
    else:
        # In case of a tie, compare the high cards
        for card1, card2 in zip(player1_hand, player2_hand):
            if card1['rank'] != card2['rank']:
                if rank_order.index(card1['rank']) > rank_order.index(card2['rank']):
                    return "Player 1", player1_type, player1_hand
                else:
                    return "Player 2", player2_type, player2_hand
        return "Tie", player1_type, player1_hand

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    deck = shuffle_deck()
    player1_hand = [deck.pop() for _ in range(4)]  # Deal 4 cards to Player 1
    player2_hand = [deck.pop() for _ in range(4)]  # Deal 4 cards to Player 2
    first_flop = [deck.pop() for _ in range(3)]   # Deal 3 cards for the first flop
    second_flop = [deck.pop() for _ in range(3)]  # Deal 3 cards for the second flop

    return jsonify({
        'deck': deck,
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'first_flop': first_flop,
        'second_flop': second_flop
    })

@app.route('/determine_winner', methods=['POST'])
def determine_winner_route():
    data = request.json
    player1_hand = data['player1_hand']
    player2_hand = data['player2_hand']
    first_flop = data['first_flop']
    second_flop = data['second_flop']

    # Determine winners for each flop
    winner_first, hand_type_first, best_hand_first = determine_winner(player1_hand, player2_hand, first_flop)
    winner_second, hand_type_second, best_hand_second = determine_winner(player1_hand, player2_hand, second_flop)

    # Debugging: Print all combinations and the winning hands to the terminal
    print("First Flop Winning Hand:")
    print(best_hand_first)
    print("Second Flop Winning Hand:")
    print(best_hand_second)

    return jsonify({
        'winner_first': winner_first,
        'hand_type_first': hand_type_first,
        'best_hand_first': best_hand_first,
        'winner_second': winner_second,
        'hand_type_second': hand_type_second,
        'best_hand_second': best_hand_second
    })

@app.route('/reveal_turn', methods=['POST'])
def reveal_turn():
    data = request.json
    deck = data['deck']
    first_flop = data['first_flop']
    second_flop = data['second_flop']

    first_flop.append(deck.pop(0))
    second_flop.append(deck.pop(0))

    return jsonify({
        'first_flop': first_flop,
        'second_flop': second_flop,
        'deck': deck
    })

@app.route('/reveal_river', methods=['POST'])
def reveal_river():
    data = request.json
    deck = data['deck']
    first_flop = data['first_flop']
    second_flop = data['second_flop']

    first_flop.append(deck.pop(0))
    second_flop.append(deck.pop(0))

    return jsonify({
        'first_flop': first_flop,
        'second_flop': second_flop,
        'deck': deck
    })

@app.route('/reveal_winner', methods=['POST'])
def reveal_winner():
    data = request.get_json()
    player1_hand = data['player1_hand']
    player2_hand = data['player2_hand']
    first_flop = data['first_flop']
    second_flop = data['second_flop']

    # Determine winners for each flop
    winner_first, hand_type_first, best_hand_first = determine_winner(player1_hand, player2_hand, first_flop)
    winner_second, hand_type_second, best_hand_second = determine_winner(player1_hand, player2_hand, second_flop)

    return jsonify({
        "winner_first": winner_first,
        "hand_type_first": hand_type_first,
        "best_hand_first": best_hand_first,
        "winner_second": winner_second,
        "hand_type_second": hand_type_second,
        "best_hand_second": best_hand_second
    })

if __name__ == '__main__':
    app.run(debug=True)