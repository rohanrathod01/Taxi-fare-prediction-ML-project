from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import User
from utils.security import hash_password, verify_password, create_jwt_token

router = APIRouter(prefix="/auth", tags=["authentication"])

class UserSignup(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int

@router.post("/signup", response_model=Token)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    """Create a new user account"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please login instead."
        )
    
    # Validate password length
    if len(user.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters long"
        )
    
    # Create new user
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate token
    token = create_jwt_token(db_user.id)
    
    return {
        "access_token": token,
        "user_id": db_user.id
    }

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password"""
    
    # Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Generate token
    token = create_jwt_token(db_user.id)
    
    return {
        "access_token": token,
        "user_id": db_user.id
    }

@router.get("/me")
def get_current_user(authorization: str = None, db: Session = Depends(get_db)):
    """Get current user information"""
    from utils.security import get_user_id_from_token
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = get_user_id_from_token(authorization)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }
