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
st.set_page_config(page_title="SENTINEL AI | Intelligence Dashboard", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")
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
    div[data-testid="stMetricValue"] { font-size: 2.2rem !important; color: #ffffff !important; font-family: 'JetBrains Mono', monospace; }
    .metric-container { background: rgba(22, 27, 34, 0.4); padding: 24px; border-radius: 20px; border: 1px solid rgba(88, 166, 255, 0.15); backdrop-filter: blur(8px); margin-bottom: 10px; }
    .anomaly-card { padding: 18px; border-radius: 12px; margin-bottom: 15px; background: rgba(255, 165, 0, 0.08); border: 1px solid rgba(255, 165, 0, 0.4); border-left: 6px solid #ffa500; backdrop-filter: blur(10px); }
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
    const count = 150;
    const geometry = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    for (let i = 0; i < count * 3; i++) { pos[i] = (Math.random()-0.5)*15; col[i] = 0.1; }
    geometry.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const material = new THREE.PointsMaterial({ size: 0.1, vertexColors: true, transparent: true, opacity: 0.6 });
    const points = new THREE.Points(geometry, material);
    scene.add(points);
    camera.position.z = 8;
    const mouse = new THREE.Vector2();
    window.addEventListener('mousemove', (e) => { mouse.x = (e.clientX/window.innerWidth)*2-1; mouse.y = -(e.clientY/window.innerHeight)*2+1; });
    function animate() {
        requestAnimationFrame(animate);
        const p = points.geometry.attributes.position.array;
        const c = points.geometry.attributes.color.array;
        for (let i = 0; i < count; i++) {
            const dist = Math.sqrt(Math.pow(p[i*3]-mouse.x*10, 2) + Math.pow(p[i*3+1]-mouse.y*6, 2));
            if (dist < 3) { c[i*3]=0.3; c[i*3+1]=0.6; c[i*3+2]=1.0; } else { c[i*3]=0.1; c[i*3+1]=0.15; c[i*3+2]=0.25; }
        }
        points.geometry.attributes.color.needsUpdate = true;
        points.rotation.y += 0.001; renderer.render(scene, camera);
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

# --- SIDEBAR & SYSTEM ACTIVITY ---
with st.sidebar:
    st.title("SENTINEL AI")
    health = api_get("health")
    if health and health["status"] == "ready": st.success("🟢 AI Core: Online")
    else: st.warning("🟠 Connecting...")
    
    st.subheader("💻 System Activity Patterns")
    sys_data = api_get("system") or {"cpu_usage": 0, "mem_usage": 0, "active_processes": 0}
    st.progress(sys_data["cpu_usage"]/100, text=f"CPU Load: {sys_data['cpu_usage']}%")
    st.progress(sys_data["mem_usage"]/100, text=f"Memory Usage: {sys_data['mem_usage']}%")
    st.metric("Active Processes", sys_data["active_processes"])
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

# --- MAIN DASHBOARD ---
st.title("🛡️ Sentinel Intelligence Dashboard")
st.markdown(f"**Holistic Monitoring** | Session Start: {st.session_state.start_time}")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Total Flows", f"{live_total}", delta=f"{stats['total_logs']} Overall")
    st.markdown('</div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Anomalies", len(df[df["Is Anomaly"] == 1]))
    st.markdown('</div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Threats", len(df[df["Severity"] == "High"]))
    st.markdown('</div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Risk Index", f"{df['Risk Score'].mean():.2f}" if not df.empty else "0.00")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.subheader("📡 Live Network Traffic")
if not df.empty: st.dataframe(df.head(10)[["Time", "Source IP", "Attack Type", "Severity", "Risk Score"]], use_container_width=True, hide_index=True)
else: st.info("Sniffing network traffic...")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Predictive Analytics", "🕵️ Forensics", "🛡️ Mitigation", "📜 Logs"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Threat Distribution")
        if not df.empty:
            fig = px.pie(df, names='Attack Type', hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("🔮 60-Min Risk Forecast")
        # Satisfies: "detect and predict potential threats"
        forecast_data = sys_data.get("threat_prediction_trend", [0]*10)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=forecast_data, mode='lines+markers', name='Predicted Risk', line=dict(color='#58a6ff', width=3, dash='dot')))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=30,b=0,l=0,r=0), yaxis_range=[0,1])
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("AI Behavioral Forensics")
    anomalies = df[df["Is Anomaly"] == 1].head(10)
    if not anomalies.empty:
        for _, row in anomalies.iterrows():
            st.markdown(f'<div class="anomaly-card"><strong>⚠️ Anomaly</strong> | {row["Source IP"]}<br><em>Analysis: {row["Summary"]}</em></div>', unsafe_allow_html=True)
    else: st.success("No behavioral anomalies detected.")

with tab3:
    st.subheader("Automated Mitigation")
    if bl_data: st.table(pd.DataFrame(bl_data, columns=["Blocked IP", "Reason", "Timestamp"]).head(10))
    else: st.info("No active IP blocks.")

with tab4:
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("📥 Export Audit Logs", df.to_csv(index=False).encode('utf-8'), "sentinel_audit.csv", "text/csv")
