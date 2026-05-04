import React, { useState } from 'react';
import '../styles/LoginPage.css';

function LoginPage({ onLogin }) {
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState('dispatcher@taxi.ai');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = isSignup ? '/auth/signup' : '/auth/login';
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Authentication failed');
        setLoading(false);
        return;
      }

      onLogin(data.access_token, data.user_id);
    } catch (err) {
      setError('Network error. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-hero">
        <div className="hero-content">
          <h1>Predict trips<br />before the<br />meter starts.</h1>
          <p>Select pickup and drop-off on a live map, auto-calculate route conditions, and send a complete fare request to your ML backend.</p>
          <div className="hero-features">
            <div className="feature">
              <span className="feature-icon">✈️</span>
              <span>Real route</span>
            </div>
            <div className="feature">
              <span className="feature-icon">📊</span>
              <span>Traffic level</span>
            </div>
            <div className="feature">
              <span className="feature-icon">☁️</span>
              <span>Weather aware</span>
            </div>
          </div>
        </div>
      </div>

      <div className="login-form-container">
        <div className="login-card">
          <div className="card-header">
            <div className="card-icon">🛡️</div>
            <h2>{isSignup ? 'Create account' : 'Welcome back'}</h2>
            <p>{isSignup ? 'Sign up to start using your taxi fare dashboard.' : 'Sign in to open your taxi fare dashboard.'}</p>
          </div>

          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                minLength={6}
                placeholder={isSignup ? 'Min 6 characters' : ''}
              />
            </div>

            <button 
              type="submit" 
              className="submit-btn"
              disabled={loading}
            >
              {loading ? 'Loading...' : (isSignup ? 'Sign up' : 'Login')}
            </button>
          </form>

          <div className="form-footer">
            {isSignup ? (
              <>
                Already have an account?{' '}
                <button 
                  type="button"
                  className="link-btn"
                  onClick={() => {
                    setIsSignup(false);
                    setError('');
                  }}
                >
                  Log in
                </button>
              </>
            ) : (
              <>
                New dispatcher?{' '}
                <button 
                  type="button"
                  className="link-btn"
                  onClick={() => {
                    setIsSignup(true);
                    setError('');
                  }}
                >
                  Create account
                </button>
              </>
            )}
          </div>

          <div className="session-note">
            Session is saved locally for this frontend demo.
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
