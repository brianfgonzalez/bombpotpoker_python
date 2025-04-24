import random
from player_hand import PlayerHand
from player_hand import Card  # Import the Card class
from itertools import combinations

def main():
    print("Welcome to Bombpot Poker!")
    print("This is a text-based poker game.")
    print("Get ready to play!")

    # Placeholder for game logic
    while True:
        print("\n1. Start Game")
        print("2. Instructions")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            start_game()
        elif choice == "2":
            show_instructions()
        elif choice == "3":
            print("Thanks for playing Bombpot Poker!")
            break
        else:
            print("Invalid choice. Please try again.")

def start_game():
    print("\nStarting the game...")
    # Create a deck of Card objects
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    deck = [Card(suit, rank) for suit in suits for rank in ranks]

    # Shuffle the deck
    random.shuffle(deck)

    # Deal cards to players (example for 2 players)
    player1_hand = PlayerHand("Player 1")
    player2_hand = PlayerHand("Player 2")

    # Add 4 cards to each player's hand
    for _ in range(4):
        player1_hand.add_card(deck.pop(0))
        player2_hand.add_card(deck.pop(0))

    # First flop (three community cards)
    first_flop = [deck.pop(0), deck.pop(0), deck.pop(0)]
    second_flop = [deck.pop(0), deck.pop(0), deck.pop(0)]

    # Show each player's hand
    print(player1_hand.show_hand())
    print(player2_hand.show_hand())

    # Show the first flop
    print("First Flop (Community Cards):", ", ".join(map(str, first_flop)))

    # Show the second flop
    print("Second Flop (Community Cards):", ", ".join(map(str, second_flop)))

    # Prompt for Turn (4th card)
    input("\nPress Enter to reveal the Turn card...")
    first_flop.append(deck.pop(0))
    second_flop.append(deck.pop(0))
    print("First Flop after Turn (4th card):", ", ".join(map(str, first_flop)))
    print("Second Flop after Turn (4th card):", ", ".join(map(str, second_flop)))

    # Prompt for River (5th card)
    input("\nPress Enter to reveal the River card...")
    first_flop.append(deck.pop(0))
    second_flop.append(deck.pop(0))
    print("First Flop after River (5th card):", ", ".join(map(str, first_flop)))
    print("Second Flop after River (5th card):", ", ".join(map(str, second_flop)))

    # Combine player hands with the final flops and determine the best five cards
    player1_best_first = get_best_five_cards(player1_hand.cards, first_flop)
    player2_best_first = get_best_five_cards(player2_hand.cards, first_flop)
    player1_best_second = get_best_five_cards(player1_hand.cards, second_flop)
    player2_best_second = get_best_five_cards(player2_hand.cards, second_flop)

    # Determine the winner for each flop
    winner_first_flop = determine_winner(player1_best_first, player2_best_first)
    winner_second_flop = determine_winner(player1_best_second, player2_best_second)

    # Print the best five cards for each player for each flop
    print("\nFinal Results:")
    print(f"Player 1's best five cards (First Flop): {', '.join(map(str, player1_best_first))}")
    print(f"Player 2's best five cards (First Flop): {', '.join(map(str, player2_best_first))}")
    print(f"Player 1's best five cards (Second Flop): {', '.join(map(str, player1_best_second))}")
    print(f"Player 2's best five cards (Second Flop): {', '.join(map(str, player2_best_second))}")

    # Output the winners
    print(f"\nWinner for First Flop: {winner_first_flop}")
    print(f"Winner for Second Flop: {winner_second_flop}")

def card_value(card):
    """Assigns a numeric value to each card rank."""
    rank_order = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                  '10': 10, 'Jack': 11, 'Queen': 12, 'King': 13, 'Ace': 14}
    return rank_order[card.rank]

def is_flush(cards):
    """Checks if all cards are of the same suit."""
    suits = [card.suit for card in cards]
    return len(set(suits)) == 1

def is_straight(cards):
    """Checks if the cards form a straight."""
    values = sorted([card_value(card) for card in cards])
    return all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1))

def get_best_five_cards(player_hand, community_cards):
    """
    Determines the best five-card poker hand from a player's hand and community cards.
    Enforces the rule that at least 2 cards must come from the player's hand.
    """
    all_combinations = []

    # Generate all combinations where at least 2 cards come from the player's hand
    for hand_cards in combinations(player_hand, 2):
        for community_cards_subset in combinations(community_cards, 3):
            all_combinations.append(hand_cards + community_cards_subset)

    # Evaluate all valid 5-card combinations and return the best one
    best_hand = max(all_combinations, key=lambda cards: hand_rank(cards))
    return best_hand

def determine_winner(hand1, hand2):
    """
    Compares two hands and determines the winner.
    Returns "Player 1", "Player 2", or "Tie".
    """
    rank1 = hand_rank(hand1)
    rank2 = hand_rank(hand2)

    if rank1 > rank2:
        return "Player 1"
    elif rank2 > rank1:
        return "Player 2"
    else:
        return "Tie"

def hand_rank(cards):
    """Assigns a rank and name to a hand based on poker rules."""
    values = sorted([card_value(card) for card in cards], reverse=True)
    flush = is_flush(cards)
    straight = is_straight(cards)

    if flush and straight:
        return (8, values, "Straight Flush")
    if len(set(values)) == 2:  # Four of a kind or Full house
        if values.count(values[0]) in [4, 1]:
            return (7, values, "Four of a Kind")
        else:
            return (6, values, "Full House")
    if flush:
        return (5, values, "Flush")
    if straight:
        return (4, values, "Straight")
    if len(set(values)) == 3:  # Three of a kind or Two pairs
        if values.count(values[0]) == 3 or values.count(values[2]) == 3:
            return (3, values, "Three of a Kind")
        else:
            return (2, values, "Two Pairs")
    if len(set(values)) == 4:
        return (1, values, "One Pair")
    return (0, values, "High Card")

def show_instructions():
    print("\nInstructions:")
    print("1. This is a text-based poker game.")
    print("2. Follow the prompts to play.")
    print("3. Have fun!")

if __name__ == "__main__":
    main()