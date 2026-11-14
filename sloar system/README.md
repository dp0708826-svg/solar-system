# Gesture Controlled 3D Solar System

This is an interactive Python application that uses your webcam to capture hand gestures and rotate a stunning 3D Solar System in real-time. It features:
* **The Sun & 8 Planets**: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune.
* **Orbits & Moons**: Rendered orbital path rings and Earth's orbiting Moon.
* **Planet Details**: Saturn's rings with Cassini Division representation and Jupiter's equatorial bands.
* **Realistic Lighting**: Standard OpenGL lighting centered inside the Sun, creating realistic day/night lighting phases on the planets as they orbit.
* **Interactive Navigation**: Gesture rotation, mouse drag fallback, speed adjustments, zoom control, and holographic bounding box toggle.

## Prerequisites

- Python 3.8 or higher
- A webcam connected to your system

## Project Structure

- `main.py`: The main application containing Pygame, PyOpenGL, and MediaPipe logic.
- `requirements.txt`: Python package dependencies.

## Installation

1. Navigate to the project directory:
   ```bash
   cd "d:\sloar system"
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Windows (CMD):
   .\venv\Scripts\activate.bat
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To run the application:
```bash
python main.py
```

### Controls

| Control | Action |
| --- | --- |
| **Index Finger Tip** | Move your index finger in front of the camera to rotate the view. |
| **Left Click & Drag** | Fallback mouse control to rotate the view. |
| **Up/Down Arrows / Mouse Scroll** | Zoom in / out. |
| **Left/Right Arrows** | Rotate view horizontally. |
| **Spacebar** | Pause / Resume the planetary orbits. |
| **`[` and `]`** | Decrease / Increase orbital simulation speed. |
| **`H`** | Toggle the holographic bounding box. |
| **`Q` or `ESC`** | Exit the simulator. |
