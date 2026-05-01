# 🦅 Cóndor Capital — B3 Quantamental Screener

Interactive dashboard for a Brazilian mid-cap long/short equity strategy running on the B3 universe.

## What it does

The screener ranks ~20 liquid Brazilian mid-cap stocks (R$2B–R$40B market cap) across three factors:

| Factor | Signal | Weight |
|---|---|---|
| **Value** | EV/EBITDA (preferred) or trailing P/E | 35% |
| **Quality** | Trailing Return on Equity (ROE) | 30% |
| **Momentum** | Equal-weight 6M + 12M price return | 35% |

Each factor is percentile-ranked 0–100 across the universe. The composite score determines the top 5 **LONG** and top 5 **SHORT** signals.

The dashboard adds:
- RSI-14 overbought/oversold flag on every signal
- Analyst consensus price target upside (informational)
- ADTV liquidity flag (names below R$5M flagged)

## Running locally

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/condor-capital.git
cd condor-capital

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) refresh live data from Yahoo Finance
python screener.py

# 4. Launch the dashboard
streamlit run dashboard.py
```

Open **http://localhost:8501** in your browser.

## Files

| File | Description |
|---|---|
| `screener.py` | Pulls live B3 data via yfinance, scores factors, exports CSV + Markdown |
| `dashboard.py` | Streamlit dashboard reading from the CSV |
| `condor_capital_results.csv` | Latest screener output (committed as snapshot) |
| `requirements.txt` | Python dependencies |

## Data

- **Source:** Yahoo Finance via `yfinance` (no API key required)
- **Universe:** ~20 liquid B3 mid-caps with `.SA` suffix tickers
- **Frequency:** Re-run `screener.py` to refresh

> ⚠️ Data is for research purposes only. Always cross-check against Bloomberg or Economatica before executing trades.

## Deployment on Streamlit Cloud

1. Push this repo to GitHub (make sure `condor_capital_results.csv` is committed)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `dashboard.py`
5. Click **Deploy**

No secrets or environment variables required.
