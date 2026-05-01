"""
Cóndor Capital — Quantamental Screener Dashboard
Local Streamlit app | B3 Mid-Cap L/S Strategy
Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cóndor Capital | B3 Screener",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colour palette ─────────────────────────────────────────────────────────────
NAVY    = "#0a1628"
NAVY2   = "#0f2040"
NAVY3   = "#1a3358"
GOLD    = "#d4af37"
GOLD2   = "#f0d060"
GREEN   = "#00b347"
RED     = "#e63946"
WHITE   = "#f0f4f8"
GREY    = "#8899aa"

# rgba helpers (Plotly requires rgba() — 8-digit hex is invalid there)
GREEN_A18 = "rgba(0,179,71,0.18)"
RED_A18   = "rgba(230,57,70,0.18)"
GREEN_A13 = "rgba(0,179,71,0.13)"
GREEN_A33 = "rgba(0,179,71,0.33)"
RED_A13   = "rgba(230,57,70,0.13)"
RED_A33   = "rgba(230,57,70,0.33)"
GREY_A13  = "rgba(136,153,170,0.13)"
GREY_A27  = "rgba(136,153,170,0.27)"

def hex_rgba(hex_color: str, alpha: float) -> str:
    """Convert a 6-digit hex colour + float alpha to a valid rgba() string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* Global */
  html, body, [data-testid="stAppViewContainer"] {{
      background-color: {NAVY};
      color: {WHITE};
  }}
  [data-testid="stHeader"] {{ background-color: {NAVY}; }}
  [data-testid="stSidebar"] {{
      background-color: {NAVY2};
      border-right: 1px solid {NAVY3};
  }}
  [data-testid="stSidebar"] * {{ color: {WHITE} !important; }}

  /* Metric cards */
  [data-testid="metric-container"] {{
      background: {NAVY2};
      border: 1px solid {NAVY3};
      border-radius: 10px;
      padding: 16px 20px;
  }}
  [data-testid="metric-container"] label {{
      color: {GREY} !important;
      font-size: 0.78rem !important;
      letter-spacing: 0.08em;
      text-transform: uppercase;
  }}
  [data-testid="metric-container"] [data-testid="stMetricValue"] {{
      color: {GOLD} !important;
      font-size: 2rem !important;
      font-weight: 700;
  }}

  /* Section headers */
  .section-title {{
      color: {GOLD};
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      border-bottom: 1px solid {NAVY3};
      padding-bottom: 6px;
      margin-bottom: 14px;
  }}

  /* Signal badges */
  .badge-long  {{ background:{GREEN_A13}; color:{GREEN}; border:1px solid {GREEN_A33};
                  border-radius:5px; padding:2px 10px; font-size:0.78rem; font-weight:700; }}
  .badge-short {{ background:{RED_A13};   color:{RED};   border:1px solid {RED_A33};
                  border-radius:5px; padding:2px 10px; font-size:0.78rem; font-weight:700; }}
  .badge-neutral {{ background:{GREY_A13}; color:{GREY}; border:1px solid {GREY_A27};
                    border-radius:5px; padding:2px 10px; font-size:0.78rem; }}

  /* Dataframe */
  [data-testid="stDataFrame"] {{ border: 1px solid {NAVY3}; border-radius: 8px; }}

  /* Sidebar sliders / selects */
  .stSlider [data-baseweb="slider"] {{ background: {NAVY3}; }}
  .stSelectbox div[data-baseweb="select"] > div {{
      background: {NAVY2} !important;
      border-color: {NAVY3} !important;
      color: {WHITE} !important;
  }}
  .stMultiSelect div[data-baseweb="select"] > div {{
      background: {NAVY2} !important;
      border-color: {NAVY3} !important;
  }}

  /* Divider */
  hr {{ border-color: {NAVY3}; }}
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
CSV_PATH = Path(__file__).parent / "condor_capital_results.csv"

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Signal"] = df["Signal"].fillna("Neutral").replace("", "Neutral")
    # Normalise column names that may vary between v1 and v2
    if "Val Metric" in df.columns:
        df = df.rename(columns={"Val Metric": "P/E"})          # treat EV/EBITDA as primary val
    numeric_cols = ["Rank","Mkt Cap (R$B)","P/E","ROE (%)","Ret 6M (%)","Ret 12M (%)",
                    "Value Score","Quality Score","Momentum Score","Composite"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

df_raw = load_data(CSV_PATH)

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='text-align:center;padding:10px 0 4px'>"
                f"<span style='font-size:2rem'>🦅</span><br>"
                f"<span style='color:{GOLD};font-weight:700;font-size:1.1rem;letter-spacing:0.06em'>CÓNDOR CAPITAL</span><br>"
                f"<span style='color:{GREY};font-size:0.72rem'>B3 Mid-Cap L/S Screener</span>"
                f"</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"<p class='section-title'>Filters</p>", unsafe_allow_html=True)

    signal_opts = ["All", "LONG", "SHORT", "Neutral"]
    signal_sel  = st.selectbox("Signal", signal_opts)

    sectors = sorted(df_raw["Sector"].dropna().unique().tolist())
    sector_sel = st.multiselect("Sector", sectors, default=sectors)

    min_comp = st.slider("Min Composite Score", 0, 100, 0, step=5)

    roe_min  = float(df_raw["ROE (%)"].min()) if "ROE (%)" in df_raw.columns else 0.0
    roe_max  = float(df_raw["ROE (%)"].max()) if "ROE (%)" in df_raw.columns else 100.0
    min_roe  = st.slider("Min ROE (%)", int(roe_min), int(roe_max), int(roe_min))

    st.markdown("---")
    st.markdown(f"<p style='color:{GREY};font-size:0.68rem;text-align:center'>"
                f"Data: Yahoo Finance via yfinance<br>Cross-check before trading.</p>",
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

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f"<h1 style='color:{GOLD};font-size:1.7rem;font-weight:800;letter-spacing:0.04em;margin-bottom:2px'>"
    f"🦅 Cóndor Capital — Quantamental Dashboard</h1>"
    f"<p style='color:{GREY};font-size:0.82rem;margin-top:0'>Brazilian Mid-Cap Long/Short | B3 Universe | Live data via Yahoo Finance</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Summary cards ─────────────────────────────────────────────────────────────
total   = len(df_raw)
longs   = int((df_raw["Signal"] == "LONG").sum())
shorts  = int((df_raw["Signal"] == "SHORT").sum())
avg_cmp = round(df_raw["Composite"].mean(), 1)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Stocks Analyzed",   total)
c2.metric("Long Signals",      longs,  delta="Top picks ↑", delta_color="normal")
c3.metric("Short Signals",     shorts, delta="Top picks ↓", delta_color="inverse")
c4.metric("Avg Composite",     avg_cmp)

st.markdown("<br>", unsafe_allow_html=True)

# ── Top 5 Longs / Shorts highlight ───────────────────────────────────────────
top_longs  = df_raw[df_raw["Signal"] == "LONG"].head(5)
top_shorts = df_raw[df_raw["Signal"] == "SHORT"].sort_values("Composite").head(5)

col_l, col_r = st.columns(2)

def signal_card(row, sig):
    colour = GREEN if sig == "LONG" else RED
    badge  = f"<span class='badge-{'long' if sig=='LONG' else 'short'}'>{sig}</span>"
    roe_str = f"{row['ROE (%)']:.0f}%" if pd.notna(row.get("ROE (%)")) else "—"
    pe_str  = f"{row['P/E']:.1f}x"     if pd.notna(row.get("P/E"))    else "—"
    r6_str  = f"{row['Ret 6M (%)']:+.0f}%" if pd.notna(row.get("Ret 6M (%)")) else "—"
    return f"""
    <div style='background:{NAVY2};border:1px solid {hex_rgba(colour,0.27)};border-left:3px solid {colour};
                border-radius:8px;padding:10px 14px;margin-bottom:8px'>
      <div style='display:flex;justify-content:space-between;align-items:center'>
        <span style='color:{colour};font-weight:800;font-size:1rem'>{row['Ticker']}</span>
        {badge}
      </div>
      <div style='color:{WHITE};font-size:0.82rem;margin:2px 0'>{row['Company']}</div>
      <div style='color:{GREY};font-size:0.74rem'>{row['Sector']}</div>
      <div style='display:flex;gap:14px;margin-top:6px'>
        <span style='color:{GREY};font-size:0.72rem'>P/E <span style='color:{WHITE}'>{pe_str}</span></span>
        <span style='color:{GREY};font-size:0.72rem'>ROE <span style='color:{WHITE}'>{roe_str}</span></span>
        <span style='color:{GREY};font-size:0.72rem'>6M <span style='color:{WHITE}'>{r6_str}</span></span>
        <span style='color:{GREY};font-size:0.72rem'>Score <span style='color:{GOLD};font-weight:700'>{row['Composite']:.1f}</span></span>
      </div>
    </div>"""

with col_l:
    st.markdown(f"<p class='section-title'>▲ Top 5 Long Ideas</p>", unsafe_allow_html=True)
    for _, row in top_longs.iterrows():
        st.markdown(signal_card(row, "LONG"), unsafe_allow_html=True)

with col_r:
    st.markdown(f"<p class='section-title'>▼ Top 5 Short Ideas</p>", unsafe_allow_html=True)
    for _, row in top_shorts.iterrows():
        st.markdown(signal_card(row, "SHORT"), unsafe_allow_html=True)

st.markdown("---")

# ── Chart row 1: Composite bar + Long vs Short comparison ────────────────────
st.markdown(f"<p class='section-title'>Charts</p>", unsafe_allow_html=True)

ch1, ch2 = st.columns(2)

def signal_color(s):
    return GREEN if s == "LONG" else (RED if s == "SHORT" else GREY)

with ch1:
    st.markdown(f"<p style='color:{GOLD};font-size:0.8rem;font-weight:600;margin-bottom:4px'>Composite Score by Ticker</p>", unsafe_allow_html=True)
    bar_df = df.sort_values("Composite", ascending=True)
    bar_df["color"] = bar_df["Signal"].apply(signal_color)
    fig_bar = go.Figure(go.Bar(
        x=bar_df["Composite"],
        y=bar_df["Ticker"],
        orientation="h",
        marker_color=bar_df["color"],
        text=bar_df["Composite"].round(1),
        textposition="outside",
        textfont=dict(color=WHITE, size=10),
        hovertemplate="<b>%{y}</b><br>Composite: %{x:.1f}<extra></extra>",
    ))
    fig_bar.update_layout(
        paper_bgcolor=NAVY2, plot_bgcolor=NAVY2,
        font=dict(color=WHITE, size=11),
        margin=dict(l=10, r=40, t=10, b=10),
        xaxis=dict(range=[0, 115], gridcolor=NAVY3, zeroline=False, color=GREY),
        yaxis=dict(gridcolor=NAVY3, color=WHITE),
        height=420,
        showlegend=False,
    )
    st.plotly_chart(fig_bar, width="stretch")

with ch2:
    st.markdown(f"<p style='color:{GOLD};font-size:0.8rem;font-weight:600;margin-bottom:4px'>Long vs Short — Factor Comparison</p>", unsafe_allow_html=True)
    grp = df_raw[df_raw["Signal"].isin(["LONG","SHORT"])].groupby("Signal")[
        ["Value Score","Quality Score","Momentum Score","Composite"]
    ].mean().reset_index()
    cats = ["Value Score","Quality Score","Momentum Score","Composite"]
    fig_radar = go.Figure()
    for _, row in grp.iterrows():
        clr      = GREEN if row["Signal"] == "LONG" else RED
        fill_clr = GREEN_A18 if row["Signal"] == "LONG" else RED_A18
        vals = [row[c] for c in cats] + [row[cats[0]]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals, theta=cats + [cats[0]],
            fill="toself", name=row["Signal"],
            line=dict(color=clr, width=2),
            fillcolor=fill_clr,
        ))
    fig_radar.update_layout(
        paper_bgcolor=NAVY2, plot_bgcolor=NAVY2,
        font=dict(color=WHITE, size=11),
        polar=dict(
            bgcolor=NAVY2,
            radialaxis=dict(range=[0,100], gridcolor=NAVY3, color=GREY, tickfont=dict(size=9)),
            angularaxis=dict(gridcolor=NAVY3, color=WHITE),
        ),
        legend=dict(bgcolor=NAVY2, bordercolor=NAVY3, font=dict(color=WHITE)),
        margin=dict(l=20, r=20, t=20, b=20),
        height=420,
    )
    st.plotly_chart(fig_radar, width="stretch")

# ── Chart row 2: Value vs Momentum scatter + ROE vs Composite ────────────────
ch3, ch4 = st.columns(2)

with ch3:
    st.markdown(f"<p style='color:{GOLD};font-size:0.8rem;font-weight:600;margin-bottom:4px'>Value Score vs Momentum Score</p>", unsafe_allow_html=True)
    sc_df = df.dropna(subset=["Value Score","Momentum Score"])
    sc_df["color"] = sc_df["Signal"].apply(signal_color)
    fig_sc1 = go.Figure()
    for sig, grp in sc_df.groupby("Signal"):
        clr = signal_color(sig)
        fig_sc1.add_trace(go.Scatter(
            x=grp["Value Score"], y=grp["Momentum Score"],
            mode="markers+text",
            name=sig,
            marker=dict(color=clr, size=11, line=dict(color=NAVY, width=1)),
            text=grp["Ticker"], textposition="top center",
            textfont=dict(color=WHITE, size=9),
            hovertemplate="<b>%{text}</b><br>Value: %{x:.1f}<br>Momentum: %{y:.1f}<extra></extra>",
        ))
    fig_sc1.add_hline(y=50, line_dash="dot", line_color=GREY, line_width=1)
    fig_sc1.add_vline(x=50, line_dash="dot", line_color=GREY, line_width=1)
    fig_sc1.update_layout(
        paper_bgcolor=NAVY2, plot_bgcolor=NAVY2,
        font=dict(color=WHITE, size=11),
        xaxis=dict(title="Value Score", gridcolor=NAVY3, zeroline=False, color=GREY, range=[-5,115]),
        yaxis=dict(title="Momentum Score", gridcolor=NAVY3, zeroline=False, color=GREY, range=[-5,115]),
        legend=dict(bgcolor=NAVY2, bordercolor=NAVY3, font=dict(color=WHITE)),
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
    )
    st.plotly_chart(fig_sc1, width="stretch")

with ch4:
    st.markdown(f"<p style='color:{GOLD};font-size:0.8rem;font-weight:600;margin-bottom:4px'>ROE (%) vs Composite Score</p>", unsafe_allow_html=True)
    sc2_df = df.dropna(subset=["ROE (%)","Composite"])
    fig_sc2 = go.Figure()
    for sig, grp in sc2_df.groupby("Signal"):
        clr = signal_color(sig)
        fig_sc2.add_trace(go.Scatter(
            x=grp["ROE (%)"], y=grp["Composite"],
            mode="markers+text",
            name=sig,
            marker=dict(color=clr, size=11, line=dict(color=NAVY, width=1)),
            text=grp["Ticker"], textposition="top center",
            textfont=dict(color=WHITE, size=9),
            hovertemplate="<b>%{text}</b><br>ROE: %{x:.1f}%<br>Composite: %{y:.1f}<extra></extra>",
        ))
    fig_sc2.update_layout(
        paper_bgcolor=NAVY2, plot_bgcolor=NAVY2,
        font=dict(color=WHITE, size=11),
        xaxis=dict(title="ROE (%)", gridcolor=NAVY3, zeroline=False, color=GREY),
        yaxis=dict(title="Composite Score", gridcolor=NAVY3, zeroline=False, color=GREY, range=[-5,115]),
        legend=dict(bgcolor=NAVY2, bordercolor=NAVY3, font=dict(color=WHITE)),
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
    )
    st.plotly_chart(fig_sc2, width="stretch")

st.markdown("---")

# ── Interactive table ─────────────────────────────────────────────────────────
st.markdown(f"<p class='section-title'>Full Universe — Interactive Table</p>", unsafe_allow_html=True)

table_cols = [c for c in ["Rank","Ticker","Company","Sector","Mkt Cap (R$B)","P/E",
                           "ROE (%)","Ret 6M (%)","Ret 12M (%)","Value Score",
                           "Quality Score","Momentum Score","Composite","Signal"]
              if c in df.columns]
display_df = df[table_cols].copy()

def colour_signal(val):
    if val == "LONG":
        return f"color: {GREEN}; font-weight: 700"
    if val == "SHORT":
        return f"color: {RED}; font-weight: 700"
    return f"color: {GREY}"

def colour_composite(val):
    if pd.isna(val):
        return ""
    if val >= 70:
        return f"color: {GREEN}; font-weight: 600"
    if val <= 30:
        return f"color: {RED}; font-weight: 600"
    return f"color: {WHITE}"

styled = (
    display_df.style
    .map(colour_signal,    subset=["Signal"])
    .map(colour_composite, subset=["Composite"])
    .format({
        "Mkt Cap (R$B)": "{:.1f}",
        "P/E":           "{:.1f}",
        "ROE (%)":       "{:.1f}",
        "Ret 6M (%)":    "{:+.1f}",
        "Ret 12M (%)":   "{:+.1f}",
        "Value Score":   "{:.1f}",
        "Quality Score": "{:.1f}",
        "Momentum Score":"{:.1f}",
        "Composite":     "{:.1f}",
    }, na_rep="—")
    .set_table_styles([
        {"selector": "thead th",
         "props": f"background-color:{NAVY3};color:{GOLD};font-size:0.75rem;"
                  f"text-transform:uppercase;letter-spacing:0.06em;padding:8px 12px;"},
        {"selector": "tbody td",
         "props": f"background-color:{NAVY2};color:{WHITE};font-size:0.82rem;padding:6px 12px;"},
        {"selector": "tbody tr:hover td",
         "props": f"background-color:{NAVY3} !important;"},
        {"selector": "table",
         "props": f"border-collapse:collapse;width:100%;border:1px solid {NAVY3};border-radius:8px;overflow:hidden"},
    ])
)

st.dataframe(display_df, width="stretch", height=480,
             column_config={
                 "Signal": st.column_config.TextColumn("Signal", width="small"),
                 "Composite": st.column_config.ProgressColumn(
                     "Composite", min_value=0, max_value=100, format="%.1f"),
                 "Ret 6M (%)": st.column_config.NumberColumn("6M Ret %", format="%.1f"),
                 "Ret 12M (%)": st.column_config.NumberColumn("12M Ret %", format="%.1f"),
             })

st.markdown("---")
st.markdown(
    f"<p style='color:{GREY};font-size:0.7rem;text-align:center'>"
    f"Cóndor Capital Screener · Data: Yahoo Finance · "
    f"Cross-check against Bloomberg / Economatica before trading.</p>",
    unsafe_allow_html=True,
)
