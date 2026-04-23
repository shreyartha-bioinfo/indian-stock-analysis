# StockDash IN — Indian Stock Market Analysis Dashboard

A professional, browser-based dashboard for BSE and NSE stock market analysis with live charts, 30+ technical indicators, and AI-powered buy/sell/hold recommendations.

## Features

### Market Overview (Home)
- Live index cards: NIFTY 50, SENSEX, NIFTY Bank, NIFTY IT, NIFTY Pharma, NIFTY Auto, FMCG, Metal, Energy, Realty
- Top 10 Gainers and Losers (NSE)
- Interactive sector heatmap (treemap)
- Auto-refresh every 60 seconds

### Stock Analysis
- Search any NSE or BSE stock (NIFTY 500 + SENSEX 30)
- Exchange toggle: NSE / BSE
- Time period: 1D · 1W · 1M · 3M · 6M · 1Y · 5Y
- Chart types: **Candlestick** · OHLC · Line · Area
- **30+ technical indicators** grouped by category:

| Category | Indicators |
|----------|-----------|
| **Trend** | SMA (20/50/200), EMA (9/21/55), Bollinger Bands, VWAP, Ichimoku Cloud, SuperTrend, Parabolic SAR |
| **Momentum** | RSI (14), MACD, Stochastic, CCI, Williams %R, ROC, TSI |
| **Volatility** | ATR, Keltner Channels, Donchian Channels |
| **Volume** | OBV, MFI, CMF, A/D Line, Force Index |
| **Oscillators** | ADX + DI±, Aroon, DPO, TRIX |

- Stock info bar: price, change, 52W hi/lo, market cap, P/E, beta
- **Buy/Sell/Hold recommendation** card with signal strength bar

### Stock Screener
- Universes: NIFTY 50 · NIFTY 500 · SENSEX 30
- Filter by sector, sort by day%, week%, price, volume
- Advance/Decline summary badges
- Auto-refresh every 5 minutes

## Data Sources

| Source | Used For | Latency |
|--------|----------|---------|
| Yahoo Finance (`yfinance`) | OHLCV, stock info, indices | 15-min delayed |
| `nsepython` | NSE market data | Near real-time |
| Hardcoded lists | Ticker metadata | Static |

> Data is 15-minute delayed during market hours per Yahoo Finance policy.
> **This tool is for educational purposes only — not financial advice.**

## Quick Start (Local)

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd indian-stock-analysis

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy env file
cp .env.example .env

# 5. Run the dashboard
python app.py
```

Open **http://localhost:8050** in your browser.

## Deploy to Render (Free Tier)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repository
4. Settings are auto-detected from `render.yaml`:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app:server --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. Click **Deploy**

## Deploy to Railway

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

## Project Structure

```
indian-stock-analysis/
├── app.py                   # Dash app entry point (import this for gunicorn)
├── requirements.txt         # Python dependencies
├── Procfile                 # Render/Railway start command
├── render.yaml              # Render deploy config
├── .env.example             # Environment variable template
├── src/
│   ├── data/
│   │   ├── fetcher.py       # yfinance + nsepython data fetching with TTL cache
│   │   └── stocks.py        # NIFTY50, NIFTY500, SENSEX30 ticker lists
│   ├── analysis/
│   │   ├── indicators.py    # 30+ technical indicators (pandas-ta)
│   │   └── recommender.py   # Weighted multi-indicator signal scoring
│   └── charts/
│       └── price_chart.py   # Plotly chart builders (candlestick, OHLC, line, area)
├── pages/
│   ├── market_overview.py   # Page 1: indices, gainers, sector heatmap
│   ├── stock_analysis.py    # Page 2: full chart + indicators + recommendation
│   └── screener.py          # Page 3: sortable stock screener table
└── assets/
    └── style.css            # Dark Bloomberg-style theme
```

## Requirements

- Python 3.10+
- See `requirements.txt` for all dependencies

## License

MIT License — © shreyartha-bioinfo 2026
