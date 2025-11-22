"""
Game Manager Singleton for storing current game state.
This is a simple solution for the example. In production, use proper session management.
"""
from typing import Optional
from src.domain.entities.game import Game


class GameManagerSingleton:
    """
    Singleton to manage the current game state.
    
    Note: This is a simple implementation for demonstration.
    In production, consider:
    - Redis for distributed systems
    - Database session storage
    - User-specific game storage
    """
    
    _instance = None
    _current_game: Optional[Game] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameManagerSingleton, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_current_game(cls) -> Optional[Game]:
        """Get the current game."""
        instance = cls()
        return instance._current_game
    
    @classmethod
    def set_current_game(cls, game: Optional[Game]) -> None:
        """Set the current game."""
        instance = cls()
        instance._current_game = game
    
    @classmethod
    def clear_game(cls) -> None:
        """Clear the current game."""
        instance = cls()
        instance._current_game = None
