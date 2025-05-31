from flask import Flask, render_template, request, jsonify, send_from_directory
import random
from itertools import combinations
import os
import json

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

    # Proper poker hand rankings (from lowest to highest):
    # 0: High Card
    # 1: One Pair
    # 2: Two Pair
    # 3: Three of a Kind
    # 4: Straight
    # 5: Flush
    # 6: Full House
    # 7: Four of a Kind
    # 8: Straight Flush
    # 9: Royal Flush

    def card_sort_key(card):
        return rank_order.index(card['rank'])

    # Check for straight
    rank_indices = sorted([rank_order.index(rank) for rank in ranks])
    is_straight = False
    straight_high = None
    
    # Check for regular straight
    if len(set(rank_indices)) == 5 and rank_indices[-1] - rank_indices[0] == 4:
        is_straight = True
        straight_high = rank_order[rank_indices[-1]]
    
    # Check for A-2-3-4-5 straight (ace low)
    elif set(rank_indices) == {0, 1, 2, 3, 12}:  # A, 2, 3, 4, 5
        is_straight = True
        straight_high = '5'  # In ace-low straight, 5 is the high card

    # Check for flush
    is_flush = len(unique_suits) == 1

    # Check for straight flush / royal flush
    if is_straight and is_flush:
        if straight_high == 'A' and set(ranks) == {'10', 'J', 'Q', 'K', 'A'}:
            return (9, "Royal Flush", sorted(cards, key=card_sort_key, reverse=True))
        else:
            return (8, f"Straight Flush, {straight_high} high", sorted(cards, key=card_sort_key, reverse=True))

    # Four of a Kind
    if 4 in rank_counts.values():
        return (7, "Four of a Kind", sorted(cards, key=lambda card: (rank_counts[card['rank']], card_sort_key(card)), reverse=True))

    # Full House
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        return (6, "Full House", sorted(cards, key=lambda card: (rank_counts[card['rank']], card_sort_key(card)), reverse=True))

    # Flush
    if is_flush:
        sorted_flush_cards = sorted(cards, key=card_sort_key, reverse=True)
        high_card = sorted_flush_cards[0]['rank']
        # Convert rank to readable format for flush high card
        high_card_readable = high_card
        if high_card == 'A':
            high_card_readable = 'Ace'
        elif high_card == 'K':
            high_card_readable = 'King'
        elif high_card == 'Q':
            high_card_readable = 'Queen'
        elif high_card == 'J':
            high_card_readable = 'Jack'
        return (5, f"{high_card_readable}-high Flush", sorted_flush_cards)

    # Straight
    if is_straight:
        return (4, f"Straight, {straight_high}", sorted(cards, key=card_sort_key, reverse=True))

    # Three of a Kind
    if 3 in rank_counts.values():
        return (3, "Three of a Kind", sorted(cards, key=lambda card: (rank_counts[card['rank']], card_sort_key(card)), reverse=True))

    # Two Pair
    if list(rank_counts.values()).count(2) == 2:
        pairs = sorted([rank for rank, count in rank_counts.items() if count == 2], key=rank_order.index, reverse=True)
        kicker = sorted([rank for rank, count in rank_counts.items() if count == 1], key=rank_order.index, reverse=True)[0]
        return (2, [pairs[0], pairs[1], kicker], sorted(cards, key=card_sort_key, reverse=True))

    # One Pair
    if 2 in rank_counts.values():
        pair_rank = max([rank for rank, count in rank_counts.items() if count == 2], key=lambda r: rank_order.index(r))
        kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], key=rank_order.index, reverse=True)[:3]
        sorted_cards = (
            [card for card in cards if card['rank'] == pair_rank] +
            sorted([card for card in cards if card['rank'] != pair_rank], key=card_sort_key, reverse=True)
        )
        return (1, [pair_rank] + kickers, sorted_cards)

    # High Card
    return (0, "High Card", sorted(cards, key=card_sort_key, reverse=True))

def compare_hands(hand1, hand2):
    # hand1 and hand2 are tuples: (rank, tiebreakers, sorted_cards)
    rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    def safe_index(val):
        if val in rank_order:
            return rank_order.index(val)
        return -1

    if hand1[0] > hand2[0]:
        return 1
    elif hand1[0] < hand2[0]:
        return -1
    # If both are two pair, compare pairs and kicker by rank_order
    if hand1[0] == 2:  # Two Pair
        # Compare each value in tiebreakers (pair1, pair2, kicker)
        for a, b in zip(hand1[1], hand2[1]):
            if safe_index(a) > safe_index(b):
                return 1
            elif safe_index(a) < safe_index(b):
                return -1
        # If all tiebreakers are equal, compare sorted_cards by suit for deterministic result
        for card1, card2 in zip(hand1[2], hand2[2]):
            if safe_index(card1['rank']) > safe_index(card2['rank']):
                return 1
            elif safe_index(card1['rank']) < safe_index(card2['rank']):
                return -1
            # If ranks are equal, compare suit unicode (for deterministic but arbitrary order)
            if card1['suit'] > card2['suit']:
                return 1
            elif card1['suit'] < card2['suit']:
                return -1
        return 0
    # For One Pair, High Card, etc, compare tiebreakers by rank_order
    for a, b in zip(hand1[1], hand2[1]):
        if safe_index(a) > safe_index(b):
            return 1
        elif safe_index(a) < safe_index(b):
            return -1
    # If still tied, compare sorted_cards by rank then suit
    for card1, card2 in zip(hand1[2], hand2[2]):
        if safe_index(card1['rank']) > safe_index(card2['rank']):
            return 1
        elif safe_index(card1['rank']) < safe_index(card2['rank']):
            return -1
        if card1['suit'] > card2['suit']:
            return 1
        elif card1['suit'] < card2['suit']:
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
    player1_best = max(player1_combinations, key=lambda hand: evaluate_hand(hand)[0:2])
    player2_best = max(player2_combinations, key=lambda hand: evaluate_hand(hand)[0:2])

    player1_eval = evaluate_hand(player1_best)
    player2_eval = evaluate_hand(player2_best)

    print("Player 1 Evaluated Hand:", player1_eval[2], "Type:", player1_eval[1], "Score:", player1_eval[0])
    print("Player 2 Evaluated Hand:", player2_eval[2], "Type:", player2_eval[1], "Score:", player2_eval[0])

    cmp = compare_hands(player1_eval, player2_eval)
    if cmp > 0:
        return "Player 1", player1_eval[1], player1_eval[2]
    elif cmp < 0:
        return "Player 2", player2_eval[1], player2_eval[2]
    else:
        return "Tie", player1_eval[1], player1_eval[2]

def determine_winner_multiple(players, flop):
    print("Debug: Players data:", players)
    print("Debug: Flop data:", flop)

    best_score = -1
    winners = []  # Changed to list to support multiple winners
    best_hand_type = None
    player_evaluations = []  # Store all evaluations for tie detection

    for index, player in enumerate(players):
        player_hand = player.get('cards', [])
        if not isinstance(player_hand, list):
            print("Error: Player hand is not a list:", player_hand)
            continue

        # For bombpot poker, players must use exactly 2 cards from their 4-card hand
        # Generate all combinations of 2 cards from the player's 4 cards
        player_card_combinations = list(combinations(player_hand, 2))
        
        best_score_for_player = -1
        best_combination_for_player = None
        best_eval_for_player = None
        
        # Try each combination of 2 cards from player's hand
        for player_two_cards in player_card_combinations:
            # Generate all combinations of 5 cards (2 from player + 3 from flop)
            flop_combinations = list(combinations(flop, 3))
            
            for flop_three_cards in flop_combinations:
                # Combine 2 player cards + 3 flop cards
                five_card_hand = list(player_two_cards) + list(flop_three_cards)
                score, hand_type, sorted_cards = evaluate_hand(five_card_hand)
                
                if score > best_score_for_player:
                    best_score_for_player = score
                    best_combination_for_player = five_card_hand
                    best_eval_for_player = (score, hand_type, sorted_cards)
                elif score == best_score_for_player:
                    # If scores are equal, use compare_hands to determine the better hand
                    current_eval = (score, hand_type, sorted_cards)
                    if compare_hands(current_eval, best_eval_for_player) > 0:
                        best_combination_for_player = five_card_hand
                        best_eval_for_player = current_eval

        if best_combination_for_player and best_eval_for_player:
            player_evaluations.append({
                'player': f"Player {index + 1}",
                'score': best_score_for_player,
                'hand_type': best_eval_for_player[1],
                'hand': best_combination_for_player,
                'evaluation': best_eval_for_player
            })

    if not player_evaluations:
        raise ValueError("No valid hands to evaluate.")

    # Sort players using compare_hands for proper comparison
    from functools import cmp_to_key
    
    def compare_player_evaluations(p1, p2):
        # Use compare_hands to compare the evaluation tuples
        return -compare_hands(p1['evaluation'], p2['evaluation'])  # Negative for descending order
    
    player_evaluations.sort(key=cmp_to_key(compare_player_evaluations))
    
    # Find all players with the best hand
    best_eval = player_evaluations[0]['evaluation']
    winners = []
    
    for player_eval in player_evaluations:
        # Compare hands using the compare_hands function
        if compare_hands(player_eval['evaluation'], best_eval) == 0:
            winners.append(player_eval['player'])
        else:
            break  # Since sorted, no need to check further
    
    # Return winners list and hand info
    if len(winners) == 1:
        return winners[0], player_evaluations[0]['hand_type'], player_evaluations[0]['hand']
    else:
        # Multiple winners (tie)
        return winners, player_evaluations[0]['hand_type'], player_evaluations[0]['hand']

LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")

def load_leaderboard():
    # Always try to load from disk, never cache in memory
    if not os.path.exists(LEADERBOARD_FILE):
        # If file does not exist, create an empty file
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # If file is corrupted, reset to empty list
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_leaderboard(leaderboard):
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(leaderboard, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving leaderboard:", e)

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    leaderboard = load_leaderboard()
    # Only show entries with at least 20 flops
    leaderboard = [entry for entry in leaderboard if entry.get("total", 0) >= 20]
    # Sort by accuracy (correct/total), then by total (descending)
    leaderboard = sorted(
        leaderboard,
        key=lambda x: ((x.get("correct", 0) / x.get("total", 1)) if x.get("total", 0) > 0 else 0, x.get("total", 0)),
        reverse=True
    )
    # Only show top 10
    leaderboard = leaderboard[:10]
    return jsonify({"leaderboard": leaderboard})

@app.route('/update_leaderboard', methods=['POST'])
def update_leaderboard():
    data = request.get_json()
    name = data.get("name", "").strip()
    correct = int(data.get("correct", 0))
    total = int(data.get("total", 0))
    difficulty = data.get("difficulty", "easy")

    if not name or total < 20:
        return jsonify({"error": "Invalid name or not enough flops"}), 400

    leaderboard = load_leaderboard()
    # Always allow multiple entries for the same name (append new entry)
    leaderboard.append({
        "name": name,
        "correct": correct,
        "total": total,
        "difficulty": difficulty
    })
    save_leaderboard(leaderboard)
    return jsonify({"success": True})

@app.route('/favicon.ico')
def favicon():
    # Return a 204 No Content response for favicon requests
    # This prevents 404 errors in the browser console
    return '', 204

@app.route('/game-options')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    num_players = data.get('num_players', 4)  # Changed default from 2 to 4
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
        # --- NEW: Require predictions to be present and non-empty before allowing reveal ---
        prediction_first = data.get('prediction_first')
        prediction_second = data.get('prediction_second')

        # Only allow reveal if both predictions are made (non-empty)
        if not prediction_first or not prediction_second:
            return jsonify({'error': 'Both player predictions must be made before revealing cards.'}), 403

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
    try:
        data = request.get_json()
        print("Data received in /reveal_winner:", data)  # Debugging: Log the received data

        # Validate required fields
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        players = data.get('players')
        first_flop = data.get('first_flop')
        second_flop = data.get('second_flop')
        prediction_first = data.get('prediction_first')
        prediction_second = data.get('prediction_second')
        
        # Validate all required fields are present
        if not players or not isinstance(players, list):
            return jsonify({'error': 'Invalid or missing players data'}), 400
        if first_flop is None or not isinstance(first_flop, list):
            return jsonify({'error': 'Invalid or missing first_flop data'}), 400
        if second_flop is None or not isinstance(second_flop, list):
            return jsonify({'error': 'Invalid or missing second_flop data'}), 400
            
        # Allow 3, 4, or 5 cards for partial winner checking
        if len(first_flop) < 3 or len(first_flop) > 5:
            return jsonify({'error': f'First flop must have 3-5 cards, got {len(first_flop)}'}), 400
        if len(second_flop) < 3 or len(second_flop) > 5:
            return jsonify({'error': f'Second flop must have 3-5 cards, got {len(second_flop)}'}), 400

        # Debugging: Log the received predictions
        print("Prediction for First Flop:", prediction_first)
        print("Prediction for Second Flop:", prediction_second)

        # Process the data and determine the winners
        # Handle cases where we might have less than 5 cards (for intermediate updates)
        winner_first = None
        hand_type_first = None
        best_hand_first = None
        
        winner_second = None
        hand_type_second = None
        best_hand_second = None
        
        # Only calculate winners if we have at least 3 cards
        if len(first_flop) >= 3:
            # Pad with dummy cards if less than 5 for evaluation
            eval_first_flop = first_flop[:]
            while len(eval_first_flop) < 5:
                # Add dummy cards that won't affect hand evaluation
                eval_first_flop.append({'rank': '2', 'suit': '♣'})
            
            winner_first, hand_type_first, best_hand_first = determine_winner_multiple(players, eval_first_flop)
        
        if len(second_flop) >= 3:
            # Pad with dummy cards if less than 5 for evaluation
            eval_second_flop = second_flop[:]
            while len(eval_second_flop) < 5:
                # Add dummy cards that won't affect hand evaluation
                eval_second_flop.append({'rank': '2', 'suit': '♦'})
            
            winner_second, hand_type_second, best_hand_second = determine_winner_multiple(players, eval_second_flop)

        # Check if the predictions were correct
        # For ties, check if prediction is in the winners list
        prediction_correct_first = False
        prediction_correct_second = False
        
        if winner_first:
            if isinstance(winner_first, list):
                prediction_correct_first = prediction_first in winner_first
            else:
                prediction_correct_first = prediction_first == winner_first
        
        if winner_second:
            if isinstance(winner_second, list):
                prediction_correct_second = prediction_second in winner_second
            else:
                prediction_correct_second = prediction_second == winner_second

        # Debugging: Log the results
        print("Winner First Flop:", winner_first, hand_type_first)
        print("Winner Second Flop:", winner_second, hand_type_second)

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
        
    except Exception as e:
        print(f"Error in /reveal_winner: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)