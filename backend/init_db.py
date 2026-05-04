"""
Database initialization script
Run this once before starting the application to create the database tables
"""
from database.db import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✓ Database initialized successfully!")
    print("Database file created at: backend/taxi_fare.db")
