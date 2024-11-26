from flask import Blueprint, render_template, Response
from .auth import requires_auth
from .video import gen_frames

main_routes = Blueprint("main", __name__)
video_routes = Blueprint("video", __name__)
timer_routes = Blueprint("timer", __name__)

# Variabile globale per il server thread
server = None


def init_routes(server_thread):
    """
    Inizializza le routes con il server thread
    """
    global server
    server = server_thread


@main_routes.route("/")
@requires_auth
def home():
    return render_template("index.html")


@video_routes.route("/video_feed")
@requires_auth
def video_feed():
    return Response(
        gen_frames(server), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@timer_routes.route("/timer")
@requires_auth
def timer():
    return render_template("timer.html")
