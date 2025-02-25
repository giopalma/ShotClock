import logging
from flask_socketio import emit, send


def register(socketio):
    @socketio.on("message")
    def on_message(message):
        logging.info(f"Client message: {message}")
        send(f"Echo: {message}")


def ws_event_send(data):
    if "event" in data and "body" in data:
        emit(data["event"], data["body"], broadcast=True)
