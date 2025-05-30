const API_BASE_URL = 'http://localhost:5001/api';

export const detectDrowsiness = async (imageData, sessionId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageData,
        sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to detect drowsiness');
    }

    return await response.json();
  } catch (error) {
    console.error('Error detecting drowsiness:', error);
    throw error;
  }
};

export const updateSettings = async (sessionId, settings) => {
  try {
    const response = await fetch(`${API_BASE_URL}/settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sessionId,
        settings,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to update settings');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating settings:', error);
    throw error;
  }
};

export const getSettings = async (sessionId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/settings?sessionId=${sessionId}`);

    if (!response.ok) {
      throw new Error('Failed to get settings');
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting settings:', error);
    throw error;
  }
};

export const resetSession = async (sessionId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to reset session');
    }

    return await response.json();
  } catch (error) {
    console.error('Error resetting session:', error);
    throw error;
  }
}; 