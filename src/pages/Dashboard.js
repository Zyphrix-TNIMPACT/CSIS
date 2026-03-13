import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Camera, AlertTriangle, Flame, Users, Car, Activity } from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const [cameras, setCameras] = useState([
    { id: 1, name: 'Camera 1', riskScore: 0, workers: 0, vehicles: 0, status: 'low', frame: null },
    { id: 2, name: 'Camera 2', riskScore: 0, workers: 0, vehicles: 0, status: 'low', frame: null },
    { id: 3, name: 'Camera 3', riskScore: 0, workers: 0, vehicles: 0, status: 'low', frame: null },
    { id: 4, name: 'Camera 4', riskScore: 0, workers: 0, vehicles: 0, status: 'low', frame: null }
  ]);

  const [alerts, setAlerts] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  // WebSocket connection
  useEffect(() => {
    console.log('🔌 Connecting to WebSocket...');
    const ws = new WebSocket('ws://localhost:8000/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
      
      // Start cameras automatically
      startCamera(1, 'webcam');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📨 Received:', data.type);

      if (data.type === 'camera_update') {
        updateCameraData(data);
      } else if (data.type === 'alert') {
        addAlert(data);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setIsConnected(false);
    };

    // Fetch recent incidents
    fetchIncidents();

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const startCamera = async (cameraId, source = 'webcam') => {
    try {
      const formData = new FormData();
      formData.append('camera_id', cameraId);
      formData.append('source', source);

      const response = await fetch('http://localhost:8000/api/camera/start', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      console.log(`📹 Camera ${cameraId}:`, result.message);
    } catch (error) {
      console.error('❌ Error starting camera:', error);
    }
  };

  const updateCameraData = (data) => {
    setCameras(prevCameras => 
      prevCameras.map(cam => 
        cam.id === data.camera_id ? {
          ...cam,
          riskScore: data.risk_score,
          workers: data.workers_count,
          vehicles: data.vehicles_count,
          status: data.severity,
          frame: data.frame
        } : cam
      )
    );
  };

  const addAlert = (alertData) => {
    const newAlert = {
      id: Date.now(),
      type: alertData.severity === 'critical' ? 'critical' : 'warning',
      icon: alertData.incident_type === 'fire' ? Flame : AlertTriangle,
      message: alertData.message,
      camera: `Camera ${alertData.camera_id}`,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };

    setAlerts(prev => [newAlert, ...prev].slice(0, 5)); // Keep only last 5 alerts
  };

  const fetchIncidents = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/incidents/recent?limit=10');
      const data = await response.json();
      
      if (data.incidents) {
        const formattedIncidents = data.incidents.map(inc => ({
          time: new Date(inc.time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          camera: inc.camera,
          incident: inc.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
          severity: inc.severity.charAt(0).toUpperCase() + inc.severity.slice(1)
        }));
        setIncidents(formattedIncidents);
      }
    } catch (error) {
      console.error('❌ Error fetching incidents:', error);
    }
  };

  const getSeverityStatus = (score) => {
    if (score >= 81) return 'critical';
    if (score >= 61) return 'high';
    if (score >= 31) return 'medium';
    return 'low';
  };

  return (
    <div className="dashboard">
      <nav className="top-nav">
        <div className="nav-left">
          <div className="logo">CSIS</div>
          <div className="nav-links">
            <a href="#" className="active">Dashboard</a>
            <a href="#cameras">Cameras</a>
            <a href="#incidents">Incidents</a>
            <a href="#analytics">Analytics</a>
            <a href="#settings">Settings</a>
          </div>
        </div>
        <button className="logout-btn">Logout</button>
      </nav>

      <div className="dashboard-content">
        <aside className="sidebar">
          <div className="sidebar-item active">
            <Camera size={20} />
            <span>Live Monitoring</span>
          </div>
          <div className="sidebar-item">
            <Activity size={20} />
            <span>Safety Zones</span>
          </div>
          <div className="sidebar-item">
            <AlertTriangle size={20} />
            <span>Incident Center</span>
          </div>
          <div className="sidebar-item">
            <Activity size={20} />
            <span>Risk Analytics</span>
          </div>
        </aside>

        <main className="main-area">
          <div className="connection-status">
            {isConnected ? (
              <span className="status-connected">🟢 Connected to AI Backend</span>
            ) : (
              <span className="status-disconnected">🔴 Connecting to backend...</span>
            )}
          </div>
          
          <h1 className="page-title">AI Safety Command Center</h1>
          
          <div className="camera-grid">
            {cameras.map((camera, index) => (
              <motion.div
                key={camera.id}
                className="camera-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="camera-header">
                  <span className="camera-name">{camera.name}</span>
                  <span className={`status-badge ${camera.status}`}>LIVE</span>
                </div>

                <div className="camera-feed">
                  {camera.frame ? (
                    <img 
                      src={`data:image/jpeg;base64,${camera.frame}`} 
                      alt={`${camera.name} feed`}
                      className="live-video-feed"
                    />
                  ) : (
                    <div className="video-placeholder">
                      <Camera size={40} className="camera-icon-placeholder" />
                      {!isConnected && <div className="connecting-text">Connecting to backend...</div>}
                      {isConnected && camera.id === 1 && <div className="connecting-text">Starting webcam...</div>}
                      {isConnected && camera.id !== 1 && <div className="connecting-text">Camera {camera.id} ready</div>}
                    </div>
                  )}
                </div>

                <div className="camera-stats">
                  <div className="stat">
                    <Users size={16} />
                    <span>{camera.workers} Workers</span>
                  </div>
                  <div className="stat">
                    <Car size={16} />
                    <span>{camera.vehicles} Vehicles</span>
                  </div>
                </div>

                <div className="risk-meter">
                  <div className="risk-label">Risk Score</div>
                  <motion.div
                    className={`risk-circle ${camera.status}`}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: index * 0.1 + 0.3, type: 'spring' }}
                  >
                    <svg width="80" height="80">
                      <circle cx="40" cy="40" r="35" fill="none" stroke="#eee" strokeWidth="6" />
                      <motion.circle
                        cx="40"
                        cy="40"
                        r="35"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="6"
                        strokeDasharray={`${2 * Math.PI * 35}`}
                        strokeDashoffset={`${2 * Math.PI * 35 * (1 - camera.riskScore / 100)}`}
                        strokeLinecap="round"
                        initial={{ strokeDashoffset: 2 * Math.PI * 35 }}
                        animate={{ strokeDashoffset: 2 * Math.PI * 35 * (1 - camera.riskScore / 100) }}
                        transition={{ duration: 1, delay: index * 0.1 + 0.5 }}
                      />
                    </svg>
                    <div className="risk-value">{camera.riskScore}</div>
                  </motion.div>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="incident-log">
            <h2>Recent Incidents</h2>
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Camera</th>
                  <th>Incident</th>
                  <th>Severity</th>
                </tr>
              </thead>
              <tbody>
                {incidents.length > 0 ? (
                  incidents.map((incident, index) => (
                    <motion.tr
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={incident.severity === 'Critical' ? 'critical-row' : ''}
                    >
                      <td>{incident.time}</td>
                      <td>{incident.camera}</td>
                      <td>{incident.incident}</td>
                      <td>
                        <span className={`severity-badge ${incident.severity.toLowerCase()}`}>
                          {incident.severity}
                        </span>
                      </td>
                    </motion.tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                      No incidents recorded yet. System is monitoring...
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </main>

        <aside className="alert-panel">
          <h2>LIVE ALERTS</h2>
          <div className="alerts-list">
            {alerts.length > 0 ? (
              alerts.map((alert, index) => (
                <motion.div
                  key={alert.id}
                  className={`alert-item ${alert.type}`}
                  initial={{ x: 100, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: index * 0.2 }}
                >
                  <alert.icon size={24} className="alert-icon" />
                  <div className="alert-content">
                    <div className="alert-message">{alert.message}</div>
                    <div className="alert-meta">
                      {alert.camera} • {alert.time}
                    </div>
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="no-alerts">
                <Activity size={40} style={{ opacity: 0.3, marginBottom: '10px' }} />
                <p>No alerts</p>
                <p style={{ fontSize: '12px', opacity: 0.6 }}>System monitoring...</p>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
};

export default Dashboard;
