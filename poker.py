def hand_rank(hand):
    # hand: list of tuples (rank, suit), e.g. [('A', '♠'), ('K', '♣'), ...]
    values = '23456789TJQKA'
    value_map = {r: i for i, r in enumerate(values, start=2)}
    ranks = sorted([value_map[r] for r, s in hand], reverse=True)
    counts = {r: ranks.count(r) for r in set(ranks)}
    pairs = [r for r, c in counts.items() if c == 2]
    trips = [r for r, c in counts.items() if c == 3]
    quads = [r for r, c in counts.items() if c == 4]
    # Straight detection (including Ace-low)
    straight = False
    straight_high = None
    unique_ranks = sorted(set(ranks), reverse=True)
    for i in range(len(unique_ranks) - 4):
        window = unique_ranks[i:i+5]
        if window[0] - window[4] == 4:
            straight = True
            straight_high = window[0]
            break
    # Ace-low straight
    if set([14, 2, 3, 4, 5]).issubset(set(ranks)):
        straight = True
        straight_high = 5
    # ...existing flush, full house, etc logic...
    # Two pair tiebreaker: sort pairs, then kicker
    if len(pairs) == 2:
        high_pair, low_pair = sorted(pairs, reverse=True)
        kicker = max([r for r in ranks if r != high_pair and r != low_pair])
        return (2, high_pair, low_pair, kicker)
    # Trips (Three of a kind)
    if len(trips) == 1:
        trip = trips[0]
        kickers = [r for r in ranks if r != trip][:2]
        # If there are less than 2 kickers, pad with 0s (shouldn't happen in 5+ card hands)
        while len(kickers) < 2:
            kickers.append(0)
        return (3, trip, *kickers)
    # Straight
    if straight:
        return (4, straight_high)
    # High card
    if len(pairs) == 0 and len(trips) == 0 and len(quads) == 0 and not straight:
        top5 = ranks[:5]
        return (0, *top5)
    # ...existing code for other hands...

# ...existing code...