import random
import uuid
from typing import Optional, List
from copy import copy, deepcopy
from functools import cmp_to_key

# Marjapussi card values from lowest to highest
CARD_NUMBERS = ['6', '7', '8', '9', 'J', 'Q', 'K', '10', 'A']
CARD_SUITS = ['H', 'S', 'D', 'C']
DECK = [s+n for s in CARD_SUITS for n in CARD_NUMBERS]


def get_value(card):
    return CARD_NUMBERS.index(card[1:])


def get_suit(card):
    return card[0]

def hand_order_compare(card1, card2):
    return DECK.index(card1) - DECK.index(card2)


class MarjapussiPlayerCards:
    def __init__(self):
        self.hand = []
        self.table = None
        self.won = []

    @staticmethod
    def from_dict(d):
        cards = MarjapussiPlayerCards()
        for k, v in d.items():
            setattr(cards, k, v)
        return cards


class MarjapussiPlayer:
    def __init__(self, name, connection_id, position):
        self.id = str(uuid.uuid4())
        self.name = name
        self.connection_id = connection_id
        self.cards = MarjapussiPlayerCards()
        self.position = position
        self.score = 0

    @staticmethod
    def from_dict(d):
        player = MarjapussiPlayer("", 0, 0)
        player.cards = MarjapussiPlayerCards.from_dict(d['cards'])
        for k, v in d.items():
            if k != 'cards':
                setattr(player, k, v)
        return player


class MarjapussiGame:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.name = "Empty game"
        self.players: List[Optional[MarjapussiPlayer]] = [None] * 4
        self.active_player = None
        self.dealer = None
        self.trump = None

    def join(self, player_name, connection_id):
        try:
            free_slot = self.players.index(None)
        except ValueError:
            return None
        self.players[free_slot] = MarjapussiPlayer(player_name, connection_id, free_slot)

        if free_slot == 0:
            self.active_player = self.dealer = self.players[0]
            self.name = self.players[0].name + "'s game"

        return self.players[free_slot].id

    def rejoin(self, player_id, connection_id):
        try:
            player = next(p for p in self.players if p is not None and p.id == player_id)
        except StopIteration:
            return False
        player.connection_id = connection_id
        return True

    def deal(self):
        if None in self.players:
            return False

        deck = copy(DECK)
        random.shuffle(deck)

        for idx, player in enumerate(self.players):
            deck_slice = (0 + 9*idx, 9+9*idx)
            player.cards.hand = deck[deck_slice[0]:deck_slice[1]]
            player.cards.hand = sorted(player.cards.hand, key=cmp_to_key(hand_order_compare))
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

    def trick_is_full(self):
        return sum(1 for p in self.players if p.cards.table is not None) >= 4

    def play_card(self, player_id, card):
        if (
                self.trick_is_full() or
                self.active_player.id != player_id or
                card not in self.active_player.cards.hand
        ):
            return False

        self.active_player.cards.hand.remove(card)
        self.active_player.cards.table = card

        self.active_player = self._next_player(self.active_player)

        return True

    def end_trick(self):
        if not self.trick_is_full():
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
                self.active_player = player
            player.cards.table = None

        return True

    def to_dict_full(self):
        game = deepcopy(self)

        if game.active_player is not None:
            game.active_player = game.active_player.id

        if game.dealer is not None:
            game.dealer = game.dealer.id

        for p in game.players:
            if p is not None:
                p.cards = vars(p.cards)

        game.players = [None if p is None else vars(p) for p in game.players]

        return vars(game)

    def to_dict_for_player(self, player_id):
        game = self.to_dict_full()
        for p in game['players']:
            if p is not None and p['id'] != player_id:
                p['cards']['hand'] = len(p['cards']['hand'])
                p['id'] = None

        return game

    @staticmethod
    def from_dict(d):
        game = MarjapussiGame()
        game.players = [None if pd is None else MarjapussiPlayer.from_dict(pd) for pd in d['players']]

        for k, v in d.items():
            if k != 'players':
                setattr(game, k, v)

        for p in game.players:
            if p is None:
                continue
            if p.id == game.dealer:
                game.dealer = p
            if p.id == game.active_player:
                game.active_player = p

        return game
