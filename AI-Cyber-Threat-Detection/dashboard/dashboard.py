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
st_autorefresh(interval=2500, key="global_refresh")

# --- PREMIUM STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    .stApp { background: #050a15 !important; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    .main { background: transparent !important; }
    header { background: transparent !important; }
    
    section[data-testid="stSidebar"] { 
        background-color: rgba(10, 15, 25, 0.8) !important; 
        border-right: 1px solid rgba(88, 166, 255, 0.2); 
        backdrop-filter: blur(15px);
    }
    
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    div[data-testid="stMetricValue"] { font-size: 2.2rem !important; color: #ffffff !important; font-family: 'JetBrains Mono', monospace; }
    
    .metric-container {
        background: rgba(22, 27, 34, 0.4); 
        padding: 24px; 
        border-radius: 20px; 
        border: 1px solid rgba(88, 166, 255, 0.15);
        backdrop-filter: blur(8px);
        margin-bottom: 10px;
    }

    .anomaly-card {
        padding: 18px; border-radius: 12px; margin-bottom: 15px;
        background: rgba(255, 165, 0, 0.08); border: 1px solid rgba(255, 165, 0, 0.4); border-left: 6px solid #ffa500;
        backdrop-filter: blur(10px);
    }

    .status-pulse { 
        display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #00ff00;
        box-shadow: 0 0 10px #00ff00; animation: pulse-green 2s infinite; margin-right: 8px; 
    }
    @keyframes pulse-green { 0% { opacity: 0.7; } 70% { opacity: 1; } 100% { opacity: 0.7; } }
</style>
""", unsafe_allow_html=True)

# --- THREE.JS INTERACTIVE FULL-SCREEN BACKGROUND ---
bg_code = """
<div id="three-bg" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; background: #050a15;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('three-bg').appendChild(renderer.domElement);

    const mouse = new THREE.Vector2();
    const target = new THREE.Vector2();

    const count = 150;
    const geometry = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    for (let i = 0; i < count * 3; i++) {
        pos[i] = (Math.random() - 0.5) * 15;
        col[i] = 0.1;
    }
    geometry.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(col, 3));

    const material = new THREE.PointsMaterial({ size: 0.1, vertexColors: true, transparent: true, opacity: 0.6 });
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
        const p = points.geometry.attributes.position.array;
        const c = points.geometry.attributes.color.array;
        for (let i = 0; i < count; i++) {
            const dx = p[i*3] - target.x * 10;
            const dy = p[i*3+1] - target.y * 6;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < 3) {
                c[i*3] = 0.3; c[i*3+1] = 0.6; c[i*3+2] = 1.0;
            } else {
                c[i*3] = 0.1; c[i*3+1] = 0.15; c[i*3+2] = 0.25;
            }
        }
        points.geometry.attributes.color.needsUpdate = true;
        points.rotation.y += 0.001;
        renderer.render(scene, camera);
    }
    animate();
</script>
"""
components.html(bg_code, height=0)

# --- DATA FETCHING ---
API_BASE = "http://127.0.0.1:5000"

def api_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}/{endpoint}", timeout=2)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("SENTINEL AI")
    health = api_get("health")
    if health and health["status"] == "ready":
        st.success("🟢 System Online")
    else:
        st.warning("🟠 Connecting to AI Core...")
    st.divider()
    st.toggle("Live Monitoring", value=True)

# --- DATA PROCESSING ---
stats = api_get("stats") or {"total_logs": 0}
logs_data = api_get("logs") or []
bl_data = api_get("blacklist") or []

df = pd.DataFrame(logs_data, columns=["Time", "Source IP", "Attack Type", "Severity", "Risk Score", "Summary", "Is Anomaly"])

if 'baseline' not in st.session_state:
    st.session_state.baseline = stats["total_logs"]
    st.session_state.start_time = datetime.now().strftime("%H:%M:%S")

live_total = max(0, stats["total_logs"] - st.session_state.baseline)

# --- DASHBOARD UI ---
st.title("🛡️ Sentinel Intelligence Dashboard")
st.markdown(f"**LIVE MONITORING ACTIVE** | Polling every 2.5s | Session Start: {st.session_state.start_time}")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Total Requests", f"{live_total}", delta=f"{stats['total_logs']} Overall")
    st.markdown('</div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Anomalies Identified", len(df[df["Is Anomaly"] == 1]))
    st.markdown('</div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    threats = len(df[df["Severity"] == "High"])
    st.metric("Threats Mitigated", threats)
    st.markdown('</div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    avg_risk = df['Risk Score'].mean() if not df.empty else 0.0
    st.metric("Avg Risk Index", f"{avg_risk:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.subheader("📡 Live Network Traffic (Real-time Monitoring)")
if not df.empty:
    st.dataframe(df.head(10)[["Time", "Source IP", "Attack Type", "Severity", "Risk Score"]], use_container_width=True, hide_index=True)
else:
    st.info("Waiting for data packets from AI Core...")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "🕵️ Forensics", "🛡️ Mitigation", "📜 Full Logs"])

with tab1:
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Intelligence Distribution")
            fig = px.pie(df, names='Attack Type', hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Behavioral Risk Velocity")
            fig = px.area(df.tail(20), y="Risk Score", color_discrete_sequence=['#58a6ff'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
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
                <strong>⚠️ Anomaly Flagged</strong> | Risk: {row['Risk Score']}<br>
                Source: {row['Source IP']} | Analysis: {row['Summary']}
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.subheader("Automated Mitigation Console")
    if bl_data:
        bl_df = pd.DataFrame(bl_data, columns=["Blocked IP", "Reason", "Timestamp"])
        st.table(bl_df.head(10))
    else:
        st.info("No active IP blocks.")

with tab4:
    st.subheader("System Activity Logs")
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Export Forensic Audit", data=csv, file_name="sentinel_logs.csv", mime="text/csv")
