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
    section[data-testid="stSidebar"] { background-color: rgba(10, 15, 25, 0.8) !important; border-right: 1px solid rgba(88, 166, 255, 0.2); backdrop-filter: blur(15px); }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    div[data-testid="stMetricValue"] { font-size: 2rem !important; color: #ffffff !important; font-family: 'JetBrains Mono', monospace; }
    .metric-container { background: rgba(22, 27, 34, 0.4); padding: 24px; border-radius: 20px; border: 1px solid rgba(88, 166, 255, 0.15); backdrop-filter: blur(8px); margin-bottom: 10px; }
    .status-pulse { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #00ff00; box-shadow: 0 0 10px #00ff00; animation: pulse-green 2s infinite; margin-right: 8px; }
    @keyframes pulse-green { 0% { transform: scale(0.95); opacity: 0.7; } 70% { transform: scale(1.1); opacity: 1; } 100% { transform: scale(0.95); opacity: 0.7; } }
</style>
""", unsafe_allow_html=True)

# --- THREE.JS BACKGROUND ---
bg_code = """
<div id="three-bg" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; background: #050a15;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({antialias: true, alpha: true});
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('three-bg').appendChild(renderer.domElement);
    const geometry = new THREE.BufferGeometry();
    const pos = new Float32Array(150 * 3);
    for(let i=0; i<150*3; i++) pos[i] = (Math.random()-0.5)*15;
    geometry.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const material = new THREE.PointsMaterial({size: 0.1, color: 0x58a6ff, transparent: true, opacity: 0.6});
    const points = new THREE.Points(geometry, material);
    scene.add(points);
    camera.position.z = 8;
    function animate() { requestAnimationFrame(animate); points.rotation.y += 0.001; renderer.render(scene, camera); }
    animate();
</script>
"""
components.html(bg_code, height=0)

# --- DATA FETCHING ---
API_BASE = "http://127.0.0.1:5000" # Use IP for reliability

def api_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}/{endpoint}", timeout=1.5)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("SENTINEL AI")
    health = api_get("health")
    if health:
        st.success("🟢 System Online")
    else:
        st.warning("🟠 Connecting to AI Core...")
    st.toggle("Live Monitoring", value=True)

# --- DATA PROCESSING ---
stats = api_get("stats") or {"total_logs": 0}
total_in_db = stats["total_logs"]
logs = api_get("logs") or []
df = pd.DataFrame(logs, columns=["Time", "Source IP", "Attack Type", "Severity", "Risk Score", "Summary", "Is Anomaly"])

if 'baseline' not in st.session_state:
    st.session_state.baseline = total_in_db
live_total = max(0, total_in_db - st.session_state.baseline)

# --- DASHBOARD UI ---
st.title("🛡️ Sentinel Intelligence Dashboard")
st.markdown(f"**LIVE MONITORING ACTIVE** | Database Records: {total_in_db}")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Total Requests", f"{live_total}", delta=f"{total_in_db} Total")
    st.markdown('</div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Anomalies", len(df[df["Is Anomaly"] == 1]))
    st.markdown('</div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    threats = len(df[df["Severity"] == "High"])
    st.metric("Threats", threats)
    st.markdown('</div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Risk Score", f"{df['Risk Score'].mean():.2f}" if not df.empty else "0.00")
    st.markdown('</div>', unsafe_allow_html=True)

st.subheader("📡 Live Network Traffic")
if not df.empty:
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
else:
    st.info("Waiting for traffic packets...")

tab1, tab2 = st.tabs(["📊 Analytics", "📜 Logs"])
with tab1:
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(df, names="Attack Type", hole=0.4, title="Threat Distribution")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.line(df.tail(20), y="Risk Score", title="Real-time Risk Velocity")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
with tab2:
    st.dataframe(df, use_container_width=True)
