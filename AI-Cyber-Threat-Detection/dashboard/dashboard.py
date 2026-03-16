import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- CONFIGURATION ---
st.set_page_config(
    page_title="SENTINEL AI | Cyber Threat Intelligence",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- GLOBAL REFRESH ---
st_autorefresh(interval=2000, key="global_refresh")

# --- FULL PAGE THREE.JS BACKGROUND & PREMIUM STYLING ---
# This script creates a fixed background canvas and a dark blue gradient theme.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Full Page Background */
    .stApp { 
        background: #050a15 !important; /* Deep Midnight Blue */
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* Make Streamlit containers transparent to show background */
    .main { background: transparent !important; }
    header { background: transparent !important; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { 
        background-color: rgba(10, 15, 25, 0.8) !important; 
        border-right: 1px solid rgba(88, 166, 255, 0.2); 
        backdrop-filter: blur(15px);
    }
    
    /* Header & Titles */
    h1, h2, h3 { 
        color: #58a6ff !important; 
        font-family: 'Inter', sans-serif; 
        font-weight: 700;
        letter-spacing: -0.5px;
        text-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
    }
    
    /* Metric Containers (Premium Glassmorphism) */
    div[data-testid="stMetricValue"] { 
        font-size: 2.2rem !important; 
        color: #ffffff !important; 
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .metric-container {
        background: rgba(22, 27, 34, 0.4); 
        padding: 24px; 
        border-radius: 20px; 
        border: 1px solid rgba(88, 166, 255, 0.15);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8); 
        backdrop-filter: blur(8px);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 10px;
    }
    
    .metric-container:hover { 
        border-color: rgba(88, 166, 255, 0.6); 
        transform: scale(1.02);
        background: rgba(88, 166, 255, 0.05);
    }

    /* Anomaly & Threat Cards */
    .threat-card, .anomaly-card {
        padding: 18px; border-radius: 12px; margin-bottom: 15px; border: 1px solid; backdrop-filter: blur(10px);
    }
    .threat-card { background: rgba(255, 75, 75, 0.08); border-color: rgba(255, 75, 75, 0.4); border-left: 6px solid #ff4b4b; }
    .anomaly-card { background: rgba(255, 165, 0, 0.08); border-color: rgba(255, 165, 0, 0.4); border-left: 6px solid #ffa500; }

    /* Pulse Animation */
    .status-pulse {
        display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #00ff00;
        box-shadow: 0 0 0 0 rgba(0, 255, 0, 1); animation: pulse-green 2s infinite; margin-right: 8px;
    }
    @keyframes pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
    }
</style>
""", unsafe_allow_html=True)

# --- THREE.JS FULL-SCREEN BACKGROUND COMPONENT ---
bg_code = """
<div id="three-bg" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; background: #050a15;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const container = document.getElementById('three-bg');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);

    const mouse = new THREE.Vector2();
    const target = new THREE.Vector2();

    // Neural Nodes
    const count = 200;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    
    for (let i = 0; i < count * 3; i++) {
        positions[i] = (Math.random() - 0.5) * 15;
        colors[i] = 0.34; // Base Blue (0.34, 0.65, 1.0)
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    const material = new THREE.PointsMaterial({
        size: 0.1,
        vertexColors: true,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending
    });

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    camera.position.z = 8;

    window.addEventListener('mousemove', (e) => {
        mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
    });

    function animate() {
        requestAnimationFrame(animate);
        target.x += (mouse.x - target.x) * 0.05;
        target.y += (mouse.y - target.y) * 0.05;

        const pos = points.geometry.attributes.position.array;
        const col = points.geometry.attributes.color.array;

        for (let i = 0; i < count; i++) {
            const x = pos[i * 3];
            const y = pos[i * 3 + 1];
            
            // Interaction: Distance from mouse
            const dx = x - target.x * 10;
            const dy = y - target.y * 6;
            const dist = Math.sqrt(dx*dx + dy*dy);
            
            if (dist < 3) {
                // Light Blue Glow on interaction
                col[i * 3] = 0.6;   // R
                col[i * 3 + 1] = 0.9; // G
                col[i * 3 + 2] = 1.0; // B
                pos[i * 3 + 2] = 0.5; // Pop forward
            } else {
                // Deep Blue Base
                col[i * 3] = 0.1;
                col[i * 3 + 1] = 0.2;
                col[i * 3 + 2] = 0.4;
                pos[i * 3 + 2] *= 0.9; // Sink back
            }
        }
        
        points.geometry.attributes.position.needsUpdate = true;
        points.geometry.attributes.color.needsUpdate = true;
        
        scene.rotation.y += 0.001;
        scene.rotation.x = target.y * 0.1;
        scene.rotation.y = target.x * 0.1;

        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
</script>
"""
components.html(bg_code, height=0) # Hidden component that runs the global background script

# --- LIVE MONITORING LOGIC ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now().strftime("%H:%M:%S")

# --- DATA FETCHING ---
API_BASE = "http://localhost:5000"

def get_stats():
    try:
        r = requests.get(f"{API_BASE}/stats", timeout=2)
        return r.json() if r.status_code == 200 else {"total_logs": 0}
    except: return {"total_logs": 0}

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
    
    st.markdown("""
        <div style='display: flex; align-items: center; justify-content: center; background: rgba(0,255,0,0.1); padding: 10px; border-radius: 8px; border: 1px solid rgba(0,255,0,0.2);'>
            <div class="status-pulse"></div>
            <span style='color: #00ff00; font-weight: 600;'>SYSTEM ACTIVE</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    auto_refresh = st.toggle("Live Monitoring", value=True)
    
    st.divider()
    with st.expander("Intelligence Specs"):
        st.write("🧠 **Model**: Hybrid RF + Isolation Forest")
        st.write("🛡️ **Response**: Automated IP Blacklisting")
        st.write("📈 **Forensics**: Behavioral Anomaly Score")

# --- DATA PROCESSING ---
stats = get_stats()
total_in_db = stats.get("total_logs", 0)
logs_data = get_logs()

df = pd.DataFrame(
    logs_data,
    columns=["Time", "Source IP", "Attack Type", "Severity", "Risk Score", "Summary", "Is Anomaly"]
)

if 'baseline_total' not in st.session_state:
    st.session_state.baseline_total = total_in_db

live_total = max(0, total_in_db - st.session_state.baseline_total)

# Demo fallback
if df.empty:
    df = pd.DataFrame([
        ["2026-03-16 10:21","203.0.113.5","DDoS","High",0.92,"Port 443 flood",0],
        ["2026-03-16 10:23","192.168.1.15","Port Scan","Medium",0.61,"Recon attempt",1],
        ["2026-03-16 10:25","198.51.100.9","BENIGN","Low",0.07,"Normal traffic",0],
        ["2026-03-16 10:27","172.16.5.2","Brute Force","High",0.88,"Login attempts",0],
        ["2026-03-16 10:29","203.0.113.77","SQL Injection","High",0.95,"Web exploit attempt",0]
    ], columns=["Time","Source IP","Attack Type","Severity","Risk Score","Summary","Is Anomaly"])

# --- TOP METRICS ---
st.title("🛡️ Sentinel Intelligence Dashboard")

st.markdown(f"""
    <div style='background: rgba(88, 166, 255, 0.1); padding: 10px 20px; border-radius: 10px; border: 1px solid rgba(88, 166, 255, 0.2); margin-bottom: 20px; display: flex; align-items: center;'>
        <div class="status-pulse"></div>
        <span style='color: #58a6ff; font-weight: 600; font-family: "JetBrains Mono", monospace;'>LIVE_MONITORING: ACTIVE | SESSION_START: {st.session_state.start_time}</span>
    </div>
""", unsafe_allow_html=True)

# Alerts
high_threats = df[df["Severity"] == "High"].head(3)
for _, threat in high_threats.iterrows():
    try:
        if (datetime.now() - datetime.strptime(threat['Time'], '%Y-%m-%d %H:%M:%S')).seconds < 10:
            st.toast(f"🚨 CRITICAL: {threat['Attack Type']} from {threat['Source IP']}", icon="🔥")
    except: pass

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Total Requests", f"{live_total:,}", delta=f"{total_in_db} Overall")
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

# --- LIVE FLOW FEED ---
st.subheader("📡 Live Network Traffic (Real-time Monitoring)")
live_df = df.head(10)[["Time", "Source IP", "Attack Type", "Severity", "Risk Score"]]

def color_severity(val):
    color = 'white'
    if val == 'High': color = '#ff4b4b'
    elif val == 'Medium': color = '#ffa500'
    elif val == 'Low': color = '#00ff00'
    return f'color: {color}'

st.dataframe(live_df.style.applymap(color_severity, subset=['Severity']), use_container_width=True, hide_index=True)

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
            reason = row['Summary'] if "Top Features" in row['Summary'] else "Unusual packet pattern identified via Unsupervised Learning."
            st.markdown(f"""
            <div class="anomaly-card">
                <strong>⚠️ Behavioral Anomaly Detected</strong> | Risk: {row['Risk Score']}<br>
                Source: {row['Source IP']} | Time: {row['Time']} | Type: {row['Attack Type']}<br>
                <em>System Analysis: {reason}</em>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.subheader("Automated Mitigation Console")
    bl_data = get_blacklist()
    if bl_data:
        bl_df = pd.DataFrame(bl_data, columns=["Blocked IP", "Reason", "Timestamp"])
        st.table(bl_df)
    else: st.info("No active IP blocks.")

with tab4:
    st.subheader("System Activity Logs")
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Export Logs for Forensic Audit", data=csv, file_name=f"sentinel_logs.csv", mime="text/csv")
