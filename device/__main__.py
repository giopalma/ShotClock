import argparse
from device.log import logging_setup
from device.config import load_config

parser = argparse.ArgumentParser(
    prog="BilliardTimer",
    description="Codice sorgente del dispositivo BilliardTimer. Il dispositivo gestisce automaticamente il timer di gioco nel gioco del billiardo",
)
parser.add_argument(
    "-d", "--debug", action="store_true", help="Abilita la modalità debug"
)


def setup():
    load_config()
    logging_setup()


if __name__ == "__main__":

    setup()
