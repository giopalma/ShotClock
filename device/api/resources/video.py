import cv2 as cv
from flask import Response
from flask_restful import Resource
from device.video_producer import VideoProducer


class VideoStreaming(Resource):
    """
    VideoStreaming e la risorsa Resource per richiedere lo streaming video dal server.
    """

    def get(self):
        """
        Metodo GET. Restituisce lo streaming video come risposta HTTP.
        """
        return Response(
            self._frame_stream(),
            content_type="multipart/x-mixed-replace; boundary=frame",
        )

    def _frame_stream(self):
        """
        Genera i frame per la visualizzazione in streaming.
        Semplicemente prende il frame dal VideoProcessor e lo codifica in formato JPEG.
        TODO: Si potrebbe aggiungere la possibilità di streammare differenti frame, ad esempio frame con maschere applicate.
        """
        vp = VideoProducer()
        while True:
            frame = vp.frame
            if frame is None:
                continue
            _, buffer = cv.imencode(".jpg", frame)
            frame_buffer = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_buffer + b"\r\n"
            )
