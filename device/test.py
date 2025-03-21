import json
import os
import cv2
from device.video_producer import VideoProducer


def test_video():
    from device.game import Game, Ruleset
    from device.table import TablePreset
    from device.utils import hex_to_opencv_hsv
    from device.video_producer import VideoProducer

    ruleset = Ruleset(
        id=0,
        name="wpa_rules",
        initial_duration=60,
        turn_duration=35,
        allarm_time=10,
        increment_duration=25,
        max_increment_for_match=1,
    )

    # Leggi i dati dal file JSON
    with open("./device/test_data/video/esempio_2.json", "r") as f:
        data = json.load(f)

    points = data["points"]
    min_area_threshold = data["min_area_threshold"]
    colors = [hex_to_opencv_hsv(color) for color in data["colors"]]

    table = TablePreset(
        0,
        "test_table",
        points=points,
        colors=colors,
        min_area_threshold=min_area_threshold,
    )
    video_test = "./device/test_data/video/esempio_2.mp4"
    video_producer = VideoProducer.get_instance(video_source=video_test, loop=False)

    game = Game(ruleset, table, "Player 1", "Player 2", video_producer)
    game.start()


def test_api(static=False):
    import device.api as api

    if static:
        frame = cv2.imread("./device/test_data/images/esempio_1.png")
        VideoProducer.get_instance(frame=frame)

    api.start(debug=True)


def test(is_video=True, static=False):
    if is_video:
        os.environ["FLASK_ENV"] = "video"
        test_video()
    else:
        os.environ["FLASK_ENV"] = "api"
        test_api(static=static)
