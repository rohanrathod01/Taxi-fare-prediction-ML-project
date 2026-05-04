import React, { useRef, useState } from 'react';
import { Wrapper, Status } from '@googlemaps/react-wrapper';

const render = (status) => {
  if (status === Status.LOADING) return <div>Loading map...</div>;
  if (status === Status.FAILURE) return <div>Error loading map</div>;
  return null;
};

function MyMapComponent({ center, zoom, onMapClick, pickupLocation, dropoffLocation }) {
  const ref = useRef();
  const [map, setMap] = useState();

  React.useEffect(() => {
    if (ref.current && !map) {
      setMap(new window.google.maps.Map(ref.current, {
        center,
        zoom,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
      }));
    }
  }, [ref, map, center, zoom]);

  React.useEffect(() => {
    if (map) {
      ['click'].forEach((eventName) =>
        window.google.maps.event.clearListeners(map, eventName)
      );

      if (onMapClick) {
        map.addListener('click', (event) => {
          onMapClick(event.latLng.lat(), event.latLng.lng());
        });
      }
    }
  }, [map, onMapClick]);

  React.useEffect(() => {
    if (map) {
      // Clear existing markers
      const markers = [];
      const bounds = new window.google.maps.LatLngBounds();

      if (pickupLocation) {
        const pickupMarker = new window.google.maps.Marker({
          position: { lat: pickupLocation.lat, lng: pickupLocation.lon },
          map,
          title: 'Pickup Location',
          icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
              <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
                <circle cx="20" cy="20" r="18" fill="#4CAF50" stroke="white" stroke-width="3"/>
                <text x="20" y="25" text-anchor="middle" fill="white" font-size="16" font-weight="bold">P</text>
              </svg>
            `),
            scaledSize: new window.google.maps.Size(40, 40),
          },
        });
        markers.push(pickupMarker);
        bounds.extend(pickupMarker.getPosition());
      }

      if (dropoffLocation) {
        const dropoffMarker = new window.google.maps.Marker({
          position: { lat: dropoffLocation.lat, lng: dropoffLocation.lon },
          map,
          title: 'Drop-off Location',
          icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
              <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
                <circle cx="20" cy="20" r="18" fill="#F44336" stroke="white" stroke-width="3"/>
                <text x="20" y="25" text-anchor="middle" fill="white" font-size="16" font-weight="bold">D</text>
              </svg>
            `),
            scaledSize: new window.google.maps.Size(40, 40),
          },
        });
        markers.push(dropoffMarker);
        bounds.extend(dropoffMarker.getPosition());
      }

      // Fit bounds if we have markers
      if (markers.length > 0) {
        map.fitBounds(bounds);
        if (markers.length === 1) {
          map.setZoom(15);
        }
      }

      return () => {
        markers.forEach(marker => marker.setMap(null));
      };
    }
  }, [map, pickupLocation, dropoffLocation]);

  return <div ref={ref} style={{ height: '400px', width: '100%' }} />;
}

function MapComponent({ pickupLocation, dropoffLocation, onMapClick, mapMode, onModeChange }) {
  const center = { lat: 40.7128, lng: -74.0060 }; // New York City
  const zoom = 12;

  const apiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

  // Calculate distance between two points using Haversine formula
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distance = R * c;
    return distance;
  };

  const getDistanceDisplay = () => {
    if (pickupLocation && dropoffLocation) {
      const distance = calculateDistance(
        pickupLocation.lat, pickupLocation.lon,
        dropoffLocation.lat, dropoffLocation.lon
      );
      return `${distance.toFixed(2)} km`;
    }
    return 'Set locations';
  };

  if (!apiKey) {
    return (
      <div className="map-section">
        <div className="section-title">
          <h2>Select trip route</h2>
          <div className="mode-buttons">
            <button
              className={`mode-btn ${mapMode === 'pickup' ? 'active' : ''}`}
              onClick={() => onModeChange('pickup')}
            >
              Pickup
            </button>
            <button
              className={`mode-btn ${mapMode === 'dropoff' ? 'active' : ''}`}
              onClick={() => onModeChange('dropoff')}
            >
              Drop-off
            </button>
          </div>
        </div>
        <div className="map-container" style={{ background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#666' }}>
          Google Maps API key not configured
        </div>
      </div>
    );
  }

  return (
    <div className="map-section">
      <div className="section-title">
        <h2>Select trip route</h2>
        <div className="mode-buttons">
          <button
            className={`mode-btn ${mapMode === 'pickup' ? 'active' : ''}`}
            onClick={() => onModeChange('pickup')}
          >
            Pickup
          </button>
          <button
            className={`mode-btn ${mapMode === 'dropoff' ? 'active' : ''}`}
            onClick={() => onModeChange('dropoff')}
          >
            Drop-off
          </button>
        </div>
      </div>

      <p style={{ padding: '0 20px', fontSize: '12px', color: '#666' }}>
        Click the map to set {mapMode === 'pickup' ? 'pickup' : 'drop-off'}: the mode switches automatically.
      </p>

      <Wrapper apiKey={apiKey} libraries={['places']} render={render}>
        <MyMapComponent
          center={center}
          zoom={zoom}
          onMapClick={onMapClick}
          pickupLocation={pickupLocation}
          dropoffLocation={dropoffLocation}
        />
      </Wrapper>

      <div className="map-info">
        <div className="info-card">
          <div className="info-label">
            <span className="icon">📍</span>
            Pickup
          </div>
          <div className="info-value">
            {pickupLocation ? `${pickupLocation.lat.toFixed(4)}, ${pickupLocation.lon.toFixed(4)}` : 'Not set'}
          </div>
        </div>
        <div className="info-card">
          <div className="info-label">
            <span className="icon">🏁</span>
            Drop-off
          </div>
          <div className="info-value">
            {dropoffLocation ? `${dropoffLocation.lat.toFixed(4)}, ${dropoffLocation.lon.toFixed(4)}` : 'Not set'}
          </div>
        </div>
        <div className="info-card">
          <div className="info-label">
            <span className="icon">📏</span>
            Distance
          </div>
          <div className="info-value">
            {getDistanceDisplay()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default MapComponent;
