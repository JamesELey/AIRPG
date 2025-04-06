import random
from enum import Enum

class WeatherType(Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"

class WeatherSystem:
    def __init__(self):
        """Initialize the weather system"""
        self.current_weather = WeatherType.SUNNY
        self.weather_duration = 0
        self.update_weather()
        
    def update_weather(self):
        """Update the weather conditions"""
        if self.weather_duration <= 0:
            # Change weather
            weights = {
                WeatherType.SUNNY: 0.4,
                WeatherType.CLOUDY: 0.3,
                WeatherType.RAINY: 0.2,
                WeatherType.STORMY: 0.1
            }
            weather_types = list(weights.keys())
            weather_weights = list(weights.values())
            self.current_weather = random.choices(weather_types, weather_weights)[0]
            self.weather_duration = random.randint(10, 30)  # Duration in minutes
            
    def get_weather_symbol(self):
        """Get the symbol representing current weather"""
        symbols = {
            WeatherType.SUNNY: "☀️",
            WeatherType.CLOUDY: "☁️",
            WeatherType.RAINY: "🌧️",
            WeatherType.STORMY: "⛈️"
        }
        return symbols[self.current_weather]
        
    def get_weather_description(self):
        """Get a description of the current weather"""
        return self.current_weather.value.title()
        
    def get_crop_growth_multiplier(self):
        """Get the crop growth multiplier based on weather"""
        multipliers = {
            WeatherType.SUNNY: 1.2,
            WeatherType.CLOUDY: 1.0,
            WeatherType.RAINY: 1.5,
            WeatherType.STORMY: 0.8
        }
        return multipliers[self.current_weather]
        
    def to_dict(self):
        """Convert weather system state to dictionary"""
        return {
            "current_weather": self.current_weather.value,
            "weather_duration": self.weather_duration
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create weather system from dictionary data"""
        system = cls()
        system.current_weather = WeatherType(data["current_weather"])
        system.weather_duration = data["weather_duration"]
        return system 