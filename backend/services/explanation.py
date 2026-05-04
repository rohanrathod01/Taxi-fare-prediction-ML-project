from typing import Dict

def explain_fare(features: Dict) -> str:
    """
    Generate a human-readable explanation for the predicted fare
    Based on traffic, weather, and demand factors
    """
    reasons = []
    
    # Check traffic level
    if features["traffic_level"] == "high":
        reasons.append("heavy traffic on this route")
    elif features["traffic_level"] == "medium":
        reasons.append("moderate traffic conditions")
    
    # Check weather
    if features["weather"] == "rain":
        reasons.append("adverse weather conditions")
    elif features["weather"] == "cloudy":
        reasons.append("cloudy weather")
    
    # Check demand level
    if features["demand_level"] == "high":
        reasons.append("high demand (peak hours)")
    
    # Check distance
    if features["distance"] > 10:
        reasons.append(f"long distance ({features['distance']} km)")
    
    # Check passenger count
    if features["passenger_count"] > 1:
        reasons.append(f"{features['passenger_count']} passengers")
    
    # Generate explanation
    if reasons:
        explanation = "Fare is determined by: " + ", ".join(reasons)
    else:
        explanation = "Fare is based on standard pricing for this route and time"
    
    return explanation

def get_fare_factors(features: Dict) -> Dict:
    """Get detailed fare factors for display"""
    return {
        "distance": f"{features['distance']} km",
        "duration": f"{features['duration']:.0f} min",
        "traffic": features["traffic_level"],
        "weather": features["weather"],
        "demand": features["demand_level"],
        "passengers": features["passenger_count"]
    }
