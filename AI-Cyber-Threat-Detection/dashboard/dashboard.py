import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
st.set_page_config(
    page_title="SENTINEL AI | Cyber Threat Intelligence",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- GLOBAL REFRESH (TOP LEVEL FOR PERFORMANCE) ---
st_autorefresh(interval=2000, key="global_refresh")

# --- PREMIUM STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at top right, #1a1f2e, #0e1117); 
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Terminal Sniffer View */
    .terminal-sniffer {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #58a6ff33;
        border-radius: 8px;
        padding: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #00ff00;
        height: 120px;
        overflow-y: hidden;
        margin-bottom: 20px;
        box-shadow: inset 0 0 10px rgba(0,255,0,0.1);
    }
    .terminal-line { margin-bottom: 2px; white-space: nowrap; }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] { 
        background-color: rgba(22, 27, 34, 0.95) !important; 
        border-right: 1px solid rgba(88, 166, 255, 0.2); 
        backdrop-filter: blur(10px);
    }
    
    /* Header & Titles */
    h1, h2, h3 { 
        color: #58a6ff !important; 
        font-family: 'Inter', sans-serif; 
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Metric Containers (Glassmorphism) */
    div[data-testid="stMetricValue"] { 
        font-size: 2.2rem !important; 
        color: #ffffff !important; 
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .metric-container {
        background: rgba(22, 27, 34, 0.6); 
        padding: 24px; 
        border-radius: 16px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4); 
        backdrop-filter: blur(4px);
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    
    .metric-container:hover { 
        border-color: rgba(88, 166, 255, 0.5); 
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(88, 166, 255, 0.15);
    }

    /* Live Feed Styling */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Threat & Anomaly Cards */
    .threat-card, .anomaly-card {
        padding: 18px; 
        border-radius: 12px; 
        margin-bottom: 15px;
        border: 1px solid;
        backdrop-filter: blur(8px);
    }
    
    .threat-card {
        background: rgba(255, 75, 75, 0.05); 
        border-color: rgba(255, 75, 75, 0.3); 
        border-left: 6px solid #ff4b4b;
    }
    
    .anomaly-card {
        background: rgba(255, 165, 0, 0.05); 
        border-color: rgba(255, 165, 0, 0.3); 
        border-left: 6px solid #ffa500;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 30px; 
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] { 
        height: 55px; 
        color: #8b949e; 
        font-weight: 600;
        font-size: 1rem;
    }
    
    .stTabs [aria-selected="true"] { 
        color: #58a6ff !important; 
        border-bottom: 3px solid #58a6ff !important; 
    }

    /* Pulse Animation for Online Status */
    .status-pulse {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00ff00;
        box-shadow: 0 0 0 0 rgba(0, 255, 0, 1);
        animation: pulse-green 2s infinite;
        margin-right: 8px;
    }

    @keyframes pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
    }
</style>
""", unsafe_allow_html=True)

# --- LIVE MONITORING LOGIC ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now().strftime("%H:%M:%S")

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
    
    # Live Status with Pulse
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
logs_data = get_logs()

df = pd.DataFrame(
    logs_data,
    columns=["Time", "Source IP", "Attack Type", "Severity", "Risk Score", "Summary", "Is Anomaly"]
)

# Robust Live Count
if 'baseline_count' not in st.session_state:
    st.session_state.baseline_count = len(df)

live_total = max(0, len(df) - st.session_state.baseline_count)

# --- THREE.JS INTERACTIVE NEURAL MESH ---
three_js_code = """
<div id="canvas-container" style="width: 100%; height: 400px; background: transparent; cursor: crosshair; border-radius: 20px; border: 1px solid rgba(88, 166, 255, 0.15); margin-bottom: 30px; overflow: hidden; box-shadow: 0 0 20px rgba(88, 166, 255, 0.05);"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(container.offsetWidth, container.offsetHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    const mouse = new THREE.Vector2();
    const target = new THREE.Vector2();

    // Create Neural Particles
    const count = 150;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    
    for (let i = 0; i < count * 3; i++) {
        positions[i] = (Math.random() - 0.5) * 10;
        velocities[i] = (Math.random() - 0.5) * 0.02;
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const material = new THREE.PointsMaterial({
        color: 0x58a6ff,
        size: 0.08,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    // Create Connections (Lines)
    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x58a6ff,
        transparent: true,
        opacity: 0.15,
        blending: THREE.AdditiveBlending
    });

    let lineMesh;

    function updateLines() {
        if (lineMesh) scene.remove(lineMesh);
        
        const lineGeometry = new THREE.BufferGeometry();
        const linePositions = [];
        const pos = points.geometry.attributes.position.array;
        
        for (let i = 0; i < count; i++) {
            for (let j = i + 1; j < count; j++) {
                const dx = pos[i * 3] - pos[j * 3];
                const dy = pos[i * 3 + 1] - pos[j * 3 + 1];
                const dz = pos[i * 3 + 2] - pos[j * 3 + 2];
                const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
                
                if (dist < 2.5) {
                    linePositions.push(pos[i*3], pos[i*3+1], pos[i*3+2]);
                    linePositions.push(pos[j*3], pos[j*3+1], pos[j*3+2]);
                }
            }
        }
        
        lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
        lineMesh = new THREE.LineSegments(lineGeometry, lineMaterial);
        scene.add(lineMesh);
    }

    camera.position.z = 6;

    container.addEventListener('mousemove', (event) => {
        const rect = container.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / container.offsetWidth) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / container.offsetHeight) * 2 + 1;
    });

    function animate() {
        requestAnimationFrame(animate);
        
        const pos = points.geometry.attributes.position.array;
        target.x += (mouse.x - target.x) * 0.05;
        target.y += (mouse.y - target.y) * 0.05;

        for (let i = 0; i < count; i++) {
            // Update base position
            pos[i * 3] += velocities[i * 3];
            pos[i * 3 + 1] += velocities[i * 3 + 1];
            pos[i * 3 + 2] += velocities[i * 3 + 2];

            // Bounce off boundaries
            if (Math.abs(pos[i * 3]) > 5) velocities[i * 3] *= -1;
            if (Math.abs(pos[i * 3 + 1]) > 5) velocities[i * 3 + 1] *= -1;
            if (Math.abs(pos[i * 3 + 2]) > 5) velocities[i * 3 + 2] *= -1;

            // Mouse Interaction (Distortion)
            const dx = pos[i * 3] - target.x * 5;
            const dy = pos[i * 3 + 1] - target.y * 3;
            const dist = Math.sqrt(dx*dx + dy*dy);
            
            if (dist < 2) {
                pos[i * 3] += dx * 0.02;
                pos[i * 3 + 1] += dy * 0.02;
            }
        }
        
        points.geometry.attributes.position.needsUpdate = true;
        updateLines();
        
        // Gentle scene rotation
        scene.rotation.y += 0.001;
        scene.rotation.x = target.y * 0.2;
        scene.rotation.y = target.x * 0.5;

        renderer.render(scene, camera);
    }
    
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = container.offsetWidth / container.offsetHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.offsetWidth, container.offsetHeight);
    });
</script>
"""
import streamlit.components.v1 as components
components.html(three_js_code, height=410)

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

# Live Monitoring Status Bar
st.markdown(f"""
    <div style='background: rgba(88, 166, 255, 0.1); padding: 10px 20px; border-radius: 10px; border: 1px solid rgba(88, 166, 255, 0.2); margin-bottom: 20px; display: flex; align-items: center;'>
        <div class="status-pulse"></div>
        <span style='color: #58a6ff; font-weight: 600; font-family: "JetBrains Mono", monospace;'>LIVE_MONITORING: ACTIVE | POLLING_INTERVAL: 2s | SESSION_START: {st.session_state.start_time}</span>
    </div>
""", unsafe_allow_html=True)

# Real-time Critical Alerts
high_threats = df[df["Severity"] == "High"].head(3)
for _, threat in high_threats.iterrows():
    if (datetime.now() - datetime.strptime(threat['Time'], '%Y-%m-%d %H:%M:%S')).seconds < 10:
        st.toast(f"🚨 CRITICAL: {threat['Attack Type']} from {threat['Source IP']}", icon="🔥")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Total Requests", f"{live_total:,}", delta=f"{len(df)} Overall")
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
st.subheader("📡 Live Network Traffic (Real-time Flow Monitoring)")
live_df = df.head(10)[["Time", "Source IP", "Attack Type", "Severity", "Risk Score"]]

def color_severity(val):
    color = 'white'
    if val == 'High': color = '#ff4b4b'
    elif val == 'Medium': color = '#ffa500'
    elif val == 'Low': color = '#00ff00'
    return f'color: {color}'

st.dataframe(
    live_df.style.applymap(color_severity, subset=['Severity']),
    use_container_width=True,
    hide_index=True
)

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
            # Use XAI data from Summary if available
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
    else:
        st.info("No active IP blocks.")

with tab4:
    st.subheader("System Activity Logs")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Export feature for Forensics
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Logs for Forensic Audit",
        data=csv,
        file_name=f"sentinel_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )
