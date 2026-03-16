import json
import pandas as pd
import requests

data = pd.read_csv("dataset/cleaned_cicids.csv")
print("Data loaded")
try:
    for i in range(5):
        row = data.iloc[i].drop("Label").to_dict()
        response = requests.post("http://127.0.0.1:10000/predict", json=row)
        print(response.status_code, response.json())
except Exception as e:
    print(f"Error: {e}")
