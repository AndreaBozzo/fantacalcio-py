import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.exceptions import PreventUpdate

from dashboard.utils.data_processing import (
    filter_dataframe, get_top_players, get_stats_summary,
    get_role_distribution, get_team_distribution
)

# Manual page - no register_page needed

def layout():
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("📊 Fantacalcio Analysis Overview", className="text-primary mb-4"),
                html.P(
                    "Dashboard per l'analisi dei dati FPEDIA e FSTATS del fantacalcio",
                    className="lead text-muted"
                )
            ])
        ], className="mb-4"),
        
        # Data Source Selection
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Select Data Source"),
                    dbc.CardBody([
                        dbc.RadioItems(
                            id="data-source-radio",
                            options=[
                                {"label": "FPEDIA (Current Season)", "value": "fpedia"},
                                {"label": "FSTATS (Previous Season)", "value": "fstats"},
                            ],
                            value="fpedia",
                            inline=True
                        )
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Key Metrics Cards
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("👥", className="metric-icon"),
                    html.H4(id="total-players", className="metric-value"),
                    html.P("Total Players", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.Span("⭐", className="metric-icon"),
                    html.H4(id="avg-convenienza", className="metric-value"),
                    html.P("Avg Convenience", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.Span("🏆", className="metric-icon"),
                    html.H4(id="top-convenienza", className="metric-value"),
                    html.P("Top Convenience", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.Span("⚽", className="metric-icon"),
                    html.H4(id="total-teams", className="metric-value"),
                    html.P("Teams Covered", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3),
        ], className="mb-4"),
        
        # Charts Row
        dbc.Row([
            # Role Distribution
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Players by Role"),
                    dbc.CardBody([
                        dcc.Graph(id="role-distribution-chart")
                    ])
                ])
            ], width=6),
            
            # Top Teams
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top Teams by Player Count"),
                    dbc.CardBody([
                        dcc.Graph(id="team-distribution-chart")
                    ])
                ])
            ], width=6),
        ], className="mb-4"),
        
        # Convenience Distribution
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Convenience Distribution"),
                    dbc.CardBody([
                        dcc.Graph(id="convenience-distribution-chart")
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Top Players Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🏆 Top 15 Players by Convenience"),
                    dbc.CardBody([
                        html.Div(id="top-players-table")
                    ])
                ])
            ], width=12)
        ])
        
    ], fluid=True)


# Callbacks
@callback(
    [Output("total-players", "children"),
     Output("avg-convenienza", "children"),
     Output("top-convenienza", "children"),
     Output("total-teams", "children"),
     Output("role-distribution-chart", "figure"),
     Output("team-distribution-chart", "figure"),
     Output("convenience-distribution-chart", "figure"),
     Output("top-players-table", "children")],
    Input("data-source-radio", "value")
)
def update_overview_content(data_source):
    """Update overview content based on selected data source."""
    # Get data loader from globals
    import dashboard.globals as globals
    data_loader = globals.data_loader
    
    if not data_loader:
        raise PreventUpdate
    
    # Load appropriate dataset
    if data_source == "fpedia":
        df = data_loader.load_fpedia_data()
        convenience_col = "Convenienza"
    else:
        df = data_loader.load_fstats_data()
        convenience_col = "Convenienza"
    
    if df.empty:
        empty_fig = go.Figure().add_annotation(
            text="No data available", x=0.5, y=0.5,
            xref="paper", yref="paper", showarrow=False
        )
        return "N/A", "N/A", "N/A", "N/A", empty_fig, empty_fig, empty_fig, "No data"
    
    # Calculate metrics
    total_players = len(df)
    avg_convenience = df[convenience_col].mean() if convenience_col in df.columns else 0
    top_convenience = df[convenience_col].max() if convenience_col in df.columns else 0
    total_teams = df['Squadra'].nunique() if 'Squadra' in df.columns else 0
    
    # Role distribution chart
    role_dist = get_role_distribution(df)
    role_fig = px.pie(
        values=role_dist.values, 
        names=role_dist.index,
        title="Distribution by Role"
    )
    
    # Team distribution chart (top 10)
    team_dist = get_team_distribution(df).head(10)
    team_fig = px.bar(
        x=team_dist.values,
        y=team_dist.index,
        orientation='h',
        title="Top 10 Teams"
    )
    team_fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    
    # Convenience distribution
    if convenience_col in df.columns:
        conv_fig = px.histogram(
            df, 
            x=convenience_col,
            nbins=30,
            title=f"{convenience_col} Distribution"
        )
    else:
        conv_fig = empty_fig
    
    # Top players table
    top_players = get_top_players(df, convenience_col, 15)
    display_cols = ['Nome', 'Ruolo', 'Squadra', convenience_col]
    if 'Convenienza Potenziale' in top_players.columns:
        display_cols.append('Convenienza Potenziale')
    
    available_cols = [col for col in display_cols if col in top_players.columns]
    
    if not top_players.empty and available_cols:
        table = dbc.Table.from_dataframe(
            top_players[available_cols].round(2),
            striped=True,
            bordered=True,
            hover=True,
            size="sm"
        )
    else:
        table = html.P("No data available")
    
    return (
        f"{total_players:,}",
        f"{avg_convenience:.2f}",
        f"{top_convenience:.2f}",
        str(total_teams),
        role_fig,
        team_fig,
        conv_fig,
        table
    )