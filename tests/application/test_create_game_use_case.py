"""
Unit tests for CreateGameUseCase.
These tests demonstrate how to test application layer in isolation using mocks.
"""
import unittest
from unittest.mock import Mock
from src.application.use_cases.create_game import CreateGameUseCase
from src.domain.entities.ruleset import Ruleset
from src.domain.entities.table_preset import TablePreset


class TestCreateGameUseCase(unittest.TestCase):
    """Test the CreateGameUseCase."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock repositories
        self.mock_ruleset_repo = Mock()
        self.mock_table_preset_repo = Mock()
        
        # Create the use case with mocks
        self.use_case = CreateGameUseCase(
            ruleset_repository=self.mock_ruleset_repo,
            table_preset_repository=self.mock_table_preset_repo,
        )
    
    def test_execute_success(self):
        """Test successful game creation."""
        # Arrange - Set up mock return values
        self.mock_ruleset_repo.get.return_value = Ruleset(
            id=1,
            name="Standard",
            initial_duration=600,
            turn_duration=30,
            allarm_time=5,
            increment_duration=10,
            max_increment_for_match=3,
        )
        
        self.mock_table_preset_repo.get.return_value = TablePreset(
            id=1,
            name="Standard Table",
            points=[(0, 0), (100, 0), (100, 100), (0, 100)],
            colors=[(180, 255, 255)],
            min_area_threshold=100,
        )
        
        # Act - Execute the use case
        game = self.use_case.execute(
            ruleset_id=1,
            table_preset_id=1,
            player1_name="Player 1",
            player2_name="Player 2",
        )
        
        # Assert - Verify the results
        self.assertIsNotNone(game)
        self.assertEqual(game.ruleset_id, 1)
        self.assertEqual(game.table_preset_id, 1)
        self.assertEqual(game.player_names, ["Player 1", "Player 2"])
        self.assertEqual(game.increments, [3, 3])
        self.assertEqual(game.status, "ready")
        
        # Verify repository methods were called
        self.mock_ruleset_repo.get.assert_called_once_with(1)
        self.mock_table_preset_repo.get.assert_called_once_with(1)
    
    def test_execute_invalid_ruleset(self):
        """Test game creation with invalid ruleset."""
        # Arrange - Ruleset not found
        self.mock_ruleset_repo.get.return_value = None
        
        # Act
        game = self.use_case.execute(
            ruleset_id=999,
            table_preset_id=1,
            player1_name="Player 1",
            player2_name="Player 2",
        )
        
        # Assert
        self.assertIsNone(game)
        self.mock_ruleset_repo.get.assert_called_once_with(999)
    
    def test_execute_invalid_table_preset(self):
        """Test game creation with invalid table preset."""
        # Arrange
        self.mock_ruleset_repo.get.return_value = Ruleset(
            id=1,
            name="Standard",
            initial_duration=600,
            turn_duration=30,
            allarm_time=5,
            increment_duration=10,
            max_increment_for_match=3,
        )
        self.mock_table_preset_repo.get.return_value = None
        
        # Act
        game = self.use_case.execute(
            ruleset_id=1,
            table_preset_id=999,
            player1_name="Player 1",
            player2_name="Player 2",
        )
        
        # Assert
        self.assertIsNone(game)
        self.mock_table_preset_repo.get.assert_called_once_with(999)
    
    def test_execute_increments_initialized(self):
        """Test that increments are properly initialized from ruleset."""
        # Arrange
        self.mock_ruleset_repo.get.return_value = Ruleset(
            id=1,
            name="Fast",
            initial_duration=300,
            turn_duration=15,
            allarm_time=3,
            increment_duration=5,
            max_increment_for_match=5,  # Different max increment
        )
        
        self.mock_table_preset_repo.get.return_value = TablePreset(
            id=1,
            name="Standard Table",
            points=[(0, 0), (100, 0), (100, 100), (0, 100)],
            colors=[(180, 255, 255)],
            min_area_threshold=100,
        )
        
        # Act
        game = self.use_case.execute(
            ruleset_id=1,
            table_preset_id=1,
            player1_name="Player 1",
            player2_name="Player 2",
        )
        
        # Assert - Both players should have max_increment_for_match increments
        self.assertEqual(game.increments, [5, 5])


if __name__ == "__main__":
    unittest.main()
