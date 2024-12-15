from . import game_events


def register_socketio_events(socketio):
    game_events.register_events(socketio)

    @socketio.on("connect")
    def connected():
        print(request.sid)
        print("client has connected")
        emit("connect", {"data": f"id: {request.sid} is connected"})
