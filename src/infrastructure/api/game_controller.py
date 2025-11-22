"""
Game API Controller using Clean Architecture.
This is an example of how to integrate the new architecture with Flask.
"""
from flask import request, jsonify
from flask_restful import Resource
from src.infrastructure.di_container import DIContainer
from src.domain.entities.game import Game
from src.infrastructure.api.game_manager_singleton import GameManagerSingleton


class GameController(Resource):
    """
    Flask-RESTful Resource for Game operations.
    
    This controller demonstrates how to use the Clean Architecture
    use cases within a Flask API endpoint.
    """
    
    def __init__(self, container: DIContainer):
        """
        Initialize the controller with the DI container.
        
        Args:
            container: Dependency Injection Container
        """
        self.container = container
        self.create_game_use_case = container.get_create_game_use_case()
        self.manage_game_use_case = container.get_manage_game_use_case()
        self.game_manager = GameManagerSingleton()
    
    def post(self):
        """
        Create a new game.
        
        Expected JSON body:
        {
            "ruleset_id": 1,
            "table_preset_id": 1,
            "player1_name": "Player 1",
            "player2_name": "Player 2"
        }
        """
        data = request.get_json()
        
        # Validate input
        required_fields = ["ruleset_id", "table_preset_id", "player1_name", "player2_name"]
        if not all(field in data for field in required_fields):
            return {"error": "Missing required fields"}, 400
        
        # Execute use case
        game = self.create_game_use_case.execute(
            ruleset_id=data["ruleset_id"],
            table_preset_id=data["table_preset_id"],
            player1_name=data["player1_name"],
            player2_name=data["player2_name"],
        )
        
        if not game:
            return {"error": "Failed to create game. Invalid ruleset or table preset."}, 400
        
        # Store current game
        self.game_manager.set_current_game(game)
        
        return {
            "message": "Game created successfully",
            "game": {
                "status": game.status,
                "player_names": game.player_names,
                "increments": game.increments,
            }
        }, 201
    
    def get(self):
        """
        Get current game status.
        """
        game = self.game_manager.get_current_game()
        if not game:
            return {"error": "No game in progress"}, 404
        
        return {
            "status": game.status,
            "player_names": game.player_names,
            "increments": game.increments,
            "last_remaining_time": game.last_remaining_time,
        }, 200
    
    def delete(self):
        """
        End the current game.
        """
        game = self.game_manager.get_current_game()
        if not game:
            return {"error": "No game in progress"}, 404
        
        error = self.manage_game_use_case.end_game(game)
        if error:
            return {"error": error}, 400
        
        self.game_manager.clear_game()
        return {"message": "Game ended successfully"}, 200


class GameActionsController(Resource):
    """
    Controller for game actions (start, pause, resume, increment).
    """
    
    def __init__(self, container: DIContainer):
        """
        Initialize the controller.
        
        Args:
            container: Dependency Injection Container
        """
        self.container = container
        self.game_manager = GameManagerSingleton()
        self.manage_game_use_case = container.get_manage_game_use_case()
    
    def post(self):
        """
        Execute a game action.
        
        Expected JSON body:
        {
            "action": "start" | "pause" | "resume" | "increment",
            "player": 0 | 1  // Only for increment action
        }
        """
        data = request.get_json()
        
        if not data or "action" not in data:
            return {"error": "Action is required"}, 400
        
        game = self.game_manager.get_current_game()
        if not game:
            return {"error": "No game in progress"}, 404
        
        action = data["action"]
        
        if action == "start":
            error = self.manage_game_use_case.start_game(game)
            if error:
                return {"error": error}, 400
            return {"message": "Game started"}, 200
        
        elif action == "pause":
            error = self.manage_game_use_case.pause_game(game)
            if error:
                return {"error": error}, 400
            return {"message": "Game paused"}, 200
        
        elif action == "resume":
            error = self.manage_game_use_case.resume_game(game)
            if error:
                return {"error": error}, 400
            return {"message": "Game resumed"}, 200
        
        elif action == "increment":
            if "player" not in data:
                return {"error": "Player index is required for increment action"}, 400
            
            player = data["player"]
            if player not in [0, 1]:
                return {"error": "Player must be 0 or 1"}, 400
            
            error = self.manage_game_use_case.increment_time(game, player)
            if error:
                return {"error": error}, 400
            return {"message": f"Time incremented for player {player}"}, 200
        
        else:
            return {"error": f"Unknown action: {action}"}, 400
