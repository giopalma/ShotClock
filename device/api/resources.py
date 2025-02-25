from flask import jsonify, request
from flask_restful import Resource
from device.game import game_manager
import json
from device.api import db
from device.api import models_dao
import logging

from device.utils import hex_to_opencv_hsv


class GameResource(Resource):

    def get(self):

        return (
            ({"message": "Game ready"}, 200)
            if game_manager.get_game()
            else ({"message": "No game in progress"}, 404)
        )

    def post(self):
        try:
            if not request.is_json:
                return ({"message": "Missing JSON in request"}, 400)
            data = request.json
            if not all(
                flag in data
                for flag in ("ruleset_id", "table_id", "player1_name", "player2_name")
            ):
                return (
                    {
                        "message": "Missing some required fields: ruleset_id, table_id, player1_name, player2_name"
                    },
                    400,
                )
            ruleset = models_dao.RulesetDao.get(data["ruleset_id"])
            table = models_dao.TablePresetDao.get(data["table_id"])
            table.points = json.loads(table.points)
            table.colors = json.loads(table.colors)
            table.colors = [hex_to_opencv_hsv(color) for color in table.colors]
            if ruleset and table:
                game = game_manager.new_game(
                    ruleset=ruleset,
                    table=table,
                    player1_name=data["player1_name"],
                    player2_name=data["player2_name"],
                )
                return ({"message": "Game created successfully"}, 200)
            else:
                return ({"message": "Ruleset or table not found"}, 404)
        except Exception as e:
            logging.error(e)
            return ({"message": "Internal server error"}, 500)


class GameActionsResource(Resource):
    def post(self):
        # Prendere il request e vedere se c'è un action
        data = None
        if not request.is_json:
            data = request.form
        else:
            data = request.json

        if "action" not in data:
            return ({"message": "Missing 'action' in request"}, 400)

        game = game_manager.get_game()
        if game is None:
            return ({"message": "No game in progress"}, 400)

        action = data["action"].lower()

        if action == "start":
            game.start()
        elif action == "pause":
            game.pause()
        elif action == "resume":
            game.resume()
        elif action == "end":
            game.end()
        else:
            return ({"message": "Invalid action"}, 400)

        return ({"message": f"Action '{action}' performed successfully"}, 200)


class TablePresetResource(Resource):
    def get(self):
        tables = models_dao.TablePresetDao.get_all()
        for table in tables:
            table.colors = json.loads(table.colors)
            table.points = json.loads(table.points)
        return jsonify(tables)

    def post(self):
        if not request.is_json:
            return ({"message": "Missing JSON in request"}, 400)
        data = request.json
        if not all(field in data for field in ("name", "points", "colors")):
            return ({"message": "Missing required fields: name, points, colors"}, 400)
        tablepreset = models_dao.TablePresetDao.create(
            name=data["name"],
            points=data["points"],
            colors=data["colors"],
        )
        return jsonify(tablepreset)


class TablePresetResource2(Resource):
    def delete(self, id):
        if models_dao.RulesetDao.delete(id):
            return ("Ruleset deleted", 200)
        return ("Ruleset not found", 404)


class RulesetResource(Resource):
    def get(self):
        rulesets = models_dao.RulesetDao.get_all()
        return jsonify(rulesets)

    def post(self):
        if not request.is_json:
            return ({"message": "Missing JSON in request"}, 400)
        data = request.json
        ruleset = models_dao.RulesetDao.create(
            name=data["name"],
            initial_duration=data["initial_duration"],
            turn_duration=data["turn_duration"],
            allarm_time=data["allarm_time"],
            increment_duration=data["increment_duration"],
            max_increment_for_match=data["max_increment_for_match"],
        )
        return jsonify(ruleset)

    def delete(self, id):
        if models_dao.RulesetDao.delete(id):
            return ("Ruleset deleted", 200)
        return ("Ruleset not found", 404)


class RulesetResource2(Resource):

    def delete(self, id):
        if models_dao.RulesetDao.delete(id):
            return ("Ruleset deleted", 200)
        return ("Ruleset not found", 404)
