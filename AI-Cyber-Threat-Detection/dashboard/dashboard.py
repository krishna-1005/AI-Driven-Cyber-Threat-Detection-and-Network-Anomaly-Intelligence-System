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
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #ffffff !important;
    }
    
    .metric-container {
        background: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    
    .metric-container:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }

    /* Alert Cards */
    .threat-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 12px;
        background: rgba(255, 75, 75, 0.1);
        border: 1px solid rgba(255, 75, 75, 0.3);
        border-left: 5px solid #ff4b4b;
    }
    
    .benign-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 12px;
        background: rgba(46, 160, 67, 0.1);
        border: 1px solid rgba(46, 160, 67, 0.3);
        border-left: 5px solid #2ea043;
    }

    /* Tabs/Buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border: none;
        color: #8b949e;
    }

    .stTabs [aria-selected="true"] {
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff !important;
    }

    /* Dataframe Styling */
    .stDataFrame {
        border: 1px solid #30363d;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA FETCHING ---
def get_backend_logs():
    try:
        r = requests.get("http://127.0.0.1:5000/logs", timeout=2)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #58a6ff;'>SENTINEL AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Next-Gen Threat Detection</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # System Status
    status_col1, status_col2 = st.columns([1, 3])
    with status_col1:
        st.markdown("🟢")
    with status_col2:
        st.markdown("**Engine: Active**")
        
    st.divider()
    
    auto_refresh = st.toggle("Live Monitoring", value=True)
    refresh_rate = st.slider("Refresh Interval (s)", 1, 10, 3)
    
    st.divider()
    
    with st.expander("Risk Thresholds"):
        st.info("🔴 High: > 0.70\n\n🟡 Med: 0.30 - 0.70\n\n🟢 Low: < 0.30")

# --- MAIN CONTENT ---
st.title("🛡️ Threat Intelligence Command Center")
st.caption(f"Network Status: Monitoring Active | Last Heartbeat: {datetime.now().strftime('%H:%M:%S')}")

# Load Data
logs_data = get_backend_logs()
df = pd.DataFrame(logs_data, columns=["Time", "Source IP", "Attack Type", "Severity", "Risk Score", "Summary"])

if df.empty:
    st.warning("📡 Waiting for network traffic data... Ensure the simulator and backend are running.")
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()
    st.stop()

# --- TOP METRICS ---
m1, m2, m3, m4 = st.columns(4)

total_req = len(df)
high_risk_count = len(df[df["Severity"] == "High"])
avg_risk = df["Risk Score"].mean()
unique_attacks = df[df["Attack Type"] != "BENIGN"]["Attack Type"].nunique()

with m1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Total Flows", f"{total_req:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with m2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Avg Risk Score", f"{avg_risk:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

with m3:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Threats Blocked", high_risk_count, delta=f"{high_risk_count} total", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)

with m4:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Attack Vectors", unique_attacks)
    st.markdown('</div>', unsafe_allow_html=True)

st.write("") # Spacer

# --- ANALYTICS TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Real-time Analysis", "🕵️ Investigation", "📜 Audit Logs"])

with tab1:
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("Attack Vector Distribution")
        attack_counts = df[df["Attack Type"] != "BENIGN"]["Attack Type"].value_counts().reset_index()
        if not attack_counts.empty:
            fig = px.pie(attack_counts, values='count', names='Attack Type', 
                         hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                              font_color="#e0e0e0", margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("Clean Network: No attacks detected in recent history.")

    with c2:
        st.subheader("Risk Velocity")
        # Show last 30 risk scores
        risk_trend = df["Risk Score"].tail(30).reset_index()
        fig = px.area(risk_trend, x=risk_trend.index, y="Risk Score", 
                      color_discrete_sequence=['#58a6ff'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_visible=False, font_color="#e0e0e0", margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    a1, a2 = st.columns([2, 1])
    
    with a1:
        st.subheader("Critical Alerts")
        high_risk_df = df[df["Severity"] == "High"].head(10)
        
        if not high_risk_df.empty:
            for _, row in high_risk_df.iterrows():
                st.markdown(f"""
                <div class="threat-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: bold; color: #ff4b4b;">🚨 {row['Attack Type']} DETECTED</span>
                        <span style="font-size: 0.8rem; color: #8b949e;">{row['Time']}</span>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.9rem;">
                        <strong>Source IP:</strong> {row['Source IP']} | <strong>Risk:</strong> {row['Risk Score']} | <strong>{row['Summary']}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("All clear. Monitoring for suspicious activity...")

    with a2:
        st.subheader("Suspicious Entities")
        if not high_risk_df.empty:
            bad_ips = high_risk_df[["Source IP", "Attack Type"]].drop_duplicates()
            st.dataframe(bad_ips, hide_index=True, use_container_width=True)
        else:
            st.write("No malicious IPs identified.")

with tab3:
    st.subheader("Full Network Flow Log")
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- AUTO REFRESH ---
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()