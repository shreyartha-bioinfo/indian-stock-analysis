"""
Technical indicators calculated via pandas-ta.
Each function accepts an OHLCV DataFrame and returns it with new columns appended.
"""
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False


def _require_min_rows(df: pd.DataFrame, n: int) -> bool:
    return len(df) >= n


# ---------------------------------------------------------------------------
# Trend Indicators
# ---------------------------------------------------------------------------

def add_sma(df: pd.DataFrame, periods: list = [20, 50, 200]) -> pd.DataFrame:
    for p in periods:
        if _require_min_rows(df, p):
            df[f"SMA_{p}"] = df["Close"].rolling(window=p).mean().round(2)
    return df


def add_ema(df: pd.DataFrame, periods: list = [9, 21, 55]) -> pd.DataFrame:
    for p in periods:
        if _require_min_rows(df, p):
            df[f"EMA_{p}"] = df["Close"].ewm(span=p, adjust=False).mean().round(2)
    return df


def add_bollinger_bands(df: pd.DataFrame, period: int = 20, std: float = 2.0) -> pd.DataFrame:
    if not _require_min_rows(df, period):
        return df
    if PANDAS_TA_AVAILABLE:
        bb = ta.bbands(df["Close"], length=period, std=std)
        if bb is not None and not bb.empty:
            df["BB_upper"] = bb.iloc[:, 0].round(2)
            df["BB_mid"] = bb.iloc[:, 1].round(2)
            df["BB_lower"] = bb.iloc[:, 2].round(2)
            df["BB_bandwidth"] = bb.iloc[:, 3].round(4) if bb.shape[1] > 3 else None
    else:
        sma = df["Close"].rolling(window=period).mean()
        std_dev = df["Close"].rolling(window=period).std()
        df["BB_upper"] = (sma + std * std_dev).round(2)
        df["BB_mid"] = sma.round(2)
        df["BB_lower"] = (sma - std * std_dev).round(2)
    return df


def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
    if "Volume" not in df.columns:
        return df
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    cum_tp_vol = (typical_price * df["Volume"]).cumsum()
    cum_vol = df["Volume"].cumsum()
    df["VWAP"] = (cum_tp_vol / cum_vol).round(2)
    return df


def add_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_min_rows(df, 52):
        return df
    high = df["High"]
    low = df["Low"]
    nine_period_high = high.rolling(window=9).max()
    nine_period_low = low.rolling(window=9).min()
    df["Ichimoku_conversion"] = ((nine_period_high + nine_period_low) / 2).round(2)
    twenty_six_high = high.rolling(window=26).max()
    twenty_six_low = low.rolling(window=26).min()
    df["Ichimoku_base"] = ((twenty_six_high + twenty_six_low) / 2).round(2)
    df["Ichimoku_spanA"] = ((df["Ichimoku_conversion"] + df["Ichimoku_base"]) / 2).round(2)
    fifty_two_high = high.rolling(window=52).max()
    fifty_two_low = low.rolling(window=52).min()
    df["Ichimoku_spanB"] = ((fifty_two_high + fifty_two_low) / 2).round(2)
    return df


def add_supertrend(df: pd.DataFrame, period: int = 7, multiplier: float = 3.0) -> pd.DataFrame:
    if not _require_min_rows(df, period + 1):
        return df
    if PANDAS_TA_AVAILABLE:
        try:
            st = ta.supertrend(df["High"], df["Low"], df["Close"], length=period, multiplier=multiplier)
            if st is not None and not st.empty:
                cols = st.columns.tolist()
                # SUPERT column is the trend line, SUPERTd is direction
                supert_col = [c for c in cols if c.startswith("SUPERT_") and "d" not in c and "l" not in c and "s" not in c]
                superd_col = [c for c in cols if "SUPERTd" in c]
                if supert_col:
                    df["SuperTrend"] = st[supert_col[0]].round(2)
                if superd_col:
                    df["SuperTrend_dir"] = st[superd_col[0]]
        except Exception:
            pass
    return df


def add_parabolic_sar(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_min_rows(df, 5):
        return df
    if PANDAS_TA_AVAILABLE:
        try:
            psar = ta.psar(df["High"], df["Low"], df["Close"])
            if psar is not None and not psar.empty:
                psar_col = [c for c in psar.columns if "PSARl" in c or "PSARs" in c]
                if psar_col:
                    df["SAR"] = psar[psar_col[0]].combine_first(
                        psar[[c for c in psar.columns if "PSARs" in c][0]] if len(psar_col) > 1 else pd.Series()
                    ).round(2)
        except Exception:
            pass
    return df


# ---------------------------------------------------------------------------
# Momentum Indicators
# ---------------------------------------------------------------------------

def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    if not _require_min_rows(df, period + 1):
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
    if not _require_min_rows(df, slow + signal):
        return df
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD"] = (ema_fast - ema_slow).round(4)
    df["MACD_signal"] = df["MACD"].ewm(span=signal, adjust=False).mean().round(4)
    df["MACD_hist"] = (df["MACD"] - df["MACD_signal"]).round(4)
    return df


def add_stochastic(df: pd.DataFrame, k: int = 14, d: int = 3) -> pd.DataFrame:
    if not _require_min_rows(df, k):
        return df
    low_min = df["Low"].rolling(window=k).min()
    high_max = df["High"].rolling(window=k).max()
    df["Stoch_K"] = (100 * (df["Close"] - low_min) / (high_max - low_min)).round(2)
    df["Stoch_D"] = df["Stoch_K"].rolling(window=d).mean().round(2)
    return df


def add_cci(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    if not _require_min_rows(df, period):
        return df
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    sma_typical = typical.rolling(window=period).mean()
    mean_dev = typical.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    df["CCI"] = ((typical - sma_typical) / (0.015 * mean_dev)).round(2)
    return df


def add_williams_r(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    if not _require_min_rows(df, period):
        return df
    high_max = df["High"].rolling(window=period).max()
    low_min = df["Low"].rolling(window=period).min()
    df["Williams_R"] = (((high_max - df["Close"]) / (high_max - low_min)) * -100).round(2)
    return df


def add_roc(df: pd.DataFrame, period: int = 12) -> pd.DataFrame:
    if not _require_min_rows(df, period + 1):
        return df
    df["ROC"] = ((df["Close"] - df["Close"].shift(period)) / df["Close"].shift(period) * 100).round(2)
    return df


def add_tsi(df: pd.DataFrame) -> pd.DataFrame:
    if not _require_min_rows(df, 35):
        return df
    if PANDAS_TA_AVAILABLE:
        try:
            tsi = ta.tsi(df["Close"])
            if tsi is not None and not tsi.empty:
                df["TSI"] = tsi.iloc[:, 0].round(2)
        except Exception:
            pass
    return df


# ---------------------------------------------------------------------------
# Volatility Indicators
# ---------------------------------------------------------------------------

def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    if not _require_min_rows(df, period + 1):
        return df
    high_low = df["High"] - df["Low"]
    high_prev = (df["High"] - df["Close"].shift()).abs()
    low_prev = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_prev, low_prev], axis=1).max(axis=1)
    df["ATR"] = tr.ewm(alpha=1 / period, min_periods=period).mean().round(2)
    return df


def add_keltner_channels(df: pd.DataFrame, period: int = 20, multiplier: float = 2.0) -> pd.DataFrame:
    if not _require_min_rows(df, period):
        return df
    if "ATR" not in df.columns:
        df = add_atr(df)
    ema = df["Close"].ewm(span=period, adjust=False).mean()
    df["KC_upper"] = (ema + multiplier * df["ATR"]).round(2)
    df["KC_mid"] = ema.round(2)
    df["KC_lower"] = (ema - multiplier * df["ATR"]).round(2)
    return df


def add_donchian_channels(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    if not _require_min_rows(df, period):
        return df
    df["DC_upper"] = df["High"].rolling(window=period).max().round(2)
    df["DC_mid"] = ((df["High"].rolling(window=period).max() + df["Low"].rolling(window=period).min()) / 2).round(2)
    df["DC_lower"] = df["Low"].rolling(window=period).min().round(2)
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
    if "Volume" not in df.columns or not _require_min_rows(df, period + 1):
        return df
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    money_flow = typical * df["Volume"]
    pos_flow = money_flow.where(typical > typical.shift(1), 0).rolling(window=period).sum()
    neg_flow = money_flow.where(typical < typical.shift(1), 0).rolling(window=period).sum()
    mfi_ratio = pos_flow / neg_flow
    df["MFI"] = (100 - (100 / (1 + mfi_ratio))).round(2)
    return df


def add_cmf(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    if "Volume" not in df.columns or not _require_min_rows(df, period):
        return df
    clv = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"])
    money_flow_vol = clv * df["Volume"]
    df["CMF"] = (money_flow_vol.rolling(window=period).sum() / df["Volume"].rolling(window=period).sum()).round(4)
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
# Trend Strength / Oscillators
# ---------------------------------------------------------------------------

def add_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    if not _require_min_rows(df, period * 2):
        return df
    if PANDAS_TA_AVAILABLE:
        try:
            adx = ta.adx(df["High"], df["Low"], df["Close"], length=period)
            if adx is not None and not adx.empty:
                # pandas-ta 0.4: columns are ADX_14, DMP_14, DMN_14
                adx_cols = [c for c in adx.columns if c.startswith("ADX_")]
                dmp_cols = [c for c in adx.columns if c.startswith("DMP_")]
                dmn_cols = [c for c in adx.columns if c.startswith("DMN_")]
                if adx_cols:
                    df["ADX"] = adx[adx_cols[0]].round(2)
                if dmp_cols:
                    df["DI_plus"] = adx[dmp_cols[0]].round(2)
                if dmn_cols:
                    df["DI_minus"] = adx[dmn_cols[0]].round(2)
        except Exception:
            pass
    return df


def add_aroon(df: pd.DataFrame, period: int = 25) -> pd.DataFrame:
    if not _require_min_rows(df, period + 1):
        return df
    aroon_up = df["High"].rolling(window=period + 1).apply(
        lambda x: ((period - (period - np.argmax(x))) / period) * 100, raw=True
    )
    aroon_down = df["Low"].rolling(window=period + 1).apply(
        lambda x: ((period - (period - np.argmin(x))) / period) * 100, raw=True
    )
    df["Aroon_up"] = aroon_up.round(2)
    df["Aroon_down"] = aroon_down.round(2)
    df["Aroon_oscillator"] = (aroon_up - aroon_down).round(2)
    return df


def add_dpo(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    if not _require_min_rows(df, period + 1):
        return df
    shift = period // 2 + 1
    df["DPO"] = (df["Close"] - df["Close"].rolling(window=period).mean().shift(shift)).round(2)
    return df


def add_trix(df: pd.DataFrame, period: int = 15) -> pd.DataFrame:
    if not _require_min_rows(df, period * 3):
        return df
    ema1 = df["Close"].ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    df["TRIX"] = ema3.pct_change() * 100
    df["TRIX"] = df["TRIX"].round(4)
    return df


# ---------------------------------------------------------------------------
# Master function
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

# Indicators that always render as overlays on the price chart
OVERLAY_INDICATORS = {"sma", "ema", "bb", "vwap", "ichimoku", "supertrend", "psar", "keltner", "donchian"}

# Indicators that need their own subplot panel
SUBPLOT_INDICATORS = {"rsi", "macd", "stochastic", "cci", "williams_r", "roc", "tsi",
                      "obv", "mfi", "cmf", "adline", "force_index", "adx", "aroon", "dpo", "trix"}


def add_indicators(df: pd.DataFrame, indicator_keys: list = None) -> pd.DataFrame:
    """Add selected indicators to df. Defaults to core set."""
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
