import pandas as pd
import requests
import json
import os
from typing import Dict, List, Optional, Union
import logging
from pathlib import Path

class UnifiedDataLoaderAgent:
    """
    Unified data loader that can load reconciliation data from files, APIs, or both
    with automatic fallback and source detection.
    """
    
    def __init__(self, 
                 data_dir: str = "data/",
                 api_config: Dict = None,
                 auto_fallback: bool = True):
        """
        Initialize the unified data loader
        
        Args:
            data_dir: Directory containing Excel files
            api_config: API configuration dictionary
            auto_fallback: Whether to automatically fallback to files if API fails
        """
        self.data_dir = Path(data_dir) if data_dir else None
        self.api_config = api_config or {}
        self.auto_fallback = auto_fallback
        
        # Initialize API session if config provided
        self.session = None
        if api_config:
            self.session = requests.Session()
            if api_config.get('api_key'):
                self.session.headers.update({
                    'Authorization': f"Bearer {api_config['api_key']}",
                    'Content-Type': 'application/json'
                })
        
        # Default API endpoints (can be overridden)
        self.endpoints = {
            'old_pricing': '/api/database/old_pricing',
            'new_pricing': '/api/database/new_pricing', 
            'trade_metadata': '/api/database/trade_metadata',
            'funding_reference': '/api/database/funding_model_reference'
        }
        
        # Update with custom endpoints if provided
        if api_config and 'endpoints' in api_config:
            self.endpoints.update(api_config['endpoints'])
    
    def load_data(self, 
                  source: str = "auto",
                  trade_ids: List[str] = None,
                  date: str = None,
                  **kwargs) -> Optional[pd.DataFrame]:
        """
        Load reconciliation data from specified source
        
        Args:
            source: "files", "api", "auto", or "hybrid"
            trade_ids: List of trade IDs (for API filtering)
            date: Specific date (for API filtering)
            **kwargs: Additional arguments passed to specific loaders
            
        Returns:
            DataFrame with merged reconciliation data
        """
        if source == "files":
            return self._load_from_files()
        elif source == "api":
            return self._load_from_api(trade_ids, date)
        elif source == "auto":
            return self._load_auto(trade_ids, date)
        elif source == "hybrid":
            return self._load_hybrid(trade_ids, date)
        else:
            raise ValueError(f"Unknown source: {source}. Use 'files', 'api', 'auto', or 'hybrid'")
    
    def _load_from_files(self) -> Optional[pd.DataFrame]:
        """Load data from Excel files"""
        if not self.data_dir or not self.data_dir.exists():
            logging.error(f"Data directory does not exist: {self.data_dir}")
            return None
        
        try:
            # Load all required files
            files = {
                'old_pricing': self.data_dir / "old_pricing.xlsx",
                'new_pricing': self.data_dir / "new_pricing.xlsx", 
                'trade_metadata': self.data_dir / "trade_metadata.xlsx",
                'funding_reference': self.data_dir / "funding_model_reference.xlsx"
            }
            
            # Check if all files exist
            missing_files = [name for name, path in files.items() if not path.exists()]
            if missing_files:
                logging.error(f"Missing required files: {missing_files}")
                return None
            
            # Load dataframes
            dataframes = {}
            for name, path in files.items():
                dataframes[name] = pd.read_excel(path)
                logging.info(f"Loaded {len(dataframes[name])} rows from {name}")
            
            # Merge data using common logic
            return self._merge_dataframes(dataframes)
            
        except Exception as e:
            logging.error(f"Error loading data from files: {e}")
            return None
    
    def _load_from_api(self, trade_ids: List[str] = None, date: str = None) -> Optional[pd.DataFrame]:
        """Load data from API endpoints"""
        if not self.session:
            logging.error("API session not configured")
            return None
        
        try:
            # Fetch data from all endpoints
            dataframes = {}
            for name, endpoint in self.endpoints.items():
                df = self._fetch_from_api(endpoint, trade_ids, date)
                if df is not None:
                    dataframes[name] = df
                    logging.info(f"Loaded {len(df)} rows from API endpoint {name}")
                else:
                    logging.error(f"Failed to load data from {name}")
                    return None
            
            # Merge data using common logic
            return self._merge_dataframes(dataframes)
            
        except Exception as e:
            logging.error(f"Error loading data from API: {e}")
            return None
    
    def _load_auto(self, trade_ids: List[str] = None, date: str = None) -> Optional[pd.DataFrame]:
        """Auto-detect and load from best available source"""
        # Try API first if configured
        if self.session and self._validate_api_connection():
            logging.info("API connection available, trying API first")
            df = self._load_from_api(trade_ids, date)
            if df is not None and not df.empty:
                return df
        
        # Fallback to files
        logging.info("Loading from files")
        return self._load_from_files()
    
    def _load_hybrid(self, trade_ids: List[str] = None, date: str = None) -> Optional[pd.DataFrame]:
        """Load from both sources and merge, with API as primary"""
        api_df = None
        file_df = None
        
        # Try API first
        if self.session:
            api_df = self._load_from_api(trade_ids, date)
        
        # Try files
        if self.data_dir:
            file_df = self._load_from_files()
        
        # Combine results
        if api_df is not None and file_df is not None:
            # Merge both sources, preferring API data
            logging.info("Merging API and file data")
            return self._merge_hybrid_data(api_df, file_df)
        elif api_df is not None:
            return api_df
        elif file_df is not None:
            return file_df
        else:
            logging.error("No data sources available")
            return None
    
    def _fetch_from_api(self, endpoint: str, trade_ids: List[str] = None, date: str = None) -> Optional[pd.DataFrame]:
        """Fetch data from specific API endpoint"""
        try:
            url = f"{self.api_config.get('base_url', '')}{endpoint}"
            params = {}
            
            if trade_ids:
                params['trade_ids'] = ','.join(trade_ids)
            if date:
                params['date'] = date
            
            timeout = self.api_config.get('timeout', 30)
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, dict):
                if 'data' in data:
                    df = pd.DataFrame(data['data'])
                elif 'results' in data:
                    df = pd.DataFrame(data['results'])
                else:
                    df = pd.DataFrame([data])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                logging.error(f"Unexpected API response format: {type(data)}")
                return None
            
            return df
            
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed for {endpoint}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error processing API response for {endpoint}: {e}")
            return None
    
    def _merge_dataframes(self, dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Merge dataframes using consistent logic across all sources
        
        Args:
            dataframes: Dictionary of dataframes to merge
            
        Returns:
            Merged DataFrame
        """
        if not dataframes:
            return pd.DataFrame()
        
        # Start with old pricing
        if 'old_pricing' in dataframes and 'new_pricing' in dataframes:
            df = dataframes['old_pricing'].merge(
                dataframes['new_pricing'], 
                on="TradeID", 
                how="outer", 
                suffixes=('_old', '_new')
            )
        elif 'old_pricing' in dataframes:
            df = dataframes['old_pricing'].copy()
        elif 'new_pricing' in dataframes:
            df = dataframes['new_pricing'].copy()
        else:
            # If no pricing data, start with first available dataframe
            df = list(dataframes.values())[0].copy()
        
        # Merge metadata if available
        if 'trade_metadata' in dataframes:
            df = df.merge(dataframes['trade_metadata'], on="TradeID", how="left")
        
        # Merge funding reference if available
        if 'funding_reference' in dataframes:
            df = df.merge(dataframes['funding_reference'], on="TradeID", how="left")
        
        logging.info(f"Merged data contains {len(df)} trades")
        return df
    
    def _merge_hybrid_data(self, api_df: pd.DataFrame, file_df: pd.DataFrame) -> pd.DataFrame:
        """Merge data from API and file sources"""
        # Use API data as primary, supplement with file data for missing trades
        merged_df = api_df.copy()
        
        # Find trades in file but not in API
        api_trade_ids = set(api_df['TradeID'].astype(str))
        file_trade_ids = set(file_df['TradeID'].astype(str))
        missing_trade_ids = file_trade_ids - api_trade_ids
        
        if missing_trade_ids:
            missing_data = file_df[file_df['TradeID'].astype(str).isin(missing_trade_ids)]
            merged_df = pd.concat([merged_df, missing_data], ignore_index=True)
            logging.info(f"Added {len(missing_data)} trades from file data")
        
        return merged_df
    
    def _validate_api_connection(self) -> bool:
        """Validate API connection"""
        if not self.session:
            return False
        
        try:
            # Try to fetch a small amount of data to test connection
            test_df = self._fetch_from_api(self.endpoints['old_pricing'])
            return test_df is not None and not test_df.empty
        except:
            return False
    
    def get_available_sources(self) -> Dict[str, bool]:
        """Check which data sources are available"""
        sources = {
            'files': False,
            'api': False
        }
        
        # Check if files exist
        if self.data_dir and self.data_dir.exists():
            required_files = [
                'old_pricing.xlsx',
                'new_pricing.xlsx', 
                'trade_metadata.xlsx',
                'funding_model_reference.xlsx'
            ]
            
            files_exist = all(
                (self.data_dir / file).exists()
                for file in required_files
            )
            sources['files'] = files_exist
        
        # Check if API is available
        sources['api'] = self._validate_api_connection()
        
        return sources
    
    def get_api_status(self) -> Dict[str, bool]:
        """Get detailed API endpoint status"""
        if not self.session:
            return {}
        
        status = {}
        for name, endpoint in self.endpoints.items():
            try:
                url = f"{self.api_config.get('base_url', '')}{endpoint}?limit=1"
                response = self.session.get(url, timeout=5)
                status[name] = response.status_code == 200
            except:
                status[name] = False
        
        return status
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Validate data quality and completeness"""
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
        """Get summary statistics for loaded data"""
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