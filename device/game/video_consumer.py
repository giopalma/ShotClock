from device.video_producer import VideoProducer
class VideoConsumer:
    """
    VideoConsumer è quello che effettivamente riconosce il movimento delle biglie da gioco.
    Viene eseguito dal Game ed esegue nel suo stesso thread dato che l'unico loop che viene
    eseguito in questo thread (il timer viene eseguito in un thread separato).
    """
    def __init__(self, start_movement_callback, stop_movement_callback):
        self.video_producer = VideoProducer()
        """
        Queste due fuzioni sono dei callback che vengono chiamati quando il VideoConsumer cambia di stato
        MOVIMENTO -> FERMO : stop_movement_callback
        FERMO -> MOVIMENTO : start_movement_callback
        """
        self.start_movement_callback = start_movement_callback
        self.stop_movement_callback = stop_movement_callback

        self.run()

    def run(self):
        while self.video_producer.is_opened():
            frame = self.video_producer.get_frame()

        raise NotImplementedError

    def end(self):
        raise NotImplementedError