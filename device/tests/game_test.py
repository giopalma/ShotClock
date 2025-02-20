import unittest

from device.game import Game
from device.game.ruleset import Ruleset

TEST_RULESET = Ruleset(0,"test_ruleset", 35, 25, 1)

class GameTest(unittest.TestCase):
    """
    Classe che viene utilizzata per unit testing
    """
    def setUp(self):
        self.game = Game(TEST_RULESET, "Giovanni", "Paolo")

    def test_game_creation(self):
        self.assertEqual(self.game.status,"ready","Il gioco non inizia con lo status ready")

    def test_timer_init(self):
        self.assertEqual(self.game.timer.remaining_time, TEST_RULESET.turn_duration, "Alla creazione del gioco, la durata del timer non corrisponde alla durata impostata nel ruleset")

if __name__ == '__main__':
    unittest.main()
