import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from loguru import logger
import os
import sys

# Add parent directory to path to import from main project
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dashboard.components.data_loader import DataLoader
import dashboard.globals as globals

# Initialize data loader
globals.data_loader = DataLoader()

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Manual page routing without use_pages
from dashboard.pages import overview, comparison, players

# App layout with navigation
app.layout = dbc.Container([
    # Navigation Bar
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Overview", href="/", active="exact")),
            dbc.NavItem(dbc.NavLink("Comparison", href="/comparison", active="exact")),
            dbc.NavItem(dbc.NavLink("Players", href="/players", active="exact")),
            dbc.NavItem(
                dbc.Button(
                    "Refresh Data", 
                    id="refresh-btn", 
                    color="outline-light", 
                    size="sm"
                )
            ),
        ],
        brand="⚽ Fantacalcio Dashboard",
        brand_href="/",
        color="primary",
        dark=True,
        className="mb-4"
    ),
    
    # Alert for data refresh
    dbc.Alert(
        "Data refreshed successfully!",
        id="refresh-alert",
        color="success",
        dismissable=True,
        is_open=False,
        className="mb-3"
    ),
    
    # Page content
    html.Div(id="page-content")
    
], fluid=True)


# Callback for data refresh
@callback(
    Output("refresh-alert", "is_open"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    """Refresh cached data when refresh button is clicked."""
    if n_clicks:
        logger.info("Refreshing dashboard data...")
        globals.data_loader.refresh_data()
        return True
    return False


# Store data loader in app context for other modules (keeping for compatibility)
app.data_loader = globals.data_loader

# Manual routing callback
@callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    """Route pages manually."""
    if pathname == '/comparison':
        return comparison.layout()
    elif pathname == '/players':
        return players.layout()
    else:  # default to overview
        return overview.layout()

# Add URL component
app.layout.children.insert(0, dcc.Location(id='url', refresh=False))


if __name__ == "__main__":
    logger.info("Starting Fantacalcio Dashboard...")
    
    # Check if data files exist
    fpedia_exists = os.path.exists(globals.data_loader.fpedia_path)
    fstats_exists = os.path.exists(globals.data_loader.fstats_path)
    
    if not fpedia_exists:
        logger.warning(f"FPEDIA file not found: {globals.data_loader.fpedia_path}")
    if not fstats_exists:
        logger.warning(f"FSTATS file not found: {globals.data_loader.fstats_path}")
    
    if not fpedia_exists and not fstats_exists:
        logger.error("No data files found! Please run the main analysis first.")
        sys.exit(1)
    
    logger.info("Dashboard starting on http://127.0.0.1:8050")
    app.run(debug=True)