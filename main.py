import argparse
import cv2 as cv
import numpy as np
import logging
import preset
import webserver
import config as cf
import time
import log
from imutils.video import FPS

"""
=================== SETUP ==================
"""


def setup():
    """
    Fasi del setup
    - Caricati i file di configurazione e di logging
    - Avviato il webserver
    - Avviato la videocamera
    - Controllare se sono preset già esistenti e caricarli
    - Eseguire il preset di default se esiste
    """

    # Caricamento file config, setup logging e argomenti da linea di comando
    args = parser.parse_args()
    cf.load_config()
    log.logging_setup()

    # Avvio Web Server
    global wserver
    wserver = webserver.start(debug=args.debug)

    # Avvio Videocamera
    global vc
    vc = cv.VideoCapture(0)
    if not vc.isOpened():
        logging.error("Impossibile aprire la videocamera")
        return False

    # Lettura del preset di default
    default_preset = preset.get_default_preset()
    if default_preset is None:
        logging.warning("Preset di default non trovato, esecuzione setup inziale...")
        # TODO: Implementazione del primo setup
        # intial_setup()

    # TODO: Lettura del preset per il carimento iniziale

    return True


"""
=================== MAIN ==================
"""


def main():
    fps = FPS().start()
    while True:
        try:
            ret, frame = vc.read()
            if not ret:
                logging.error("Impossibile leggere il frame")
                return

            wserver.set_frame(frame)
            fps.update()
        except KeyboardInterrupt:
            logging.info("Interruzione rilevata, chiusura in corso...")
            break
    fps.stop()
    logging.info(f"FPS: {fps.fps()}")


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
    parser = argparse.ArgumentParser(
        prog="BilliardTimer",
        description="Codice sorgente del dispositivo BilliardTimer. Il dispositivo gestisce automaticamente il timer di gioco nel gioco del billiardo",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Abilita la modalità debug"
    )

    if setup():
        main()
    else:
        logging.error("Impossibile inizializzare il programma")
    end()
