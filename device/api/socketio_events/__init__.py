from . import game_events


def register_socketio_events(socketio):
    game_events.register_events(socketio)

    @socketio.on("connect")
    def connected():
        print(socketio.request.sid)
        print("client has connected")
        socketio.emit("connect", {"data": f"id: {socketio.request.sid} is connected"})
