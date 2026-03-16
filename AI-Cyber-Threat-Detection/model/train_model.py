import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "cleaned_cicids.csv")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "cyber_model.pkl")
SCALER_SAVE_PATH = os.path.join(BASE_DIR, "scaler.pkl")

print(f"Loading cleaned dataset from {DATASET_PATH}...")
data = pd.read_csv(DATASET_PATH)

# remove spaces from column names
data.columns = data.columns.str.strip()

# Remove features with zero variance (no information)
data = data.loc[:, (data != data.iloc[0]).any()]

# split features and label
X = data.drop("Label", axis=1)
y = data["Label"]

print("Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("Splitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print("Training Advanced RandomForest model (Balanced)...")
# class_weight='balanced' handles the 98% Benign vs 2% Attack imbalance
model = RandomForestClassifier(
    n_estimators=150, 
    max_depth=20,
    class_weight='balanced', 
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Save the feature names the model expects
model.feature_names_in_ = X.columns.tolist()

print("Training completed. Saving artifacts...")
joblib.dump(model, MODEL_SAVE_PATH)
joblib.dump(scaler, SCALER_SAVE_PATH)

print(f"Model and Scaler saved successfully.")