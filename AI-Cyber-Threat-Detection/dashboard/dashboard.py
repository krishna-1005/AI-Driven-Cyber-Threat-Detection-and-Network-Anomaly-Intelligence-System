import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import plotly.express as px

# =============================
# CONFIG
# =============================

API_URL = "https://ai-driven-cyber-threat-detection-and.onrender.com/logs"

st.set_page_config(
    page_title="SENTINEL AI | Cyber Threat Intelligence",
    layout="wide",
    page_icon="🛡️"
)

# =============================
# STYLING
# =============================

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}

.metric-container {
    background: #161b22;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #30363d;
}

.threat-card {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    background: rgba(255,75,75,0.1);
    border-left: 5px solid #ff4b4b;
}

</style>
""", unsafe_allow_html=True)

# =============================
# FETCH LOGS
# =============================

def fetch_logs():
    try:
        r = requests.get(API_URL)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

# =============================
# HEADER
# =============================

st.title("🛡️ SENTINEL AI — Cyber Threat Command Center")

st.caption(
    f"Live Monitoring | Last Update: {datetime.now().strftime('%H:%M:%S')}"
)

# =============================
# LOAD DATA
# =============================

logs = fetch_logs()

if not logs:
    st.warning("Waiting for traffic data...")
    st.stop()

df = pd.DataFrame(logs)

# rename columns for UI
df = df.rename(columns={
    "attack_type": "Attack Type",
    "severity": "Severity",
    "risk_score": "Risk Score",
    "source_ip": "Source IP"
})

# =============================
# METRICS
# =============================

col1, col2, col3, col4 = st.columns(4)

total = len(df)
attacks = len(df[df["Severity"] == "High"])
benign = len(df[df["Severity"] == "Low"])
avg_risk = df["Risk Score"].mean()

with col1:
    st.metric("Total Traffic", total)

with col2:
    st.metric("Detected Attacks", attacks)

with col3:
    st.metric("Benign Traffic", benign)

with col4:
    st.metric("Avg Risk Score", round(avg_risk,2))

st.divider()

# =============================
# CHARTS
# =============================

c1, c2 = st.columns(2)

with c1:

    st.subheader("Attack Type Distribution")

    attack_df = df[df["Attack Type"] != "BENIGN"]

    if not attack_df.empty:

        chart = px.pie(
            attack_df,
            names="Attack Type",
            hole=0.4
        )

        st.plotly_chart(chart, use_container_width=True)

    else:
        st.success("No attacks detected")


with c2:

    st.subheader("Risk Score Trend")

    trend = df.tail(30)

    fig = px.line(
        trend,
        y="Risk Score"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# =============================
# HIGH RISK ALERTS
# =============================

st.subheader("🚨 Critical Alerts")

alerts = df[df["Severity"] == "High"].head(10)

if alerts.empty:

    st.success("No active threats")

else:

    for _, row in alerts.iterrows():

        st.markdown(f"""
        <div class="threat-card">
        <b>{row['Attack Type']} detected</b><br>
        Source IP: {row['Source IP']}<br>
        Risk Score: {row['Risk Score']}
        </div>
        """, unsafe_allow_html=True)

# =============================
# FULL LOG TABLE
# =============================

st.subheader("📜 Network Log")

st.dataframe(df, use_container_width=True)

# =============================
# AUTO REFRESH
# =============================

time.sleep(3)
st.rerun()