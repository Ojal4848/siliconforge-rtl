import streamlit as st
import os
import re
import io
import zipfile
import subprocess
from groq import Groq
from agent_engine import run_autonomous_loop, detect_eda_environment

# Page Configuration
st.set_page_config(
    page_title="SILICONFORGE | Autonomous RTL & EDA Platform",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise Scrollable Architectural CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html {
        scroll-behavior: smooth;
    }

    /* Top Toolbar & Header Fix */
    header, header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stAppHeader"] {
        background-color: #060913 !important;
        border-bottom: 1px solid #1e293b !important;
    }
    div[data-testid="stToolbar"] button, div[data-testid="stToolbar"] span, div[data-testid="stToolbar"] svg {
        color: #f8fafc !important;
        fill: #f8fafc !important;
    }
    div[data-testid="stDeployButton"] button {
        background-color: #0f172a !important;
        border: 1px solid #38bdf8 !important;
        color: #38bdf8 !important;
    }

    /* Eliminate Any Floating White Bottom Container */
    div[data-testid="stBottom"], div[data-testid="stBottom"] > div {
        background-color: transparent !important;
        background: transparent !important;
    }

    /* Core Scrollable Canvas */
    .stApp {
        background-color: #060913 !important;
        background-image: 
            linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Global Text Contrast Enforcement */
    p, span, label, h1, h2, h3, h4, h5, h6, li, div {
        color: #f8fafc !important;
    }

    /* Inline Code Badges */
    code {
        background-color: #0f172a !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        padding: 0.15rem 0.45rem !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Top Navigation Bar */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.6rem;
        background: #0b101d;
        border: 1px solid #1e293b;
        border-radius: 6px;
        margin-bottom: 1.8rem;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .brand-logo {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.12em !important;
        color: #ffffff !important;
    }
    .brand-logo span {
        color: #38bdf8 !important;
    }
    .nav-menu {
        display: flex;
        gap: 1.4rem;
        align-items: center;
        flex-wrap: wrap;
    }
    .nav-menu a {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        color: #e2e8f0 !important;
        text-decoration: none !important;
        letter-spacing: 0.06em;
        transition: color 0.2s ease;
    }
    .nav-menu a:hover {
        color: #38bdf8 !important;
    }
    .nav-cta {
        border: 1px solid #38bdf8 !important;
        padding: 0.35rem 0.85rem !important;
        border-radius: 4px;
        color: #38bdf8 !important;
    }

    /* Hero Section */
    .hero-box {
        background: linear-gradient(135deg, #0b1120 0%, #0f172a 60%, #111c33 100%);
        border: 1px solid #1e293b;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 2.2rem 2.4rem;
        margin-bottom: 1.5rem;
    }
    .hero-kicker {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        color: #38bdf8 !important;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .hero-heading {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2.7rem !important;
        font-weight: 700 !important;
        line-height: 1.15 !important;
        color: #ffffff !important;
        margin-bottom: 0.85rem;
    }
    .hero-desc {
        font-size: 1.04rem !important;
        color: #e2e8f0 !important;
        line-height: 1.65;
        font-weight: 400 !important;
    }

    /* Bracketed Section Headers */
    .section-bracket {
        text-align: center;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.16em !important;
        color: #38bdf8 !important;
        margin: 3rem 0 1.5rem 0;
        padding: 0.8rem 0;
        border-top: 1px solid #1e293b;
        border-bottom: 1px solid #1e293b;
        background: rgba(11, 16, 29, 0.7);
    }

    /* Telemetry Strip */
    .stat-box {
        background: #0b101d;
        border: 1px solid #1e293b;
        border-top: 2px solid #38bdf8;
        border-radius: 6px;
        padding: 1.2rem;
        text-align: center;
    }
    .stat-num {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }
    .stat-title {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
        color: #f8fafc !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.25rem;
    }

    /* Service Cards */
    .service-card {
        background: #0b101d;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 1.5rem;
        height: 100%;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .service-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
    }
    .service-index {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
        color: #38bdf8 !important;
        margin-bottom: 0.5rem;
    }
    .service-title {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.22rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-bottom: 0.6rem;
    }
    .service-text {
        font-size: 0.94rem !important;
        color: #e2e8f0 !important;
        line-height: 1.6;
        font-weight: 400 !important;
    }
    .service-link {
        display: inline-block;
        margin-top: 0.9rem;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
        color: #38bdf8 !important;
        text-decoration: none !important;
    }

    /* Text Areas & Text Inputs */
    textarea, input[type="text"] {
        background-color: #090e1a !important;
        color: #38bdf8 !important;
        border: 1.5px solid #334155 !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.95rem !important;
    }
    textarea:focus, input[type="text"]:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.25) !important;
    }

    /* Primary & Download Buttons */
    .stButton>button, .stDownloadButton>button, a[data-testid="stBaseLinkButton-secondary"] {
        background: #0284c7 !important;
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 6px !important;
        padding: 0.6rem 1.4rem !important;
        letter-spacing: 0.04em !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background: #0369a1 !important;
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.35) !important;
    }

    /* Embedded Architect Console Styling */
    .console-header {
        background: #0b101d;
        border: 1px solid #1e293b;
        border-bottom: 2px solid #38bdf8;
        border-radius: 8px 8px 0 0;
        padding: 0.9rem 1.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }
    .console-status {
        color: #6ee7b7 !important;
    }
    .chat-msg-user {
        background: #0f172a;
        border-left: 3px solid #38bdf8;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.3rem;
        margin: 0.75rem 0;
    }
    .chat-msg-ai {
        background: #0b101d;
        border: 1px solid #1e293b;
        border-left: 3px solid #10b981;
        border-radius: 0 8px 8px 0;
        padding: 1.1rem 1.4rem;
        margin: 0.75rem 0;
    }
    .chat-role-tag {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    /* Footer */
    .site-footer {
        margin-top: 3.5rem;
        padding: 1.5rem;
        border-top: 1px solid #1e293b;
        text-align: center;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
        color: #cbd5e1 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #080c17 !important;
        border-right: 1px solid #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

def extract_vivado_summary(util_path="utilization.rpt"):
    luts, ffs, dsps = "0", "0", "0"
    if os.path.exists(util_path):
        with open(util_path, "r") as f:
            content = f.read()
        lut_match = re.search(r"\|\s*CLB LUTs\*?\s*\|\s*(\d+)", content)
        ff_match = re.search(r"\|\s*CLB Registers\s*\|\s*(\d+)", content)
        dsp_match = re.search(r"\|\s*DSPs\s*\|\s*(\d+)", content)
        if lut_match: luts = lut_match.group(1)
        if ff_match: ffs = ff_match.group(1)
        if dsp_match: dsps = dsp_match.group(1)
    return luts, ffs, dsps

def build_vivado_zip():
    """Packages RTL, Testbench, and Vivado TCL script into a downloadable ZIP bundle."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in ["design.sv", "tb_design.sv", "run_synth.tcl"]:
            if os.path.exists(fname):
                zf.write(fname)
    return buf.getvalue()

def ask_architect_copilot(prompt_text: str, api_key: str, model_name: str):
    """Queries the SoC Architect LLM with live design.sv and utilization.rpt context."""
    st.session_state.chat_history.append({"role": "user", "content": prompt_text})
    client = Groq(api_key=api_key)
    
    rtl_context = ""
    if os.path.exists("design.sv"):
        with open("design.sv", "r") as f:
            rtl_context = f.read()

    util_context = ""
    if os.path.exists("utilization.rpt"):
        with open("utilization.rpt", "r") as f:
            util_context = f.read()[:1500]

    system_context = (
        "You are a Principal SoC Hardware Architect. Provide concise, actionable, engineering-grade answers "
        "on RTL design, timing closure, pipelining, and FPGA/ASIC resource inference.\n"
        f"Active RTL (`design.sv`):\n```verilog\n{rtl_context}\n```\n"
        f"Synthesis Summary:\n{util_context}"
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_context},
            *st.session_state.chat_history[-6:]
        ],
        max_tokens=900
    )
    bot_reply = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

eda_env = detect_eda_environment()
active_engine_label = "AMD VIVADO 2022.2" if eda_env["has_vivado"] else ("YOSYS CLOUD EDA" if eda_env["has_yosys"] else "CLOUD COMPILER")

# ==============================================================================
# SIDEBAR: API CONTROLS, VIVADO IDE LAUNCHER & ZIP EXPORT
# ==============================================================================
st.sidebar.markdown("### SYSTEM CONFIGURATION")
user_api_key = st.sidebar.text_input("Groq API Key", type="password", placeholder="gsk_...")

available_models = []
if user_api_key.strip():
    try:
        client = Groq(api_key=user_api_key.strip())
        models_data = client.models.list()
        available_models = [
            m.id for m in models_data.data 
            if any(k in m.id.lower() for k in ["llama-3", "mixtral", "qwen"]) 
            and not any(x in m.id.lower() for x in ["guard", "whisper", "vision", "embed", "orpheus", "playht"])
        ]
    except Exception:
        st.sidebar.error("API Authentication Failed.")

if not available_models:
    available_models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"]

model_choice = st.sidebar.selectbox("Synthesis LLM Model", available_models)
target_luts = st.sidebar.number_input("Max CLB LUT Budget", value=250, step=10)
max_retries = st.sidebar.slider("Optimization Passes", min_value=1, max_value=3, value=2)

st.sidebar.markdown("---")
st.sidebar.markdown("### EDA WORKSPACE LAUNCHER")

# Always show Open Project in Vivado IDE button
if st.sidebar.button("Open Project in Vivado IDE", use_container_width=True):
    if eda_env["has_vivado"]:
        xpr_path = os.path.abspath("agent_project/agent_project.xpr")
        if os.path.exists(xpr_path):
            subprocess.Popen([eda_env["vivado_bin"], xpr_path])
            st.sidebar.success("Launching AMD Vivado GUI...")
        else:
            st.sidebar.error("No active .xpr project found. Execute synthesis first.")
    else:
        st.sidebar.info("Cloud Host Detected: Download the Vivado Bundle (.ZIP) below to open on your local PC's Vivado IDE, or use the Online Simulator.")

# Downloadable Vivado Project Bundle (.ZIP)
if os.path.exists("design.sv"):
    st.sidebar.download_button(
        label="⬇ Download Vivado Bundle (.ZIP)",
        data=build_vivado_zip(),
        file_name="siliconforge_vivado_project.zip",
        mime="application/zip",
        use_container_width=True
    )

# Online Waveform & Synthesis Fallback Link
st.sidebar.link_button(
    "🌐 Online Simulator (EDA Playground)",
    "https://www.edaplayground.com/",
    use_container_width=True
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==============================================================================
# SECTION 0: TOP NAVIGATION BAR WITH SMOOTH SCROLL ANCHORS
# ==============================================================================
st.markdown(f"""
<div id="overview" class="nav-bar">
    <div class="brand-logo">SILICON<span>FORGE</span> // RTL COPILOT</div>
    <div class="nav-menu">
        <a href="#overview">OVERVIEW</a>
        <a href="#services">SERVICES</a>
        <a href="#synthesis">SYNTHESIS ENGINE</a>
        <a href="#artifacts">RTL & TESTBENCH</a>
        <a href="#copilot" class="nav-cta">[ ARCHITECT COPILOT ]</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# SECTION 1: HERO BANNER & ARCHITECTURAL PIPELINE DIAGRAM
# ==============================================================================
col_hero_text, col_hero_svg = st.columns([2.2, 1])

with col_hero_text:
    st.markdown(f"""
    <div class="hero-box">
        <div class="hero-kicker">[ ACTIVE ENGINE: {active_engine_label} // TARGET: XCKU035 ]</div>
        <div class="hero-heading">Autonomous RTL Generation & Closed-Loop PPA Synthesis</div>
        <div class="hero-desc">
            Transform hardware specifications into verified, synthesizable SystemVerilog. 
            SILICONFORGE integrates LLM reasoning with batch EDA compilation, automated testbench generation, 
            and iterative area/timing convergence in one continuous engineering workflow.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_hero_svg:
    st.markdown("""
    <div style="background:#0b101d; border:1px solid #1e293b; border-radius:8px; padding:1.25rem; text-align:center;">
        <svg width="100%" height="190" viewBox="0 0 300 190" xmlns="http://www.w3.org/2000/svg">
            <rect x="20" y="25" width="70" height="40" rx="4" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
            <text x="55" y="49" fill="#f8fafc" font-family="monospace" font-size="11" text-anchor="middle">SPEC.MD</text>
            <line x1="90" y1="45" x2="125" y2="45" stroke="#38bdf8" stroke-width="1.5"/>
            <polygon points="125,41 133,45 125,49" fill="#38bdf8"/>
            <rect x="135" y="20" width="85" height="50" rx="4" fill="#131c31" stroke="#00f2fe" stroke-width="2"/>
            <text x="177" y="42" fill="#00f2fe" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">RTL AGENT</text>
            <text x="177" y="57" fill="#cbd5e1" font-family="monospace" font-size="9" text-anchor="middle">SystemVerilog</text>
            <line x1="177" y1="70" x2="177" y2="105" stroke="#38bdf8" stroke-width="1.5"/>
            <polygon points="173,105 177,113 181,105" fill="#38bdf8"/>
            <rect x="120" y="115" width="115" height="45" rx="4" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
            <text x="177" y="135" fill="#6ee7b7" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">EDA SYNTHESIS</text>
            <text x="177" y="150" fill="#cbd5e1" font-family="monospace" font-size="9" text-anchor="middle">Vivado / Yosys</text>
            <path d="M 120 137 L 55 137 L 55 72" fill="none" stroke="#38bdf8" stroke-width="1.2" stroke-dasharray="4,3"/>
            <polygon points="51,73 55,65 59,73" fill="#38bdf8"/>
            <text x="55" y="152" fill="#38bdf8" font-family="monospace" font-size="9" text-anchor="middle">PPA LOOP</text>
        </svg>
    </div>
    """, unsafe_allow_html=True)

# Key Platform Telemetry Strip
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown("<div class='stat-box'><div class='stat-num'>IEEE 1800</div><div class='stat-title'>SystemVerilog Standard</div></div>", unsafe_allow_html=True)
with s2:
    st.markdown(f"<div class='stat-box'><div class='stat-num'>{target_luts} LUTs</div><div class='stat-title'>Active Area Target</div></div>", unsafe_allow_html=True)
with s3:
    st.markdown("<div class='stat-box'><div class='stat-num'>DUAL-EDA</div><div class='stat-title'>Vivado + Yosys Hybrid</div></div>", unsafe_allow_html=True)
with s4:
    st.markdown("<div class='stat-box'><div class='stat-num'>AUTO-TB</div><div class='stat-title'>Self-Checking Testbench</div></div>", unsafe_allow_html=True)

# ==============================================================================
# SECTION 2: [ OUR SERVICES & PLATFORM CAPABILITIES ]
# ==============================================================================
st.markdown("<div id='services' class='section-bracket'>[ OUR SERVICES & PLATFORM CAPABILITIES ]</div>", unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown("""
    <div class="service-card">
        <div class="service-index">01 // RTL COMPILER</div>
        <div class="service-title">Autonomous SystemVerilog</div>
        <div class="service-text">Generates synthesizable, lint-clean RTL modules adhering strictly to hardware port, reset, and clocking conventions.</div>
        <a href="#synthesis" class="service-link">[ ACCESS COMPILER ↓ ]</a>
    </div>
    """, unsafe_allow_html=True)
with f2:
    st.markdown("""
    <div class="service-card">
        <div class="service-index">02 // PPA OPTIMIZATION</div>
        <div class="service-title">Closed-Loop Convergence</div>
        <div class="service-text">Parses post-synthesis utilization and timing slack reports to iteratively refactor logic until CLB LUT targets are met.</div>
        <a href="#synthesis" class="service-link">[ VIEW METRICS ↓ ]</a>
    </div>
    """, unsafe_allow_html=True)
with f3:
    st.markdown("""
    <div class="service-card">
        <div class="service-index">03 // VERIFICATION</div>
        <div class="service-title">Testbench & Simulation</div>
        <div class="service-text">Automatically constructs stimulus testbenches (<code>tb_design.sv</code>) and packages Vivado project bundles for local or online simulation.</div>
        <a href="#artifacts" class="service-link">[ INSPECT CODE ↓ ]</a>
    </div>
    """, unsafe_allow_html=True)
with f4:
    st.markdown("""
    <div class="service-card">
        <div class="service-index">04 // ARCHITECTURE AI</div>
        <div class="service-title">SoC Design Copilot</div>
        <div class="service-text">Context-aware hardware architect consultation that inspects your active RTL to advise on pipelining and DSP48 inference.</div>
        <a href="#copilot" class="service-link">[ OPEN COPILOT ↓ ]</a>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# SECTION 3: [ CLOSED-LOOP SYNTHESIS & PPA ENGINE ]
# ==============================================================================
st.markdown("<div id='synthesis' class='section-bracket'>[ 01. CLOSED-LOOP SYNTHESIS & PPA ENGINE ]</div>", unsafe_allow_html=True)

user_prompt = st.text_area(
    "Hardware Design Specification:", 
    "Design a 4-element 8-bit signed vector MAC unit named 'top_module' computing Y = sum(Ai * Wi) with active-high reset and enable.",
    height=110
)

col_btn1, col_btn2, col_btn3 = st.columns([1.3, 1.3, 1.4])
with col_btn1:
    run_clicked = st.button("EXECUTE SYNTHESIS WORKFLOW", use_container_width=True)
with col_btn2:
    if st.button("LAUNCH VIVADO IDE PROJECT", use_container_width=True):
        if eda_env["has_vivado"]:
            xpr_path = os.path.abspath("agent_project/agent_project.xpr")
            if os.path.exists(xpr_path):
                subprocess.Popen([eda_env["vivado_bin"], xpr_path])
                st.success("Opening project in AMD Vivado GUI...")
            else:
                st.error("No active .xpr project found. Execute synthesis first.")
        else:
            st.info("Running in Cloud Mode: Download the Vivado Bundle (.ZIP) on the right to open locally in Vivado.")
with col_btn3:
    if os.path.exists("design.sv"):
        st.download_button(
            label="⬇ DOWNLOAD VIVADO BUNDLE (.ZIP)",
            data=build_vivado_zip(),
            file_name="siliconforge_vivado_project.zip",
            mime="application/zip",
            use_container_width=True
        )

if run_clicked:
    if not user_api_key.strip():
        st.error("Authentication Required: Enter your Groq API Key in the left sidebar.")
    else:
        with st.spinner("Executing RTL generation and batch EDA synthesis..."):
            success = run_autonomous_loop(
                user_requirement=user_prompt,
                api_key=user_api_key.strip(),
                model_name=model_choice,
                target_luts=target_luts,
                max_iterations=max_retries
            )
        if success:
            st.success("Synthesis Completed: Design converged within target PPA constraints.")
        else:
            st.warning("Synthesis Finished: Review post-synthesis utilization and timing logs below.")

if os.path.exists("utilization.rpt"):
    st.markdown("<br>", unsafe_allow_html=True)
    luts, ffs, dsps = extract_vivado_summary("utilization.rpt")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='stat-box'><div class='stat-num'>{luts} / {target_luts}</div><div class='stat-title'>CLB LUTs Utilized</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='stat-box'><div class='stat-num'>{ffs}</div><div class='stat-title'>Flip-Flop Registers</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='stat-box'><div class='stat-num'>{dsps}</div><div class='stat-title'>DSP48 Slices</div></div>", unsafe_allow_html=True)
    with m4:
        status_txt = "CONVERGED" if int(luts) <= target_luts else "EXCEEDS BUDGET"
        st.markdown(f"<div class='stat-box'><div class='stat-num'>{status_txt}</div><div class='stat-title'>Area Constraint</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_rep1, col_rep2 = st.columns(2)
    with col_rep1:
        st.markdown("#### Resource Utilization Report (`utilization.rpt`)")
        with open("utilization.rpt", "r") as f:
            st.text_area("utilization_raw", f.read(), height=320, label_visibility="collapsed")

    with col_rep2:
        st.markdown("#### Timing Summary Report (`timing.rpt`)")
        if os.path.exists("timing.rpt"):
            with open("timing.rpt", "r") as f:
                st.text_area("timing_raw", f.read(), height=320, label_visibility="collapsed")

# ==============================================================================
# SECTION 4: [ GENERATED RTL & VERIFICATION ARTIFACTS ]
# ==============================================================================
st.markdown("<div id='artifacts' class='section-bracket'>[ 02. GENERATED RTL & VERIFICATION ARTIFACTS ]</div>", unsafe_allow_html=True)

col_rtl, col_tb = st.columns(2)
with col_rtl:
    st.markdown("#### Synthesizable RTL Module (`design.sv`)")
    if os.path.exists("design.sv"):
        with open("design.sv", "r") as f:
            st.code(f.read(), language="verilog")
    else:
        st.info("No RTL artifact generated yet. Execute synthesis in Section 01 above.")

with col_tb:
    st.markdown("#### Verification Testbench (`tb_design.sv`)")
    if os.path.exists("tb_design.sv"):
        with open("tb_design.sv", "r") as f:
            st.code(f.read(), language="verilog")
    else:
        st.info("No testbench artifact generated yet. Execute synthesis in Section 01 above.")

# ==============================================================================
# SECTION 5: [ SOC HARDWARE ARCHITECT COPILOT CONSOLE ]
# ==============================================================================
st.markdown("<div id='copilot' class='section-bracket'>[ 03. SOC HARDWARE ARCHITECT COPILOT ]</div>", unsafe_allow_html=True)

rtl_loaded = "ACTIVE (`design.sv`)" if os.path.exists("design.sv") else "STANDBY (Run Synthesis First)"
st.markdown(f"""
<div class="console-header">
    <div><strong>PRINCIPAL SOC ARCHITECT CONSOLE</strong> // CONTEXT: {rtl_loaded}</div>
    <div class="console-status">● LINKED TO {model_choice.upper()}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

qp1, qp2, qp3, qp4 = st.columns(4)
quick_query = None
with qp1:
    if st.button("⚡ Analyze Critical Path", use_container_width=True):
        quick_query = "Analyze the critical combinational path in design.sv and suggest how to pipeline it for higher Fmax."
with qp2:
    if st.button("📐 Optimize LUT / DSP48 Area", use_container_width=True):
        quick_query = "How can I reduce CLB LUT usage or infer Xilinx DSP48E2 slices for the multipliers in design.sv?"
with qp3:
    if st.button("🛡️ Audit Reset & Clocking", use_container_width=True):
        quick_query = "Review the reset polarity, bit-widths, and signed arithmetic overflow safety in design.sv."
with qp4:
    if st.button("🗑️ Clear Console History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

with st.form("architect_console_form", clear_on_submit=True):
    col_in, col_sub = st.columns([4.5, 1])
    with col_in:
        typed_query = st.text_input(
            "Architect Query",
            placeholder="Enter architectural question (e.g., How many pipeline stages are needed to hit 300 MHz on Kintex UltraScale?)...",
            label_visibility="collapsed"
        )
    with col_sub:
        submitted = st.form_submit_button("TRANSMIT →", use_container_width=True)

active_query = quick_query if quick_query else (typed_query.strip() if submitted and typed_query.strip() else None)

if active_query:
    if not user_api_key.strip():
        st.error("Groq API Key required in the left sidebar.")
    else:
        with st.spinner("Principal Architect analyzing RTL & PPA telemetry..."):
            ask_architect_copilot(active_query, user_api_key.strip(), model_choice)

if st.session_state.chat_history:
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-msg-user">
                <div class="chat-role-tag" style="color:#38bdf8 !important;">[ ENGINEER QUERY ]</div>
                <div>{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="chat-msg-ai">
                <div class="chat-role-tag" style="color:#6ee7b7 !important;">[ PRINCIPAL SOC ARCHITECT RESPONSE ]</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(msg["content"])
else:
    st.markdown("""
    <div style="background:#0b101d; border:1px dashed #334155; border-radius:6px; padding:1.2rem; text-align:center; font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#cbd5e1 !important;">
        CONSOLE READY — Select a diagnostic preset above or transmit an architectural query below.
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown(f"""
<div class="site-footer">
    SILICONFORGE // AUTONOMOUS RTL &amp; EDA PLATFORM &nbsp;•&nbsp; ENGINE: {active_engine_label} &nbsp;•&nbsp; IEEE 1800 SYSTEMVERILOG
</div>
""", unsafe_allow_html=True)

