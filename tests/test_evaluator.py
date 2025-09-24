# tests/test_evaluator.py

import pytest
from src.evaluator import evaluate_hand

def test_royal_flush():
    cards = ["AS", "KS", "QS", "JS", "TS", "3D", "4H"]
    assert evaluate_hand(cards)[0] == 9

def test_straight_flush():
    cards = ["9H","8H","7H","6H","5H","2C","KD"]
    rank, kicker = evaluate_hand(cards)
    assert rank == 8
    assert kicker[0] == 9  # 9 high Straight Flush

def test_four_of_a_kind():
    cards = ["7D","7C","7H","7S","2D","5C","9H"]
    rank, kicker = evaluate_hand(cards)
    assert rank == 7
    assert kicker[0] == 7 # Quad 7s

def test_full_house():
    cards = ["KH","KS","KC","2D","2C","9H","TD"]
    rank, kicker = evaluate_hand(cards)
    assert rank == 6
    assert kicker[0] == 13  # Kings full of 2s

def test_flush():
    cards = ["AH","JH","8H","4H","2H","KS","QD"]
    rank, kicker = evaluate_hand(cards)
    assert rank == 5
    assert kicker[0] == 14  # Ace high Flush

def test_straight_wheel():
    cards = ["5D","4C","3H","2S","AD","9C","KH"]
    rank, kicker = evaluate_hand(cards)
    assert rank == 4
    assert kicker[0] == 5  # Wheel Straight (A to 5)

def test_three_of_a_kind():
    cards = ["QH","QS","QC","8D","4S","2C","9H"]
    rank, kicker = evaluate_hand(cards)
    assert rank == 3
    assert kicker[0] == 12  # Queen Trips

def test_two_pair():
    cards = ["JD","JC","8S","8H","2C","5D","KH"]
    rank, kicker = evaluate_hand(cards)
    assert rank == 2
    assert sorted(kicker, reverse=True) == [11, 8] # "Two Pair - Jacks and 8s"

def test_one_pair():
    cards = ["AD","AC","7H","4C","2D","9S","TH"]
    rank, kicker = evaluate_hand(cards)
    assert rank == 1
    assert kicker[0] == 14  # Pair of Aces

def test_high_card():
    cards = ["AS","KD","9C","7H","4D","2S","3C"]
    rank, kicker = evaluate_hand(cards)
    assert rank == 0
    assert kicker[0] == 14  # Ace High