# src/algorithms.py

import itertools
import random

from src.evaluator import evaluate_hand


def las_vegas_equity(hero, villain, deck):
    remaining_deck = [c for c in deck if c not in hero + villain]
    wins = ties = losses = 0

    for board in itertools.combinations(remaining_deck, 5):
        result = winner(hero, villain, list(board))
        if result == 1:
            wins += 1
        elif result == -1:
            losses += 1
        else:
            ties += 1

    total = wins + losses + ties
    equity = (wins + 0.5 * ties) / total
    return equity

def monte_carlo_equity(hero, villain, deck, iterations=10000):
    wins = ties = losses = 0

    for _ in range(iterations):
        remaining_deck = [c for c in deck if c not in hero + villain]
        board = random.sample(remaining_deck, 5)
        result = winner(hero, villain, board)
        if result == 1:
            wins += 1
        elif result == -1:
            losses += 1
        else:
            ties += 1

    total = wins + losses + ties
    equity = (wins + 0.5 * ties) / total
    return equity

def winner(hero, villain, board):
    hero_eval = evaluate_hand(hero + board)
    villain_eval = evaluate_hand(villain + board)

    if hero_eval[0] > villain_eval[0]:
        return 1
    elif hero_eval[0] < villain_eval[0]:
        return -1

    for h, v in zip(hero_eval[1], villain_eval[1]):
        if h > v:
            return 1
        elif h < v:
            return -1

    return 0