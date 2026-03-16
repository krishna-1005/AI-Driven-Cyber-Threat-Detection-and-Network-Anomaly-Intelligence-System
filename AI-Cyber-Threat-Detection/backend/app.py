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

model = None
anomaly_model = None
scaler = None
threat_tracker = {}

def load_models():
    global model, anomaly_model, scaler
    try:
        model = joblib.load(MODEL_PATH)
        anomaly_model = joblib.load(ANOMALY_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("Backend: Models Loaded")
    except Exception as e:
        print(f"Backend Error: {e}")

load_models()

@app.route("/health", methods=["GET"])
def health(): return jsonify({"status": "ready" if model else "loading"})

@app.route("/stats", methods=["GET"])
def fetch_stats(): return jsonify({"total_logs": get_log_count()})

@app.route("/logs", methods=["GET"])
def fetch_logs(): return jsonify(get_logs(limit=100))

@app.route("/blacklist", methods=["GET"])
def fetch_blacklist(): return jsonify(get_blacklist())

@app.route("/predict", methods=["POST"])
def predict():
    if model is None: return jsonify({"error": "Init..."}), 500
    data = request.json
    source_ip = data.get("source_ip", f"192.168.1.{random.randint(100, 254)}")
    try:
        df_input = pd.DataFrame([data])
        X_scaled = scaler.transform(df_input[model.feature_names_in_])
        prediction = str(model.predict(X_scaled)[0])
        base_risk = round(float(np.max(model.predict_proba(X_scaled)[0])), 2)
        severity = "High" if prediction != "BENIGN" else "Low"
        is_anomaly = 1 if int(anomaly_model.predict(df_input[anomaly_model.feature_names_in_])[0]) == -1 else 0
        
        # XAI logic
        feature_importance = []
        if prediction != "BENIGN":
            diffs = np.abs(X_scaled[0])
            top_indices = np.argsort(diffs)[-3:][::-1]
            feature_importance = [model.feature_names_in_[i] for i in top_indices]
        
        summary = f"Top Features: {', '.join(feature_importance)}" if feature_importance else "Normal Activity"

        if severity == "High" or base_risk > 0.8:
            blacklist_ip(source_ip, f"Auto Block: {prediction}")

        log_prediction(source_ip, prediction, severity, base_risk, summary, is_anomaly)
        return jsonify({"status": "ok"})
    except: return jsonify({"status": "err"}), 500

def run_simulation():
    time.sleep(10)
    try:
        data = pd.read_csv(DATASET_PATH, nrows=500)
        while True:
            row = data.sample(1).drop("Label", axis=1).iloc[0].to_dict()
            row = {k: float(v) for k, v in row.items()}
            try: requests.post("http://127.0.0.1:5000/predict", json=row, timeout=1)
            except: pass
            time.sleep(4)
    except: pass

threading.Thread(target=run_simulation, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
