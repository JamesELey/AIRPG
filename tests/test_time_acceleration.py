#!/usr/bin/env python
"""
Test script to demonstrate accelerated time and crop growth.
This script simulates game operation with the 5x time multiplier.
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Import after setting up path
from environment.time_system import TimeSystem
from items.crop import Crop
from environment.weather import Weather

def simulate_crop_growth():
    """Simulate crop growth with accelerated time"""
    logging.info("Starting time acceleration simulation")
    
    # Initialize time system with 5x multiplier
    time_system = TimeSystem()
    time_system.time_scale = 5.0  # Set to 5x faster
    weather = Weather()
    
    # Create test crops with different growth times
    crops = [
        {"name": "Fast Crop", "growth_time": 1.0, "value": 50},     # 1 hour growth
        {"name": "Medium Crop", "growth_time": 2.0, "value": 100},  # 2 hours growth
        {"name": "Slow Crop", "growth_time": 4.0, "value": 200}     # 4 hours growth
    ]
    
    planted_crops = {}
    for i, crop_data in enumerate(crops):
        crop = Crop(crop_data["name"], crop_data["growth_time"], crop_data["value"])
        crop.growth_progress = 0.0
        crop.planted_time = time_system.current_time  # Set planting time
        planted_crops[i] = crop
        logging.info(f"Planted {crop.name} (Growth time: {crop.growth_time}h)")
    
    # Simulate time passing and crop growth for 60 seconds
    start_time = time.time()
    simulation_duration = 60  # seconds
    check_interval = 5       # Check every 5 seconds
    
    logging.info(f"Simulation will run for {simulation_duration} seconds with checks every {check_interval} seconds")
    logging.info(f"With 5x time multiplier, this is equivalent to {simulation_duration * 5 / 60:.1f} game hours")
    
    # Print initial state
    logging.info(f"Initial time: {time_system.current_time.strftime('%I:%M %p')}")
    logging.info("Initial crop progress:")
    for i, crop in planted_crops.items():
        logging.info(f"  {crop.name}: {crop.growth_progress * 100:.1f}% grown")
    
    # Run simulation loop
    elapsed = 0
    while elapsed < simulation_duration:
        time.sleep(check_interval)
        elapsed = time.time() - start_time
        
        # Advance game time based on real seconds passed
        real_seconds_passed = check_interval
        game_minutes = real_seconds_passed * time_system.time_scale
        time_system.advance_time(minutes=game_minutes)
        
        logging.info(f"Advanced time by {game_minutes:.1f} minutes (game time)")
        
        # Get weather multiplier
        weather_multiplier = weather.get_crop_growth_multiplier()
        
        # Update crop growth for each crop
        for i, crop in planted_crops.items():
            old_progress = crop.growth_progress
            if crop.growth_progress < 1.0:
                # Calculate hours passed since planting
                hours_passed = (time_system.current_time - crop.planted_time).total_seconds() / 3600
                
                # Update growth based on total hours and growth time
                growth_progress = (hours_passed / crop.growth_time) * weather_multiplier
                crop.growth_progress = min(1.0, growth_progress)
                
                logging.info(f"  {crop.name} grew: {old_progress * 100:.1f}% -> {crop.growth_progress * 100:.1f}%")
        
        # Log current game time
        logging.info(f"Current time: {time_system.current_time.strftime('%I:%M %p')} (after {elapsed:.1f}s real time)")
        
        # Check which crops are ready
        ready_crops = [crop.name for crop in planted_crops.values() if crop.growth_progress >= 1.0]
        if ready_crops:
            logging.info(f"Crops ready to harvest: {', '.join(ready_crops)}")
    
    # Show final state
    logging.info("Simulation complete")
    logging.info(f"Final time: {time_system.current_time.strftime('%I:%M %p')}")
    logging.info("Final crop growth status:")
    for i, crop in planted_crops.items():
        status = "READY TO HARVEST" if crop.growth_progress >= 1.0 else f"{crop.growth_progress * 100:.1f}% grown"
        logging.info(f"  {crop.name}: {status}")
    
    # Calculate total advancement
    total_game_minutes = simulation_duration * time_system.time_scale
    logging.info(f"Time advanced by {total_game_minutes:.1f} game minutes ({total_game_minutes/60:.1f} game hours)")

if __name__ == "__main__":
    simulate_crop_growth() 