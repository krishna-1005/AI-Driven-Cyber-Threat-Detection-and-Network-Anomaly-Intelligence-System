import pandas as pd
import requests
import time
import os

# ==============================
# CONFIGURATION
# ==============================

# Your deployed API endpoint
API_URL = "https://ai-driven-cyber-threat-detection-and.onrender.com/predict"

# Get current script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dataset path
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "cleaned_cicids.csv")

print(f"Loading dataset from: {DATASET_PATH}")

# ==============================
# LOAD DATASET
# ==============================

data = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully")
print("Total rows:", data.shape[0])

# Split normal and attack traffic
benign = data[data["Label"] == "BENIGN"]
attack = data[data["Label"] != "BENIGN"]

print("Benign samples:", len(benign))
print("Attack samples:", len(attack))

print("\nStarting network traffic simulation...\n")

# ==============================
# SIMULATION LOOP
# ==============================

for i in range(50):

    # Every 5th packet is an attack
    if i % 5 == 0:
        row = attack.sample(1).drop("Label", axis=1)
        traffic_type = "ATTACK"
    else:
        row = benign.sample(1).drop("Label", axis=1)
        traffic_type = "NORMAL"

    # Convert row to dictionary payload
    payload = row.iloc[0].to_dict()

    try:
        response = requests.post("https://ai-driven-cyber-threat-detection-and.onrender.com/predict",json=payload)

        if response.status_code == 200:
            result = response.json()
            print(f"{traffic_type} → {result}")
        else:
            print("Server Error:", response.status_code)

    except Exception as e:
        print("Request failed:", e)

    # Wait 1 second before next packet
    time.sleep(1)

print("\nSimulation finished.")