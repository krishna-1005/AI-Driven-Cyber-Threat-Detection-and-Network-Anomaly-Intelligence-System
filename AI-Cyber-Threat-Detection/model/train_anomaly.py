import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "cleaned_cicids.csv")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "anomaly_model.pkl")

print(f"Loading dataset for Anomaly Detection training...")
data = pd.read_csv(DATASET_PATH)

# remove spaces from column names
data.columns = data.columns.str.strip()

# Train ONLY on Benign data to learn "Normal" behavior
normal_data = data[data["Label"] == "BENIGN"].drop("Label", axis=1)

# Remove features with zero variance
normal_data = normal_data.loc[:, (normal_data != normal_data.iloc[0]).any()]

print(f"Training Isolation Forest on {len(normal_data)} normal samples...")
# contamination=0.01 assumes 1% of training data might be outliers
model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42, n_jobs=-1)
model.fit(normal_data)

# Save feature names
model.feature_names_in_ = normal_data.columns.tolist()

print("Anomaly Model trained. Saving...")
joblib.dump(model, MODEL_SAVE_PATH)
print(f"Anomaly model saved to {MODEL_SAVE_PATH}")
