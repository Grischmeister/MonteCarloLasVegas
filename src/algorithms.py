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

# --- NEU: Hilfsfunktion für Mehrspieler (keine Änderung am bestehenden winner) ---
def winner_multi(hole_hands, board):
    """
    Bestimmt die Gewinner unter mehreren Spielern.
    :param hole_hands: Liste von 2-Karten-Listen, z. B. [["AS","KS"], ["QD","QC"], ...]
    :param board:      5-Karten-Liste fürs Board
    :return: (gewinner_indizes, evaluations)
             gewinner_indizes: Liste der Indizes in hole_hands, die gewinnen (bei Split alle)
             evaluations: Liste der evaluate_hand-Ergebnisse je Spieler
    """
    evals = [evaluate_hand(hand + board) for hand in hole_hands]

    # Bestwert initialisieren
    best = evals[0]
    winners = [0]

    # Vergleich wie in winner(): erst Kategorie, dann Tiebreaker (elementweise)
    def cmp(a, b):
        if a[0] != b[0]:
            return 1 if a[0] > b[0] else -1
        # elementweiser Vergleich (auffüllen, falls Längen differieren)
        la, lb = len(a[1]), len(b[1])
        L = max(la, lb)
        va = a[1] + [0]*(L-la)
        vb = b[1] + [0]*(L-lb)
        if va == vb:
            return 0
        return 1 if va > vb else -1

    for i in range(1, len(evals)):
        c = cmp(evals[i], best)
        if c > 0:
            best = evals[i]
            winners = [i]
        elif c == 0:
            winners.append(i)
    return winners, evals


# --- NEU: Exakte Equity bei TEILWEISE bekanntem Board (Heads-Up) ---
def las_vegas_equity_known_board(hero, villain, deck, board_known):
    """
    Exakte Equity (Heads-Up), wenn Teile des Boards bereits feststehen (Flop/Turn).
    :param board_known: Liste bekannter Boardkarten (Länge 0..5)
    """
    assert 0 <= len(board_known) <= 5
    remaining_deck = [c for c in deck if c not in hero + villain + board_known]
    need = 5 - len(board_known)

    wins = ties = losses = 0
    for tail in itertools.combinations(remaining_deck, need):
        board = board_known + list(tail)
        result = winner(hero, villain, board)
        if result == 1:
            wins += 1
        elif result == -1:
            losses += 1
        else:
            ties += 1

    total = wins + losses + ties
    return (wins + 0.5 * ties) / total


# --- NEU: Monte-Carlo mit bekanntem Board (Heads-Up) ---
def monte_carlo_equity_known_board(hero, villain, deck, board_known, iterations=10000):
    """
    MC-Equity (Heads-Up) bei bekanntem Boardteil (Flop/Turn).
    """
    assert 0 <= len(board_known) <= 5
    base_deck = [c for c in deck if c not in hero + villain + board_known]
    need = 5 - len(board_known)

    wins = ties = losses = 0
    for _ in range(iterations):
        tail = random.sample(base_deck, need) if need > 0 else []
        board = board_known + tail
        result = winner(hero, villain, board)
        if result == 1:
            wins += 1
        elif result == -1:
            losses += 1
        else:
            ties += 1

    total = wins + losses + ties
    return (wins + 0.5 * ties) / total


# --- NEU: Exakte Equity für MEHRERE Gegner (Preflop / unbekanntes Board) ---
def las_vegas_equity_multi(hero, villains, deck):
    """
    Exakte Equity für Hero gegen mehrere feste Villain-Hände (villains = Liste von 2-Karten-Listen).
    """
    used = hero + [c for v in villains for c in v]
    remaining_deck = [c for c in deck if c not in used]

    wins_share = 0.0
    total = 0
    for board in itertools.combinations(remaining_deck, 5):
        hands = [hero] + villains
        winners, _ = winner_multi(hands, list(board))
        total += 1
        if 0 in winners:
            # Hero gewinnt allein => Anteil 1.0, Split => anteilig
            wins_share += 1.0 / len(winners)
    return wins_share / total


# --- NEU: Monte-Carlo für MEHRERE Gegner (Preflop / unbekanntes Board) ---
def monte_carlo_equity_multi(hero, villains, deck, iterations=10000):
    """
    MC-Equity für Hero gegen mehrere feste Villain-Hände.
    """
    used = hero + [c for v in villains for c in v]
    base_deck = [c for c in deck if c not in used]

    wins_share = 0.0
    for _ in range(iterations):
        board = random.sample(base_deck, 5)
        winners, _ = winner_multi([hero] + villains, board)
        if 0 in winners:
            wins_share += 1.0 / len(winners)
    return wins_share / iterations


# --- NEU: Varianten mit bekanntem Board für MEHRERE Gegner ---
def las_vegas_equity_multi_known_board(hero, villains, deck, board_known):
    """
    Exakte Equity (mehrere Gegner) mit bekanntem Boardteil.
    """
    assert 0 <= len(board_known) <= 5
    used = hero + [c for v in villains for c in v] + board_known
    remaining_deck = [c for c in deck if c not in used]
    need = 5 - len(board_known)

    wins_share = 0.0
    total = 0
    for tail in itertools.combinations(remaining_deck, need):
        board = board_known + list(tail)
        winners, _ = winner_multi([hero] + villains, board)
        total += 1
        if 0 in winners:
            wins_share += 1.0 / len(winners)
    return wins_share / total


def monte_carlo_equity_multi_known_board(hero, villains, deck, board_known, iterations=10000):
    """
    MC-Equity (mehrere Gegner) mit bekanntem Boardteil.
    """
    assert 0 <= len(board_known) <= 5
    used = hero + [c for v in villains for c in v] + board_known
    base_deck = [c for c in deck if c not in used]
    need = 5 - len(board_known)

    wins_share = 0.0
    for _ in range(iterations):
        tail = random.sample(base_deck, need) if need > 0 else []
        board = board_known + tail
        winners, _ = winner_multi([hero] + villains, board)
        if 0 in winners:
            wins_share += 1.0 / len(winners)
    return wins_share / iterations