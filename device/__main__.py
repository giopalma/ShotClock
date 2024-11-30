import argparse
from device.log import logging_setup
from device.config import load_config
import device.api as api
from device.video import VideoProcessor

parser = argparse.ArgumentParser(
    prog="BilliardTimer",
    description="Codice sorgente del dispositivo BilliardTimer. Il dispositivo gestisce automaticamente il timer di gioco nel gioco del billiardo",
)
parser.add_argument(
    "-d", "--debug", action="store_true", help="Abilita la modalità debug"
)


def setup():
    args = parser.parse_args()
    load_config()
    logging_setup()

    video_processor = VideoProcessor()
    api_thread = api.run(debug=args.debug)

    try:
        if api_thread:
            api_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    setup()
