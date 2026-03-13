import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Camera, ZoomIn, Pause, Play, Users, Car, AlertTriangle } from 'lucide-react';
import './CameraMonitoring.css';

const CameraMonitoring = () => {
  const [isPaused, setIsPaused] = useState(false);
  const [zoom, setZoom] = useState(1);

  const incidents = [
    { time: '10:45', type: 'Near Miss', severity: 'medium' },
    { time: '10:32', type: 'Zone Violation', severity: 'high' },
    { time: '10:15', type: 'PPE Missing', severity: 'medium' },
    { time: '09:58', type: 'Worker Fall', severity: 'critical' }
  ];

  return (
    <div className="camera-monitoring">
      <div className="monitoring-header">
        <h1>Camera 1 - Production Floor</h1>
        <div className="header-actions">
          <button className="btn-icon" onClick={() => setIsPaused(!isPaused)}>
            {isPaused ? <Play size={20} /> : <Pause size={20} />}
          </button>
          <button className="btn-icon" onClick={() => setZoom(zoom === 1 ? 1.5 : 1)}>
            <ZoomIn size={20} />
          </button>
        </div>
      </div>

      <div className="monitoring-content">
        <div className="video-section">
          <motion.div 
            className="large-feed"
            animate={{ scale: zoom }}
            transition={{ duration: 0.3 }}
          >
            <div className="video-placeholder-large">
              <Camera size={60} />
            </div>

            <motion.div
              className="detection-worker"
              animate={{ opacity: [0.7, 1, 0.7] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <span className="detect-label">Worker</span>
            </motion.div>

            <motion.div
              className="detection-vehicle"
              animate={{ opacity: [0.7, 1, 0.7] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
            >
              <span className="detect-label">Vehicle</span>
            </motion.div>

            <motion.div
              className="hazard-boundary"
              animate={{
                boxShadow: [
                  '0 0 10px rgba(231, 76, 60, 0.5)',
                  '0 0 30px rgba(231, 76, 60, 0.9)',
                  '0 0 10px rgba(231, 76, 60, 0.5)'
                ]
              }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
          </motion.div>

          <div className="video-stats">
            <div className="stat-card">
              <div className="stat-icon risk">
                <AlertTriangle size={24} />
              </div>
              <div className="stat-info">
                <div className="stat-label">Risk Score</div>
                <div className="stat-value">72</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon workers">
                <Users size={24} />
              </div>
              <div className="stat-info">
                <div className="stat-label">Worker Count</div>
                <div className="stat-value">3</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon vehicles">
                <Car size={24} />
              </div>
              <div className="stat-info">
                <div className="stat-label">Vehicles</div>
                <div className="stat-value">1</div>
              </div>
            </div>
          </div>
        </div>

        <div className="timeline-section">
          <h2>Incident Timeline</h2>
          <div className="timeline">
            {incidents.map((incident, index) => (
              <motion.div
                key={index}
                className={`timeline-item ${incident.severity}`}
                initial={{ x: -50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="timeline-time">{incident.time}</div>
                <div className="timeline-dot" />
                <div className="timeline-content">
                  <div className="timeline-type">{incident.type}</div>
                  <div className={`timeline-severity ${incident.severity}`}>
                    {incident.severity}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CameraMonitoring;
