import dash
from dash import dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from dash.exceptions import PreventUpdate

from dashboard.utils.data_processing import (
    merge_datasets_on_name, prepare_scatter_data, get_stats_summary
)

# Manual page - no register_page needed

def layout():
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("⚽ Performance Analysis Hub", className="text-primary mb-2"),
                html.P(
                    "Analisi avanzata delle prestazioni: confronta giocatori, squadre e identifica occasioni di mercato",
                    className="lead text-muted mb-4"
                )
            ])
        ]),
        
        # Quick Stats Cards
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("🏆", className="metric-icon"),
                    html.H4(id="best-value-player", className="metric-value text-success"),
                    html.P("Best Value Player", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.Span("💎", className="metric-icon"),
                    html.H4(id="hidden-gem", className="metric-value text-info"),
                    html.P("Hidden Gem", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.Span("📈", className="metric-icon"),
                    html.H4(id="trending-up", className="metric-value text-warning"),
                    html.P("Trending Up", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3),
            dbc.Col([
                html.Div([
                    html.Span("⚡", className="metric-icon"),
                    html.H4(id="most-consistent", className="metric-value text-primary"),
                    html.P("Most Consistent", className="metric-label")
                ], className="metric-card animate-fadeInUp")
            ], width=3)
        ], className="mb-4"),
        
        # Main Analysis Section
        dbc.Row([
            # Left Panel - Player Search & Comparison
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🔍 Player Comparison Tool"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Player 1"),
                                dcc.Dropdown(
                                    id="player1-dropdown",
                                    placeholder="Select first player",
                                    searchable=True
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Player 2"),
                                dcc.Dropdown(
                                    id="player2-dropdown", 
                                    placeholder="Select second player",
                                    searchable=True
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Focus Role"),
                                dcc.Dropdown(
                                    id="role-filter-comp",
                                    options=[
                                        {"label": "All Players", "value": "ALL"},
                                        {"label": "Portieri (P)", "value": "P"},
                                        {"label": "Difensori (D)", "value": "D"},
                                        {"label": "Centrocampisti (C)", "value": "C"},
                                        {"label": "Attaccanti (A)", "value": "A"}
                                    ],
                                    value="ALL"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Season Data"),
                                dbc.RadioItems(
                                    id="season-toggle",
                                    options=[
                                        {"label": "Current", "value": "current"},
                                        {"label": "Previous", "value": "previous"},
                                        {"label": "Both", "value": "both"}
                                    ],
                                    value="both",
                                    inline=True
                                )
                            ], width=6)
                        ])
                    ])
                ])
            ], width=4),
            
            # Right Panel - Performance Radar
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📊 Performance Radar"),
                    dbc.CardBody([
                        dcc.Graph(id="radar-comparison", style={"height": "400px"})
                    ])
                ])
            ], width=8)
        ], className="mb-4"),
        
        # Value vs Performance Analysis
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("💰 Value vs Performance Matrix", className="mb-0"),
                        html.Small("Identify undervalued and overvalued players", className="text-muted")
                    ]),
                    dbc.CardBody([
                        # Controls
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("X-Axis Metric"),
                                dcc.Dropdown(
                                    id="x-metric-dropdown",
                                    options=[
                                        {"label": "Fantasy Average", "value": "fanta_avg"},
                                        {"label": "Convenience Score", "value": "Convenienza"},
                                        {"label": "Goals", "value": "goals"},
                                        {"label": "Assists", "value": "assists"}
                                    ],
                                    value="fanta_avg"
                                )
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Y-Axis Metric"), 
                                dcc.Dropdown(
                                    id="y-metric-dropdown",
                                    options=[
                                        {"label": "Convenience Score", "value": "Convenienza"},
                                        {"label": "Potential Score", "value": "Convenienza Potenziale"},
                                        {"label": "Consistency", "value": "presences"},
                                        {"label": "Goals", "value": "goals"}
                                    ],
                                    value="Convenienza"
                                )
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Bubble Size"),
                                dcc.Dropdown(
                                    id="size-metric-dropdown",
                                    options=[
                                        {"label": "None", "value": "none"},
                                        {"label": "Appearances", "value": "presences"},
                                        {"label": "Goals + Assists", "value": "total_contributions"}
                                    ],
                                    value="presences"
                                )
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Filter"),
                                dbc.Checklist(
                                    id="filter-options",
                                    options=[
                                        {"label": "Top 50 only", "value": "top50"},
                                        {"label": "Show trend line", "value": "trend"}
                                    ],
                                    value=["trend"],
                                    inline=True
                                )
                            ], width=3)
                        ], className="mb-3"),
                        
                        dcc.Graph(id="value-performance-scatter", style={"height": "500px"})
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Team Analysis
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🏟️ Team Performance Breakdown"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id="team-value-distribution", style={"height": "350px"})
                            ], width=6),
                            dbc.Col([
                                dcc.Graph(id="team-role-breakdown", style={"height": "350px"})
                            ], width=6)
                        ])
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Market Opportunities
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("💎 Market Opportunities"),
                    dbc.CardBody([
                        html.Div(id="market-opportunities-table")
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📊 Performance Insights"),
                    dbc.CardBody([
                        html.Div(id="performance-insights")
                    ])
                ])
            ], width=6)
        ])
        
    ], fluid=True)


# Callbacks
@callback(
    [Output("player1-dropdown", "options"),
     Output("player2-dropdown", "options"),
     Output("best-value-player", "children"),
     Output("hidden-gem", "children"),
     Output("trending-up", "children"),
     Output("most-consistent", "children")],
    Input("role-filter-comp", "value")
)
def update_player_options_and_stats(selected_role):
    """Update player dropdown options and quick stats."""
    import dashboard.globals as globals
    data_loader = globals.data_loader
    
    if not data_loader:
        return [], [], "N/A", "N/A", "N/A", "N/A"
    
    # Load both datasets
    fpedia_df = data_loader.load_fpedia_data()
    fstats_df = data_loader.load_fstats_data()
    
    if fpedia_df.empty and fstats_df.empty:
        return [], [], "N/A", "N/A", "N/A", "N/A"
    
    # Combine player names from both datasets
    all_players = set()
    if not fpedia_df.empty:
        fpedia_players = fpedia_df['Nome'].tolist() if 'Nome' in fpedia_df.columns else []
        if selected_role != "ALL" and 'Ruolo' in fpedia_df.columns:
            fpedia_players = fpedia_df[fpedia_df['Ruolo'] == selected_role]['Nome'].tolist()
        all_players.update(fpedia_players)
    
    if not fstats_df.empty:
        fstats_players = fstats_df['Nome'].tolist() if 'Nome' in fstats_df.columns else []
        if selected_role != "ALL" and 'Ruolo' in fstats_df.columns:
            fstats_players = fstats_df[fstats_df['Ruolo'] == selected_role]['Nome'].tolist()
        all_players.update(fstats_players)
    
    player_options = [{"label": name, "value": name} for name in sorted(all_players)]
    
    # Calculate quick stats
    best_value = "N/A"
    hidden_gem = "N/A"
    trending = "N/A"
    consistent = "N/A"
    
    if not fpedia_df.empty and 'Convenienza' in fpedia_df.columns:
        df_filtered = fpedia_df if selected_role == "ALL" else fpedia_df[fpedia_df['Ruolo'] == selected_role]
        if not df_filtered.empty:
            best_value = df_filtered.loc[df_filtered['Convenienza'].idxmax(), 'Nome']
            
            # Hidden gem: high potential convenience but not in top convenience
            if 'Convenienza Potenziale' in df_filtered.columns:
                potential_high = df_filtered.nlargest(20, 'Convenienza Potenziale')
                convenience_low = df_filtered.nsmallest(len(df_filtered)//2, 'Convenienza')
                gems = potential_high[potential_high['Nome'].isin(convenience_low['Nome'])]
                if not gems.empty:
                    hidden_gem = gems.iloc[0]['Nome']
    
    return player_options, player_options, best_value, hidden_gem, trending, consistent


@callback(
    [Output("value-performance-scatter", "figure"),
     Output("team-value-distribution", "figure"),
     Output("team-role-breakdown", "figure"),
     Output("market-opportunities-table", "children"),
     Output("performance-insights", "children")],
    [Input("x-metric-dropdown", "value"),
     Input("y-metric-dropdown", "value"),
     Input("size-metric-dropdown", "value"),
     Input("filter-options", "value"),
     Input("role-filter-comp", "value")]
)
def update_analysis_charts(x_metric, y_metric, size_metric, filters, role_filter):
    """Update all analysis charts."""
    import dashboard.globals as globals
    data_loader = globals.data_loader
    
    empty_fig = go.Figure().add_annotation(
        text="No data available", x=0.5, y=0.5,
        xref="paper", yref="paper", showarrow=False
    )
    
    if not data_loader:
        return empty_fig, empty_fig, empty_fig, "No data", "No data"
    
    # Load data
    fpedia_df = data_loader.load_fpedia_data()
    fstats_df = data_loader.load_fstats_data()
    
    # Use FPEDIA as primary dataset
    df = fpedia_df if not fpedia_df.empty else fstats_df
    
    if df.empty:
        return empty_fig, empty_fig, empty_fig, "No data", "No data"
    
    # Apply role filter
    if role_filter != "ALL" and 'Ruolo' in df.columns:
        df = df[df['Ruolo'] == role_filter]
    
    # Apply top 50 filter if selected
    if 'top50' in (filters or []) and 'Convenienza' in df.columns:
        df = df.nlargest(50, 'Convenienza')
    
    # 1. Value vs Performance Scatter
    scatter_fig = create_scatter_plot(df, x_metric, y_metric, size_metric, 'trend' in (filters or []))
    
    # 2. Team value distribution
    team_fig = create_team_distribution(df)
    
    # 3. Team role breakdown
    role_fig = create_role_breakdown(df)
    
    # 4. Market opportunities table
    opportunities_table = create_opportunities_table(df)
    
    # 5. Performance insights
    insights = create_insights(df)
    
    return scatter_fig, team_fig, role_fig, opportunities_table, insights


@callback(
    Output("radar-comparison", "figure"),
    [Input("player1-dropdown", "value"),
     Input("player2-dropdown", "value"),
     Input("season-toggle", "value")]
)
def update_radar_chart(player1, player2, season):
    """Create radar chart comparing two players."""
    if not player1 and not player2:
        return go.Figure().add_annotation(
            text="Select players to compare", x=0.5, y=0.5,
            xref="paper", yref="paper", showarrow=False, font=dict(size=16)
        )
    
    import dashboard.globals as globals
    data_loader = globals.data_loader
    
    if not data_loader:
        return go.Figure()
    
    fpedia_df = data_loader.load_fpedia_data()
    fstats_df = data_loader.load_fstats_data()
    
    fig = go.Figure()
    
    # Define radar metrics based on available columns
    radar_metrics = []
    if not fpedia_df.empty:
        possible_metrics = ['Convenienza', 'Punteggio', 'Convenienza Potenziale']
        radar_metrics = [m for m in possible_metrics if m in fpedia_df.columns][:6]
    
    if len(radar_metrics) < 3:
        return fig.add_annotation(
            text="Insufficient data for radar chart", x=0.5, y=0.5,
            xref="paper", yref="paper", showarrow=False
        )
    
    colors = ['rgb(67, 156, 209)', 'rgb(209, 67, 67)']
    players = [player1, player2]
    
    for i, player in enumerate(players):
        if not player:
            continue
            
        # Get player data from appropriate dataset
        player_data = None
        if season in ['current', 'both'] and not fpedia_df.empty:
            player_data = fpedia_df[fpedia_df['Nome'] == player]
        
        if player_data is None or player_data.empty:
            if season in ['previous', 'both'] and not fstats_df.empty:
                player_data = fstats_df[fstats_df['Nome'] == player]
        
        if player_data is not None and not player_data.empty:
            values = []
            for metric in radar_metrics:
                if metric in player_data.columns:
                    val = player_data[metric].iloc[0]
                    # Normalize to 0-100 scale
                    if pd.notnull(val):
                        values.append(min(100, max(0, float(val))))
                    else:
                        values.append(0)
                else:
                    values.append(0)
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=radar_metrics,
                fill='toself',
                name=player,
                line_color=colors[i],
                fillcolor=colors[i].replace('rgb', 'rgba').replace(')', ', 0.1)')
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="Player Performance Comparison",
        font=dict(size=12)
    )
    
    return fig


def create_scatter_plot(df, x_metric, y_metric, size_metric, show_trend):
    """Create enhanced scatter plot for value vs performance."""
    if x_metric not in df.columns or y_metric not in df.columns:
        return go.Figure().add_annotation(
            text=f"Metrics not available in dataset", x=0.5, y=0.5,
            xref="paper", yref="paper", showarrow=False
        )
    
    # Prepare data
    plot_df = df.dropna(subset=[x_metric, y_metric])
    
    if plot_df.empty:
        return go.Figure()
    
    # Handle size metric
    size_values = None
    if size_metric != "none" and size_metric in plot_df.columns:
        size_values = plot_df[size_metric]
        # Normalize size values
        if size_values.max() > size_values.min():
            size_values = (size_values - size_values.min()) / (size_values.max() - size_values.min()) * 30 + 10
    
    # Create scatter plot
    fig = px.scatter(
        plot_df,
        x=x_metric,
        y=y_metric,
        color='Ruolo' if 'Ruolo' in plot_df.columns else None,
        size=size_values if size_values is not None else None,
        hover_data=['Nome', 'Squadra'] if 'Nome' in plot_df.columns and 'Squadra' in plot_df.columns else None,
        title=f"{y_metric} vs {x_metric}",
        color_discrete_map={
            'P': '#FF6B6B',
            'D': '#4ECDC4', 
            'C': '#45B7D1',
            'A': '#96CEB4'
        }
    )
    
    # Add quadrant lines (if applicable)
    x_median = plot_df[x_metric].median()
    y_median = plot_df[y_metric].median()
    
    fig.add_hline(y=y_median, line_dash="dot", line_color="gray", opacity=0.5)
    fig.add_vline(x=x_median, line_dash="dot", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    x_range = plot_df[x_metric].max() - plot_df[x_metric].min()
    y_range = plot_df[y_metric].max() - plot_df[y_metric].min()
    
    annotations = [
        dict(x=x_median + x_range*0.25, y=y_median + y_range*0.25, text="⭐ Stars", showarrow=False, bgcolor="rgba(255,255,255,0.8)"),
        dict(x=x_median - x_range*0.25, y=y_median + y_range*0.25, text="💎 Hidden Gems", showarrow=False, bgcolor="rgba(255,255,255,0.8)"),
        dict(x=x_median + x_range*0.25, y=y_median - y_range*0.25, text="📈 Potential", showarrow=False, bgcolor="rgba(255,255,255,0.8)"),
        dict(x=x_median - x_range*0.25, y=y_median - y_range*0.25, text="⚠️ Risky", showarrow=False, bgcolor="rgba(255,255,255,0.8)")
    ]
    
    fig.update_layout(annotations=annotations)
    
    return fig


def create_team_distribution(df):
    """Create team value distribution chart."""
    if 'Squadra' not in df.columns or 'Convenienza' not in df.columns:
        return go.Figure()
    
    # Calculate team averages
    team_stats = df.groupby('Squadra').agg({
        'Convenienza': ['mean', 'count'],
        'Nome': 'count'
    }).round(2)
    
    team_stats.columns = ['Avg_Convenience', 'Convenience_Count', 'Player_Count']
    team_stats = team_stats.reset_index()
    team_stats = team_stats.sort_values('Avg_Convenience', ascending=False).head(10)
    
    fig = px.bar(
        team_stats,
        x='Squadra',
        y='Avg_Convenience',
        title="Top 10 Teams - Average Convenience Score",
        color='Avg_Convenience',
        color_continuous_scale='Viridis'
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig


def create_role_breakdown(df):
    """Create role breakdown chart."""
    if 'Ruolo' not in df.columns:
        return go.Figure()
    
    # Role distribution with convenience scores
    role_stats = df.groupby('Ruolo').agg({
        'Convenienza': ['mean', 'count'] if 'Convenienza' in df.columns else ['count'],
        'Nome': 'count'
    }).round(2)
    
    if 'Convenienza' in df.columns:
        role_stats.columns = ['Avg_Convenience', 'Conv_Count', 'Player_Count']
    else:
        role_stats.columns = ['Player_Count', 'Total_Count']
        
    role_stats = role_stats.reset_index()
    
    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=role_stats['Ruolo'],
        values=role_stats['Player_Count'],
        hole=.3,
        textinfo='label+percent',
        textposition='outside',
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    )])
    
    fig.update_layout(
        title="Player Distribution by Role",
        showlegend=True,
        font=dict(size=12)
    )
    
    return fig


def create_opportunities_table(df):
    """Create market opportunities table."""
    if df.empty or 'Convenienza' not in df.columns:
        return html.P("No data available")
    
    # Find undervalued players (high convenience, low visibility)
    opportunities = df.nlargest(15, 'Convenienza')[['Nome', 'Ruolo', 'Squadra', 'Convenienza']]
    
    if 'Convenienza Potenziale' in df.columns:
        opportunities = opportunities.merge(
            df[['Nome', 'Convenienza Potenziale']], 
            on='Nome', 
            how='left'
        )
    
    return dbc.Table.from_dataframe(
        opportunities.round(2),
        striped=True,
        bordered=True,
        hover=True,
        size="sm",
        className="mt-2"
    )


def create_insights(df):
    """Generate performance insights."""
    if df.empty:
        return html.P("No data available")
    
    insights = []
    
    # Basic stats
    total_players = len(df)
    avg_convenience = df['Convenienza'].mean() if 'Convenienza' in df.columns else 0
    
    insights.append(html.Li(f"📊 Total Players Analyzed: {total_players}"))
    insights.append(html.Li(f"💯 Average Convenience Score: {avg_convenience:.2f}"))
    
    # Role insights
    if 'Ruolo' in df.columns:
        best_role = df.groupby('Ruolo')['Convenienza'].mean().idxmax() if 'Convenienza' in df.columns else None
        if best_role:
            insights.append(html.Li(f"🏆 Best Value Role: {best_role}"))
    
    # Team insights  
    if 'Squadra' in df.columns and 'Convenienza' in df.columns:
        best_team = df.groupby('Squadra')['Convenienza'].mean().idxmax()
        insights.append(html.Li(f"⚽ Best Value Team: {best_team}"))
    
    return html.Ul(insights, className="list-unstyled")