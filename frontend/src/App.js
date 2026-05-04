import React, { useState, useEffect } from 'react';
import './App.css';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Currency settings (can be changed based on locale)
  const EXCHANGE_RATE_USD_TO_INR = 83; // 1 USD = 83 INR (approximately)
  const CURRENCY = 'INR';

  // Update time every second for live display
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);

  // Check if user is already logged in (from localStorage)
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUserId = localStorage.getItem('userId');
    
    if (storedToken && storedUserId) {
      setToken(storedToken);
      setUserId(storedUserId);
      setIsAuthenticated(true);
    }
    
    setLoading(false);
  }, []);

  const handleLogin = (token, userId) => {
    setToken(token);
    setUserId(userId);
    setIsAuthenticated(true);
    localStorage.setItem('token', token);
    localStorage.setItem('userId', userId);
  };

  const handleLogout = () => {
    setToken(null);
    setUserId(null);
    setIsAuthenticated(false);
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="App">
      {!isAuthenticated ? (
        <LoginPage onLogin={handleLogin} />
      ) : (
        <DashboardPage token={token} userId={userId} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;
