import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px
import time

# =============================
# BACKEND API
# =============================

API_URL = "https://ai-driven-cyber-threat-detection-and.onrender.com/logs"

# =============================
# PAGE CONFIG
# =============================

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

.stApp{
background-color:#0e1117;
color:white;
}

.metric-card{
background:#161b22;
padding:20px;
border-radius:10px;
border:1px solid #30363d;
}

.alert-card{
background:rgba(255,75,75,0.1);
padding:15px;
border-left:5px solid red;
border-radius:8px;
margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# =============================
# FETCH DATA FROM BACKEND
# =============================

def fetch_logs():
    try:
        r = requests.get(API_URL, timeout=5)

        if r.status_code == 200:
            return r.json()

    except:
        pass

    return []


# =============================
# HEADER
# =============================

st.title("🛡️ SENTINEL AI — Threat Intelligence Command Center")

st.caption(
    f"Network Monitoring Active | Last Update: {datetime.now().strftime('%H:%M:%S')}"
)

# =============================
# LOAD DATA
# =============================

logs = fetch_logs()

if not logs:
    st.warning("📡 Waiting for network traffic data... Ensure simulator is running.")
    st.stop()

# backend returns list format
df = pd.DataFrame(
    logs,
    columns=[
        "Time",
        "Source IP",
        "Attack Type",
        "Severity",
        "Risk Score",
        "Summary"
    ]
)

# =============================
# METRICS
# =============================

total_traffic = len(df)

attacks = len(df[df["Severity"] == "High"])

benign = len(df[df["Attack Type"] == "BENIGN"])

avg_risk = df["Risk Score"].mean()

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.metric("Total Traffic", total_traffic)

with c2:
    st.metric("Detected Attacks", attacks)

with c3:
    st.metric("Benign Traffic", benign)

with c4:
    st.metric("Average Risk Score", round(avg_risk,2))


st.divider()

# =============================
# CHARTS
# =============================

col1,col2 = st.columns(2)

# Attack Distribution
with col1:

    st.subheader("Attack Distribution")

    attack_df = df[df["Attack Type"] != "BENIGN"]

    if not attack_df.empty:

        fig = px.pie(
            attack_df,
            names="Attack Type",
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)

    else:

        st.success("No attacks detected")


# Risk Score Trend
with col2:

    st.subheader("Risk Score Trend")

    trend = df.tail(30)

    fig = px.line(
        trend,
        y="Risk Score"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# =============================
# ALERTS
# =============================

st.subheader("🚨 Critical Threat Alerts")

alerts = df[df["Severity"] == "High"].head(10)

if alerts.empty:

    st.success("No active threats detected")

else:

    for _,row in alerts.iterrows():

        st.markdown(f"""
        <div class="alert-card">

        <b>{row['Attack Type']} Detected</b><br>

        Source IP : {row['Source IP']} <br>

        Risk Score : {row['Risk Score']} <br>

        {row['Summary']}

        </div>
        """, unsafe_allow_html=True)


# =============================
# NETWORK LOG TABLE
# =============================

st.subheader("📜 Full Network Log")

st.dataframe(df, use_container_width=True)


# =============================
# AUTO REFRESH
# =============================

time.sleep(3)

st.rerun()