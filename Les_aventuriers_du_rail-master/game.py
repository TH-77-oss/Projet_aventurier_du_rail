import random
from data.data import *
from models.player import Player
import json

class Game:
    def __init__(self, players):
        self.players = [Player(players[i], PLAYER_COLORS[i]) for i in range(len(players))]
        self.current_player_index = 0
        self.train_deck = WAGON_COLORS * 12
        random.shuffle(self.train_deck)

        self.SCORE_TABLE = {}

        with open("data/destinations.json", "r", encoding="utf-8") as f:
            self.destinations = json.load(f)

        self.visible_cards = []
        for _ in range(5):
            if self.train_deck:
                self.visible_cards.append(self.train_deck.pop())

    def start_game(self):
        for player in self.players:
            for _ in range(4):
                if self.train_deck:
                    player.draw_card(self.train_deck.pop())

    def get_visible_cards(self):
        return self.visible_cards

    def draw_destination_cards(self, count=3):
        cards = []
        for _ in range(count):
            if self.destinations:
                cards.append(self.destinations.pop())
        return cards

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def draw_train_card(self):
        if self.train_deck:
            return self.train_deck.pop()
        return None

    def player_draw_cards(self, nb_cards):
        for _ in range(nb_cards):
            card = self.draw_train_card()
            if card:
                self.current_player.draw_card(card)

    def visible_card_draw(self, index):
        if 0 <= index < len(self.visible_cards):
            card = self.visible_cards[index]
            self.current_player.train_cards.append(card)
            if self.train_deck:
                self.visible_cards[index] = self.train_deck.pop()
            else:
                del self.visible_cards[index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)