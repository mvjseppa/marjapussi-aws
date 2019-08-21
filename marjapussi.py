import random
from typing import Optional, List

# Marjapussi card values from lowest to highest
CARD_NUMBERS = ['6', '7', '8', '9', 'J', 'Q', 'K', '10', 'A']
CARD_SUITS = ['H', 'S', 'D', 'C']
deck = [s+n for n in CARD_NUMBERS for s in CARD_SUITS]


def get_value(card):
    return CARD_NUMBERS.index(card[1])


def get_suit(card):
    return card[0]


class MarjapussiPlayerCards:
    def __init__(self):
        self.hand = []
        self.table = None
        self.won = []


class MarjapussiPlayer:
    def __init__(self, player_id, position):
        self.id = player_id
        self.cards = MarjapussiPlayerCards()
        self.position = position
        self.score = 0


class MarjapussiGame:
    def __init__(self):
        self.players: List[Optional[MarjapussiPlayer]] = [None] * 4
        self.active_player = None
        self.dealer = None
        self.trump = None

    def join(self, player_id):
        try:
            free_slot = self.players.index(None)
        except ValueError:
            return False
        self.players[free_slot] = MarjapussiPlayer(player_id, free_slot)

        if free_slot == 0:
            self.active_player = self.dealer = self.players[0]

        return True

    def deal(self):
        if None in self.players:
            return False

        random.shuffle(deck)

        for idx, player in enumerate(self.players):
            deck_slice = (0 + 9*idx, 9+9*idx)
            player.cards.hand = deck[deck_slice[0]:deck_slice[1]]
            player.cards.table = None
            player.cards.won = []

        self.active_player = self.dealer
        self.dealer = self._next_player(self.dealer)
        self.trump = None

        return True

    def _next_player(self, player):
        idx = self.players.index(player) + 1
        if idx >= len(self.players):
            idx = 0
        return self.players[idx]

    def _count_cards_on_table(self):
        return sum(1 for p in self.players if p.cards.table is not None)

    def play_card(self, player_id, card):
        if self.active_player.id != player_id or card not in self.active_player.cards.hand:
            return False

        self.active_player.cards.hand.remove(card)
        self.active_player.cards.table = card

        self.active_player = self._next_player(self.active_player)

        return True

    def check_trick_end(self):
        if self._count_cards_on_table() < 4:
            return False

        highest_card = self.active_player.cards.table
        trick_cards = [p.cards.table for p in self.players]

        for card in trick_cards:
            first_trump = get_suit(highest_card) != self.trump and get_suit(card) == self.trump
            higher_same_suit = get_suit(highest_card) == get_suit(card) and get_value(highest_card) < get_value(card)

            if first_trump or higher_same_suit:
                highest_card = card

        for player in self.players:
            if player.cards.table == highest_card:
                player.cards.won.append(trick_cards)
            player.cards.table = None
