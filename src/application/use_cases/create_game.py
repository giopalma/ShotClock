"""
Use case for creating a new game.
This contains the application-specific business logic.
"""
from typing import Optional
from src.domain.entities.game import Game
from src.domain.repositories.ruleset_repository import RulesetRepository
from src.domain.repositories.table_preset_repository import TablePresetRepository


class CreateGameUseCase:
    """
    Use case for creating a new game.
    
    This encapsulates the business logic for creating a game,
    depending only on domain abstractions (repositories).
    """
    
    def __init__(
        self,
        ruleset_repository: RulesetRepository,
        table_preset_repository: TablePresetRepository,
    ):
        self.ruleset_repository = ruleset_repository
        self.table_preset_repository = table_preset_repository
    
    def execute(
        self,
        ruleset_id: int,
        table_preset_id: int,
        player1_name: str,
        player2_name: str,
    ) -> Optional[Game]:
        """
        Create a new game with the specified parameters.
        
        Args:
            ruleset_id: ID of the ruleset to use.
            table_preset_id: ID of the table preset to use.
            player1_name: Name of the first player.
            player2_name: Name of the second player.
            
        Returns:
            A new Game entity if successful, None otherwise.
        """
        # Validate that ruleset and table preset exist
        ruleset = self.ruleset_repository.get(ruleset_id)
        if not ruleset:
            return None
        
        table_preset = self.table_preset_repository.get(table_preset_id)
        if not table_preset:
            return None
        
        # Create the game entity
        game = Game(
            ruleset_id=ruleset_id,
            table_preset_id=table_preset_id,
            player_names=[player1_name, player2_name],
            increments=[
                ruleset.max_increment_for_match,
                ruleset.max_increment_for_match,
            ],
            status="ready",
            last_remaining_time=0.0,
        )
        
        return game
