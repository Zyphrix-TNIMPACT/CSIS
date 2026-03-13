import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_FILENAME = 'incident_log.db'

def get_connection():
    return sqlite3.connect(DB_FILENAME, check_same_thread=False)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            action_taken TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_incident(incident_type, risk_level, action_taken):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO incidents (timestamp, incident_type, risk_level, action_taken) VALUES (?, ?, ?, ?)",
        (timestamp, incident_type, risk_level, action_taken)
    )
    conn.commit()
    conn.close()

def get_recent_incidents(limit=10):
    conn = get_connection()
    query = "SELECT timestamp as Time, incident_type as Incident, risk_level as Severity, action_taken as Status FROM incidents ORDER BY id DESC LIMIT ?"
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df
