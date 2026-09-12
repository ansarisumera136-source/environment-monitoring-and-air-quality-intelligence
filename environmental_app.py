import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Environmental Monitoring", page_icon="🌍", layout="wide")

# Load data and model
try:
    df = pd.read_csv("air_quality.csv")
    df["Date"] = pd.to_datetime(df["Date"])
except FileNotFoundError:
    st.error("air_quality.csv not found in the repository root. Upload the dataset or place it in the repo before running the app.")
    st.stop()

try:
    model = joblib.load("aqi_model.pkl")
except Exception:
    model = None

# Utility
def get_aqi_category(aqi: float) -> str:
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"

# App UI
st.title("🌍 Environmental Monitoring and Air Quality Intelligence")
st.write("Interactive platform for air-quality analysis and AQI prediction.")

st.sidebar.header("Dashboard Controls")
if "City" not in df.columns:
    st.error("'City' column not found in air_quality.csv. Add a City column to use city-based filtering.")
    st.stop()

city = st.sidebar.selectbox("Select City", sorted(df["City"].unique()))
city_data = df[df["City"] == city].copy().sort_values("Date")

st.header("AQI Prediction")
col1, col2, col3 = st.columns(3)

with col1:
    pm25 = st.number_input("PM2.5", min_value=0.0, value=50.0)
    pm10 = st.number_input("PM10", min_value=0.0, value=80.0)

with col2:
    no2 = st.number_input("NO2", min_value=0.0, value=40.0)
    so2 = st.number_input("SO2", min_value=0.0, value=20.0)

with col3:
    co = st.number_input("CO", min_value=0.0, value=1.0)
    o3 = st.number_input("O3", min_value=0.0, value=30.0)

if st.button("Predict AQI"):
    input_data = np.array([[pm25, pm10, no2, so2, co, o3]])
    if model is None:
        st.error("Model not available. Run training first (python train_model.py) to produce aqi_model.pkl.")
    else:
        prediction = float(model.predict(input_data)[0])
        category = get_aqi_category(prediction)
        st.metric("Predicted AQI", round(prediction, 2))
        st.subheader(f"AQI Category: {category}")

st.header("Pollutant Input Visualization")
pollutant_data = pd.DataFrame({
    "Pollutant": ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"],
    "Value": [pm25, pm10, no2, so2, co, o3]
}).set_index("Pollutant")

st.bar_chart(pollutant_data)

st.header("Historical AQI Trend")
if "AQI" in city_data.columns:
    historical = city_data.set_index("Date")
    st.line_chart(historical["AQI"])
else:
    st.warning("AQI column not found in dataset; historical trend unavailable.")

st.header("Pollutant Trend Analysis")
selected_pollutant = st.selectbox("Select Pollutant", ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"])
if selected_pollutant in city_data.columns:
    st.line_chart(city_data.set_index("Date")[selected_pollutant])
else:
    st.warning(f"{selected_pollutant} column not found in dataset.")

st.header("Environmental Matrix")
if not city_data.empty:
    latest = city_data.iloc[-1]
    pollutants = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
    matrix = pd.DataFrame({
        "Parameter": pollutants,
        "Value": [latest.get(p, np.nan) for p in pollutants]
    })
    st.dataframe(matrix, use_container_width=True)

# Optional: show correlation matrix
if st.checkbox("Show correlation matrix"):
    numeric_cols = [c for c in ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3", "AQI"] if c in df.columns]
    corr = df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# Feature importance (if model has attribute)
if st.checkbox("Show model feature importance"):
    if model is None:
        st.warning("Model not loaded.")
    else:
        if hasattr(model, "feature_importances_"):
            importance = pd.DataFrame({
                "Feature": ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"],
                "Importance": model.feature_importances_
            }).sort_values("Importance", ascending=False)
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(x="Importance", y="Feature", data=importance, ax=ax)
            ax.set_title("Feature Importance")
            st.pyplot(fig)
        else:
            st.info("Loaded model does not expose feature_importances_.")
