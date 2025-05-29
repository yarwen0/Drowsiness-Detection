import React, { useState, useEffect } from 'react';
import './App.css';
import WebcamCapture from './components/WebcamCapture';
import ZenMode from './components/ZenMode';
import logo from './assets/logo.png';

const App = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isZenMode, setIsZenMode] = useState(false);
  const [notification, setNotification] = useState(null);
  const [sessionStartTime] = useState(new Date());

  useEffect(() => {
    // Check system preference for dark mode
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setIsDarkMode(prefersDark);

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e) => setIsDarkMode(e.matches);
    mediaQuery.addEventListener('change', handleChange);

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const handleDrowsinessDetected = () => {
    setNotification({
      type: 'warning',
      message: 'Drowsiness detected! Stay alert!'
    });
    setTimeout(() => setNotification(null), 5000);
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    setNotification({
      type: 'info',
      message: `${!isDarkMode ? 'Dark' : 'Light'} mode activated`
    });
    setTimeout(() => setNotification(null), 3000);
  };

  const toggleZenMode = () => {
    setIsZenMode(!isZenMode);
    setNotification({
      type: 'info',
      message: `Zen mode ${!isZenMode ? 'activated' : 'deactivated'}`
    });
    setTimeout(() => setNotification(null), 3000);
  };

  const getSessionDuration = () => {
    const now = new Date();
    const diff = now - sessionStartTime;
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    return `${hours > 0 ? `${hours}h ` : ''}${minutes}m ${seconds}s`;
  };

  return (
    <div className={`app-container ${isDarkMode ? 'dark-mode' : ''}`}>
      <header className="app-header">
        <div className="app-title">
          <h1>👁️ Stay Alert ⚡</h1>
          <p>Your AI-powered drowsiness detection companion</p>
        </div>
        <div className="header-controls">
          <button
            className={`control-btn ${isDarkMode ? 'active' : ''}`}
            onClick={toggleDarkMode}
            title={`Switch to ${isDarkMode ? 'Light' : 'Dark'} Mode`}
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
          <button
            className={`control-btn ${isZenMode ? 'active' : ''}`}
            onClick={toggleZenMode}
            title={`${isZenMode ? 'Disable' : 'Enable'} Zen Mode`}
          >
            {isZenMode ? '🧘‍♂️' : '🧘‍♀️'}
          </button>
        </div>
      </header>

      <main className="app-main">
        {isZenMode ? (
          <div className="zen-mode">
            <h2>Zen Mode Active</h2>
            <p>Take a moment to breathe and relax...</p>
          </div>
        ) : (
          <WebcamCapture
            onDrowsinessDetected={handleDrowsinessDetected}
            isDarkMode={isDarkMode}
          />
        )}
      </main>

      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.message}
        </div>
      )}

      <footer className="app-footer">
        <div className="session-stats">
          <div className="stat-item">
            <span className="stat-label">Session Duration</span>
            <span className="stat-value">{getSessionDuration()}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Status</span>
            <span className="stat-value">{isZenMode ? 'Zen Mode' : 'Active'}</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App; 