"""
Repository interface (port) for Ruleset.
This defines the contract that infrastructure adapters must implement.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from shotclock.domain.entities.ruleset import Ruleset


class RulesetRepository(ABC):
    """
    Abstract repository interface for Ruleset entities.
    
    This is a port in the Clean Architecture - it defines what operations
    are available but not how they are implemented.
    """
    
    @abstractmethod
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        """Retrieve a ruleset by its ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Ruleset]:
        """Retrieve all rulesets."""
        pass
    
    @abstractmethod
    def create(
        self,
        name: str,
        initial_duration: int,
        turn_duration: int,
        allarm_time: int,
        increment_duration: int,
        max_increment_for_match: int,
    ) -> Ruleset:
        """Create a new ruleset."""
        pass
    
    @abstractmethod
    def delete(self, ruleset_id: int) -> bool:
        """Delete a ruleset by its ID. Returns True if successful."""
        pass
