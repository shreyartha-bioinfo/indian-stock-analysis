"""
Page 1 — Market Overview
Shows live index cards, top gainers/losers, and sector heatmap.
Auto-refreshes every 60 seconds.
"""
import dash
from dash import dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from src.data.fetcher import get_index_quotes, get_top_movers
from src.data.stocks import SECTOR_INDICES, NIFTY50

dash.register_page(__name__, path="/", name="Market Overview", order=0)

GREEN = "#00ff88"
RED = "#ff4444"
NEUTRAL = "#c9d1d9"
CARD_BG = "#161b22"
CHART_BG = "#0d1117"
GRID_COLOR = "#21262d"


def _make_index_card(name: str, data: dict) -> dbc.Col:
    price = data.get("price")
    change = data.get("change", 0)
    pct = data.get("pct_change", 0)

    color = GREEN if change >= 0 else RED
    arrow = "▲" if change >= 0 else "▼"
    price_str = f"₹{price:,.2f}" if price else "N/A"
    change_str = f"{arrow} {abs(change):,.2f} ({abs(pct):.2f}%)" if price else "—"

    return dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.P(name, className="index-card-name"),
                html.H4(price_str, className="index-card-price"),
                html.P(change_str, style={"color": color, "fontWeight": "600", "marginBottom": 0}),
            ], style={"padding": "12px 16px"}),
        ], style={"backgroundColor": CARD_BG, "border": f"1px solid {GRID_COLOR}", "borderRadius": "8px"}),
        xs=6, sm=4, md=3, lg=2,
        className="mb-3",
    )


def _make_movers_table(rows: list, title: str, is_gainers: bool) -> dbc.Card:
    color = GREEN if is_gainers else RED
    header_bg = "rgba(0,255,136,0.08)" if is_gainers else "rgba(255,68,68,0.08)"
    rows_html = []
    for r in rows:
        pct = r.get("pct_change", 0)
        pct_color = GREEN if pct >= 0 else RED
        rows_html.append(
            html.Tr([
                html.Td(dcc.Link(r["symbol"], href=f"/analysis?symbol={r['full_symbol']}&exchange=NSE"),
                        style={"color": "#4fc3f7", "fontWeight": "600"}),
                html.Td(r["name"][:22], style={"color": NEUTRAL, "fontSize": "12px"}),
                html.Td(f"₹{r['price']:,.2f}", style={"textAlign": "right", "color": NEUTRAL}),
                html.Td(f"{'+' if pct >= 0 else ''}{pct:.2f}%",
                        style={"textAlign": "right", "color": pct_color, "fontWeight": "600"}),
            ])
        )
    return dbc.Card([
        dbc.CardHeader(
            html.H6(title, style={"color": color, "marginBottom": 0}),
            style={"backgroundColor": header_bg, "border": f"1px solid {GRID_COLOR}"},
        ),
        dbc.CardBody([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Symbol"), html.Th("Name"), html.Th("Price", style={"textAlign": "right"}),
                    html.Th("Change%", style={"textAlign": "right"}),
                ])),
                html.Tbody(rows_html),
            ], className="movers-table"),
        ], style={"padding": "8px"}),
    ], style={"backgroundColor": CARD_BG, "border": f"1px solid {GRID_COLOR}", "borderRadius": "8px"})


def _make_heatmap(index_quotes: dict) -> go.Figure:
    """Sector heatmap using index % changes."""
    names = list(index_quotes.keys())
    pcts = [index_quotes[n].get("pct_change", 0) for n in names]
    prices = [index_quotes[n].get("price") for n in names]

    labels = [
        f"{n}<br>{'₹'+f'{p:,.0f}' if p else 'N/A'}<br>{'+'if c>=0 else ''}{c:.2f}%"
        for n, p, c in zip(names, prices, pcts)
    ]
    colors = ["rgba(0,255,136," + str(min(0.9, 0.3 + abs(c) / 5)) + ")" if c >= 0
              else "rgba(255,68,68," + str(min(0.9, 0.3 + abs(c) / 5)) + ")"
              for c in pcts]

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=[""] * len(names),
        values=[1] * len(names),
        textfont=dict(size=12, color="#ffffff"),
        marker=dict(colors=colors, line=dict(width=2, color="#0d1117")),
        hovertemplate="%{label}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        margin=dict(l=0, r=0, t=0, b=0),
        height=280,
    )
    return fig


layout = html.Div([
    dcc.Interval(id="market-interval", interval=60 * 1000, n_intervals=0),
    html.Div([
        html.H5("Market Overview", style={"color": "#c9d1d9", "marginBottom": "4px"}),
        html.Small(id="market-last-updated", style={"color": "#8b949e"}),
    ], style={"marginBottom": "16px"}),

    # Index cards row
    html.Div(id="index-cards-row"),

    # Heatmap
    dbc.Card([
        dbc.CardHeader(html.H6("Sector Heatmap", style={"color": "#c9d1d9", "marginBottom": 0}),
                       style={"backgroundColor": CARD_BG, "border": f"1px solid {GRID_COLOR}"}),
        dbc.CardBody(dcc.Graph(id="sector-heatmap", config={"displayModeBar": False}),
                     style={"padding": "8px"}),
    ], style={"backgroundColor": CARD_BG, "border": f"1px solid {GRID_COLOR}",
              "borderRadius": "8px", "marginBottom": "20px"}),

    # Gainers / Losers
    dbc.Row([
        dbc.Col(html.Div(id="gainers-table"), md=6),
        dbc.Col(html.Div(id="losers-table"), md=6),
    ], className="g-3"),
])


@callback(
    Output("index-cards-row", "children"),
    Output("sector-heatmap", "figure"),
    Output("gainers-table", "children"),
    Output("losers-table", "children"),
    Output("market-last-updated", "children"),
    Input("market-interval", "n_intervals"),
)
def refresh_market(_):
    import datetime
    now = datetime.datetime.now().strftime("%I:%M:%S %p")

    quotes = get_index_quotes()
    movers = get_top_movers("NSE", n=10)

    cards = dbc.Row(
        [_make_index_card(name, data) for name, data in quotes.items()],
        className="g-2 mb-4",
    )
    heatmap = _make_heatmap(quotes)
    gainers_tbl = _make_movers_table(movers.get("gainers", []), "Top Gainers (NSE)", True)
    losers_tbl = _make_movers_table(movers.get("losers", []), "Top Losers (NSE)", False)

    return cards, heatmap, gainers_tbl, losers_tbl, f"Last updated: {now}"
