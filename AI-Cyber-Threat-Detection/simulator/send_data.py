import pandas as pd
import requests
import time
import os

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Correct dataset path
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "cleaned_cicids.csv")

print(f"Loading cleaned dataset from {DATASET_PATH}...")

data = pd.read_csv(DATASET_PATH)

print("Dataset loaded:", data.shape)

# split normal and attack traffic
benign = data[data["Label"] == "BENIGN"]
attack = data[data["Label"] != "BENIGN"]

print("Benign rows:", len(benign))
print("Attack rows:", len(attack))

print("Starting traffic simulation...")

for i in range(50):

    if i % 5 == 0:
        row = attack.sample(1).drop("Label", axis=1)
        traffic_type = "ATTACK"
    else:
        row = benign.sample(1).drop("Label", axis=1)
        traffic_type = "NORMAL"

    payload = row.iloc[0].to_dict()

    r = requests.post("http://127.0.0.1:5000/predict", json=payload)

    print(traffic_type, "→", r.json())

    time.sleep(1)