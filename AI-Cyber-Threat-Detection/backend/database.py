import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cyber_threats.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Drop table if it exists to ensure new schema (use with caution in prod)
        # For a hackathon, this is safe to ensure the UI works.
        cursor.execute("DROP TABLE IF EXISTS logs")
        cursor.execute("""
            CREATE TABLE logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_ip TEXT,
                attack_type TEXT,
                severity TEXT,
                risk_score REAL,
                summary TEXT
            )
        """)
        conn.commit()
        conn.close()
        print("Database initialized with new schema.")
    except Exception as e:
        print(f"DB Init Error: {e}")

def log_prediction(source_ip, attack_type, severity, risk_score, summary):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (source_ip, attack_type, severity, risk_score, summary) 
        VALUES (?, ?, ?, ?, ?)
    """, (source_ip, attack_type, severity, risk_score, summary))
    conn.commit()
    conn.close()

def get_logs(limit=1000):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, source_ip, attack_type, severity, risk_score, summary FROM logs ORDER BY id DESC LIMIT ?", (limit,))
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
