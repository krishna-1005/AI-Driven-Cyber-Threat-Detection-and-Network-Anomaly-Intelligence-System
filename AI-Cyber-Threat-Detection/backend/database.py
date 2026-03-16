import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cyber_threats.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS logs")
        cursor.execute("DROP TABLE IF EXISTS blacklist")
        cursor.execute("""
            CREATE TABLE logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_ip TEXT,
                attack_type TEXT,
                severity TEXT,
                risk_score REAL,
                summary TEXT,
                is_anomaly INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE blacklist (
                ip TEXT PRIMARY KEY,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        print("Database initialized with Blacklist & Anomaly support.")
    except Exception as e:
        print(f"DB Init Error: {e}")

def log_prediction(source_ip, attack_type, severity, risk_score, summary, is_anomaly=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (source_ip, attack_type, severity, risk_score, summary, is_anomaly) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (source_ip, attack_type, severity, risk_score, summary, is_anomaly))
    conn.commit()
    conn.close()

def blacklist_ip(ip, reason):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO blacklist (ip, reason) VALUES (?, ?)", (ip, reason))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Blacklist Error: {e}")

def is_blacklisted(ip):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ip FROM blacklist WHERE ip = ?", (ip,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def get_blacklist():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ip, reason, timestamp FROM blacklist ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_logs(limit=1000):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, source_ip, attack_type, severity, risk_score, summary, is_anomaly FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def cleanup_db(max_rows=5000):
    """Keep only the latest rows to prevent database bloat."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs WHERE id NOT IN (SELECT id FROM logs ORDER BY id DESC LIMIT ?)", (max_rows,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Cleanup Error: {e}")
