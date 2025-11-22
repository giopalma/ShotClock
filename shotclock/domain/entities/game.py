"""
Domain entity for Game.
This is a pure domain model representing the game state.
"""
from dataclasses import dataclass, field
from typing import List, Literal


@dataclass
class Game:
    """
    Represents the game state and metadata.
    
    This is a pure domain entity that contains only the game's data
    and business rules, without any implementation details.
    
    Attributes:
        ruleset_id: ID of the ruleset being used.
        table_preset_id: ID of the table preset being used.
        player_names: Names of the two players.
        increments: Available increments for each player.
        status: Current status of the game.
        last_remaining_time: Last recorded remaining time.
    """
    ruleset_id: int
    table_preset_id: int
    player_names: List[str]
    increments: List[int]
    status: Literal["ready", "running", "waiting", "ended", "paused"] = "ready"
    last_remaining_time: float = 0.0
