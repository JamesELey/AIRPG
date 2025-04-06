from datetime import datetime, timedelta
import logging

class TimeSystem:
    def __init__(self):
        """Initialize the time system"""
        self.current_time = datetime.now()
        self.time_multiplier = 5.0  # 1 real second = 5 game minutes
        self.last_update_time = datetime.now()  # Add tracking for real-time updates
        logging.info(f"[TimeSystem] Initialized with time: {self.current_time.strftime('%I:%M %p')}, multiplier: {self.time_multiplier}")
        
    def update(self, real_seconds_passed):
        """Update game time based on real seconds passed"""
        game_minutes = real_seconds_passed * self.time_multiplier
        old_time = self.current_time
        self.current_time += timedelta(minutes=game_minutes)
        logging.debug(f"[TimeSystem] Updated time: {old_time.strftime('%I:%M %p')} -> {self.current_time.strftime('%I:%M %p')} (+{game_minutes:.1f} game minutes)")
        self.last_update_time = datetime.now()
        
    def get_time_delta_in_hours(self):
        """Calculate time passed since last update in game hours"""
        # Calculate real seconds passed since last update
        real_seconds = (datetime.now() - self.last_update_time).total_seconds()
        # Convert to game minutes based on multiplier
        game_minutes = real_seconds * self.time_multiplier
        # Convert to game hours
        game_hours = game_minutes / 60.0
        
        logging.debug(f"[TimeSystem] Time delta: {real_seconds:.1f} real seconds = {game_hours:.2f} game hours")
        
        # Update the last update time and current game time
        self.update(real_seconds)
        
        return game_hours
        
    def get_time_of_day(self):
        """Get the current time of day (morning, afternoon, evening, night)"""
        hour = self.current_time.hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"
            
    def to_dict(self):
        """Convert time system state to dictionary"""
        data = {
            "current_time": self.current_time.isoformat(),
            "time_multiplier": self.time_multiplier
        }
        logging.debug(f"[TimeSystem] Saving state: time={self.current_time.strftime('%I:%M %p')}, multiplier={self.time_multiplier}")
        return data
        
    @classmethod
    def from_dict(cls, data):
        """Create time system from dictionary data"""
        system = cls()
        system.current_time = datetime.fromisoformat(data["current_time"])
        system.time_multiplier = data.get("time_multiplier", 1.0)  # Use default 1.0 if missing
        system.last_update_time = datetime.now()  # Reset the update time on load
        logging.info(f"[TimeSystem] Loaded from save: time={system.current_time.strftime('%I:%M %p')}, multiplier={system.time_multiplier}")
        return system 