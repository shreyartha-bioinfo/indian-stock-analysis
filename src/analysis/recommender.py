"""
Multi-indicator signal scoring engine for Buy/Sell/Hold recommendations.
Each signal returns a score: +1 (bullish), 0 (neutral), -1 (bearish).
"""
import pandas as pd
import numpy as np
from src.analysis.indicators import add_indicators


def _last(series: pd.Series, n: int = 1):
    """Return last n values or None if unavailable."""
    clean = series.dropna()
    if len(clean) < n:
        return None
    return clean.iloc[-n] if n == 1 else clean.iloc[-n:]


def score_rsi(df: pd.DataFrame) -> tuple:
    """RSI: oversold=buy, overbought=sell."""
    if "RSI" not in df.columns:
        return 0, "RSI: N/A"
    val = _last(df["RSI"])
    if val is None:
        return 0, "RSI: N/A"
    if val < 30:
        return 1, f"RSI: {val:.1f} — Oversold (Buy)"
    if val > 70:
        return -1, f"RSI: {val:.1f} — Overbought (Sell)"
    return 0, f"RSI: {val:.1f} — Neutral"


def score_macd(df: pd.DataFrame) -> tuple:
    """MACD crossover detection."""
    if "MACD" not in df.columns or "MACD_signal" not in df.columns:
        return 0, "MACD: N/A"
    macd_now = _last(df["MACD"])
    signal_now = _last(df["MACD_signal"])
    macd_prev = _last(df["MACD"], 2)
    signal_prev = _last(df["MACD_signal"], 2)
    if any(v is None for v in [macd_now, signal_now, macd_prev, signal_prev]):
        # Fallback: simple position
        if macd_now is not None and signal_now is not None:
            if macd_now > signal_now:
                return 0.5, f"MACD: {macd_now:.4f} above signal (Mildly Bullish)"
            return -0.5, f"MACD: {macd_now:.4f} below signal (Mildly Bearish)"
        return 0, "MACD: N/A"
    if macd_prev < signal_prev and macd_now > signal_now:
        return 1, f"MACD: Bullish crossover"
    if macd_prev > signal_prev and macd_now < signal_now:
        return -1, f"MACD: Bearish crossover"
    if macd_now > signal_now:
        return 0.5, f"MACD: {macd_now:.4f} above signal"
    return -0.5, f"MACD: {macd_now:.4f} below signal"


def score_sma200(df: pd.DataFrame) -> tuple:
    """Price relative to SMA200."""
    if "SMA_200" not in df.columns:
        return 0, "SMA200: N/A"
    price = _last(df["Close"])
    sma = _last(df["SMA_200"])
    if price is None or sma is None:
        return 0, "SMA200: N/A"
    if price > sma:
        return 1, f"Price ({price:.2f}) above SMA200 ({sma:.2f}) — Bullish"
    return -1, f"Price ({price:.2f}) below SMA200 ({sma:.2f}) — Bearish"


def score_sma50(df: pd.DataFrame) -> tuple:
    """Price relative to SMA50."""
    if "SMA_50" not in df.columns:
        return 0, "SMA50: N/A"
    price = _last(df["Close"])
    sma = _last(df["SMA_50"])
    if price is None or sma is None:
        return 0, "SMA50: N/A"
    if price > sma:
        return 0.5, f"Price ({price:.2f}) above SMA50 ({sma:.2f})"
    return -0.5, f"Price ({price:.2f}) below SMA50 ({sma:.2f})"


def score_stochastic(df: pd.DataFrame) -> tuple:
    """Stochastic %K: oversold=buy, overbought=sell."""
    if "Stoch_K" not in df.columns:
        return 0, "Stochastic: N/A"
    k = _last(df["Stoch_K"])
    if k is None:
        return 0, "Stochastic: N/A"
    if k < 20:
        return 1, f"Stochastic K: {k:.1f} — Oversold (Buy)"
    if k > 80:
        return -1, f"Stochastic K: {k:.1f} — Overbought (Sell)"
    return 0, f"Stochastic K: {k:.1f} — Neutral"


def score_bollinger(df: pd.DataFrame) -> tuple:
    """Price touching Bollinger Bands."""
    if "BB_upper" not in df.columns or "BB_lower" not in df.columns:
        return 0, "Bollinger Bands: N/A"
    price = _last(df["Close"])
    upper = _last(df["BB_upper"])
    lower = _last(df["BB_lower"])
    if any(v is None for v in [price, upper, lower]):
        return 0, "Bollinger Bands: N/A"
    if price <= lower:
        return 1, f"Price at lower BB ({lower:.2f}) — Possible reversal up"
    if price >= upper:
        return -1, f"Price at upper BB ({upper:.2f}) — Possible reversal down"
    return 0, f"Price ({price:.2f}) inside Bollinger Bands"


def score_adx(df: pd.DataFrame) -> tuple:
    """ADX with DI+/DI- for trend direction."""
    if "ADX" not in df.columns:
        return 0, "ADX: N/A"
    adx = _last(df["ADX"])
    di_plus = _last(df.get("DI_plus", pd.Series(dtype=float)))
    di_minus = _last(df.get("DI_minus", pd.Series(dtype=float)))
    if adx is None:
        return 0, "ADX: N/A"
    if adx > 25:
        if di_plus is not None and di_minus is not None:
            if di_plus > di_minus:
                return 1, f"ADX: {adx:.1f} strong trend, DI+ ({di_plus:.1f}) > DI- — Bullish"
            return -1, f"ADX: {adx:.1f} strong trend, DI- ({di_minus:.1f}) > DI+ — Bearish"
        return 0.5, f"ADX: {adx:.1f} — Strong trend"
    return 0, f"ADX: {adx:.1f} — Weak/No trend"


def score_cci(df: pd.DataFrame) -> tuple:
    """CCI: below -100=buy, above +100=sell."""
    if "CCI" not in df.columns:
        return 0, "CCI: N/A"
    val = _last(df["CCI"])
    if val is None:
        return 0, "CCI: N/A"
    if val < -100:
        return 1, f"CCI: {val:.1f} — Oversold (Buy)"
    if val > 100:
        return -1, f"CCI: {val:.1f} — Overbought (Sell)"
    return 0, f"CCI: {val:.1f} — Neutral"


def score_obv(df: pd.DataFrame) -> tuple:
    """OBV trending direction over last 5 days."""
    if "OBV" not in df.columns:
        return 0, "OBV: N/A"
    recent = df["OBV"].dropna().tail(5)
    if len(recent) < 5:
        return 0, "OBV: Insufficient data"
    slope = np.polyfit(range(len(recent)), recent.values, 1)[0]
    if slope > 0:
        return 0.5, "OBV: Rising — Volume confirms uptrend"
    return -0.5, "OBV: Falling — Volume confirms downtrend"


def score_supertrend(df: pd.DataFrame) -> tuple:
    """SuperTrend direction."""
    if "SuperTrend_dir" not in df.columns:
        return 0, "SuperTrend: N/A"
    direction = _last(df["SuperTrend_dir"])
    if direction is None:
        return 0, "SuperTrend: N/A"
    if direction == 1:
        return 1, "SuperTrend: Bullish"
    if direction == -1:
        return -1, "SuperTrend: Bearish"
    return 0, "SuperTrend: Neutral"


# Weighted scoring: more reliable indicators carry more weight
SCORERS = [
    (score_rsi, 1.5),
    (score_macd, 1.5),
    (score_sma200, 1.0),
    (score_sma50, 0.75),
    (score_stochastic, 1.0),
    (score_bollinger, 1.0),
    (score_adx, 1.0),
    (score_cci, 0.75),
    (score_obv, 0.75),
    (score_supertrend, 1.0),
]

MAX_POSSIBLE_SCORE = sum(weight for _, weight in SCORERS)


def generate_recommendation(df: pd.DataFrame) -> dict:
    """
    Compute overall Buy/Sell/Hold signal from all indicators.
    Returns {signal, strength (0-100), raw_score, signals: list of detail strings}.
    """
    if df.empty:
        return {"signal": "N/A", "strength": 0, "raw_score": 0, "signals": []}

    required_keys = ["sma", "ema", "bb", "rsi", "macd", "stochastic", "cci", "obv", "adx", "supertrend"]
    df = add_indicators(df, required_keys)

    total_score = 0.0
    details = []

    for scorer_fn, weight in SCORERS:
        try:
            score, label = scorer_fn(df)
            total_score += score * weight
            details.append({"label": label, "score": score})
        except Exception:
            pass

    # Normalize to [-100, +100]
    normalized = (total_score / MAX_POSSIBLE_SCORE) * 100

    # Determine signal: thresholds at ±25
    if normalized >= 25:
        signal = "BUY"
        color = "#00ff88"
    elif normalized <= -25:
        signal = "SELL"
        color = "#ff4444"
    else:
        signal = "HOLD"
        color = "#ffcc00"

    # Strength: 0-100 based on distance from neutral
    strength = min(100, abs(normalized))

    return {
        "signal": signal,
        "strength": round(strength, 1),
        "raw_score": round(normalized, 1),
        "color": color,
        "signals": details,
    }
