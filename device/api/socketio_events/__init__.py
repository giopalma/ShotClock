from . import game_events


def register_socketio_events():
    game_events.register_events()
