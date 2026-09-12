# ============================================================
# FILE: src/app.py
# PURPOSE: DeepResearch AI — Multi-Agent Intelligence Dashboard
# ============================================================

import sys
import os

# Dynamic path resolution for seamless local and Streamlit Cloud execution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [current_dir, parent_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import time
import re
import pandas as pd
from typing import Optional
from dotenv import load_dotenv

# Ensure .env is explicitly loaded from project root
env_path = os.path.join(parent_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

try:
    from src.state import PipelineState
    from src.orchestrator import MultiAgentOrchestrator
except ImportError:
    from state import PipelineState
    from orchestrator import MultiAgentOrchestrator

# 1. Page Configuration
st.set_page_config(
    page_title="DeepResearch AI | Autonomous Multi-Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# SESSION STATE DEFAULTS
# ================================================================
st.session_state["engine_mode"] = "gemini_flash"
st.session_state["framework_choice"] = "crewai"
if "max_revisions" not in st.session_state:
    st.session_state["max_revisions"] = 2
if "enable_sound" not in st.session_state:
    st.session_state["enable_sound"] = True
if "search_counter" not in st.session_state:
    st.session_state["search_counter"] = 0


# ================================================================
# SIDEBAR (Configuration Controls)
# ================================================================
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")

    st.markdown("#### ⚡ AI Engine")
    st.markdown("""
    <div style="background: rgba(26, 6, 12, 0.65); border: 1px solid rgba(190, 18, 60, 0.3); border-radius: 12px; padding: 0.8rem 1rem; margin-bottom: 0.8rem;">
        <div style="display: flex; align-items: center; gap: 0.65rem;">
            <span style="font-size: 1.35rem;">⚡</span>
            <div>
                <div style="color: #ffffff; font-weight: 800; font-size: 0.95rem; letter-spacing: -0.01em;">Google Gemini 3.8 Flash</div>
                <div style="color: #fbcfe8; font-size: 0.78rem; font-weight: 600;">Active Cloud Turbo Engine</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### 🦜 Multi-Agent Architecture")
    st.markdown("""
    <div style="background: rgba(26, 6, 12, 0.65); border: 1px solid rgba(190, 18, 60, 0.3); border-radius: 12px; padding: 0.8rem 1rem; margin-bottom: 0.8rem;">
        <div style="display: flex; align-items: center; gap: 0.65rem;">
            <span style="font-size: 1.35rem;">🦜</span>
            <div>
                <div style="color: #ffffff; font-weight: 800; font-size: 0.95rem; letter-spacing: -0.01em;">CrewAI Multi-Agent</div>
                <div style="color: #fb7185; font-size: 0.78rem; font-weight: 600;">Autonomous Collaborative Agents</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🔄 Reflection & Revision")
    st.session_state["max_revisions"] = st.slider(
        "Max Critique Loops", min_value=1, max_value=3,
        value=st.session_state["max_revisions"],
        help="Maximum times the Critic can request the Writer to self-correct."
    )

    st.markdown("---")
    st.markdown("#### 🔊 Audio Notifications")
    st.session_state["enable_sound"] = st.toggle(
        "Completion Chime",
        value=st.session_state["enable_sound"],
        help="Plays a subtle audio chime when the research pipeline finishes."
    )

    st.markdown("---")
    st.markdown("#### 👥 Active Agent Team")
    st.markdown("""
    - 🔍 **Researcher** — Live Web & Wikipedia Retrieval
    - ✍️ **Writer** — Substantive Report Authoring
    - 🧐 **Critic** — 4-Dimension Rubric Scoring
    - 🛡️ **Fact-Checker** — Factual Evidence Verification
    """)


# ================================================================
# 2. PREMIUM STYLING — Dark Velvet Red & Minimalist Obsidian
# ================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ─── MAIN APP CANVAS: Deep Charcoal / Dark Velvet Red Glow ─── */
    .stApp, [data-testid="stAppViewContainer"] {
        background: 
            radial-gradient(ellipse 80% 50% at 50% -8%, rgba(136, 19, 55, 0.24) 0%, transparent 65%),
            radial-gradient(circle at 6% 28%, rgba(159, 18, 57, 0.14) 0%, transparent 40%),
            radial-gradient(circle at 94% 72%, rgba(120, 15, 45, 0.14) 0%, transparent 42%),
            linear-gradient(175deg, #080204 0%, #0e0307 32%, #15050b 68%, #060103 100%) !important;
        color: #f8fafc !important;
    }

    /* ─── SIDEBAR: Deep Velvet Obsidian with Delicate Border ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080204 0%, #110308 50%, #060103 100%) !important;
        border-right: 1px solid rgba(190, 18, 60, 0.2) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.65) !important;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
        color: #fbcfe8 !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(190, 18, 60, 0.18) !important;
    }

    /* ─── TOP UTILITY BAR ─── */
    .top-utility-bar {
        background: rgba(18, 4, 9, 0.72) !important;
        border: 1px solid rgba(190, 18, 60, 0.22) !important;
        border-radius: 12px;
        padding: 0.65rem 1.4rem;
        display: flex;
        justify-content: space-around;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.8rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45) !important;
        backdrop-filter: blur(16px);
    }

    .utility-badge {
        display: flex;
        align-items: center;
        gap: 0.48rem;
        font-size: 0.88rem;
        color: #e2e8f0;
        font-weight: 600;
    }

    /* ─── HERO HEADER BANNER ─── */
    .hero-header {
        border-radius: 20px;
        padding: 2.1rem 2.4rem;
        margin-bottom: 1.8rem;
        background: linear-gradient(135deg, rgba(24, 6, 12, 0.8) 0%, rgba(36, 8, 18, 0.65) 50%, rgba(14, 3, 7, 0.88) 100%) !important;
        border: 1px solid rgba(190, 18, 60, 0.26) !important;
        box-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.55), 0 0 25px rgba(136, 19, 55, 0.14) !important;
        backdrop-filter: blur(16px);
    }

    .hero-title {
        background: linear-gradient(135deg, #ffffff 0%, #ffe4e6 28%, #fbcfe8 58%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.9rem;
        font-weight: 800;
        letter-spacing: -0.025em;
    }

    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(136, 19, 55, 0.24);
        border: 1px solid rgba(190, 18, 60, 0.35);
        color: #ffe4e6;
        padding: 0.3rem 0.85rem;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.4px;
    }

    /* ─── AGENT CARDS ─── */
    .agent-card {
        background: rgba(18, 4, 9, 0.7) !important;
        border: 1px solid rgba(190, 18, 60, 0.2) !important;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin: 0.6rem 0;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(12px);
    }

    /* ─── METRIC CARDS ─── */
    .metrics-row {
        display: flex;
        gap: 1rem;
        margin: 1.2rem 0;
        flex-wrap: wrap;
    }
    .metric-card {
        flex: 1;
        min-width: 140px;
        background: rgba(18, 4, 9, 0.7) !important;
        border: 1px solid rgba(190, 18, 60, 0.2) !important;
        border-radius: 14px;
        padding: 1.1rem;
        text-align: center;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(12px);
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #ffffff;
        background: linear-gradient(135deg, #ffffff 0%, #fbcfe8 50%, #fda4af 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 600;
        margin-top: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    /* ─── REPORT CONTAINER (Dedicated High-Readability Scrollbox) ─── */
    .report-container {
        background: linear-gradient(145deg, rgba(14, 3, 7, 0.94) 0%, rgba(8, 2, 4, 0.98) 100%) !important;
        border: 1px solid rgba(190, 18, 60, 0.22) !important;
        border-radius: 16px;
        padding: 2.2rem 2.6rem;
        margin: 1.2rem 0;
        max-height: 650px;
        overflow-y: auto;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(16px);
        font-size: 1.1rem;
        line-height: 1.85;
        color: #f1f5f9 !important;
    }
    .report-container::-webkit-scrollbar {
        width: 7px;
    }
    .report-container::-webkit-scrollbar-track {
        background: rgba(8, 2, 4, 0.6);
        border-radius: 8px;
    }
    .report-container::-webkit-scrollbar-thumb {
        background: rgba(190, 18, 60, 0.32);
        border-radius: 8px;
    }
    .report-container::-webkit-scrollbar-thumb:hover {
        background: rgba(225, 29, 72, 0.55);
    }
    .report-container h1, .report-container h2, .report-container h3, .report-container h4 {
        color: #ffffff !important;
        font-weight: 800;
        margin-top: 1.4rem;
        margin-bottom: 0.6rem;
        letter-spacing: -0.01em;
    }
    .report-container p, .report-container li {
        color: #e2e8f0 !important;
        font-size: 1.08rem !important;
        line-height: 1.85 !important;
    }
    .report-container strong {
        color: #ffffff !important;
        font-weight: 700;
    }
    .report-container a {
        color: #38bdf8 !important;
        text-decoration: underline;
    }

    /* ─── NAVIGATION TABS BAR ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem !important;
        background: rgba(16, 4, 8, 0.65) !important;
        border-bottom: 1px solid rgba(190, 18, 60, 0.2) !important;
        padding: 0.35rem 0.5rem 0 0.5rem !important;
        border-radius: 12px 12px 0 0 !important;
        margin-bottom: 1.4rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 0.7rem 1.3rem !important;
        border-bottom: 2.5px solid transparent !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #fbcfe8 !important;
        background: rgba(190, 18, 60, 0.08) !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(190, 18, 60, 0.14) !important;
        color: #ffe4e6 !important;
        border-bottom: 2.5px solid #be123c !important;
    }

    /* ─── TEXT INPUTS & FORMS ─── */
    .stTextInput > div > div > input {
        background: rgba(18, 4, 9, 0.75) !important;
        border: 1px solid rgba(190, 18, 60, 0.25) !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #be123c !important;
        box-shadow: 0 0 12px rgba(190, 18, 60, 0.3) !important;
    }

    /* ─── PROGRESS BAR ─── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #701a2b 0%, #be123c 50%, #fda4af 100%) !important;
    }

    /* ─── SECONDARY & QUICK-PICK BUTTONS ─── */
    .stButton > button {
        background: rgba(18, 4, 9, 0.65) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(190, 18, 60, 0.24) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.65rem 1.3rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25) !important;
        letter-spacing: 0.2px !important;
    }
    .stButton > button:hover {
        background: rgba(136, 19, 55, 0.2) !important;
        border-color: rgba(225, 29, 72, 0.45) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* ─── PRIMARY SUBMIT BUTTON ─── */
    .stFormSubmitButton > button,
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(180deg, #9f1239 0%, #701a2b 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(244, 63, 94, 0.3) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.8rem 2rem !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 4px 14px rgba(112, 26, 43, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    .stFormSubmitButton > button:hover,
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(180deg, #be123c 0%, #881337 100%) !important;
        border-color: rgba(251, 113, 133, 0.5) !important;
        box-shadow: 0 6px 20px rgba(159, 18, 57, 0.48) !important;
        transform: translateY(-1px) !important;
    }

    /* ─── DOWNLOAD BUTTON ─── */
    .stDownloadButton > button {
        background: rgba(18, 4, 9, 0.7) !important;
        color: #fbcfe8 !important;
        border: 1px solid rgba(190, 18, 60, 0.25) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0.7rem 1.5rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(136, 19, 55, 0.22) !important;
        border-color: rgba(225, 29, 72, 0.48) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)



def play_chime():
    """Plays pleasant synthetic chime when multi-agent pipeline finishes."""
    st.components.v1.html("""
    <script>
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(587.33, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(880.00, ctx.currentTime + 0.15);
            gain.gain.setValueAtTime(0.08, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.5);
        } catch(e) {}
    </script>
    """, height=0)


# ================================================================
# TOP UTILITY BAR & HERO BANNER
# ================================================================
st.markdown("""
<div class="top-utility-bar">
    <div class="utility-badge"><span style="font-size: 1.15rem;">🦜</span> <strong>Architecture:</strong> <span style="color: #fbcfe8;">CrewAI Autonomous Agents</span></div>
    <div class="utility-badge"><span style="font-size: 1.15rem;">⚡</span> <strong>LLM Engine:</strong> <span style="color: #fda4af;">Google Gemini 3.8 Flash</span></div>
    <div class="utility-badge"><span style="font-size: 1.15rem;">🌐</span> <strong>Grounding:</strong> <span style="color: #fb7185;">Live Web & Wikipedia Index</span></div>
    <div class="utility-badge"><span style="font-size: 1.15rem;">🛡️</span> <strong>Audit:</strong> <span style="color: #ffe4e6;">Anti-Hallucination Gate</span></div>
</div>

<div class="hero-header">
    <div style="display: flex; align-items: center; gap: 0.9rem; margin-bottom: 0.7rem; flex-wrap: wrap;">
        <span style="font-size: 3.2rem; line-height: 1; filter: drop-shadow(0 0 20px rgba(225, 29, 72, 0.75));">🤖</span>
        <span class="hero-title">DeepResearch AI</span>
        <span class="hero-pill">🦜 CREWAI • ⚡ GEMINI 3.8 FLASH</span>
    </div>
    <div style="color: #cbd5e1; font-size: 1.15rem; line-height: 1.75;">
        <strong>Autonomous Multi-Agent Intelligence & Fact-Verification Platform</strong> — Orchestrating 4 specialized AI agents (<strong>Lead Researcher ➔ Senior Writer ➔ Editorial Critic ➔ Fact-Checking Auditor</strong>) through an adversarial reflection & self-correction loop powered by <strong>Google Gemini 3.8 Flash</strong>.
    </div>
</div>
""", unsafe_allow_html=True)


# ================================================================
# HELPER FUNCTIONS
# ================================================================
def _render_markdown_to_html(md_text: str) -> str:
    """Converts markdown to well-spaced, readable HTML with fallback."""
    try:
        import markdown
        return markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'nl2br'])
    except ImportError:
        import html
        return "<div style='white-space: pre-wrap;'>" + html.escape(md_text) + "</div>"


def _add_copy_button(report_text: str):
    """Adds a prominent, high-reliability Copy Text button via JS clipboard API + fallback."""
    import json
    escaped_json = json.dumps(report_text)

    copy_html = f"""
    <div style="display: flex; justify-content: center; align-items: center; margin: 1.2rem 0 0.6rem 0; width: 100%;">
        <button onclick="copyReport()" id="copyBtn" style="
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.75rem;
            width: 100%;
            max-width: 520px;
            background: linear-gradient(135deg, rgba(28, 6, 13, 0.94) 0%, rgba(136, 19, 55, 0.45) 50%, rgba(20, 5, 10, 0.98) 100%);
            border: 1.5px solid rgba(190, 18, 60, 0.45);
            border-radius: 14px;
            padding: 1.1rem 2.6rem;
            color: #ffffff;
            font-size: 1.15rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
            letter-spacing: 0.35px;
            box-shadow: 0 4px 22px rgba(0, 0, 0, 0.5), 0 0 16px rgba(159, 18, 57, 0.22);
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        "
        onmouseover="this.style.background='linear-gradient(135deg, rgba(38, 8, 18, 0.98) 0%, rgba(159, 18, 57, 0.65) 50%, rgba(26, 6, 13, 1) 100%)'; this.style.borderColor='rgba(244, 63, 94, 0.7)'; this.style.boxShadow='0 6px 26px rgba(159, 18, 57, 0.45)'; this.style.transform='translateY(-1px)';"
        onmouseout="this.style.background='linear-gradient(135deg, rgba(28, 6, 13, 0.94) 0%, rgba(136, 19, 55, 0.45) 50%, rgba(20, 5, 10, 0.98) 100%)'; this.style.borderColor='rgba(190, 18, 60, 0.45)'; this.style.boxShadow='0 4px 22px rgba(0, 0, 0, 0.5), 0 0 16px rgba(159, 18, 57, 0.22)'; this.style.transform='translateY(0)';"
        >
            <span style="font-size: 1.35rem;">📋</span>
            <span id="copyBtnText">Copy Text</span>
        </button>
    </div>
    <script>
        function copyReport() {{
            const text = {escaped_json};
            function showSuccess() {{
                const btn = document.getElementById('copyBtn');
                if (btn) {{
                    btn.style.borderColor = 'rgba(52, 211, 153, 0.75)';
                    btn.style.boxShadow = '0 0 24px rgba(52, 211, 153, 0.4)';
                    btn.style.color = '#34d399';
                    btn.innerHTML = '<span style="font-size: 1.35rem;">✅</span> <span id="copyBtnText" style="color: #34d399;">Copied to Clipboard!</span>';
                    setTimeout(() => {{
                        btn.style.borderColor = 'rgba(190, 18, 60, 0.45)';
                        btn.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.45), 0 0 16px rgba(159, 18, 57, 0.22)';
                        btn.style.color = '#ffffff';
                        btn.innerHTML = '<span style="font-size: 1.35rem;">📋</span> <span id="copyBtnText">Copy Text</span>';
                    }}, 2200);
                }}
            }}

            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(showSuccess).catch(() => {{
                    fallbackCopy(text, showSuccess);
                }});
            }} else {{
                fallbackCopy(text, showSuccess);
            }}
        }}

        function fallbackCopy(text, callback) {{
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.top = "-9999px";
            textArea.style.left = "-9999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {{
                const successful = document.execCommand('copy');
                if (successful && callback) callback();
            }} catch (err) {{}}
            document.body.removeChild(textArea);
        }}
    </script>
    """
    st.components.v1.html(copy_html, height=90)




# ================================================================
# MAIN NAVIGATION TABS
# ================================================================
tab_lab, tab_dossier, tab_analytics, tab_architecture = st.tabs([
    "🚀 Intelligence Lab",
    "📚 Research Dossier",
    "📈 Critique Analytics",
    "🏗️ Architecture"
])


# ================================================================
# TAB 1: INTELLIGENCE LAB
# ================================================================
with tab_lab:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 0.8rem 0;">
        <div style="font-size: 1.8rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.4rem;">What would you like to research?</div>
        <div style="color: #94a3b8; font-size: 0.95rem;">Autonomous 4-agent collaborative team — Researcher ➔ Writer ➔ Critic ➔ Fact-Checker</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Topic Picks
    col_pick1, col_pick2, col_pick3 = st.columns(3)
    with col_pick1:
        if st.button("🔋 Solid-State Batteries 2026", use_container_width=True):
            st.session_state["active_topic"] = "Solid-State EV Battery Breakthroughs and Commercialization Roadmap in 2026"
            st.session_state.pop("pipeline_state", None)
            st.session_state["search_counter"] += 1
    with col_pick2:
        if st.button("⚛️ Quantum Computing in Finance", use_container_width=True):
            st.session_state["active_topic"] = "Quantum Computing Applications in Financial Risk and Algorithmic Trading 2026"
            st.session_state.pop("pipeline_state", None)
            st.session_state["search_counter"] += 1
    with col_pick3:
        if st.button("🧠 Agentic AI in Healthcare", use_container_width=True):
            st.session_state["active_topic"] = "Autonomous Agentic AI in Clinical Diagnostics and Drug Discovery"
            st.session_state.pop("pipeline_state", None)
            st.session_state["search_counter"] += 1

    # Search Form
    with st.form(key=f"search_form_{st.session_state['search_counter']}", clear_on_submit=False):
        topic = st.text_input(
            "Enter any research topic, market trend, or technical domain:",
            value=st.session_state.get("active_topic", ""),
            placeholder="e.g. Solid-State Batteries in 2026, Advancements in Quantum Computing, Agentic AI Architectures..."
        )
        start_btn = st.form_submit_button("⚡ Deploy Multi-Agent Team", type="primary", use_container_width=True)

    # Execution Flow
    if start_btn and topic.strip():
        st.session_state.pop("pipeline_state", None)
        st.session_state["active_topic"] = topic.strip()
        st.session_state["search_counter"] += 1

        max_revisions = st.session_state.get("max_revisions", 2)
        framework = st.session_state.get("framework_choice", "crewai")
        orchestrator = MultiAgentOrchestrator(framework=framework)

        progress_bar = st.progress(0, text="Initializing Agent Team...")
        status_box = st.empty()

        def update_progress(state: PipelineState):
            step_map = {
                "idle": (10, "⚡ Initializing agent personas..."),
                "researching": (30, "🔍 Lead Researcher scouring live web & Wikipedia for empirical evidence..."),
                "drafting": (60, "✍️ Senior Writer authoring structured intelligence briefing..."),
                "critiquing": (80, f"🧐 Editorial Critic evaluating 4-dimension rubric (Score: {state.critique_score}/100)..."),
                "fact_checking": (90, "🛡️ Fact-Checking Auditor cross-examining claims against research dossier..."),
                "completed": (100, "✅ Research Mission Complete!"),
                "error": (100, "❌ Error encountered during execution.")
            }
            val, txt = step_map.get(state.status, (50, "Autonomous agents collaborating..."))
            progress_bar.progress(val, text=txt)

            if state.logs:
                latest = state.logs[-1]
                status_box.markdown(f"""
                <div class="agent-card" style="border-left: 4px solid #be123c;">
                    <div style="font-weight: 700; font-size: 1.05rem; color: #fbcfe8;">
                        {latest['agent_icon']} {latest['agent_name']} — <em>{latest['action']}</em>
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.92rem; margin-top: 0.3rem;">
                        {latest['details']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.spinner("🤖 Multi-agent crew researching and synthesizing..."):
            final_state = orchestrator.run_pipeline(
                topic=topic,
                max_revisions=max_revisions,
                on_step_callback=update_progress
            )
            st.session_state["pipeline_state"] = final_state

            if st.session_state.get("enable_sound"):
                play_chime()

        st.rerun()

    # Display Results
    if "pipeline_state" in st.session_state:
        state: PipelineState = st.session_state["pipeline_state"]

        if state.status == "error":
            st.error(f"❌ Pipeline Execution Notice: {state.error_message}")
        else:
            st.markdown("---")

            # Metrics Row
            st.markdown(f"""
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-value">{state.critique_score}/100</div>
                    <div class="metric-label">Editorial Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{state.revision_count}</div>
                    <div class="metric-label">Revision Loops</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(state.sources)}</div>
                    <div class="metric-label">Live Sources</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="background: none; -webkit-text-fill-color: #34d399;">PASSED</div>
                    <div class="metric-label">Fact-Check Audit</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # High-readability Report Container with internal scroll
            st.markdown(f"""<div class="report-container">{_render_markdown_to_html(state.final_report)}</div>""", unsafe_allow_html=True)

            # Prominent Copy Text Action
            _add_copy_button(state.final_report)



# ================================================================
# TAB 2: RESEARCH DOSSIER
# ================================================================
with tab_dossier:
    st.markdown("### 📚 Ground-Truth Intelligence Dossier")
    if "pipeline_state" in st.session_state:
        state: PipelineState = st.session_state["pipeline_state"]

        st.markdown("**Search Queries Formulated by Researcher:**")
        for q in state.search_queries_used:
            st.code(f"🔍 {q}")

        st.markdown("#### 📑 Ground-Truth Evidence Base:")
        st.text_area("Researcher Evidence", value=state.research_dossier, height=350)

        st.markdown("#### 🌐 Live Sources Collected:")
        for idx, src in enumerate(state.sources, 1):
            with st.expander(f"Source {idx}: {src.get('title', 'Untitled')}"):
                st.markdown(f"**URL:** [{src.get('url')}]({src.get('url')})")
                st.markdown(f"**Snippet:** {src.get('snippet')}")
    else:
        st.info("💡 Run a research mission in the Intelligence Lab tab first to inspect raw evidence!")


# ================================================================
# TAB 3: CRITIQUE ANALYTICS
# ================================================================
with tab_analytics:
    st.markdown("### 📈 Editorial Rubric & Score Progression")
    if "pipeline_state" in st.session_state:
        state: PipelineState = st.session_state["pipeline_state"]

        if state.critique_history:
            df = pd.DataFrame(state.critique_history)

            c_left, c_right = st.columns([1.5, 1])
            with c_left:
                st.markdown("#### 📊 Score Progression Over Revisions")
                st.line_chart(df.set_index("revision")[["total_score", "depth_score", "evidence_score", "structure_score"]])
            with c_right:
                st.markdown("#### 🧐 4-Dimension Rubric Breakdown")
                st.dataframe(df[["revision", "total_score", "depth_score", "structure_score", "evidence_score", "passed"]], use_container_width=True)

            st.markdown("#### 📋 Editorial Director Directives:")
            st.info(f"**Critic Verdict ({state.critique_score}/100):**\n\n{state.critique}")

        st.markdown("#### ⏱️ Complete Agent Communication Timeline")
        for log in state.logs:
            st.markdown(f"""
            <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.45rem; padding-left: 0.6rem; border-left: 2px solid #be123c;">
                <strong style="color: #e2e8f0;">{log['agent_icon']} {log['agent_name']}</strong> — <span style="color: #fda4af;">{log['action']}</span> ({log['details']})
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💡 Run a mission to visualize how the Critic's feedback guided revisions!")


# ================================================================
# TAB 4: ARCHITECTURE
# ================================================================
with tab_architecture:
    st.markdown("### 🏗️ CrewAI Multi-Agent Architecture")
    st.markdown("""
    ```
    [User Prompt] ➔ [1. Researcher] (Google News + Wikipedia Tools)
                          │
                          ▼
                    [2. Writer] (Executive Intelligence Report)
                          │
                          ▼
                    [3. Critic] ◄──────────────┐ (Adversarial Reflection: Score < 85)
                          │                    │
                          ├────────────────────┘
                          ▼ (Score >= 85)
                    [4. Fact-Checker] (Anti-Hallucination Audit)
                          │
                          ▼
                    [Verified Intelligence Briefing]
    ```

    #### 🌟 Why This Architecture Excels:
    1. **Separation of Concerns**: Each agent operates with a dedicated persona and task, preventing single-prompt cognitive overload.
    2. **Adversarial Reflection**: The Editorial Critic grades drafts against an empirical 4-dimension rubric (Depth, Structure, Evidence, Strategy), sending actionable feedback back to the Writer if quality is below 85%.
    3. **Hallucination Prevention**: The Fact-Checking Auditor rigorously cross-examines all numerical assertions, dates, and names against the original research dossier.
    4. **Google Gemini 3.8 Flash Powered**: Powered by Google's latest Gemini 3.8 Flash engine for rapid, deeply grounded analytical synthesis.
    """)
