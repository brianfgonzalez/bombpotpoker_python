from flask import Flask, render_template, request, jsonify
import random
from itertools import combinations

app = Flask(__name__)

# Example deck of cards
SUITS = ['♥', '♦', '♣', '♠']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
DECK = [{'rank': rank, 'suit': suit} for suit in SUITS for rank in RANKS]

def generate_deck():
    return [{'rank': rank, 'suit': suit} for suit in SUITS for rank in RANKS]

# Helper functions
def create_deck():
    suits = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return [{'suit': suits[suit], 'rank': rank} for suit in suits for rank in ranks]

def shuffle_deck():
    deck = create_deck()  # Create a standard deck of cards
    random.shuffle(deck)  # Shuffle the deck
    return deck

def compare_two_pair(hand1, hand2):
    # hand1 and hand2 are tuples: (rank, [pair1, pair2, kicker])
    # Higher pair wins, then lower pair, then kicker
    for i in range(3):
        if hand1[1][i] > hand2[1][i]:
            return 1
        elif hand1[1][i] < hand2[1][i]:
            return -1
    return 0

def evaluate_hand(cards):
    suits = [card['suit'] for card in cards]
    ranks = [card['rank'] for card in cards]
    rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    rank_counts = {rank: ranks.count(rank) for rank in ranks}
    unique_suits = set(suits)

    hand_types = {
        0: "High Card",
        1: "One Pair",
        2: "Two Pair",
        3: "Three of a Kind",
        6: "Flush",
        7: "Four of a Kind"
    }

    def card_sort_key(card):
        return rank_order.index(card['rank'])

    # Check for flush
    if len(unique_suits) == 1:
        return (6, hand_types[6], sorted(cards, key=card_sort_key, reverse=True))  # Flush

    # Four of a Kind
    if 4 in rank_counts.values():
        return (7, hand_types[7], sorted(cards, key=lambda card: (rank_counts[card['rank']], card_sort_key(card)), reverse=True))  # Four of a Kind

    # Full House
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        return (6, "Full House", sorted(cards, key=lambda card: (rank_counts[card['rank']], card_sort_key(card)), reverse=True))  # Full House

    # Three of a Kind
    if 3 in rank_counts.values():
        return (3, hand_types[3], sorted(cards, key=lambda card: (rank_counts[card['rank']], card_sort_key(card)), reverse=True))  # Three of a Kind

    # Two Pair
    if list(rank_counts.values()).count(2) == 2:
        pairs = sorted([rank for rank, count in rank_counts.items() if count == 2], key=rank_order.index, reverse=True)
        kicker = sorted([rank for rank, count in rank_counts.items() if count == 1], key=rank_order.index, reverse=True)[0]
        return (2, [pairs[0], pairs[1], kicker], sorted(cards, key=card_sort_key, reverse=True))  # Two Pair

    # One Pair
    if 2 in rank_counts.values():
        pair_rank = max([rank for rank, count in rank_counts.items() if count == 2], key=lambda r: rank_order.index(r))
        kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], key=rank_order.index, reverse=True)
        # Sort cards: pair cards first (highest pair), then kickers in order
        sorted_cards = (
            [card for card in cards if card['rank'] == pair_rank] +
            sorted([card for card in cards if card['rank'] != pair_rank], key=card_sort_key, reverse=True)
        )
        return (1, [pair_rank] + kickers, sorted_cards)  # One Pair

    # High Card
    return (0, hand_types[0], sorted(cards, key=card_sort_key, reverse=True))  # High Card

def compare_hands(hand1, hand2):
    # hand1 and hand2 are tuples: (rank, tiebreakers)
    if hand1[0] > hand2[0]:
        return 1
    elif hand1[0] < hand2[0]:
        return -1
    # If both are two pair, use special comparison
    if hand1[0] == 2:  # TWO_PAIR
        return compare_two_pair(hand1, hand2)
    # Fallback: compare tiebreakers in order
    for a, b in zip(hand1[1], hand2[1]):
        if a > b:
            return 1
        elif a < b:
            return -1
    return 0

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

def determine_winner_multiple(players, flop):
    print("Debug: Players data:", players)
    print("Debug: Flop data:", flop)

    best_score = -1
    best_player = None
    best_hand = None
    best_hand_type = None

    for index, player in enumerate(players):
        player_hand = player.get('cards', [])
        if not isinstance(player_hand, list):
            print("Error: Player hand is not a list:", player_hand)
            continue

        # Generate all combinations of 5 cards (2 from player + 3 from flop)
        combinations_list = [
            list(comb) for comb in combinations(player_hand + flop, 5)
            if sum(1 for card in comb if card in player_hand) == 2
        ]

        if not combinations_list:
            print(f"Error: No valid combinations generated for Player {index + 1}.")
            continue

        # Find the best combination for the current player
        best_combination = max(combinations_list, key=lambda hand: evaluate_hand(hand)[0])
        score, hand_type, _ = evaluate_hand(best_combination)

        # Update the best player if the current player's score is higher
        if score > best_score:
            best_score = score
            best_player = f"Player {index + 1}"
            best_hand = best_combination
            best_hand_type = hand_type

    if best_player is None:
        raise ValueError("No valid hands to evaluate.")

    return best_player, best_hand_type, best_hand

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    num_players = data.get('num_players', 2)  # Default to 2 players
    num_flops = data.get('num_flops', 2)  # Default to 2 flops

    # Shuffle the deck
    deck = DECK[:]
    random.shuffle(deck)

    # Deal 4 cards to each player
    players = [{'cards': [deck.pop() for _ in range(4)]} for _ in range(num_players)]

    # Create the flops with 3 exposed cards and 2 flipped cards
    first_flop = {
        'exposed': [deck.pop() for _ in range(3)],
        'flipped': [deck.pop() for _ in range(2)]
    }
    second_flop = {
        'exposed': [deck.pop() for _ in range(3)],
        'flipped': [deck.pop() for _ in range(2)]
    } if num_flops == 2 else None

    return jsonify({
        'players': players,
        'first_flop': first_flop,
        'second_flop': second_flop,
        'deck': deck
    })

@app.route('/reveal_card', methods=['POST'])
def reveal_card():
    try:
        data = request.get_json()
        app.logger.debug(f"Received payload in /reveal_card: {data}")  # Debugging

        if not data:
            return jsonify({'error': 'Invalid request payload. No data provided.'}), 400

        flop = data.get('flop')
        index = data.get('index')
        flops = data.get('flops')

        if not flop or not isinstance(index, int) or not flops:
            app.logger.error(f"Invalid payload structure: {data}")  # Debugging
            return jsonify({'error': 'Invalid request payload. Missing or invalid "flop", "index", or "flops" key.'}), 400

        # Enforce: 5th card cannot be revealed until both 4th cards are revealed
        # Only applies if both flops exist and have 2 flipped cards each
        if (
            flop in ["first_flop", "second_flop"]
            and len(flops.get("first_flop", {}).get("flipped", [])) + len(flops.get("second_flop", {}).get("flipped", [])) == 2
            and len(flops[flop]['flipped']) == 1
            and index == 1  # Trying to reveal the 5th card (index 1 in flipped)
        ):
            # Only allow if the other flop has no flipped cards left (i.e., its 4th card is already revealed)
            other_flop = "second_flop" if flop == "first_flop" else "first_flop"
            if len(flops.get(other_flop, {}).get("flipped", [])) > 1:
                return jsonify({'error': 'You must reveal the 4th card on both flops before revealing the 5th card.'}), 403

        if flop not in flops or index >= len(flops[flop]['flipped']):
            app.logger.error(f"Invalid flop or index: flop={flop}, index={index}, flops={flops}")  # Debugging
            return jsonify({'error': 'Invalid flop or index.'}), 400

        # Reveal the card
        revealed_card = flops[flop]['flipped'].pop(index)
        flops[flop]['exposed'].append(revealed_card)

        app.logger.debug(f"Updated flops after revealing card: {flops}")  # Debugging
        return jsonify({'flops': flops})  # Return the updated flops
    except Exception as e:
        app.logger.error(f"Error in reveal_card: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

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
    print("Data received in /reveal_winner:", data)  # Debugging: Log the received data

    players = data['players']
    first_flop = data['first_flop']
    second_flop = data.get('second_flop', [])
    prediction_first = data.get('prediction_first', None)
    prediction_second = data.get('prediction_second', None)

    # Debugging: Log the received predictions
    print("Prediction for First Flop:", prediction_first)
    print("Prediction for Second Flop:", prediction_second)

    # Process the data and determine the winners
    # (Assume determine_winner_multiple is a function that determines the winner)
    winner_first, hand_type_first, best_hand_first = determine_winner_multiple(players, first_flop)
    winner_second, hand_type_second, best_hand_second = None, None, None
    if second_flop:
        winner_second, hand_type_second, best_hand_second = determine_winner_multiple(players, second_flop)

    # Check if the predictions were correct
    prediction_correct_first = prediction_first == winner_first
    prediction_correct_second = prediction_second == winner_second if second_flop else None

    # Debugging: Log the results
    print("Winner First Flop:", winner_first, hand_type_first, best_hand_first)
    if second_flop:
        print("Winner Second Flop:", winner_second, hand_type_second, best_hand_second)

    return jsonify({
        "winner_first": winner_first,
        "hand_type_first": hand_type_first,
        "best_hand_first": best_hand_first,
        "prediction_correct_first": prediction_correct_first,
        "winner_second": winner_second,
        "hand_type_second": hand_type_second,
        "best_hand_second": best_hand_second,
        "prediction_correct_second": prediction_correct_second
    })

if __name__ == '__main__':
    app.run(debug=True)