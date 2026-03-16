import pandas as pd
import requests
import time
import os
import itertools

# =====================================
# CONFIGURATION
# =====================================

# Change back to local URL for local testing as per user's earlier setup
API_URL = "http://127.0.0.1:5000/predict"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "cleaned_cicids.csv")

# =====================================
# LOAD DATASET
# =====================================

print("\nLoading dataset...")
data = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully")
print("Total rows:", len(data))

# split normal and attack traffic
benign = data[data["Label"] == "BENIGN"]
attack = data[data["Label"] != "BENIGN"]

print("Benign samples:", len(benign))
print("Attack samples:", len(attack))

print("\nStarting INFINITE traffic simulation... (Press Ctrl+C to stop)\n")

# =====================================
# SIMULATION
# =====================================

for i in itertools.count(1):
    try:
        # every 5th packet = attack
        if i % 5 == 0:
            row = attack.sample(1).drop("Label", axis=1)
            traffic_type = "ATTACK"
        else:
            row = benign.sample(1).drop("Label", axis=1)
            traffic_type = "NORMAL"

        payload = row.iloc[0].to_dict()

        # convert numpy types to python types
        payload = {k: float(v) for k, v in payload.items()}

        try:
            response = requests.post(
                API_URL,
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                print(f"[{i}] {traffic_type} → {result['attack_type']} (Risk: {result['risk_score']})")
            else:
                print(f"[{i}] Server Error ({response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"[{i}] Request failed: {e}")

        time.sleep(1)
        
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
        break
