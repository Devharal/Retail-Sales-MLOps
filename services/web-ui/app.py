import streamlit as st
import requests
from datetime import datetime
from datetime import datetime, timedelta
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine


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
            "store": store_id,
            "date": date.strftime("%Y-%m-%d"),
            "promo": promo,
            "stateholiday": holiday,
            "schoolholiday": school
        }
        response = requests.post("http://nginx/predict", json=payload)
        response.raise_for_status()
        if response.ok:
            st.success(f"✅ Predicted Sales: ₹{response.json()['predicted_sales']:.2f}")
        else:
            st.error("❌ Prediction failed!")

# # Main area
# st.markdown("### 🧠 Current Model Info")
# info = requests.get("http://localhost/forecast/model/info")
# if info.ok:
#     st.json(info.json())
# else:
#     st.warning("Could not fetch model info.")

# Retrain model section
st.markdown("### 🔁 Retrain Model")
if st.button("🚀 Retrain Now"):
    train_payload = {
        "store": 6,
        "start_date": "2025-02-11",
        "end_date": "2025-06-29"
    }
    try:
        train_response = requests.post("http://nginx/train", json=train_payload)
        train_response.raise_for_status()
        if train_response.ok:
            result = train_response.json()
            st.success(f"🎯 Retrain successful! Run ID: {result.get('run_id', 'N/A')}")
            st.json(result.get("metrics", {}))
        else:
            st.error(f"❌ Retrain failed: {train_response.text}")
    except Exception as e:
        st.error(f"❌ Error occurred: {e}")




# ---------- Database ----------
@st.cache_resource
def get_engine():
    return create_engine("postgresql://postgres:SuperSecurePwdHere@postgres:5432/postgres")

def get_data(query: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(query, engine)

# ---------- Autorefresh ----------
st_autorefresh(interval=5000, key="refresh")  # refresh every 5 seconds

# ---------- Historic Sales ----------
st.markdown("### 🗂️ Historic Sales (Last 7 Days)")

hist_query = """
SELECT date AS timestamp, store, sales
FROM rossman_sales
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date ASC;
"""
df_hist = get_data(hist_query)

if df_hist.empty:
    st.warning("No historic sales data found.")
else:
    chart_hist = alt.Chart(df_hist).mark_line().encode(
        x="timestamp:T",
        y="sales:Q",
        color="store:N"
    ).properties(
        title="Sales per Store (Last 7 Days)",
        height=400
    )
    st.altair_chart(chart_hist, use_container_width=True)

# ---------- Live Sales ----------
st.markdown("### 🔴 Live Sales (Last Minute)")

live_query = """
SELECT created_at AS timestamp, store, sales
FROM rossman_sales
WHERE created_at >= NOW() - INTERVAL '1 minute'
ORDER BY created_at DESC;
"""
df_live = get_data(live_query)

if df_live.empty:
    st.info("No recent sales recorded in the last minute.")
else:
    st.dataframe(df_live.head(10))  # show raw data
    chart_live = alt.Chart(df_live).mark_line(point=True).encode(
        x="timestamp:T",
        y="sales:Q",
        color="store:N"
    ).properties(
        title="Live Sales Activity (Last 1 Minute)",
        height=300
    )
    st.altair_chart(chart_live, use_container_width=True)