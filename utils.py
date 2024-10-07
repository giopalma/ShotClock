import configparser
import logging
import sys
import os

config = None


def load_config(config_file='config.ini'):
    global config
    config = configparser.ConfigParser()
    config.read(config_file)


def get_config():
    global config
    if config is None:
        load_config()
    return config


def logging_setup():
    config = get_config()
    formatter = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO,
                        format=formatter,
                        filename=config['LOG']['Filename'],
                        filemode='a')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(formatter)
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)

def get_mask():
    mask_path = '.\\local\\mask.png'
    if not os.path.exists(mask_path):
        logging.error("Impossibile trovare il file {}".format(mask_path))
        return False