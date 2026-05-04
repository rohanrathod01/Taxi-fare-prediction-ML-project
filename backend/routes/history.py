from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Trip
from utils.security import get_user_id_from_token
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/history", tags=["history"])

class TripResponse(BaseModel):
    id: int
    pickup_lat: float
    pickup_lon: float
    drop_lat: float
    drop_lon: float
    distance: float
    duration: float
    fare: float
    traffic_level: str
    weather: str
    demand_level: str
    timestamp: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[TripResponse])
def get_history(
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """Get user's trip history"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = get_user_id_from_token(authorization)
    
    trips = db.query(Trip).filter(Trip.user_id == user_id).order_by(Trip.timestamp.desc()).all()
    
    return [
        TripResponse(
            id=trip.id,
            pickup_lat=trip.pickup_lat,
            pickup_lon=trip.pickup_lon,
            drop_lat=trip.drop_lat,
            drop_lon=trip.drop_lon,
            distance=trip.distance,
            duration=trip.duration,
            fare=trip.fare,
            traffic_level=trip.traffic_level,
            weather=trip.weather,
            demand_level=trip.demand_level,
            timestamp=trip.timestamp.isoformat()
        )
        for trip in trips
    ]

@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """Get user's trip statistics"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = get_user_id_from_token(authorization)
    
    trips = db.query(Trip).filter(Trip.user_id == user_id).all()
    
    if not trips:
        return {
            "total_trips": 0,
            "total_distance": 0.0,
            "total_spent": 0.0,
            "average_fare": 0.0,
            "average_distance": 0.0
        }
    
    total_distance = sum(trip.distance for trip in trips)
    total_spent = sum(trip.fare for trip in trips)
    
    return {
        "total_trips": len(trips),
        "total_distance": round(total_distance, 2),
        "total_spent": round(total_spent, 2),
        "average_fare": round(total_spent / len(trips), 2),
        "average_distance": round(total_distance / len(trips), 2)
    }
