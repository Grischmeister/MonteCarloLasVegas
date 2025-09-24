# src/deck.py

ranks = "23456789TJQKA"
suits = "DHCS"

def create_deck():
    return [r + s for r in ranks for s in suits]

deck = create_deck()

if __name__ == '__main__':
    print("decksize:", len(deck))
    print("example cards:", deck[:8])