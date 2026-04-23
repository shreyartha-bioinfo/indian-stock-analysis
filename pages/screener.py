"""
Page 3 — Stock Screener
Sortable, filterable table of NIFTY 50 / NIFTY 500 / SENSEX 30 stocks.
"""
import dash
from dash import dcc, html, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc

from src.data.fetcher import get_screener_data
from src.data.stocks import NIFTY50, NIFTY500, SENSEX30, SECTOR_INDICES

dash.register_page(__name__, path="/screener", name="Screener", order=2)

GREEN = "#00ff88"
RED = "#ff4444"
NEUTRAL = "#c9d1d9"
CARD_BG = "#161b22"
CHART_BG = "#0d1117"
GRID_COLOR = "#21262d"

ALL_SECTORS = sorted(set(s["sector"] for s in NIFTY500))

TABLE_COLUMNS = [
    {"name": "#", "id": "rank", "type": "numeric"},
    {"name": "Symbol", "id": "symbol_short"},
    {"name": "Company", "id": "name"},
    {"name": "Sector", "id": "sector"},
    {"name": "Price (₹)", "id": "price", "type": "numeric"},
    {"name": "Day %", "id": "day_pct", "type": "numeric"},
    {"name": "Week %", "id": "week_pct", "type": "numeric"},
    {"name": "Volume", "id": "volume", "type": "numeric"},
    {"name": "Exchange", "id": "exchange"},
]


def _get_conditional_styles():
    base = [
        {
            "if": {"row_index": "odd"},
            "backgroundColor": "#111820",
        },
        {
            "if": {"filter_query": "{day_pct} > 0", "column_id": "day_pct"},
            "color": GREEN,
            "fontWeight": "600",
        },
        {
            "if": {"filter_query": "{day_pct} < 0", "column_id": "day_pct"},
            "color": RED,
            "fontWeight": "600",
        },
        {
            "if": {"filter_query": "{day_pct} > 0", "column_id": "week_pct"},
            "color": GREEN,
        },
        {
            "if": {"filter_query": "{day_pct} < 0", "column_id": "week_pct"},
            "color": RED,
        },
        {
            "if": {"column_id": "symbol_short"},
            "color": "#4fc3f7",
            "fontWeight": "600",
            "cursor": "pointer",
        },
    ]
    return base


layout = html.Div([
    dcc.Store(id="screener-universe", data="NIFTY50"),
    dcc.Interval(id="screener-interval", interval=300 * 1000, n_intervals=0),

    html.Div([
        html.H5("Stock Screener", style={"color": NEUTRAL, "marginBottom": "4px"}),
        html.Small(id="screener-updated", style={"color": "#8b949e"}),
    ], className="mb-3"),

    # Controls
    dbc.Row([
        # Universe selector
        dbc.Col([
            html.Small("Universe", style={"color": "#8b949e", "display": "block"}),
            dbc.RadioItems(
                id="universe-selector",
                options=[
                    {"label": "NIFTY 50", "value": "NIFTY50"},
                    {"label": "NIFTY 500", "value": "NIFTY500"},
                    {"label": "SENSEX 30", "value": "SENSEX30"},
                ],
                value="NIFTY50",
                inline=True,
            ),
        ], xs=12, md=4),

        # Sector filter
        dbc.Col([
            dcc.Dropdown(
                id="sector-filter",
                options=[{"label": s, "value": s} for s in ALL_SECTORS],
                placeholder="Filter by sector...",
                multi=True,
                style={"backgroundColor": CARD_BG},
            ),
        ], xs=12, md=4),

        # Sort by
        dbc.Col([
            dcc.Dropdown(
                id="sort-by",
                options=[
                    {"label": "Day % (High→Low)", "value": "day_pct_desc"},
                    {"label": "Day % (Low→High)", "value": "day_pct_asc"},
                    {"label": "Week % (High→Low)", "value": "week_pct_desc"},
                    {"label": "Price (High→Low)", "value": "price_desc"},
                    {"label": "Price (Low→High)", "value": "price_asc"},
                    {"label": "Volume (High→Low)", "value": "volume_desc"},
                ],
                value="day_pct_desc",
                clearable=False,
                style={"backgroundColor": CARD_BG},
            ),
        ], xs=12, md=4),
    ], className="mb-3 g-2"),

    # Loading + table
    dcc.Loading([
        dbc.Row([
            # Summary badges
            dbc.Col([
                html.Div(id="screener-summary", className="mb-2"),
            ]),
        ]),
        dash_table.DataTable(
            id="screener-table",
            columns=TABLE_COLUMNS,
            data=[],
            sort_action="native",
            filter_action="native",
            page_action="native",
            page_size=25,
            row_selectable=False,
            style_table={"overflowX": "auto", "borderRadius": "8px"},
            style_cell={
                "backgroundColor": CHART_BG,
                "color": NEUTRAL,
                "border": f"1px solid {GRID_COLOR}",
                "padding": "8px 12px",
                "fontFamily": "monospace",
                "fontSize": "13px",
                "whiteSpace": "normal",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "maxWidth": "180px",
            },
            style_header={
                "backgroundColor": CARD_BG,
                "color": NEUTRAL,
                "fontWeight": "700",
                "border": f"1px solid {GRID_COLOR}",
                "fontSize": "12px",
                "letterSpacing": "0.04em",
            },
            style_data_conditional=_get_conditional_styles(),
            style_filter={
                "backgroundColor": CARD_BG,
                "color": NEUTRAL,
            },
        ),
    ], type="circle", color=GREEN),
])


@callback(
    Output("screener-table", "data"),
    Output("screener-summary", "children"),
    Output("screener-updated", "children"),
    Input("screener-interval", "n_intervals"),
    Input("universe-selector", "value"),
    Input("sector-filter", "value"),
    Input("sort-by", "value"),
)
def refresh_screener(_, universe, sectors, sort_by):
    import datetime
    now = datetime.datetime.now().strftime("%I:%M:%S %p")

    if universe == "NIFTY50":
        stocks = NIFTY50
    elif universe == "NIFTY500":
        stocks = NIFTY500
    else:
        stocks = SENSEX30

    # Apply sector filter
    if sectors:
        stocks = [s for s in stocks if s["sector"] in sectors]

    if not stocks:
        return [], html.Span("No stocks match filters.", style={"color": RED}), f"Updated: {now}"

    symbols = [s["symbol"] for s in stocks]
    name_map = {s["symbol"]: s["name"] for s in stocks}
    sector_map = {s["symbol"]: s["sector"] for s in stocks}

    price_data = get_screener_data(symbols)
    price_map = {row["symbol"]: row for row in price_data}

    rows = []
    for s in stocks:
        sym = s["symbol"]
        p = price_map.get(sym, {})
        rows.append({
            "symbol": sym,
            "symbol_short": sym.replace(".NS", "").replace(".BO", ""),
            "name": s["name"],
            "sector": sector_map.get(sym, ""),
            "price": p.get("price"),
            "day_pct": p.get("day_pct"),
            "week_pct": p.get("week_pct"),
            "volume": p.get("volume"),
            "exchange": "NSE" if sym.endswith(".NS") else "BSE",
        })

    # Sort
    reverse = sort_by.endswith("_desc")
    sort_col = sort_by.replace("_desc", "").replace("_asc", "")
    rows = sorted(rows, key=lambda x: (x.get(sort_col) or 0), reverse=reverse)

    for i, row in enumerate(rows):
        row["rank"] = i + 1
        if row.get("day_pct") is not None:
            row["day_pct"] = round(row["day_pct"], 2)
        if row.get("week_pct") is not None:
            row["week_pct"] = round(row["week_pct"], 2)

    # Summary badges
    gainers = sum(1 for r in rows if (r.get("day_pct") or 0) > 0)
    losers = sum(1 for r in rows if (r.get("day_pct") or 0) < 0)
    unchanged = len(rows) - gainers - losers
    summary = dbc.Row([
        dbc.Col(dbc.Badge(f"▲ {gainers} Gainers", color="success", className="me-2"), xs="auto"),
        dbc.Col(dbc.Badge(f"▼ {losers} Losers", color="danger", className="me-2"), xs="auto"),
        dbc.Col(dbc.Badge(f"● {unchanged} Unchanged", color="secondary"), xs="auto"),
    ], className="g-1")

    return rows, summary, f"Last updated: {now}"
