import React, { useState, useEffect, useRef } from 'react';
import MapComponent from '../components/MapComponent';
import PredictionForm from '../components/PredictionForm';
import TripHistory from '../components/TripHistory';
import '../styles/DashboardPage.css';

function DashboardPage({ token, userId, onLogout }) {
  const [pickupLocation, setPickupLocation] = useState(null);
  const [dropoffLocation, setDropoffLocation] = useState(null);
  const [pickupAddress, setPickupAddress] = useState('');
  const [dropoffAddress, setDropoffAddress] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mapMode, setMapMode] = useState('pickup');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [currentWeather, setCurrentWeather] = useState(null);
  const [currentTraffic, setCurrentTraffic] = useState(null);

  const pickupInputRef = useRef(null);
  const dropoffInputRef = useRef(null);

  // Currency settings
  const EXCHANGE_RATE = 83; // 1 USD = 83 INR
  const CURRENCY = 'INR';

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Update time every second for live display
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);

  // Fetch trip history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  // Initialize Google Places Autocomplete
  useEffect(() => {
    const initAutocomplete = () => {
      if (window.google && window.google.maps && window.google.maps.places && pickupInputRef.current && dropoffInputRef.current) {
        const pickupAutocomplete = new window.google.maps.places.Autocomplete(pickupInputRef.current, {
          types: ['geocode'],
          componentRestrictions: { country: 'in' } // Restrict to India
        });
        pickupAutocomplete.addListener('place_changed', () => {
          const place = pickupAutocomplete.getPlace();
          if (place.geometry) {
            const lat = place.geometry.location.lat();
            const lng = place.geometry.location.lng();
            setPickupLocation({ lat, lon: lng });
            setPickupAddress(place.formatted_address);
            setMapMode('dropoff');
          }
        });

        const dropoffAutocomplete = new window.google.maps.places.Autocomplete(dropoffInputRef.current, {
          types: ['geocode'],
          componentRestrictions: { country: 'in' } // Restrict to India
        });
        dropoffAutocomplete.addListener('place_changed', () => {
          const place = dropoffAutocomplete.getPlace();
          if (place.geometry) {
            const lat = place.geometry.location.lat();
            const lng = place.geometry.location.lng();
            setDropoffLocation({ lat, lon: lng });
            setDropoffAddress(place.formatted_address);
          }
        });
      }
    };

    // Check if Google Maps is already loaded
    if (window.google) {
      initAutocomplete();
    } else {
      // Wait for it to load
      const checkGoogle = setInterval(() => {
        if (window.google) {
          clearInterval(checkGoogle);
          initAutocomplete();
        }
      }, 100);
    }
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_URL}/history/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  const handleMapClick = (lat, lon) => {
    if (mapMode === 'pickup') {
      setPickupLocation({ lat, lon });
      reverseGeocode(lat, lon, 'pickup');
      setMapMode('dropoff');
    } else {
      setDropoffLocation({ lat, lon });
      reverseGeocode(lat, lon, 'dropoff');
    }
  };

  const reverseGeocode = (lat, lng, type) => {
    if (window.google && window.google.maps) {
      const geocoder = new window.google.maps.Geocoder();
      geocoder.geocode({ location: { lat, lng } }, (results, status) => {
        if (status === 'OK' && results[0]) {
          if (type === 'pickup') {
            setPickupAddress(results[0].formatted_address);
          } else {
            setDropoffAddress(results[0].formatted_address);
          }
        }
      });
    }
  };

  // Fare is now returned in INR from backend

  const handlePrediction = async (formData) => {
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/predict/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          pickup_lat: pickupLocation.lat,
          pickup_lon: pickupLocation.lon,
          drop_lat: dropoffLocation.lat,
          drop_lon: dropoffLocation.lon,
          passenger_count: formData.passenger_count,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Prediction failed');
        setLoading(false);
        return;
      }

      const convertedPrediction = {
        ...data,
        predicted_fare_usd: data.predicted_fare / EXCHANGE_RATE, // Convert INR back to USD for display
        predicted_fare: data.predicted_fare, // Already in INR
        currency: CURRENCY,
        exchange_rate: EXCHANGE_RATE
      };

      // Also convert history fares if present
      if (convertedPrediction.history) {
        convertedPrediction.history = convertedPrediction.history.map(item => ({
          ...item,
          fare_usd: item.fare / EXCHANGE_RATE, // Convert INR to USD
          fare: item.fare // Already in INR
        }));
      }

      setPrediction(convertedPrediction);
      setCurrentWeather(data.weather);
      setCurrentTraffic(data.traffic_level);
      fetchHistory();
      setLoading(false);
    } catch (err) {
      setError('Network error. Please try again.');
      setLoading(false);
    }
  };

  const handleReset = () => {
    setPickupLocation(null);
    setDropoffLocation(null);
    setPickupAddress('');
    setDropoffAddress('');
    setPrediction(null);
    setMapMode('pickup');
    setError('');
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-left">
          <div className="logo">🚕</div>
          <div className="app-title">
            <h1>Taxi Fare Prediction</h1>
            <p>Route Intelligence Dashboard</p>
          </div>
        </div>
        <div className="header-center">
          <div className="live-info">
            <span className="live-badge">● LIVE</span>
            <span className="current-time">
              {currentTime.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit',
                hour12: true 
              })}
            </span>
            <span className="current-date">
              {currentTime.toLocaleDateString('en-US', { 
                weekday: 'short',
                month: 'short',
                day: 'numeric'
              })}
            </span>
            {currentWeather && <span className="current-weather">Weather: {currentWeather}</span>}
            {currentTraffic && <span className="current-traffic">Traffic: {currentTraffic}</span>}
          </div>
        </div>
        <div className="header-right">
          <span className="user-email">{userId}</span>
          <button className="logout-btn" onClick={onLogout}>
            ↪️ Logout
          </button>
        </div>
      </header>

      <main className="main-content">
        <div className="container">
          <div className="location-inputs-section">
            <h3>Enter Locations</h3>
            <div className="location-inputs">
              <div className="input-group">
                <label htmlFor="pickup-input">Pickup Location</label>
                <input
                  id="pickup-input"
                  ref={pickupInputRef}
                  type="text"
                  placeholder="Enter pickup address"
                  value={pickupAddress}
                  onChange={(e) => setPickupAddress(e.target.value)}
                />
              </div>
              <div className="input-group">
                <label htmlFor="dropoff-input">Drop-off Location</label>
                <input
                  id="dropoff-input"
                  ref={dropoffInputRef}
                  type="text"
                  placeholder="Enter drop-off address"
                  value={dropoffAddress}
                  onChange={(e) => setDropoffAddress(e.target.value)}
                />
              </div>
            </div>
            <p className="input-help">Start typing an address or click on the map below to set locations</p>
          </div>

          <MapComponent 
            pickupLocation={pickupLocation}
            dropoffLocation={dropoffLocation}
            onMapClick={handleMapClick}
            mapMode={mapMode}
            onModeChange={setMapMode}
          />

          <div>
            {error && <div className="error-message">{error}</div>}
            
            <PredictionForm
              pickupLocation={pickupLocation}
              dropoffLocation={dropoffLocation}
              onPrediction={handlePrediction}
              onReset={handleReset}
              prediction={prediction}
              loading={loading}
              disabled={!pickupLocation || !dropoffLocation}
              exchangeRate={EXCHANGE_RATE}
              currency={CURRENCY}
            />

            <TripHistory trips={history} exchangeRate={EXCHANGE_RATE} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default DashboardPage;
