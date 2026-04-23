"""
Indian Stock Market Analysis Dashboard
Entry point for the Dash multi-page application.
Run with: python app.py  (dev) or gunicorn app:server (prod)
"""
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.CYBORG,
        dbc.icons.FONT_AWESOME,
    ],
    suppress_callback_exceptions=True,
    title="StockDash IN — Indian Market Analysis",
    update_title="Loading...",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Live BSE & NSE stock market analysis dashboard"},
    ],
)

server = app.server  # Flask WSGI server for gunicorn

DARK_BG = "#0d1117"
CARD_BG = "#161b22"
GRID_COLOR = "#21262d"
NEUTRAL = "#c9d1d9"
GREEN = "#00ff88"
RED = "#ff4444"


def _is_market_open() -> bool:
    """Check if NSE is open based on IST time (fallback to time check)."""
    try:
        now_ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
        weekday = now_ist.weekday()  # 0=Monday, 6=Sunday
        if weekday >= 5:  # Saturday / Sunday
            return False
        market_open = now_ist.replace(hour=9, minute=15, second=0)
        market_close = now_ist.replace(hour=15, minute=30, second=0)
        return market_open <= now_ist <= market_close
    except Exception:
        return False


navbar = dbc.Navbar(
    dbc.Container([
        # Brand
        dbc.Row([
            dbc.Col(html.I(className="fas fa-chart-line me-2",
                           style={"color": "#4fc3f7", "fontSize": "20px"})),
            dbc.Col(dbc.NavbarBrand(
                "StockDash IN",
                href="/",
                style={"color": "#ffffff", "fontWeight": "800",
                       "fontSize": "18px", "letterSpacing": "0.02em"},
            )),
        ], align="center", className="g-0"),

        # Nav links (collapsed on mobile)
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavLink(
                    [html.I(className="fas fa-chart-bar me-1"), "Overview"],
                    href="/",
                    active="exact",
                    style={"color": NEUTRAL},
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-candlestick-chart me-1"), "Analysis"],
                    href="/analysis",
                    active="exact",
                    style={"color": NEUTRAL},
                ),
                dbc.NavLink(
                    [html.I(className="fas fa-filter me-1"), "Screener"],
                    href="/screener",
                    active="exact",
                    style={"color": NEUTRAL},
                ),
            ], navbar=True, className="ms-auto"),
            id="navbar-collapse",
            navbar=True,
        ),

        # Market status badge + time
        html.Div([
            html.Span(id="market-status-badge", className="me-3"),
            html.Small(id="nav-time", style={"color": "#8b949e", "fontFamily": "monospace"}),
        ], className="d-flex align-items-center ms-3"),
    ], fluid=True),
    color="dark",
    dark=True,
    sticky="top",
    style={"borderBottom": f"1px solid {GRID_COLOR}", "backgroundColor": CARD_BG},
    className="mb-3",
)

app.layout = dbc.Container([
    navbar,
    dcc.Interval(id="nav-clock", interval=10 * 1000, n_intervals=0),
    dcc.Location(id="url"),
    dash.page_container,
    # Footer
    html.Hr(style={"borderColor": GRID_COLOR, "marginTop": "40px"}),
    html.Div([
        html.Small([
            "StockDash IN · Data via Yahoo Finance · 15-min delayed during market hours · ",
            html.Span("Not financial advice", style={"color": RED}),
        ], style={"color": "#8b949e"}),
    ], className="text-center pb-3"),
], fluid=True, style={"backgroundColor": DARK_BG, "minHeight": "100vh"})


@app.callback(
    Output("market-status-badge", "children"),
    Output("nav-time", "children"),
    Input("nav-clock", "n_intervals"),
)
def update_nav_clock(_):
    now_ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    time_str = now_ist.strftime("%H:%M:%S IST")
    is_open = _is_market_open()
    badge = dbc.Badge(
        "● OPEN" if is_open else "● CLOSED",
        color="success" if is_open else "danger",
        style={"fontSize": "11px", "padding": "4px 8px"},
    )
    return badge, time_str


@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_navbar(n):
    return bool(n % 2)


if __name__ == "__main__":
    debug = os.getenv("DASH_DEBUG", "True").lower() == "true"
    port = int(os.getenv("PORT", os.getenv("DASH_PORT", "8050")))
    app.run(debug=debug, host="0.0.0.0", port=port)
