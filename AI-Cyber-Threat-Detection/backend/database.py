import sqlite3
import os
from datetime import datetime

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cyber_threats.db")


# ----------------------------------------------------
# Initialize Database (SAFE VERSION)
# ----------------------------------------------------
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source_ip TEXT,
            attack_type TEXT,
            severity TEXT,
            risk_score REAL,
            summary TEXT,
            is_anomaly INTEGER DEFAULT 0,
            review_status TEXT DEFAULT 'Pending'
        )
        """)

        # Create blacklist table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
            ip TEXT PRIMARY KEY,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()

        # Migration: Ensure review_status column exists for HITL features
        try:
            cursor.execute("ALTER TABLE logs ADD COLUMN review_status TEXT DEFAULT 'Pending'")
            conn.commit()
        except sqlite3.OperationalError:
            pass # Column already exists

        conn.close()

        print("Database initialized successfully")

    except Exception as e:
        print(f"DB Init Error: {e}")


# ----------------------------------------------------
# Log Predictions
# ----------------------------------------------------
def log_prediction(source_ip, attack_type, severity, risk_score, summary, is_anomaly=0):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO logs 
        (source_ip, attack_type, severity, risk_score, summary, is_anomaly)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (source_ip, attack_type, severity, risk_score, summary, is_anomaly))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Log Error: {e}")


# ----------------------------------------------------
# Blacklist IP
# ----------------------------------------------------
def blacklist_ip(ip, reason):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT OR REPLACE INTO blacklist (ip, reason)
        VALUES (?, ?)
        """, (ip, reason))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Blacklist Error: {e}")


# ----------------------------------------------------
# Check if IP is Blacklisted
# ----------------------------------------------------
def is_blacklisted(ip):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT ip FROM blacklist WHERE ip = ?", (ip,))
    row = cursor.fetchone()

    conn.close()

    return row is not None


# ----------------------------------------------------
# Get Blacklisted IPs
# ----------------------------------------------------
def get_blacklist():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ip, reason, timestamp 
    FROM blacklist 
    ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ----------------------------------------------------
# Get Stats for Dashboard
# ----------------------------------------------------
def get_log_count():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM logs")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ----------------------------------------------------
# Get Logs for Dashboard
# ----------------------------------------------------
def get_logs(limit=1000):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, timestamp, source_ip, attack_type, severity, risk_score, summary, is_anomaly, review_status
    FROM logs
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    conn.close()

    return rows


def update_review_status(log_id, status):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE logs SET review_status = ? WHERE id = ?", (status, log_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Review Update Error: {e}")
        return False


# ----------------------------------------------------
# Cleanup old logs
# ----------------------------------------------------
def cleanup_db(max_rows=5000):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM logs
        WHERE id NOT IN (
            SELECT id FROM logs
            ORDER BY id DESC
            LIMIT ?
        )
        """, (max_rows,))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"DB Cleanup Error: {e}")