import json
import os

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
        allarm_time=50,
        increment_duration=25,
        max_increment_for_match=1,
    )

    # Leggi i dati dal file JSON
    with open("./device/test_data/video/output.json", "r") as f:
        data = json.load(f)

    points = data["points"]
    colors = [hex_to_opencv_hsv(color) for color in data["colors"]]

    table = TablePreset(
        0,
        "test_table",
        points=points,
        colors=colors,
    )
    video_test = "./device/test_data/video/output.avi"
    webcam = 0
    video_producer = VideoProducer.get_instance(video_source=video_test, loop=False)

    game = Game(ruleset, table, "Player 1", "Player 2", video_producer)
    game.start()


def test_api():
    import device.api as api

    api.start(debug=True)


def test(is_video=False):
    if is_video:
        os.environ["FLASK_ENV"] = "video"
        test_video()
    else:
        os.environ["FLASK_ENV"] = "development"
        test_api()
