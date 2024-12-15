import threading
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_restful import Api

from .resources.video import VideoStreaming
from .resources.game import GameResource
from .socketio_events import register_socketio_events


app = Flask(__name__, static_folder="", template_folder="")
api = Api(app)
CORS(app)
socketio = SocketIO(app)
register_socketio_events(socketio)

api.add_resource(GameResource, "/game")
api.add_resource(VideoStreaming, "/video")


def _server_run(debug):
    socketio.run(app, debug=debug)


# TODO: Vedere besta sta cosa del thread
def run(debug=False):
    if not debug:  # In debug mode, flask deve girare sul main thread
        api_thread = threading.Thread(target=_server_run(debug=debug))
        api_thread.daemon = True
        api_thread.start()
        return api_thread
    _server_run(debug=debug)
    return None
