import pandas as pd
import os
from typing import Dict, List, Optional, Union
import logging
from .data_loader import DataLoaderAgent
from .api_data_loader import APIDataLoaderAgent

class HybridDataLoaderAgent:
    """
    Hybrid data loader that can load reconciliation data from files or APIs
    """
    
    def __init__(self, data_dir: str = "data/", api_config: Dict = None):
        self.data_dir = data_dir
        # Only create file loader if data_dir is provided
        self.file_loader = DataLoaderAgent(data_dir) if data_dir else None
        self.api_loader = None
        
        # Initialize API loader if config provided
        if api_config:
            self.api_loader = APIDataLoaderAgent(
                base_url=api_config.get('base_url'),
                api_key=api_config.get('api_key'),
                timeout=api_config.get('timeout', 30)
            )
            
            # Set custom endpoints if provided
            if 'endpoints' in api_config:
                self.api_loader.set_endpoints(api_config['endpoints'])
            
            # Set custom headers if provided
            if 'headers' in api_config:
                self.api_loader.set_headers(api_config['headers'])
    
    def load_from_files(self) -> Optional[pd.DataFrame]:
        """Load data from files"""
        if not self.file_loader:
            logging.error("File loader not configured (no data_dir provided)")
            return None
        
        try:
            return self.file_loader.load_all_data()
        except Exception as e:
            logging.error(f"Error loading data from files: {e}")
            return None
    
    def load_from_api(self, trade_ids: List[str] = None, date: str = None) -> Optional[pd.DataFrame]:
        """Load data from API"""
        if not self.api_loader:
            logging.error("API loader not configured")
            return None
        
        try:
            return self.api_loader.load_all_data_from_api(trade_ids, date)
        except Exception as e:
            logging.error(f"Error loading data from API: {e}")
            return None
    
    def load_data(self, source: str = "auto", trade_ids: List[str] = None, date: str = None) -> Optional[pd.DataFrame]:
        """
        Load data from specified source or auto-detect
        
        Args:
            source: "files", "api", or "auto"
            trade_ids: List of trade IDs (for API)
            date: Specific date (for API)
            
        Returns:
            DataFrame with reconciliation data
        """
        if source == "files":
            return self.load_from_files()
        elif source == "api":
            return self.load_from_api(trade_ids, date)
        elif source == "auto":
            return self.load_auto(trade_ids, date)
        else:
            logging.error(f"Unknown data source: {source}")
            return None
    
    def load_auto(self, trade_ids: List[str] = None, date: str = None) -> Optional[pd.DataFrame]:
        """
        Auto-detect and load data from best available source
        
        Args:
            trade_ids: List of trade IDs (for API)
            date: Specific date (for API)
            
        Returns:
            DataFrame with reconciliation data
        """
        # Check if API is available and configured
        if self.api_loader and self.api_loader.validate_api_connection():
            logging.info("API connection available, loading from API")
            df = self.load_from_api(trade_ids, date)
            if df is not None and not df.empty:
                return df
        
        # Fallback to files
        logging.info("Loading from files")
        return self.load_from_files()
    
    def get_available_sources(self) -> Dict[str, bool]:
        """
        Check which data sources are available
        
        Returns:
            Dictionary with source availability status
        """
        sources = {
            'files': False,
            'api': False
        }
        
        # Check if files exist
        if self.data_dir:
            required_files = [
                'old_pricing.xlsx',
                'new_pricing.xlsx',
                'trade_metadata.xlsx',
                'funding_model_reference.xlsx'
            ]
            
            files_exist = all(
                os.path.exists(os.path.join(self.data_dir, file))
                for file in required_files
            )
            sources['files'] = files_exist
        else:
            sources['files'] = False
        
        # Check if API is available
        if self.api_loader:
            sources['api'] = self.api_loader.validate_api_connection()
        
        return sources
    
    def get_api_status(self) -> Dict[str, bool]:
        """Get detailed API endpoint status"""
        if self.api_loader:
            return self.api_loader.get_api_status()
        return {}
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate data quality and completeness
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'has_data': False,
            'has_required_columns': False,
            'has_pricing_data': False,
            'has_metadata': False,
            'has_funding_data': False
        }
        
        if df is None or df.empty:
            return validation
        
        validation['has_data'] = True
        
        # Check required columns
        required_columns = ['TradeID']
        validation['has_required_columns'] = all(col in df.columns for col in required_columns)
        
        # Check pricing data
        pricing_columns = ['PV_old', 'PV_new', 'Delta_old', 'Delta_new']
        validation['has_pricing_data'] = all(col in df.columns for col in pricing_columns)
        
        # Check metadata
        metadata_columns = ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']
        validation['has_metadata'] = all(col in df.columns for col in metadata_columns)
        
        # Check funding data (optional)
        funding_columns = ['FundingRate', 'CollateralType', 'MarginType']
        validation['has_funding_data'] = any(col in df.columns for col in funding_columns)
        
        return validation
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics for loaded data
        
        Args:
            df: DataFrame to summarize
            
        Returns:
            Dictionary with summary statistics
        """
        if df is None or df.empty:
            return {'total_trades': 0, 'source': 'none'}
        
        summary = {
            'total_trades': len(df),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict()
        }
        
        # Add pricing statistics if available
        if 'PV_old' in df.columns and 'PV_new' in df.columns:
            summary['pv_stats'] = {
                'old_mean': df['PV_old'].mean(),
                'new_mean': df['PV_new'].mean(),
                'old_std': df['PV_old'].std(),
                'new_std': df['PV_new'].std()
            }
        
        if 'Delta_old' in df.columns and 'Delta_new' in df.columns:
            summary['delta_stats'] = {
                'old_mean': df['Delta_old'].mean(),
                'new_mean': df['Delta_new'].mean(),
                'old_std': df['Delta_old'].std(),
                'new_std': df['Delta_new'].std()
            }
        
        return summary 