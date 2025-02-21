import unittest
from device.game.timer import Timer


class TimerTest(unittest.TestCase):
    def setUp(self):
        self.timer = Timer(10, self.end_callback)

    def end_callback(self):
        print("END CALLBACK")

    def test_init_timer(self):
        self.assertIsInstance(
            self.timer,
            Timer,
            "new timer is not an instance of Timer",
        )


if __name__ == "__main__":
    unittest.main()
