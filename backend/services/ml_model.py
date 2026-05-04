import joblib
import os
from typing import Dict
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../model/model.pkl")

def load_model():
    """Load the ML model"""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"ML model not found at {MODEL_PATH}. "
            "Please run ml_model/train.py first."
        )
    return joblib.load(MODEL_PATH)

def predict_fare(features: Dict) -> float:
    """
    Predict fare using the trained ML model
    For now, using estimate_fare with Indian rates since model is trained on NYC data
    """
    try:
        # For Indian context, use the estimate_fare with local rates
        return estimate_fare(features)
        
        # Original model code commented out
        # model = load_model()
        # ... rest of model code
        
    except Exception as e:
        # Fallback to estimate
        return estimate_fare(features)

def estimate_fare(features: Dict) -> float:
    """
    Fallback fare estimation using a simple formula for Indian taxi fares
    Base fare + distance * rate + time * rate + adjustments
    All in INR
    """
    base_fare = 50.0  # ₹50 base fare
    distance_rate = 25.0  # ₹25 per km
    time_rate = 2.0     # ₹2 per minute
    
    distance_cost = features["distance"] * distance_rate
    time_cost = features["duration"] * time_rate
    
    # Adjustments
    traffic_multiplier = {"low": 1.0, "medium": 1.2, "high": 1.5}.get(
        features["traffic_level"], 1.0
    )
    weather_multiplier = {"clear": 1.0, "cloudy": 1.1, "rain": 1.3}.get(
        features["weather"], 1.0
    )
    demand_multiplier = {"low": 1.0, "high": 1.3}.get(
        features["demand_level"], 1.0
    )
    
    # Passenger surcharge
    passenger_surcharge = (features["passenger_count"] - 1) * 10.0 if features["passenger_count"] > 1 else 0  # ₹10 per extra passenger
    
    fare = (base_fare + distance_cost + time_cost + passenger_surcharge) * traffic_multiplier * weather_multiplier * demand_multiplier
    
    return round(max(20.0, min(2000.0, fare)), 2)
