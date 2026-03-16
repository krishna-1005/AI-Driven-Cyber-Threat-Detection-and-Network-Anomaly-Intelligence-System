import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(
    page_title="SENTINEL AI | Cyber Threat Intelligence",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- PREMIUM STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    div[data-testid="stMetricValue"] { font-size: 2rem !important; color: #ffffff !important; }
    .metric-container {
        background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: transform 0.2s;
    }
    .metric-container:hover { border-color: #58a6ff; transform: translateY(-2px); }
    .threat-card {
        padding: 15px; border-radius: 10px; margin-bottom: 12px;
        background: rgba(255, 75, 75, 0.1); border: 1px solid rgba(255, 75, 75, 0.3); border-left: 5px solid #ff4b4b;
    }
    .anomaly-card {
        padding: 15px; border-radius: 10px; margin-bottom: 12px;
        background: rgba(255, 165, 0, 0.1); border: 1px solid rgba(255, 165, 0, 0.3); border-left: 5px solid #ffa500;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; color: #8b949e; }
    .stTabs [aria-selected="true"] { color: #58a6ff !important; border-bottom: 2px solid #58a6ff !important; }
</style>
""", unsafe_allow_html=True)

# --- DATA FETCHING ---
API_BASE = "http://localhost:5000"

def get_logs():
    try:
        r = requests.get(f"{API_BASE}/logs", timeout=2)
        return r.json() if r.status_code == 200 else []
    except: return []

def get_blacklist():
    try:
        r = requests.get(f"{API_BASE}/blacklist", timeout=2)
        return r.json() if r.status_code == 200 else []
    except: return []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>SENTINEL AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Intelligent Cyber Defense</p>", unsafe_allow_html=True)
    st.divider()
    status = st.empty()
    status.markdown("🟢 **System: Online**")
    auto_refresh = st.toggle("Live Monitoring", value=False)
    refresh_rate = st.slider("Interval (s)", 1, 10, 3)
    st.divider()
    with st.expander("Intelligence Specs"):
        st.write("🧠 **Model**: Hybrid RF + Isolation Forest")
        st.write("🛡️ **Response**: Automated IP Blacklisting")
        st.write("📈 **Forensics**: Behavioral Anomaly Score")

# --- DATA PROCESSING ---
logs_data = get_logs()

df = pd.DataFrame(
    logs_data,
    columns=["Time", "Source IP", "Attack Type", "Severity", "Risk Score", "Summary", "Is Anomaly"]
)

# Demo fallback if API returns no data
if df.empty:
    st.info("Demo Mode: Displaying simulated cyber threat intelligence.")

    df = pd.DataFrame([
        ["2026-03-16 10:21","203.0.113.5","DDoS","High",0.92,"Port 443 flood",0],
        ["2026-03-16 10:23","192.168.1.15","Port Scan","Medium",0.61,"Recon attempt",1],
        ["2026-03-16 10:25","198.51.100.9","BENIGN","Low",0.07,"Normal traffic",0],
        ["2026-03-16 10:27","172.16.5.2","Brute Force","High",0.88,"Login attempts",0],
        ["2026-03-16 10:29","203.0.113.77","SQL Injection","High",0.95,"Web exploit attempt",0]
    ],
    columns=["Time","Source IP","Attack Type","Severity","Risk Score","Summary","Is Anomaly"])

# --- TOP METRICS ---
st.title("🛡️ Sentinel Intelligence Dashboard")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Total Flows", f"{len(df):,}")
    st.markdown('</div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Anomalies Identified", len(df[df["Is Anomaly"] == 1]))
    st.markdown('</div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    threats = len(df[df["Severity"] == "High"])
    st.metric("Threats Mitigated", threats, delta=threats, delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Avg Risk Index", f"{df['Risk Score'].mean():.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "🕵️ Forensics", "🛡️ Mitigation", "📜 Full Logs"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Intelligence Distribution")
        counts = df["Attack Type"].value_counts().reset_index()
        counts.columns = ["Attack Type","count"]
        fig = px.pie(counts, values='count', names='Attack Type', hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Behavioral Risk Velocity")
        fig = px.area(df.tail(50), x=range(len(df.tail(50))), y="Risk Score", color_discrete_sequence=['#58a6ff'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_visible=False, font_color="white")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Behavioral Anomaly Forensics")
    anomalies = df[df["Is Anomaly"] == 1].head(10)
    if anomalies.empty:
        st.success("No behavioral anomalies detected.")
    else:
        for _, row in anomalies.iterrows():
            st.markdown(f"""
            <div class="anomaly-card">
                <strong>⚠️ Behavioral Anomaly Detected</strong> | Risk: {row['Risk Score']}<br>
                Source: {row['Source IP']} | Time: {row['Time']} | Type: {row['Attack Type']}<br>
                <em>System Analysis: Unusual packet pattern identified via Unsupervised Learning.</em>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.subheader("Automated Mitigation Console")
    bl_data = get_blacklist()
    if bl_data:
        bl_df = pd.DataFrame(bl_data, columns=["Blocked IP", "Reason", "Timestamp"])
        st.table(bl_df)
    else:
        st.info("No active IP blocks.")

with tab4:
    st.dataframe(df, use_container_width=True, hide_index=True)

if auto_refresh:
    time.sleep(refresh_rate); st.rerun()
