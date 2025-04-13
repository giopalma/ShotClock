import argparse
from device.log import logging_setup
from device.config import load_config
from device.test import test
import os

parser = argparse.ArgumentParser(
    prog="ShotClock",
    description="Codice sorgente del dispositivo ShotClock. Il dispositivo gestisce automaticamente il timer di gioco nel gioco del billiardo",
)
parser.add_argument(
    "-d", "--debug", action="store_true", help="Abilita la modalità debug"
)
parser.add_argument(
    "-t", "--test", action="store_true", help="Avvia il dispositivo in modalità test"
)
parser.add_argument(
    "-s", "--static", action="store_true", help="Avvia il dispositivo con frame fisso"
)


def main():
    try:
        import device.api as api

        os.environ["FLASK_ENV"] = "api"
        api.start(debug=args.debug)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    args = parser.parse_args()
    load_config()
    logging_setup()
    if args.test:
        test(static=args.static)
    else:
        main()
