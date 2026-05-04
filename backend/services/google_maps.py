import requests
import os
from typing import Tuple, Dict

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "demo-key")

def get_route_info(pickup_lat: float, pickup_lon: float, drop_lat: float, drop_lon: float) -> Dict:
    """
    Get distance, duration, and duration_in_traffic from Google Maps API
    Falls back to simulated data if API key is demo or invalid
    """
    try:
        url = (
            f"https://maps.googleapis.com/maps/api/directions/json?"
            f"origin={pickup_lat},{pickup_lon}&destination={drop_lat},{drop_lon}"
            f"&key={GOOGLE_API_KEY}&departure_time=now"
        )
        
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if resp.status_code != 200 or not data.get("routes"):
            # Return simulated data for demo
            return _simulate_route_data(pickup_lat, pickup_lon, drop_lat, drop_lon)
        
        leg = data["routes"][0]["legs"][0]
        distance = leg["distance"]["value"] / 1000  # km
        duration = leg["duration"]["value"] / 60    # minutes
        duration_in_traffic = leg.get("duration_in_traffic", leg["duration"])["value"] / 60
        
        return {
            "distance": round(distance, 2),
            "duration": round(duration, 2),
            "duration_in_traffic": round(duration_in_traffic, 2)
        }
    except Exception as e:
        print(f"Google Maps API error: {e}. Using simulated data.")
        return _simulate_route_data(pickup_lat, pickup_lon, drop_lat, drop_lon)

def _simulate_route_data(pickup_lat: float, pickup_lon: float, drop_lat: float, drop_lon: float) -> Dict:
    """Simulate route data using haversine distance"""
    import math
    
    # Haversine formula to calculate distance
    R = 6371  # Earth's radius in km
    lat1, lon1 = math.radians(pickup_lat), math.radians(pickup_lon)
    lat2, lon2 = math.radians(drop_lat), math.radians(drop_lon)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    # Simulate duration (approx 15-20 km/h average in city)
    duration = distance / 0.27  # approx 15 km/h
    duration_in_traffic = duration * 1.3  # Simulate 30% traffic factor
    
    return {
        "distance": round(max(distance, 0.5), 2),
        "duration": round(max(duration, 5), 2),
        "duration_in_traffic": round(max(duration_in_traffic, 5), 2)
    }
