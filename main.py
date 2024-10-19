import cv2 as cv
import numpy as np
import logging
import web_server
import config as cf
import time
import log
import utils

'''
=================== SETUP ==================
'''


def camera_setup(vc):
    logging.info("Videocamera aperta")
    camera_config = cf.get_config()['CAMERA']
    vc.set(cv.CAP_PROP_FRAME_WIDTH, float(camera_config['Width']))
    vc.set(cv.CAP_PROP_FRAME_HEIGHT, float(camera_config['Height']))
    vc.set(cv.CAP_PROP_FPS, float(camera_config['FPS']))
    logging.info("Videocamera impostata")


def setup():
    cf.load_config()
    log.logging_setup()

    # Avvio Web Server
    global wserver
    wserver = web_server.start()

    global vc
    vc = cv.VideoCapture(0)
    if not vc.isOpened():
        logging.error("Impossibile aprire la videocamera")
        return False

    """ 
    camera_setup(vc)
    image = cv.imread('./data/imgs/test.png', cv.IMREAD_COLOR_BGR)
    cv.imshow('test', image)

    logging.info("Setup della maschera")
    logging.info("Ricerca mashera salvata in locale...")
    mask = utils.get_mask()
    if not mask:
        logging.warning("Maschera non trovata, avvio setup maschera")
 """
    return True


'''
=================== MAIN ==================
'''


def main():
    fps = 0
    frame_count = 0
    start_time = time.time()
    fps_update_interval = 1/3
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
            cv.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                       cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            wserver.print_frame(frame)
        except KeyboardInterrupt:
            logging.info("Interruzione rilevata, chiusura in corso...")
            break


'''
=================== END ==================
'''


def end():
    if vc.isOpened():
        vc.release()
    if wserver:
        wserver.shutdown()


'''
=================== ENTRY POINT ==================
'''

if __name__ == '__main__':
    if setup():
        main()
        end()
    else:
        logging.error("Impossibile inizializzare il programma")
