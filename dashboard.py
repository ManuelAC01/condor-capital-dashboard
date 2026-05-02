"""
Cóndor Capital — Quantamental Screener Dashboard  (v4 — premium UI)
Local Streamlit app | B3 Mid-Cap L/S Strategy
Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cóndor Capital | B3 Screener",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY    = "#070f1f"
NAVY2   = "#0d1b2e"
NAVY3   = "#152540"
NAVY4   = "#1e3356"
GOLD    = "#c9a227"
GOLD2   = "#e8c84a"
GREEN   = "#00c853"
RED     = "#f44336"
WHITE   = "#e8eef4"
MUTED   = "#6b7f96"
BORDER  = "#1e3356"

def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# Pre-computed alpha variants
G15, G35 = rgba(GREEN, 0.15), rgba(GREEN, 0.35)
R15, R35 = rgba(RED,   0.15), rgba(RED,   0.35)
GOLD10    = rgba(GOLD,  0.10)
GOLD30    = rgba(GOLD,  0.30)
MUTED12   = rgba(MUTED, 0.12)
MUTED30   = rgba(MUTED, 0.30)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Base ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {{
    background: {NAVY} !important;
    color: {WHITE};
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}}

/* ── Streamlit chrome: leave ALL sidebar/header controls untouched ──
   Do NOT hide stHeader, stSidebarCollapsedControl, stDecoration,
   stToolbar, #MainMenu, or footer — they contain the native sidebar
   toggle. Hiding any of them breaks collapse/expand. ── */

/* Main layout */
.main .block-container {{
    padding: 1.8rem 2.2rem 4rem !important;
    max-width: 1440px;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {NAVY2} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] > div:first-child {{ padding: 1rem 0.9rem 2rem !important; }}
[data-testid="stSidebar"] * {{
    color: {WHITE} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* Sidebar select / multi-select */
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: {NAVY3} !important;
    border: 1px solid {NAVY4} !important;
    border-radius: 7px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div {{ color: {WHITE} !important; }}

/* Sidebar slider thumb = gold */
[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] > div:last-child > div {{
    background: {GOLD} !important;
    border-color: {GOLD} !important;
}}

/* ── Plotly chart cards ── */
[data-testid="stPlotlyChart"] {{
    background: {NAVY2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    padding: 0 !important;
}}

/* ── KPI cards ── */
.kpi-card {{
    background: {NAVY2};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 18px 20px 16px;
    position: relative;
    overflow: hidden;
    height: 100%;
}}
.kpi-card::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, {GOLD}, transparent 60%);
}}
.kpi-accent {{
    width: 28px; height: 3px;
    border-radius: 2px;
    margin-bottom: 12px;
}}
.kpi-label {{
    font-size: 0.63rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: {MUTED};
    margin-bottom: 6px;
}}
.kpi-value {{
    font-size: 2.1rem;
    font-weight: 900;
    line-height: 1;
    margin-bottom: 5px;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
}}
.kpi-sub {{
    font-size: 0.68rem;
    color: {MUTED};
    font-weight: 400;
    line-height: 1.4;
}}

/* ── Factor methodology strip ── */
.factor-strip {{
    background: {NAVY2};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 0;
}}
.factor-item {{
    flex: 1;
    text-align: center;
    padding: 0 16px;
    position: relative;
}}
.factor-item:not(:last-child)::after {{
    content: '';
    position: absolute;
    right: 0; top: 10%; bottom: 10%;
    width: 1px;
    background: {BORDER};
}}
.factor-name {{
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {WHITE};
    margin-bottom: 2px;
}}
.factor-signal {{
    font-size: 0.62rem;
    color: {MUTED};
    margin-bottom: 6px;
}}
.factor-weight {{
    font-size: 1.1rem;
    font-weight: 800;
    color: {GOLD};
    letter-spacing: -0.02em;
}}

/* ── Section headers ── */
.section-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}}
.section-header-line {{
    height: 1px;
    flex: 1;
    background: linear-gradient(90deg, {BORDER}, transparent);
}}
.section-header-text {{
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {GOLD};
    white-space: nowrap;
}}

/* ── Signal badges ── */
.badge {{
    display: inline-block;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
.badge-long  {{ background:{G15}; color:{GREEN}; border:1px solid {G35}; }}
.badge-short {{ background:{R15}; color:{RED};   border:1px solid {R35}; }}
.badge-neutral {{ background:{MUTED12}; color:{MUTED}; border:1px solid {MUTED30}; }}

/* ── Position cards ── */
.pos-card {{
    background: {NAVY2};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 14px 16px 12px;
    margin-bottom: 8px;
}}
.pos-header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; }}
.pos-rank   {{ font-size:0.6rem; font-weight:700; color:{MUTED}; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:2px; }}
.pos-ticker {{ font-size:1.05rem; font-weight:900; letter-spacing:-0.01em; }}
.pos-meta   {{ font-size:0.72rem; color:{WHITE}; margin:1px 0; }}
.pos-sector {{ font-size:0.65rem; color:{MUTED}; margin-bottom:10px; }}
.pos-grid   {{ display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:10px; }}
.pos-metric-label {{ font-size:0.58rem; color:{MUTED}; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:2px; }}
.pos-metric-value {{ font-size:0.82rem; font-weight:600; color:{WHITE}; }}
.score-bar-track {{ background:{NAVY3}; border-radius:3px; height:3px; overflow:hidden; margin-top:8px; }}

/* ── Dividers ── */
.div-sm {{ border:none; border-top:1px solid {BORDER}; margin:20px 0; }}
.div-md {{ border:none; border-top:1px solid {BORDER}; margin:28px 0; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width:4px; height:4px; }}
::-webkit-scrollbar-track {{ background:{NAVY}; }}
::-webkit-scrollbar-thumb {{ background:{NAVY4}; border-radius:2px; }}
::-webkit-scrollbar-thumb:hover {{ background:{GOLD}; }}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    border-radius: 10px !important;
    overflow: hidden;
}}
[data-testid="stDataFrame"] th {{
    background: {NAVY3} !important;
    color: {MUTED} !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}}

/* Streamlit column gap */
[data-testid="column"] {{ gap: 1rem !important; }}
</style>
""", unsafe_allow_html=True)

# ── Plotly chart config (no toolbar) ─────────────────────────────────────────
CHART_CFG = {"displayModeBar": False, "displaylogo": False, "staticPlot": False}

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=NAVY2,
    font=dict(family="Inter, sans-serif", color=WHITE, size=11),
    hoverlabel=dict(
        bgcolor=NAVY3, bordercolor=NAVY4,
        font=dict(color=WHITE, size=11, family="Inter"),
    ),
    margin=dict(l=16, r=16, t=64, b=16),
)

# ── Load data ─────────────────────────────────────────────────────────────────
CSV_PATH = Path(__file__).parent / "condor_capital_results.csv"

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Signal"] = df["Signal"].fillna("Neutral").replace("", "Neutral")
    if "Val Metric" in df.columns:
        df = df.rename(columns={"Val Metric": "P/E"})
    nums = ["Rank","Mkt Cap (R$B)","P/E","ROE (%)","Ret 6M (%)","Ret 12M (%)",
            "Value Score","Quality Score","Momentum Score","Composite"]
    for c in nums:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

df_raw = load_data(CSV_PATH)

# ── Helpers ───────────────────────────────────────────────────────────────────
def sig_color(s):
    return GREEN if s == "LONG" else (RED if s == "SHORT" else MUTED)

def fmt(val, fmt_str, fallback="—"):
    return fmt_str.format(val) if pd.notna(val) else fallback

def section_hdr(icon, text):
    st.markdown(f"""
    <div class="section-header">
      <span class="section-header-text">{icon} &nbsp; {text}</span>
      <div class="section-header-line"></div>
    </div>""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:10px 4px 18px;border-bottom:1px solid {BORDER};margin-bottom:18px">
      <div style="font-size:2rem;text-align:center;margin-bottom:8px">🦅</div>
      <div style="color:{GOLD};font-weight:900;font-size:0.95rem;letter-spacing:0.12em;
                  text-align:center;text-transform:uppercase">Cóndor Capital</div>
      <div style="color:{MUTED};font-size:0.63rem;letter-spacing:0.08em;
                  text-align:center;margin-top:3px">B3 MID-CAP L/S SCREENER</div>
    </div>""", unsafe_allow_html=True)

    st.caption("Use the ← arrow button or ⌘ Shift S to show / hide filters.")

    st.markdown(f"<p style='font-size:0.63rem;font-weight:700;letter-spacing:0.16em;"
                f"text-transform:uppercase;color:{MUTED};margin-bottom:8px'>Signal</p>",
                unsafe_allow_html=True)
    signal_opts = ["All", "LONG", "SHORT", "Neutral"]
    signal_sel  = st.selectbox("Signal", signal_opts, label_visibility="collapsed")

    st.markdown(f"<p style='font-size:0.63rem;font-weight:700;letter-spacing:0.16em;"
                f"text-transform:uppercase;color:{MUTED};margin:14px 0 8px'>Sector</p>",
                unsafe_allow_html=True)
    sectors    = sorted(df_raw["Sector"].dropna().unique().tolist())
    sector_sel = st.multiselect("Sector", sectors, default=sectors, label_visibility="collapsed")

    st.markdown(f"<p style='font-size:0.63rem;font-weight:700;letter-spacing:0.16em;"
                f"text-transform:uppercase;color:{MUTED};margin:14px 0 8px'>"
                f"Min Composite Score</p>", unsafe_allow_html=True)
    min_comp = st.slider("Composite", 0, 100, 0, step=5, label_visibility="collapsed")

    roe_floor = float(df_raw["ROE (%)"].min()) if "ROE (%)" in df_raw.columns else 0.0
    roe_ceil  = float(df_raw["ROE (%)"].max()) if "ROE (%)" in df_raw.columns else 100.0
    st.markdown(f"<p style='font-size:0.63rem;font-weight:700;letter-spacing:0.16em;"
                f"text-transform:uppercase;color:{MUTED};margin:14px 0 8px'>Min ROE (%)</p>",
                unsafe_allow_html=True)
    min_roe = st.slider("ROE", int(roe_floor), int(roe_ceil), int(roe_floor),
                        label_visibility="collapsed")

    st.markdown(f"<hr style='border-color:{BORDER};margin:18px 0'>", unsafe_allow_html=True)

    active_n = sum([signal_sel != "All", len(sector_sel) < len(sectors),
                    min_comp > 0, min_roe > int(roe_floor)])
    if active_n:
        st.markdown(f"<div style='background:{GOLD10};border:1px solid {GOLD30};"
                    f"border-radius:6px;padding:6px 10px;text-align:center;margin-bottom:10px'>"
                    f"<span style='color:{GOLD};font-size:0.7rem;font-weight:600'>"
                    f"⚡ {active_n} filter{'s' if active_n>1 else ''} active</span></div>",
                    unsafe_allow_html=True)

    st.markdown(f"<p style='color:{MUTED};font-size:0.62rem;text-align:center;line-height:1.7'>"
                f"Yahoo Finance · yfinance<br>"
                f"<span style='color:{rgba(RED,0.8)}'>⚠</span> "
                f"Research only · not financial advice</p>",
                unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if signal_sel != "All":
    df = df[df["Signal"] == signal_sel]
if sector_sel:
    df = df[df["Sector"].isin(sector_sel)]
df = df[df["Composite"] >= min_comp]
if "ROE (%)" in df.columns:
    df = df[df["ROE (%)"] >= min_roe]

# ── Hero ──────────────────────────────────────────────────────────────────────
today  = datetime.today().strftime("%d %b %Y")
n_long = int((df_raw["Signal"] == "LONG").sum())
n_short= int((df_raw["Signal"] == "SHORT").sum())

st.markdown(f"""
<div style="background:linear-gradient(135deg,{NAVY2} 0%,{NAVY3} 55%,{NAVY2} 100%);
            border:1px solid {BORDER};border-radius:14px;
            padding:26px 32px 22px;margin-bottom:22px;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,{GOLD},{GOLD2} 40%,transparent)"></div>
  <div style="position:absolute;right:24px;top:50%;transform:translateY(-50%);
              font-size:7rem;opacity:0.04;line-height:1;user-select:none">🦅</div>
  <div style="display:flex;justify-content:space-between;align-items:center;
              flex-wrap:wrap;gap:16px;position:relative">
    <div>
      <div style="font-size:1.65rem;font-weight:900;color:{GOLD};
                  letter-spacing:0.03em;line-height:1;margin-bottom:6px">
        Cóndor Capital
      </div>
      <div style="font-size:0.9rem;font-weight:400;color:{WHITE};
                  opacity:0.85;margin-bottom:12px">
        Brazilian Mid-Cap Long / Short &nbsp;·&nbsp; Quantamental Screener
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:7px">
        <span style="background:{GOLD10};border:1px solid {GOLD30};border-radius:5px;
               padding:3px 11px;font-size:0.65rem;color:{GOLD};font-weight:700;letter-spacing:0.08em">
          B3 UNIVERSE
        </span>
        <span style="background:{G15};border:1px solid {G35};border-radius:5px;
               padding:3px 11px;font-size:0.65rem;color:{GREEN};font-weight:700;letter-spacing:0.08em">
          LIVE DATA
        </span>
        <span style="background:{MUTED12};border:1px solid {MUTED30};border-radius:5px;
               padding:3px 11px;font-size:0.65rem;color:{MUTED};font-weight:500">
          {today}
        </span>
      </div>
    </div>
    <div style="display:flex;gap:20px;text-align:center">
      <div style="border-left:2px solid {GREEN};padding:4px 0 4px 14px">
        <div style="font-size:1.6rem;font-weight:900;color:{GREEN};line-height:1">{n_long}</div>
        <div style="font-size:0.62rem;color:{MUTED};text-transform:uppercase;letter-spacing:0.1em;margin-top:2px">Longs</div>
      </div>
      <div style="border-left:2px solid {RED};padding:4px 0 4px 14px">
        <div style="font-size:1.6rem;font-weight:900;color:{RED};line-height:1">{n_short}</div>
        <div style="font-size:0.62rem;color:{MUTED};text-transform:uppercase;letter-spacing:0.1em;margin-top:2px">Shorts</div>
      </div>
      <div style="border-left:2px solid {BORDER};padding:4px 0 4px 14px">
        <div style="font-size:1.6rem;font-weight:900;color:{WHITE};line-height:1">{len(df_raw)}</div>
        <div style="font-size:0.62rem;color:{MUTED};text-transform:uppercase;letter-spacing:0.1em;margin-top:2px">Universe</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Factor methodology strip ──────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{NAVY2};border:1px solid {BORDER};border-radius:10px;
            padding:14px 8px;display:flex;align-items:stretch;margin-bottom:22px">

  <div style="flex:1;text-align:center;padding:4px 20px;
              border-right:1px solid {BORDER}">
    <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
                text-transform:uppercase;color:{MUTED};margin-bottom:3px">Value</div>
    <div style="font-size:0.68rem;color:{WHITE};margin-bottom:5px">EV/EBITDA · P/E</div>
    <div style="font-size:1.4rem;font-weight:900;color:{GOLD};line-height:1">35%</div>
  </div>

  <div style="flex:1;text-align:center;padding:4px 20px;
              border-right:1px solid {BORDER}">
    <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
                text-transform:uppercase;color:{MUTED};margin-bottom:3px">Quality</div>
    <div style="font-size:0.68rem;color:{WHITE};margin-bottom:5px">Return on Equity</div>
    <div style="font-size:1.4rem;font-weight:900;color:{GOLD};line-height:1">30%</div>
  </div>

  <div style="flex:1;text-align:center;padding:4px 20px;
              border-right:1px solid {BORDER}">
    <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
                text-transform:uppercase;color:{MUTED};margin-bottom:3px">Momentum</div>
    <div style="font-size:0.68rem;color:{WHITE};margin-bottom:5px">6M + 12M Return</div>
    <div style="font-size:1.4rem;font-weight:900;color:{GOLD};line-height:1">35%</div>
  </div>

  <div style="flex:1;text-align:center;padding:4px 20px">
    <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
                text-transform:uppercase;color:{MUTED};margin-bottom:3px">Method</div>
    <div style="font-size:0.68rem;color:{WHITE};margin-bottom:5px">Percentile rank 0–100</div>
    <div style="font-size:1.4rem;font-weight:900;color:{GOLD};line-height:1">∑</div>
  </div>

</div>
""", unsafe_allow_html=True)

# ── KPI cards ─────────────────────────────────────────────────────────────────
total   = len(df_raw)
avg_cmp = round(df_raw["Composite"].mean(), 1)
top_cmp = round(df_raw["Composite"].max(), 1)
top_tkr = df_raw.loc[df_raw["Composite"].idxmax(), "Ticker"]
n_neut  = total - n_long - n_short

def kpi_card(col, accent, label, value, sub, value_color=None):
    vc = value_color or GOLD
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-accent" style="background:{accent}"></div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value" style="color:{vc}">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
kpi_card(k1, GOLD,  "Universe",      total,   "B3 mid-caps tracked")
kpi_card(k2, GREEN, "Long Signals",  n_long,  "highest composite",  GREEN)
kpi_card(k3, RED,   "Short Signals", n_short, "lowest composite",   RED)
kpi_card(k4, GOLD,  "Avg Score",     avg_cmp, "universe composite")
kpi_card(k5, GOLD2, "Top Score",     top_cmp, f"#{top_tkr}")

st.markdown("<div class='div-md'></div>", unsafe_allow_html=True)

# ── Top 5 Longs & Shorts ──────────────────────────────────────────────────────
section_hdr("▲▼", "Signal Book — Top Ideas")

top_longs  = df_raw[df_raw["Signal"] == "LONG"].head(5)
top_shorts = df_raw[df_raw["Signal"] == "SHORT"].sort_values("Composite").head(5)

col_l, col_r = st.columns(2, gap="large")

def pos_card(rank, row, sig):
    clr  = GREEN if sig == "LONG" else RED
    bcls = "badge-long" if sig == "LONG" else "badge-short"
    arrow= "▲" if sig == "LONG" else "▼"
    pe   = fmt(row.get("P/E"),         "{:.1f}×")
    roe  = fmt(row.get("ROE (%)"),     "{:.0f}%")
    r6   = fmt(row.get("Ret 6M (%)"),  "{:+.0f}%")
    r12  = fmt(row.get("Ret 12M (%)"), "{:+.0f}%")
    cmp  = fmt(row.get("Composite"),   "{:.1f}")
    bw   = max(0, min(100, float(row.get("Composite", 50) or 50)))

    return f"""
    <div class="pos-card" style="border-left:3px solid {clr}">
      <div class="pos-header">
        <div>
          <div class="pos-rank">Rank {rank} &nbsp;{arrow}</div>
          <div class="pos-ticker" style="color:{clr}">{row['Ticker']}</div>
        </div>
        <span class="badge {bcls}">{sig}</span>
      </div>
      <div class="pos-meta">{row['Company']}</div>
      <div class="pos-sector">{row['Sector']}</div>
      <div class="pos-grid">
        <div>
          <div class="pos-metric-label">P/E</div>
          <div class="pos-metric-value">{pe}</div>
        </div>
        <div>
          <div class="pos-metric-label">ROE</div>
          <div class="pos-metric-value">{roe}</div>
        </div>
        <div>
          <div class="pos-metric-label">6M</div>
          <div class="pos-metric-value">{r6}</div>
        </div>
        <div>
          <div class="pos-metric-label">12M</div>
          <div class="pos-metric-value">{r12}</div>
        </div>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
        <span style="font-size:0.6rem;color:{MUTED};text-transform:uppercase;
                     letter-spacing:0.1em;font-weight:700">Composite</span>
        <span style="font-size:0.88rem;font-weight:800;color:{GOLD}">{cmp}</span>
      </div>
      <div class="score-bar-track">
        <div style="width:{bw}%;height:100%;
                    background:linear-gradient(90deg,{clr},{rgba(clr,0.4)});
                    border-radius:3px"></div>
      </div>
    </div>"""

with col_l:
    st.markdown(f"<p style='font-size:0.65rem;font-weight:700;letter-spacing:0.14em;"
                f"color:{GREEN};text-transform:uppercase;margin-bottom:10px'>"
                f"▲ &nbsp;Long Ideas</p>", unsafe_allow_html=True)
    for i, (_, row) in enumerate(top_longs.iterrows(), 1):
        st.markdown(pos_card(i, row, "LONG"), unsafe_allow_html=True)

with col_r:
    st.markdown(f"<p style='font-size:0.65rem;font-weight:700;letter-spacing:0.14em;"
                f"color:{RED};text-transform:uppercase;margin-bottom:10px'>"
                f"▼ &nbsp;Short Ideas</p>", unsafe_allow_html=True)
    for i, (_, row) in enumerate(top_shorts.iterrows(), 1):
        st.markdown(pos_card(i, row, "SHORT"), unsafe_allow_html=True)

st.markdown("<div class='div-md'></div>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
section_hdr("◈", "Factor Analytics")

ch1, ch2 = st.columns(2, gap="large")

# ── Chart 1: Composite bar ────────────────────────────────────────────────────
with ch1:
    bar_df = df.sort_values("Composite", ascending=True).copy()
    bar_df["clr"] = bar_df["Signal"].apply(sig_color)

    fig_bar = go.Figure(go.Bar(
        x=bar_df["Composite"],
        y=bar_df["Ticker"],
        orientation="h",
        marker=dict(
            color=bar_df["clr"],
            opacity=0.90,
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        text=bar_df["Composite"].round(1),
        textposition="outside",
        textfont=dict(color=MUTED, size=9, family="Inter"),
        hovertemplate=(
            "<b style='font-size:13px'>%{y}</b><br>"
            "<span style='color:#6b7f96'>%{customdata}</span><br>"
            "Composite: <b>%{x:.1f}</b><extra></extra>"
        ),
        customdata=bar_df["Company"],
    ))
    fig_bar.update_layout(
        **PLOTLY_BASE,
        title=dict(
            text="<b>Composite Score Ranking</b>",
            font=dict(size=13, color=WHITE, family="Inter"),
            x=0.016, y=0.97, xanchor="left", yanchor="top",
        ),
        height=480,
        showlegend=False,
        xaxis=dict(
            range=[0, 120],
            gridcolor=NAVY3,
            zeroline=False,
            color=MUTED,
            tickfont=dict(size=9),
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0)",
            color=WHITE,
            tickfont=dict(size=10, family="Inter"),
        ),
        bargap=0.38,
    )
    st.plotly_chart(fig_bar, width="stretch", config=CHART_CFG)

# ── Chart 2: Radar ────────────────────────────────────────────────────────────
with ch2:
    grp_data = (
        df_raw[df_raw["Signal"].isin(["LONG","SHORT"])]
        .groupby("Signal")[["Value Score","Quality Score","Momentum Score"]]
        .mean().reset_index()
    )
    cats = ["Value Score", "Quality Score", "Momentum Score"]

    fig_radar = go.Figure()
    for _, row in grp_data.iterrows():
        clr  = GREEN if row["Signal"] == "LONG" else RED
        fclr = rgba(GREEN, 0.15) if row["Signal"] == "LONG" else rgba(RED, 0.15)
        vals = [row[c] for c in cats] + [row[cats[0]]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals,
            theta=cats + [cats[0]],
            fill="toself",
            name=row["Signal"],
            line=dict(color=clr, width=2.5),
            fillcolor=fclr,
            hovertemplate="%{theta}: <b>%{r:.1f}</b><extra>" + row["Signal"] + "</extra>",
        ))

    fig_radar.update_layout(
        **PLOTLY_BASE,
        title=dict(
            text="<b>Long vs Short — Factor Profile</b>",
            font=dict(size=13, color=WHITE, family="Inter"),
            x=0.016, y=0.97, xanchor="left", yanchor="top",
        ),
        height=480,
        polar=dict(
            bgcolor=NAVY2,
            radialaxis=dict(
                range=[0, 100],
                gridcolor=NAVY3,
                color=MUTED,
                tickfont=dict(size=8),
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["0", "25", "50", "75", "100"],
            ),
            angularaxis=dict(
                gridcolor=NAVY4,
                color=WHITE,
                tickfont=dict(size=10.5, family="Inter"),
            ),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(color=WHITE, size=11),
            orientation="h",
            yanchor="bottom", y=-0.14,
            xanchor="center", x=0.5,
        ),
    )
    st.plotly_chart(fig_radar, width="stretch", config=CHART_CFG)

# ── Charts row 2 ──────────────────────────────────────────────────────────────
ch3, ch4 = st.columns(2, gap="large")

# ── Chart 3: Value vs Momentum scatter ───────────────────────────────────────
with ch3:
    sc_df = df.dropna(subset=["Value Score", "Momentum Score"]).copy()
    fig_sc1 = go.Figure()

    for sig, grp in sc_df.groupby("Signal"):
        clr = sig_color(sig)
        fig_sc1.add_trace(go.Scatter(
            x=grp["Value Score"],
            y=grp["Momentum Score"],
            mode="markers+text",
            name=sig,
            marker=dict(
                color=clr, size=11, opacity=0.88,
                line=dict(color=NAVY, width=1.5),
                symbol="circle",
            ),
            text=grp["Ticker"],
            textposition="top center",
            textfont=dict(color=WHITE, size=8.5, family="Inter"),
            hovertemplate=(
                "<b>%{text}</b>  ·  %{customdata}<br>"
                "Value Score: <b>%{x:.1f}</b><br>"
                "Momentum Score: <b>%{y:.1f}</b><extra></extra>"
            ),
            customdata=grp["Company"],
        ))

    # Median crosshairs
    fig_sc1.add_hline(y=50, line_dash="dot", line_color=MUTED, line_width=1, opacity=0.4)
    fig_sc1.add_vline(x=50, line_dash="dot", line_color=MUTED, line_width=1, opacity=0.4)

    # Quadrant labels
    for qx, qy, qtxt, qanc in [
        (3,  97, "VALUE PLAYS",    "left"),
        (97, 97, "BEST LONGS",     "right"),
        (3,  3,  "SHORT TARGETS",  "left"),
        (97, 3,  "MOM. TRAPS",     "right"),
    ]:
        fig_sc1.add_annotation(
            x=qx, y=qy, text=qtxt, showarrow=False,
            font=dict(size=7.5, color=MUTED, family="Inter"),
            xanchor=qanc, yanchor="top" if qy > 50 else "bottom",
        )

    fig_sc1.update_layout(
        **PLOTLY_BASE,
        title=dict(
            text="<b>Value vs Momentum</b>",
            font=dict(size=13, color=WHITE, family="Inter"),
            x=0.016, y=0.97, xanchor="left", yanchor="top",
        ),
        height=420,
        xaxis=dict(
            title=dict(text="Value Score", font=dict(size=10, color=MUTED)),
            gridcolor=NAVY3, zeroline=False, color=MUTED,
            range=[-5, 115], tickfont=dict(size=9),
        ),
        yaxis=dict(
            title=dict(text="Momentum Score", font=dict(size=10, color=MUTED)),
            gridcolor=NAVY3, zeroline=False, color=MUTED,
            range=[-5, 115], tickfont=dict(size=9),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
            font=dict(color=WHITE, size=10), orientation="h",
            yanchor="bottom", y=1.01, xanchor="right", x=1,
        ),
    )
    st.plotly_chart(fig_sc1, width="stretch", config=CHART_CFG)

# ── Chart 4: ROE vs Composite ─────────────────────────────────────────────────
with ch4:
    sc2_df = df.dropna(subset=["ROE (%)", "Composite"]).copy()
    fig_sc2 = go.Figure()

    for sig, grp in sc2_df.groupby("Signal"):
        clr   = sig_color(sig)
        sizes = grp["Mkt Cap (R$B)"].fillna(5).clip(2, 30).values * 1.9

        fig_sc2.add_trace(go.Scatter(
            x=grp["ROE (%)"],
            y=grp["Composite"],
            mode="markers+text",
            name=sig,
            marker=dict(
                color=clr, size=sizes, opacity=0.82,
                line=dict(color=NAVY, width=1.5),
                sizemode="diameter",
            ),
            text=grp["Ticker"],
            textposition="top center",
            textfont=dict(color=WHITE, size=8.5, family="Inter"),
            hovertemplate=(
                "<b>%{text}</b>  ·  %{customdata}<br>"
                "ROE: <b>%{x:.1f}%</b><br>"
                "Composite: <b>%{y:.1f}</b><extra></extra>"
            ),
            customdata=grp["Company"],
        ))

    fig_sc2.update_layout(
        **PLOTLY_BASE,
        title=dict(
            text="<b>Quality vs Composite</b>  "
                 "<span style='font-size:10px;font-weight:400'>bubble = market cap</span>",
            font=dict(size=13, color=WHITE, family="Inter"),
            x=0.016, y=0.97, xanchor="left", yanchor="top",
        ),
        height=420,
        xaxis=dict(
            title=dict(text="ROE (%)", font=dict(size=10, color=MUTED)),
            gridcolor=NAVY3, zeroline=False, color=MUTED, tickfont=dict(size=9),
        ),
        yaxis=dict(
            title=dict(text="Composite Score", font=dict(size=10, color=MUTED)),
            gridcolor=NAVY3, zeroline=False, color=MUTED,
            range=[-5, 115], tickfont=dict(size=9),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
            font=dict(color=WHITE, size=10), orientation="h",
            yanchor="bottom", y=1.01, xanchor="right", x=1,
        ),
    )
    st.plotly_chart(fig_sc2, width="stretch", config=CHART_CFG)

st.markdown("<div class='div-md'></div>", unsafe_allow_html=True)

# ── Universe table ────────────────────────────────────────────────────────────
section_hdr("≡", "Full Universe — Interactive Table")

n_shown = len(df)
n_total = len(df_raw)
note    = f"{n_shown} of {n_total} stocks" + (" · filters applied" if n_shown < n_total else " · no filters")
st.markdown(f"<p style='color:{MUTED};font-size:0.7rem;margin:-8px 0 14px'>{note}</p>",
            unsafe_allow_html=True)

table_cols = [c for c in ["Rank","Ticker","Company","Sector","Mkt Cap (R$B)","P/E",
                           "ROE (%)","Ret 6M (%)","Ret 12M (%)","Value Score",
                           "Quality Score","Momentum Score","Composite","Signal"]
              if c in df.columns]
display_df = df[table_cols].reset_index(drop=True)

st.dataframe(
    display_df,
    width="stretch",
    height=520,
    hide_index=True,
    column_config={
        "Rank":         st.column_config.NumberColumn("Rank",     width="small",  format="%d"),
        "Ticker":       st.column_config.TextColumn  ("Ticker",   width="small"),
        "Company":      st.column_config.TextColumn  ("Company",  width="medium"),
        "Sector":       st.column_config.TextColumn  ("Sector",   width="medium"),
        "Mkt Cap (R$B)":st.column_config.NumberColumn("MktCap R$B",               format="%.1f"),
        "P/E":          st.column_config.NumberColumn("P/E",                       format="%.1f"),
        "ROE (%)":      st.column_config.NumberColumn("ROE %",                     format="%.1f"),
        "Ret 6M (%)":   st.column_config.NumberColumn("6M %",                      format="%+.1f"),
        "Ret 12M (%)":  st.column_config.NumberColumn("12M %",                     format="%+.1f"),
        "Value Score":  st.column_config.ProgressColumn("Value",  min_value=0, max_value=100, format="%.0f"),
        "Quality Score":st.column_config.ProgressColumn("Quality",min_value=0, max_value=100, format="%.0f"),
        "Momentum Score":st.column_config.ProgressColumn("Momentum",min_value=0, max_value=100, format="%.0f"),
        "Composite":    st.column_config.ProgressColumn("Composite ◈", min_value=0, max_value=100, format="%.1f"),
        "Signal":       st.column_config.TextColumn  ("Signal",   width="small"),
    },
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:36px;padding:16px 0 8px;
            border-top:1px solid {BORDER};
            display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
  <div style="color:{MUTED};font-size:0.65rem">
    <span style="color:{GOLD};font-weight:700">Cóndor Capital</span>
    &nbsp;·&nbsp; B3 Mid-Cap L/S Quantamental Screener
    &nbsp;·&nbsp; Data: Yahoo Finance · yfinance
  </div>
  <div style="color:{MUTED};font-size:0.65rem">
    Research only &nbsp;·&nbsp; Cross-check vs Bloomberg / Economatica before trading
  </div>
</div>
""", unsafe_allow_html=True)
