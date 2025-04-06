from datetime import datetime, timedelta

class TimeSystem:
    def __init__(self):
        """Initialize the time system"""
        self.current_time = datetime.now()
        self.time_multiplier = 1.0  # 1 real second = 1 game minute
        
    def update(self, real_seconds_passed):
        """Update game time based on real seconds passed"""
        game_minutes = real_seconds_passed * self.time_multiplier
        self.current_time += timedelta(minutes=game_minutes)
        
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
        return {
            "current_time": self.current_time.isoformat(),
            "time_multiplier": self.time_multiplier
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create time system from dictionary data"""
        system = cls()
        system.current_time = datetime.fromisoformat(data["current_time"])
        system.time_multiplier = data["time_multiplier"]
        return system 