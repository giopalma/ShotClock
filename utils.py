import logging
import os

def get_mask():
    mask_path = '.\\local\\mask.png'
    if not os.path.exists(mask_path):
        logging.error("Impossibile trovare il file {}".format(mask_path))
        return False