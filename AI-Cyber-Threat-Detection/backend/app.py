import os
import random
import numpy as np
from flask import Flask, request, jsonify
import joblib
import pandas as pd
from database import init_db, log_prediction, get_logs, cleanup_db, is_blacklisted, blacklist_ip, get_blacklist

app = Flask(__name__)
init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "cyber_model.pkl")
ANOMALY_PATH = os.path.join(BASE_DIR, "..", "model", "anomaly_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "..", "model", "scaler.pkl")

print(f"Loading models...")
try:
    model = joblib.load(MODEL_PATH)
    anomaly_model = joblib.load(ANOMALY_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("Models and Scaler loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    anomaly_model = None
    scaler = None

# Mock list of suspicious IPs for simulation
IP_LIST = ["192.168.1.10", "10.0.0.5", "172.16.5.85", "203.0.113.4", "198.51.100.12"]

# Simple in-memory tracker for predictive risk scoring (Escalation)
threat_tracker = {}

@app.route("/logs", methods=["GET"])
def fetch_logs():
    logs = get_logs()
    return jsonify(logs)

@app.route("/blacklist", methods=["GET"])
def fetch_blacklist():
    return jsonify(get_blacklist())

@app.route("/predict", methods=["POST"])
def predict():
    if model is None or scaler is None or anomaly_model is None:
        return jsonify({"error": "System not fully initialized"}), 500

    data = request.json
    source_ip = data.get("source_ip", f"192.168.1.{random.randint(100, 254)}")

    # 1. Check Mitigation Status
    if False and is_blacklisted(source_ip):
        return jsonify({
            "attack_type": "BLOCKED",
            "severity": "CRITICAL",
            "risk_score": 1.0,
            "source_ip": source_ip,
            "message": "Access Denied: IP is Blacklisted"
        }), 403

    try:
        # 2. Input Processing
        df = pd.DataFrame([data])
        
        # Ensure we only use columns that the models were trained on
        if hasattr(model, "feature_names_in_"):
            for col in model.feature_names_in_:
                if col not in df.columns:
                    df[col] = 0
            df_classifier = df[model.feature_names_in_]
        
        if hasattr(anomaly_model, "feature_names_in_"):
            for col in anomaly_model.feature_names_in_:
                if col not in df.columns:
                    df[col] = 0
            df_anomaly = df[anomaly_model.feature_names_in_]

        # 3. Scaling & Supervised Prediction
        X_scaled = scaler.transform(df_classifier)
        prediction = str(model.predict(X_scaled)[0])
        
        # Calculate Risk Score
        probs = model.predict_proba(X_scaled)[0]
        class_idx = np.argmax(probs)
        base_risk = round(float(probs[class_idx]), 2)

        if prediction == "BENIGN":
            base_risk = round(1.0 - base_risk, 2)
            base_risk = max(0.01, min(0.15, base_risk + random.uniform(-0.02, 0.02)))
            severity = "Low"
        else:
            severity = "High"

        # 4. Behavioral Anomaly Detection (Isolation Forest)
        # 1 = Normal, -1 = Anomaly
        is_anomaly_pred = int(anomaly_model.predict(df_anomaly)[0])
        is_anomaly = 1 if is_anomaly_pred == -1 else 0

        if is_anomaly and prediction == "BENIGN":
            prediction = "ANOMALY (Unseen Pattern)"
            severity = "Medium"
            base_risk = max(base_risk, 0.45) # Escalate risk for anomalies

        # 5. Predictive Risk Escalation (Behavioral Patterns)
        if source_ip not in threat_tracker:
            threat_tracker[source_ip] = []
        
        # Keep track of last 5 events
        threat_tracker[source_ip].append({"risk": base_risk, "time": pd.Timestamp.now()})
        threat_tracker[source_ip] = threat_tracker[source_ip][-5:]

        # If 3+ suspicious events (>0.3) in short time, escalate risk
        suspicious_events = [e for e in threat_tracker[source_ip] if e['risk'] > 0.3]
        if len(suspicious_events) >= 3 and severity != "High":
            prediction = "RECONNAISSANCE (Escalated)"
            severity = "High"
            base_risk = 0.85
            
        # 6. Explainable AI (XAI) - Identify top contributors
        feature_importance = []
        if prediction != "BENIGN":
            # Simple heuristic: find features furthest from mean (scaled)
            diffs = np.abs(X_scaled[0])
            top_indices = np.argsort(diffs)[-3:][::-1]
            feature_importance = [model.feature_names_in_[i] for i in top_indices]

        # 7. Automated Mitigation (Response)
        if severity == "High" or base_risk > 0.8:
            blacklist_ip(source_ip, f"Automatic Block: High Threat ({prediction})")

        summary = f"Top Features: {', '.join(feature_importance)}" if feature_importance else f"Port: {data.get('Destination Port')} | Flow: {data.get('Flow Duration')}"
        
        # Log to Database
        log_prediction(source_ip, prediction, severity, base_risk, summary, is_anomaly)

        # Periodic cleanup
        if random.random() < 0.01:
            cleanup_db()

        return jsonify({
            "attack_type": prediction,
            "severity": severity,
            "risk_score": base_risk,
            "source_ip": source_ip,
            "is_anomaly": bool(is_anomaly),
            "top_features": feature_importance
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
 