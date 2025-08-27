import pandas as pd
import numpy as np
from typing import List, Dict, Any


def filter_dataframe(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """Apply filters to dataframe."""
    filtered_df = df.copy()
    
    # Role filter
    if filters.get('roles') and 'Ruolo' in df.columns:
        filtered_df = filtered_df[filtered_df['Ruolo'].isin(filters['roles'])]
    
    # Team filter
    if filters.get('teams') and 'Squadra' in df.columns:
        filtered_df = filtered_df[filtered_df['Squadra'].isin(filters['teams'])]
    
    # Convenience filter
    convenience_filter = filters.get('convenience_filter', 'all')
    if convenience_filter != 'all' and 'Convenienza' in df.columns:
        if convenience_filter == 'top50':
            filtered_df = filtered_df.nlargest(50, 'Convenienza')
        elif convenience_filter == 'top100':
            filtered_df = filtered_df.nlargest(100, 'Convenienza')
        elif convenience_filter == 'above_avg':
            avg_conv = filtered_df['Convenienza'].mean()
            filtered_df = filtered_df[filtered_df['Convenienza'] > avg_conv]
    
    # Legacy convenience range filter (for backward compatibility)
    if filters.get('convenienza_range') and 'Convenienza' in df.columns:
        min_conv, max_conv = filters['convenienza_range']
        filtered_df = filtered_df[
            (filtered_df['Convenienza'] >= min_conv) & 
            (filtered_df['Convenienza'] <= max_conv)
        ]
    
    # Potential convenience range filter
    if filters.get('convenienza_pot_range') and 'Convenienza Potenziale' in df.columns:
        min_conv, max_conv = filters['convenienza_pot_range']
        filtered_df = filtered_df[
            (filtered_df['Convenienza Potenziale'] >= min_conv) & 
            (filtered_df['Convenienza Potenziale'] <= max_conv)
        ]
    
    return filtered_df


def get_top_players(df: pd.DataFrame, column: str = 'Convenienza', n: int = 10) -> pd.DataFrame:
    """Get top N players by specified column."""
    if column not in df.columns or df.empty:
        return pd.DataFrame()
    
    return df.nlargest(n, column)


def get_stats_summary(df: pd.DataFrame, column: str) -> Dict[str, float]:
    """Get statistical summary for a column."""
    if column not in df.columns or df.empty:
        return {}
    
    series = pd.to_numeric(df[column], errors='coerce').dropna()
    
    return {
        'count': len(series),
        'mean': series.mean(),
        'median': series.median(),
        'std': series.std(),
        'min': series.min(),
        'max': series.max(),
        'q25': series.quantile(0.25),
        'q75': series.quantile(0.75)
    }


def get_role_distribution(df: pd.DataFrame) -> pd.Series:
    """Get distribution of players by role."""
    if 'Ruolo' not in df.columns or df.empty:
        return pd.Series()
    
    return df['Ruolo'].value_counts()


def get_team_distribution(df: pd.DataFrame) -> pd.Series:
    """Get distribution of players by team."""
    if 'Squadra' not in df.columns or df.empty:
        return pd.Series()
    
    return df['Squadra'].value_counts()


def merge_datasets_on_name(fpedia_df: pd.DataFrame, fstats_df: pd.DataFrame, 
                          suffix_fpedia: str = '_fpedia', suffix_fstats: str = '_fstats') -> pd.DataFrame:
    """Merge FPEDIA and FSTATS datasets on player name."""
    if fpedia_df.empty or fstats_df.empty:
        return pd.DataFrame()
    
    # Ensure Nome column exists
    if 'Nome' not in fpedia_df.columns or 'Nome' not in fstats_df.columns:
        return pd.DataFrame()
    
    # Merge on Nome
    merged_df = pd.merge(
        fpedia_df, 
        fstats_df, 
        on='Nome', 
        how='inner',
        suffixes=(suffix_fpedia, suffix_fstats)
    )
    
    return merged_df


def prepare_scatter_data(df: pd.DataFrame, x_col: str, y_col: str, 
                        color_col: str = None, size_col: str = None) -> Dict[str, Any]:
    """Prepare data for scatter plot."""
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        return {}
    
    # Convert to numeric
    x_data = pd.to_numeric(df[x_col], errors='coerce')
    y_data = pd.to_numeric(df[y_col], errors='coerce')
    
    # Remove NaN values
    mask = ~(x_data.isna() | y_data.isna())
    
    scatter_data = {
        'x': x_data[mask].tolist(),
        'y': y_data[mask].tolist(),
        'text': df.loc[mask, 'Nome'].tolist() if 'Nome' in df.columns else [],
        'customdata': df.loc[mask].to_dict('records')
    }
    
    if color_col and color_col in df.columns:
        scatter_data['color'] = df.loc[mask, color_col].tolist()
    
    if size_col and size_col in df.columns:
        size_data = pd.to_numeric(df[size_col], errors='coerce')
        scatter_data['size'] = size_data[mask].tolist()
    
    return scatter_data