from functools import wraps
import os
from flask import Flask, Response, render_template, request
from threading import Thread
from werkzeug.serving import make_server
from config import get_config
import logging
import cv2 as cv


class ServerThread(Thread):
    def __init__(self, app, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.frame = None
        self.server = make_server(host, port, app, threaded=True)
        self.server.timeout = 1  # Timeout di 1 secondo
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        logging.info("Avvio Web Server  {}:{}".format(self.host, self.port))
        self.server.serve_forever()

    def shutdown(self):
        logging.info("Arresto Web Server...")
        self.server.shutdown()
        self.server.server_close()
        self.join()

    def set_frame(self, frame):
        self.frame = frame


def gen_frames(server_thread):
    while True:
        if server_thread.frame is not None:
            _, buffer = cv.imencode(".jpg", server_thread.frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


def check_auth(username, password):
    config = get_config()
    return (
        username == config["WEB"]["Username"] and password == config["WEB"]["Password"]
    )


def http_basic_auth():
    return Response(
        "Could not verify your access level for that URL.\n"
        "You have to login with proper credentials",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return http_basic_auth()
        return f(*args, **kwargs)

    return decorated


def start(debug:bool):
    logging.info("Avvio Flask App")
    app = Flask(__name__)
    app.config["DEBUG"] = debug

    @app.route("/")
    @requires_auth
    def home():
        return render_template("index.html")
        # return '<img src="/video_feed" width="640" height="480" />'

    @app.route("/video_feed")
    @requires_auth
    def video_feed():
        return Response(
            gen_frames(server), mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    @app.route("/timer")
    @requires_auth
    def timer():
        return render_template("timer.html")

    web_config = get_config()["WEB"]
    server = ServerThread(app, web_config["Host"], web_config["Port"])
    server.start()

    return server
