import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Camera, Shield, User, Lock, AlertTriangle } from 'lucide-react';
import './LoginPage.css';

const LoginPage = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    navigate('/dashboard');
  };

  const handleEmergencyAccess = () => {
    navigate('/dashboard');
  };

  return (
    <div className="login-page">
      <motion.div
        className="login-left"
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        <div className="illustration">
          <motion.div
            className="factory-bg"
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
          >
            <Shield size={120} className="shield-icon" />
          </motion.div>
          
          <motion.div
            className="camera-overlay"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <Camera size={60} />
          </motion.div>

          <div className="detection-boxes">
            <motion.div
              className="detect-box box-1"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <motion.div
              className="detect-box box-2"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
            />
          </div>

          <div className="illustration-text">
            <h2>AI-Powered Safety Monitoring</h2>
            <p>Real-time detection • Instant alerts • Automated response</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        className="login-right"
        initial={{ x: 100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        <div className="login-card">
          <div className="login-header">
            <h1>Welcome to CSIS</h1>
            <p>Secure Access Control</p>
          </div>

          <form onSubmit={handleLogin} className="login-form">
            <div className="input-group">
              <User size={20} className="input-icon" />
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="input-group">
              <Lock size={20} className="input-icon" />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className="remember-device">
              <input type="checkbox" id="remember" />
              <label htmlFor="remember">Remember Device</label>
            </div>

            <motion.button
              type="submit"
              className="btn btn-primary login-btn"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              LOGIN
            </motion.button>

            <motion.button
              type="button"
              className="btn btn-emergency"
              onClick={handleEmergencyAccess}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <AlertTriangle size={18} />
              EMERGENCY ACCESS (Supervisor)
            </motion.button>
          </form>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
