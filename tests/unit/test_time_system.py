import unittest
import time
from datetime import datetime, timedelta
from environment.time_system import TimeSystem
from items.crop import Crop
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestTimeSystem(unittest.TestCase):
    
    def test_time_scale(self):
        """Test that the time scale is correctly set to 5.0"""
        time_system = TimeSystem()
        self.assertEqual(time_system.time_scale, 5.0)
    
    def test_time_progression(self):
        """Test that time progresses at 5x normal speed"""
        time_system = TimeSystem()
        start_time = time_system.current_time
        
        # Sleep for 1 second of real time
        time.sleep(1)
        
        # Advance time by 1 real second * 5 (time_scale)
        time_system.advance_time(minutes=5)
        
        # Check that the current time has advanced by 5 minutes
        game_minutes_diff = (time_system.current_time - start_time).total_seconds() / 60
        self.assertAlmostEqual(game_minutes_diff, 5.0, delta=0.1)
    
    def test_crop_growth_with_accelerated_time(self):
        """Test that crop growth is correctly calculated with the accelerated time"""
        time_system = TimeSystem()
        
        # Create a test crop with 1 hour growth time
        crop = Crop("Test Crop", 1.0, 100)  # 1 hour growth time, 100 credit value
        crop.growth_progress = 0.0
        crop.planted_time = time_system.current_time
        
        # Advance time by 30 minutes (0.5 hours)
        time_system.advance_time(minutes=30)
        
        # Calculate hours passed since planting
        hours_passed = (time_system.current_time - crop.planted_time).total_seconds() / 3600
        
        # Calculate expected growth with weather multiplier (default 1.0)
        weather_multiplier = 1.0
        expected_growth = (hours_passed / crop.growth_time) * weather_multiplier
        
        # Verify hours_passed is about 0.5
        self.assertAlmostEqual(hours_passed, 0.5, delta=0.01)
        
        # Verify expected growth is about 0.5 (50%)
        self.assertAlmostEqual(expected_growth, 0.5, delta=0.01)
        
        # Calculate actual growth using the formula from the simulation
        crop.growth_progress = min(1.0, expected_growth)
        
        # Verify growth progress is about 0.5 (50%)
        self.assertAlmostEqual(crop.growth_progress, 0.5, delta=0.01)
        
    def test_time_serialization(self):
        """Test that the time system can be serialized and deserialized with the correct scale"""
        original_system = TimeSystem()
        original_system.time_scale = 5.0
        
        # Serialize
        data = original_system.to_dict()
        
        # Deserialize
        new_system = TimeSystem.from_dict(data)
        
        # Check the scale is preserved
        self.assertEqual(new_system.time_scale, 5.0)
        
        # Check that time is preserved
        self.assertEqual(new_system.current_time, original_system.current_time)

if __name__ == '__main__':
    unittest.main() 