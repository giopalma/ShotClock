from flask import Response
from flask_restful import Resource
from device.game import game_manager
import json


class GameResource(Resource):
    """
    GameResource è la risorsa REST che rappresenta lo stato corrente della partita in corso.
    """

    def get(self):
        game = game_manager.get_game()
        data = json.dumps(game.__dict__)

        return (data, 200) if game else ({"message": "No game in progress"}, 404)
