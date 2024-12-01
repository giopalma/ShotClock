from ast import arg
import threading
from flask import Flask, render_template
from .resources.video import VideoStreaming
from .resources.game import GameResource
from flask_cors import CORS
from flask_restful import Api

app = Flask(__name__, static_folder="", template_folder="")
api = Api(app)
CORS(app)


api.add_resource(VideoStreaming, "/video")
api.add_resource(GameResource, "/game")


def run(debug=False):
    if not debug:
        api_thread = threading.Thread(target=app.run(debug=debug))
        api_thread.daemon = True
        api_thread.start()
        return api_thread
    app.run(debug=True)
    return None
