from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from pathlib import Path

# Database setup
DATABASE_DIR = Path(__file__).parent.parent
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/taxi_fare.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from database.models import Base
    Base.metadata.create_all(bind=engine)
