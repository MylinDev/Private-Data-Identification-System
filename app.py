import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import warnings

warnings.filterwarnings('ignore')

# Adiciona raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from components.pii_detector import PIIDetector
from components.utils.masker import ENTITY_CONFIG

# ========================== CONFIGURAÇÃO DA PÁGINA ==========================

st.set_page_config(
    page_title="PII Shield · Detector de Dados Pessoais",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================== CSS GLOBAL ==========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ─── RESET & BASE ────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* ─── FUNDO: near-black absoluto + dot-grid ─────────────── */
.stApp {
    background-color: #060810;
    color: #bcc8d8;
    min-height: 100vh;
}
/* dot-grid — pontos minúsculos estilo AuthKit/WorkOS */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: radial-gradient(circle, rgba(148,163,184,0.07) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
    z-index: 0;
    mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
    -webkit-mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
}
/* Orb de luz central — blue-tinted AuthKit style */
.stApp::after {
    content: '';
    position: fixed;
    top: -30vh;
    left: 50%;
    transform: translateX(-50%);
    width: 65vw;
    height: 55vh;
    background: radial-gradient(ellipse at 50% 0%,
        rgba(152,192,239,0.07) 0%,
        rgba(99,120,230,0.035) 55%,
        transparent 72%);
    pointer-events: none;
    z-index: 0;
    animation: orb-pulse 8s ease-in-out infinite;
}
@keyframes orb-pulse {
    0%, 100% { opacity: 1; transform: translateX(-50%) scale(1); }
    50%       { opacity: 0.75; transform: translateX(-50%) scale(1.06); }
}
.block-container { position: relative; z-index: 1; padding-top: 2rem !important; max-width: 1100px !important; }

/* ─── SIDEBAR ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(4,5,12,0.97) !important;
    border-right: 1px solid rgba(255,255,255,0.04) !important;
}
[data-testid="stSidebar"] * { color: #b0bac8 !important; }
[data-testid="stSidebar"] .sidebar-badge { color: #ffffff !important; }
[data-testid="stSidebar"] .stSlider > div > div > div > div {
    background: linear-gradient(90deg, #3656d2, #7c3aed) !important;
}

/* ─── TABS ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 4px;
    gap: 3px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: rgba(255,255,255,0.2);
    border-radius: 9px;
    font-weight: 500;
    font-size: 0.88rem;
    padding: 8px 20px;
    border: none !important;
    letter-spacing: 0.02em;
    transition: all 0.2s;
}
.stTabs [data-baseweb="tab"]:hover { color: rgba(255,255,255,0.5); }
.stTabs [aria-selected="true"] {
    background: rgba(255,255,255,0.07) !important;
    color: rgba(255,255,255,0.9) !important;
    box-shadow: none !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 2rem; }

/* ─── BOTÕES ──────────────────────────────────────────────── */
.stButton > button {
    background: rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.9);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    font-weight: 500;
    font-size: 0.88rem;
    letter-spacing: 0.02em;
    padding: 0.6rem 1.6rem;
    transition: all 0.2s;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
}
.stButton > button:hover {
    background: rgba(255,255,255,0.12);
    border-color: rgba(255,255,255,0.18);
    transform: translateY(-1px);
}
/* Botão primário — glowing-button style AuthKit */
.stButton > button[kind="primary"] {
    background: rgba(99,120,230,0.18) !important;
    border-color: rgba(152,192,239,0.32) !important;
    color: #D8ECF8 !important;
    box-shadow: 0 0 20px rgba(99,120,230,0.18), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    transition: all 0.25s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: rgba(99,120,230,0.3) !important;
    border-color: rgba(152,192,239,0.55) !important;
    box-shadow: 0 0 36px rgba(99,120,230,0.32), inset 0 1px 0 rgba(255,255,255,0.12) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    color: rgba(255,255,255,0.4) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(255,255,255,0.1) !important;
}

/* ─── INPUTS ──────────────────────────────────────────────── */
.stTextArea textarea {
    background: rgba(255,255,255,0.03) !important;
    color: #c8cdd8 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
    backdrop-filter: blur(4px);
}
.stTextArea textarea:focus {
    border-color: rgba(54,86,210,0.6) !important;
    box-shadow: 0 0 0 3px rgba(54,86,210,0.12) !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #c8cdd8 !important;
}

/* ─── FILE UPLOADER ────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02);
    border: 2px dashed rgba(54,86,210,0.25);
    border-radius: 18px;
    transition: border-color 0.2s, background 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(54,86,210,0.55);
    background: rgba(54,86,210,0.04);
}

/* ─── EXPANDER ────────────────────────────────────────────── */
details {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    margin-bottom: 8px !important;
    backdrop-filter: blur(8px);
    transition: border-color 0.2s;
}
details summary {
    color: #c8cdd8 !important;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 0.85rem 1.2rem;
}
details[open] { border-color: rgba(54,86,210,0.35) !important; }

/* ─── PROGRESS ────────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #3656d2, #7c3aed, #c026d3) !important;
}

/* ─── SCROLLBAR ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }

/* ════════ COMPONENTES CUSTOM ════════════════════════════════ */

/* ── HERO — AuthKit editorial ────────────────────────────── */
.hero-wrapper {
    text-align: center;
    padding: 4rem 1rem 2.5rem;
    position: relative;
    /* grid de linhas cruzadas estilo AuthKit hero__lines */
    background-image:
        repeating-linear-gradient(0deg,   transparent, transparent calc(100%/5 - 0.5px), rgba(255,255,255,0.028) calc(100%/5 - 0.5px), rgba(255,255,255,0.028) calc(100%/5)),
        repeating-linear-gradient(90deg,  transparent, transparent calc(100%/7 - 0.5px), rgba(255,255,255,0.022) calc(100%/7 - 0.5px), rgba(255,255,255,0.022) calc(100%/7));
}
/* corner × markers nos 4 cantos — idêntico ao AuthKit */
.hero-wrapper::before {
    content: '×';
    white-space: pre;
    position: absolute;
    top: 1.5rem; left: 2rem;
    font-size: 1rem;
    font-weight: 300;
    color: rgba(255,255,255,0.1);
    line-height: 1.6;
}
.hero-wrapper::after {
    content: '×';
    white-space: pre;
    position: absolute;
    top: 1.5rem; right: 2rem;
    font-size: 1rem;
    font-weight: 300;
    color: rgba(255,255,255,0.1);
    line-height: 1.6;
    text-align: right;
}
.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 500;
    color: rgba(152,192,239,0.62);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
}
.hero-eyebrow::before, .hero-eyebrow::after {
    content: '';
    display: inline-block;
    width: 40px;
    height: 1px;
    background: rgba(152,192,239,0.18);
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(152,192,239,0.06);
    border: 1px solid rgba(152,192,239,0.2);
    color: rgba(152,192,239,0.82);
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 999px;
    margin-bottom: 1.8rem;
}
.hero-title {
    font-size: clamp(3.5rem, 8vw, 5.5rem);
    font-weight: 900;
    letter-spacing: -0.05em;
    line-height: 0.95;
    color: #ffffff;
    background: linear-gradient(185deg,
        #ffffff 0%,
        #D8ECF8 42%,
        #98C0EF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1.5rem;
}
.hero-sub {
    color: rgba(186,214,247,0.4);
    font-size: 0.95rem;
    font-weight: 400;
    max-width: 500px;
    margin: 0 auto 0.5rem;
    line-height: 1.8;
}
.hero-glow-line {
    display: none;
}

/* ── GLASS CARDS (stat) — estilo AuthKit, quase invisíveis ── */
.stat-card {
    background: rgba(255,255,255,0.018);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 2rem 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, background 0.3s;
}
/* luz interna sutil no topo */
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 15%; right: 15%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
}
/* marcador de canto superior-esquerdo — signature AuthKit */
.stat-card::after {
    content: '×';
    position: absolute;
    top: 8px; right: 12px;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.08);
    font-weight: 300;
    line-height: 1;
}
.stat-card:hover {
    background: rgba(255,255,255,0.028);
    border-color: rgba(255,255,255,0.1);
    box-shadow: 0 0 28px rgba(99,120,230,0.06);
}
.stat-card.privado:hover  { border-color: rgba(239,68,68,0.18); }
.stat-card.publico:hover  { border-color: rgba(34,197,94,0.18); }
.stat-card.neutro:hover   { border-color: rgba(99,120,230,0.25); }
.stat-card.score-alto:hover { border-color: rgba(192,38,211,0.18); }

.stat-card-value {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 0.5rem;
}
.stat-card-value.privado  { color: #fca5a5; }
.stat-card-value.publico  { color: #86efac; }
.stat-card-value.neutro   { color: #a5b4fc; }
.stat-card-value.score-alto { color: #f0abfc; }
.stat-card-label {
    color: rgba(255,255,255,0.2);
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

/* ── CLASSIFICATION BANNER — AuthKit style ──────────────── */
.classification-banner {
    border-radius: 18px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
}
/* corner markers — signature AuthKit */
.classification-banner::before {
    content: '×';
    position: absolute;
    top: 12px; left: 16px;
    font-size: 0.85rem;
    font-weight: 300;
    opacity: 0.25;
}
.classification-banner::after {
    content: '×';
    position: absolute;
    top: 12px; right: 16px;
    font-size: 0.85rem;
    font-weight: 300;
    opacity: 0.25;
}
.classification-banner.privado {
    background: rgba(239,68,68,0.04);
    border: 1px solid rgba(239,68,68,0.12);
    color: #fca5a5;
}
.classification-banner.publico {
    background: rgba(34,197,94,0.04);
    border: 1px solid rgba(34,197,94,0.12);
    color: #86efac;
}
.classification-banner h2 {
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    margin: 0 0 0.5rem;
    line-height: 1;
}
.classification-banner.privado h2 { color: #fca5a5; }
.classification-banner.publico h2 { color: #86efac; }
.classification-banner p { color: rgba(255,255,255,0.25); margin: 0; font-size: 0.88rem; font-weight: 400; }
.classification-banner .glow-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 10px;
    vertical-align: middle;
    animation: pulse-glow 2.5s ease-in-out infinite;
}
.classification-banner.privado .glow-dot { background: #f87171; box-shadow: 0 0 10px rgba(248,113,113,0.6); }
.classification-banner.publico .glow-dot { background: #4ade80; box-shadow: 0 0 10px rgba(74,222,128,0.6); }
@keyframes pulse-glow {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.3; transform: scale(1.6); }
}

/* ── TEXT PANEL (estilo terminal AuthKit) ───────────────────── */
.text-panel {
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    overflow: hidden;
    transition: border-color 0.25s;
    position: relative;
}
/* corner marker */
.text-panel::after {
    content: '×';
    position: absolute;
    bottom: 10px; right: 14px;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.05);
    font-weight: 300;
}
.text-panel:hover { border-color: rgba(99,120,230,0.2); }
.text-panel-header {
    background: rgba(255,255,255,0.025);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding: 0.7rem 1rem;
    display: flex;
    align-items: center;
    gap: 7px;
}
.text-panel-header .dot { width:10px;height:10px;border-radius:50%;opacity:0.7; }
.text-panel-header .dot-r { background:#ef4444; }
.text-panel-header .dot-y { background:#f59e0b; }
.text-panel-header .dot-g { background:#22c55e; }
.text-panel-header .panel-title {
    color: rgba(255,255,255,0.18);
    font-size: 0.76rem;
    font-weight: 400;
    margin-left: 6px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.03em;
}
.text-panel-body {
    padding: 1.4rem;
    line-height: 2.1;
    font-size: 0.92rem;
    color: #8896ae;
    min-height: 90px;
}
.text-panel-body.masked {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.2);
    line-height: 1.9;
}

/* ── ENTITY CHIPS ───────────────────────────────────────── */
.entity-chip {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.76rem;
    font-weight: 600;
    color: white;
    margin: 3px 4px 3px 0;
    letter-spacing: 0.04em;
    opacity: 0.9;
}

/* ── ENTITY GROUP CARD ──────────────────────────────────── */
.entity-group-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 14px;
    padding: 1.3rem;
    margin-bottom: 10px;
    position: relative;
    transition: border-color 0.25s, background 0.25s;
}
.entity-group-card::after {
    content: '×';
    position: absolute;
    top: 10px; right: 12px;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.07);
    font-weight: 300;
}
.entity-group-card:hover {
    border-color: rgba(99,120,230,0.2);
    background: rgba(255,255,255,0.03);
}
.entity-group-title {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: rgba(255,255,255,0.18);
    margin-bottom: 0.7rem;
}
.entity-value {
    background: rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 6px;
    padding: 4px 11px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.65);
    display: inline-block;
    margin: 3px 4px 3px 0;
    letter-spacing: 0.02em;
}

/* ── SECTION TITLE — AuthKit between-lines-gradient style ── */
.section-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: rgba(152,192,239,0.52);
    text-transform: uppercase;
    letter-spacing: 0.18em;
    margin: 2.5rem 0 1.2rem;
    display: flex;
    align-items: center;
    gap: 14px;
    text-align: center;
}
.section-title::before, .section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(152,192,239,0.12), transparent);
}

/* ── RESULT ROW BADGE ───────────────────────────────────── */
.result-row-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.73rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.result-row-badge.privado {
    background: rgba(239,68,68,0.12);
    color: #f87171;
    border: 1px solid rgba(239,68,68,0.25);
}
.result-row-badge.publico {
    background: rgba(34,197,94,0.12);
    color: #4ade80;
    border: 1px solid rgba(34,197,94,0.25);
}

/* ── SIDEBAR BADGE ──────────────────────────────────────── */
.sidebar-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 5px;
    font-size: 0.72rem;
    font-weight: 700;
    color: #ffffff !important;
    margin: 2px 2px;
    letter-spacing: 0.03em;
}

/* ── METRICS OVERRIDE ─────────────────────────────────────── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1rem;
    backdrop-filter: blur(8px);
}
[data-testid="stMetricValue"] { color: #818cf8 !important; font-weight: 700; }
[data-testid="stMetricLabel"] { color: #4a5568 !important; font-size: 0.78rem !important; }

/* ── DOWNLOAD BUTTON ─────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(54,86,210,0.25) !important;
    color: #818cf8 !important;
    box-shadow: none !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(54,86,210,0.08) !important;
    border-color: rgba(54,86,210,0.5) !important;
    transform: translateY(-1px);
}

/* ── SUCCESS / INFO ALERTS ──────────────────────────────── */
.stAlert {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(8px);
}

/* ════════ INTRO FEATURE CARDS ═══════════════════════════ */
.intro-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 0.25rem 0 2.8rem;
}
.intro-card {
    background: rgba(255,255,255,0.018);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 1.8rem 1.5rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, background 0.3s, box-shadow 0.3s;
}
/* linha de luz no topo */
.intro-card::before {
    content: '';
    position: absolute;
    top: 0; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(152,192,239,0.13), transparent);
}
/* marcador × canto AuthKit */
.intro-card::after {
    content: '×';
    position: absolute;
    top: 10px; right: 14px;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.07);
    font-weight: 300;
}
.intro-card:hover {
    background: rgba(255,255,255,0.028);
    border-color: rgba(152,192,239,0.18);
    box-shadow: 0 0 32px rgba(99,120,230,0.07);
}
.intro-card-icon {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    display: block;
}
.intro-card-tag {
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.17em;
    color: rgba(152,192,239,0.48);
    margin-bottom: 0.45rem;
    display: block;
}
.intro-card-title {
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #D8ECF8 0%, #98C0EF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.65rem;
    display: block;
    line-height: 1.35;
}
.intro-card-body {
    font-size: 0.83rem;
    color: rgba(186,214,247,0.42);
    line-height: 1.8;
}
.intro-card-chips {
    margin-top: 1.1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.intro-mini-chip {
    font-size: 0.67rem;
    font-weight: 600;
    padding: 2px 9px;
    border-radius: 999px;
    background: rgba(152,192,239,0.07);
    border: 1px solid rgba(152,192,239,0.16);
    color: rgba(152,192,239,0.72);
    letter-spacing: 0.04em;
}

/* ════════ SIDEBAR REDESIGN ══════════════════════════════ */
.sb-logo-section {
    padding: 1.6rem 0.5rem 0.9rem;
    text-align: center;
}
.sb-logo-icon { font-size: 2rem; line-height: 1; display: block; }
.sb-logo-name {
    font-size: 1.05rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    margin-top: 8px;
    display: block;
    background: linear-gradient(135deg, #ffffff 0%, #D8ECF8 55%, #98C0EF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sb-logo-sub {
    font-size: 0.61rem;
    color: rgba(152,192,239,0.38) !important;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 4px;
    display: block;
}
.sb-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin: 0.8rem 0;
}
.sb-section-label {
    font-size: 0.61rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: rgba(152,192,239,0.45) !important;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sb-section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.05);
}
.sb-score-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.8rem;
    line-height: 2;
    margin-top: 8px;
}
.sb-entity-row {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 5px 0;
    border-bottom: 1px solid rgba(255,255,255,0.035);
}
.sb-entity-row:last-child { border-bottom: none; }
.sb-entity-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}
.sb-entity-name {
    color: rgba(186,214,247,0.68) !important;
    font-size: 0.8rem;
    font-weight: 500;
}
.sb-tech-row {
    font-size: 0.79rem;
    color: rgba(186,214,247,0.5) !important;
    padding: 3px 0;
    display: flex;
    align-items: center;
    gap: 8px;
    line-height: 1.6;
}
.sb-tech-row::before {
    content: '';
    width: 3px; height: 3px;
    border-radius: 50%;
    background: rgba(152,192,239,0.38);
    flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

# ========================== INICIALIZAÇÃO ==========================

@st.cache_resource
def carregar_detector(threshold):
    return PIIDetector(threshold=threshold)

# ========================== SIDEBAR ==========================

with st.sidebar:
    st.markdown("""
    <div class="sb-logo-section">
        <span class="sb-logo-icon">🛡️</span>
        <span class="sb-logo-name">PII Shield</span>
        <span class="sb-logo-sub">Hackathon CapacitaDF · 2026</span>
    </div>
    <hr class="sb-divider">
    <div class="sb-section-label">Configuração</div>
    """, unsafe_allow_html=True)

    threshold = st.slider(
        "Threshold de sensibilidade",
        min_value=10, max_value=100, value=30, step=5,
        help="Score mínimo para classificar como PRIVADO. Padrão: 30 (conservador)."
    )
    st.markdown(f"""
    <div class="sb-score-card">
        <span style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:rgba(152,192,239,0.55);">Regra de classificação</span><br>
        Score &lt; <strong style="color:#98C0EF;">{threshold}</strong>
        &nbsp;→&nbsp; <span style="color:#4ade80;font-weight:600;">PÚBLICO</span><br>
        Score ≥ <strong style="color:#98C0EF;">{threshold}</strong>
        &nbsp;→&nbsp; <span style="color:#f87171;font-weight:600;">PRIVADO</span>
    </div>
    <hr class="sb-divider" style="margin-top:14px;">
    <div class="sb-section-label">Entidades detectadas</div>
    """, unsafe_allow_html=True)

    entidades_flat = [
        ('cpf',            'CPF'),
        ('rg',             'RG'),
        ('cnh',            'CNH'),
        ('cnpj',           'CNPJ'),
        ('titulo_eleitor', 'Título de eleitor'),
        ('nomes',          'Nome'),
        ('email',          'E-mail'),
        ('telefone',       'Telefone'),
        ('endereco',       'Endereço'),
        ('dados_bancarios','Dados bancários'),
        ('cartao_credito', 'Cartão de crédito'),
        ('processo_sei',   'Processo SEI'),
        ('protocolo_lai',  'Protocolo LAI'),
        ('saude',          'Saúde'),
        ('data_nascimento','Data de nascimento'),
        ('filiacao',       'Filiação'),
    ]
    rows_html = ''.join(
        f'<div class="sb-entity-row">'
        f'<div class="sb-entity-dot" style="background:{ENTITY_CONFIG.get(k, {}).get("color", "#64748b")}"></div>'
        f'<span class="sb-entity-name">{label}</span>'
        f'</div>'
        for k, label in entidades_flat
    )
    st.markdown(f'<div style="margin-bottom:4px;">{rows_html}</div>', unsafe_allow_html=True)

    st.markdown("""
    <hr class="sb-divider" style="margin-top:10px;">
    <div class="sb-section-label">Tecnologia</div>
    <div style="padding-bottom:1.2rem;">
        <div class="sb-tech-row">Regex com janela de contexto</div>
        <div class="sb-tech-row">spaCy NER pt_core_news_lg</div>
        <div class="sb-tech-row">Validação Módulo 11 (CPF)</div>
        <div class="sb-tech-row">Algoritmo de Luhn (cartão)</div>
        <div class="sb-tech-row">67 DDDs Anatel validados</div>
        <div class="sb-tech-row">100% local · sem envio de dados</div>
    </div>
    """, unsafe_allow_html=True)

# ========================== HERO ==========================

st.markdown("""
<div class="hero-wrapper">
    <div class="hero-eyebrow">Hackathon CapacitaDF &nbsp;·&nbsp; Privacidade &amp; LGPD</div>
    <div class="hero-badge">🛡️&nbsp; Detector de PII em Português Brasileiro</div>
    <div class="hero-title">PII Shield</div>
    <p class="hero-sub">
        Detecção e anonimização automática de dados pessoais sensíveis.<br>
        100% local &mdash; seus dados nunca saem do seu computador.
    </p>
    <div class="hero-glow-line"></div>
</div>
""", unsafe_allow_html=True)

# ========================== INTRO CARDS ==========================

st.markdown("""
<div class="intro-grid">
    <div class="intro-card">
        <span class="intro-card-icon">📝</span>
        <span class="intro-card-tag">Passo 1 · Texto livre</span>
        <span class="intro-card-title">Cole ou digite qualquer texto</span>
        <p class="intro-card-body">
            Na aba <strong style="color:#D8ECF8;">Análise de Texto</strong>, cole e-mails,
            ofícios, requerimentos ou qualquer trecho. O sistema detecta e destaca
            automaticamente dados pessoais com score de sensibilidade em tempo real.
        </p>
        <div class="intro-card-chips">
            <span class="intro-mini-chip">CPF</span>
            <span class="intro-mini-chip">RG / CNH</span>
            <span class="intro-mini-chip">Nomes</span>
            <span class="intro-mini-chip">E-mail</span>
            <span class="intro-mini-chip">+16 tipos</span>
        </div>
    </div>
    <div class="intro-card">
        <span class="intro-card-icon">📁</span>
        <span class="intro-card-tag">Passo 2 · Arquivo em lote</span>
        <span class="intro-card-title">Envie uma planilha Excel ou CSV</span>
        <p class="intro-card-body">
            Na aba <strong style="color:#D8ECF8;">Análise de Arquivo</strong>, faça upload de
            um arquivo <code style="color:#98C0EF;font-size:0.79rem;">.xlsx</code>,
            <code style="color:#98C0EF;font-size:0.79rem;">.xls</code> ou
            <code style="color:#98C0EF;font-size:0.79rem;">.csv</code>.
            Selecione a coluna de texto e processe centenas de registros de uma só vez.
        </p>
        <div class="intro-card-chips">
            <span class="intro-mini-chip">.xlsx</span>
            <span class="intro-mini-chip">.xls</span>
            <span class="intro-mini-chip">.csv</span>
            <span class="intro-mini-chip">Processamento em lote</span>
        </div>
    </div>
    <div class="intro-card">
        <span class="intro-card-icon">📊</span>
        <span class="intro-card-tag">Resultado · Relatório completo</span>
        <span class="intro-card-title">Visualize, analise e exporte</span>
        <p class="intro-card-body">
            Receba <strong style="color:#D8ECF8;">score de privacidade</strong>, entidades
            destacadas em cores por categoria, versão anonimizada pronta para uso
            e exportação completa em CSV com todos os registros processados.
        </p>
        <div class="intro-card-chips">
            <span class="intro-mini-chip">Score</span>
            <span class="intro-mini-chip">Highlight</span>
            <span class="intro-mini-chip">Anonimizado</span>
            <span class="intro-mini-chip">Export CSV</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========================== TABS ==========================

tab_texto, tab_arquivo = st.tabs(["  📝  Análise de Texto  ", "  📁  Análise de Arquivo  "])

# ========================== TAB 1: TEXTO INDIVIDUAL ==========================

with tab_texto:
    st.markdown("""
    <div class="section-title">Cole ou digite um texto para análise</div>
    """, unsafe_allow_html=True)

    if 'exemplo_texto' not in st.session_state:
        st.session_state['exemplo_texto'] = ''

    texto_input = st.text_area(
        "Texto",
        value=st.session_state['exemplo_texto'],
        height=160,
        placeholder="Ex: O requerente João da Silva, CPF 123.456.789-01, solicita acesso ao processo SEI 00015-01009853/2026-01...",
        label_visibility="collapsed"
    )

    col_btn, col_ex, col_clear = st.columns([2, 2, 1])
    with col_btn:
        analisar = st.button("🔍 Analisar Texto", type="primary", use_container_width=True)
    with col_ex:
        usar_exemplo = st.button("📋 Carregar exemplo realista", use_container_width=True)
    with col_clear:
        limpar = st.button("🗑️ Limpar", use_container_width=True)

    if usar_exemplo:
        st.session_state['exemplo_texto'] = (
            "O requerente João da Silva, CPF 123.456.789-01, nascido em 15/03/1990, "
            "residente na Rua das Flores, 123, Brasília-DF, CEP 70000-000, "
            "telefone (61) 99999-8888, email joao.silva@email.com, "
            "solicita acesso aos documentos do processo SEI 00015-01009853/2026-01. "
            "Protocolo LAI-258789/2025. Mãe: Maria Aparecida da Silva. "
            "O requerente é diabético e possui prontuário no Hospital Regional. "
            "Veículo de placa ABC1D23, conta bancária 12345-6, agência 0012-3."
        )
        st.rerun()
    if limpar:
        st.session_state['exemplo_texto'] = ''
        st.rerun()

    if analisar and texto_input:
        detector = carregar_detector(threshold)

        with st.spinner("Analisando..."):
            resultado = detector.detectar_pii(texto_input)

        eh_privado = resultado['classificacao'] == 'PRIVADO'
        total_entidades = sum(len(v) for v in resultado['entidades'].values() if v)

        # Banner de classificação
        if eh_privado:
            st.markdown(f"""
            <div class="classification-banner privado">
                <span class="glow-dot"></span>
                <h2>🔴 PRIVADO</h2>
                <p>Score de sensibilidade: <strong style="color:#fca5a5">{resultado['score']}</strong> pts &nbsp;·&nbsp; {total_entidades} entidade(s) detectada(s)</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="classification-banner publico">
                <span class="glow-dot"></span>
                <h2>🟢 PÚBLICO</h2>
                <p>Score de sensibilidade: <strong style="color:#86efac">{resultado['score']}</strong> pts &nbsp;·&nbsp; Nenhuma entidade sensível significativa</p>
            </div>
            """, unsafe_allow_html=True)

        # Cards de stats
        col1, col2, col3 = st.columns(3)
        with col1:
            cls = "privado" if eh_privado else "publico"
            val_label = "PRIVADO" if eh_privado else "PÚBLICO"
            st.markdown(f"""
            <div class="stat-card {cls}">
                <div class="stat-card-value {cls}">{val_label}</div>
                <div class="stat-card-label">Classificação Final</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card neutro">
                <div class="stat-card-value neutro">{total_entidades}</div>
                <div class="stat-card-label">Entidades Detectadas</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            score_cls = "score-alto" if resultado['score'] >= 80 else "neutro"
            st.markdown(f"""
            <div class="stat-card {score_cls}">
                <div class="stat-card-value {score_cls}">{resultado['score']}</div>
                <div class="stat-card-label">Score de Sensibilidade</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Painéis lado a lado — original vs. anonimizado
        col_orig, col_mask = st.columns(2)

        with col_orig:
            st.markdown("""
            <div class="text-panel">
                <div class="text-panel-header">
                    <div class="dot dot-r"></div><div class="dot dot-y"></div><div class="dot dot-g"></div>
                    <span class="panel-title">original.txt — entidades destacadas</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f'<div class="text-panel-body">{resultado["texto_highlight"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_mask:
            st.markdown("""
            <div class="text-panel">
                <div class="text-panel-header">
                    <div class="dot dot-r"></div><div class="dot dot-y"></div><div class="dot dot-g"></div>
                    <span class="panel-title">anonimizado.txt — dados substituídos</span>
                </div>
            """, unsafe_allow_html=True)
            import html as html_lib
            masked_escaped = html_lib.escape(resultado["texto_mascarado"]).replace('\n','<br>')
            st.markdown(f'<div class="text-panel-body masked">{masked_escaped}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Entidades encontradas
        entidades_com_valor = {k: v for k, v in resultado['entidades'].items() if v}
        if entidades_com_valor:
            st.markdown('<div class="section-title">📋 Entidades Encontradas</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(entidades_com_valor), 4))
            for i, (tipo, valores) in enumerate(entidades_com_valor.items()):
                cfg = ENTITY_CONFIG.get(tipo, {'label': tipo, 'color': '#999'})
                vals_html = ''.join(f'<span class="entity-value">{v}</span>' for v in valores)
                with cols[i % len(cols)]:
                    st.markdown(f"""
                    <div class="entity-group-card">
                        <div class="entity-group-title">{cfg['label'].replace('[','').replace(']','')}</div>
                        <span class="entity-chip" style="background:{cfg['color']};margin-bottom:6px;">
                            {len(valores)} ocorrência{'s' if len(valores) > 1 else ''}
                        </span><br>
                        {vals_html}
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(34,197,94,0.04);border:1px solid rgba(34,197,94,0.14);border-radius:12px;padding:1.2rem;text-align:center;color:#86efac;">
                ✅ Nenhuma entidade sensível detectada neste texto.
            </div>
            """, unsafe_allow_html=True)

# ========================== TAB 2: ARQUIVO ==========================

with tab_arquivo:
    st.markdown('<div class="section-title">Faça upload de um arquivo Excel ou CSV para análise em lote</div>', unsafe_allow_html=True)

    arquivo = st.file_uploader(
        "Arraste ou selecione o arquivo",
        type=['xlsx', 'xls', 'csv'],
        label_visibility="collapsed"
    )

    if arquivo:
        if arquivo.name.endswith('.csv'):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo, engine='openpyxl')

        st.markdown(f"""
        <div style="background:rgba(152,192,239,0.05);border:1px solid rgba(152,192,239,0.14);border-radius:10px;padding:0.8rem 1.2rem;color:#98C0EF;font-size:0.92rem;margin-bottom:1rem;">
            📂 <strong>{arquivo.name}</strong> carregado com sucesso — <strong>{len(df)}</strong> registros, <strong>{len(df.columns)}</strong> colunas
        </div>
        """, unsafe_allow_html=True)

        coluna_texto = None
        for col in df.columns:
            if 'texto' in col.lower() or 'conteúdo' in col.lower() or 'conteudo' in col.lower():
                coluna_texto = col
                break
        if coluna_texto is None:
            coluna_texto = df.columns[1] if len(df.columns) > 1 else df.columns[0]

        coluna_texto = st.selectbox("Coluna de texto:", df.columns.tolist(), index=df.columns.tolist().index(coluna_texto))

        if st.button("🚀 Processar Arquivo", type="primary", use_container_width=True):
            detector = carregar_detector(threshold)
            progress = st.progress(0, text="Processando registros...")
            resultados = []

            for i, (idx, row) in enumerate(df.iterrows()):
                texto = str(row[coluna_texto]) if pd.notna(row[coluna_texto]) else ""
                resultado = detector.detectar_pii(texto)
                entidades_str = ', '.join(resultado['resumo']) if resultado['resumo'] else 'Nenhuma'

                resultados.append({
                    'ID': row[df.columns[0]],
                    'Texto Original': texto,
                    'Texto Anonimizado': resultado.get('texto_mascarado', texto),
                    'Entidades': entidades_str,
                    'Classificação': resultado['classificacao'],
                    'Score': resultado['score'],
                    '_highlight': resultado.get('texto_highlight', texto),
                    '_entidades_raw': resultado['entidades']
                })

                progress.progress((i + 1) / len(df), text=f"Analisando {i + 1}/{len(df)}...")

            progress.empty()
            df_resultado = pd.DataFrame(resultados)
            st.session_state['df_resultado'] = df_resultado

        if 'df_resultado' in st.session_state:
            df_resultado = st.session_state['df_resultado']
            import plotly.express as px
            import html as html_lib

            total = len(df_resultado)
            privados = int((df_resultado['Classificação'] == 'PRIVADO').sum())
            publicos = int((df_resultado['Classificação'] == 'PUBLICO').sum())
            score_medio = df_resultado['Score'].mean()

            st.markdown('<div class="section-title">📊 Painel de Resultados</div>', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="stat-card neutro">
                    <div class="stat-card-value neutro">{total}</div>
                    <div class="stat-card-label">Total de Registros</div>
                </div>""", unsafe_allow_html=True)
            with col2:
                pct_priv = f"{privados/total*100:.1f}%" if total else "0%"
                st.markdown(f"""
                <div class="stat-card privado">
                    <div class="stat-card-value privado">{privados}</div>
                    <div class="stat-card-label">PRIVADO &nbsp;({pct_priv})</div>
                </div>""", unsafe_allow_html=True)
            with col3:
                pct_pub = f"{publicos/total*100:.1f}%" if total else "0%"
                st.markdown(f"""
                <div class="stat-card publico">
                    <div class="stat-card-value publico">{publicos}</div>
                    <div class="stat-card-label">PÚBLICO &nbsp;({pct_pub})</div>
                </div>""", unsafe_allow_html=True)
            with col4:
                score_cls = "score-alto" if score_medio >= 80 else "neutro"
                st.markdown(f"""
                <div class="stat-card {score_cls}">
                    <div class="stat-card-value {score_cls}">{score_medio:.1f}</div>
                    <div class="stat-card-label">Score Médio</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            col_pizza, col_barra = st.columns(2)

            dark_layout = dict(
                paper_bgcolor="#060810",
                plot_bgcolor="#0a0c18",
                font_color="#bcc8d8",
                title_font_color="#98C0EF",
                height=360
            )

            with col_pizza:
                fig_pizza = px.pie(
                    values=[privados, publicos],
                    names=['PRIVADO', 'PÚBLICO'],
                    color_discrete_sequence=['#f87171', '#4ade80'],
                    title='Distribuição de Classificação',
                    hole=0.45
                )
                fig_pizza.update_layout(**dark_layout)
                fig_pizza.update_traces(textfont_color="#e2e8f0")
                st.plotly_chart(fig_pizza, use_container_width=True)

            with col_barra:
                contagem_entidades = {}
                for _, row in df_resultado.iterrows():
                    for tipo, valores in row['_entidades_raw'].items():
                        if valores:
                            contagem_entidades[tipo] = contagem_entidades.get(tipo, 0) + len(valores)

                if contagem_entidades:
                    df_ent = pd.DataFrame(
                        list(contagem_entidades.items()),
                        columns=['Tipo', 'Quantidade']
                    ).sort_values('Quantidade', ascending=True)

                    fig_bar = px.bar(
                        df_ent, x='Quantidade', y='Tipo', orientation='h',
                        title='Frequência por Tipo de Entidade',
                        color='Tipo',
                        color_discrete_map={t: ENTITY_CONFIG.get(t, {}).get('color', '#64748b') for t in df_ent['Tipo']}
                    )
                    fig_bar.update_layout(**dark_layout, showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown('<div class="section-title">📋 Registros Detalhados</div>', unsafe_allow_html=True)

            filtro = st.selectbox("Filtrar por classificação:", ["Todos", "PRIVADO", "PUBLICO"])
            df_display = df_resultado.copy()
            if filtro != "Todos":
                df_display = df_display[df_display['Classificação'] == filtro]

            for _, row in df_display.iterrows():
                badge_cls = "privado" if row['Classificação'] == 'PRIVADO' else "publico"
                badge_txt = "🔴 PRIVADO" if row['Classificação'] == 'PRIVADO' else "🟢 PÚBLICO"
                exp_label = f"ID {row['ID']}  ·  {badge_txt}  ·  Score {row['Score']}  ·  {row['Entidades']}"

                with st.expander(exp_label):
                    st.markdown(f'<span class="result-row-badge {badge_cls}">{badge_txt}</span> &nbsp; Score: <strong style="color:#fbbf24">{row["Score"]}</strong>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)

                    with c1:
                        st.markdown("""
                        <div class="text-panel">
                            <div class="text-panel-header">
                                <div class="dot dot-r"></div><div class="dot dot-y"></div><div class="dot dot-g"></div>
                                <span class="panel-title">original.txt</span>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f'<div class="text-panel-body">{row["_highlight"]}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    with c2:
                        st.markdown("""
                        <div class="text-panel">
                            <div class="text-panel-header">
                                <div class="dot dot-r"></div><div class="dot dot-y"></div><div class="dot dot-g"></div>
                                <span class="panel-title">anonimizado.txt</span>
                            </div>
                        """, unsafe_allow_html=True)
                        masked_esc = html_lib.escape(row["Texto Anonimizado"]).replace('\n', '<br>')
                        st.markdown(f'<div class="text-panel-body masked">{masked_esc}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            df_download = df_resultado[['ID', 'Texto Original', 'Texto Anonimizado', 'Entidades', 'Classificação', 'Score']]
            csv_data = df_download.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Exportar resultados (CSV)",
                csv_data,
                file_name="resultado_pii.csv",
                mime="text/csv",
                use_container_width=True
            )
