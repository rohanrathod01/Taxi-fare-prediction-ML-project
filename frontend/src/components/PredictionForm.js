import React, { useState, useEffect } from 'react';

function PredictionForm({ pickupLocation, dropoffLocation, onPrediction, onReset, prediction, loading, disabled }) {
  const [passengers, setPassengers] = useState(1);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [currentTraffic, setCurrentTraffic] = useState('Low');
  const [currentWeather, setCurrentWeather] = useState('Clear');

  // Exchange rate: 1 USD = 83 INR
  const EXCHANGE_RATE = 83;

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);

  // Update traffic and weather based on prediction
  useEffect(() => {
    if (prediction) {
      setCurrentTraffic(prediction.traffic_level || 'Low');
      setCurrentWeather(prediction.weather_label || 'Clear');
    }
  }, [prediction]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (disabled) return;
    onPrediction({ passenger_count: passengers });
  };

  const getTimeString = () => {
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayName = dayNames[currentTime.getDay()];
    const timeStr = currentTime.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
    return `${timeStr} • ${dayName}`;
  };

  return (
    <div className="prediction-section">
      <h3 className="prediction-title">Prediction inputs</h3>

      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label className="input-label">
            <span className="icon">⏰</span>
            Time (Live)
          </label>
          <div className="input-value live-display">
            <span className="live-badge">● LIVE</span>
            <span id="current-time">{getTimeString()}</span>
          </div>
        </div>

        <div className="input-group">
          <label className="input-label">
            <span className="icon">🚗</span>
            Traffic (Live)
          </label>
          <div className="input-value live-display">
            <span className="live-badge">● LIVE</span>
            <span>{currentTraffic}</span>
          </div>
        </div>

        <div className="input-group">
          <label className="input-label">
            <span className="icon">☁️</span>
            Weather (Live)
          </label>
          <div className="input-value live-display">
            <span className="live-badge">● LIVE</span>
            <span>{loading ? 'Fetching...' : currentWeather}</span>
          </div>
        </div>

        <div className="input-group">
          <label className="input-label">
            <span className="icon">👥</span>
            Passengers
          </label>
          <input
            type="number"
            min="1"
            max="6"
            value={passengers}
            onChange={(e) => setPassengers(parseInt(e.target.value))}
            className="input-field"
            disabled={loading}
          />
        </div>

        <button 
          type="submit"
          className="predict-btn"
          disabled={disabled || loading}
        >
          {loading ? '⏳ Predicting...' : '📍 Predict fare'}
        </button>

        <button 
          type="button"
          className="reset-btn"
          onClick={onReset}
          disabled={loading}
        >
          ↺ Reset
        </button>
      </form>

      {prediction && (
        <div className="result-section">
          <div className="result-fare-container">
            <div className="result-fare">₹{prediction.predicted_fare.toLocaleString('en-IN')}</div>
            <div className="result-fare-usd">≈ ${prediction.predicted_fare_usd.toFixed(2)}</div>
          </div>
          <div className="result-explanation">{prediction.explanation}</div>
          
          <div className="result-details">
            <div className="detail-item">
              <div className="detail-label">Distance</div>
              <div className="detail-value">{prediction.distance} km</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Duration</div>
              <div className="detail-value">{Math.round(prediction.duration)} min</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Traffic</div>
              <div className="detail-value">{prediction.traffic_level}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Demand</div>
              <div className="detail-value">{prediction.demand_level}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PredictionForm;
