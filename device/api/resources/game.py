from flask import Response
from flask_restful import Resource

from device.game.game_manager import game


class GameResource(Resource):
    def get(self):
        return game if game else {"message": "No game in progress"}, 404
