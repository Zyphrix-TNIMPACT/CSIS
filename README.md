# CSIS – Cognitive Safety Intelligence System

A semi-functional prototype for an AI-based industrial safety monitoring system using YOLOv8, OpenCV, and Streamlit.

## Features
- **Real-Time Object Detection**: Detects persons and vehicles (simulates missing helmets).
- **Context-Aware Safety Zones**: Identifies if a person enters a designated digital hazard zone.
- **Dynamic Risk Scoring**: Risk rules logic dynamically calculates a score based on proximity and zones.
- **Near-Miss Detection**: Triggers when a person is dangerously close to a vehicle but not colliding.
- **Incident-Aware Emergency Response (IERRE)**: On-dashboard buttons to simulate events like Fall, Fire, or Security Breach.

## Tech Stack
- **Python**: Core programming
- **Ultralytics YOLOv8**: Object detection
- **OpenCV**: Computer vision frame processing
- **Streamlit**: Dashboard and user interface
- **NumPy**: Distance calculations

---

## Installation

1. Make sure you have Python installed (Python 3.8 to 3.11 recommended).
2. Open your terminal or command prompt in this `CSIS` folder.
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

*(Note: The first time you run the system, YOLOv8 will automatically download the `yolov8n.pt` model file, which is about 6MB.)*

## How to Run

1. To start the system, run the main launcher:

```bash
python main.py
```
*(Alternatively, you can run `streamlit run dashboard.py` directly).*

2. The Streamlit dashboard will automatically open in your default browser.
3. In the left sidebar:
   - Select **Webcam** to use your computer's camera.
   - Or select **Sample Video** if you place a `sample.mp4` video file directly inside this `CSIS` folder.
   - Click **Start System**.

## System Interaction
- **Live Video**: Bounding boxes will show Green for persons, Red for persons without helmets, and Blue for vehicles. Red/Green zones denote the Digital Twin boundaries.
- **Simulation Actions**: Use the "Fall", "Fire", and "Theft" buttons in the IERRE panel to simulate events and watch the Incident Log Table update.
- **Risk Evaluation**: Move objects or people in front of the camera (or video) into the Hazard Zone (Red box) to see the risk score visually increase on the metrics panel.
