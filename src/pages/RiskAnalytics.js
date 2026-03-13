import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, AlertTriangle, Activity } from 'lucide-react';
import './RiskAnalytics.css';

const RiskAnalytics = () => {
  const riskDistribution = [
    { name: 'Zone A', value: 35, color: '#E74C3C' },
    { name: 'Zone B', value: 28, color: '#F39C12' },
    { name: 'Zone C', value: 22, color: '#3498DB' },
    { name: 'Zone D', value: 15, color: '#2ECC71' }
  ];

  const nearMissTrends = [
    { month: 'Jan', incidents: 12 },
    { month: 'Feb', incidents: 15 },
    { month: 'Mar', incidents: 8 },
    { month: 'Apr', incidents: 18 },
    { month: 'May', incidents: 10 },
    { month: 'Jun', incidents: 6 }
  ];

  const topRisks = [
    { area: 'Zone A - Production Floor', risk: 35, incidents: 24 },
    { area: 'Zone B - Loading Bay', risk: 28, incidents: 18 },
    { area: 'Zone C - Assembly Line', risk: 22, incidents: 14 },
    { area: 'Zone D - Storage Area', risk: 15, incidents: 9 }
  ];

  return (
    <div className="risk-analytics">
      <h1 className="analytics-title">Risk Analytics Dashboard</h1>

      <div className="analytics-grid">
        <motion.div
          className="analytics-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="card-header">
            <h2>Risk Distribution by Zone</h2>
            <TrendingUp size={24} className="header-icon" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                animationBegin={0}
                animationDuration={1000}
              >
                {riskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          className="analytics-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="card-header">
            <h2>Near-Miss Trends</h2>
            <Activity size={24} className="header-icon" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={nearMissTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="incidents" fill="#D2B48C" animationDuration={1000} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          className="analytics-card full-width"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="card-header">
            <h2>Top Risk Areas</h2>
            <AlertTriangle size={24} className="header-icon" />
          </div>
          <div className="risk-areas">
            {topRisks.map((risk, index) => (
              <motion.div
                key={index}
                className="risk-area-item"
                initial={{ x: -50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.4 + index * 0.1 }}
              >
                <div className="risk-area-info">
                  <div className="risk-area-name">{risk.area}</div>
                  <div className="risk-area-incidents">{risk.incidents} incidents</div>
                </div>
                <div className="risk-area-bar">
                  <motion.div
                    className="risk-area-fill"
                    style={{
                      width: `${risk.risk}%`,
                      background: risk.risk > 30 ? '#E74C3C' : risk.risk > 20 ? '#F39C12' : '#3498DB'
                    }}
                    initial={{ width: 0 }}
                    animate={{ width: `${risk.risk}%` }}
                    transition={{ delay: 0.5 + index * 0.1, duration: 0.8 }}
                  />
                </div>
                <div className="risk-area-percentage">{risk.risk}%</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div
          className="analytics-card heatmap-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="card-header">
            <h2>Incident Heatmap</h2>
          </div>
          <div className="heatmap">
            {[...Array(8)].map((_, row) => (
              <div key={row} className="heatmap-row">
                {[...Array(12)].map((_, col) => {
                  const intensity = Math.random();
                  return (
                    <motion.div
                      key={col}
                      className="heatmap-cell"
                      style={{
                        background: `rgba(231, 76, 60, ${intensity})`,
                      }}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.5 + (row * 12 + col) * 0.01 }}
                    />
                  );
                })}
              </div>
            ))}
          </div>
          <div className="heatmap-legend">
            <span>Low Risk</span>
            <div className="legend-gradient" />
            <span>High Risk</span>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default RiskAnalytics;
