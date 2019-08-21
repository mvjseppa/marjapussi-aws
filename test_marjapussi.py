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
        for idx, player_id in enumerate([123, 456, 789, 612]):
            self.assertTrue(game.join(player_id))
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

        self.assertTrue(game.deal())

        for p in game.players:
            self.assertEqual(9, len(p.cards.hand))
            self.assertEqual(None, p.cards.table)
            self.assertEqual([], p.cards.won)


class MarjapussiDealTestCase(unittest.TestCase):
    def setUp(self):
        self.game = marjapussi.MarjapussiGame()




if __name__ == '__main__':
    unittest.main()
