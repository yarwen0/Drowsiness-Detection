import React, { useEffect, useRef, useState } from 'react';

const ZEN_MUSIC_URLS = [
  'https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0c6ff1bab.mp3',
  'https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73c3a.mp3',
  'https://cdn.pixabay.com/download/audio/2022/01/20/audio_0625c1539a.mp3'
];

const BREATHING_EXERCISES = [
  { name: '4-7-8 Breathing', inhale: 4, hold: 7, exhale: 8 },
  { name: 'Box Breathing', inhale: 4, hold: 4, exhale: 4 },
  { name: 'Deep Breathing', inhale: 5, hold: 2, exhale: 5 }
];

const ZenMode = () => {
  const audioRef = useRef(null);
  const [currentMusicIndex, setCurrentMusicIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [volume, setVolume] = useState(0.5);
  const [currentExercise, setCurrentExercise] = useState(0);
  const [breathingPhase, setBreathingPhase] = useState('inhale');
  const [timer, setTimer] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.volume = volume;
      if (isPlaying) {
        audio.play().catch(error => {
          console.warn('Audio playback failed:', error);
        });
      } else {
        audio.pause();
      }
    }

    return () => {
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
      }
    };
  }, [isPlaying, volume, currentMusicIndex]);

  useEffect(() => {
    let interval;
    if (isPlaying) {
      const exercise = BREATHING_EXERCISES[currentExercise];
      interval = setInterval(() => {
        setTimer(prev => {
          if (prev >= exercise[breathingPhase]) {
            if (breathingPhase === 'inhale') {
              setBreathingPhase('hold');
            } else if (breathingPhase === 'hold') {
              setBreathingPhase('exhale');
            } else {
              setBreathingPhase('inhale');
            }
            return 0;
          }
          return prev + 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, currentExercise, breathingPhase]);

  const nextMusic = () => {
    setCurrentMusicIndex((prev) => (prev + 1) % ZEN_MUSIC_URLS.length);
  };

  const prevMusic = () => {
    setCurrentMusicIndex((prev) => (prev - 1 + ZEN_MUSIC_URLS.length) % ZEN_MUSIC_URLS.length);
  };

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleVolumeChange = (e) => {
    setVolume(parseFloat(e.target.value));
  };

  const nextExercise = () => {
    setCurrentExercise((prev) => (prev + 1) % BREATHING_EXERCISES.length);
    setBreathingPhase('inhale');
    setTimer(0);
  };

  return (
    <div className="zen-mode">
      <audio ref={audioRef} src={ZEN_MUSIC_URLS[currentMusicIndex]} loop />
      
      <div className="zen-content">
        <div className="zen-header">
          <h2>Zen Mode</h2>
          <div className="zen-controls">
            <button onClick={prevMusic} className="zen-control-btn">⏮️</button>
            <button onClick={togglePlayPause} className="zen-control-btn">
              {isPlaying ? '⏸️' : '▶️'}
            </button>
            <button onClick={nextMusic} className="zen-control-btn">⏭️</button>
          </div>
          <div className="volume-control">
            <span>🔈</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={handleVolumeChange}
            />
            <span>🔊</span>
          </div>
        </div>

        <div className="breathing-section">
          <h3>{BREATHING_EXERCISES[currentExercise].name}</h3>
          <div className={`breathing-circle ${breathingPhase}`}>
            <div className="breathing-text">
              {breathingPhase.charAt(0).toUpperCase() + breathingPhase.slice(1)}
              <span className="timer">{timer}</span>
            </div>
          </div>
          <button onClick={nextExercise} className="exercise-btn">
            Next Exercise
          </button>
        </div>

        <div className="zen-tips">
          <h3>Tips for Relaxation</h3>
          <ul>
            <li>Find a comfortable position</li>
            <li>Focus on your breath</li>
            <li>Let your thoughts pass by</li>
            <li>Stay present in the moment</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ZenMode; 