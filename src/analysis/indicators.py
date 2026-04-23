"""
Technical indicators — fully manual implementations using only pandas + numpy.
No third-party TA library required.
Each function accepts an OHLCV DataFrame with columns Open/High/Low/Close/Volume.
"""
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")


def _ok(df: pd.DataFrame, n: int) -> bool:
    return len(df) >= n


# ---------------------------------------------------------------------------
# Trend Indicators
# ---------------------------------------------------------------------------

def add_sma(df: pd.DataFrame, periods: list = None) -> pd.DataFrame:
    for p in (periods or [20, 50, 200]):
        if _ok(df, p):
            df[f"SMA_{p}"] = df["Close"].rolling(window=p).mean().round(2)
    return df


def add_ema(df: pd.DataFrame, periods: list = None) -> pd.DataFrame:
    for p in (periods or [9, 21, 55]):
        if _ok(df, p):
            df[f"EMA_{p}"] = df["Close"].ewm(span=p, adjust=False).mean().round(2)
    return df


def add_bollinger_bands(df: pd.DataFrame, period: int = 20, std: float = 2.0) -> pd.DataFrame:
    if not _ok(df, period):
        return df
    sma = df["Close"].rolling(window=period).mean()
    std_dev = df["Close"].rolling(window=period).std()
    df["BB_upper"] = (sma + std * std_dev).round(2)
    df["BB_mid"] = sma.round(2)
    df["BB_lower"] = (sma - std * std_dev).round(2)
    return df


def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
    if "Volume" not in df.columns:
        return df
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    df["VWAP"] = (typical * df["Volume"]).cumsum() / df["Volume"].cumsum()
    df["VWAP"] = df["VWAP"].round(2)
    return df


def add_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    if not _ok(df, 52):
        return df
    h, l = df["High"], df["Low"]
    nine_high = h.rolling(9).max()
    nine_low = l.rolling(9).min()
    df["Ichimoku_conversion"] = ((nine_high + nine_low) / 2).round(2)
    twenty_six_high = h.rolling(26).max()
    twenty_six_low = l.rolling(26).min()
    df["Ichimoku_base"] = ((twenty_six_high + twenty_six_low) / 2).round(2)
    df["Ichimoku_spanA"] = ((df["Ichimoku_conversion"] + df["Ichimoku_base"]) / 2).round(2)
    df["Ichimoku_spanB"] = ((h.rolling(52).max() + l.rolling(52).min()) / 2).round(2)
    return df


def add_supertrend(df: pd.DataFrame, period: int = 7, multiplier: float = 3.0) -> pd.DataFrame:
    if not _ok(df, period + 1):
        return df
    df = add_atr(df, period)
    if "ATR" not in df.columns:
        return df
    hl2 = (df["High"] + df["Low"]) / 2
    upper = hl2 + multiplier * df["ATR"]
    lower = hl2 - multiplier * df["ATR"]
    close = df["Close"]

    supertrend = pd.Series(np.nan, index=df.index)
    direction = pd.Series(1, index=df.index)

    for i in range(1, len(df)):
        prev_upper = upper.iloc[i - 1] if pd.isna(supertrend.iloc[i - 1]) else supertrend.iloc[i - 1]
        prev_lower = lower.iloc[i - 1] if pd.isna(supertrend.iloc[i - 1]) else supertrend.iloc[i - 1]

        # Recalculate bands with continuity
        curr_upper = upper.iloc[i]
        curr_lower = lower.iloc[i]

        if curr_upper > prev_upper or close.iloc[i - 1] > prev_upper:
            curr_upper = curr_upper
        else:
            curr_upper = min(curr_upper, prev_upper)

        if curr_lower < prev_lower or close.iloc[i - 1] < prev_lower:
            curr_lower = curr_lower
        else:
            curr_lower = max(curr_lower, prev_lower)

        upper.iloc[i] = curr_upper
        lower.iloc[i] = curr_lower

        if direction.iloc[i - 1] == 1:
            direction.iloc[i] = 1 if close.iloc[i] >= curr_lower else -1
        else:
            direction.iloc[i] = -1 if close.iloc[i] <= curr_upper else 1

        supertrend.iloc[i] = curr_lower if direction.iloc[i] == 1 else curr_upper

    df["SuperTrend"] = supertrend.round(2)
    df["SuperTrend_dir"] = direction
    return df


def add_parabolic_sar(df: pd.DataFrame, af_start: float = 0.02,
                      af_step: float = 0.02, af_max: float = 0.2) -> pd.DataFrame:
    if not _ok(df, 2):
        return df
    high = df["High"].values
    low = df["Low"].values
    close = df["Close"].values
    n = len(df)

    sar = np.zeros(n)
    ep = np.zeros(n)
    af = np.zeros(n)
    bull = np.zeros(n, dtype=bool)

    sar[0] = low[0]
    ep[0] = high[0]
    af[0] = af_start
    bull[0] = True

    for i in range(1, n):
        prev_sar = sar[i - 1]
        prev_ep = ep[i - 1]
        prev_af = af[i - 1]
        prev_bull = bull[i - 1]

        if prev_bull:
            sar[i] = prev_sar + prev_af * (prev_ep - prev_sar)
            sar[i] = min(sar[i], low[max(0, i - 1)], low[max(0, i - 2)])
            if low[i] < sar[i]:
                bull[i] = False
                sar[i] = prev_ep
                ep[i] = low[i]
                af[i] = af_start
            else:
                bull[i] = True
                if high[i] > prev_ep:
                    ep[i] = high[i]
                    af[i] = min(prev_af + af_step, af_max)
                else:
                    ep[i] = prev_ep
                    af[i] = prev_af
        else:
            sar[i] = prev_sar - prev_af * (prev_sar - prev_ep)
            sar[i] = max(sar[i], high[max(0, i - 1)], high[max(0, i - 2)])
            if high[i] > sar[i]:
                bull[i] = True
                sar[i] = prev_ep
                ep[i] = high[i]
                af[i] = af_start
            else:
                bull[i] = False
                if low[i] < prev_ep:
                    ep[i] = low[i]
                    af[i] = min(prev_af + af_step, af_max)
                else:
                    ep[i] = prev_ep
                    af[i] = prev_af

    df["SAR"] = np.round(sar, 2)
    return df


# ---------------------------------------------------------------------------
# Momentum Indicators
# ---------------------------------------------------------------------------

def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    if not _ok(df, period + 1):
        return df
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = (100 - (100 / (1 + rs))).round(2)
    return df


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    if not _ok(df, slow + signal):
        return df
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD"] = (ema_fast - ema_slow).round(4)
    df["MACD_signal"] = df["MACD"].ewm(span=signal, adjust=False).mean().round(4)
    df["MACD_hist"] = (df["MACD"] - df["MACD_signal"]).round(4)
    return df


def add_stochastic(df: pd.DataFrame, k: int = 14, d: int = 3) -> pd.DataFrame:
    if not _ok(df, k):
        return df
    low_min = df["Low"].rolling(k).min()
    high_max = df["High"].rolling(k).max()
    df["Stoch_K"] = (100 * (df["Close"] - low_min) / (high_max - low_min)).round(2)
    df["Stoch_D"] = df["Stoch_K"].rolling(d).mean().round(2)
    return df


def add_cci(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    if not _ok(df, period):
        return df
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    sma = typical.rolling(period).mean()
    mean_dev = typical.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    df["CCI"] = ((typical - sma) / (0.015 * mean_dev)).round(2)
    return df


def add_williams_r(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    if not _ok(df, period):
        return df
    high_max = df["High"].rolling(period).max()
    low_min = df["Low"].rolling(period).min()
    df["Williams_R"] = (((high_max - df["Close"]) / (high_max - low_min)) * -100).round(2)
    return df


def add_roc(df: pd.DataFrame, period: int = 12) -> pd.DataFrame:
    if not _ok(df, period + 1):
        return df
    df["ROC"] = ((df["Close"] - df["Close"].shift(period)) / df["Close"].shift(period) * 100).round(2)
    return df


def add_tsi(df: pd.DataFrame) -> pd.DataFrame:
    if not _ok(df, 40):
        return df
    momentum = df["Close"].diff(1)
    # Double-smoothed momentum
    ds_m = momentum.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    # Double-smoothed absolute momentum
    ds_abs = momentum.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    df["TSI"] = (100 * ds_m / ds_abs).round(2)
    return df


# ---------------------------------------------------------------------------
# Volatility Indicators
# ---------------------------------------------------------------------------

def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    if not _ok(df, period + 1):
        return df
    hl = df["High"] - df["Low"]
    hc = (df["High"] - df["Close"].shift()).abs()
    lc = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    df["ATR"] = tr.ewm(alpha=1 / period, min_periods=period).mean().round(2)
    return df


def add_keltner_channels(df: pd.DataFrame, period: int = 20, multiplier: float = 2.0) -> pd.DataFrame:
    if not _ok(df, period):
        return df
    if "ATR" not in df.columns:
        df = add_atr(df)
    if "ATR" not in df.columns:
        return df
    ema = df["Close"].ewm(span=period, adjust=False).mean()
    df["KC_upper"] = (ema + multiplier * df["ATR"]).round(2)
    df["KC_mid"] = ema.round(2)
    df["KC_lower"] = (ema - multiplier * df["ATR"]).round(2)
    return df


def add_donchian_channels(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    if not _ok(df, period):
        return df
    df["DC_upper"] = df["High"].rolling(period).max().round(2)
    df["DC_lower"] = df["Low"].rolling(period).min().round(2)
    df["DC_mid"] = ((df["DC_upper"] + df["DC_lower"]) / 2).round(2)
    return df


# ---------------------------------------------------------------------------
# Volume Indicators
# ---------------------------------------------------------------------------

def add_obv(df: pd.DataFrame) -> pd.DataFrame:
    if "Volume" not in df.columns:
        return df
    direction = np.where(df["Close"] > df["Close"].shift(1), 1,
                         np.where(df["Close"] < df["Close"].shift(1), -1, 0))
    df["OBV"] = (direction * df["Volume"]).cumsum()
    return df


def add_mfi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    if "Volume" not in df.columns or not _ok(df, period + 1):
        return df
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    money_flow = typical * df["Volume"]
    pos_flow = money_flow.where(typical > typical.shift(1), 0).rolling(period).sum()
    neg_flow = money_flow.where(typical < typical.shift(1), 0).rolling(period).sum()
    mfi_ratio = pos_flow / neg_flow
    df["MFI"] = (100 - (100 / (1 + mfi_ratio))).round(2)
    return df


def add_cmf(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    if "Volume" not in df.columns or not _ok(df, period):
        return df
    clv = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"])
    mfv = clv * df["Volume"]
    df["CMF"] = (mfv.rolling(period).sum() / df["Volume"].rolling(period).sum()).round(4)
    return df


def add_adline(df: pd.DataFrame) -> pd.DataFrame:
    if "Volume" not in df.columns:
        return df
    clv = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"])
    df["AD_Line"] = (clv * df["Volume"]).cumsum()
    return df


def add_force_index(df: pd.DataFrame, period: int = 13) -> pd.DataFrame:
    if "Volume" not in df.columns:
        return df
    fi = df["Close"].diff() * df["Volume"]
    df["Force_Index"] = fi.ewm(span=period, adjust=False).mean().round(0)
    return df


# ---------------------------------------------------------------------------
# Oscillators / Trend Strength
# ---------------------------------------------------------------------------

def add_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    if not _ok(df, period * 2):
        return df
    # True Range
    hl = df["High"] - df["Low"]
    hc = (df["High"] - df["Close"].shift()).abs()
    lc = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)

    # Directional movement
    up_move = df["High"].diff()
    down_move = -df["Low"].diff()
    pos_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    neg_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    # Smooth with Wilder's EWM (alpha = 1/period)
    atr = tr.ewm(alpha=1 / period, min_periods=period).mean()
    pos_di = 100 * pos_dm.ewm(alpha=1 / period, min_periods=period).mean() / atr
    neg_di = 100 * neg_dm.ewm(alpha=1 / period, min_periods=period).mean() / atr
    dx = (pos_di - neg_di).abs() / (pos_di + neg_di) * 100
    df["ADX"] = dx.ewm(alpha=1 / period, min_periods=period).mean().round(2)
    df["DI_plus"] = pos_di.round(2)
    df["DI_minus"] = neg_di.round(2)
    return df


def add_aroon(df: pd.DataFrame, period: int = 25) -> pd.DataFrame:
    if not _ok(df, period + 1):
        return df
    aroon_up = df["High"].rolling(period + 1).apply(
        lambda x: ((period - (period - np.argmax(x))) / period) * 100, raw=True
    )
    aroon_down = df["Low"].rolling(period + 1).apply(
        lambda x: ((period - (period - np.argmin(x))) / period) * 100, raw=True
    )
    df["Aroon_up"] = aroon_up.round(2)
    df["Aroon_down"] = aroon_down.round(2)
    df["Aroon_oscillator"] = (aroon_up - aroon_down).round(2)
    return df


def add_dpo(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    if not _ok(df, period + 1):
        return df
    shift = period // 2 + 1
    df["DPO"] = (df["Close"] - df["Close"].rolling(period).mean().shift(shift)).round(2)
    return df


def add_trix(df: pd.DataFrame, period: int = 15) -> pd.DataFrame:
    if not _ok(df, period * 3):
        return df
    ema1 = df["Close"].ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    df["TRIX"] = (ema3.pct_change() * 100).round(4)
    return df


# ---------------------------------------------------------------------------
# Indicator registry and master function
# ---------------------------------------------------------------------------

INDICATOR_GROUPS = {
    "Trend": {
        "SMA (20, 50, 200)": "sma",
        "EMA (9, 21, 55)": "ema",
        "Bollinger Bands": "bb",
        "VWAP": "vwap",
        "Ichimoku Cloud": "ichimoku",
        "SuperTrend": "supertrend",
        "Parabolic SAR": "psar",
    },
    "Momentum": {
        "RSI (14)": "rsi",
        "MACD": "macd",
        "Stochastic": "stochastic",
        "CCI (20)": "cci",
        "Williams %R": "williams_r",
        "ROC (12)": "roc",
        "TSI": "tsi",
    },
    "Volatility": {
        "ATR (14)": "atr",
        "Keltner Channels": "keltner",
        "Donchian Channels": "donchian",
    },
    "Volume": {
        "OBV": "obv",
        "MFI (14)": "mfi",
        "CMF (20)": "cmf",
        "A/D Line": "adline",
        "Force Index": "force_index",
    },
    "Oscillators": {
        "ADX (14)": "adx",
        "Aroon (25)": "aroon",
        "DPO": "dpo",
        "TRIX": "trix",
    },
}

INDICATOR_DISPATCH = {
    "sma": add_sma,
    "ema": add_ema,
    "bb": add_bollinger_bands,
    "vwap": add_vwap,
    "ichimoku": add_ichimoku,
    "supertrend": add_supertrend,
    "psar": add_parabolic_sar,
    "rsi": add_rsi,
    "macd": add_macd,
    "stochastic": add_stochastic,
    "cci": add_cci,
    "williams_r": add_williams_r,
    "roc": add_roc,
    "tsi": add_tsi,
    "atr": add_atr,
    "keltner": add_keltner_channels,
    "donchian": add_donchian_channels,
    "obv": add_obv,
    "mfi": add_mfi,
    "cmf": add_cmf,
    "adline": add_adline,
    "force_index": add_force_index,
    "adx": add_adx,
    "aroon": add_aroon,
    "dpo": add_dpo,
    "trix": add_trix,
}

OVERLAY_INDICATORS = {"sma", "ema", "bb", "vwap", "ichimoku", "supertrend", "psar", "keltner", "donchian"}
SUBPLOT_INDICATORS = {"rsi", "macd", "stochastic", "cci", "williams_r", "roc", "tsi",
                      "obv", "mfi", "cmf", "adline", "force_index", "adx", "aroon", "dpo", "trix"}


def add_indicators(df: pd.DataFrame, indicator_keys: list = None) -> pd.DataFrame:
    """Add selected indicators to df. Defaults to a core set."""
    if df.empty:
        return df
    df = df.copy()
    keys = indicator_keys or ["sma", "ema", "bb", "rsi", "macd", "vwap", "atr", "obv", "adx"]
    for key in keys:
        fn = INDICATOR_DISPATCH.get(key)
        if fn:
            try:
                df = fn(df)
            except Exception:
                pass
    return df
