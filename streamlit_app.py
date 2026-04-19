import streamlit as st
import requests
import json
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="RAG Observability Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM THEME STYLES (Professional Dark Enterprise Theme) ---
st.markdown("""
<style>
    /* ===== GOOGLE FONT IMPORT ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ===== ROOT VARIABLES ===== */
    :root {
        --bg-primary: #0E1117;
        --bg-card: #161B22;
        --bg-code: #0D1117;
        --accent-cyan: #00E5FF;
        --accent-purple: #7C4DFF;
        --border: #2A2F3A;
        --text-primary: #E6EDF3;
        --text-secondary: #9DA7B3;
        --text-code: #7EE787;
        --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.4);
        --shadow-hover: 0 8px 32px rgba(0, 229, 255, 0.15);
    }

    /* ===== GLOBAL BACKGROUND ===== */
    .stApp {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ===== GLOBAL TEXT RESET ===== */
    h1, h2, h3, h4, h5, h6, label, p, span, div, li, td, th, caption {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ===== ANIMATED GRADIENT TITLE ===== */
    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: title-glow 4s ease-in-out infinite alternate;
        margin-bottom: 35px;
        letter-spacing: -0.5px;
    }

    @keyframes title-glow {
        from { filter: drop-shadow(0 0 6px rgba(0,229,255,0.4)); }
        to   { filter: drop-shadow(0 0 18px rgba(124,77,255,0.5)); }
    }

    /* ===== BLINKING STATUS INDICATOR ===== */
    @keyframes blink {
        0%   { opacity: 1; }
        50%  { opacity: 0.35; }
        100% { opacity: 1; }
    }
    .blinking {
        animation: blink 2s ease-in-out infinite;
        color: var(--accent-cyan) !important;
        font-weight: 600;
        font-size: 14px;
    }

    /* ===== METRIC CARDS ===== */
    .metric-box {
        background: var(--bg-card);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid var(--border);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 10px;
        box-shadow: var(--shadow-card);
    }
    .metric-box:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-hover);
        border-color: var(--accent-cyan);
    }
    .metric-title {
        font-size: 11px;
        color: var(--text-secondary) !important;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 500;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--accent-cyan) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ===== CACHE HIT BANNER ===== */
    .cache-hit {
        background: linear-gradient(135deg, #00E5FF, #7C4DFF);
        color: #FFFFFF !important;
        padding: 14px 24px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 15px;
        animation: pulse-banner 2.5s ease-in-out infinite;
        margin-bottom: 20px;
        text-align: center;
        letter-spacing: 0.02em;
    }
    .cache-hit * {
        color: #FFFFFF !important;
    }
    @keyframes pulse-banner {
        0%   { opacity: 0.85; box-shadow: 0 0 20px rgba(0,229,255,0.2); }
        50%  { opacity: 1;    box-shadow: 0 0 30px rgba(124,77,255,0.3); }
        100% { opacity: 0.85; box-shadow: 0 0 20px rgba(0,229,255,0.2); }
    }

    /* ===== PANELS / CARDS ===== */
    .panel {
        background: var(--bg-card) !important;
        border: 1px solid var(--border);
        padding: 20px;
        border-radius: 12px;
        box-shadow: var(--shadow-card);
        color: var(--text-primary) !important;
    }
    .panel * {
        color: var(--text-primary) !important;
    }

    /* ===== GLOW TEXT ===== */
    .glow {
        color: var(--accent-cyan) !important;
        text-shadow: 0 0 12px rgba(0,229,255,0.4);
        font-weight: 600;
    }

    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        color: var(--text-secondary) !important;
        font-size: 13px;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid var(--border);
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    /* ===== CONTROL PANEL TITLE ===== */
    .control-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--accent-cyan) !important;
        margin-bottom: 12px;
        letter-spacing: -0.3px;
    }

    /* ===== STATUS BADGES ===== */
    .status-box {
        background: rgba(0,229,255,0.06);
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(0,229,255,0.15);
        margin-bottom: 10px;
    }

    /* ===============================================
       DEEP STREAMLIT WIDGET OVERRIDES
       Fix white-on-white visibility issues
       =============================================== */

    /* --- File Uploader Container --- */
    section[data-testid="stFileUploader"],
    div[data-testid="stFileUploader"] {
        background: var(--bg-card) !important;
        border-radius: 10px !important;
        border: 1px dashed var(--border) !important;
        padding: 12px !important;
    }
    section[data-testid="stFileUploader"] *,
    div[data-testid="stFileUploader"] * {
        color: var(--text-primary) !important;
    }
    /* Uploaded file name chip */
    div[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"],
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] span {
        color: var(--text-primary) !important;
    }
    /* Browse files button inside uploader */
    section[data-testid="stFileUploader"] button,
    div[data-testid="stFileUploader"] button {
        background: rgba(0,229,255,0.1) !important;
        color: var(--accent-cyan) !important;
        border: 1px solid var(--accent-cyan) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stFileUploader"] button:hover,
    div[data-testid="stFileUploader"] button:hover {
        background: rgba(0,229,255,0.2) !important;
    }

    /* --- Uploaded File Chips / Tags --- */
    div[data-testid="stFileUploaderFile"],
    div[data-testid="stFileUploaderFile"] * {
        background: var(--bg-code) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stFileUploaderFile"] span,
    div[data-testid="stFileUploaderFile"] small {
        color: var(--text-secondary) !important;
    }
    /* Delete button on uploaded file */
    div[data-testid="stFileUploaderFile"] button {
        background: transparent !important;
        color: #f87171 !important;
        border: none !important;
    }

    /* --- Text Input --- */
    div[data-testid="stTextInput"] input,
    .stTextInput input {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        caret-color: var(--accent-cyan) !important;
        transition: border-color 0.2s ease !important;
    }
    div[data-testid="stTextInput"] input:focus,
    .stTextInput input:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 2px rgba(0,229,255,0.15) !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: var(--text-secondary) !important;
        opacity: 0.7 !important;
    }
    div[data-testid="stTextInput"] label {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }

    /* --- Buttons --- */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.02em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(0,229,255,0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(124,77,255,0.3) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* --- Code Blocks (JSON Logs) --- */
    pre, code,
    div[data-testid="stCode"],
    div[data-testid="stCode"] pre,
    div[data-testid="stCode"] code,
    .stCode, .stCode pre, .stCode code {
        background: var(--bg-code) !important;
        color: var(--text-code) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
    }

    /* --- st.info / st.success / st.warning / st.error banners --- */
    div[data-testid="stAlert"] {
        border-radius: 10px !important;
    }
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span {
        color: var(--text-primary) !important;
    }

    /* --- Caption text --- */
    .stCaption, div[data-testid="stCaptionContainer"] * {
        color: var(--text-secondary) !important;
        font-size: 13px !important;
    }

    /* --- Expanders --- */
    details, summary,
    div[data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }
    div[data-testid="stExpander"] * {
        color: var(--text-primary) !important;
    }

    /* --- Spinner --- */
    .stSpinner > div {
        border-top-color: var(--accent-cyan) !important;
    }

    /* --- Horizontal Rule --- */
    hr {
        border-color: var(--border) !important;
        opacity: 0.5;
    }

    /* --- Scrollbar Styling --- */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }

    /* --- Markdown inside .panel blocks --- */
    .panel p, .panel span, .panel div, .panel li {
        color: var(--text-primary) !important;
    }
    .panel strong, .panel b {
        color: var(--accent-cyan) !important;
    }
    .panel code, .panel pre {
        background: var(--bg-code) !important;
        color: var(--text-code) !important;
    }

    /* --- Sidebar divider --- */
    section[data-testid="stSidebar"] hr {
        border-color: var(--border) !important;
    }

    /* --- Sidebar buttons --- */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
    }

    /* --- Sidebar headings --- */
    section[data-testid="stSidebar"] h3 {
        color: var(--accent-cyan) !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }

    /* --- Native st.metric() Widgets --- */
    div[data-testid="stMetric"] {
        background: var(--bg-card) !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        box-shadow: var(--shadow-card) !important;
        text-align: center !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: var(--shadow-hover) !important;
        border-color: var(--accent-cyan) !important;
    }
    div[data-testid="stMetric"] label {
        color: var(--text-secondary) !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--accent-cyan) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 22px !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        color: var(--text-secondary) !important;
    }

    /* --- Wide layout element spacing --- */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8000"

st.markdown('<div class="main-title">Enterprise RAG Observability Dashboard</div>', unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    st.markdown('<div class="control-title">⚙️ Control Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="blinking">System Status: ONLINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="blinking">Cache Status: CONNECTED</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Upload Document")
    uploaded_file = st.file_uploader("Accepts PDF or TXT", type=["pdf", "txt"])
    
    if st.button("Upload via API"):
        if uploaded_file is not None:
            with st.spinner("Processing..."):
                try:
                    start_time = time.time()
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    latency = time.time() - start_time
                    
                    if response.status_code == 200:
                        st.success(f"File stored safely. Upload Latency: {latency:.2f}s")
                    else:
                        st.error(f"API rejection: {response.text}")
                except Exception as e:
                    st.error("API connection failed")
        else:
            st.warning("Please browse and attach a document.")

# ================================
# QUERY SECTION 
# ================================
query = st.text_input("Ask a question:")

if st.button("Trigger Query Sequence"):
    if not query.strip():
        st.warning("Query cannot be blank.")
    else:
        with st.spinner("Processing pipeline sequence..."):
            try:
                rq_start = time.time()
                payload = {"query": query}
                res = requests.post(f"{API_BASE_URL}/query", json=payload, stream=True)
                
                if res.status_code == 200:
                    answer = ""
                    metrics = {}
                    retrieved_chunks = []
                    cache_hit = False

                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown('<div class="panel">', unsafe_allow_html=True)
                        st.markdown('<h3 class="glow">LLM Generation Payload</h3>', unsafe_allow_html=True)
                        placeholder = st.empty()
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Process Streaming Loop
                    for line in res.iter_lines():
                        if line:
                            chunk = json.loads(line)

                            if chunk["type"] == "token":
                                answer += chunk["token"]
                                placeholder.markdown(f"{answer}▌")

                            elif chunk["type"] == "metric":
                                metrics[chunk["metric"]] = chunk["value"]

                            elif chunk["type"] == "retrieved_chunks":
                                retrieved_chunks = chunk["chunks"]

                            elif chunk["type"] == "cache":
                                cache_hit = chunk["cache_hit"]
                                
                            elif chunk["type"] == "final":
                                if not answer and chunk.get("answer"):
                                    answer = chunk["answer"]
                                placeholder.markdown(answer)
                                
                    overall_latency = time.time() - rq_start

                    # ----- Cache Status Banner -----
                    if cache_hit:
                        st.markdown('<div class="cache-hit">⚡ Cache Hit — Instant Response from Redis</div>', unsafe_allow_html=True)
                    else:
                        st.info("Cache Miss — Full pipeline executed.")
                    
                    with col2:
                        st.markdown('<div class="panel">', unsafe_allow_html=True)
                        st.markdown('<h3 class="glow">Retrieved Vectors</h3>', unsafe_allow_html=True)
                        if retrieved_chunks:
                            for idx, c in enumerate(retrieved_chunks):
                                st.markdown(f"**Chunk {idx+1}:**")
                                st.caption(c[:150] + "...")
                                st.markdown("---")
                        else:
                            st.write("No constraints mapped locally.")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # ----- Metrics View -----
                    st.markdown('<h3 class="glow">Metrics Telemetry</h3>', unsafe_allow_html=True)

                    if cache_hit:
                        embedding_time  = "Skipped (Cache Hit)"
                        retrieval_time  = "Skipped (Cache Hit)"
                        reranking_time  = "Skipped (Cache Hit)"
                        generation_time = "Skipped (Cache Hit)"
                        total_time      = f"{overall_latency:.4f}s"
                    else:
                        embedding_time  = f"{metrics.get('embedding_time', 0):.4f}s"
                        retrieval_time  = f"{metrics.get('retrieval_time', 0):.4f}s"
                        reranking_time  = f"{metrics.get('reranking_time', 0):.4f}s"
                        generation_time = f"{metrics.get('generation_time', 0):.4f}s"
                        total_time      = f"{metrics.get('total_time', 0):.4f}s"

                    col1, col2, col3, col4, col5 = st.columns(5)

                    col1.metric("Embedding Time", embedding_time)
                    col2.metric("Retrieval Time", retrieval_time)
                    col3.metric("Reranking Time", reranking_time)
                    col4.metric("Generation Time", generation_time)
                    col5.metric("Total Time", total_time)
                            
                    st.markdown("---")
                    
                    # ----- Logs Presentation -----
                    st.markdown('<h3 class="glow">Structured JSON Logs Simulation</h3>', unsafe_allow_html=True)
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    
                    log_array = []
                    log_array.append({"event": "query_received", "time": f"+0.000s"})
                    if cache_hit:
                        log_array.append({"event": "cache_hit_intercept", "time": f"+{metrics.get('total_time', 0):.4f}s"})
                        log_array.append({"event": "query_resolved", "latencies_bounded": True})
                    else:
                        log_array.append({"event": "embedding_complete", "time": f"+{metrics.get('embedding_time', 0):.4f}s"})
                        log_array.append({"event": "retrieval_complete", "time": f"+{metrics.get('retrieval_time', 0):.4f}s"})
                        log_array.append({"event": "reranking_complete", "time": f"+{metrics.get('reranking_time', 0):.4f}s"})
                        log_array.append({"event": "generation_complete", "time": f"+{metrics.get('generation_time', 0):.4f}s"})
                        log_array.append({"event": "cache_storage_update_complete", "status": "success"})
                        
                    for lg in log_array:
                        st.code(json.dumps(lg, indent=2), language="json")
                        
                    st.markdown('</div>', unsafe_allow_html=True)

                else:
                    st.error(f"API Rejection Flag: {res.status_code}")
                    st.write(res.text)
                    
            except requests.exceptions.RequestException as e:
                st.error("API connection failed")

st.markdown('<div class="footer">Enterprise RAG System with Observability</div>', unsafe_allow_html=True)
