import cv2
import threading
import time


class VideoProcessor:
    _instance = None

    def __new__(cls, video_source=0):
        if not cls._instance:
            cls._instance = super(VideoProcessor, cls).__new__(cls)
            cls._instance.frame = None
            cls._instance.video_capture = cv2.VideoCapture(video_source)
            cls._instance.is_running = False
            cls._instance.capture_thread = None
            cls._instance.frame_lock = threading.Lock()
            cls._instance._start_capture()
        return cls._instance

    def _capture_loop(self):
        while self.is_running:
            ret, frame = self.video_capture.read()
            if ret:
                with self.frame_lock:
                    self.frame = frame
            time.sleep(1 / 30)

    def _start_capture(self):
        if not self.is_running:
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()

    def get_frame(self):
        with self.frame_lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join()
        if self.video_capture:
            self.video_capture.release()

    def __del__(self):
        self.stop()
