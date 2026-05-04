import requests
import os
from typing import Dict

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "demo-key")

def get_weather(lat: float, lon: float) -> str:
    """
    Get weather condition from OpenWeatherMap API
    Falls back to simulated data if API key is demo or invalid
    """
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        )
        
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if resp.status_code != 200 or "weather" not in data:
            # Return simulated weather
            return _simulate_weather(lat, lon)
        
        weather = data["weather"][0]["main"].lower()
        return _categorize_weather(weather)
    except Exception as e:
        print(f"Weather API error: {e}. Using simulated data.")
        return _simulate_weather(lat, lon)

def _simulate_weather(lat: float, lon: float) -> str:
    """Simulate weather based on location"""
    import random
    # Simulate weather with higher probability for clear
    rand = random.random()
    if rand < 0.7:
        return "clear"
    elif rand < 0.9:
        return "cloudy"
    else:
        return "rain"

def _categorize_weather(weather: str) -> str:
    """Categorize weather into clear, cloudy, or rain"""
    weather_lower = weather.lower()
    
    if "rain" in weather_lower or "drizzle" in weather_lower or "thunderstorm" in weather_lower:
        return "rain"
    elif "cloud" in weather_lower or "overcast" in weather_lower:
        return "cloudy"
    elif "snow" in weather_lower:
        return "rain"  # Treat snow as heavy weather
    else:
        return "clear"
