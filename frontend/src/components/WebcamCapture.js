import React, { useRef, useState, useCallback, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const WebcamCapture = ({ onDrowsinessDetected, isDarkMode }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDrowsy, setIsDrowsy] = useState(false);
  const [detectionCount, setDetectionCount] = useState(0);
  const [consecutiveDrowsyCount, setConsecutiveDrowsyCount] = useState(0);
  const [sessionStartTime] = useState(new Date());
  const [lastAlertTime, setLastAlertTime] = useState(null);
  const [showMotivationalQuote, setShowMotivationalQuote] = useState(false);
  const [currentQuote, setCurrentQuote] = useState('');
  const [stats, setStats] = useState({
    total_drowsiness_events: 0,
    total_blinks: 0,
    average_blink_rate: 0,
    session_duration: 0,
    drowsiness_percentage: 0
  });
  const [showStats, setShowStats] = useState(false);
  const [alertHistory, setAlertHistory] = useState([]);
  const [earHistory, setEarHistory] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    sensitivity: 0.5,
    alarmVolume: 0.7,
    showGraph: true,
    autoZenMode: false,
    showFaceBox: true,
    showEyeMarkers: true
  });
  const [isAnimating, setIsAnimating] = useState(false);
  const [faceBox, setFaceBox] = useState(null);
  const [eyeMarkers, setEyeMarkers] = useState(null);
  const [detectionQuality, setDetectionQuality] = useState('good'); // 'good', 'poor', 'none'

  const alarmSound = useRef(new Audio('/alarm.mp3'));
  alarmSound.current.volume = settings.alarmVolume;

  const captureFrame = useCallback(async () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      try {
        const response = await fetch('http://localhost:5001/api/detect', {
          method: 'POST',
          body: JSON.stringify({
            image: canvas.toDataURL('image/jpeg')
          }),
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        setIsDrowsy(data.is_drowsy);
        setStats(data.stats);
        
        if (data.is_drowsy) {
          setDetectionCount(prev => prev + 1);
          onDrowsinessDetected();
        }
        
        if (data.ear_value) {
          setEarHistory(prev => [...prev, data.ear_value].slice(-50));
          setDetectionQuality('good');
        } else {
          setDetectionQuality('none');
        }

        // Update face box and eye markers if available
        if (data.face_box) {
          setFaceBox(data.face_box);
        }
        if (data.eye_markers) {
          setEyeMarkers(data.eye_markers);
        }
      } catch (err) {
        console.error('Error detecting drowsiness:', err);
        setDetectionQuality('poor');
      }
    }
  }, [onDrowsinessDetected]);

  useEffect(() => {
    let stream = null;
    const startCamera = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          } 
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setIsLoading(false);
        }
      } catch (err) {
        setError('Error accessing camera: ' + err.message);
        setIsLoading(false);
      }
    };

    startCamera();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  useEffect(() => {
    let interval;
    if (!isLoading && !error) {
      interval = setInterval(captureFrame, 100);
    }
    return () => clearInterval(interval);
  }, [isLoading, error, captureFrame]);

  useEffect(() => {
    if (isDrowsy) {
      playAlarm();
      setLastAlertTime(new Date());
      setConsecutiveDrowsyCount(prev => prev + 1);
      
      if (consecutiveDrowsyCount >= 1) {
        showRandomQuote();
      }
      
      setAlertHistory(prev => [...prev, {
        timestamp: new Date(),
        duration: 1
      }]);
    } else {
      stopAlarm();
      setConsecutiveDrowsyCount(0);
    }
  }, [isDrowsy, consecutiveDrowsyCount]);

  const playAlarm = () => {
    if (alarmSound.current) {
      alarmSound.current.currentTime = 0;
      alarmSound.current.play().catch(err => console.error('Error playing alarm:', err));
    }
  };

  const stopAlarm = () => {
    if (alarmSound.current) {
      alarmSound.current.pause();
      alarmSound.current.currentTime = 0;
    }
  };

  const showRandomQuote = () => {
    const quotes = [
      "Stay focused! You're doing great! 💪",
      "Keep your eyes on the prize! 🎯",
      "You've got this! Stay alert! ⚡",
      "Time for a quick stretch? 🧘‍♂️",
      "Take a deep breath and stay awake! 🌬️",
      "Your future self thanks you for staying alert! 🌟",
      "Remember why you started! 🚀",
      "Stay sharp, stay successful! 💫",
      "You're stronger than sleep! 💪",
      "Keep pushing forward! 🎯",
      "Take a short walk to refresh! 🚶‍♂️",
      "Hydrate yourself! 💧",
      "Do some quick exercises! 🏃‍♂️",
      "Focus on your goals! 🎯",
      "You're making progress! 🌟"
    ];
    setCurrentQuote(quotes[Math.floor(Math.random() * quotes.length)]);
    setShowMotivationalQuote(true);
    setIsAnimating(true);
    setTimeout(() => {
      setShowMotivationalQuote(false);
      setIsAnimating(false);
    }, 5000);
  };

  const getSessionDuration = () => {
    const now = new Date();
    const diff = now - sessionStartTime;
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    return `${hours > 0 ? `${hours}h ` : ''}${minutes}m ${seconds}s`;
  };

  const chartData = {
    labels: Array.from({ length: earHistory.length }, (_, i) => i),
    datasets: [
      {
        label: 'Eye Aspect Ratio',
        data: earHistory,
        borderColor: isDrowsy ? '#ff4444' : '#4CAF50',
        tension: 0.4,
        fill: false,
        pointRadius: 0,
        borderWidth: 2
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        max: 0.4,
        grid: {
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          color: isDarkMode ? '#fff' : '#666'
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          display: false
        }
      }
    },
    plugins: {
      legend: {
        display: false
      }
    },
    animation: {
      duration: 0
    }
  };

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`webcam-container ${isDarkMode ? 'dark-mode' : ''}`}>
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Initializing camera...</p>
        </div>
      )}
      
      <div className="video-wrapper">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="webcam-video"
        />
        
        {settings.showFaceBox && faceBox && (
          <div 
            className="face-box"
            style={{
              left: `${faceBox.x}px`,
              top: `${faceBox.y}px`,
              width: `${faceBox.width}px`,
              height: `${faceBox.height}px`
            }}
          />
        )}
        
        {settings.showEyeMarkers && eyeMarkers && eyeMarkers.map((marker, index) => (
          <div
            key={index}
            className="eye-marker"
            style={{
              left: `${marker.x}px`,
              top: `${marker.y}px`
            }}
          />
        ))}
      </div>
      
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      
      {isDrowsy && (
        <div className="drowsy-overlay">
          <div className="drowsy-warning">
            <span className="warning-icon">⚠️</span>
            <span className="warning-text">Stay Alert!</span>
          </div>
        </div>
      )}
      
      {showMotivationalQuote && (
        <div className={`motivational-quote ${isAnimating ? 'animate' : ''}`}>
          {currentQuote}
        </div>
      )}
      
      <div className="detection-quality">
        <span className={`quality-indicator ${detectionQuality}`}>
          {detectionQuality === 'good' ? '✓' : detectionQuality === 'poor' ? '!' : '×'}
        </span>
        <span className="quality-text">
          {detectionQuality === 'good' ? 'Good Detection' : 
           detectionQuality === 'poor' ? 'Poor Detection' : 'No Face Detected'}
        </span>
      </div>
      
      <div className="controls-panel">
        <button 
          className={`control-btn ${showStats ? 'active' : ''}`}
          onClick={() => setShowStats(!showStats)}
          title="Toggle Statistics"
        >
          📊
        </button>
        <button 
          className={`control-btn ${showSettings ? 'active' : ''}`}
          onClick={() => setShowSettings(!showSettings)}
          title="Settings"
        >
          ⚙️
        </button>
      </div>
      
      {showStats && (
        <div className="stats-panel">
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Session Duration</span>
              <span className="stat-value">{getSessionDuration()}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Drowsiness Events</span>
              <span className="stat-value">{stats.total_drowsiness_events}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Blink Rate</span>
              <span className="stat-value">{stats.average_blink_rate.toFixed(1)}/s</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Drowsiness %</span>
              <span className="stat-value">{stats.drowsiness_percentage.toFixed(1)}%</span>
            </div>
          </div>
          
          {settings.showGraph && (
            <div className="graph-container">
              <Line data={chartData} options={chartOptions} />
            </div>
          )}
        </div>
      )}
      
      {showSettings && (
        <div className="settings-panel">
          <h3>Settings</h3>
          <div className="setting-item">
            <label>Detection Sensitivity</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={settings.sensitivity}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                sensitivity: parseFloat(e.target.value)
              }))}
            />
          </div>
          <div className="setting-item">
            <label>Alarm Volume</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={settings.alarmVolume}
              onChange={(e) => {
                const volume = parseFloat(e.target.value);
                setSettings(prev => ({ ...prev, alarmVolume: volume }));
                alarmSound.current.volume = volume;
              }}
            />
          </div>
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.showGraph}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  showGraph: e.target.checked
                }))}
              />
              Show Graph
            </label>
          </div>
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.autoZenMode}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  autoZenMode: e.target.checked
                }))}
              />
              Auto Zen Mode
            </label>
          </div>
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.showFaceBox}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  showFaceBox: e.target.checked
                }))}
              />
              Show Face Box
            </label>
          </div>
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.showEyeMarkers}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  showEyeMarkers: e.target.checked
                }))}
              />
              Show Eye Markers
            </label>
          </div>
        </div>
      )}
    </div>
  );
};

export default WebcamCapture; 