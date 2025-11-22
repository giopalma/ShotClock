"""
Domain entity for Ruleset.
This is a pure domain model without any external dependencies.
"""
from dataclasses import dataclass


@dataclass
class Ruleset:
    """
    Represents a set of rules for the billiards game.
    
    Attributes:
        id: Unique identifier for the ruleset.
        name: Name of the ruleset.
        initial_duration: Initial game duration in seconds.
        turn_duration: Duration of each turn in seconds.
        allarm_time: Time before end of turn when alarm should activate in seconds.
        increment_duration: Time increment for each turn in seconds.
        max_increment_for_match: Maximum total increment for the match in seconds.
    """
    id: int
    name: str
    initial_duration: int
    turn_duration: int
    allarm_time: int
    increment_duration: int
    max_increment_for_match: int
