# src/evaluator.py

from collections import Counter

ranks = "23456789TJQKA"
suits = "DHCS"

rank_value = {r: i for i, r in enumerate(ranks, start=2)}

def evaluate_hand(cards):
    """
    :param cards: list of strings, for example ['AS','KH','QD','JC','TC','7D','2C']
    :return: (Category, Tiebreaker) for comparison
    Categories:
        9 = Royal Flush
        8 = Straight Flush
        7 = Quads
        6 = Full House
        5 = Flush
        4 = Straight
        3 = Trips
        2 = Two Pair
        1 = Pair
        0 = High Card
    """

    values = [c[0] for c in cards]
    suits_list = [c[1] for c in cards]

    nums = sorted([rank_value[v] for v in values], reverse=True)

    # Wheel Straight (A,2,3,4,5)
    nums_unique = sorted(set(nums), reverse=True)
    if 14 in nums_unique:
        nums_unique.append(1)

    counter = Counter(values)
    most_common = counter.most_common()

    # Flush
    flush_suit = None
    for suit, count in Counter(suits_list).items():
        if count >= 5:
            flush_suit = suit
            break
    flush_nums = []
    if flush_suit:
        flush_nums = sorted([rank_value[c[0]] for c in cards if c[1] == flush_suit], reverse=True)

    # Straight
    straight_high = None
    for i in range(len(nums_unique) - 4):
        window = nums_unique[i:i+5]
        if window[0] - window[4] == 4:
            straight_high = window[0]
            break

    # Straight Flush
    if flush_suit:
        flush_cards = [rank_value[c[0]] for c in cards if c[1] == flush_suit]
        flush_unique= sorted(set(flush_cards), reverse=True)
        if 14 in flush_unique:
            flush_unique.append(1)
        for i in range(len(flush_unique) - 4):
            window = flush_unique[i:i+5]
            if window[0] - window[4]  == 4:
                if window[0] == 14:
                    return 9, [14]  # Royal Flush
                return 8, [window[0]]  # Straight Flush

    # Quads
    if most_common[0][1] == 4:
        return 7, [rank_value[most_common[0][0]]]

    # Full House
    if most_common[0][1] == 3 and most_common[1][1] >=2:
        return 6, [rank_value[most_common[0][0]], rank_value[most_common[1][0]]]

    # Flush
    if flush_suit:
        return 5, flush_nums[:5]

    #Straight
    if straight_high:
        return 4, [straight_high]

    # Trips
    if most_common[0][1] == 3:
        return 3, [rank_value[most_common[0][0]]]

    # Two Pair
    if most_common[0][1] == 2 and most_common[1][1] == 2:
        return 2, [rank_value[most_common[0][0]], rank_value[most_common[1][0]]]

    # Pair
    if most_common[0][1] == 2:
        return 1, [rank_value[most_common[0][0]]]

    # High Card
    return 0, sorted([rank_value[v] for v in values], reverse=True)