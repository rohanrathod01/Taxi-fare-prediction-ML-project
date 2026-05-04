"""
Database initialization and setup script
Run once before starting the app: python -m database.init_db
"""
from database.db import init_db

if __name__ == "__main__":
    print("🚀 Initializing Taxi Fare Prediction Database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
        print("📊 Database created at: backend/taxi_fare.db")
        print("\nNext steps:")
        print("1. Train the ML model: python ml_model/train.py")
        print("2. Start the backend: uvicorn main:app --reload")
        print("3. Run the frontend: npm start (in frontend/)")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
