from device.game.game_manager import game


def register_events(socketio):
    @socketio.on("start_timer")
    def start_timer():
        socketio.emit("game_update", game)

    @socketio.on("stop_timer")
    def stop_timer():
        socketio.emit("game_update", game)

    @socketio.on("reset_timer")
    def reset_timer():
        socketio.emit("game_update", game)
