import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaCog, FaEye, FaFaceSmile, FaBell, FaChartLine } from 'react-icons/fa';

const SettingsPanel = ({ settings, onSettingsChange, isOpen, onClose }) => {
  const [localSettings, setLocalSettings] = useState(settings);
  const [activeTab, setActiveTab] = useState('detection');

  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  const handleChange = (key, value) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    onSettingsChange(newSettings);
  };

  const tabs = [
    { id: 'detection', icon: <FaEye />, label: 'Detection' },
    { id: 'display', icon: <FaFaceSmile />, label: 'Display' },
    { id: 'alerts', icon: <FaBell />, label: 'Alerts' },
    { id: 'analytics', icon: <FaChartLine />, label: 'Analytics' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'detection':
        return (
          <div className="settings-section">
            <h3>Detection Settings</h3>
            <div className="setting-item">
              <label>EAR Threshold</label>
              <input
                type="range"
                min="0.1"
                max="0.4"
                step="0.01"
                value={localSettings.ear_threshold}
                onChange={(e) => handleChange('ear_threshold', parseFloat(e.target.value))}
              />
              <span>{localSettings.ear_threshold.toFixed(2)}</span>
            </div>
            <div className="setting-item">
              <label>MAR Threshold</label>
              <input
                type="range"
                min="0.1"
                max="0.5"
                step="0.01"
                value={localSettings.mar_threshold}
                onChange={(e) => handleChange('mar_threshold', parseFloat(e.target.value))}
              />
              <span>{localSettings.mar_threshold.toFixed(2)}</span>
            </div>
            <div className="setting-item">
              <label>Consecutive Frames</label>
              <input
                type="number"
                min="1"
                max="10"
                value={localSettings.consecutive_frames}
                onChange={(e) => handleChange('consecutive_frames', parseInt(e.target.value))}
              />
            </div>
          </div>
        );

      case 'display':
        return (
          <div className="settings-section">
            <h3>Display Settings</h3>
            <div className="setting-item">
              <label>Show Face Box</label>
              <input
                type="checkbox"
                checked={localSettings.show_face_box}
                onChange={(e) => handleChange('show_face_box', e.target.checked)}
              />
            </div>
            <div className="setting-item">
              <label>Show Eye Markers</label>
              <input
                type="checkbox"
                checked={localSettings.show_eye_markers}
                onChange={(e) => handleChange('show_eye_markers', e.target.checked)}
              />
            </div>
            <div className="setting-item">
              <label>Auto Zen Mode</label>
              <input
                type="checkbox"
                checked={localSettings.auto_zen_mode}
                onChange={(e) => handleChange('auto_zen_mode', e.target.checked)}
              />
            </div>
          </div>
        );

      case 'alerts':
        return (
          <div className="settings-section">
            <h3>Alert Settings</h3>
            <div className="setting-item">
              <label>Alert Volume</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={localSettings.alert_volume || 0.5}
                onChange={(e) => handleChange('alert_volume', parseFloat(e.target.value))}
              />
              <span>{((localSettings.alert_volume || 0.5) * 100).toFixed(0)}%</span>
            </div>
            <div className="setting-item">
              <label>Alert Cooldown (seconds)</label>
              <input
                type="number"
                min="1"
                max="60"
                value={localSettings.alert_cooldown || 5}
                onChange={(e) => handleChange('alert_cooldown', parseInt(e.target.value))}
              />
            </div>
          </div>
        );

      case 'analytics':
        return (
          <div className="settings-section">
            <h3>Analytics Settings</h3>
            <div className="setting-item">
              <label>Data Retention (days)</label>
              <input
                type="number"
                min="1"
                max="30"
                value={localSettings.data_retention || 7}
                onChange={(e) => handleChange('data_retention', parseInt(e.target.value))}
              />
            </div>
            <div className="setting-item">
              <label>Export Data</label>
              <button
                className="export-btn"
                onClick={() => {
                  const data = JSON.stringify(localSettings, null, 2);
                  const blob = new Blob([data], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'drowsiness-settings.json';
                  a.click();
                }}
              >
                Download Settings
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="settings-panel"
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 20 }}
        >
          <div className="settings-header">
            <h2>
              <FaCog /> Settings
            </h2>
            <button className="close-btn" onClick={onClose}>
              ×
            </button>
          </div>

          <div className="settings-tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          <div className="settings-content">
            {renderTabContent()}
          </div>

          <div className="settings-footer">
            <button
              className="reset-btn"
              onClick={() => {
                const defaultSettings = {
                  ear_threshold: 0.20,
                  mar_threshold: 0.30,
                  consecutive_frames: 3,
                  show_face_box: true,
                  show_eye_markers: true,
                  auto_zen_mode: false,
                  alert_volume: 0.5,
                  alert_cooldown: 5,
                  data_retention: 7
                };
                setLocalSettings(defaultSettings);
                onSettingsChange(defaultSettings);
              }}
            >
              Reset to Defaults
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default SettingsPanel; 