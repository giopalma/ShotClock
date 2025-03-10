import cv2
import threading
import time
from picamera2 import Picamera2


class VideoProducer:
    """
    VideoProcessor è un Singleton che gira su un thread separato e gestirà la registrazione
    video. Fornisce la funzione get_frame() che restituisce il frame attuale.
    """

    _instance = None

    def __init__(self):
        raise RuntimeError("VideoProcessor instance cannot be instantiated")

    def __new__(cls, video_source=None, loop=False):
        if not cls._instance:
            cls._instance = super(VideoProducer, cls).__new__(cls)

            cls._instance.frame = None
            cls._instance.is_picamera = (
                video_source is None
            )  # Usa picamera se non è specificata una sorgente

            if cls._instance.is_picamera:
                cls._instance.picam = Picamera2()
                # Configurazione base della camera
                config = cls._instance.picam.create_preview_configuration(
                    main={"size": (640, 480), "format": "BGR888"},
                )
                cls._instance.picam.configure(config)
                cls._instance.picam.start()
            else:
                cls._instance.video_capture = cv2.VideoCapture(video_source)

            cls._instance._loop = loop
            cls._instance.is_running = False
            cls._instance.capture_thread = None
            cls._instance.stop_lock = threading.Lock()
            cls._instance._start_capture()
        return cls._instance

    @classmethod
    def get_instance(cls, video_source=None, loop=False):
        if not cls._instance:
            cls._instance = cls.__new__(cls, video_source, loop)
        return cls._instance

    def _capture_loop(self):
        if self.is_picamera:
            while self.is_running:
                self.frame = self.picam.capture_array()
                time.sleep(1 / 30)
        else:
            while self.video_capture.isOpened() and self.is_running:
                ret, frame = self.video_capture.read()
                if ret:
                    self.frame = frame
                elif self._loop:
                    self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                time.sleep(1 / 30)

    def _start_capture(self):
        if not self.is_running:
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = (
                True  # Era False, meglio True per chiusura automatica
            )
            self.capture_thread.name = "VideoProducerThread"
            self.capture_thread.start()

    def get_fps(self):
        if self.is_picamera:
            # Ritorna un valore nominale per picamera, potresti anche calcolarlo
            return 30
        else:
            return self.video_capture.get(cv2.CAP_PROP_FPS)

    def get_frame(self):
        while self.frame is None:
            time.sleep(0.01)  # Aggiungi un piccolo ritardo per evitare il 100% CPU
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
                if self.is_picamera:
                    self.picam.stop()
                    self.picam.close()
                elif hasattr(self, "video_capture") and self.video_capture.isOpened():
                    self.video_capture.release()

    def is_opened(self):
        if self.is_picamera:
            # Non c'è un metodo isOpened() equivalente in picamera2
            # quindi assumiamo che sia aperta se l'istanza esiste
            return True
        else:
            return self.video_capture.isOpened()

    def __del__(self):
        self.stop()
