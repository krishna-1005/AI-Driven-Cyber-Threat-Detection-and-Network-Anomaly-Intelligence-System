import pandas as pd
import requests
import time
import os

# =====================================
# CONFIGURATION
# =====================================

API_URL = "https://ai-driven-cyber-threat-detection-and.onrender.com/predict"

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

print("\nStarting traffic simulation...\n")

# =====================================
# SIMULATION
# =====================================

for i in range(50):

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
            timeout=10
        )

        if response.status_code == 200:

            result = response.json()

            print(f"{traffic_type} → {result}")

        else:

            print(f"Server Error ({response.status_code})")

    except requests.exceptions.RequestException as e:

        print("Request failed:", e)

    time.sleep(1)

print("\nSimulation finished.")