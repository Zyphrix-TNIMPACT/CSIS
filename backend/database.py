import sqlite3
from datetime import datetime
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'csis.db')

def init_database():
    """Initialize database with all required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Incidents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER NOT NULL,
            camera_name TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            snapshot_path TEXT,
            details TEXT
        )
    ''')
    
    # Risk scores history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER NOT NULL,
            risk_score INTEGER NOT NULL,
            workers_count INTEGER DEFAULT 0,
            vehicles_count INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Safety zones configuration
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS safety_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER NOT NULL,
            zone_name TEXT NOT NULL,
            zone_type TEXT NOT NULL,
            coordinates TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Detection snapshots
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER NOT NULL,
            snapshot_path TEXT NOT NULL,
            detections TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Analytics data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            total_incidents INTEGER DEFAULT 0,
            near_miss_count INTEGER DEFAULT 0,
            critical_count INTEGER DEFAULT 0,
            avg_risk_score REAL DEFAULT 0,
            UNIQUE(date)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

def add_user(username, password, phone_number=None):
    """Add new user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password, phone_number) VALUES (?, ?, ?)',
                      (username, password, phone_number))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    """Verify user credentials"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, phone_number FROM users WHERE username=? AND password=?',
                  (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

def log_incident(camera_id, camera_name, incident_type, severity, risk_score, snapshot_path=None, details=None):
    """Log incident to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO incidents (camera_id, camera_name, incident_type, severity, risk_score, snapshot_path, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (camera_id, camera_name, incident_type, severity, risk_score, snapshot_path, json.dumps(details) if details else None))
    conn.commit()
    incident_id = cursor.lastrowid
    conn.close()
    return incident_id

def log_risk_score(camera_id, risk_score, workers_count=0, vehicles_count=0):
    """Log risk score history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO risk_history (camera_id, risk_score, workers_count, vehicles_count)
        VALUES (?, ?, ?, ?)
    ''', (camera_id, risk_score, workers_count, vehicles_count))
    conn.commit()
    conn.close()

def save_safety_zone(camera_id, zone_name, zone_type, coordinates):
    """Save or update safety zone"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if zone exists
    cursor.execute('SELECT id FROM safety_zones WHERE camera_id=? AND zone_name=?',
                  (camera_id, zone_name))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('''
            UPDATE safety_zones SET zone_type=?, coordinates=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (zone_type, json.dumps(coordinates), existing[0]))
    else:
        cursor.execute('''
            INSERT INTO safety_zones (camera_id, zone_name, zone_type, coordinates)
            VALUES (?, ?, ?, ?)
        ''', (camera_id, zone_name, zone_type, json.dumps(coordinates)))
    
    conn.commit()
    conn.close()

def get_safety_zones(camera_id):
    """Get all safety zones for a camera"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT zone_name, zone_type, coordinates FROM safety_zones WHERE camera_id=?',
                  (camera_id,))
    zones = []
    for row in cursor.fetchall():
        zones.append({
            'name': row[0],
            'type': row[1],
            'coordinates': json.loads(row[2])
        })
    conn.close()
    return zones

def get_recent_incidents(limit=10, days=7):
    """Get recent incidents"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT camera_name, incident_type, severity, risk_score, timestamp
        FROM incidents
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (days, limit))
    incidents = []
    for row in cursor.fetchall():
        incidents.append({
            'camera': row[0],
            'type': row[1],
            'severity': row[2],
            'risk_score': row[3],
            'time': row[4]
        })
    conn.close()
    return incidents

def get_analytics_data(days=7):
    """Get analytics data for charts"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Incident frequency by day
    cursor.execute('''
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM incidents
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
        GROUP BY DATE(timestamp)
        ORDER BY date
    ''', (days,))
    incident_frequency = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Risk distribution by severity
    cursor.execute('''
        SELECT severity, COUNT(*) as count
        FROM incidents
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
        GROUP BY severity
    ''', (days,))
    risk_distribution = [{'severity': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Top risk areas
    cursor.execute('''
        SELECT camera_name, COUNT(*) as incidents, AVG(risk_score) as avg_risk
        FROM incidents
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
        GROUP BY camera_name
        ORDER BY avg_risk DESC
        LIMIT 5
    ''', (days,))
    top_risk_areas = [{'camera': row[0], 'incidents': row[1], 'avg_risk': round(row[2], 1)} 
                      for row in cursor.fetchall()]
    
    conn.close()
    return {
        'incident_frequency': incident_frequency,
        'risk_distribution': risk_distribution,
        'top_risk_areas': top_risk_areas
    }

# Initialize database on import
init_database()
