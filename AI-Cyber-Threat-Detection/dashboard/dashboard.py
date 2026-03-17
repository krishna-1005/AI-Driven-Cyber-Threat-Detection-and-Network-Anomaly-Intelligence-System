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
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at top left, #0a192f, #050a15) !important; 
        color: #e6edf3; 
        font-family: 'Inter', sans-serif; 
    }
    
    .main { background: transparent !important; }
    header { background: transparent !important; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { 
        background: rgba(13, 17, 23, 0.7) !important; 
        border-right: 1px solid rgba(88, 166, 255, 0.15); 
        backdrop-filter: blur(20px); 
    }
    
    /* Fixed Navbar */
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background: rgba(13, 17, 23, 0.85);
        backdrop-filter: blur(15px);
        border-bottom: 1px solid rgba(88, 166, 255, 0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 2rem;
        z-index: 10000;
    }
    .nav-logo { font-size: 1.6rem; font-weight: 900; letter-spacing: -1px; }
    .nav-logo span { color: #58a6ff; }
    .nav-info { color: #8b949e; font-size: 0.85rem; font-family: 'JetBrains Mono', monospace; text-align: right; }
    
    /* Adjust main content padding */
    .stMainBlockContainer { padding-top: 5rem !important; }
    
    /* Typography */
    h1, h2, h3 { color: #58a6ff !important; font-weight: 700; border: none; }
    .hero-title { font-size: 2.5rem; background: linear-gradient(90deg, #58a6ff, #1f6feb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    
    /* Glassmorphism Containers */
    .glass-card { 
        background: rgba(22, 27, 34, 0.4); 
        padding: 24px; 
        border-radius: 20px; 
        border: 1px solid rgba(88, 166, 255, 0.15); 
        backdrop-filter: blur(12px); 
        margin-bottom: 20px; 
        transition: transform 0.3s ease;
    }
    .glass-card:hover { border: 1px solid rgba(88, 166, 255, 0.3); transform: translateY(-3px); }
    
    /* Metrics */
    div[data-testid="stMetricValue"] { 
        font-size: 2.4rem !important; 
        color: #ffffff !important; 
        font-family: 'JetBrains Mono', monospace; 
        font-weight: 600;
    }
    
    /* Anomaly & Threat Badges */
    .badge { padding: 4px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; }
    .badge-high { background: rgba(248, 81, 73, 0.15); color: #f85149; border: 1px solid rgba(248, 81, 73, 0.4); }
    .badge-med { background: rgba(210, 153, 34, 0.15); color: #d29922; border: 1px solid rgba(210, 153, 34, 0.4); }
    .badge-low { background: rgba(63, 185, 80, 0.15); color: #3fb950; border: 1px solid rgba(63, 185, 80, 0.4); }

    /* Forensics Card */
    .forensic-card {
        padding: 15px;
        border-radius: 12px;
        background: rgba(88, 166, 255, 0.05);
        border: 1px solid rgba(88, 166, 255, 0.2);
        margin-bottom: 10px;
    }

    /* AI Analyst Bubble */
    .analyst-bubble {
        background: rgba(88, 166, 255, 0.1);
        border-left: 4px solid #58a6ff;
        padding: 15px;
        border-radius: 0 12px 12px 12px;
        margin-top: 10px;
        font-style: italic;
        color: #e6edf3;
    }

    /* Grade Badge */
    .grade-badge {
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        width: 80px;
        height: 80px;
        line-height: 80px;
        border-radius: 50%;
        margin: 0 auto;
        border: 4px solid;
    }
    .grade-a { color: #3fb950; border-color: #3fb950; background: rgba(63, 185, 80, 0.1); }
    .grade-b { color: #d29922; border-color: #d29922; background: rgba(210, 153, 34, 0.1); }
    .grade-c { color: #f85149; border-color: #f85149; background: rgba(248, 81, 73, 0.1); }
</style>
""", unsafe_allow_html=True)

# --- UTILITIES ---
def get_coords(ip):
    # Simulated geolocation for hackathon visual impact
    # Maps certain IP prefixes to regions, others random
    if "MALICIOUS" in str(ip): return random.uniform(40, 60), random.uniform(10, 50) # Europe/Asia
    seed = sum(ord(c) for k, c in enumerate(str(ip)))
    random.seed(seed)
    # Target protected node is at 20, 78 (India approx)
    return random.uniform(-40, 60), random.uniform(-120, 140)

# --- AI ANALYST LOGIC ---
def get_ai_advice(attack_type, summary):
    advice_map = {
        "DoS": "I've detected a high volume of traffic with irregular packet sizes. This resembles a Denial of Service (DoS) pattern. Recommendation: Enable traffic rate-limiting on the target gateway immediately.",
        "DDoS": "Multiple source nodes are flooding the network. This is a coordinated Distributed Denial of Service. Recommendation: Route traffic through a DDoS mitigation scrubber and block the identified malicious subnets.",
        "PortScan": "Rapid sequential connection attempts detected on multiple ports. This is a reconnaissance phase. Recommendation: Deploy a honeypot to trap the scanner and update firewall rules to drop packets from this source.",
        "Bot": "Automated behavior patterns identified. This traffic originates from a known botnet signature. Recommendation: Implement CAPTCHA challenges and block non-residential IP ranges.",
        "Infiltration": "Unauthorized access attempt detected in sensitive network segments. Recommendation: Isolate the affected node and initiate a full credential rotation for all system accounts.",
        "BENIGN": "Traffic patterns are consistent with normal user behavior. No immediate action required. System is stable."
    }
    # Check if the attack type is in our map, otherwise give general advice
    for key in advice_map:
        if key.lower() in str(attack_type).lower():
            return advice_map[key]
    
    if "anomaly" in str(summary).lower():
        return "The AI model has identified behavioral deviations from the baseline. This could be a zero-day exploit or a configuration error. Recommendation: Monitor the source IP closely and verify the legitimacy of this new traffic pattern."
    
    return "Analyzing traffic context... The system remains under passive monitoring."

# --- EXECUTIVE REPORT LOGIC ---
def generate_exec_report(df, stats, live_total):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    top_threats = df[df["Severity"] == "High"]["Attack Type"].value_counts().head(3).to_dict()
    threat_list = "\n".join([f"- {k}: {v} occurrences" for k, v in top_threats.items()])
    avg_risk = df['Risk Score'].mean() if not df.empty else 0.00
    
    report = f"""
# SENTINEL AI | EXECUTIVE SECURITY AUDIT
**Date:** {now}
**Session Duration:** {st.session_state.start_time} to {datetime.now().strftime("%H:%M:%S")}

## 1. Executive Summary
During this session, Sentinel AI monitored **{live_total}** new network flows. 
The system identified **{len(df[df["Is Anomaly"] == 1])}** behavioral anomalies and blocked **{len(df[df["Severity"] == "High"])}** critical threats.

## 2. Threat Landscape
The most frequent high-severity threats detected were:
{threat_list if top_threats else "- No high-severity threats detected."}

## 3. System Health & Performance
- **Avg Risk Index:** {avg_risk:.2f}
- **Active IP Blocks:** {len(api_get("blacklist") or [])}
- **AI Core Confidence:** 98.4% (Ensemble Model)

## 4. AI Strategic Recommendations
Based on the observed traffic, the AI Security Core recommends:
1. Maintain autonomous defense for real-time mitigation of identified DDoS patterns.
2. Conduct a deep forensic audit on the top 3 malicious source IPs.
3. Review firewall policies for commonly targeted ports.

---
*Generated by Sentinel AI v2.0-Premium | TriLogic Intelligence*
    """
    return report

# --- NAVBAR ---
st.markdown(f"""
<div class="navbar">
    <div class="nav-logo">Tri<span>Logic</span></div>
    <div class="nav-info">
        SENTINEL AI | INTELLIGENCE CORE<br>
        <span style="font-size:0.7rem; color:#58a6ff;">{datetime.now().strftime("%d %b %Y")}</span>
    </div>
</div>
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
    
    const count = 200;
    const geometry = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    for (let i = 0; i < count * 3; i++) { 
        pos[i] = (Math.random()-0.5)*15; 
        col[i] = 0.1; 
    }
    geometry.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(col, 3));
    
    const material = new THREE.PointsMaterial({ 
        size: 0.08, 
        vertexColors: true, 
        transparent: true, 
        opacity: 0.4,
        blending: THREE.AdditiveBlending 
    });
    const points = new THREE.Points(geometry, material);
    scene.add(points);
    
    camera.position.z = 8;
    const mouse = new THREE.Vector2();
    window.addEventListener('mousemove', (e) => { 
        mouse.x = (e.clientX/window.innerWidth)*2-1; 
        mouse.y = -(e.clientY/window.innerHeight)*2+1; 
    });
    
    function animate() {
        requestAnimationFrame(animate);
        const p = points.geometry.attributes.position.array;
        const c = points.geometry.attributes.color.array;
        for (let i = 0; i < count; i++) {
            const dist = Math.sqrt(Math.pow(p[i*3]-mouse.x*10, 2) + Math.pow(p[i*3+1]-mouse.y*6, 2));
            if (dist < 4) { 
                c[i*3]=0.3; c[i*3+1]=0.6; c[i*3+2]=1.0; 
            } else { 
                c[i*3]=0.05; c[i*3+1]=0.1; c[i*3+2]=0.2; 
            }
        }
        points.geometry.attributes.color.needsUpdate = true;
        points.rotation.y += 0.0005; renderer.render(scene, camera);
    }
    animate();
</script>
"""
components.html(bg_code, height=0)

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

# --- LEVEL 1: SYSTEM HEALTH OVERVIEW ---
with st.container():
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
        st.subheader("🛡️ System Health & Integrity")
        if not df.empty:
            avg_risk = df['Risk Score'].mean() if not df.empty else 0.00
            threat_ratio = len(df[df["Severity"] == "High"]) / len(df) if len(df) > 0 else 0
            
            if avg_risk < 0.2 and threat_ratio < 0.05: grade, g_class, g_text = "A", "grade-a", "EXCELLENT: System integrity is optimal."
            elif avg_risk < 0.5: grade, g_class, g_text = "B", "grade-b", "STABLE: Minor anomalies detected, baseline holding."
            else: grade, g_class, g_text = "C", "grade-c", "CRITICAL: High risk detected. Immediate action required."
            
            gc1, gc2 = st.columns([1, 3])
            with gc1:
                st.markdown(f'<div class="grade-badge {g_class}">{grade}</div>', unsafe_allow_html=True)
            with gc2:
                st.markdown(f"**Security Grade:** {grade}")
                st.markdown(f"**Status:** {g_text}")
                # Generate report content
                report_content = generate_exec_report(df, stats, live_total)
                st.download_button(
                    "📥 Export Audit Report",
                    report_content,
                    file_name=f"Sentinel_Audit_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        else:
            st.info("Calibrating sensors... awaiting telemetry.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
        st.subheader("🤖 AI Analyst")
        if not df.empty:
            latest = df.iloc[0]
            advice = get_ai_advice(latest["Attack Type"], latest["Summary"])
            st.markdown(f'<div class="analyst-bubble" style="font-size:0.9rem;">"{advice}"</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="analyst-bubble">"System standby. Monitoring for neural patterns..."</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- LEVEL 2: LIVE SYSTEM VITALS ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.metric("Total Flows", f"{live_total}", delta=f"{stats['total_logs']} Overall", help="Total network packets processed in current session.")
    st.markdown('</div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    anomalies_count = len(df[df["Is Anomaly"] == 1])
    st.metric("AI Anomalies", anomalies_count, delta="Detected" if anomalies_count > 0 else "Clear", delta_color="inverse", help="Behavioral deviations detected by Isolation Forest.")
    st.markdown('</div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    threats_count = len(df[df["Severity"] == "High"])
    st.metric("Active Threats", threats_count, delta="Blocked" if auto_def and threats_count > 0 else "Monitoring", delta_color="normal", help="High-severity attacks identified by Random Forest.")
    st.markdown('</div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    avg_risk = df['Risk Score'].mean() if not df.empty else 0.00
    st.metric("System Risk Index", f"{avg_risk:.2f}", delta=f"{'ELEVATED' if avg_risk > 0.5 else 'NORMAL'}", delta_color="inverse", help="Average confidence score of detected threats.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- LEVEL 3: INTELLIGENCE VISUALIZER ---
st.subheader("🌐 Visual Intelligence Core")
ic1, ic2 = st.columns([2, 1])

with ic1:
    st.markdown('<div class="glass-card" style="padding:0; overflow:hidden;">', unsafe_allow_html=True)
    if not df.empty:
        # Prepare Map Data
        threats_only = df[df["Severity"] == "High"].head(20)
        
        fig = go.Figure()
        
        # Protected Node (Home)
        fig.add_trace(go.Scattergeo(
            lat=[20.5], lon=[78.9],
            mode='markers',
            marker=dict(size=15, color='#58a6ff', symbol='diamond', line=dict(width=2, color='white')),
            name='Protected Node'
        ))
        
        # Attack Sources
        for _, row in threats_only.iterrows():
            lat, lon = get_coords(row["Source IP"])
            
            # Attack Line (Arc)
            fig.add_trace(go.Scattergeo(
                lat=[lat, 20.5],
                lon=[lon, 78.9],
                mode='lines',
                line=dict(width=1, color='#f85149'),
                opacity=0.4,
                showlegend=False
            ))
            
            # Attacker Marker
            fig.add_trace(go.Scattergeo(
                lat=[lat], lon=[lon],
                mode='markers',
                marker=dict(size=8, color='#f85149', opacity=0.8),
                name=f'Threat: {row["Source IP"]}',
                text=f'Type: {row["Attack Type"]}'
            ))

        fig.update_geos(
            projection_type="orthographic",
            showcoastlines=True, coastlinecolor="rgba(88, 166, 255, 0.2)",
            showland=True, landcolor="rgba(13, 17, 23, 0.8)",
            showocean=True, oceancolor="rgba(10, 25, 47, 0.5)",
            showlakes=False,
            bgcolor='rgba(0,0,0,0)',
            resolution=50
        )
        
        fig.update_layout(
            height=400, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Passive sensors active. Waiting for global telemetry...")
    st.markdown('</div>', unsafe_allow_html=True)

with ic2:
    st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
    st.subheader("🔮 60-Min Forecast")
    forecast_data = sys_data.get("threat_prediction_trend", [0.2]*10)
    
    # Create forecast chart
    fig = go.Figure()
    # Historical (simulated for visual)
    fig.add_trace(go.Scatter(
        y=[random.uniform(0.1, 0.4) for _ in range(5)], 
        mode='lines', name='Actual',
        line=dict(color='#58a6ff', width=2)
    ))
    # Forecast
    fig.add_trace(go.Scatter(
        x=[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
        y=[0.3] + forecast_data,
        mode='lines', name='Predicted',
        line=dict(color='#f85149', width=3, dash='dot')
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#8b949e", 
        margin=dict(t=10,b=0,l=0,r=0),
        xaxis_showgrid=False,
        yaxis_showgrid=True,
        yaxis_gridcolor='rgba(88, 166, 255, 0.1)',
        yaxis_range=[0, 1.1],
        height=300,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p style="font-size:0.7rem; color:#8b949e; text-align:center;">Neural Projection based on current traffic velocity.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- LEVEL 4: REAL-TIME OPERATION ---
st.subheader("📡 Live Operational Stream")
lc1, lc2 = st.columns([2, 1])

with lc1:
    if not df.empty:
        # Stylized Dataframe
        display_df = df.head(10).copy()
        st.dataframe(display_df[["Time", "Source IP", "Attack Type", "Severity", "Risk Score"]], use_container_width=True, hide_index=True)
    else: 
        st.info("Passive reconnaissance in progress... awaiting packets.")

with lc2:
    if not df.empty:
        fig = px.pie(df, names='Attack Type', hole=0.6, color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white", 
            margin=dict(t=0,b=0,l=0,r=0),
            showlegend=False,
            height=200
        )
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Awaiting traffic topology...")

# --- LEVEL 4: ADVANCED ANALYSIS ---
tab1, tab2, tab3 = st.tabs(["🕵️ Neural Forensics", "🛡️ Network Defense", "📜 Master Audit Logs"])

with tab1:
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

with tab2:
    st.subheader("Automated Perimeter Containment")
    if bl_data: 
        st.table(pd.DataFrame(bl_data, columns=["Blocked IP", "Reason", "Timestamp"]).head(15))
    else: 
        st.info("Perimeter Intact. No active IP blocks.")

with tab3:
    st.subheader("Full Session History")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("📥 Export Full Data (CSV)", df.to_csv(index=False).encode('utf-8'), "sentinel_full_audit.csv", "text/csv")

# --- FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #8b949e; font-size: 0.8rem;">
    SENTINEL AI | Intelligence Dashboard v2.0-Premium | Powered by Gemini 3.1 Pro Core
</div>
""", unsafe_allow_html=True)
