import cv2 as cv
import numpy as np
import logging
import webserver
import config as cf
import time
import log

"""
=================== SETUP ==================
"""


def setup():
    # Caricamento file config e setup logging
    cf.load_config()
    log.logging_setup()

    # Avvio Web Server
    global wserver
    wserver = webserver.start()

    # Avvio Videocamera
    global vc
    vc = cv.VideoCapture(0)
    if not vc.isOpened():
        logging.error("Impossibile aprire la videocamera")
        return False

    return True


"""
=================== MAIN ==================
"""


def main():
    # TODO: Migliorare la legibilità del main
    fps = 0
    frame_count = 0
    start_time = time.time()
    fps_update_interval = 1 / 3
    while True:
        try:
            ret, frame = vc.read()
            if not ret:
                logging.error("Impossibile leggere il frame")
                return
            # Scrivere FPS nel frame

            frame_count += 1
            elapsed_time = time.time() - start_time

            if elapsed_time > fps_update_interval:
                fps = frame_count / elapsed_time
                frame_count = 0
                start_time = time.time()

            # Scrivere FPS nel frame
            cv.putText(
                frame,
                f"FPS: {fps:.2f}",
                (10, 30),
                cv.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
            wserver.print_frame(frame)
        except KeyboardInterrupt:
            logging.info("Interruzione rilevata, chiusura in corso...")
            break


"""
=================== END ==================
"""


def end():
    if vc and vc.isOpened():
        vc.release()
    if wserver:
        wserver.shutdown()


"""
=================== ENTRY POINT ==================
"""

if __name__ == "__main__":
    if setup():
        main()
    else:
        logging.error("Impossibile inizializzare il programma")
    end()
