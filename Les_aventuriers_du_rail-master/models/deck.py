import random

class Deck:
    def __init__(self, cards):
        self.cards = cards
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop() if self.cards else None
