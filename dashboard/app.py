import streamlit as st
import streamlit.components.v1 as components
import requests
import time

# =========================
# CONSTANTS
# =========================
WS_URL = "ws://localhost:8000/ws/video"
VIDEO_URL = "http://localhost:8000/video_feed"
STATS_URL = "http://localhost:8000/stats"
SETTINGS_URL = "http://localhost:8000/settings"
SOURCE_URL = "http://localhost:8000/source"
COUNTER_RESET_URL = "http://localhost:8000/counter/reset"
HEALTH_URL = "http://localhost:8000/"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="CoconutCount AI",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
    <style>
        MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .main {font-family: 'Segoe UI', sans-serif;}
        .block-container {
            max-width: 98% !important;
            padding-top: 0.1rem;
            padding-bottom: 1rem;
        }
        .main .block-container {
            transform: none !important;
        }
        /* FONT SIZE */
        html, body, [class*="css"] {
            font-size: 15px;
        }
        /* TITLE */
        h1 {
            font-size: 2rem !important;
        }

        /* SUBTITLE */
        h2, h3 {
            font-size: 1.4rem !important;
        }
        
        h4 {
            font-size: 1rem !important;
        }
        /* VALUE metric */
        [data-testid="stMetricValue"] {
            # font-size: 10px;
        }

        /* LABEL metric */
        [data-testid="stMetricLabel"] {
            # font-size: 18px;
        }

        /* DELTA metric */
        [data-testid="stMetricDelta"] {
            # font-size: 16px;
        }

        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: transparent;
        }}

        .metric-card {
            position: relative;
            margin-bottom: 10px;
            padding: 10px 20px;
            border: 0.5px solid #30363d;
            border-radius: 10px;
            font-family: monospace;
            height: 120px;
            overflow: hidden;
            background:
                linear-gradient(
                    145deg,
                    rgba(255,255,255,0.05),
                    rgba(255,255,255,0.02)
                );
            backdrop-filter: blur(12px);
            transition:
                transform 0.25s ease,
                box-shadow 0.25s ease,
                border 0.25s ease;
        }
        .metric-card h4 {
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.3px;
            color: rgba(255,255,255,0.72);
        }
        .metric-card h1 {
            margin: 0;
            font-size: 46px;
            font-weight: 800;
            line-height: 1;
            color: white;
        }
        .metric-card::after {
            content: "";
            position: absolute;
            inset: 0;
            border-radius: 18px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
            pointer-events: none;
        }
        .metric-card.status-good::before {
            background: linear-gradient(90deg, #00ff99, #00d084);
        }
        .metric-card.status-warning::before {
            background: linear-gradient(90deg, #ffcc00, #ffaa00);
        }
        .metric-card.status-danger::before {
            background: linear-gradient(90deg, #ff4d4d, #ff1a1a);
        }
        .log-box {
            background-color: #1e1e1e;
            color: #00ff00;
            padding: 10px;
            border-radius: 10px;
            font-family: monospace;
            # height: 150px;
            overflow-y: auto;
        }
        /* Streamlit widgets */
        .stButton > button, .stform_submit_button > button {
            background-color: #fa4b4b !important;
            color: white !important;
            # border-radius: 6px;
            # padding: 10px 18px;
            font-weight: 600;
        }
        /* SOURCE ACTION BUTTONS */
        div[data-testid="column"] .stButton > button {
            border-radius: 14px;
            font-weight: 600;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.04);
            backdrop-filter: blur(10px);
            transition: all 0.25s ease;
        }
        /* HOVER */
        div[data-testid="column"] .stButton > button:hover {
            transform: translateY(-2px);
            border: 1px solid rgba(0,255,180,0.35);
            box-shadow: 0 4px 20px rgba(0,255,180,0.15);
        }
        /* DISABLED BUTTON */
        div[data-testid="column"] .stButton > button:disabled {
            opacity: 0.45;
            cursor: not-allowed;
        }
        /* BUTTON SPACING */
        div[data-testid="column"] {
            # padding-top: 6px;
        }
        /* SIDEBAR COLUMNS */
        div[data-testid="stColumn"] > div:not([data-testid="stVerticalBlock"]) {
            padding-top: 6px;
            padding-bottom: 6px;
        }
        .stSelectbox, .stTextInput, .stRadio> div {
            color: #333333;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 6px;
            padding: 8px;
        }
        /* Metric cards container */
        .css-1v3fvcr {
            padding: 1rem;
            border-radius: 8px;
            background-color: #ffffff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        .css-1y4p8pa {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            # background-color: #e9f0f7 !important;
        }

        /* Headers */
        h1, h2, h3, h4 {
            # color: #003366 !important;
        }

        /* Info and warning colors */
        .stInfo {
            background-color: #d1ecf1 !important;
            color: #0c5460 !important;
        }

        .stWarning {
            background-color: #fff3cd !important;
            color: #856404 !important;
        }

        .stError {
            background-color: #f8d7da !important;
            color: #721c24 !important;
        }

            .video-status-box {
                border: 0.5px solid #30363d;
                border-radius: 10px;
                padding: 10px 16px 12px 16px;
                margin-bottom: 10px;
                font-family: monospace;
                background: linear-gradient(145deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
                backdrop-filter: blur(8px);
            }
            .video-status-box h4 {
                font-size: 13px;
                font-weight: 600;
                color: rgba(255,255,255,0.6);
                margin: 0 0 8px 0;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }
            .video-status-row {
                display: flex;
                justify-content: space-between;
                font-size: 12px;
                color: rgba(255,255,255,0.75);
                margin: 3px 0;
            }
            .video-status-value {
                color: white;
                font-weight: 600;
            }
            .progress-bar-bg {
                width: 100%;
                background: rgba(255,255,255,0.1);
                border-radius: 4px;
                height: 6px;
                margin-top: 8px;
                overflow: hidden;
            }
            .progress-bar-fill {
                height: 100%;
                border-radius: 4px;
                background: {bar_colour};
                transition: width 0.4s ease;
            }
    </style>
""", unsafe_allow_html=True)

# =========================
# STATE INITIALIZATION
# =========================
if 'settings' not in st.session_state:
    try:
        resp = requests.get(SETTINGS_URL, timeout=1.0)
        if resp.status_code == 200:
            st.session_state.settings = resp.json()
        else:
            st.session_state.settings = {}
    except:
        st.session_state.settings = {}

if 'logs' not in st.session_state:
    st.session_state.logs = ["System initialized."]

def add_log(msg):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{timestamp}] {msg}")
    if len(st.session_state.logs) > 50:
        st.session_state.logs.pop()

# =========================
# SIDEBAR — Slim Status Panel
# =========================
with st.sidebar:
    st.markdown("### 🥥 CoconutCount AI")
    st.markdown("---")
    st.caption("**System Status**")
    # Populated after health check below

# =========================
# STATS POLLING (outside tabs — fires on every tab)
# =========================
stats = {}
source_state = {}
is_online = False
latency = 0.0

start_time = time.time()
try:
    health_resp = requests.get(HEALTH_URL, timeout=0.5)
    if health_resp.status_code == 200:
        is_online = True
        stats_resp = requests.get(STATS_URL, timeout=0.5)
        if stats_resp.status_code == 200:
            stats = stats_resp.json()
        source_resp = requests.get(SOURCE_URL, timeout=0.5)
        if source_resp.status_code == 200:
            source_state = source_resp.json()
    latency = (time.time() - start_time) * 1000
except Exception as e:
    add_log(f"API Disconnected or Timeout: {e}")
    latency = 0.0

# =========================
# MAIN DASHBOARD TITLE
# =========================
st.title("Monitoring Realtime Coconut Counting")

# Status bar
_stream_status = source_state.get('status_message', 'Unknown')
_stream_mode = source_state.get('mode', '–')
st.markdown(f"**API Status:** <span id='api-status'>{'🟢 ONLINE' if is_online else '🔴 OFFLINE'}</span> &nbsp; | &nbsp; **Stream Latency:** <span id='api-latency'>{latency:.0f}</span> ms &nbsp; | &nbsp; **Source:** <code id='api-mode'>{_stream_mode}</code> — <code id='api-stream-status'>{_stream_status}</code>", unsafe_allow_html=True)

# =========================
# TABS
# =========================
tab_monitor, tab_settings = st.tabs(["🎥 Live Monitoring", "⚙️ Production Settings"])

# ─────────────────────────────────────────────
# TAB 1 — LIVE MONITORING (unchanged layout)
# ─────────────────────────────────────────────
with tab_monitor:
    col_video, col_stats = st.columns([2, 1])

    with col_video:
        if is_online:
            # WebSocket video receiver — static JS component that survives Streamlit reruns
            components.html(f'''
                <div id="ws-container" style="position: relative; width: 100%; max-width: 65%; margin-left: 80px;">
                    <img id="stream" style="
                        width: 100%;
                        border: 2px solid #333;
                        border-radius: 10px;
                        display: block;
                    ">
                    <div id="ws-status" style="
                        position: absolute;
                        top: 10px;
                        right: 14px;
                        padding: 4px 12px;
                        border-radius: 8px;
                        font-family: monospace;
                        font-size: 12px;
                        font-weight: 600;
                        color: white;
                        background: rgba(0,0,0,0.6);
                        backdrop-filter: blur(6px);
                        pointer-events: none;
                    ">Connecting...</div>
                </div>
                <script>
                    const WS_URL = "{WS_URL}";
                    const img = document.getElementById("stream");
                    const status = document.getElementById("ws-status");
                    let ws = null;
                    let reconnectTimer = null;
                    let heartbeatTimer = null;
                    let frameCount = 0;
                    let lastUrl = null;
                    let lastFrameTime = performance.now();

                    const pDoc = window.parent.document;

                    function setTxt(id, txt) {{
                        const el = pDoc.getElementById(id);
                        if (el) el.innerText = txt;
                    }}
                    function setStyle(id, prop, val) {{
                        const el = pDoc.getElementById(id);
                        if (el) el.style[prop] = val;
                    }}
                    function setClass(id, cls) {{
                        const el = pDoc.getElementById(id);
                        if (el) el.className = cls;
                    }}
                    function fmt(secs) {{
                        let s = Math.floor(secs);
                        let m = Math.floor(s / 60);
                        s = s % 60;
                        return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
                    }}

                    function connect() {{
                        if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;
                        ws = new WebSocket(WS_URL);
                        ws.binaryType = "arraybuffer";

                        ws.onopen = function() {{
                            status.textContent = "\\u25cf LIVE";
                            status.style.background = "rgba(0,180,80,0.7)";
                            setTxt("api-status", "🟢 ONLINE");
                            clearInterval(heartbeatTimer);
                            heartbeatTimer = setInterval(() => {{
                                if (ws.readyState === WebSocket.OPEN) ws.send("ping");
                            }}, 15000);
                        }};

                        ws.onmessage = function(evt) {{
                            if (typeof evt.data === "string") {{
                                if (evt.data === "pong" || evt.data === "keepalive") return;
                                try {{
                                    const state = JSON.parse(evt.data);
                                    
                                    // Update Metrics
                                    setTxt("val-total", state.total_count);
                                    setClass("card-total", "metric-card " + (state.total_count > 0 ? "status-good" : ""));
                                    setTxt("val-in", state.in_count);
                                    setClass("card-in", "metric-card " + (state.in_count > 0 ? "status-good" : ""));
                                    setTxt("val-fps", state.fps);
                                    setClass("card-fps", "metric-card " + (state.fps >= 20 ? "status-good" : (state.fps >= 10 ? "status-warning" : "status-danger")));
                                    
                                    // Update Video Status
                                    setTxt("val-duration", fmt(state.duration_s));
                                    setTxt("val-elapsed", fmt(state.elapsed_s));
                                    setTxt("val-remaining", fmt(state.remaining_s));
                                    setTxt("val-progress-text", state.progress_pct + "%");
                                    setStyle("val-progress-bar", "width", state.progress_pct + "%");
                                    setStyle("val-progress-bar", "background", state.progress_pct < 90 ? "#00ff99" : "#ffcc00");
                                    setTxt("val-session-rt", fmt(state.session_runtime_s));
                                    setTxt("val-proc-frames", state.processed_frames.toLocaleString());
                                    setTxt("val-replay-cnt", state.replay_count);
                                    
                                    // Update API Status
                                    setTxt("api-mode", state.stream_mode);
                                    setTxt("api-stream-status", state.stream_status);
                                    
                                    // Update Latency
                                    let now = performance.now();
                                    setTxt("api-latency", Math.round(now - lastFrameTime));
                                    
                                    // Update Tab 2 Status
                                    let ind = "🔴";
                                    if (state.stream_paused) ind = "⏸️";
                                    else if (state.stream_finished) ind = "🔵";
                                    else if (state.status === "active") ind = "🟢";
                                    setTxt("tab2-indicator", ind);
                                    setTxt("tab2-status", state.stream_status);

                                    // Update Controls
                                    const btnPlayPause = pDoc.getElementById("ws-btn-playpause");
                                    const btnReplay = pDoc.getElementById("ws-btn-replay");
                                    if (btnPlayPause) {{
                                        btnPlayPause.innerText = state.stream_paused ? "▶️" : "⏸️";
                                        btnPlayPause.disabled = state.stream_finished;
                                    }}
                                    if (btnReplay) {{
                                        btnReplay.disabled = !state.stream_finished;
                                    }}
                                }} catch (e) {{}}
                            }} else {{
                                lastFrameTime = performance.now();
                                if (lastUrl) URL.revokeObjectURL(lastUrl);
                                const blob = new Blob([evt.data], {{type: "image/jpeg"}});
                                lastUrl = URL.createObjectURL(blob);
                                img.src = lastUrl;
                            }}
                        }};

                        ws.onclose = function() {{
                            status.textContent = "\\u25cb Reconnecting...";
                            status.style.background = "rgba(200,50,50,0.7)";
                            setTxt("api-status", "🔴 OFFLINE");
                            clearInterval(heartbeatTimer);
                            clearTimeout(reconnectTimer);
                            reconnectTimer = setTimeout(connect, 2000);
                        }};
                        ws.onerror = function() {{ ws.close(); }};
                    }}

                    // Attach click listeners to Streamlit DOM buttons
                    const attachInterval = setInterval(() => {{
                        const btnReplay = pDoc.getElementById("ws-btn-replay");
                        if (btnReplay) {{
                            const btnPlayPause = pDoc.getElementById("ws-btn-playpause");
                            const btnReset = pDoc.getElementById("ws-btn-reset");
                            if (btnPlayPause) btnPlayPause.onclick = () => {{ if(!btnPlayPause.disabled && ws && ws.readyState===1) ws.send(JSON.stringify({{action: "toggle_pause"}})); }};
                            if (btnReplay) btnReplay.onclick = () => {{ if(!btnReplay.disabled && ws && ws.readyState===1) ws.send(JSON.stringify({{action: "replay"}})); }};
                            if (btnReset) btnReset.onclick = () => {{ if(!btnReset.disabled && ws && ws.readyState===1) ws.send(JSON.stringify({{action: "reset_count"}})); }};
                            clearInterval(attachInterval);
                        }}
                    }}, 200);

                    connect();
                </script>
            ''', height=600)
        else:
            st.error("\ud83d\udd0c API Disconnected. Retrying automatically...")

    with col_stats:
        # ── Dynamic Status Color Logic ──
        fps = stats.get("fps", 0)
        total = stats.get("total_count", 0)
        in_count = stats.get("in_count", 0)

        if fps >= 20:
            fps_class = "status-good"
        elif fps >= 10:
            fps_class = "status-warning"
        else:
            fps_class = "status-danger"

        total_class = "status-good" if total > 0 else ""
        in_class = "status-good" if in_count > 0 else ""

        st.markdown("### Analytics")
        # ── Video Status Panel (new — only visible in file mode) ──
        _stream_mode = source_state.get('mode', 'file')
        if _stream_mode == 'file':
            duration_s  = stats.get('duration_s', 0)
            elapsed_s   = stats.get('elapsed_s', 0)
            remaining_s = stats.get('remaining_s', 0)
            progress    = stats.get('progress_pct', 0)
            replay_cnt  = stats.get('replay_count', 0)
            proc_frames = stats.get('processed_frames', 0)
            sess_rt     = stats.get('session_runtime_s', 0)

            def _fmt(secs):
                secs = int(secs)
                return f"{secs // 60:02d}:{secs % 60:02d}"

            # Progress bar fill colour based on progress
            bar_colour = "#00ff99" if progress < 90 else "#ffcc00"
            st.markdown(f"""
                <div class='video-status-box'>
                    <h4>Detail Information</h4>
                    <div class='video-status-row'><span>Duration</span><span id='val-duration' class='video-status-value'>{_fmt(duration_s)}</span></div>
                    <div class='video-status-row'><span>Elapsed</span><span id='val-elapsed' class='video-status-value'>{_fmt(elapsed_s)}</span></div>
                    <div class='video-status-row'><span>Remaining</span><span id='val-remaining' class='video-status-value'>{_fmt(remaining_s)}</span></div>
                    <div class='video-status-row'><span>Progress</span><span id='val-progress-text' class='video-status-value'>{progress}%</span></div>
                    <div class='progress-bar-bg'><div id='val-progress-bar' class='progress-bar-fill' style='width:{progress}%'></div></div>
                    <div class='video-status-row' style='margin-top:8px'><span>Session Runtime</span><span id='val-session-rt' class='video-status-value'>{_fmt(sess_rt)}</span></div>
                    <div class='video-status-row'><span>Processed Frames</span><span id='val-proc-frames' class='video-status-value'>{proc_frames:,}</span></div>
                    <div class='video-status-row'><span>Replay Count</span><span id='val-replay-cnt' class='video-status-value'>{replay_cnt}</span></div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown(f"<div id='card-total' class='metric-card {total_class}'><h4>COCONUT COUNT</h4><h1 id='val-total'>{total}</h1></div>", unsafe_allow_html=True)


        # ── Stream Control Buttons ──
        st.markdown("---")
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
        _is_paused = source_state.get('is_paused', False)
        _is_finished = source_state.get('is_finished', False)

        with ctrl_col1:
            st.markdown(f'<div class="stButton"><button id="ws-btn-playpause" style="width: 100%;" {"disabled" if _is_finished else ""}>{"▶️" if _is_paused else "⏸️"}</button></div>', unsafe_allow_html=True)
        with ctrl_col2:
            st.markdown(f'<div class="stButton"><button id="ws-btn-replay" style="width: 100%;" {"" if _is_finished else "disabled"}>🔁</button></div>', unsafe_allow_html=True)
        with ctrl_col3:
            st.markdown('<div class="stButton"><button id="ws-btn-reset" style="width: 100%;">🗑️</button></div>', unsafe_allow_html=True)

    # ── Diagnostic Logs ──
    st.markdown("---")
    st.markdown("**Diagnostic Logs:**")
    logs_html = "<br>".join(st.session_state.logs[:10])
    st.markdown(f"<div class='log-box'>{logs_html}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB 2 — PRODUCTION SETTINGS
# ─────────────────────────────────────────────
with tab_settings:
    if not st.session_state.settings:
        st.warning("⚠️ Cannot connect to backend API. Start the FastAPI server then refresh.")
    else:
        s = st.session_state.settings

        # ── Source Mode Panel (outside main form so it can POST independently) ──
        st.markdown("## 📡 Stream Source Configuration")
        st.caption("Switch between **File Playback** and **Live Stream** mode. Changes apply immediately.")

        _cur_mode = source_state.get('mode', 'file')
        _mode_options = ["file", "live"]
        _mode_labels = {"file": "📁 File Playback", "live": "📷 Live Stream (RTSP / Camera)"}

        src_col1, src_col2, src_col3 = st.columns([1, 2, 1])
        with src_col1:
            selected_mode = st.radio(
                "Source Mode",
                _mode_options,
                index=_mode_options.index(_cur_mode) if _cur_mode in _mode_options else 0,
                format_func=lambda x: _mode_labels[x],
            )

        with src_col2:
            if selected_mode == "file":
                st.markdown("File Playback")
                src_file = st.text_input(
                    "Video File Path",
                    value=source_state.get('file_path', ''),
                    placeholder="Absolute path, e.g. C:/videos/line_A.mp4",
                    help="The video will play once and stop — no looping."
                )
                src_live_url = source_state.get('live_url', '')
            else:
                src_live_url = st.text_input(
                    "Live Source URL / Camera Index",
                    value=source_state.get('live_url', ''),
                    placeholder="rtsp://user:pass@192.168.1.10/stream or 0 for webcam",
                    help="RTSP, HTTP-MJPEG, or integer webcam index."
                )
                src_reconnect = st.number_input(
                    "Reconnect Interval (s)",
                    min_value=1.0, max_value=60.0,
                    value=float(source_state.get('reconnect_interval', 3.0)),
                    step=0.5
                )
                src_max_retries = st.number_input(
                    "Max Retries (0 = infinite)",
                    min_value=0, max_value=100,
                    value=int(source_state.get('max_retries', 10))
                )
                src_file = source_state.get('file_path', '')

        with src_col3:
            _status_msg = source_state.get('status_message', '–')
            _is_connected = source_state.get('is_connected', False)
            _tab2_is_paused = source_state.get('is_paused', False)
            _tab2_finished = source_state.get('is_finished', False)
            if _tab2_is_paused:
                _indicator = "⏸️"
            elif _is_connected:
                _indicator = "🟢"
            elif _tab2_finished:
                _indicator = "🔵"
            else:
                _indicator = "🔴"
            st.markdown(
                f"""
                <div class="custom-info-box">
                    <span id='tab2-indicator'>{_indicator}</span>
                    Stream Status:
                    <strong><span id='tab2-status'>{_status_msg}</span></strong>
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.button("✅ Apply Source", use_container_width=True):
            payload = {
                "mode": selected_mode,
                "file_path": src_file if selected_mode == "file" else source_state.get('file_path', ''),
                "live_url": src_live_url if selected_mode == "live" else source_state.get('live_url', ''),
                "reconnect_interval": src_reconnect if selected_mode == "live" else float(source_state.get('reconnect_interval', 3.0)),
                "max_retries": src_max_retries if selected_mode == "live" else int(source_state.get('max_retries', 10)),
            }
            try:
                r = requests.post(SOURCE_URL, json=payload, timeout=2.0)
                if r.status_code == 200:
                    add_log(f"Source updated: mode={selected_mode}")
                    st.success("✅ Source applied!")
                else:
                    st.error(f"Backend error: HTTP {r.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")

        st.markdown("---")

        with st.form("settings_form"):
            st.markdown("## ⚙️ Production Configuration Panel")
            st.caption("Adjust all parameters below, then click **Apply** to push to the AI backend.")
            st.markdown("---")

            col_det, col_track = st.columns(2)

            with col_det:
                st.markdown("### 🎯 Detection Settings")
                s['conf_thresh'] = st.slider("Confidence Threshold", 0.0, 1.0, s.get('conf_thresh', 0.25), 0.05,
                                             help="Minimum detection confidence. Lower = more detections, more noise.")
                s['iou_thresh'] = st.slider("IOU Threshold (NMS)", 0.0, 1.0, s.get('iou_thresh', 0.5), 0.05,
                                            help="NMS IOU overlap threshold. Lower = fewer overlapping boxes kept.")
                s['imgsz'] = st.select_slider("Image Size (imgsz)", options=[256, 320, 416, 512, 640, 768, 960, 1280], value=s.get('imgsz', 640),
                                              help="Inference resolution. Higher = more accurate but slower.")

                st.markdown("### 📏 Line Config (Counting)")
                s['line_start_x'] = st.slider("Line Start X", 0, 1280, s.get('line_start_x', 560))
                s['line_end_x'] = st.slider("Line End X", 0, 1280, s.get('line_end_x', 590))

            with col_track:
                st.markdown("### 🔁 Tracker Settings")
                s['track_high_thresh'] = st.slider("Track High Threshold", 0.0, 1.0, s.get('track_high_thresh', 0.3), 0.05,
                                                   help="Min confidence to start a new confirmed track.")
                s['track_low_thresh'] = st.slider("Track Low Threshold", 0.0, 1.0, s.get('track_low_thresh', 0.1), 0.05,
                                                  help="Min confidence for second-pass association (occluded objects).")
                s['new_track_thresh'] = st.slider("New Track Threshold", 0.0, 1.0, s.get('new_track_thresh', 0.4), 0.05,
                                                  help="Confidence threshold to initialize a brand new track.")
                s['track_buffer'] = st.slider("Track Buffer (frames)", 10, 120, s.get('track_buffer', 60), 5,
                                             help="How many frames a lost track is remembered. Higher = fewer ID switches.")
                s['match_thresh'] = st.slider("Match Threshold (IOU)", 0.0, 1.0, s.get('match_thresh', 0.9), 0.05,
                                             help="IOU threshold for associating detections to existing tracks.")
                s['min_box_area'] = st.slider("Min Box Area", 0.0, 100.0, s.get('min_box_area', 1.0), 1.0,
                                             help="Discard tracks whose bounding box area is below this value.")
                s['mot20'] = st.checkbox("MOT20 Mode", s.get('mot20', False),
                                         help="Enable for dense multi-object scenarios (MOT20 dataset style).")

            st.markdown("---")
            submitted = st.form_submit_button("🚀 Apply Configuration", use_container_width=True)
            if submitted:
                try:
                    resp = requests.post(SETTINGS_URL, json=s, timeout=2.0)
                    if resp.status_code == 200:
                        add_log("Settings updated successfully.")
                        st.success("✅ Configuration applied to backend successfully!")
                    else:
                        add_log(f"Failed to update settings: HTTP {resp.status_code}")
                        st.error(f"Backend returned HTTP {resp.status_code}")
                except Exception as e:
                    add_log(f"Error updating settings: {e}")
                    st.error(f"Connection error: {e}")