# src/evaluator.py

from typing import List, Tuple

RANKS = "23456789TJQKA"
rank_value = {r: i for i, r in enumerate(RANKS, start=2)}

SUITS = "DHCS"
suit_value = {s: i for i, s in enumerate(SUITS)}

def evaluate_hand(cards: List[str]) -> Tuple[int, List[int]]:
    """
    Bewertet eine 7-Karten-Hand
    Rückgabe: (Kategorie, Tiebreaker-Liste)
    """

    ranks = [rank_value[c[0]] for c in cards]
    suits = [suit_value[c[1]] for c in cards]

    rank_counts = [0] * 15
    suit_counts = [0] * 4

    for r, s in zip(ranks, suits):
        rank_counts[r] += 1
        suit_counts[s] += 1

    # Flush prüfen
    flush_suit = -1
    for s, count in enumerate(suit_counts):
        if count >= 5:
            flush_suit = s
            break

    # Straight prüfen
    bitmask = 0
    for r in range(2, 15):
        if rank_counts[r] > 0:
            bitmask |= 1 << r

    wheel_mask = (1 << 14) | (1 << 5) | (1 << 4) | (1 << 3) | (1 << 2)

    straight_high = 0
    if (bitmask & wheel_mask) == wheel_mask:
        straight_high = 5
    else:
        for high in range(14, 5, -1):
            seq_mask = 0b11111 << (high - 4)
            if (bitmask & seq_mask) == seq_mask:
                straight_high = high
                break

    # Straight und Royal Flush prüfen
    if flush_suit != -1:
        flush_bitmask = 0
        for i in range(7):
            if suits[i] == flush_suit:
                flush_bitmask |= 1 << ranks[i]

        if (flush_bitmask & wheel_mask) == wheel_mask:
            return 8, [5]

        for high in range(14, 5, -1):
            seq_mask = 0b1111 << (high - 4)
            if (flush_bitmask & seq_mask) == seq_mask:
                if high == 14:
                    return 9, [14]
                return 8, [high]

    counts_sorted = sorted(
        [(cnt, r) for r, cnt in enumerate(rank_counts) if cnt > 0],
        reverse=True
    )

    # Quads
    if counts_sorted[0][0] == 4:
        kicker = max(r for r, c in enumerate(rank_counts) if c > 0 and r != counts_sorted[0][1])
        return 7, [counts_sorted[0][1], kicker]

    # Full House
    if counts_sorted[0][0] == 3 and counts_sorted[1][0] >= 2:
        return 6, [counts_sorted[0][1], counts_sorted[1][1]]

    # Flush
    if flush_suit != -1:
        flush_cards = sorted(
            [ranks[i] for i in range(7) if suits[i] == flush_suit],
            reverse=True
        )
        return 5, flush_cards[:5]

    # Straight
    if straight_high > 0:
        return 4, [straight_high]

    # Trips
    if counts_sorted[0][0] == 3:
        kickers = [r for r, c in enumerate(rank_counts) if c > 0 and r != counts_sorted[0][1]]
        kickers.sort(reverse=True)
        return 3, [counts_sorted[0][1]] + kickers[:2]

    # Two Pair
    pairs = [r for r, c in enumerate(rank_counts) if c == 2]
    if len(pairs) >= 2:
        pairs.sort(reverse=True)
        kicker = max(r for r, c in enumerate(rank_counts) if c > 0 and r not in pairs[:2])
        return 2, pairs[:2] + [kicker]

    # One Pair
    if len(pairs) == 1:
        kicker = [r for r, c in enumerate(rank_counts) if c >0 and r != pairs[0]]
        kicker.sort(reverse=True)
        return 1, [pairs[0]] + kicker[:3]

    # High Card
    high_cards = sorted([r for r, c in enumerate(rank_counts) if c > 0], reverse=True)
    return 0, high_cards[:5]