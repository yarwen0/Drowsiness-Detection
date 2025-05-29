# Drowsiness Detection System

A real-time drowsiness detection system using computer vision and machine learning. The system monitors eye movements and facial features to detect signs of drowsiness and alerts the user.

## Features

- Real-time eye tracking and drowsiness detection
- Eye Aspect Ratio (EAR) monitoring
- Visual and audio alerts for drowsiness
- Session statistics and analytics
- Dark mode support
- Responsive design
- Motivational quotes
- Customizable settings

## Tech Stack

### Backend
- Python
- OpenCV
- Flask
- NumPy
- SciPy

### Frontend
- React
- Chart.js
- WebRTC
- CSS3 with animations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/drowsiness-detection.git
cd drowsiness-detection
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

## Usage

1. Start the backend server:
```bash
python app.py
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Open your browser and navigate to `http://localhost:3000`

## Configuration

The system can be configured through the settings panel:
- Detection sensitivity
- Alarm volume
- Graph display
- Face box visualization
- Eye markers
- Auto Zen mode

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenCV for computer vision capabilities
- React community for the frontend framework
- Chart.js for data visualization 