from device.game import game_manager


# === WEBSOCKET EVENTS ===
# TODO: Da controllare


def register(socketio):
    @socketio.on("start_timer")
    def start_timer():
        socketio.emit("game_update", game_manager.get_game())

    @socketio.on("stop_timer")
    def stop_timer():
        socketio.emit("game_update", game_manager.get_game())

    @socketio.on("reset_timer")
    def reset_timer():
        socketio.emit("game_update", game_manager.get_game())

    @socketio.on("connect")
    def connected():
        print(socketio.request.sid)
        print("client has connected")
        socketio.emit("connect", {"data": f"id: {socketio.request.sid} is connected"})
