from enum import Enum
import random


class WeatherType(Enum):
    SUNNY = "☀️"
    CLOUDY = "☁️"
    RAIN = "🌧️"
    STORM = "⛈️"
    SNOW = "❄️"


class Weather:
    def __init__(self):
        """Initialize the weather system"""
        self.current_weather = WeatherType.SUNNY
        self.weather_duration = 0  # Hours until next weather change
        self.weather_effects = {
            WeatherType.SUNNY: {
                "crop_growth": 1.2,
                "description": "The sun shines brightly, perfect for crop growth."
            },
            WeatherType.CLOUDY: {
                "crop_growth": 1.0,
                "description": "Clouds fill the sky, providing moderate growing conditions."
            },
            WeatherType.RAIN: {
                "crop_growth": 1.5,
                "description": "Rain falls steadily, greatly benefiting the crops."
            },
            WeatherType.STORM: {
                "crop_growth": 0.5,
                "description": "A fierce storm rages, potentially damaging crops."
            },
            WeatherType.SNOW: {
                "crop_growth": 0.2,
                "description": "Snow covers the ground, severely limiting crop growth."
            }
        }

    def set_weather(self, weather_type):
        """Set the current weather"""
        if isinstance(weather_type, WeatherType):
            self.current_weather = weather_type
            self.weather_duration = random.randint(
                4, 12)  # Weather lasts 4-12 hours

    def update_weather(self, hours_passed):
        """Update weather based on time passed"""
        self.weather_duration -= hours_passed
        if self.weather_duration <= 0:
            self._generate_new_weather()

    def _generate_new_weather(self):
        """Generate new random weather"""
        # Weather chances (out of 100)
        chances = {
            WeatherType.SUNNY: 40,
            WeatherType.CLOUDY: 30,
            WeatherType.RAIN: 20,
            WeatherType.STORM: 7,
            WeatherType.SNOW: 3
        }

        # Generate random number and determine weather
        roll = random.randint(1, 100)
        cumulative = 0
        for weather, chance in chances.items():
            cumulative += chance
            if roll <= cumulative:
                self.set_weather(weather)
                break

    def get_crop_growth_multiplier(self):
        """Get the current weather's effect on crop growth"""
        return self.weather_effects[self.current_weather]["crop_growth"]

    def get_weather_description(self):
        """Get a description of the current weather"""
        return self.weather_effects[self.current_weather]["description"]

    def get_weather_symbol(self):
        """Get the symbol for the current weather"""
        return self.current_weather.value

    def to_dict(self):
        """Convert weather state to a dictionary for saving"""
        return {
            "current_weather": self.current_weather.name,
            "weather_duration": self.weather_duration
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Weather instance from saved data"""
        weather = cls()
        weather.current_weather = WeatherType[data["current_weather"]]
        weather.weather_duration = data["weather_duration"]
        return weather
