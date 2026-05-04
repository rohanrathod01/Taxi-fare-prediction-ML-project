import React from 'react';

function TripHistory({ trips, exchangeRate = 83 }) {
  const convertToINR = (inrAmount) => {
    return inrAmount; // Already in INR
  };

  return (
    <div className="trip-history-section">
      <div className="history-title">
        <span className="icon">⏱️</span>
        Trip History
      </div>

      {trips && trips.length === 0 ? (
        <div className="empty-message">
          Completed predictions will appear here.
        </div>
      ) : (
        <div className="history-list">
          {trips && trips.map((trip) => (
            <div key={trip.id} className="history-item">
              <div className="history-info">
                <div className="history-route">
                  {trip.distance.toFixed(1)} km • {Math.round(trip.duration)} min
                </div>
                <div className="history-timestamp">
                  {new Date(trip.timestamp).toLocaleDateString()} {new Date(trip.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
              <div className="history-fare">
                ₹{convertToINR(trip.fare).toLocaleString('en-IN')}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TripHistory;
