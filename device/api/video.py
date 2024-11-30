import cv2 as cv
from device.video import VideoProcessor


def frame_stream():
    """
    Genera i frame per la visualizzazione in streaming.
    Semplicemente prende il frame dal thread del server e lo codifica in formato JPEG.
    """
    vp = VideoProcessor()
    while True:
        frame = vp.frame
        if frame is None:
            continue
        _, buffer = cv.imencode(".jpg", frame)
        frame_buffer = buffer.tobytes()
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_buffer + b"\r\n"
        )
