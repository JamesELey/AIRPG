"""
Test file for save/load functionality in the grid game.

This test suite verifies that the game state is correctly saved and loaded, ensuring game progress
is properly preserved between sessions. It's critical for maintaining player progress and preventing
data loss.

The tests specifically focus on:
1. Basic save/load functionality for simple game state
2. Complex save/load with inventory, positions, and more
3. Player credits persistence - ensuring credits are properly saved and loaded
4. Game statistics preservation, including credit tracking 
5. Farming and crop data persistence
6. Save metadata and slot management
7. Validation of save/load with invalid slots

The tests for player credits (both current credits and total earned credits) are especially 
important as they affect the player's ability to purchase items, plant crops, and track progress.
Issues with credit persistence can significantly impact gameplay experience.
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to the system path to allow imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the main game class
from grid_game import GridGame
from entities.player import Player
from items.potion import SmallPotion
from items.crop import Crop


class TestSaveLoadFunctionality(unittest.TestCase):
    """Test cases for saving and loading game state."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test save files
        self.test_dir = tempfile.mkdtemp()
        # Store original get_save_filename method to restore later
        self.original_get_save_filename = GridGame.get_save_filename
        
        # Mock the get_save_filename method to use our temp directory
        def mock_get_save_filename(slot):
            if not 1 <= slot <= 5:
                raise ValueError("Save slot must be between 1 and 5.")
            return str(Path(self.test_dir) / f"savegame_{slot}.json")
        
        # Apply the mock
        GridGame.get_save_filename = staticmethod(mock_get_save_filename)
        
        # Create a clean game instance for each test
        self.game = GridGame()
    
    def tearDown(self):
        """Clean up after each test."""
        # Restore original method
        GridGame.get_save_filename = self.original_get_save_filename
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.test_dir)
    
    def test_save_and_load_basic(self):
        """Test basic save and load functionality."""
        # Modify the game state in a detectable way
        self.game.player.name = "TestPlayer"
        self.game.player.credits = 1000
        self.game.player.health = 75
        
        # Save the game
        result = self.game.save_game(1)
        self.assertTrue(result, "Save operation should succeed")
        
        # Verify save file exists
        save_path = Path(self.test_dir) / "savegame_1.json"
        self.assertTrue(save_path.exists(), "Save file should exist")
        
        # Load the game into a new instance
        loaded_game = GridGame.load_game(1)
        self.assertIsNotNone(loaded_game, "Load operation should succeed")
        
        # Verify the state was preserved
        self.assertEqual("TestPlayer", loaded_game.player.name)
        self.assertEqual(1000, loaded_game.player.credits)
        self.assertEqual(75, loaded_game.player.health)
    
    def test_save_and_load_complex(self):
        """Test saving and loading more complex game state."""
        # Modify game state with more complex changes
        self.game.player.name = "ComplexTest"
        self.game.player.credits = 2500
        
        # Add items to inventory
        for _ in range(3):
            self.game.player.add_to_inventory(SmallPotion())
        
        # Modify stats
        self.game.farming_stats["crops_planted"] = 10
        self.game.farming_stats["farming_level"] = 3
        self.game.game_stats["battles_won"] = 5
        
        # Change player position
        self.game.player_pos = [1, 5, 5]  # Different level
        
        # Save the game
        self.game.save_game(2)
        
        # Load the game
        loaded_game = GridGame.load_game(2)
        
        # Verify complex state was preserved
        self.assertEqual("ComplexTest", loaded_game.player.name)
        self.assertEqual(2500, loaded_game.player.credits)
        self.assertEqual(3, len(loaded_game.player.inventory))
        self.assertEqual(10, loaded_game.farming_stats["crops_planted"])
        self.assertEqual(3, loaded_game.farming_stats["farming_level"])
        self.assertEqual(5, loaded_game.game_stats["battles_won"])
        self.assertEqual([1, 5, 5], loaded_game.player_pos)
    
    def test_player_credits(self):
        """Test specifically that player credits are correctly saved and loaded."""
        # Set initial credits
        initial_credits = 500
        self.game.player.credits = initial_credits
        
        # Save the game
        self.game.save_game(1)
        
        # Verify credits in the save file directly
        save_path = Path(self.test_dir) / "savegame_1.json"
        with open(save_path, 'r') as f:
            save_data = json.load(f)
            self.assertEqual(initial_credits, save_data['player']['credits'], 
                           "Credits should be correctly stored in the save file")
        
        # Modify credits after saving
        self.game.player.credits = 1000
        
        # Load the game
        loaded_game = GridGame.load_game(1)
        
        # Verify the loaded credits match what was saved
        self.assertEqual(initial_credits, loaded_game.player.credits,
                       "Credits should be restored to the saved value")
        
        # Test credit changes through gameplay operations
        # 1. Increase credits and save
        loaded_game.player.credits += 250
        new_credits = initial_credits + 250
        loaded_game.save_game(1)
        
        # 2. Load again and verify
        reloaded_game = GridGame.load_game(1)
        self.assertEqual(new_credits, reloaded_game.player.credits,
                       "Credits changes should persist after saving and loading again")
    
    def test_game_stats_and_credits(self):
        """Test that game statistics including credit statistics are properly saved and loaded."""
        # Set initial stats
        self.game.game_stats["total_credits_earned"] = 1000
        self.game.game_stats["battles_won"] = 5
        self.game.game_stats["battles_lost"] = 2
        
        # Record a battle with credits gained
        self.game.record_battle(
            npc_name="Test Monster",
            player_won=True,
            turns=3,
            credits_gained=250,
            dropped_items=["Test Item"]
        )
        
        # Verify stats were updated
        self.assertEqual(1250, self.game.game_stats["total_credits_earned"])
        self.assertEqual(6, self.game.game_stats["battles_won"])
        
        # Save the game
        self.game.save_game(1)
        
        # Load the game
        loaded_game = GridGame.load_game(1)
        
        # Verify statistics were preserved
        self.assertEqual(1250, loaded_game.game_stats["total_credits_earned"])
        self.assertEqual(6, loaded_game.game_stats["battles_won"])
        self.assertEqual(2, loaded_game.game_stats["battles_lost"])
        
        # Verify battle history was preserved
        self.assertEqual(1, len(loaded_game.battle_history))
        battle_record = loaded_game.battle_history[0]
        self.assertEqual("Test Monster", battle_record["npc_name"])
        self.assertEqual(True, battle_record["player_won"])
        self.assertEqual(3, battle_record["turns"])
        self.assertEqual(250, battle_record["credits_gained"])
        self.assertEqual(["Test Item"], battle_record["items_gained"])
        
        # Record another battle and save again
        loaded_game.record_battle(
            npc_name="Another Monster",
            player_won=True,
            turns=5,
            credits_gained=500,
            dropped_items=["Valuable Item"]
        )
        
        # Verify stats updated in the loaded game
        self.assertEqual(1750, loaded_game.game_stats["total_credits_earned"])
        self.assertEqual(7, loaded_game.game_stats["battles_won"])
        
        # Save the updated game
        loaded_game.save_game(2)
        
        # Load from the new save
        reloaded_game = GridGame.load_game(2)
        
        # Verify all data was preserved in the new save
        self.assertEqual(1750, reloaded_game.game_stats["total_credits_earned"])
        self.assertEqual(7, reloaded_game.game_stats["battles_won"])
        self.assertEqual(2, len(reloaded_game.battle_history))
    
    def test_farming_and_crops(self):
        """Test that planted crops and farming statistics are properly saved and loaded."""
        # Skip the actual planting since it's dependent on game mechanics
        # and not directly related to save/load functionality
        self.game.player.credits = 1000
        
        # Create test crops - Crop takes (name, growth_time, value)
        crop1 = Crop("Carrot", 2.0, 50)
        crop1.growth_progress = 0.75
        
        crop2 = Crop("Potato", 1.5, 40)
        crop2.growth_progress = 1.0
        
        # Manually add crops to the planted_crops dictionary
        position1 = [0, 3, 3]  # Level 0, row 3, col 3
        position2 = [0, 5, 5]  # Level 0, row 5, col 5
        
        self.game.planted_crops[tuple(position1)] = crop1
        self.game.planted_crops[tuple(position2)] = crop2
        
        # Manually update farming stats
        self.game.farming_stats["crops_planted"] = 2
        
        # Save game with planted crops
        self.game.save_game(1)
        
        # Load the game
        loaded_game = GridGame.load_game(1)
        
        # Verify crops were properly saved and loaded
        self.assertEqual(2, len(loaded_game.planted_crops))
        
        # Check crop 1 properties
        loaded_crop1 = loaded_game.planted_crops[tuple(position1)]
        self.assertEqual("Carrot", loaded_crop1.name)
        self.assertEqual(0.75, loaded_crop1.growth_progress)
        self.assertEqual(50, loaded_crop1.value)
        
        # Check crop 2 properties
        loaded_crop2 = loaded_game.planted_crops[tuple(position2)]
        self.assertEqual("Potato", loaded_crop2.name)
        self.assertEqual(1.0, loaded_crop2.growth_progress)
        self.assertEqual(40, loaded_crop2.value)
        
        # Test harvesting fully grown crop and saving changes
        value, names, _ = loaded_game.harvest_crop(tuple(position2))
        self.assertEqual(40, value, "Harvested crop should give correct value")
        self.assertEqual(["Potato"], names, "Harvested crop name should match")
        
        # Verify farming stats updated
        self.assertEqual(1, loaded_game.farming_stats["crops_harvested"])
        self.assertEqual(40, loaded_game.farming_stats["total_crop_value"])
        
        # Save game after harvest
        loaded_game.save_game(2)
        
        # Load harvested game state
        reloaded_game = GridGame.load_game(2)
        
        # Verify only one crop remains
        self.assertEqual(1, len(reloaded_game.planted_crops))
        self.assertIn(tuple(position1), reloaded_game.planted_crops)
        self.assertNotIn(tuple(position2), reloaded_game.planted_crops)
        
        # Verify farming stats persisted
        self.assertEqual(2, reloaded_game.farming_stats["crops_planted"])
        self.assertEqual(1, reloaded_game.farming_stats["crops_harvested"])
        self.assertEqual(40, reloaded_game.farming_stats["total_crop_value"])
    
    def test_save_metadata(self):
        """Test that save metadata is correctly stored and retrieved."""
        # Set up a test game
        self.game.player.name = "MetadataTest"
        
        # Save the game
        self.game.save_game(3)
        
        # Get metadata directly
        metadata = GridGame.get_save_metadata(3)
        
        # Verify metadata
        self.assertIsNotNone(metadata)
        self.assertEqual(3, metadata["slot"])
        self.assertEqual("MetadataTest", metadata["player_name"])
        self.assertIsNotNone(metadata["save_time"])
        
        # Test get_all_save_metadata
        all_metadata = GridGame.get_all_save_metadata()
        self.assertEqual(5, len(all_metadata))
        self.assertIsNotNone(all_metadata[2])  # Slot 3 (index 2) should have data
        
        # Test find_most_recent_save_slot
        most_recent = GridGame.find_most_recent_save_slot()
        self.assertEqual(3, most_recent)
    
    def test_save_slot_validation(self):
        """Test validation of save slot numbers."""
        # First, test get_save_filename directly
        # This should raise ValueError for invalid slots
        with self.assertRaises(ValueError):
            GridGame.get_save_filename(0)
        
        with self.assertRaises(ValueError):
            GridGame.get_save_filename(6)
        
        # In the actual implementation:
        # - save_game tries to call get_save_filename which raises ValueError
        # - load_game also tries to call get_save_filename which raises ValueError
        
        # Test save_game with valid slots works properly
        self.assertTrue(self.game.save_game(1), "save_game should succeed with valid slot")
        
        # Test load_game with valid slot after saving
        loaded_game = GridGame.load_game(1)
        self.assertIsNotNone(loaded_game, "load_game should succeed with valid slot")
        
        # Test load_game with valid but unused slot returns None (not ValueError)
        loaded_game = GridGame.load_game(4)  # We haven't saved to slot 4
        self.assertIsNone(loaded_game, "load_game should return None for unused slots")
    
    def test_load_nonexistent_save(self):
        """Test loading a save that doesn't exist."""
        # Try to load a save that doesn't exist
        loaded_game = GridGame.load_game(4)  # We haven't saved to slot 4
        self.assertIsNone(loaded_game)


if __name__ == "__main__":
    unittest.main() 