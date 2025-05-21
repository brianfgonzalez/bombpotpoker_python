# Minimal test script for poker hand evaluation logic using your app's determine_winner.
# Place this file in your backend directory and run with: python test_poker_hands.py

from app import determine_winner  # Adjust import if needed

def test_determine_winner():
    # Each test: (players, board, expected_winner, description)
    tests = [
        # Straight (A-2-3-4-5)
        (
            [
                {'cards': [{'rank': 'A', 'suit': '♠'}, {'rank': '2', 'suit': '♣'}]},
                {'cards': [{'rank': '3', 'suit': '♦'}, {'rank': '4', 'suit': '♠'}]},
            ],
            # Board
            [{'rank': '5', 'suit': '♥'}, {'rank': '9', 'suit': '♣'}, {'rank': 'K', 'suit': '♠'}, {'rank': '7', 'suit': '♣'}, {'rank': '8', 'suit': '♣'}],
            0,  # Player 1 wins with A-2-3-4-5 straight
            "Ace-low straight"
        ),
        # Two pair (Aces and Kings, Q kicker)
        (
            [
                {'cards': [{'rank': 'A', 'suit': '♠'}, {'rank': 'K', 'suit': '♣'}]},
                {'cards': [{'rank': 'A', 'suit': '♦'}, {'rank': 'K', 'suit': '♠'}]},
            ],
            [{'rank': 'Q', 'suit': '♥'}, {'rank': '2', 'suit': '♣'}, {'rank': '3', 'suit': '♠'}, {'rank': 'A', 'suit': '♥'}, {'rank': 'K', 'suit': '♦'}],
            1,  # Player 2 wins (better kicker)
            "Two pair, Aces & Kings, Q kicker"
        ),
        # Trips
        (
            [
                {'cards': [{'rank': 'Q', 'suit': '♠'}, {'rank': '5', 'suit': '♠'}]},
                {'cards': [{'rank': 'Q', 'suit': '♣'}, {'rank': 'Q', 'suit': '♦'}]},
            ],
            [{'rank': '2', 'suit': '♥'}, {'rank': '3', 'suit': '♣'}, {'rank': '4', 'suit': '♠'}, {'rank': '6', 'suit': '♣'}, {'rank': '7', 'suit': '♣'}],
            1,  # Player 2 wins with three Queens
            "Three of a kind, Queens"
        ),
        # High card
        (
            [
                {'cards': [{'rank': 'A', 'suit': '♠'}, {'rank': 'K', 'suit': '♣'}]},
                {'cards': [{'rank': 'Q', 'suit': '♦'}, {'rank': 'J', 'suit': '♠'}]},
            ],
            [{'rank': '9', 'suit': '♥'}, {'rank': '2', 'suit': '♣'}, {'rank': '3', 'suit': '♠'}, {'rank': '4', 'suit': '♣'}, {'rank': '5', 'suit': '♣'}],
            0,  # Player 1 wins with Ace high
            "High card Ace"
        ),
        # High card kicker test
        (
            [
                {'cards': [{'rank': 'A', 'suit': '♠'}, {'rank': '7', 'suit': '♣'}]},
                {'cards': [{'rank': 'A', 'suit': '♦'}, {'rank': '6', 'suit': '♠'}]},
            ],
            # Board: both have top pair (Aces), but Player 1 has higher kicker (7 vs 6)
            [{'rank': 'A', 'suit': '♥'}, {'rank': '2', 'suit': '♣'}, {'rank': '3', 'suit': '♠'}, {'rank': '4', 'suit': '♣'}, {'rank': '5', 'suit': '♣'}],
            0,  # Player 1 should win with higher kicker
            "Pair of Aces, Player 1 wins with 7 kicker"
        ),
    ]
    for players, board, expected_idx, desc in tests:
        # Defensive: ensure each player has exactly 2 cards
        valid_players = [p for p in players if 'cards' in p and len(p['cards']) == 2]
        if len(valid_players) != len(players):
            print(f"Failed: {desc}. Invalid player structure: {players}")
            continue

        # Defensive: ensure board is 5 cards
        if len(board) != 5:
            print(f"Failed: {desc}. Board must have 5 cards: {board}")
            continue

        # Deep copy to avoid mutation
        import copy
        test_players = copy.deepcopy(players)
        test_board = copy.deepcopy(board)

        # Ensure all cards are dicts with 'rank' and 'suit'
        malformed = False
        for p in test_players:
            if not isinstance(p, dict) or 'cards' not in p or not isinstance(p['cards'], list) or len(p['cards']) != 2:
                print(f"Failed: {desc}. Malformed player: {p}")
                malformed = True
            for c in p['cards']:
                if not isinstance(c, dict) or 'rank' not in c or 'suit' not in c:
                    print(f"Failed: {desc}. Malformed card in player: {p}")
                    malformed = True
        for c in test_board:
            if not isinstance(c, dict) or 'rank' not in c or 'suit' not in c:
                print(f"Failed: {desc}. Malformed card on board: {c}")
                malformed = True
        if malformed:
            continue

        # --- CRITICAL: Print exactly what is being passed to determine_winner ---
        # This will help you debug what your backend expects.
        print(f"\nDEBUG: Calling determine_winner with:")
        print(f"Players: {test_players}")
        print(f"Board: {test_board}")

        try:
            # Pass player hands and board as required by app.py's determine_winner(hand1, hand2, flop)
            winner_idx = determine_winner(
                test_players[0]['cards'],
                test_players[1]['cards'],
                test_board
            )
        except Exception as e:
            print(f"Failed: {desc}. Exception: {e}")
            continue

        # If determine_winner returns ("Player 1", ...), ("Player 2", ...), or ("Tie", ...)
        # Convert to index for comparison with expected_idx
        if isinstance(winner_idx, tuple) and isinstance(winner_idx[0], str):
            if winner_idx[0] == "Player 1":
                idx = 0
            elif winner_idx[0] == "Player 2":
                idx = 1
            else:
                idx = -1  # Tie or unknown
        else:
            idx = winner_idx

        if idx != expected_idx:
            print(f"Failed: {desc}. Got winner index {idx}, expected {expected_idx}")
            print(f"Players: {test_players}")
            print(f"Board: {test_board}")
        else:
            print(f"Passed: {desc}")

if __name__ == "__main__":
    test_determine_winner()
    print("All tests completed.")
