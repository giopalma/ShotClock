from threading import Thread
from flask import Flask
from werkzeug.serving import make_server
from config import get_config
import logging
from .routes import main_routes, video_routes, timer_routes, init_routes


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


def start(debug: bool):
    logging.info("Avvio Flask App")
    app = Flask(__name__)
    app.config["DEBUG"] = debug

    # Registra i blueprint
    app.register_blueprint(main_routes)
    app.register_blueprint(video_routes)
    app.register_blueprint(timer_routes)

    web_config = get_config()["WEB"]
    server = ServerThread(app, web_config["Host"], web_config["Port"])

    # Inizializza le routes con il server thread
    init_routes(server)

    server.start()

    return server
