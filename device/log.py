import logging
from device.config import get_config
import sys


def logging_setup():
    """
    Configurazione iniziale del sistema di logging.
    Il livello di logging è impostato a INFO, e i messaggi vengono stampati su console e su file.
    Il nome del file di log è specificato nel file di configurazione.
    """
    config = get_config()
    formatter = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=formatter,
        filename=config["LOG"]["Filename"],
        filemode="a",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(formatter)
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)
