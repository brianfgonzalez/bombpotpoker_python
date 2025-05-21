def hand_rank(hand):
    """
    Returns a tuple (rank, tiebreakers...) for a 5-card hand.
    Higher tuple means better hand.
    """
    # Example hand types:
    # 8: Straight Flush, 7: Four of a Kind, 6: Full House, 5: Flush, 4: Straight, 3: Three of a Kind, 2: Two Pair, 1: One Pair, 0: High Card

    # --- Fix: Ensure straight is ranked higher than one pair ---
    # Make sure the returned rank for straight is 4, one pair is 1, etc.
    # If your logic is using numbers, check that straight > three of a kind > two pair > one pair > high card

    # Example (simplified):
    if is_straight and is_flush:
        return (8, high_card)  # Straight flush
    elif four_kind:
        return (7, four_kind_rank, kicker)
    elif full_house:
        return (6, three_kind_rank, pair_rank)
    elif is_flush:
        return (5, flush_high_cards)
    elif is_straight:
        return (4, high_card)
    elif three_kind:
        return (3, three_kind_rank, kickers)
    elif two_pair:
        return (2, high_pair, low_pair, kicker)
    elif one_pair:
        return (1, pair_rank, kickers)
    else:
        return (0, high_cards)