from services.google_maps import get_route_info
from services.weather import get_weather
from datetime import datetime
from typing import Dict

def enrich_trip_features(
    pickup_lat: float,
    pickup_lon: float,
    drop_lat: float,
    drop_lon: float,
    passenger_count: int
) -> Dict:
    """
    Enrich trip with all necessary features from external APIs
    Returns a dict with all features needed for ML prediction
    Features: distance(km), duration(min), hour(0-23), day_of_week(0-6), 
              passenger_count(1-6), traffic_level(0-2), weather(0-2), demand_level(0-1)
    """
    
    # Get route info from Google Maps (distance in km, duration in minutes)
    route_info = get_route_info(pickup_lat, pickup_lon, drop_lat, drop_lon)
    distance = route_info["distance"]
    duration = route_info["duration"]
    duration_in_traffic = route_info["duration_in_traffic"]
    
    # Get current time features
    now = datetime.now()
    hour = int(now.hour)
    day_of_week = int(now.weekday())  # 0=Monday, 6=Sunday
    
    # Calculate traffic level (numeric: 0=low, 1=medium, 2=high)
    # Based on actual vs expected duration ratio from Google Maps
    if duration > 0:
        traffic_ratio = duration_in_traffic / duration
    else:
        traffic_ratio = 1.0
    
    # Map traffic ratio to numeric levels
    if traffic_ratio < 1.15:
        traffic_level = 0  # Low traffic
        traffic_label = "Low"
    elif traffic_ratio < 1.35:
        traffic_level = 1  # Medium traffic
        traffic_label = "Medium"
    else:
        traffic_level = 2  # High traffic
        traffic_label = "High"
    
    # Get weather (returns 0, 1, or 2)
    weather_raw = get_weather(pickup_lat, pickup_lon)
    weather_mapping = {"clear": 0, "cloudy": 1, "rain": 2}
    
    if isinstance(weather_raw, str):
        weather = weather_mapping.get(weather_raw.lower(), 0)
        weather_label = weather_raw.title()
    else:
        weather = int(weather_raw)
        weather_labels = {0: "Clear", 1: "Cloudy", 2: "Rain"}
        weather_label = weather_labels.get(weather, "Clear")
    
    # Calculate demand level (numeric: 0=low, 1=high)
    # Peak hours: 7-9 AM, 5-7 PM (high demand)
    if hour in [7, 8, 9, 17, 18, 19, 22, 23]:
        demand_level = 1  # High demand
        demand_label = "High"
    else:
        demand_level = 0  # Low demand
        demand_label = "Low"
    
    # Ensure passenger count is within valid range
    passenger_count = max(1, min(6, int(passenger_count)))
    
    return {
        "distance": round(float(distance), 2),
        "duration": round(float(duration), 2),
        "hour": hour,
        "day_of_week": day_of_week,
        "passenger_count": passenger_count,
        "traffic_level": traffic_level,
        "traffic_label": traffic_label,
        "weather": weather,
        "weather_label": weather_label,
        "demand_level": demand_level,
        "demand_label": demand_label
    }
