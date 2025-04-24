class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}"


class PlayerHand:
    def __init__(self, player_name):
        self.player_name = player_name
        self.cards = []

    def add_card(self, card):
        # Remove the restriction on the number of cards
        self.cards.append(card)

    def show_hand(self):
        return f"{self.player_name}'s hand: {', '.join(map(str, self.cards))}"


# Example usage:
# card1 = Card("Hearts", "Ace")
# card2 = Card("Spades", "King")
# player_hand = PlayerHand("Player 1")
# player_hand.add_card(card1)
# player_hand.add_card(card2)
# print(player_hand.show_hand())