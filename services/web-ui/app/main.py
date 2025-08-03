import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")
st.title("📈 Retail Sales WebBI Dashboard")

# Sidebar for prediction input
with st.sidebar:
    st.header("Prediction Input")
    store_id = st.number_input("Store ID", min_value=1, value=1)
    date = st.date_input("Prediction Date", value=datetime.now().date())
    promo = st.selectbox("Promo", [0, 1])
    holiday = st.selectbox("State Holiday", ["0", "a", "b", "c"])
    school = st.selectbox("School Holiday", [0, 1])

    if st.button("📊 Predict"):
        payload = {
            "store_id": store_id,
            "date": date.strftime("%Y-%m-%d"),
            "promo": promo,
            "stateholiday": holiday,
            "schoolholiday": school
        }
        response = requests.post("http://localhost/forecast/predict", json=payload)
        if response.ok:
            st.success(f"✅ Predicted Sales: ₹{response.json()['predicted_sales']:.2f}")
        else:
            st.error("❌ Prediction failed!")

# Main area
st.markdown("### 🧠 Current Model Info")
info = requests.get("http://localhost/forecast/model/info")
if info.ok:
    st.json(info.json())
else:
    st.warning("Could not fetch model info.")

# Retrain model section
st.markdown("### 🔁 Retrain Model")
if st.button("🚀 Retrain Now"):
    train_payload = {
        "store_id": store_id,
        "start_date": None,
        "end_date": None,
        "params": {
            "max_depth": 6,
            "learning_rate": 0.1,
            "n_estimators": 100
        }
    }
    try:
        train_response = requests.post("http://localhost/train/train", json=train_payload)
        if train_response.ok:
            result = train_response.json()
            st.success(f"🎯 Retrain successful! Run ID: {result.get('run_id', 'N/A')}")
            st.json(result.get("metrics", {}))
        else:
            st.error(f"❌ Retrain failed: {train_response.text}")
    except Exception as e:
        st.error(f"❌ Error occurred: {e}")
