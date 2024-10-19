import logging
import config as cf
import sys

def logging_setup():
    config = cf.get_config()
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