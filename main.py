# main.py
import time

from experiments import heads_up_las_vegas
from src.deck import create_deck
from src.experiments import heads_up_monte_carlo

def main():
    start = time.time()
    deck = create_deck()
#    heads_up_monte_carlo(100000, deck)
    heads_up_las_vegas(deck)
    end = time.time()
    print(end - start)

if __name__ == "__main__":
    main()