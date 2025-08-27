import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
from dash.exceptions import PreventUpdate

from dashboard.utils.data_processing import filter_dataframe

# Manual page - no register_page needed

def layout():
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("👤 Player Analysis", className="text-primary mb-4"),
                html.P(
                    "Analisi dettagliata dei giocatori con filtri avanzati e tabelle interattive",
                    className="lead text-muted"
                )
            ])
        ], className="mb-4"),
        
        # Filters Card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🔍 Filters"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Data Source"),
                                dbc.RadioItems(
                                    id="players-data-source",
                                    options=[
                                        {"label": "FPEDIA", "value": "fpedia"},
                                        {"label": "FSTATS", "value": "fstats"},
                                    ],
                                    value="fpedia",
                                    inline=True
                                )
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Roles"),
                                dcc.Dropdown(
                                    id="roles-filter",
                                    placeholder="Select roles",
                                    multi=True
                                )
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Teams"),
                                dcc.Dropdown(
                                    id="teams-filter",
                                    placeholder="Select teams",
                                    multi=True
                                )
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Convenience Filter"),
                                dcc.Dropdown(
                                    id="convenience-filter-dropdown",
                                    options=[
                                        {"label": "All Players", "value": "all"},
                                        {"label": "Top 50", "value": "top50"},
                                        {"label": "Top 100", "value": "top100"},
                                        {"label": "Above Average", "value": "above_avg"}
                                    ],
                                    value="all",
                                    clearable=False
                                )
                            ], width=3)
                        ])
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Summary Stats
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("📊", className="metric-icon"),
                    html.H4(id="filtered-count", className="metric-value"),
                    html.P("Players Shown", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.Span("💯", className="metric-icon"),
                    html.H4(id="avg-filtered-convenience", className="metric-value"),
                    html.P("Avg Convenience", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.Span("🌟", className="metric-icon"),
                    html.H4(id="top-filtered-convenience", className="metric-value"),
                    html.P("Top Convenience", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.Span("🏟️", className="metric-icon"),
                    html.H4(id="filtered-teams", className="metric-value"),
                    html.P("Teams", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3)
        ], className="mb-4"),
        
        # Players Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("📋 Players Table", className="mb-0"),
                        html.Small(" (Interactive: click to sort, type to filter)", className="text-muted")
                    ]),
                    dbc.CardBody([
                        html.Div(id="players-table-container")
                    ])
                ])
            ], width=12)
        ])
        
    ], fluid=True)


# Callbacks
@callback(
    [Output("roles-filter", "options"),
     Output("teams-filter", "options"),
     Output("filtered-count", "children"),
     Output("avg-filtered-convenience", "children"),
     Output("top-filtered-convenience", "children"),
     Output("filtered-teams", "children"),
     Output("players-table-container", "children")],
    [Input("players-data-source", "value"),
     Input("roles-filter", "value"),
     Input("teams-filter", "value"),
     Input("convenience-filter-dropdown", "value")],
    prevent_initial_call=False
)
def update_players_page(data_source, selected_roles, selected_teams, convenience_filter):
    """Update filter options based on selected data source."""
    import dashboard.globals as globals
    data_loader = globals.data_loader
    
    if not data_loader:
        raise PreventUpdate
    
    # Load appropriate dataset
    if data_source == "fpedia":
        df = data_loader.load_fpedia_data()
    else:
        df = data_loader.load_fstats_data()
    
    if df.empty:
        return [], [], "0", "N/A", "N/A", "0", html.P("No data available")
    
    # Role options
    roles = []
    if 'Ruolo' in df.columns:
        roles = [{"label": role, "value": role} for role in sorted(df['Ruolo'].unique())]
    
    # Team options
    teams = []
    if 'Squadra' in df.columns:
        unique_teams = df['Squadra'].unique()
        # Handle potential dict values in FSTATS data
        team_names = []
        for team in unique_teams:
            if isinstance(team, dict):
                team_names.append(team.get('name', str(team)))
            else:
                team_names.append(str(team))
        teams = [{"label": team, "value": team} for team in sorted(team_names)]
    
    # Apply filters for table data
    filters = {
        'roles': selected_roles,
        'teams': selected_teams,
        'convenience_filter': convenience_filter
    }
    
    filtered_df = filter_dataframe(df, filters)
    
    # Calculate stats
    filtered_count = len(filtered_df)
    avg_conv = filtered_df['Convenienza'].mean() if 'Convenienza' in filtered_df.columns and not filtered_df.empty else 0
    top_conv = filtered_df['Convenienza'].max() if 'Convenienza' in filtered_df.columns and not filtered_df.empty else 0
    filtered_teams_count = filtered_df['Squadra'].nunique() if 'Squadra' in filtered_df.columns and not filtered_df.empty else 0
    
    # Prepare table data
    if filtered_df.empty:
        table_content = html.P("No players match the selected filters")
    else:
        # Select relevant columns for display
        display_columns = []
        for col in ['Nome', 'Ruolo', 'Squadra', 'Convenienza', 'Convenienza Potenziale']:
            if col in filtered_df.columns:
                display_columns.append(col)
        
        # Add a few more columns based on data source
        if data_source == "fpedia":
            extra_cols = ['Punteggio', 'Fantamedia anno 2024-2025', 'Presenze campionato corrente']
        else:
            extra_cols = ['fantacalcioFantaindex', 'fanta_avg', 'presences', 'goals']
        
        for col in extra_cols:
            if col in filtered_df.columns and col not in display_columns:
                display_columns.append(col)
        
        # Prepare data for AG Grid
        table_data = filtered_df[display_columns].round(2).to_dict('records')
        
        # Column definitions for AG Grid
        column_defs = []
        for col in display_columns:
            col_def = {
                "headerName": col,
                "field": col,
                "sortable": True,
                "filter": True,
                "resizable": True
            }
            
            # Special formatting for numeric columns
            if col in ['Convenienza', 'Convenienza Potenziale', 'Punteggio']:
                col_def["type"] = "numericColumn"
                col_def["valueFormatter"] = {"function": "d3.format(',.2f')(params.value)"}
            
            # Pin important columns
            if col in ['Nome', 'Ruolo']:
                col_def["pinned"] = "left"
                
            column_defs.append(col_def)
        
        # Create AG Grid table
        table_content = dag.AgGrid(
            id="players-ag-grid",
            rowData=table_data,
            columnDefs=column_defs,
            defaultColDef={
                "sortable": True,
                "filter": True,
                "resizable": True,
                "minWidth": 100
            },
            style={"height": "600px"},
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 50,
                "rowSelection": "single",
                "animateRows": True
            }
        )
    
    return (
        roles, teams,
        f"{filtered_count:,}",
        f"{avg_conv:.2f}",
        f"{top_conv:.2f}",
        str(filtered_teams_count),
        table_content
    )


