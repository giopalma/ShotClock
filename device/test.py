import json
from device.game import Game, Ruleset
from device.table import TablePreset
from device.utils import hex_to_opencv_hsv
from device.video_producer import VideoProducer
import cv2


def list_ports():
    """
    Test the ports and returns a tuple with the available ports and the ones that are working.
    """
    non_working_ports = []
    dev_port = 0
    working_ports = []
    available_ports = []
    while (
        len(non_working_ports) < 6
    ):  # if there are more than 5 non working ports stop the testing.
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
            print("Port %s is not working." % dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print(
                    "Port %s is working and reads images (%s x %s)" % (dev_port, h, w)
                )
                working_ports.append(dev_port)
            else:
                print(
                    "Port %s for camera ( %s x %s) is present but does not reads."
                    % (dev_port, h, w)
                )
                available_ports.append(dev_port)
        dev_port += 1
    return available_ports, working_ports, non_working_ports


def test():
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
    video_test = "./device/test_data/video/example_edited_extended.mp4"
    webcam = 0
    video_producer = VideoProducer.get_instance(video_source=video_test, loop=False)

    game = Game(ruleset, table, "Player 1", "Player 2", video_producer)
    game.start()
