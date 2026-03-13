import React from 'react';
import { motion } from 'framer-motion';
import { Flame, Bell, Users, AlertTriangle, CheckCircle } from 'lucide-react';
import './EmergencyResponse.css';

const EmergencyResponse = () => {
  const triggeredActions = [
    { id: 1, action: 'Alarm Activated', status: 'completed', icon: Bell },
    { id: 2, action: 'Supervisor Alert Sent', status: 'completed', icon: Users },
    { id: 3, action: 'Evacuation Notification', status: 'completed', icon: AlertTriangle },
    { id: 4, action: 'Emergency Services Contacted', status: 'in-progress', icon: AlertTriangle }
  ];

  return (
    <div className="emergency-response">
      <motion.div
        className="emergency-banner"
        animate={{
          background: [
            'linear-gradient(135deg, #E74C3C 0%, #C0392B 100%)',
            'linear-gradient(135deg, #C0392B 0%, #E74C3C 100%)',
            'linear-gradient(135deg, #E74C3C 0%, #C0392B 100%)'
          ]
        }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <motion.div
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
        >
          <Flame size={60} />
        </motion.div>
        <h1>INCIDENT DETECTED</h1>
      </motion.div>

      <div className="emergency-content">
        <motion.div
          className="incident-details"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="incident-type">
            <Flame size={40} className="incident-icon" />
            <div>
              <h2>Fire in Zone 2</h2>
              <p>Production Floor - Camera 3</p>
            </div>
          </div>

          <div className="risk-level-display">
            <div className="risk-label">Risk Level</div>
            <motion.div
              className="risk-badge critical"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              CRITICAL
            </motion.div>
          </div>

          <div className="incident-time">
            Detected at: 10:47:23
          </div>
        </motion.div>

        <motion.div
          className="actions-triggered"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2>Automated Response Actions</h2>
          <div className="actions-list">
            {triggeredActions.map((action, index) => (
              <motion.div
                key={action.id}
                className={`action-item ${action.status}`}
                initial={{ x: -50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.5 + index * 0.15 }}
              >
                <div className="action-icon-wrapper">
                  {action.status === 'completed' ? (
                    <CheckCircle size={24} className="check-icon" />
                  ) : (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    >
                      <action.icon size={24} />
                    </motion.div>
                  )}
                </div>
                <div className="action-text">{action.action}</div>
                <div className={`action-status ${action.status}`}>
                  {action.status === 'completed' ? 'Completed' : 'In Progress'}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div
          className="emergency-instructions"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <h3>Emergency Protocol Active</h3>
          <ul>
            <li>All personnel evacuating from Zone 2</li>
            <li>Fire suppression system activated</li>
            <li>Emergency exits unlocked</li>
            <li>Supervisor en route to location</li>
          </ul>
        </motion.div>
      </div>
    </div>
  );
};

export default EmergencyResponse;
