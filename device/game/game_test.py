import unittest

from device.game import Game, game_manager
from device.game.ruleset import Ruleset

TEST_RULESET = Ruleset(0, "test_ruleset", 60, 35, 25, 1)


class GameTest(unittest.TestCase):
    """
    Classe che viene utilizzata per unit testing
    """

    def setUp(self):
        self.game = Game(TEST_RULESET, "Giovanni", "Paolo")

    def test_game_creation(self):
        self.assertEqual(
            self.game._status, "ready", "Il gioco non inizia con lo status ready"
        )

    def test_timer_init(self):
        self.assertEqual(
            self.game._timer.remaining_time,
            TEST_RULESET.turn_duration,
            "Alla creazione del gioco, la durata del timer non corrisponde alla durata impostata nel ruleset",
        )

    def test_game_manager_new_game(self):
        game = game_manager.new_game(TEST_RULESET, "Giovanni", "Paolo")
        self.assertEqual(
            game,
            game_manager.get_game(),
            "Il gioco creato non corrisponde al gioco attuale",
        )

    def test_game_manager_new_game_replace_old_game(self):
        game = game_manager.new_game(TEST_RULESET, "Giovanni", "Paolo")
        game2 = game_manager.new_game(TEST_RULESET, "Giovanni", "Marco")
        self.assertEqual(
            game2,
            game_manager.get_game(),
            "Il gioco creato non corrisponde al gioco attuale",
        )
        self.assertEqual(game._status, "ended", "Il gioco vecchio non è terminato")


if __name__ == "__main__":
    unittest.main()
