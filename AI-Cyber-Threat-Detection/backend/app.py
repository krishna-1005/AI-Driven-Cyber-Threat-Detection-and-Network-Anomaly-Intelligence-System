import os
import random
import numpy as np
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import threading
import time
import requests
from database import init_db, log_prediction, get_logs, cleanup_db, is_blacklisted, blacklist_ip, get_blacklist, get_log_count

app = Flask(__name__)
init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "cyber_model.pkl")
ANOMALY_PATH = os.path.join(BASE_DIR, "..", "model", "anomaly_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "..", "model", "scaler.pkl")
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "cleaned_cicids.csv")

# Global variables for models
model = None
anomaly_model = None
scaler = None

def load_models():
    global model, anomaly_model, scaler
    try:
        model = joblib.load(MODEL_PATH)
        anomaly_model = joblib.load(ANOMALY_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("Models and Scaler loaded successfully")
    except Exception as e:
        print(f"Error loading models: {e}")

load_models()

# In-memory tracker for predictive risk scoring
threat_tracker = {}

@app.route("/stats", methods=["GET"])
def fetch_stats():
    return jsonify({"total_logs": get_log_count()})

@app.route("/logs", methods=["GET"])
def fetch_logs():
    return jsonify(get_logs())

@app.route("/blacklist", methods=["GET"])
def fetch_blacklist():
    return jsonify(get_blacklist())

@app.route("/predict", methods=["POST"])
def predict():
    if model is None: return jsonify({"error": "Model not loaded"}), 500
    
    data = request.json
    source_ip = data.get("source_ip", f"192.168.1.{random.randint(100, 254)}")

    try:
        df_input = pd.DataFrame([data])
        # Feature alignment
        for col in model.feature_names_in_:
            if col not in df_input.columns: df_input[col] = 0
        df_classifier = df_input[model.feature_names_in_]
        
        for col in anomaly_model.feature_names_in_:
            if col not in df_input.columns: df_input[col] = 0
        df_anomaly = df_input[anomaly_model.feature_names_in_]

        X_scaled = scaler.transform(df_classifier)
        prediction = str(model.predict(X_scaled)[0])
        
        probs = model.predict_proba(X_scaled)[0]
        base_risk = round(float(np.max(probs)), 2)

        if prediction == "BENIGN":
            base_risk = max(0.01, min(0.15, (1.0 - base_risk) + random.uniform(-0.02, 0.02)))
            severity = "Low"
        else:
            severity = "High"

        # Behavioral Anomaly
        is_anomaly = 1 if int(anomaly_model.predict(df_anomaly)[0]) == -1 else 0
        if is_anomaly and prediction == "BENIGN":
            prediction = "ANOMALY (Unseen Pattern)"
            severity = "Medium"
            base_risk = max(base_risk, 0.45)

        # Risk Escalation
        if source_ip not in threat_tracker: threat_tracker[source_ip] = []
        threat_tracker[source_ip].append(base_risk)
        threat_tracker[source_ip] = threat_tracker[source_ip][-5:]
        if len([r for r in threat_tracker[source_ip] if r > 0.3]) >= 3 and severity != "High":
            prediction = "RECONNAISSANCE (Escalated)"
            severity = "High"
            base_risk = 0.85
            
        # Explainable AI (XAI)
        feature_importance = []
        if prediction != "BENIGN":
            diffs = np.abs(X_scaled[0])
            top_indices = np.argsort(diffs)[-3:][::-1]
            feature_importance = [model.feature_names_in_[i] for i in top_indices]

        if severity == "High" or base_risk > 0.8:
            blacklist_ip(source_ip, f"Auto Block: {prediction}")

        summary = f"Top Features: {', '.join(feature_importance)}" if feature_importance else f"Port: {data.get('Destination Port')}"
        log_prediction(source_ip, prediction, severity, base_risk, summary, is_anomaly)

        return jsonify({"attack_type": prediction, "severity": severity, "risk_score": base_risk})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- INTERNAL SIMULATOR THREAD ---
def run_simulation():
    print("Background Simulator Started...")
    try:
        data = pd.read_csv(DATASET_PATH)
        benign = data[data["Label"] == "BENIGN"]
        attack = data[data["Label"] != "BENIGN"]
        
        while True:
            # Pick a random sample
            row = attack.sample(1) if random.random() < 0.2 else benign.sample(1)
            payload = row.drop("Label", axis=1).iloc[0].to_dict()
            payload = {k: float(v) for k, v in payload.items()}
            
            # Post to self
            try:
                requests.post("http://localhost:5000/predict", json=payload, timeout=2)
            except: pass
            
            time.sleep(3) # Slowed down to save memory
    except Exception as e:
        print(f"Simulator Error: {e}")

# Start simulator in background
threading.Thread(target=run_simulation, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
