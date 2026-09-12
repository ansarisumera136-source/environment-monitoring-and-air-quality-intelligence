import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Load data
try:
    df = pd.read_csv("air_quality.csv")
except FileNotFoundError:
    raise FileNotFoundError("air_quality.csv not found in the repository root. Add the dataset before running this script.")

# Basic cleaning: drop duplicates, parse dates, fill numeric NaNs with median
df = df.drop_duplicates().copy()
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
numeric_cols = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3", "AQI"]
for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Fill numeric missing values with median of each column
present_numeric = [c for c in numeric_cols if c in df.columns]
if len(present_numeric) == 0:
    raise ValueError("No numeric pollutant columns found in air_quality.csv")

df[present_numeric] = df[present_numeric].fillna(df[present_numeric].median())

# Prepare features/target
features = [f for f in ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"] if f in df.columns]
if "AQI" not in df.columns:
    raise ValueError("Target column 'AQI' not found in air_quality.csv")

X = df[features]
y = df["AQI"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train a Gradient Boosting model
gb = GradientBoostingRegressor(n_estimators=200, random_state=42)
gb.fit(X_train, y_train)

# Evaluate
y_pred = gb.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("Gradient Boosting performance:")
print(f"MAE: {mae:.3f}, RMSE: {rmse:.3f}, R2: {r2:.3f}")

# Save model
joblib.dump(gb, "aqi_model.pkl")
print("Saved model to aqi_model.pkl")
