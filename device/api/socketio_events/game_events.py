from device.game import game_manager


def register_events(socketio):
    @socketio.on("start_timer")
    def start_timer():
        socketio.emit("game_update", game_manager.get_game())

    @socketio.on("stop_timer")
    def stop_timer():
        socketio.emit("game_update", game_manager.get_game())

    @socketio.on("reset_timer")
    def reset_timer():
        socketio.emit("game_update", game_manager.get_game())
