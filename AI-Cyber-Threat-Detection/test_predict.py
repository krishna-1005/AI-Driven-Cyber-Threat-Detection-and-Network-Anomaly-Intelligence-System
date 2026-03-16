import json
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.app import app

with app.app_context():
    data = pd.read_csv("dataset/cleaned_cicids.csv").iloc[0].drop("Label").to_dict()
    client = app.test_client()
    response = client.post("/predict", json=data)
    print(response.status_code)
    print(response.json)
