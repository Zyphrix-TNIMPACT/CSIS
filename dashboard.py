import streamlit as st
import cv2
import pandas as pd
import time
from datetime import datetime
import glob

from detection_module import DetectionModule
from zone_module import ZoneModule
from near_miss import detect_near_miss
from risk_engine import calculate_risk_score, classify_incident
from utils import simulate_event
from database import initialize_db, add_incident, get_recent_incidents

# Initialize database
initialize_db()

st.set_page_config(page_title="CSIS Dashboard", layout="wide")

# Custom CSS for earthy, elegant corporate theme
st.markdown("""
<style>
    /* Background and typography */
    .stApp {
        background-color: #FFFFF0; /* Ivory */
        color: #2B2B2B; /* Charcoal Black */
    }
    
    /* Headers and Base Text */
    h1, h2, h3, h4, h5, h6, .stMarkdown p {
        color: #2B2B2B !important;
    }
    
    /* Sidebar styling override */
    [data-testid="stSidebar"] {
        background-color: #483C32 !important; /* Taupe */
    }
    /* Keep headings and basic text in sidebar Ivory so it contrasts with Taupe */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p {
        color: #FFFFF0 !important;
    }
    
    /* Make buttons and selectbox text Chocolate Brown so they are visible on lighter element backgrounds */
    .stButton > button, .stButton > button * {
        color: #7B3F00 !important; /* Chocolate Brown */
        font-weight: bold;
    }
    
    .stSelectbox div[data-baseweb="select"] * {
        color: #7B3F00 !important; /* Chocolate Brown */
    }

    /* Metric/Card Containers */
    .metric-row {
        background-color: #D2B48C; /* Tan */
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(43, 43, 43, 0.08); /* Soft minimal shadow */
        margin-bottom: 25px;
        color: #2B2B2B;
    }
    
    /* Global Alert Boxes */
    .alert-box {
        padding: 16px;
        border-radius: 8px;
        color: #FFFFF0;
        font-weight: 500;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Severity Colors */
    .alert-critical { background-color: #800020; } /* Deep Maroon */
    .alert-high { background-color: #8B4513; } /* Earthy SaddleBrown for High (Alternative to Maroon) */
    .alert-medium { background-color: #CD853F; color: #FFFFF0; } /* Earthy Peru/Bronze */
    .alert-low { background-color: #556B2F; } /* Olive Green */
</style>
""", unsafe_allow_html=True)

# Define the logo path for UI rendering
logo_path = "logo.png"

# Layout for Header with Logo
header_col1, header_col2 = st.columns([1.5, 9])
with header_col1:
    try:
        st.image(logo_path, width=150)
    except:
        pass # Fallback gracefully if image path is unavailable
with header_col2:
    st.title("CSIS – Cognitive Safety Intelligence System")
    st.markdown('<h3 style="color: #7B3F00; text-align: center; font-style: italic; font-weight: 600; margin-top: -10px; margin-bottom: 25px;">"Safety in Sight"</h3>', unsafe_allow_html=True)

# We no longer need session state for incident_logs
def add_log(incident, severity, status="Logged"):
    add_incident(incident, severity, status)

# Cooldown state to prevent log spamming
if "last_near_miss_time" not in st.session_state:
    st.session_state.last_near_miss_time = 0
if "last_auto_ierre_time" not in st.session_state:
    st.session_state.last_auto_ierre_time = 0

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎥 Live Video Feed")
    video_placeholder = st.empty()

with col2:
    st.subheader("📊 Risk Metrics")
    metric_placeholder = st.empty()
    
    st.subheader("🚨 Incident-Aware Emergency Response (IERRE)")
    b1, b2, b3 = st.columns(3)
    if b1.button("Fall"):
        msg = simulate_event("Fall")
        add_log("Worker Fall Simulated", "Critical", "Emergency Protocol")
        st.error(msg)
    if b2.button("Fire"):
        msg = simulate_event("Fire")
        add_log("Fire Simulated", "Critical", "Evacuation")
        st.error(msg)
    if b3.button("Theft"):
        msg = simulate_event("Security Breach")
        add_log("Security Breach Simulated", "High", "Silent Alert")
        st.warning(msg)

    st.subheader("📝 Incident Log Table")
    log_placeholder = st.empty()
    
    # Always render the table based on current state
    df_logs = get_recent_incidents(10)
    if not df_logs.empty:
        log_placeholder.dataframe(df_logs, use_container_width=True)
    else:
        log_placeholder.info("No incidents logged yet.")

# Initialization Sidebar
st.sidebar.title("Settings")

# Multi-Camera Capability (Conceptual UI)
st.sidebar.subheader("🎥 Camera Architecture")
st.sidebar.markdown("""
<div style='background-color: #382C22; padding: 10px; border-radius: 8px;'>
    <small style='color: #D2B48C;'><b>Edge node processing:</b></small><br/>
    <span style='color: #4CAF50;'>● Cam 1 (Main Hub) - Active</span><br/>
    <span style='color: #F44336;'>● Cam 2 (Zone B) - Offline</span><br/>
    <span style='color: #F44336;'>● Cam 3 (Storage) - Offline</span>
</div>
<br/>
""", unsafe_allow_html=True)

# Find available video files
video_files = glob.glob("*.mp4") + glob.glob("*.avi") + glob.glob("*.mov")
video_options = ["Webcam (Cam 1)"] + video_files

video_source = st.sidebar.selectbox("Active Stream", video_options)

if "system_running" not in st.session_state:
    st.session_state.system_running = False

start_button = st.sidebar.button("Start System")
stop_button = st.sidebar.button("Stop System")

if start_button:
    st.session_state.system_running = True
if stop_button:
    st.session_state.system_running = False
    
if st.session_state.system_running:
    # Initialize Modules (Cache these or instantiate once per run to avoid reloading models)
    detector = DetectionModule()
    
    # Define a generic hazard zone and safe zone using relative coordinates (0.0 to 1.0)
    hazard_box_rel = [0.3, 0.2, 0.7, 0.8] 
    safe_box_rel = [0.05, 0.05, 0.95, 0.95]
    zoner = ZoneModule(hazard_zone_rel=hazard_box_rel, safe_zone_rel=safe_box_rel)
    
    source = 0 if video_source.startswith("Webcam") else video_source
    cap = cv2.VideoCapture(source)

    while cap.isOpened() and st.session_state.system_running:
        ret, frame = cap.read()
        if not ret:
            st.warning("Video stream ended.")
            break
        
        # Resize for consistent processing
        frame = cv2.resize(frame, (640, 480))
        
        # 1. Detection
        frame, persons, vehicles, helmets_missing, incident_triggered = detector.process_frame(frame)
        
        # Process Automated IERRE Events from Vision System
        current_time = time.time()
        if incident_triggered and (current_time - st.session_state.last_auto_ierre_time > 5):
            msg = simulate_event(incident_triggered)
            if incident_triggered == "Fall":
                add_log("Worker Fall Analyzed via Feed", "Critical", "Emergency Protocol")
                st.error(msg)
            elif incident_triggered == "Fire":
                add_log("Fire Analyzed via Feed", "Critical", "Evacuation")
                st.error(msg)
                
            st.session_state.last_auto_ierre_time = current_time
        
        # 2. Zone Overlays
        frame = zoner.draw_zones(frame)
        
        # Risk Evaluation Logic per frame
        in_hazard = False
        no_helmet = False
        
        h, w = frame.shape[:2]
        
        for i, p_bbox in enumerate(persons):
            if zoner.is_in_hazard_zone(p_bbox, w, h):
                in_hazard = True
            if helmets_missing[i]:
                no_helmet = True
                
        # 3. Near Miss
        has_near_miss, miss_events = detect_near_miss(persons, vehicles, distance_threshold=150)
        
        # 4. Risk Engine
        total_risk = calculate_risk_score(in_hazard, has_near_miss, no_helmet)
        level, classification, alert_msg = classify_incident(total_risk)
        
        # Debounce Near-Miss logs to prevent flooding
        current_time = time.time()
        if has_near_miss and (current_time - st.session_state.last_near_miss_time > 3):
            add_log("Near-Miss Detected", "High", "Logged")
            st.session_state.last_near_miss_time = current_time
        if in_hazard:
            # Throttle logs in a real system, but for prototype we can log or just show it live
            pass
            
        # Apply Explainable AI (XAI) Overlay on Frame
        overlay_text = f"XAI Risk Score: {total_risk} ({level})"
        color = (0, 255, 0)
        if level == "Critical": color = (0, 0, 255)
        elif level == "High": color = (0, 165, 255)
        elif level == "Medium": color = (0, 255, 255)
        
        cv2.rectangle(frame, (10, 10), (320, 50), (43, 43, 43), -1)
        cv2.putText(frame, overlay_text, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        if incident_triggered:
            cv2.putText(frame, f"EVENT: {incident_triggered}", (15, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # UI Updates
        # Convert BGR to RGB for Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, use_container_width=True)
        
        # Update Metrics
        with metric_placeholder.container():
            st.markdown('<div class="metric-row">', unsafe_allow_html=True)
            kpi1, kpi2 = st.columns(2)
            kpi1.metric("Current Risk Score", f"{total_risk}")
            kpi2.metric("Severity Level", level)
            
            # Alert Notification Panel
            if level == "Critical":
                st.markdown(f'<div class="alert-box alert-critical">{alert_msg}</div>', unsafe_allow_html=True)
            elif level == "High":
                st.markdown(f'<div class="alert-box alert-high">{alert_msg}</div>', unsafe_allow_html=True)
            elif level == "Medium":
                st.markdown(f'<div class="alert-box alert-medium">{alert_msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-box alert-low">{alert_msg}</div>', unsafe_allow_html=True)
                
            # Near miss panel
            if has_near_miss:
                st.error(f"⚠️ Near-Miss Event Detected! ({len(miss_events)} instances)")
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Update Logs
        df_logs = get_recent_incidents(10)
        if not df_logs.empty:
            log_placeholder.dataframe(df_logs, use_container_width=True)
        else:
            log_placeholder.info("No incidents logged yet.")

        # Simulate frame rate delay
        time.sleep(0.05)
        
    cap.release()
