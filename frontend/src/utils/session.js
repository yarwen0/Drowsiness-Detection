import { v4 as uuidv4 } from 'uuid';

const SESSION_KEY = 'drowsiness_detection_session';
const SETTINGS_KEY = 'drowsiness_detection_settings';

export const defaultSettings = {
  earThreshold: 0.25,
  marThreshold: 0.5,
  consecutiveFrames: 3,
  showFaceBox: true,
  showEyeMarkers: true,
  autoZenMode: false,
  alertVolume: 0.5,
  alertCooldown: 3000,
  dataRetention: 100,
};

export const createSession = () => {
  const sessionId = uuidv4();
  const session = {
    id: sessionId,
    startTime: Date.now(),
    settings: { ...defaultSettings },
  };

  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(defaultSettings));

  return session;
};

export const getSession = () => {
  const sessionData = localStorage.getItem(SESSION_KEY);
  if (!sessionData) {
    return createSession();
  }

  return JSON.parse(sessionData);
};

export const updateSessionSettings = (settings) => {
  const session = getSession();
  session.settings = { ...session.settings, ...settings };
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  return session;
};

export const getSessionSettings = () => {
  const settingsData = localStorage.getItem(SETTINGS_KEY);
  if (!settingsData) {
    return defaultSettings;
  }

  return JSON.parse(settingsData);
};

export const resetSession = () => {
  const session = getSession();
  session.startTime = Date.now();
  session.settings = { ...defaultSettings };
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(defaultSettings));
  return session;
};

export const exportSessionData = (sessionData) => {
  const dataStr = JSON.stringify(sessionData, null, 2);
  const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
  
  const exportFileDefaultName = `drowsiness-session-${Date.now()}.json`;
  
  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();
}; 