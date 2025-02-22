import unittest
from device.table import TablePreset
from device.game.video_consumer import VideoConsumer
from device.utils import hex_to_opencv_hsv
from device.video_producer import VideoProducer


class VideoConsumerTest(unittest.TestCase):

    def setUp(self):
        colors = ["#45c6ed", "#2288b5", "#1978a2", "#3bbbf3", "#0b6d9e"]
        self.table = TablePreset(
            id=0,
            name="test_table_preset",
            points=[(120, 80), (520, 80), (520, 280), (120, 280)],
            colors=[hex_to_opencv_hsv(color) for color in colors],
        )
        self.video_consumer = VideoConsumer(
            self.table,
            self.start_movement_callback,
            self.stop_movement_callback,
            VideoProducer.get_instance(),
        )

    def start_movement_callback(self):
        print("START MOVEMENT")

    def stop_movement_callback(self):
        print("STOP MOVEMENT")

    def test_init_video_consumer(self):
        self.assertIsInstance(
            self.video_consumer,
            VideoConsumer,
            "new video_consumer is not an instance of VideoConsumer",
        )


if __name__ == "__main__":
    unittest.main()
