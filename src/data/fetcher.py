"""
Data fetching layer using yfinance (primary) and nsepython (NSE-specific data).
All results are cached to reduce API calls during dashboard interactions.
"""
import os
import warnings
import logging
import datetime
from functools import lru_cache

import numpy as np
import pandas as pd
import yfinance as yf

from src.data.stocks import SECTOR_INDICES, NIFTY50, SENSEX30, NIFTY500

warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# Simple in-memory TTL cache
_cache: dict = {}


def _cached(key: str, ttl: int, fn):
    now = datetime.datetime.utcnow()
    if key in _cache:
        value, ts = _cache[key]
        if (now - ts).total_seconds() < ttl:
            return value
    value = fn()
    _cache[key] = (value, now)
    return value


# ---------------------------------------------------------------------------
# Stock price & OHLCV data
# ---------------------------------------------------------------------------

PERIOD_MAP = {
    "1D": ("1d", "5m"),
    "1W": ("5d", "15m"),
    "1M": ("1mo", "1h"),
    "3M": ("3mo", "1d"),
    "6M": ("6mo", "1d"),
    "1Y": ("1y", "1d"),
    "5Y": ("5y", "1wk"),
}


def get_ticker_symbol(symbol: str, exchange: str = "NSE") -> str:
    """Convert plain symbol to yfinance format."""
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol
    suffix = ".NS" if exchange == "NSE" else ".BO"
    return f"{symbol}{suffix}"


def get_stock_data(symbol: str, exchange: str = "NSE", period: str = "3M") -> pd.DataFrame:
    """Fetch OHLCV data. Returns empty DataFrame on failure."""
    ticker = get_ticker_symbol(symbol, exchange)
    yf_period, yf_interval = PERIOD_MAP.get(period, ("3mo", "1d"))
    cache_key = f"ohlcv_{ticker}_{period}"
    ttl = 60 if period == "1D" else 300

    def fetch():
        try:
            df = yf.download(ticker, period=yf_period, interval=yf_interval,
                             progress=False, auto_adjust=True)
            if df.empty:
                return pd.DataFrame()
            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.index = pd.to_datetime(df.index)
            df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
            return df
        except Exception:
            return pd.DataFrame()

    return _cached(cache_key, ttl, fetch)


def get_stock_info(symbol: str, exchange: str = "NSE") -> dict:
    """Fetch fundamental info (P/E, market cap, 52w high/low, etc.)."""
    ticker = get_ticker_symbol(symbol, exchange)
    cache_key = f"info_{ticker}"

    def fetch():
        try:
            t = yf.Ticker(ticker)
            info = t.info or {}
            return {
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "eps": info.get("trailingEps"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "week52_high": info.get("fiftyTwoWeekHigh"),
                "week52_low": info.get("fiftyTwoWeekLow"),
                "avg_volume": info.get("averageVolume"),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "previous_close": info.get("previousClose"),
                "open_price": info.get("open"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("volume"),
            }
        except Exception:
            return {}

    return _cached(cache_key, 120, fetch)


def get_current_price(symbol: str, exchange: str = "NSE") -> dict:
    """Fast fetch for current price and day change."""
    ticker = get_ticker_symbol(symbol, exchange)
    cache_key = f"price_{ticker}"

    def fetch():
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            price = getattr(info, "last_price", None) or getattr(info, "previous_close", None)
            prev_close = getattr(info, "previous_close", None)
            change = (price - prev_close) if price and prev_close else 0
            pct_change = (change / prev_close * 100) if prev_close else 0
            return {
                "price": round(price, 2) if price else None,
                "change": round(change, 2),
                "pct_change": round(pct_change, 2),
            }
        except Exception:
            return {"price": None, "change": 0, "pct_change": 0}

    return _cached(cache_key, 60, fetch)


# ---------------------------------------------------------------------------
# Market indices
# ---------------------------------------------------------------------------

def get_index_quotes() -> dict:
    """Fetch all sector indices. Returns dict of name -> {price, change, pct_change}."""
    cache_key = "index_quotes"

    def fetch():
        result = {}
        tickers = list(SECTOR_INDICES.values())
        names = list(SECTOR_INDICES.keys())
        try:
            data = yf.download(tickers, period="2d", interval="1d",
                               progress=False, auto_adjust=True, group_by="ticker")
            for name, ticker in zip(names, tickers):
                try:
                    if len(tickers) == 1:
                        df = data
                    else:
                        df = data[ticker] if ticker in data.columns.get_level_values(0) else pd.DataFrame()
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    if df.empty or len(df) < 2:
                        result[name] = {"price": None, "change": 0, "pct_change": 0}
                        continue
                    close = df["Close"].dropna()
                    today = float(close.iloc[-1])
                    yesterday = float(close.iloc[-2])
                    change = today - yesterday
                    pct = (change / yesterday) * 100
                    result[name] = {
                        "price": round(today, 2),
                        "change": round(change, 2),
                        "pct_change": round(pct, 2),
                    }
                except Exception:
                    result[name] = {"price": None, "change": 0, "pct_change": 0}
        except Exception:
            for name in names:
                result[name] = {"price": None, "change": 0, "pct_change": 0}
        return result

    return _cached(cache_key, 90, fetch)


# ---------------------------------------------------------------------------
# Top movers
# ---------------------------------------------------------------------------

def get_top_movers(exchange: str = "NSE", n: int = 10) -> dict:
    """Return top n gainers and losers for the given exchange."""
    cache_key = f"movers_{exchange}_{n}"

    def fetch():
        stocks = NIFTY50 if exchange == "NSE" else SENSEX30
        symbols = [s["symbol"] for s in stocks]
        name_map = {s["symbol"]: s["name"] for s in stocks}
        results = []
        try:
            data = yf.download(symbols, period="2d", interval="1d",
                               progress=False, auto_adjust=True, group_by="ticker")
            for sym in symbols:
                try:
                    if len(symbols) == 1:
                        df = data
                    else:
                        df = data[sym] if sym in data.columns.get_level_values(0) else pd.DataFrame()
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    close = df["Close"].dropna()
                    if len(close) < 2:
                        continue
                    today = float(close.iloc[-1])
                    yesterday = float(close.iloc[-2])
                    pct = ((today - yesterday) / yesterday) * 100
                    results.append({
                        "symbol": sym.replace(".NS", "").replace(".BO", ""),
                        "full_symbol": sym,
                        "name": name_map.get(sym, sym),
                        "price": round(today, 2),
                        "pct_change": round(pct, 2),
                    })
                except Exception:
                    continue
        except Exception:
            pass
        results.sort(key=lambda x: x["pct_change"], reverse=True)
        return {
            "gainers": results[:n],
            "losers": results[-n:][::-1],
        }

    return _cached(cache_key, 120, fetch)


# ---------------------------------------------------------------------------
# Screener data
# ---------------------------------------------------------------------------

def get_screener_data(symbols_list: list) -> list:
    """Batch fetch price + basic metrics for a list of symbols."""
    cache_key = f"screener_{'_'.join(symbols_list[:5])}_{len(symbols_list)}"

    def fetch():
        results = []
        try:
            data = yf.download(symbols_list, period="5d", interval="1d",
                               progress=False, auto_adjust=True, group_by="ticker")
            for sym in symbols_list:
                try:
                    if len(symbols_list) == 1:
                        df = data
                    else:
                        df = data[sym] if sym in data.columns.get_level_values(0) else pd.DataFrame()
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    close = df["Close"].dropna()
                    if len(close) < 2:
                        continue
                    vol = df["Volume"].dropna()
                    today = float(close.iloc[-1])
                    yesterday = float(close.iloc[-2])
                    week_ago = float(close.iloc[0]) if len(close) >= 5 else yesterday
                    day_pct = ((today - yesterday) / yesterday) * 100
                    week_pct = ((today - week_ago) / week_ago) * 100
                    results.append({
                        "symbol": sym,
                        "price": round(today, 2),
                        "day_pct": round(day_pct, 2),
                        "week_pct": round(week_pct, 2),
                        "volume": int(vol.iloc[-1]) if len(vol) else 0,
                    })
                except Exception:
                    continue
        except Exception:
            pass
        return results

    return _cached(cache_key, 180, fetch)


def format_market_cap(value) -> str:
    if value is None:
        return "N/A"
    if value >= 1e12:
        return f"₹{value/1e12:.2f}T"
    if value >= 1e9:
        return f"₹{value/1e9:.2f}B"
    if value >= 1e7:
        return f"₹{value/1e7:.2f}Cr"
    return f"₹{value:,.0f}"
