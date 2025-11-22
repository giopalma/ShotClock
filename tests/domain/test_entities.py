"""
Unit tests for domain entities.
These tests demonstrate that domain entities have no external dependencies.
"""
import unittest
from src.domain.entities.ruleset import Ruleset
from src.domain.entities.table_preset import TablePreset
from src.domain.entities.game import Game


class TestRulesetEntity(unittest.TestCase):
    """Test the Ruleset domain entity."""
    
    def test_create_ruleset(self):
        """Test creating a Ruleset entity."""
        ruleset = Ruleset(
            id=1,
            name="Standard",
            initial_duration=600,
            turn_duration=30,
            allarm_time=5,
            increment_duration=10,
            max_increment_for_match=3,
        )
        
        self.assertEqual(ruleset.id, 1)
        self.assertEqual(ruleset.name, "Standard")
        self.assertEqual(ruleset.initial_duration, 600)
        self.assertEqual(ruleset.turn_duration, 30)
        self.assertEqual(ruleset.allarm_time, 5)
        self.assertEqual(ruleset.increment_duration, 10)
        self.assertEqual(ruleset.max_increment_for_match, 3)


class TestTablePresetEntity(unittest.TestCase):
    """Test the TablePreset domain entity."""
    
    def test_create_table_preset(self):
        """Test creating a TablePreset entity."""
        table_preset = TablePreset(
            id=1,
            name="Standard Table",
            points=[(0, 0), (100, 0), (100, 100), (0, 100)],
            colors=[(180, 255, 255)],
            min_area_threshold=100,
        )
        
        self.assertEqual(table_preset.id, 1)
        self.assertEqual(table_preset.name, "Standard Table")
        self.assertEqual(len(table_preset.points), 4)
        self.assertEqual(table_preset.colors[0], (180, 255, 255))
        self.assertEqual(table_preset.min_area_threshold, 100)


class TestGameEntity(unittest.TestCase):
    """Test the Game domain entity."""
    
    def test_create_game(self):
        """Test creating a Game entity."""
        game = Game(
            ruleset_id=1,
            table_preset_id=1,
            player_names=["Player 1", "Player 2"],
            increments=[3, 3],
            status="ready",
            last_remaining_time=0.0,
        )
        
        self.assertEqual(game.ruleset_id, 1)
        self.assertEqual(game.table_preset_id, 1)
        self.assertEqual(game.player_names, ["Player 1", "Player 2"])
        self.assertEqual(game.increments, [3, 3])
        self.assertEqual(game.status, "ready")
        self.assertEqual(game.last_remaining_time, 0.0)
    
    def test_game_default_values(self):
        """Test Game entity with default values."""
        game = Game(
            ruleset_id=1,
            table_preset_id=1,
            player_names=["Player 1", "Player 2"],
            increments=[3, 3],
        )
        
        self.assertEqual(game.status, "ready")
        self.assertEqual(game.last_remaining_time, 0.0)


if __name__ == "__main__":
    unittest.main()
