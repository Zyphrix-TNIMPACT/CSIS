from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import cv2
import asyncio
import json
import base64
import numpy as np
from datetime import datetime
import os
from typing import List
import threading

from detection import detection_engine
from database import (
    add_user, verify_user, log_incident, log_risk_score,
    save_safety_zone, get_safety_zones, get_recent_incidents, get_analytics_data
)
from voice_alerts import voice_system

app = FastAPI(title="CSIS Backend API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variables
active_connections: List[WebSocket] = []
video_sources = {}  # camera_id: video_source
processing_active = {}  # camera_id: bool
hazard_zones = {}  # camera_id: [zones]
last_alerts = {}  # camera_id: last_alert_time
user_language = 'english'  # Default language

class VideoProcessor:
    def __init__(self, camera_id, source):
        self.camera_id = camera_id
        self.source = source
        self.cap = None
        self.is_running = False
        
    def start(self):
        """Start video processing"""
        if self.source == 0:  # Webcam
            self.cap = cv2.VideoCapture(0)
        elif os.path.exists(self.source):  # Video file
            self.cap = cv2.VideoCapture(self.source)
        else:
            print(f"❌ Invalid video source: {self.source}")
            return False
        
        if not self.cap.isOpened():
            print(f"❌ Failed to open video source: {self.source}")
            return False
        
        self.is_running = True
        print(f"✅ Video processor started for camera {self.camera_id}")
        return True
    
    def stop(self):
        """Stop video processing"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        print(f"🛑 Video processor stopped for camera {self.camera_id}")
    
    def get_frame(self):
        """Get next frame"""
        if not self.cap or not self.is_running:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            # Loop video if it's a file
            if self.source != 0:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
            
            if not ret:
                return None
        
        return frame

async def broadcast_update(data):
    """Broadcast update to all connected WebSocket clients"""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        active_connections.remove(conn)

async def process_camera_feed(camera_id, processor):
    """Process camera feed and send updates"""
    frame_count = 0
    last_risk_log_time = datetime.now()
    
    while processor.is_running:
        try:
            frame = processor.get_frame()
            if frame is None:
                await asyncio.sleep(0.1)
                continue
            
            # Process every 15 frames (0.5 seconds at 30fps)
            frame_count += 1
            if frame_count % 15 != 0:
                await asyncio.sleep(0.033)  # ~30fps
                continue
            
            # Detect objects
            detections = detection_engine.detect_objects(frame)
            
            # Get hazard zones for this camera
            zones = hazard_zones.get(camera_id, [])
            
            # Calculate risk
            risk_info = detection_engine.calculate_risk_score(detections, zones)
            
            # Draw annotations
            annotated_frame = detection_engine.draw_detections(frame, detections, risk_info, zones)
            
            # Encode frame to base64
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Prepare update data
            update_data = {
                'type': 'camera_update',
                'camera_id': camera_id,
                'risk_score': risk_info['risk_score'],
                'severity': risk_info['severity'],
                'workers_count': risk_info['workers_count'],
                'vehicles_count': risk_info['vehicles_count'],
                'incidents': risk_info['incidents'],
                'frame': frame_base64,
                'timestamp': datetime.now().isoformat()
            }
            
            # Broadcast update
            await broadcast_update(update_data)
            
            # Log risk score every 5 seconds
            if (datetime.now() - last_risk_log_time).seconds >= 5:
                log_risk_score(camera_id, risk_info['risk_score'], 
                             risk_info['workers_count'], risk_info['vehicles_count'])
                last_risk_log_time = datetime.now()
            
            # Check for incidents and trigger alerts
            if risk_info['incidents']:
                await handle_incidents(camera_id, risk_info)
            
            await asyncio.sleep(0.5)  # Process every 0.5 seconds
            
        except Exception as e:
            print(f"❌ Error processing camera {camera_id}: {e}")
            await asyncio.sleep(1)

async def handle_incidents(camera_id, risk_info):
    """Handle detected incidents"""
    global last_alerts
    
    current_time = datetime.now()
    
    # Avoid duplicate alerts within 10 seconds
    if camera_id in last_alerts:
        if (current_time - last_alerts[camera_id]).seconds < 10:
            return
    
    last_alerts[camera_id] = current_time
    
    for incident in risk_info['incidents']:
        incident_type = incident['type']
        severity = incident['severity']
        
        # Log to database
        incident_id = log_incident(
            camera_id=camera_id,
            camera_name=f"Camera {camera_id}",
            incident_type=incident_type,
            severity=severity,
            risk_score=risk_info['risk_score'],
            details=incident
        )
        
        # Trigger voice alert for critical incidents
        if risk_info['risk_score'] >= 61:  # High or Critical
            alert_type = incident_type
            if alert_type == 'near_miss':
                voice_system.announce('near_miss', user_language)
            elif alert_type == 'zone_violation':
                voice_system.announce('zone_violation', user_language)
            elif alert_type == 'worker_fall':
                voice_system.announce('fall', user_language)
        
        # Broadcast alert
        alert_data = {
            'type': 'alert',
            'camera_id': camera_id,
            'incident_type': incident_type,
            'severity': severity,
            'risk_score': risk_info['risk_score'],
            'message': get_alert_message(incident_type),
            'timestamp': current_time.isoformat()
        }
        await broadcast_update(alert_data)

def get_alert_message(incident_type):
    """Get alert message for incident type"""
    messages = {
        'near_miss': 'Worker detected near moving vehicle',
        'zone_violation': 'Worker entered restricted zone',
        'worker_fall': 'Worker fall detected',
        'no_helmet': 'Worker without helmet detected',
        'fire': 'Fire detected',
        'collision': 'Vehicle collision detected',
        'theft': 'Suspicious activity detected'
    }
    return messages.get(incident_type, 'Incident detected')

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 CSIS Backend Server Starting...")
    print(f"📊 Detection Engine: {detection_engine.device}")
    print("✅ Server ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down...")
    for camera_id, processor in video_sources.items():
        processor.stop()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    print(f"✅ WebSocket connected. Total connections: {len(active_connections)}")
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total connections: {len(active_connections)}")

@app.post("/api/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """User login"""
    result = verify_user(username, password)
    if result:
        user_id, phone_number = result
        return {
            'success': True,
            'user_id': user_id,
            'username': username,
            'phone_number': phone_number
        }
    return {'success': False, 'message': 'Invalid credentials'}

@app.post("/api/auth/register")
async def register(username: str = Form(...), password: str = Form(...), phone_number: str = Form(None)):
    """User registration"""
    success = add_user(username, password, phone_number)
    if success:
        return {'success': True, 'message': 'User registered successfully'}
    return {'success': False, 'message': 'Username already exists'}

@app.post("/api/camera/start")
async def start_camera(camera_id: int = Form(...), source: str = Form("0")):
    """Start camera processing"""
    global video_sources, processing_active
    
    # Convert source
    if source == "webcam" or source == "0":
        source = 0
    
    # Stop existing processor if any
    if camera_id in video_sources:
        video_sources[camera_id].stop()
    
    # Create new processor
    processor = VideoProcessor(camera_id, source)
    if processor.start():
        video_sources[camera_id] = processor
        processing_active[camera_id] = True
        
        # Load hazard zones
        zones = get_safety_zones(camera_id)
        hazard_zones[camera_id] = zones
        
        # Start processing in background
        asyncio.create_task(process_camera_feed(camera_id, processor))
        
        return {'success': True, 'message': f'Camera {camera_id} started'}
    
    return {'success': False, 'message': 'Failed to start camera'}

@app.post("/api/camera/stop")
async def stop_camera(camera_id: int = Form(...)):
    """Stop camera processing"""
    if camera_id in video_sources:
        video_sources[camera_id].stop()
        del video_sources[camera_id]
        processing_active[camera_id] = False
        return {'success': True, 'message': f'Camera {camera_id} stopped'}
    
    return {'success': False, 'message': 'Camera not found'}

@app.post("/api/zones/save")
async def save_zone(
    camera_id: int = Form(...),
    zone_name: str = Form(...),
    zone_type: str = Form(...),
    coordinates: str = Form(...)
):
    """Save safety zone"""
    coords = json.loads(coordinates)
    save_safety_zone(camera_id, zone_name, zone_type, coords)
    
    # Update in-memory zones
    zones = get_safety_zones(camera_id)
    hazard_zones[camera_id] = zones
    
    return {'success': True, 'message': 'Zone saved successfully'}

@app.get("/api/zones/{camera_id}")
async def get_zones(camera_id: int):
    """Get safety zones for camera"""
    zones = get_safety_zones(camera_id)
    return {'zones': zones}

@app.get("/api/incidents/recent")
async def get_incidents(limit: int = 10, days: int = 7):
    """Get recent incidents"""
    incidents = get_recent_incidents(limit, days)
    return {'incidents': incidents}

@app.get("/api/analytics")
async def get_analytics(days: int = 7):
    """Get analytics data"""
    data = get_analytics_data(days)
    return data

@app.post("/api/settings/language")
async def set_language(language: str = Form(...)):
    """Set voice alert language"""
    global user_language
    if language in ['english', 'hindi', 'tamil']:
        user_language = language
        return {'success': True, 'message': f'Language set to {language}'}
    return {'success': False, 'message': 'Invalid language'}

@app.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file"""
    try:
        # Save uploaded file
        file_path = os.path.join('static', 'videos', file.filename)
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        return {'success': True, 'file_path': file_path, 'message': 'Video uploaded successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        'message': 'CSIS Backend API',
        'version': '1.0.0',
        'status': 'running'
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
