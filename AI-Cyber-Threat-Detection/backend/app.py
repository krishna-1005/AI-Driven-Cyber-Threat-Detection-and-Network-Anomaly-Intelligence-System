import os
import random
import numpy as np
from flask import Flask, request, jsonify
import joblib
import pandas as pd
from database import init_db, log_prediction, get_logs

app = Flask(__name__)
init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "cyber_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "..", "model", "scaler.pkl")

print(f"Loading models...")
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("Models and Scaler loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    scaler = None

# Mock list of suspicious IPs for simulation
IP_LIST = ["192.168.1.10", "10.0.0.5", "172.16.5.85", "203.0.113.4", "198.51.100.12"]

@app.route("/logs", methods=["GET"])
def fetch_logs():
    logs = get_logs()
    return jsonify(logs)

@app.route("/predict", methods=["POST"])
def predict():
    if model is None or scaler is None:
        return jsonify({"error": "System not fully initialized"}), 500

    data = request.json
    try:
        # 1. Input Processing
        df = pd.DataFrame([data])
        
        # Ensure we only use columns that the model was trained on
        if hasattr(model, "feature_names_in_"):
            # Fill missing columns with 0
            for col in model.feature_names_in_:
                if col not in df.columns:
                    df[col] = 0
            df = df[model.feature_names_in_]

        # 2. Precise Feature Scaling
        X_scaled = scaler.transform(df)

        # 3. Known Attack Detection (Supervised)
        prediction = str(model.predict(X_scaled)[0])
        
        # Calculate Risk Score using Prediction Probabilities
        probs = model.predict_proba(X_scaled)[0]
        # Get index of the predicted class
        class_idx = np.argmax(probs)
        risk_score = round(float(probs[class_idx]), 2)

        if prediction == "BENIGN":
            # Invert probability: high confidence BENIGN means low risk score
            risk_score = round(1.0 - risk_score, 2)
            # Add small jitter for realistic UI
            risk_score = max(0.01, min(0.15, risk_score + random.uniform(-0.02, 0.02)))
            severity = "Low"
        else:
            severity = "High"

        # Simulate a Source IP
        source_ip = random.choice(IP_LIST) if severity == "High" else f"192.168.1.{random.randint(100, 254)}"
        
        summary = f"Port: {data.get('Destination Port')} | Flow: {data.get('Flow Duration')}"
        
        # Log to Database
        log_prediction(source_ip, prediction, severity, risk_score, summary)

        return jsonify({
            "attack_type": prediction,
            "severity": severity,
            "risk_score": risk_score,
            "source_ip": source_ip
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)