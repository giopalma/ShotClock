import argparse
from device.log import logging_setup
from device.config import load_config
from device.test import test

# from device.video_producer import VideoProducer

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


def setup():
    import device.api as api

    api_thread = api.run(debug=args.debug)

    try:
        if api_thread:
            api_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    args = parser.parse_args()
    load_config()
    logging_setup()
    if args.test:
        test()
    else:
        setup()
