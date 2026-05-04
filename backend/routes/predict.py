from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from database.db import get_db
from database.models import Trip
from services.enrich import enrich_trip_features
from services.ml_model import predict_fare
from services.explanation import explain_fare
from utils.security import get_user_id_from_token

router = APIRouter(prefix="/predict", tags=["predictions"])

class PredictRequest(BaseModel):
    pickup_lat: float
    pickup_lon: float
    drop_lat: float
    drop_lon: float
    passenger_count: int = 1

class PredictResponse(BaseModel):
    predicted_fare: float
    distance: float
    duration: float
    traffic_level: str
    weather: str
    demand_level: str
    explanation: str

@router.post("/", response_model=PredictResponse)
def predict(
    req: PredictRequest,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """Predict taxi fare for a route"""
    
    try:
        # Authenticate user
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        user_id = get_user_id_from_token(authorization)
        
        # Validate input
        if req.passenger_count < 1 or req.passenger_count > 6:
            raise HTTPException(
                status_code=400,
                detail="Passenger count must be between 1 and 6"
            )
        
        # Validate coordinates (basic check)
        if not (-90 <= req.pickup_lat <= 90) or not (-180 <= req.pickup_lon <= 180):
            raise HTTPException(status_code=400, detail="Invalid pickup coordinates")
        if not (-90 <= req.drop_lat <= 90) or not (-180 <= req.drop_lon <= 180):
            raise HTTPException(status_code=400, detail="Invalid drop coordinates")
        
        # Check if pickup and drop are not the same
        if req.pickup_lat == req.drop_lat and req.pickup_lon == req.drop_lon:
            raise HTTPException(status_code=400, detail="Pickup and drop locations cannot be the same")
        
        # Enrich features from external APIs
        features = enrich_trip_features(
            req.pickup_lat,
            req.pickup_lon,
            req.drop_lat,
            req.drop_lon,
            req.passenger_count
        )
        
        # Predict fare
        fare = predict_fare(features)
        
        # Generate explanation
        explanation = explain_fare(features)
        
        # Store trip in database
        trip = Trip(
            user_id=user_id,
            pickup_lat=req.pickup_lat,
            pickup_lon=req.pickup_lon,
            drop_lat=req.drop_lat,
            drop_lon=req.drop_lon,
            distance=features["distance"],
            duration=features["duration"],
            fare=fare,
            traffic_level=features["traffic_level"],
            weather=features["weather"],
            demand_level=features["demand_level"],
            timestamp=datetime.now()
        )
        db.add(trip)
        db.commit()
        
        return PredictResponse(
            predicted_fare=fare,
            distance=features["distance"],
            duration=features["duration"],
            traffic_level=features["traffic_label"],
            weather=features["weather_label"],
            demand_level=features["demand_label"],
            explanation=explanation
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
