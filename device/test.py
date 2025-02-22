import json
from device.game import Game, Ruleset
from device.table import TablePreset
from device.utils import hex_to_opencv_hsv
from device.video_producer import VideoProducer
import cv2


def test():
    ruleset = Ruleset(0, "wpa_rules", 60, 35, 25, 1)

    # Leggi i dati dal file JSON
    with open("./device/test_data/video/example_edited.json", "r") as f:
        data = json.load(f)

    points = data["points"]
    colors = [hex_to_opencv_hsv(color) for color in data["colors"]]

    table = TablePreset(
        0,
        "test_table",
        points=points,
        colors=colors,
    )
    video_producer = VideoProducer.get_instance(
        video_source="./device/test_data/video/example_edited.mp4", loop=False
    )

    game = Game(ruleset, table, "Player 1", "Player 2", video_producer)
    game.start()
