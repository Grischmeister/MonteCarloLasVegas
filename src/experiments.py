# src/experiments.py
from algorithms import monte_carlo_equity, las_vegas_equity


def heads_up_monte_carlo(iterations, deck):
    hero = ["AS", "KS"]
    villain = ["QD", "QC"]
    print("Monte Carlo Equity (" + str(iterations) + " Iterationen):", monte_carlo_equity(hero, villain, deck,iterations))

def heads_up_las_vegas(deck):
    hero = ["AS", "KS"]
    villain = ["QD", "QC"]
    print("Las Vegas Equity: ", las_vegas_equity(hero, villain, deck))