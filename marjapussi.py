import random

# Marjapussi card values from highest to lowest
CARD_NUMBERS = ['A', '10', 'K', 'D', 'J', '9', '8', '7', '6']
CARD_SUITS = ['H', 'S', 'D', 'C']
deck = [s+n for n in CARD_NUMBERS for s in CARD_SUITS]


class MarjapussiPlayerCards:
    def __init__(self):
        self.hand = []
        self.table = None
        self.won = []


class MarjapussiPlayer:
    def __init__(self, id, position):
        self.id = id
        self.cards = MarjapussiPlayerCards()
        self.position = position


class MarjapussiGame:
    def __init__(self):
        self.players = [None] * 4
        self.active_position = 0

    def join(self, player_id):
        try:
            free_slot = self.players.index(None)
        except ValueError:
            return False
        self.players[free_slot] = MarjapussiPlayer(player_id, free_slot)
        return True

    def deal(self):
        if None in self.players:
            return

        shuffled_deck = random.shuffle(deck)

        deck_slice = (0,9)
        for p in self.players:
            p.cards.hand = shuffled_deck[deck_slice[0]:deck_slice[1]]

    def count_cards_on_table(self):
        return len([p for p in self.players if p.cards.table is not None])

    def play_card(self, player_id, card):
        player = self.players[self.active_position]
        if player.id != player_id or card not in player.cards.hand:
            return False

        player.cards.hand.remove(card)
        player.cards.table = card

        #TODO: score trick if all players have card on table

        return True

    def score_trick(self):
        pass