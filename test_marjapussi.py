import unittest
import marjapussi


class MarjapussiNewGameTestCase(unittest.TestCase):

    def test_new_game_is_empty(self):
        game = marjapussi.MarjapussiGame()
        players = list(filter(lambda x: x is not None, game.players))
        self.assertEqual([], players)
        self.assertEqual(None, game.dealer)
        self.assertEqual(None, game.active_player)
        self.assertEqual(None, game.trump)

    def test_adding_players(self):
        game = marjapussi.MarjapussiGame()
        for idx, connection_id in enumerate([123, 456, 789, 612]):
            player_id = game.join(connection_id)
            self.assertIsNotNone(player_id)
            players = list(filter(lambda x: x is not None, game.players))
            self.assertEqual(idx + 1, len(players))

            p = players[idx]
            self.assertEqual([], p.cards.hand)
            self.assertEqual(None, p.cards.table)
            self.assertEqual([], p.cards.won)
            self.assertEqual(player_id, p.id)
            self.assertEqual(0, p.score)

    def test_cannot_join_full_game(self):
        game = marjapussi.MarjapussiGame()
        for pid in range(4):
            self.assertTrue(game.join(pid))
        self.assertFalse(game.join(5))
        self.assertEqual([], [p for p in game.players if p.id == 5])

    def test_need_four_players_to_deal(self):
        game = marjapussi.MarjapussiGame()
        for pid in range(4):
            self.assertFalse(game.deal())
            self.assertTrue(game.join(pid))

        for p in game.players:
            self.assertEqual([], p.cards.hand)

        self.assertIsNotNone(game.dealer)
        self.assertIsNotNone(game.active_player)
        self.assertEqual(game.players[0], game.dealer)
        self.assertEqual(game.players[0], game.active_player)

        self.assertTrue(game.deal())

        self.assertIsNotNone(game.dealer)
        self.assertIsNotNone(game.active_player)
        self.assertEqual(game.players[1], game.dealer)
        self.assertEqual(game.players[0], game.active_player)

        for p in game.players:
            self.assertEqual(9, len(p.cards.hand))
            self.assertEqual(None, p.cards.table)
            self.assertEqual([], p.cards.won)


class MarjapussiGameActionsTestCase(unittest.TestCase):
    def setUp(self):
        self.game = marjapussi.MarjapussiGame()
        for pid in range(4):
            self.assertTrue(self.game.join(pid))
        self.game.deal()

    def test_playing_card(self):
        self.assertEqual(self.game.active_player, self.game.players[0])

        pid = self.game.active_player.id
        card = self.game.active_player.cards.hand[0]
        self.assertTrue(self.game.play_card(pid, card))

        self.assertEqual(self.game.active_player, self.game.players[1])
        self.assertTrue(card not in self.game.players[0].cards.hand)
        self.assertEqual(card, self.game.players[0].cards.table)

    def test_can_play_card_only_on_own_turn(self):
        self.assertEqual(self.game.active_player, self.game.players[0])

        pid = self.game.players[1].id
        card = self.game.players[1].cards.hand[0]
        self.assertFalse(self.game.play_card(pid, card))

        self.assertEqual(self.game.active_player, self.game.players[0])
        self.assertTrue(card in self.game.players[1].cards.hand)
        self.assertIsNone(self.game.players[1].cards.table)

        pid = self.game.active_player.id
        card = self.game.active_player.cards.hand[0]
        self.assertTrue(self.game.play_card(pid, card))

        pid = self.game.players[1].id
        card = self.game.players[1].cards.hand[0]
        self.assertTrue(self.game.play_card(pid, card))
        self.assertTrue(card not in self.game.players[1].cards.hand)
        self.assertEqual(card, self.game.players[1].cards.table)

    def test_cannot_play_card_that_is_not_in_hand(self):
        self.assertEqual(self.game.active_player, self.game.players[0])
        pid = self.game.players[0].id
        card = self.game.players[1].cards.hand[4]
        self.assertFalse(self.game.play_card(pid, card))

        self.assertEqual(self.game.active_player, self.game.players[0])
        self.assertTrue(card in self.game.players[1].cards.hand)
        self.assertIsNone(self.game.players[1].cards.table)

    def test_playing_turn_is_passed_correctly(self):
        self.assertEqual(self.game.active_player, self.game.players[0])
        for turn in range(9):
            expected_player = turn % 4
            self.assertEqual(self.game.active_player, self.game.players[expected_player])

            pid = self.game.active_player.id
            card = self.game.active_player.cards.hand[0]
            self.assertTrue(self.game.play_card(pid, card))

            full_trick = self.game.trick_is_full()
            if expected_player == 3:
                self.assertTrue(full_trick)
                self.assertTrue(self.game.check_trick_end())
            else:
                self.assertFalse(full_trick)

    def test_dealer_turn_is_passed_correctly(self):
        self.assertEqual(self.game.active_player, self.game.players[0])
        self.assertEqual(self.game.dealer, self.game.players[1])

        for turn in range(9):
            expected_dealer = (turn + 1) % 4
            self.assertEqual(self.game.dealer, self.game.players[expected_dealer])
            self.assertTrue(self.game.active_player, self.game.dealer)

            pid = self.game.active_player.id
            card = self.game.active_player.cards.hand[0]
            self.assertTrue(self.game.play_card(pid, card))

            self.assertEqual(self.game.dealer, self.game.players[expected_dealer])

            self.assertTrue(self.game.deal())


class MarjapussiTrickScoringTestCase(unittest.TestCase):
    def setUp(self):
        self.game = marjapussi.MarjapussiGame()
        for pid in range(4):
            self.assertTrue(self.game.join(pid))

    def prepare_trick(self, trick):
        for card, player in zip(trick, self.game.players):
            player.cards.table = card

    def check_winner(self):
        for p in self.game.players:
            if len(p.cards.won) != 0:
                return p
        return None

    def test_score_trick_all_same_suit(self):
        test_trick = ['H6', 'HK', 'H10', 'H8']
        self.prepare_trick(test_trick)
        self.assertTrue(self.game.check_trick_end())
        self.assertEqual(self.game.players[2], self.check_winner())

    def test_score_trick_all_different_suit_no_trump(self):
        test_trick = ['H6', 'DK', 'C10', 'S8']
        self.prepare_trick(test_trick)
        self.assertTrue(self.game.check_trick_end())
        self.assertEqual(self.game.players[0], self.check_winner())

    def test_score_trick_all_different_suit_no_trump_change_starter(self):
        test_trick = ['H6', 'DK', 'C10', 'S8']
        self.prepare_trick(test_trick)

        self.game.active_player = self.game.players[1]

        self.assertTrue(self.game.check_trick_end())
        self.assertEqual(self.game.players[1], self.check_winner())

    def test_score_trick_with_trumps_change_starter(self):
        test_trick = ['D6', 'D7', 'C10', 'CA']
        self.prepare_trick(test_trick)

        self.game.active_player = self.game.players[2]
        self.game.trump = 'D'

        self.assertTrue(self.game.check_trick_end())
        self.assertEqual(self.game.players[1], self.check_winner())

    def test_score_trick_with_trump_set_not_played_change_starter(self):
        test_trick = ['CA', 'S6', 'SJ', 'S8']
        self.prepare_trick(test_trick)

        self.game.active_player = self.game.players[3]
        self.game.trump = 'D'

        self.assertTrue(self.game.check_trick_end())
        self.assertEqual(self.game.players[2], self.check_winner())


class MarjapussiDictionaryTransformTestCase(unittest.TestCase):
    def setUp(self):
        self.game = marjapussi.MarjapussiGame()
        for pid in range(4):
            self.game.join(pid)
        self.game.deal()

        self.play_trick()
        self.play_trick()
        self.play_trick()

        self.game.play_card(self.game.active_player.id, self.game.active_player.cards.hand[0])
        self.game.play_card(self.game.active_player.id, self.game.active_player.cards.hand[0])

    def play_trick(self):
        for i in range(4):
            self.game.play_card(self.game.active_player.id, self.game.active_player.cards.hand[0])
        self.game.check_trick_end()

    def test_dictionary_transforms(self):
        game_dict = self.game.to_dict_full()
        game_from_dict = marjapussi.MarjapussiGame.from_dict(game_dict)
        game_dict2 = self.game.to_dict_full()

        self.assertEqual(game_dict, game_dict2)

        for p1, p2 in zip(self.game.players, game_from_dict.players):
            self.assertEqual(p1.cards.hand, p2.cards.hand)
            self.assertEqual(p1.cards.table, p2.cards.table)
            self.assertEqual(p1.cards.won, p2.cards.won)


if __name__ == '__main__':
    unittest.main()
