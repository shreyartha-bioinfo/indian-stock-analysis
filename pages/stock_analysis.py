"""
Page 2 — Stock Analysis
Full charting suite with technical indicators and buy/sell/hold recommendation.
"""
import dash
from dash import dcc, html, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from src.data.fetcher import get_stock_data, get_stock_info, format_market_cap
from src.analysis.indicators import add_indicators, INDICATOR_GROUPS, OVERLAY_INDICATORS, SUBPLOT_INDICATORS
from src.analysis.recommender import generate_recommendation
from src.charts.price_chart import build_price_chart
from src.data.stocks import NIFTY500, SENSEX30, get_symbol_name_map

dash.register_page(__name__, path="/analysis", name="Stock Analysis", order=1)

GREEN = "#00ff88"
RED = "#ff4444"
NEUTRAL = "#c9d1d9"
CARD_BG = "#161b22"
CHART_BG = "#0d1117"
GRID_COLOR = "#21262d"

ALL_STOCKS = NIFTY500 + [s for s in SENSEX30 if not s["symbol"].endswith(".NS")]
STOCK_OPTIONS = [
    {"label": f"{s['name']} ({s['symbol'].replace('.NS','').replace('.BO','')})",
     "value": s["symbol"]}
    for s in ALL_STOCKS
]


def _info_badge(label: str, value: str, color: str = NEUTRAL) -> html.Div:
    return html.Div([
        html.Small(label, style={"color": "#8b949e", "display": "block", "fontSize": "10px"}),
        html.Span(value, style={"color": color, "fontWeight": "600", "fontSize": "13px"}),
    ], style={"padding": "4px 8px", "backgroundColor": CHART_BG, "borderRadius": "6px",
              "border": f"1px solid {GRID_COLOR}", "minWidth": "80px"})


def _indicator_checklist(group: str, names: dict) -> html.Div:
    options = [{"label": label, "value": key} for label, key in names.items()]
    return html.Div([
        html.Small(group.upper(), style={"color": "#8b949e", "fontSize": "10px",
                                          "letterSpacing": "0.05em", "display": "block",
                                          "marginTop": "10px"}),
        dbc.Checklist(
            id=f"ind-{group.lower()}",
            options=options,
            value=[],
            inline=False,
            input_class_name="me-1",
            style={"fontSize": "12px"},
        ),
    ])


layout = html.Div([
    dcc.Store(id="selected-period", data="3M"),
    dcc.Interval(id="stock-interval", interval=60 * 1000, n_intervals=0),

    # ── Top controls row ──────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="stock-search",
                options=STOCK_OPTIONS,
                value="RELIANCE.NS",
                placeholder="Search stock...",
                searchable=True,
                style={"backgroundColor": CARD_BG, "color": NEUTRAL},
            ),
        ], xs=12, md=4),

        dbc.Col([
            dbc.RadioItems(
                id="exchange-toggle",
                options=[{"label": "NSE", "value": "NSE"}, {"label": "BSE", "value": "BSE"}],
                value="NSE",
                inline=True,
                className="mt-2",
                input_checked_style={"backgroundColor": "#4fc3f7", "borderColor": "#4fc3f7"},
            ),
        ], xs=6, md=2),

        dbc.Col([
            dbc.ButtonGroup(
                [dbc.Button(p, id=f"btn-period-{p}", size="sm", outline=True,
                            color="info", className="px-2")
                 for p in ["1D", "1W", "1M", "3M", "6M", "1Y", "5Y"]],
                className="mt-1",
            ),
        ], xs=12, md=4),

        dbc.Col([
            dcc.Dropdown(
                id="chart-type",
                options=[
                    {"label": "Candlestick", "value": "Candlestick"},
                    {"label": "OHLC", "value": "OHLC"},
                    {"label": "Line", "value": "Line"},
                    {"label": "Area", "value": "Area"},
                ],
                value="Candlestick",
                clearable=False,
                style={"backgroundColor": CARD_BG, "color": NEUTRAL},
            ),
        ], xs=6, md=2),
    ], className="mb-3 g-2"),

    # ── Stock info row ─────────────────────────────────────────────────────
    html.Div(id="stock-info-bar", className="mb-3"),

    # ── Main content: indicators sidebar | chart | recommendation ─────────
    dbc.Row([
        # Left: indicator selectors
        dbc.Col([
            html.H6("Indicators", style={"color": NEUTRAL, "marginBottom": "4px"}),
            html.Div([
                _indicator_checklist(group, names)
                for group, names in INDICATOR_GROUPS.items()
            ], style={"overflowY": "auto", "maxHeight": "700px"}),
        ], xs=12, md=2, style={"backgroundColor": CARD_BG, "borderRadius": "8px",
                                 "padding": "12px", "border": f"1px solid {GRID_COLOR}"}),

        # Center: chart
        dbc.Col([
            dcc.Loading(
                dcc.Graph(id="main-chart", config={"displayModeBar": True,
                                                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                                                    "toImageButtonOptions": {"format": "png", "scale": 2}}),
                type="circle", color=GREEN,
            ),
        ], xs=12, md=7),

        # Right: recommendation
        dbc.Col([
            html.Div(id="recommendation-card"),
        ], xs=12, md=3),
    ], className="g-3"),
])


# ── Period button callbacks ─────────────────────────────────────────────────
for _p in ["1D", "1W", "1M", "3M", "6M", "1Y", "5Y"]:
    @callback(
        Output("selected-period", "data"),
        Input(f"btn-period-{_p}", "n_clicks"),
        State("selected-period", "data"),
        prevent_initial_call=True,
    )
    def _set_period(n_clicks, _current, period=_p):
        if n_clicks:
            return period
        return _current


# ── Main chart callback ─────────────────────────────────────────────────────
@callback(
    Output("main-chart", "figure"),
    Output("stock-info-bar", "children"),
    Output("recommendation-card", "children"),
    Input("stock-interval", "n_intervals"),
    Input("stock-search", "value"),
    Input("exchange-toggle", "value"),
    Input("chart-type", "value"),
    Input("selected-period", "data"),
    Input("ind-trend", "value"),
    Input("ind-momentum", "value"),
    Input("ind-volatility", "value"),
    Input("ind-volume", "value"),
    Input("ind-oscillators", "value"),
    prevent_initial_call=False,
)
def update_chart(_, symbol, exchange, chart_type, period,
                 trend_inds, momentum_inds, vol_inds, volume_inds, osc_inds):
    if not symbol:
        empty = go.Figure()
        empty.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                            annotations=[dict(text="Select a stock", showarrow=False,
                                              font=dict(color=NEUTRAL, size=16), xref="paper", yref="paper",
                                              x=0.5, y=0.5)])
        return empty, "", ""

    # Gather selected indicators
    selected_keys = (trend_inds or []) + (momentum_inds or []) + (vol_inds or []) + (volume_inds or []) + (osc_inds or [])

    # Fetch OHLCV data
    df = get_stock_data(symbol, exchange, period or "3M")
    info = get_stock_info(symbol, exchange)

    # Add indicator calculations
    if not df.empty:
        df = add_indicators(df, selected_keys)

    # Build chart
    fig = build_price_chart(df, symbol.replace(".NS", "").replace(".BO", ""), chart_type, selected_keys)

    # Stock info bar
    price = info.get("current_price")
    prev = info.get("previous_close")
    change = (price - prev) if price and prev else 0
    pct = (change / prev * 100) if prev else 0
    price_color = GREEN if change >= 0 else RED
    arrow = "▲" if change >= 0 else "▼"

    info_bar = dbc.Row([
        dbc.Col(html.Div([
            html.H4(f"₹{price:,.2f}" if price else "N/A",
                    style={"color": price_color, "marginBottom": 0}),
            html.Small(f"{arrow} {abs(change):,.2f} ({abs(pct):.2f}%)",
                       style={"color": price_color}),
        ]), xs="auto"),
        dbc.Col(_info_badge("Prev Close", f"₹{prev:,.2f}" if prev else "N/A"), xs="auto"),
        dbc.Col(_info_badge("Open", f"₹{info.get('open_price', 'N/A'):,.2f}"
                            if info.get("open_price") else "N/A"), xs="auto"),
        dbc.Col(_info_badge("Day Hi", f"₹{info.get('day_high', 'N/A'):,.2f}"
                            if info.get("day_high") else "N/A", GREEN), xs="auto"),
        dbc.Col(_info_badge("Day Lo", f"₹{info.get('day_low', 'N/A'):,.2f}"
                            if info.get("day_low") else "N/A", RED), xs="auto"),
        dbc.Col(_info_badge("52W Hi", f"₹{info.get('week52_high', 'N/A'):,.2f}"
                            if info.get("week52_high") else "N/A"), xs="auto"),
        dbc.Col(_info_badge("52W Lo", f"₹{info.get('week52_low', 'N/A'):,.2f}"
                            if info.get("week52_low") else "N/A"), xs="auto"),
        dbc.Col(_info_badge("Mkt Cap", format_market_cap(info.get("market_cap"))), xs="auto"),
        dbc.Col(_info_badge("P/E", f"{info.get('pe_ratio', 'N/A'):.1f}"
                            if info.get("pe_ratio") else "N/A"), xs="auto"),
        dbc.Col(_info_badge("Beta", f"{info.get('beta', 'N/A'):.2f}"
                            if info.get("beta") else "N/A"), xs="auto"),
    ], className="g-2 align-items-center")

    # Recommendation card
    rec = generate_recommendation(df) if not df.empty else {"signal": "N/A", "strength": 0, "signals": []}
    signal = rec.get("signal", "N/A")
    strength = rec.get("strength", 0)
    sig_color = rec.get("color", NEUTRAL)
    signals_list = rec.get("signals", [])

    def _signal_icon(score):
        if score > 0:
            return "▲"
        if score < 0:
            return "▼"
        return "●"

    def _signal_color(score):
        if score > 0:
            return GREEN
        if score < 0:
            return RED
        return "#ffcc00"

    signal_rows = [
        html.Div([
            html.Span(_signal_icon(s["score"]),
                      style={"color": _signal_color(s["score"]), "marginRight": "6px", "fontSize": "10px"}),
            html.Small(s["label"], style={"color": NEUTRAL, "fontSize": "11px"}),
        ], style={"borderBottom": f"1px solid {GRID_COLOR}", "paddingBottom": "4px", "marginBottom": "4px"})
        for s in signals_list
    ]

    rec_card = dbc.Card([
        dbc.CardHeader(
            html.H6("Signal", style={"color": NEUTRAL, "marginBottom": 0}),
            style={"backgroundColor": CHART_BG, "border": f"1px solid {GRID_COLOR}"},
        ),
        dbc.CardBody([
            html.H2(signal, style={"color": sig_color, "textAlign": "center",
                                    "fontWeight": "800", "letterSpacing": "0.1em"}),
            html.Div([
                html.Small("Strength", style={"color": "#8b949e"}),
                html.Div([
                    html.Div(style={
                        "width": f"{strength}%",
                        "height": "8px",
                        "backgroundColor": sig_color,
                        "borderRadius": "4px",
                        "transition": "width 0.5s ease",
                    }),
                ], style={"backgroundColor": GRID_COLOR, "borderRadius": "4px",
                          "height": "8px", "marginTop": "4px", "marginBottom": "4px"}),
                html.Small(f"{strength:.0f}%", style={"color": sig_color, "fontWeight": "600"}),
            ], className="mb-3"),
            html.Div([
                html.Small("INDICATOR SIGNALS", style={"color": "#8b949e", "fontSize": "10px",
                                                        "letterSpacing": "0.05em"}),
                html.Hr(style={"margin": "4px 0", "borderColor": GRID_COLOR}),
            ]),
            html.Div(signal_rows, style={"maxHeight": "380px", "overflowY": "auto"}),
        ], style={"padding": "16px"}),
    ], style={"backgroundColor": CARD_BG, "border": f"1px solid {GRID_COLOR}", "borderRadius": "8px"})

    return fig, info_bar, rec_card
