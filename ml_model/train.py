"""
ML Model Training Script - Using Real NYC Taxi Data
This script trains a Random Forest model on real taxi trip data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

def load_real_data():
def load_real_data():
    """
    Load real taxi trip data from parquet file.
    NYC Yellow Taxi Trip Records - January 2025
    """
    
    print("\n📥 Loading real taxi trip data...")
    
    # Load parquet file
    file_path = '../yellow_tripdata_2025-01.parquet'
    
    try:
        df = pd.read_parquet(file_path)
    except FileNotFoundError:
        file_path = 'yellow_tripdata_2025-01.parquet'
        df = pd.read_parquet(file_path)
    
    print(f"   Total records: {len(df):,}")
    
    # Calculate trip duration in minutes
    df['duration'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 60
    
    # Extract time features
    df['hour'] = df['tpep_pickup_datetime'].dt.hour
    df['day_of_week'] = df['tpep_pickup_datetime'].dt.dayofweek
    
    # Handle passenger count
    df['passenger_count'] = df['passenger_count'].fillna(1).astype(int)
    df['passenger_count'] = df['passenger_count'].clip(1, 6)
    
    # Distance in km (trip_distance is in miles)
    df['distance'] = df['trip_distance'] * 1.60934
    
    # Estimate traffic level from trip duration vs expected duration
    # Expected at ~15 km/h in light traffic
    df['expected_duration'] = (df['distance'] / 15) * 60  # in minutes
    df['traffic_ratio'] = (df['duration'] / df['expected_duration']).clip(0.5, 3.0)
    df['traffic_level'] = pd.cut(df['traffic_ratio'], bins=[0, 1, 1.5, 3], labels=[0, 1, 2]).astype(int)
    
    # Weather - using simulated weather based on time patterns
    # (In real scenario, would use actual weather API)
    df['weather'] = 0  # Default to clear
    
    # Determine demand level from peak hours
    peak_hours = [7, 8, 9, 17, 18, 19, 22, 23]
    df['demand_level'] = df['hour'].isin(peak_hours).astype(int)
    
    # Use fare_amount as target (in dollars, will convert to INR later in frontend)
    df['fare'] = df['fare_amount']
    
    # Data cleaning
    print("\n🧹 Cleaning data...")
    
    # Remove zero or negative distances
    df = df[df['distance'] > 0]
    print(f"   After removing zero distance: {len(df):,}")
    
    # Remove extreme fares (outliers)
    df = df[(df['fare'] > 2.5) & (df['fare'] < 300)]
    print(f"   After removing fare outliers: {len(df):,}")
    
    # Remove very long trips (likely data errors)
    df = df[df['duration'] < 300]  # Less than 5 hours
    print(f"   After removing long trips: {len(df):,}")
    
    # Remove invalid passenger counts
    df = df[(df['passenger_count'] >= 1) & (df['passenger_count'] <= 6)]
    print(f"   After passenger count filter: {len(df):,}")
    
    return df

def prepare_training_data(df, n_samples=None):
    """
    Prepare features and target for model training.
    """
    
    if n_samples is None:
        n_samples = min(200000, len(df))  # Use up to 200k samples
    
    # Sample data if needed
    if len(df) > n_samples:
        print(f"\n📊 Sampling {n_samples:,} records from {len(df):,} available...")
        df = df.sample(n=n_samples, random_state=42)
    
    # Select features matching the backend service
    features = ['distance', 'duration', 'hour', 'day_of_week', 'passenger_count',
                'traffic_level', 'weather', 'demand_level']
    
    X = df[features].copy()
    y = df['fare'].copy()
    
    # Remove any NaN values
    mask = ~(X.isna().any(axis=1) | y.isna())
    X = X[mask]
    y = y[mask]
    
    print(f"   Training features shape: {X.shape}")
    print(f"   Target shape: {y.shape}")
    
    return X, y

def train_model():
    """Train the Random Forest model on real taxi data."""
    
    print("\n" + "=" * 80)
    print("🚕 TAXI FARE PREDICTION - MODEL TRAINING WITH REAL DATA")
    print("=" * 80)
    
    # Load real data
    df = load_real_data()
    
    # Prepare training data
    print("\n🔧 Preparing training data...")
    X, y = prepare_training_data(df, n_samples=200000)
    
    # Split data
    print("\n📂 Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    print("\n🤖 Training Random Forest model...")
    print("   (This may take 1-2 minutes with real data...)")
    
    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\n" + "=" * 80)
    print("📈 MODEL PERFORMANCE METRICS")
    print("=" * 80)
    
    # Training metrics
    y_train_pred = model.predict(X_train)
    train_r2 = r2_score(y_train, y_train_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    train_mae = mean_absolute_error(y_train, y_train_pred)
    
    # Test metrics
    y_test_pred = model.predict(X_test)
    test_r2 = r2_score(y_test, y_test_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    test_mae = mean_absolute_error(y_test, y_test_pred)
    
    print(f"\n📊 Training Set Performance:")
    print(f"   R² Score:     {train_r2:.6f} (explains {train_r2*100:.2f}% of variance)")
    print(f"   RMSE:         ${train_rmse:.2f}")
    print(f"   MAE:          ${train_mae:.2f}")
    
    print(f"\n✅ Test Set Performance (Unseen Data):")
    print(f"   R² Score:     {test_r2:.6f} (explains {test_r2*100:.2f}% of variance)")
    print(f"   RMSE:         ${test_rmse:.2f}")
    print(f"   MAE:          ${test_mae:.2f}")
    
    # Feature importance
    print("\n" + "=" * 80)
    print("🎯 FEATURE IMPORTANCE (What drives fare predictions)")
    print("=" * 80)
    
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    total_importance = feature_importance['importance'].sum()
    
    print()
    for idx, row in feature_importance.iterrows():
        percentage = (row['importance'] / total_importance) * 100
        bar_length = int(percentage / 2)  # Scale to fit
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"   {row['feature']:20s} {bar} {percentage:5.1f}%")
    
    # Save model
    print("\n" + "=" * 80)
    print("💾 SAVING MODEL")
    print("=" * 80)
    
    model_path = 'model.pkl'
    joblib.dump(model, model_path)
    print(f"\n✅ Model saved to: {model_path}")
    
    # Statistics
    print("\n" + "=" * 80)
    print("📊 TRAINING DATA STATISTICS")
    print("=" * 80)
    
    print(f"\nFare Amount (USD):")
    print(f"   Mean:         ${y.mean():.2f}")
    print(f"   Median:       ${y.median():.2f}")
    print(f"   Min:          ${y.min():.2f}")
    print(f"   Max:          ${y.max():.2f}")
    print(f"   Std Dev:      ${y.std():.2f}")
    
    print(f"\nTrip Distance (km):")
    print(f"   Mean:         {df['distance'].mean():.2f} km")
    print(f"   Median:       {df['distance'].median():.2f} km")
    print(f"   Max:          {df['distance'].max():.2f} km")
    
    print(f"\nTrip Duration:")
    print(f"   Mean:         {df['duration'].mean():.1f} minutes")
    print(f"   Median:       {df['duration'].median():.1f} minutes")
    
    print(f"\nPassenger Count:")
    print(f"   Mean:         {df['passenger_count'].mean():.2f}")
    print(f"   Distribution: {df['passenger_count'].value_counts().to_dict()}")
    
    print(f"\nTraffic Distribution:")
    print(f"   Low (0):      {(df['traffic_level']==0).sum():,} trips ({(df['traffic_level']==0).sum()/len(df)*100:.1f}%)")
    print(f"   Medium (1):   {(df['traffic_level']==1).sum():,} trips ({(df['traffic_level']==1).sum()/len(df)*100:.1f}%)")
    print(f"   High (2):     {(df['traffic_level']==2).sum():,} trips ({(df['traffic_level']==2).sum()/len(df)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ TRAINING COMPLETE!")
    print("=" * 80)

if __name__ == '__main__':
    train_model()
