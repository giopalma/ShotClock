import cv2 as cv


def gen_frames(server_thread):
    """
    Genera i frame per la visualizzazione in streaming.
    Semplicemente prende il frame dal thread del server e lo codifica in formato JPEG.
    TODO: Valutare le prestazioni di questa soluzione e se è possibile ottimizzarla.
    """
    while True:
        if server_thread.frame is not None:
            _, buffer = cv.imencode(".jpg", server_thread.frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
