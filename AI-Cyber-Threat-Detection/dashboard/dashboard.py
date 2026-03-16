import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="SENTINEL AI | Intelligence Dashboard", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")

# --- DATA FETCHING ---
API_BASE = "http://127.0.0.1:5000"
def api_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}/{endpoint}", timeout=2)
        return r.json() if r.status_code == 200 else None
    except: return None

def api_post(endpoint, data):
    try:
        r = requests.post(f"{API_BASE}/{endpoint}", json=data, timeout=2)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- SIDEBAR & MISSION CONTROL ---
with st.sidebar:
    st.markdown('<h1 style="color:#58a6ff; margin-bottom:0;">SENTINEL AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8b949e; margin-top:0;">Autonomous Intelligence Core</p>', unsafe_allow_html=True)
    
    health = api_get("health")
    if health and health["status"] == "ready": 
        st.success("🟢 Core Intelligence: Online")
    else: 
        st.warning("🟠 Synchronizing Core...")
    
    st.divider()
    
    st.subheader("🛠️ Mission Control")
    live_mon = st.toggle("Live Stream", value=True)
    
    # Sync Autonomous Defense with backend
    def_status = api_get("defense") or {"defense_mode": True}
    auto_def = st.toggle("Autonomous Defense", value=def_status["defense_mode"])
    if auto_def != def_status["defense_mode"]:
        api_post("defense", {"status": auto_def})
    
    st.divider()
    
    st.subheader("💻 Node Activity")
    sys_data = api_get("system") or {"cpu_usage": 0, "mem_usage": 0, "active_processes": 0}
    st.progress(sys_data["cpu_usage"]/100, text=f"Neural Load: {sys_data['cpu_usage']}%")
    st.progress(sys_data["mem_usage"]/100, text=f"Buffer Usage: {sys_data['mem_usage']}%")
    
    st.divider()
    if st.button("🚨 Simulate Breach Attempt", use_container_width=True, type="primary"):
        # Manual simulation of attack
        try:
            requests.post(f"{API_BASE}/predict", json={"Destination Port": 80, "Flow Duration": 100, "Total Fwd Packets": 10, "Total Backward Packets": 10, "Total Length of Fwd Packets": 1000, "Total Length of Bwd Packets": 1000, "Fwd Packet Length Max": 500, "Fwd Packet Length Min": 500, "Fwd Packet Length Mean": 500, "Fwd Packet Length Std": 0, "Bwd Packet Length Max": 500, "Bwd Packet Length Min": 500, "Bwd Packet Length Mean": 500, "Bwd Packet Length Std": 0, "Flow Bytes/s": 20, "Flow Packets/s": 0.2, "Flow IAT Mean": 10, "Flow IAT Std": 0, "Flow IAT Max": 10, "Flow IAT Min": 10, "Fwd IAT Total": 100, "Fwd IAT Mean": 10, "Fwd IAT Std": 0, "Fwd IAT Max": 10, "Fwd IAT Min": 10, "Bwd IAT Total": 100, "Bwd IAT Mean": 10, "Bwd IAT Std": 0, "Bwd IAT Max": 10, "Bwd IAT Min": 10, "Fwd PSH Flags": 0, "Bwd PSH Flags": 0, "Fwd URG Flags": 0, "Bwd URG Flags": 0, "Fwd Header Length": 20, "Bwd Header Length": 20, "Fwd Packets/s": 0.1, "Bwd Packets/s": 0.1, "Min Packet Length": 0, "Max Packet Length": 100, "Packet Length Mean": 50, "Packet Length Std": 0, "Packet Length Variance": 0, "FIN Flag Count": 0, "SYN Flag Count": 1, "RST Flag Count": 0, "PSH Flag Count": 0, "ACK Flag Count": 0, "URG Flag Count": 0, "CWE Flag Count": 0, "ECE Flag Count": 0, "Down/Up Ratio": 1, "Average Packet Size": 50, "Avg Fwd Segment Size": 50, "Avg Bwd Segment Size": 50, "Fwd Header Length.1": 20, "Fwd Avg Bytes/Bulk": 0, "Fwd Avg Packets/Bulk": 0, "Fwd Avg Bulk Rate": 0, "Bwd Avg Bytes/Bulk": 0, "Bwd Avg Packets/Bulk": 0, "Bwd Avg Bulk Rate": 0, "Subflow Fwd Packets": 10, "Subflow Fwd Bytes": 1000, "Subflow Bwd Packets": 10, "Subflow Bwd Bytes": 1000, "Init_Win_bytes_forward": 100, "Init_Win_bytes_backward": 100, "act_data_pkt_fwd": 5, "min_seg_size_forward": 20, "Active Mean": 0, "Active Std": 0, "Active Max": 0, "Active Min": 0, "Idle Mean": 0, "Idle Std": 0, "Idle Max": 0, "Idle Min": 0, "source_ip": f"MALICIOUS-{random.randint(10, 99)}"})
            st.toast("Breach attempt simulated!")
        except: pass

# --- AUTO-REFRESH ---
if live_mon:
    st_autorefresh(interval=2500, key="global_refresh")

# --- PREMIUM STYLING (Glassmorphism) ---

# --- DATA PROCESSING ---
stats = api_get("stats") or {"total_logs": 0}
logs_data = api_get("logs") or []
bl_data = api_get("blacklist") or []
df = pd.DataFrame(logs_data, columns=["Time", "Source IP", "Attack Type", "Severity", "Risk Score", "Summary", "Is Anomaly"])

if 'baseline' not in st.session_state:
    st.session_state.baseline = stats["total_logs"]
    st.session_state.start_time = datetime.now().strftime("%H:%M:%S")
live_total = max(0, stats["total_logs"] - st.session_state.baseline)

# --- MAIN DASHBOARD ---
st.markdown('<h1 class="hero-title">🛡️ Sentinel Intelligence Dashboard</h1>', unsafe_allow_html=True)
st.markdown(f"**Holistic Network Monitoring** | Session Active: {st.session_state.start_time}")

# --- EXECUTIVE SCORECARD ---
with st.container():
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
        st.subheader("📊 Executive Security Posture")
        if not df.empty:
            avg_risk = df['Risk Score'].mean() if not df.empty else 0.00
            threat_ratio = len(df[df["Severity"] == "High"]) / len(df) if len(df) > 0 else 0
            
            if avg_risk < 0.2 and threat_ratio < 0.05: grade, g_class, g_text = "A", "grade-a", "EXCELLENT: System integrity is optimal."
            elif avg_risk < 0.5: grade, g_class, g_text = "B", "grade-b", "STABLE: Minor anomalies detected, baseline holding."
            else: grade, g_class, g_text = "C", "grade-c", "CRITICAL: High risk detected. Immediate action required."
            
            gc1, gc2 = st.columns([1, 4])
            with gc1:
                st.markdown(f'<div class="grade-badge {g_class}">{grade}</div>', unsafe_allow_html=True)
            with gc2:
                st.markdown(f"**Status:** {g_text}")
                st.markdown(f"*Integrity Score: {(100 - avg_risk*100):.1f}%*")
                # Generate report content
                report_content = generate_exec_report(df, stats, live_total)
                st.download_button(
                    "📥 Download Executive Audit Report",
                    report_content,
                    file_name=f"Sentinel_Executive_Report_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        else:
            st.info("Calculating initial posture... awaiting network telemetry.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
        st.subheader("🤖 AI Core")
        if not df.empty:
            latest = df.iloc[0]
            advice = get_ai_advice(latest["Attack Type"], latest["Summary"])
            st.markdown(f'<div class="analyst-bubble">"{advice}"</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="analyst-bubble">"System standby. Monitoring for neural patterns..."</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- HERO METRICS ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.metric("Total Flows", f"{live_total}", delta=f"{stats['total_logs']} Overall")
    st.markdown('</div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    anomalies_count = len(df[df["Is Anomaly"] == 1])
    st.metric("AI Anomalies", anomalies_count, delta="Detected" if anomalies_count > 0 else "Clear", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    threats_count = len(df[df["Severity"] == "High"])
    st.metric("Active Threats", threats_count, delta="Blocked" if auto_def and threats_count > 0 else None, delta_color="normal")
    st.markdown('</div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    avg_risk = df['Risk Score'].mean() if not df.empty else 0.00
    st.metric("System Risk Index", f"{avg_risk:.2f}", delta=f"{'ELEVATED' if avg_risk > 0.5 else 'NORMAL'}", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)

# --- LIVE ACTIVITY ---
st.write("")
st.subheader("📡 Real-time Neural Activity Stream")
if not df.empty:
    # Stylized Dataframe
    display_df = df.head(10).copy()
    st.dataframe(display_df[["Time", "Source IP", "Attack Type", "Severity", "Risk Score"]], use_container_width=True, hide_index=True)
else: 
    st.info("Passive reconnaissance in progress... awaiting network packets.")

# --- ANALYTICS TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Threat Intelligence", "🕵️ Neural Forensics", "🛡️ Automated Mitigation", "📜 Event Logs"])

with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Threat Topology")
        if not df.empty:
            fig = px.pie(df, names='Attack Type', hole=0.6, color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="white", 
                margin=dict(t=0,b=0,l=0,r=0),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Insufficient data for topology.")
    
    with c2:
        st.subheader("📈 Risk Evolution (Real-time)")
        if not df.empty:
            # Risk trend over the last 100 events
            trend_df = df.iloc[::-1].tail(100) # Latest 100 in order
            fig = px.area(trend_df, x=trend_df.index, y='Risk Score', color_discrete_sequence=['#58a6ff'])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#8b949e", 
                margin=dict(t=30,b=0,l=0,r=0),
                xaxis_showgrid=False,
                yaxis_showgrid=True,
                yaxis_gridcolor='rgba(88, 166, 255, 0.1)',
                yaxis_range=[0, 1.1]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Calibrating risk sensors...")

with tab2:
    st.subheader("AI Behavioral Reasonings")
    anomalies = df[df["Is Anomaly"] == 1].head(10)
    if not anomalies.empty:
        for _, row in anomalies.iterrows():
            st.markdown(f"""
            <div class="forensic-card">
                <span class="badge badge-high">Anomaly Detected</span> 
                <strong>{row['Source IP']}</strong> | {row['Time']}
                <br><br>
                <p style="color:#8b949e; font-size:0.9rem;">AI Logic Analysis:</p>
                <code>{row['Summary']}</code>
                <div style="margin-top:10px; font-size:0.8rem; color:#58a6ff;">Confidence Score: {(row['Risk Score']*100):.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    else: 
        st.success("Clean Behavioral Profile. No anomalies detected in current buffer.")

with tab3:
    st.subheader("Network Containment")
    if bl_data: 
        st.table(pd.DataFrame(bl_data, columns=["Blocked IP", "Reason", "Timestamp"]).head(15))
    else: 
        st.info("Perimeter Intact. No active IP blocks.")

with tab4:
    st.subheader("Master Audit Log")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("📥 Export Forensic Audit", df.to_csv(index=False).encode('utf-8'), "sentinel_audit.csv", "text/csv")

# --- FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #8b949e; font-size: 0.8rem;">
    SENTINEL AI | Intelligence Dashboard v2.0-Premium | Powered by Gemini 3.1 Pro Core
</div>
""", unsafe_allow_html=True)

