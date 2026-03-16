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

# Global variables
model = None
anomaly_model = None
scaler = None
threat_tracker = {}

def load_models():
    global model, anomaly_model, scaler
    try:
        # Load models using mmap_mode to save RAM if supported
        model = joblib.load(MODEL_PATH)
        anomaly_model = joblib.load(ANOMALY_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("Models loaded successfully")
    except Exception as e:
        print(f"Error loading models: {e}")

load_models()

@app.route("/stats", methods=["GET"])
def fetch_stats():
    return jsonify({"total_logs": get_log_count()})

@app.route("/logs", methods=["GET"])
def fetch_logs():
    return jsonify(get_logs(limit=100)) # Reduced limit for memory

@app.route("/predict", methods=["POST"])
def predict():
    if model is None: return jsonify({"error": "Init..."}), 500
    data = request.json
    source_ip = data.get("source_ip", f"192.168.1.{random.randint(100, 254)}")
    try:
        # Minimize DF size
        df_input = pd.DataFrame([data])
        X_scaled = scaler.transform(df_input[model.feature_names_in_])
        prediction = str(model.predict(X_scaled)[0])
        base_risk = round(float(np.max(model.predict_proba(X_scaled)[0])), 2)
        
        severity = "High" if prediction != "BENIGN" else "Low"
        is_anomaly = 1 if int(anomaly_model.predict(df_input[anomaly_model.feature_names_in_])[0]) == -1 else 0
        
        log_prediction(source_ip, prediction, severity, base_risk, "Live Traffic", is_anomaly)
        return jsonify({"status": "ok"})
    except: return jsonify({"status": "err"}), 500

def run_simulation():
    print("Simulator starting in 15s...")
    time.sleep(15) # Give system time to settle
    try:
        # Load only 500 rows to save memory instead of the whole file
        data = pd.read_csv(DATASET_PATH, nrows=500)
        while True:
            row = data.sample(1).drop("Label", axis=1).iloc[0].to_dict()
            row = {k: float(v) for k, v in row.items()}
            try: requests.post("http://localhost:5000/predict", json=row, timeout=1)
            except: pass
            time.sleep(5) # Slower simulation = lower CPU/RAM
    except Exception as e: print(f"Sim error: {e}")

threading.Thread(target=run_simulation, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
