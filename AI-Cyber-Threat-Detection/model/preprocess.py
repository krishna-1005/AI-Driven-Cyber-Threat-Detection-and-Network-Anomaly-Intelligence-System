import pandas as pd
import numpy as np
import os

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Correct dataset paths
INPUT_PATH = os.path.join(BASE_DIR, "..", "dataset", "cicids.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "dataset", "cleaned_cicids.csv")

print(f"Loading dataset from {INPUT_PATH}...")

data = pd.read_csv(INPUT_PATH)

print("Dataset loaded successfully")
print("Shape:", data.shape)

# remove spaces from column names
data.columns = data.columns.str.strip()

# remove missing values
data = data.dropna()

# replace infinite values
data.replace([np.inf, -np.inf], np.nan, inplace=True)

# drop rows containing those values
data = data.dropna()

print("After cleaning:", data.shape)


# convert label column to string
data["Label"] = data["Label"].astype(str)

# save cleaned dataset
data.to_csv(OUTPUT_PATH, index=False)

print("Cleaned dataset saved successfully")