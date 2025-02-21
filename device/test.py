from device.game import Game, Ruleset
from device.table import TablePreset
from device.utils import hex_to_opencv_hsv
from device.video_producer import VideoProducer


def test():
    ruleset = Ruleset(0, "wpa_rules", 60, 35, 25, 1)
    colors = ["#45c6ed", "#2288b5", "#1978a2", "#3bbbf3", "#0b6d9e"]
    table = TablePreset(
        0,
        "test_table",
        points=[(120, 80), (520, 80), (520, 280), (120, 280)],
        table_colors=[hex_to_opencv_hsv(color) for color in colors],
    )
    video_producer = VideoProducer.get_instance(
        video_source="./test_data/video/example.mp4"
    )
    game = Game(ruleset, table, "Player 1", "Player 2", video_producer)

    # game.start()
