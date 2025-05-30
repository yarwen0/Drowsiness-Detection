class SoundManager {
  constructor() {
    this.alertSound = new Audio('/assets/alert.mp3');
    this.alertSound.volume = 0.5;
    this.isPlaying = false;
    this.lastPlayTime = 0;
    this.cooldown = 3000; // 3 seconds cooldown between alerts
  }

  playAlert() {
    const currentTime = Date.now();
    if (currentTime - this.lastPlayTime < this.cooldown) {
      return;
    }

    if (!this.isPlaying) {
      this.alertSound.currentTime = 0;
      this.alertSound.play()
        .then(() => {
          this.isPlaying = true;
          this.lastPlayTime = currentTime;
        })
        .catch((error) => {
          console.error('Error playing alert sound:', error);
        });

      this.alertSound.onended = () => {
        this.isPlaying = false;
      };
    }
  }

  setVolume(volume) {
    this.alertSound.volume = Math.max(0, Math.min(1, volume));
  }

  setCooldown(cooldown) {
    this.cooldown = Math.max(1000, Math.min(10000, cooldown));
  }
}

export const soundManager = new SoundManager(); 