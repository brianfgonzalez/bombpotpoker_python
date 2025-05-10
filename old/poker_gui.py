import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # For handling the background image
from player_hand import PlayerHand, Card


class PokerGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bombpot Poker")
        self.root.geometry("1920x1080")  # Set the game to full screen
        self.deck = self.create_deck()
        self.player1_name, self.player2_name = self.generate_player_names()
        self.player1_hand = PlayerHand(self.player1_name)
        self.player2_hand = PlayerHand(self.player2_name)
        self.first_flop = []
        self.second_flop = []
        self.turn_revealed = False
        self.river_revealed = False
        self.start_button = None
        self.instructions_button = None
        self.restart_button = None
        self.init_ui()

    def create_deck(self):
        suits = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        return [Card(suits[suit], rank) for suit in suits for rank in ranks]

    def generate_player_names(self):
        """Generates random player names from a list of popular USA names in 2025."""
        names = ["Liam", "Olivia", "Noah", "Emma", "Oliver", "Ava", "Elijah", "Sophia", "James", "Isabella"]
        return random.sample(names, 2)

    def init_ui(self):
        # Create a container frame to hold both "In Play" and "Results"
        self.container_frame = tk.Frame(self.root, bg="#228B22")
        self.container_frame.pack(fill="both", expand=True)

        # Main layout: Split into left (In Play) and right (Results)
        self.left_frame = tk.LabelFrame(
            self.container_frame,
            text="In Play",
            font=("Arial", 16),
            bg="#228B22",
            fg="white",
            padx=10,
            pady=10
        )
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.right_frame = tk.LabelFrame(
            self.container_frame,
            text="Results",
            font=("Arial", 16),
            bg="#228B22",
            fg="white",
            padx=10,
            pady=10
        )
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Title Label
        tk.Label(self.left_frame, text="Bombpot Poker", font=("Arial", 36), bg="#228B22", fg="white").pack(pady=10)

        # Buttons
        self.start_button = tk.Button(self.left_frame, text="Start Game", command=self.start_game, font=("Arial", 18))
        self.start_button.pack(pady=5)

        self.instructions_button = tk.Button(self.left_frame, text="Instructions", command=self.show_instructions, font=("Arial", 18))
        self.instructions_button.pack(pady=5)

    def load_background_image(self):
        """Loads and sets the background image for the card table."""
        try:
            image = Image.open("card_table.jpg")  # Replace with the path to your card table image
            image = image.resize((800, 600), Image.ANTIALIAS)  # Resize the image to fit the window
            self.background_image = ImageTk.PhotoImage(image)

            # Create a canvas to display the background image
            canvas = tk.Canvas(self.root, width=800, height=600)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(0, 0, image=self.background_image, anchor="nw")
        except FileNotFoundError:
            print("Background image 'card_table.jpg' not found. Using default background.")

    def start_game(self):
        # Hide the Start and Instructions buttons
        if self.start_button:
            self.start_button.pack_forget()
        if self.instructions_button:
            self.instructions_button.pack_forget()

        # Clear the Results section and add a placeholder
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        tk.Label(self.right_frame, text="Results will be displayed here after the game ends.",
                 font=("Arial", 18), bg="#228B22", fg="white").pack(pady=10)

        # Reset the game
        self.deck = self.create_deck()
        random.shuffle(self.deck)
        self.player1_hand = PlayerHand(self.player1_name)
        self.player2_hand = PlayerHand(self.player2_name)
        self.first_flop = []
        self.second_flop = []
        self.turn_revealed = False
        self.river_revealed = False

        # Deal cards to players
        for _ in range(4):
            self.player1_hand.add_card(self.deck.pop(0))
            self.player2_hand.add_card(self.deck.pop(0))

        # Deal the first and second flops
        self.first_flop = [self.deck.pop(0) for _ in range(3)]
        self.second_flop = [self.deck.pop(0) for _ in range(3)]

        # Display the game state
        self.display_game_state()

    def display_game_state(self):
        # Clear the left frame
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        # Player 1's Hand
        tk.Label(self.left_frame, text=f"{self.player1_name}'s Hand:", font=("Arial", 12), bg="#228B22", fg="white").pack(pady=5)
        self.display_cards(self.player1_hand.cards, sort=True, frame=self.left_frame)

        # Player 2's Hand
        tk.Label(self.left_frame, text=f"{self.player2_name}'s Hand:", font=("Arial", 12), bg="#228B22", fg="white").pack(pady=5)
        self.display_cards(self.player2_hand.cards, sort=True, frame=self.left_frame)

        # First Flop
        tk.Label(self.left_frame, text="First Flop:", font=("Arial", 12), bg="#228B22", fg="white").pack(pady=5)
        self.display_cards(self.first_flop, sort=False, frame=self.left_frame)

        # Second Flop
        tk.Label(self.left_frame, text="Second Flop:", font=("Arial", 12), bg="#228B22", fg="white").pack(pady=5)
        self.display_cards(self.second_flop, sort=False, frame=self.left_frame)

        # Buttons for Turn and River
        if not self.turn_revealed:
            tk.Button(self.left_frame, text="Reveal Turn", command=self.reveal_turn, font=("Arial", 12)).pack(pady=5)
        elif not self.river_revealed:
            tk.Button(self.left_frame, text="Reveal River", command=self.reveal_river, font=("Arial", 12)).pack(pady=5)

    def display_cards(self, cards, sort=False, frame=None):
        """Displays cards side by side with slanted corners and a white background."""
        if sort:
            cards.sort(key=lambda card: (card.suit, card_value(card)))  # Sort by suit and rank if required

        canvas = tk.Canvas(frame, height=150, width=1800, bg="#228B22", highlightthickness=0)
        canvas.pack()

        x_start = 10
        for card in cards:
            # Define the points for the slimmer slanted rectangle
            points = [
                x_start, 10,               # Top-left
                x_start + 50, 10,          # Top-right (slanted)
                x_start + 60, 20,          # Top-right slant
                x_start + 60, 90,          # Bottom-right
                x_start + 10, 90,          # Bottom-left (slanted)
                x_start, 80                # Bottom-left slant
            ]

            # Draw the slanted rectangle (polygon)
            canvas.create_polygon(points, outline="black", fill="white", width=2)

            # Draw the card text in the center with larger font
            canvas.create_text(x_start + 30, 50, text=self.format_card(card), font=("Arial", 20, "bold"), fill=self.get_card_color(card))

            x_start += 70  # Move to the next card position

    def format_card(self, card):
        """Formats the card as a string with face card letters."""
        return f"{card.rank[0]}{card.suit}"  # Use the first letter of the rank (e.g., J, Q, K, A)

    def get_card_color(self, card):
        """Returns the color for the card based on its suit."""
        if card.suit == '♥':
            return "red"
        elif card.suit == '♦':
            return "orange"
        elif card.suit == '♣':
            return "green"
        elif card.suit == '♠':
            return "black"

    def reveal_turn(self):
        # Add a 4th card to each flop
        self.first_flop.append(self.deck.pop(0))
        self.second_flop.append(self.deck.pop(0))
        self.turn_revealed = True  # Mark the Turn as revealed
        self.display_game_state()

    def reveal_river(self):
        print("Revealing the river...")
        self.first_flop.append(self.deck.pop(0))
        self.second_flop.append(self.deck.pop(0))
        self.river_revealed = True
        self.display_game_state()
        print("River revealed. Determining winners...")
        self.determine_winners()

    def determine_winners(self):
        print("Determining winners...")

        # Determine the best hands and winners
        player1_best_first = get_best_five_cards(self.player1_hand.cards, self.first_flop)
        player2_best_first = get_best_five_cards(self.player2_hand.cards, self.first_flop)
        player1_best_second = get_best_five_cards(self.player1_hand.cards, self.second_flop)
        player2_best_second = get_best_five_cards(self.player2_hand.cards, self.second_flop)

        winner_first_flop, hand_type_first = determine_winner(player1_best_first, player2_best_first)
        winner_second_flop, hand_type_second = determine_winner(player1_best_second, player2_best_second)

        # Clear the Results section
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Display the results
        tk.Label(self.right_frame, text="Results:", font=("Arial", 24, "bold"), bg="#228B22", fg="white").pack(pady=10)

        # Display the winning hands
        tk.Label(self.right_frame, text=f"Winner for First Flop: {winner_first_flop} with a {hand_type_first}", font=("Arial", 18), bg="#228B22", fg="white").pack(pady=5)
        self.display_cards(player1_best_first if winner_first_flop == self.player1_name else player2_best_first, sort=False, frame=self.right_frame)

        tk.Label(self.right_frame, text=f"Winner for Second Flop: {winner_second_flop} with a {hand_type_second}", font=("Arial", 18), bg="#228B22", fg="white").pack(pady=5)
        self.display_cards(player1_best_second if winner_second_flop == self.player1_name else player2_best_second, sort=False, frame=self.right_frame)

        # Add a Restart Game button
        self.add_restart_button()
        print("Winners determined and results displayed.")

    def add_restart_button(self):
        """Adds a Restart Game button."""
        tk.Button(self.right_frame, text="Restart Game", command=self.start_game, font=("Arial", 18)).pack(pady=10)

    def show_instructions(self):
        messagebox.showinfo("Instructions", "1. This is a graphical poker game.\n"
                                            "2. Click 'Start Game' to begin.\n"
                                            "3. Reveal the Turn and River cards.\n"
                                            "4. Winners will be determined automatically.")


# Helper functions (reuse from your existing code)
def get_best_five_cards(player_hand, community_cards):
    """
    Determines the best five-card poker hand from a player's hand and community cards.
    Enforces the rule that at least 2 cards must come from the player's hand.
    """
    from itertools import combinations

    all_combinations = []

    # Generate all combinations where at least 2 cards come from the player's hand
    for hand_cards in combinations(player_hand, 2):
        for community_cards_subset in combinations(community_cards, 3):
            all_combinations.append(list(hand_cards) + list(community_cards_subset))

    # Evaluate all valid 5-card combinations and return the best one
    if not all_combinations:
        raise ValueError("No valid combinations found in get_best_five_cards.")
    best_hand = max(all_combinations, key=lambda cards: hand_rank(cards))
    return best_hand

def determine_winner(hand1, hand2):
    """
    Compares two hands and determines the winner.
    Returns the winner and the type of winning hand.
    """
    rank1, _, hand_type1 = hand_rank(hand1)
    rank2, _, hand_type2 = hand_rank(hand2)

    if rank1 > rank2:
        return "Player 1", hand_type1
    elif rank2 > rank1:
        return "Player 2", hand_type2
    else:
        return "Tie", hand_type1  # In case of a tie, return one of the hand types

def hand_rank(cards):
    """Assigns a rank and name to a hand based on poker rules."""
    if not all(cards):  # Check for None in the cards list
        raise ValueError("Invalid card detected in hand_rank function.")

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

def card_value(card):
    """Assigns a numeric value to each card rank."""
    rank_order = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                  '10': 10, 'Jack': 11, 'Queen': 12, 'King': 13, 'Ace': 14}
    return rank_order.get(card.rank, 0)  # Default to 0 if rank is invalid

def is_flush(cards):
    """Checks if all cards are of the same suit."""
    suits = [card.suit for card in cards]
    return len(set(suits)) == 1

def is_straight(cards):
    """Checks if the cards form a straight."""
    values = sorted([card_value(card) for card in cards])
    return all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1))

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = PokerGameGUI(root)
    root.mainloop()