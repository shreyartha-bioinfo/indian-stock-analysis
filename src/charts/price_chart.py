"""
Plotly chart builders for price data: Candlestick, OHLC, Line, Area.
Returns go.Figure objects configured with the dark financial theme.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.analysis.indicators import OVERLAY_INDICATORS, SUBPLOT_INDICATORS

CHART_BG = "#0d1117"
PAPER_BG = "#0d1117"
GRID_COLOR = "#21262d"
TEXT_COLOR = "#c9d1d9"
GREEN = "#00ff88"
RED = "#ff4444"
VOLUME_UP = "rgba(0,255,136,0.4)"
VOLUME_DOWN = "rgba(255,68,68,0.4)"

OVERLAY_COLORS = {
    "SMA_20": "#f0c040",
    "SMA_50": "#4fc3f7",
    "SMA_200": "#ef5350",
    "EMA_9": "#ce93d8",
    "EMA_21": "#80cbc4",
    "EMA_55": "#ffb74d",
    "BB_upper": "#546e7a",
    "BB_mid": "#78909c",
    "BB_lower": "#546e7a",
    "VWAP": "#26c6da",
    "Ichimoku_conversion": "#f48fb1",
    "Ichimoku_base": "#80deea",
    "Ichimoku_spanA": "rgba(0,200,83,0.15)",
    "Ichimoku_spanB": "rgba(255,68,68,0.15)",
    "SuperTrend": "#ff9800",
    "SAR": "#e040fb",
    "KC_upper": "#37474f",
    "KC_lower": "#37474f",
    "DC_upper": "#1a237e",
    "DC_lower": "#1a237e",
}


def _base_layout(title: str = "") -> dict:
    return dict(
        title=dict(text=title, font=dict(color=TEXT_COLOR, size=14)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=TEXT_COLOR, size=11),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            rangeslider=dict(visible=False),
            type="date",
        ),
        yaxis=dict(gridcolor=GRID_COLOR, showgrid=True),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=GRID_COLOR,
            font=dict(size=10),
            orientation="h",
            y=1.02,
            x=0,
        ),
        hovermode="x unified",
    )


def _add_overlay_traces(fig: go.Figure, df: pd.DataFrame, row: int = 1):
    """Add all overlay indicator traces (SMA, EMA, BB, VWAP, etc.) to row."""
    overlay_cols = {
        "SMA_20": "SMA 20",
        "SMA_50": "SMA 50",
        "SMA_200": "SMA 200",
        "EMA_9": "EMA 9",
        "EMA_21": "EMA 21",
        "EMA_55": "EMA 55",
        "BB_upper": "BB Upper",
        "BB_mid": "BB Mid",
        "BB_lower": "BB Lower",
        "VWAP": "VWAP",
        "Ichimoku_conversion": "Ichimoku Conv",
        "Ichimoku_base": "Ichimoku Base",
        "SuperTrend": "SuperTrend",
        "SAR": "Parabolic SAR",
        "KC_upper": "KC Upper",
        "KC_lower": "KC Lower",
        "DC_upper": "DC Upper",
        "DC_lower": "DC Lower",
    }
    for col, label in overlay_cols.items():
        if col in df.columns:
            color = OVERLAY_COLORS.get(col, "#888888")
            mode = "markers" if col == "SAR" else "lines"
            marker = dict(symbol="circle", size=3, color=color) if col == "SAR" else None
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    name=label,
                    line=dict(color=color, width=1) if mode == "lines" else None,
                    mode=mode,
                    marker=marker,
                    opacity=0.85,
                ),
                row=row, col=1,
            )
    # Bollinger fill
    if "BB_upper" in df.columns and "BB_lower" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=pd.concat([df.index.to_series(), df.index.to_series()[::-1]]),
                y=pd.concat([df["BB_upper"], df["BB_lower"][::-1]]),
                fill="toself",
                fillcolor="rgba(84,110,122,0.08)",
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,
                hoverinfo="skip",
            ),
            row=row, col=1,
        )
    # Ichimoku cloud fill
    if "Ichimoku_spanA" in df.columns and "Ichimoku_spanB" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["Ichimoku_spanA"],
                line=dict(color="rgba(0,200,83,0.3)", width=0),
                showlegend=False, hoverinfo="skip",
            ),
            row=row, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["Ichimoku_spanB"],
                fill="tonexty",
                fillcolor="rgba(38,50,56,0.3)",
                line=dict(color="rgba(255,68,68,0.3)", width=0),
                showlegend=False, hoverinfo="skip",
            ),
            row=row, col=1,
        )


def build_price_chart(
    df: pd.DataFrame,
    symbol: str,
    chart_type: str = "Candlestick",
    selected_indicators: list = None,
) -> go.Figure:
    """
    Build the full chart figure with price + volume + indicator subplots.

    Args:
        df: OHLCV DataFrame with indicator columns already added.
        symbol: Stock symbol string for title.
        chart_type: One of Candlestick | OHLC | Line | Area.
        selected_indicators: List of indicator keys (from SUBPLOT_INDICATORS).

    Returns:
        Plotly Figure.
    """
    selected_indicators = selected_indicators or []
    subplot_inds = [k for k in selected_indicators if k in SUBPLOT_INDICATORS]

    n_rows = 2 + len(subplot_inds)  # price + volume + each subplot indicator
    row_heights = [0.5] + [0.15] + [0.15] * len(subplot_inds)

    subplot_titles = [symbol, "Volume"] + [k.upper() for k in subplot_inds]
    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=row_heights,
        subplot_titles=subplot_titles,
    )

    if df.empty:
        fig.update_layout(**_base_layout(f"{symbol} — No Data"))
        return fig

    # --- Row 1: Price chart ---
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            name=symbol,
            increasing_line_color=GREEN,
            decreasing_line_color=RED,
            increasing_fillcolor=GREEN,
            decreasing_fillcolor=RED,
        ), row=1, col=1)
    elif chart_type == "OHLC":
        fig.add_trace(go.Ohlc(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            name=symbol,
            increasing_line_color=GREEN,
            decreasing_line_color=RED,
        ), row=1, col=1)
    elif chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"],
            name=symbol,
            line=dict(color=GREEN, width=2),
            mode="lines",
        ), row=1, col=1)
    elif chart_type == "Area":
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"],
            name=symbol,
            line=dict(color=GREEN, width=2),
            fill="tozeroy",
            fillcolor="rgba(0,255,136,0.08)",
            mode="lines",
        ), row=1, col=1)

    # Overlay indicators on price chart
    _add_overlay_traces(fig, df, row=1)

    # --- Row 2: Volume ---
    if "Volume" in df.columns:
        colors = [
            VOLUME_UP if c >= o else VOLUME_DOWN
            for c, o in zip(df["Close"], df["Open"])
        ]
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"],
            name="Volume",
            marker_color=colors,
            showlegend=False,
        ), row=2, col=1)

    # --- Rows 3+: Subplot indicators ---
    for i, key in enumerate(subplot_inds):
        r = 3 + i
        _add_indicator_subplot(fig, df, key, r)

    # Apply dark theme to all axes
    layout_update = _base_layout(f"{symbol}")
    for j in range(1, n_rows + 1):
        xk = f"xaxis{j}" if j > 1 else "xaxis"
        yk = f"yaxis{j}" if j > 1 else "yaxis"
        layout_update[xk] = dict(gridcolor=GRID_COLOR, showgrid=True, rangeslider=dict(visible=False))
        layout_update[yk] = dict(gridcolor=GRID_COLOR, showgrid=True)
    layout_update["height"] = 300 + 150 * n_rows
    layout_update["showlegend"] = True
    fig.update_layout(**layout_update)
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        annotations=[dict(font=dict(color=TEXT_COLOR, size=11)) for _ in range(n_rows)],
    )
    return fig


def _add_indicator_subplot(fig: go.Figure, df: pd.DataFrame, key: str, row: int):
    """Add a specific subplot indicator trace to the given row."""
    if key == "rsi":
        if "RSI" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                                     line=dict(color="#f0c040", width=1.5)), row=row, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,68,68,0.5)", row=row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,255,136,0.5)", row=row, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="rgba(200,200,200,0.2)", row=row, col=1)

    elif key == "macd":
        if "MACD" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD",
                                     line=dict(color="#4fc3f7", width=1.5)), row=row, col=1)
        if "MACD_signal" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], name="Signal",
                                     line=dict(color="#f48fb1", width=1.5)), row=row, col=1)
        if "MACD_hist" in df.columns:
            colors = [GREEN if v >= 0 else RED for v in df["MACD_hist"].fillna(0)]
            fig.add_trace(go.Bar(x=df.index, y=df["MACD_hist"], name="Histogram",
                                 marker_color=colors, showlegend=False), row=row, col=1)

    elif key == "stochastic":
        if "Stoch_K" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["Stoch_K"], name="%K",
                                     line=dict(color="#f0c040", width=1.5)), row=row, col=1)
        if "Stoch_D" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["Stoch_D"], name="%D",
                                     line=dict(color="#ef5350", width=1.5)), row=row, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="rgba(255,68,68,0.5)", row=row, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="rgba(0,255,136,0.5)", row=row, col=1)

    elif key == "cci":
        if "CCI" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["CCI"], name="CCI",
                                     line=dict(color="#ce93d8", width=1.5)), row=row, col=1)
            fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,68,68,0.5)", row=row, col=1)
            fig.add_hline(y=-100, line_dash="dash", line_color="rgba(0,255,136,0.5)", row=row, col=1)

    elif key == "williams_r":
        if "Williams_R" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["Williams_R"], name="Williams %R",
                                     line=dict(color="#80cbc4", width=1.5)), row=row, col=1)
            fig.add_hline(y=-20, line_dash="dash", line_color="rgba(255,68,68,0.5)", row=row, col=1)
            fig.add_hline(y=-80, line_dash="dash", line_color="rgba(0,255,136,0.5)", row=row, col=1)

    elif key == "roc":
        if "ROC" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["ROC"], name="ROC",
                                     line=dict(color="#ffb74d", width=1.5)), row=row, col=1)
            fig.add_hline(y=0, line_dash="solid", line_color=GRID_COLOR, row=row, col=1)

    elif key == "obv":
        if "OBV" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["OBV"], name="OBV",
                                     line=dict(color="#26c6da", width=1.5)), row=row, col=1)

    elif key == "mfi":
        if "MFI" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["MFI"], name="MFI",
                                     line=dict(color="#ef5350", width=1.5)), row=row, col=1)
            fig.add_hline(y=80, line_dash="dash", line_color="rgba(255,68,68,0.5)", row=row, col=1)
            fig.add_hline(y=20, line_dash="dash", line_color="rgba(0,255,136,0.5)", row=row, col=1)

    elif key == "cmf":
        if "CMF" in df.columns:
            colors = [GREEN if v >= 0 else RED for v in df["CMF"].fillna(0)]
            fig.add_trace(go.Bar(x=df.index, y=df["CMF"], name="CMF",
                                 marker_color=colors), row=row, col=1)

    elif key == "adline":
        if "AD_Line" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["AD_Line"], name="A/D Line",
                                     line=dict(color="#ce93d8", width=1.5)), row=row, col=1)

    elif key == "force_index":
        if "Force_Index" in df.columns:
            colors = [GREEN if v >= 0 else RED for v in df["Force_Index"].fillna(0)]
            fig.add_trace(go.Bar(x=df.index, y=df["Force_Index"], name="Force Index",
                                 marker_color=colors), row=row, col=1)

    elif key == "adx":
        if "ADX" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["ADX"], name="ADX",
                                     line=dict(color="#f0c040", width=1.5)), row=row, col=1)
        if "DI_plus" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["DI_plus"], name="DI+",
                                     line=dict(color=GREEN, width=1)), row=row, col=1)
        if "DI_minus" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["DI_minus"], name="DI-",
                                     line=dict(color=RED, width=1)), row=row, col=1)
        fig.add_hline(y=25, line_dash="dash", line_color="rgba(200,200,200,0.3)", row=row, col=1)

    elif key == "aroon":
        if "Aroon_up" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["Aroon_up"], name="Aroon Up",
                                     line=dict(color=GREEN, width=1.5)), row=row, col=1)
        if "Aroon_down" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["Aroon_down"], name="Aroon Down",
                                     line=dict(color=RED, width=1.5)), row=row, col=1)

    elif key == "dpo":
        if "DPO" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["DPO"], name="DPO",
                                     line=dict(color="#80cbc4", width=1.5)), row=row, col=1)
            fig.add_hline(y=0, line_dash="solid", line_color=GRID_COLOR, row=row, col=1)

    elif key == "trix":
        if "TRIX" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["TRIX"], name="TRIX",
                                     line=dict(color="#ffb74d", width=1.5)), row=row, col=1)
            fig.add_hline(y=0, line_dash="solid", line_color=GRID_COLOR, row=row, col=1)

    elif key == "tsi":
        if "TSI" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["TSI"], name="TSI",
                                     line=dict(color="#4fc3f7", width=1.5)), row=row, col=1)
            fig.add_hline(y=0, line_dash="solid", line_color=GRID_COLOR, row=row, col=1)
