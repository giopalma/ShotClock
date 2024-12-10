from . import game_events


def register_socketio_events(socketio):
    game_events.register_events(socketio)
