import logging
import time
from flask_socketio import emit, send


def register(socketio):
    @socketio.on("message")
    def on_message(message):
        logging.info(f"Client message: {message}")
        send(f"Echo: {message}")

    @socketio.on("connect")
    def on_connect():
        emit("time_sync", {"server_time": time.time()})
        logging.info("Client connesso")

    @socketio.on("disconnect")
    def on_disconnect():
        logging.info("Client disconnesso")


def ws_event_send(data):
    if "event" in data and "body" in data:
        emit(data["event"], data["body"], broadcast=True)
