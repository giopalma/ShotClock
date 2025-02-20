import argparse
from device.log import logging_setup
from device.config import load_config
import device.api as api
from device.video_producer import VideoProducer

parser = argparse.ArgumentParser(
    prog="ShotClock",
    description="Codice sorgente del dispositivo ShotClock. Il dispositivo gestisce automaticamente il timer di gioco nel gioco del billiardo",
)
parser.add_argument(
    "-d", "--debug", action="store_true", help="Abilita la modalità debug"
)

def setup():
    args = parser.parse_args()
    load_config()
    logging_setup()
    VideoProducer()

    api_thread = api.run(debug=args.debug)

    try:
        if api_thread:
            api_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    setup()
