from datetime import datetime, timedelta


class TimeSystem:
    def __init__(self):
        """Initialize the time system"""
        self.current_time = datetime.now()
        self.time_scale = 1.0  # 1 real second = 1 game minute by default
        self.daytime_start = 6  # 6 AM
        self.daytime_end = 20   # 8 PM

    def advance_time(self, minutes=0, hours=0, days=0):
        """Advance game time by the specified amount"""
        delta = timedelta(minutes=minutes, hours=hours, days=days)
        self.current_time += delta

    def set_time(self, hour=None, minute=None):
        """Set the current time to a specific hour and minute"""
        if hour is not None:
            self.current_time = self.current_time.replace(hour=hour)
        if minute is not None:
            self.current_time = self.current_time.replace(minute=minute)

    def is_daytime(self):
        """Check if it's currently daytime"""
        current_hour = self.current_time.hour
        return self.daytime_start <= current_hour < self.daytime_end

    def get_time_of_day(self):
        """Get a description of the current time of day"""
        hour = self.current_time.hour
        if 5 <= hour < 8:
            return "Dawn"
        elif 8 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 14:
            return "Noon"
        elif 14 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 20:
            return "Evening"
        elif 20 <= hour < 22:
            return "Dusk"
        else:
            return "Night"

    def to_dict(self):
        """Convert time system state to a dictionary for saving"""
        return {
            "current_time": self.current_time.isoformat(),
            "time_scale": self.time_scale,
            "daytime_start": self.daytime_start,
            "daytime_end": self.daytime_end
        }

    @classmethod
    def from_dict(cls, data):
        """Create a TimeSystem instance from saved data"""
        time_system = cls()
        time_system.current_time = datetime.fromisoformat(data["current_time"])
        time_system.time_scale = data["time_scale"]
        time_system.daytime_start = data["daytime_start"]
        time_system.daytime_end = data["daytime_end"]
        return time_system
