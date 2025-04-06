class Crop:
    def __init__(self, name, growth_time, value):
        """Initialize a crop"""
        self.name = name
        self.growth_time = growth_time  # Hours to fully grow
        self.value = value  # Base value when harvested
        self.growth_progress = 0.0  # Progress from 0.0 to 1.0
        self.planted_time = None  # Will be set when planted

    def update_growth(self, hours_passed, growth_multiplier=1.0):
        """Update the crop's growth progress"""
        if self.growth_progress < 1.0:
            growth_amount = (hours_passed / self.growth_time) * \
                growth_multiplier
            self.growth_progress = min(
                1.0, self.growth_progress + growth_amount)

    def get_growth_stage(self):
        """Get the appropriate symbol based on growth progress"""
        if self.growth_progress >= 1.0:
            return '🌾'  # Ready to harvest
        elif self.growth_progress >= 0.5:
            return '🌿'  # Growing
        else:
            return '🌱'  # Just planted

    def is_ready_to_harvest(self):
        """Check if the crop is ready to harvest"""
        return self.growth_progress >= 1.0

    def get_value(self):
        """Get the current value of the crop"""
        if not self.is_ready_to_harvest():
            return 0
        return self.value

    def to_dict(self):
        """Convert crop state to a dictionary for saving"""
        return {
            "name": self.name,
            "growth_time": self.growth_time,
            "value": self.value,
            "growth_progress": self.growth_progress,
            "planted_time": self.planted_time.isoformat() if self.planted_time else None
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Crop instance from saved data"""
        crop = cls(data["name"], data["growth_time"], data["value"])
        crop.growth_progress = data["growth_progress"]
        if data["planted_time"]:
            from datetime import datetime
            crop.planted_time = datetime.fromisoformat(data["planted_time"])
        return crop

    @staticmethod
    def get_available_crops():
        """Get a list of all available crop types"""
        return [
            {
                "name": "Tomato",
                "growth_time": 24,
                "value": 50,
                "description": "A juicy red tomato. Grows best in sunny weather."
            },
            {
                "name": "Wheat",
                "growth_time": 48,
                "value": 30,
                "description": "Basic but reliable crop. Moderate weather resistance."
            },
            {
                "name": "Corn",
                "growth_time": 72,
                "value": 75,
                "description": "High-value crop that takes longer to grow."
            },
            {
                "name": "Potato",
                "growth_time": 36,
                "value": 40,
                "description": "Hardy crop that can grow in most weather conditions."
            },
            {
                "name": "Rice",
                "growth_time": 60,
                "value": 60,
                "description": "Grows exceptionally well in rainy weather."
            }
        ]
