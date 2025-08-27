import pandas as pd
import os
from typing import Tuple, Optional
from loguru import logger


class DataLoader:
    """Load and cache Excel data for the dashboard."""
    
    def __init__(self, data_dir: str = "data/output"):
        self.data_dir = data_dir
        self.fpedia_path = os.path.join(data_dir, "fpedia_analysis.xlsx")
        self.fstats_path = os.path.join(data_dir, "FSTATS_analysis.xlsx")
        self._fpedia_data = None
        self._fstats_data = None
    
    def load_fpedia_data(self) -> pd.DataFrame:
        """Load FPEDIA analysis data."""
        if self._fpedia_data is None:
            if os.path.exists(self.fpedia_path):
                logger.info(f"Loading FPEDIA data from {self.fpedia_path}")
                self._fpedia_data = pd.read_excel(self.fpedia_path)
                logger.info(f"Loaded {len(self._fpedia_data)} FPEDIA records")
            else:
                logger.warning(f"FPEDIA file not found: {self.fpedia_path}")
                self._fpedia_data = pd.DataFrame()
        return self._fpedia_data
    
    def load_fstats_data(self) -> pd.DataFrame:
        """Load FSTATS analysis data."""
        if self._fstats_data is None:
            if os.path.exists(self.fstats_path):
                logger.info(f"Loading FSTATS data from {self.fstats_path}")
                self._fstats_data = pd.read_excel(self.fstats_path)
                # Clean up nested dict strings in Squadra column
                if 'Squadra' in self._fstats_data.columns:
                    self._fstats_data['Squadra'] = self._fstats_data['Squadra'].apply(
                        lambda x: x.get('name', x) if isinstance(x, dict) else str(x)
                    )
                logger.info(f"Loaded {len(self._fstats_data)} FSTATS records")
            else:
                logger.warning(f"FSTATS file not found: {self.fstats_path}")
                self._fstats_data = pd.DataFrame()
        return self._fstats_data
    
    def load_both(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load both datasets."""
        return self.load_fpedia_data(), self.load_fstats_data()
    
    def get_common_columns(self) -> list:
        """Get columns that exist in both datasets."""
        fpedia_df = self.load_fpedia_data()
        fstats_df = self.load_fstats_data()
        
        if fpedia_df.empty or fstats_df.empty:
            return []
        
        return list(set(fpedia_df.columns) & set(fstats_df.columns))
    
    def get_unique_players(self) -> dict:
        """Get player counts and overlaps between datasets."""
        fpedia_df = self.load_fpedia_data()
        fstats_df = self.load_fstats_data()
        
        if fpedia_df.empty or fstats_df.empty:
            return {}
        
        fpedia_players = set(fpedia_df['Nome'].values) if 'Nome' in fpedia_df.columns else set()
        fstats_players = set(fstats_df['Nome'].values) if 'Nome' in fstats_df.columns else set()
        
        return {
            'fpedia_total': len(fpedia_players),
            'fstats_total': len(fstats_players),
            'common_players': len(fpedia_players & fstats_players),
            'fpedia_unique': len(fpedia_players - fstats_players),
            'fstats_unique': len(fstats_players - fpedia_players)
        }
    
    def refresh_data(self):
        """Clear cached data to force reload."""
        self._fpedia_data = None
        self._fstats_data = None