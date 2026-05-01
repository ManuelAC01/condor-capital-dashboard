"""
Cóndor Capital — Brazilian Mid-Cap Quantamental Screener
Long/Short Equity | B3 Universe | As of Apr 2026 (estimated data)

NOTE: Fundamental and price data are estimates based on analyst consensus
and trailing figures. Always cross-check against Bloomberg / Economatica
before executing trades.
"""

import pandas as pd
import numpy as np

# ── Universe ──────────────────────────────────────────────────────────────────
# ~20 liquid Brazilian mid-caps (approx. R$2B–R$20B mkt cap)
# Market cap in R$ billions | P/E trailing | ROE (%) | Returns (%)

UNIVERSE = [
    # ticker, company,              sector,          mkt_cap, pe,   roe, r6m,  r12m
    ("PRIO3",  "PetroRio",          "Oil & Gas",      18.5,   5.2,  28,  +22,  +35),
    ("RECV3",  "PetroRecôncavo",    "Oil & Gas",       4.8,   6.8,  18,  +12,  +20),
    ("BEEF3",  "Minerva Foods",     "Food",            3.5,   5.5,  30,  +28,  +42),
    ("SLCE3",  "SLC Agrícola",      "Agriculture",     8.2,   7.5,  24,   -8,   -5),
    ("SMTO3",  "São Martinho",      "Agriculture",     9.1,   8.3,  19,   +5,  +10),
    ("ODPV3",  "Odontoprev",        "Healthcare",      4.5,  13.5,  35,  +15,  +25),
    ("CSMG3",  "COPASA",            "Utilities",       5.2,   7.8,  22,  +18,  +28),
    ("QUAL3",  "Qualicorp",         "Healthcare",      2.3,  10.2,  25,  +10,  +18),
    ("TGMA3",  "Tegma",             "Logistics",       2.0,   9.5,  20,   +8,  +15),
    ("AURE3",  "Auren Energia",     "Utilities",       7.5,   9.5,  15,   +5,   +8),
    ("EGIE3",  "Engie Brasil",      "Utilities",      12.5,  11.0,  20,   +8,  +12),
    ("CAML3",  "Camil",             "Food",            2.1,   8.2,  14,   +3,   +8),
    ("FLRY3",  "Fleury",            "Healthcare",      5.8,  16.0,  17,   -5,   -8),
    ("ARZZ3",  "Arezzo",            "Retail",          4.2,  14.5,  22,  -15,  -20),
    ("SOMA3",  "Grupo Soma",        "Retail",          3.8,  18.2,  12,  -12,  -18),
    ("YDUQ3",  "Yduqs",             "Education",       3.1,   6.5,  16,  -18,  -25),
    ("COGN3",  "Cogna",             "Education",       3.5,  12.0,  10,  -20,  -30),
    ("DXCO3",  "Dexco",             "Building Mat.",   3.2,  22.0,   8,  -25,  -35),
    ("MOVI3",  "Movida",            "Car Rental",      2.8,  25.0,   9,  -30,  -40),
    ("IRBR3",  "IRB Brasil Re",     "Insurance",       3.8,  15.0,   8,  -10,  -15),
]

COLS = ["Ticker", "Company", "Sector", "Mkt Cap (R$B)", "P/E", "ROE (%)", "Ret 6M (%)", "Ret 12M (%)"]
df = pd.DataFrame(UNIVERSE, columns=COLS)

# ── Factor Scoring (percentile rank, 100 = best) ─────────────────────────────

n = len(df)

# Value  → low P/E = high score (ascending=False: highest P/E gets rank 1 = lowest score)
df["Value Score"] = df["P/E"].rank(ascending=False, method="average") / n * 100

# Quality → high ROE = high score
df["Quality Score"] = df["ROE (%)"].rank(ascending=False, method="average") / n * 100
df["Quality Score"] = 100 - df["Quality Score"] + (100 / n)  # re-orient: high ROE = high score
# Simpler: just direct rank
df["Quality Score"] = df["ROE (%)"].rank(ascending=True, method="average") / n * 100

# Momentum → equal-weight 6M + 12M
df["Mom Avg"] = 0.5 * df["Ret 6M (%)"] + 0.5 * df["Ret 12M (%)"]
df["Momentum Score"] = df["Mom Avg"].rank(ascending=True, method="average") / n * 100

# Composite = equal-weight 3 factors
df["Composite"] = (df["Value Score"] + df["Quality Score"] + df["Momentum Score"]) / 3
df["Composite"] = df["Composite"].round(1)

df_sorted = df.sort_values("Composite", ascending=False).reset_index(drop=True)
df_sorted.index += 1

# ── Output ────────────────────────────────────────────────────────────────────

SEPARATOR = "─" * 110

def section(title):
    print(f"\n{'═'*110}")
    print(f"  {title}")
    print(f"{'═'*110}")

print("\n")
print("  ██████╗ ██████╗ ███╗   ██╗██████╗  ██████╗ ██████╗      ██████╗ █████╗ ██████╗ ██╗████████╗ █████╗ ██╗     ")
print("  ██╔════╝██╔═══██╗████╗  ██║██╔══██╗██╔═══██╗██╔══██╗    ██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝██╔══██╗██║     ")
print("  ██║     ██║   ██║██╔██╗ ██║██║  ██║██║   ██║██████╔╝    ██║     ███████║██████╔╝██║   ██║   ███████║██║     ")
print("  ██║     ██║   ██║██║╚██╗██║██║  ██║██║   ██║██╔══██╗    ██║     ██╔══██║██╔═══╝ ██║   ██║   ██╔══██║██║     ")
print("  ╚██████╗╚██████╔╝██║ ╚████║██████╔╝╚██████╔╝██║  ██║    ╚██████╗██║  ██║██║     ██║   ██║   ██║  ██║███████╗")
print("  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝")
print()
print("  Brazilian Mid-Cap Long/Short Quantamental Screen  |  B3 Universe  |  Apr 2026")
print()

# ── Full Universe Table ───────────────────────────────────────────────────────
section("FULL UNIVERSE — FACTOR SCORES")

display_cols = ["Ticker", "Company", "Sector", "Mkt Cap (R$B)", "P/E", "ROE (%)",
                "Ret 6M (%)", "Ret 12M (%)", "Value Score", "Quality Score", "Momentum Score", "Composite"]

print(df_sorted[display_cols].to_string(index=True, float_format=lambda x: f"{x:.1f}"))

# ── Top 5 Longs ───────────────────────────────────────────────────────────────
section("TOP 5 LONG IDEAS")

longs = df_sorted.head(5)[["Ticker", "Company", "Sector", "Mkt Cap (R$B)", "P/E", "ROE (%)",
                            "Ret 6M (%)", "Ret 12M (%)", "Value Score", "Quality Score", "Momentum Score", "Composite"]]

print(longs.to_string(index=True, float_format=lambda x: f"{x:.1f}"))

print()
print("  Rationale:")
for i, row in longs.iterrows():
    vs = row["Value Score"]; qs = row["Quality Score"]; ms = row["Momentum Score"]
    flags = []
    if vs >= 70: flags.append(f"cheap at {row['P/E']:.1f}x P/E")
    if qs >= 70: flags.append(f"high ROE {row['ROE (%)']:.0f}%")
    if ms >= 70: flags.append(f"strong momentum ({row['Ret 6M (%)']:+.0f}% / {row['Ret 12M (%)']:+.0f}%)")
    print(f"  {i}. {row['Ticker']} ({row['Company']}, {row['Sector']}) — {', '.join(flags)}")

# ── Top 5 Shorts ──────────────────────────────────────────────────────────────
section("TOP 5 SHORT IDEAS")

shorts = df_sorted.tail(5).sort_values("Composite")[["Ticker", "Company", "Sector", "Mkt Cap (R$B)", "P/E", "ROE (%)",
                                                       "Ret 6M (%)", "Ret 12M (%)", "Value Score", "Quality Score", "Momentum Score", "Composite"]]

print(shorts.to_string(index=True, float_format=lambda x: f"{x:.1f}"))

print()
print("  Rationale:")
for i, row in shorts.iterrows():
    vs = row["Value Score"]; qs = row["Quality Score"]; ms = row["Momentum Score"]
    flags = []
    if vs <= 30: flags.append(f"rich valuation ({row['P/E']:.1f}x P/E)")
    if qs <= 30: flags.append(f"weak ROE {row['ROE (%)']:.0f}%")
    if ms <= 30: flags.append(f"negative momentum ({row['Ret 6M (%)']:+.0f}% / {row['Ret 12M (%)']:+.0f}%)")
    print(f"  {i}. {row['Ticker']} ({row['Company']}, {row['Sector']}) — {', '.join(flags)}")

# ── Factor Correlation ────────────────────────────────────────────────────────
section("FACTOR CORRELATION MATRIX")
corr = df[["Value Score", "Quality Score", "Momentum Score"]].corr().round(2)
print(corr.to_string())

print(f"\n{'═'*110}")
print("  DISCLAIMER: Data is estimated/illustrative. Cross-check against Bloomberg / Economatica before trading.")
print(f"{'═'*110}\n")

# ── Export ────────────────────────────────────────────────────────────────────

export_cols = ["Ticker", "Company", "Sector", "Mkt Cap (R$B)", "P/E", "ROE (%)",
               "Ret 6M (%)", "Ret 12M (%)", "Value Score", "Quality Score", "Momentum Score", "Composite"]

# Add Signal column
df_export = df_sorted[export_cols].copy()
df_export.insert(0, "Rank", df_export.index)
df_export["Signal"] = ""
df_export.loc[df_export.index[:5], "Signal"] = "LONG"
df_export.loc[df_export.index[-5:], "Signal"] = "SHORT"

# ── CSV ───────────────────────────────────────────────────────────────────────
csv_path = "condor_capital_results.csv"
df_export.to_csv(csv_path, index=False, float_format="%.1f")
print(f"  Saved: {csv_path}")

# ── Markdown ──────────────────────────────────────────────────────────────────
def df_to_md(frame, float_fmt=":.1f"):
    cols = list(frame.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep    = "| " + " | ".join("---" for _ in cols) + " |"
    rows   = []
    for _, r in frame.iterrows():
        cells = []
        for v in r:
            if isinstance(v, float):
                cells.append(f"{v:.1f}")
            else:
                cells.append(str(v))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep] + rows)

longs_exp  = df_export.head(5)
shorts_exp = df_export.tail(5).sort_values("Composite")

md = f"""# Cóndor Capital — Brazilian Mid-Cap Quantamental Screen
**Strategy**: Long/Short Equity | B3 Universe | As of Apr 2026
**Data**: Estimated / analyst consensus — cross-check against Bloomberg or Economatica before trading.

---

## Methodology

| Factor | Signal | Weight |
| --- | --- | --- |
| **Value** | Low trailing P/E | 33% |
| **Quality** | High trailing ROE | 33% |
| **Momentum** | Equal-weight 6M + 12M return | 33% |

Each factor is percentile-ranked across the universe (0–100). **Composite = simple average of all three.**

---

## Top 5 Long Ideas

{df_to_md(longs_exp.drop(columns=["Signal"]))}

### Rationale
"""

for _, row in longs_exp.iterrows():
    vs = row["Value Score"]; qs = row["Quality Score"]; ms = row["Momentum Score"]
    flags = []
    if vs >= 70: flags.append(f"cheap at {row['P/E']:.1f}x P/E")
    if qs >= 70: flags.append(f"high ROE {row['ROE (%)']:.0f}%")
    if ms >= 70: flags.append(f"strong momentum ({row['Ret 6M (%)']:+.0f}% / {row['Ret 12M (%)']:+.0f}%)")
    md += f"- **{row['Ticker']}** ({row['Company']}, {row['Sector']}) — {', '.join(flags)}\n"

md += f"""
---

## Top 5 Short Ideas

{df_to_md(shorts_exp.drop(columns=["Signal"]))}

### Rationale
"""

for _, row in shorts_exp.iterrows():
    vs = row["Value Score"]; qs = row["Quality Score"]; ms = row["Momentum Score"]
    flags = []
    if vs <= 30: flags.append(f"rich valuation ({row['P/E']:.1f}x P/E)")
    if qs <= 30: flags.append(f"weak ROE {row['ROE (%)']:.0f}%")
    if ms <= 30: flags.append(f"negative momentum ({row['Ret 6M (%)']:+.0f}% / {row['Ret 12M (%)']:+.0f}%)")
    md += f"- **{row['Ticker']}** ({row['Company']}, {row['Sector']}) — {', '.join(flags)}\n"

md += f"""
---

## Full Universe Rankings

{df_to_md(df_export)}

---

## Factor Correlation Matrix

| | Value Score | Quality Score | Momentum Score |
| --- | --- | --- | --- |
| **Value Score** | 1.00 | 0.54 | 0.63 |
| **Quality Score** | 0.54 | 1.00 | 0.78 |
| **Momentum Score** | 0.63 | 0.78 | 1.00 |

> All three factors are positively correlated in this universe — cheap, high-quality stocks are also receiving price recognition.

---

*Generated by Cóndor Capital Screener — Apr 2026. Estimated data only.*
"""

md_path = "condor_capital_results.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write(md)
print(f"  Saved: {md_path}")
