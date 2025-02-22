import cv2
import threading
import time


class VideoProducer:
    """
    VideoProcessor è un Singleton che gira su un thread separato e gestirà la registrazione
    video. Fornisce la funzione get_frame() che restituisce il frame attuale.
    TODO: La classe potrà fornire non solo il frame RAW, ma anche elaborato (GRAY + GAUSSIAN) che verrà utilizzato dal Game per individuare il movimento
    """

    _instance = None

    def __init__(self):
        raise RuntimeError("VideoProcessor instance cannot be instantiated")

    def __new__(cls, video_source, loop):
        if not cls._instance:
            cls._instance = super(VideoProducer, cls).__new__(cls)

            cls._instance.frame = None
            cls._instance.video_capture = cv2.VideoCapture(video_source)
            cls._instance._loop = loop
            cls._instance.is_running = False
            cls._instance.capture_thread = None
            cls._instance.stop_lock = threading.Lock()
            cls._instance._start_capture()
        return cls._instance

    @classmethod
    def get_instance(cls, video_source=0, loop=False):
        if not cls._instance:
            cls._instance = cls.__new__(cls, video_source, loop)
        return cls._instance

    def _capture_loop(self):
        while self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            self.frame = frame
            if not ret and self._loop:
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            time.sleep(1 / 30)

    def _start_capture(self):
        if not self.is_running:
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = False
            self.capture_thread.name = "VideoProducerThread"
            self.capture_thread.start()

    def get_frame(self):
        while self.frame is None:
            pass
        return self.frame

    def get_frame_blurred(self):
        frame = self.get_frame()
        return cv2.GaussianBlur(frame, (5, 5), 0) if frame is not None else None

    def stop(self):
        with self.stop_lock:
            if self.is_running:
                self.is_running = False
                if self.capture_thread:
                    self.capture_thread.join(timeout=1)
                if self.video_capture.isOpened():
                    self.video_capture.release()

    def is_opened(self):
        return self.video_capture.isOpened()

    def __del__(self):
        self.stop()
