from flask import Flask, Response
from threading import Thread
from werkzeug.serving import make_server
from utils import get_config
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

    def print_frame(self, frame):
        self.frame = frame


def gen_frames(server_thread):
    while True:
        if server_thread.frame is not None:
            ret, buffer = cv.imencode('.jpg', server_thread.frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def start():
    logging.info("Avvio Flask App")
    app = Flask(__name__)

    @app.route('/')
    def home():
        return '<img src="/video_feed" width="640" height="480" />'

    @app.route('/video_feed')
    def video_feed():
        return Response(gen_frames(server),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    web_config = get_config()['WEB']
    server = ServerThread(app, web_config['Host'], web_config['Port'])
    server.start()

    return server
