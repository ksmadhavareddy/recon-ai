import pandas as pd
import requests
import json
from typing import Dict, List, Optional
import logging

class APIDataLoaderAgent:
    """
    Agent for loading reconciliation data from external APIs
    """
    
    def __init__(self, base_url: str = None, api_key: str = None, timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure session headers
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
        
        # API endpoints configuration - Updated to match local REST API server
        self.endpoints = {
            'old_pricing': '/api/database/old_pricing',
            'new_pricing': '/api/database/new_pricing',
            'trade_metadata': '/api/database/trade_metadata',
            'funding_reference': '/api/database/funding_model_reference'
        }
    
    def set_endpoints(self, endpoints: Dict[str, str]):
        """Update API endpoints configuration"""
        self.endpoints.update(endpoints)
    
    def set_headers(self, headers: Dict[str, str]):
        """Set custom headers for API requests"""
        self.session.headers.update(headers)
    
    def fetch_data(self, endpoint: str, params: Dict = None) -> Optional[pd.DataFrame]:
        """
        Fetch data from API endpoint
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            DataFrame with fetched data or None if error
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, dict):
                if 'data' in data:
                    # Local API server format
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
    
    def fetch_old_pricing(self, trade_ids: List[str] = None, date: str = None) -> Optional[pd.DataFrame]:
        """
        Fetch old pricing data from API
        
        Args:
            trade_ids: List of trade IDs to fetch (optional)
            date: Specific date for pricing data (optional)
            
        Returns:
            DataFrame with old pricing data
        """
        params = {}
        if trade_ids:
            params['trade_ids'] = ','.join(trade_ids)
        if date:
            params['date'] = date
            
        return self.fetch_data(self.endpoints['old_pricing'], params)
    
    def fetch_new_pricing(self, trade_ids: List[str] = None, date: str = None) -> Optional[pd.DataFrame]:
        """
        Fetch new pricing data from API
        
        Args:
            trade_ids: List of trade IDs to fetch (optional)
            date: Specific date for pricing data (optional)
            
        Returns:
            DataFrame with new pricing data
        """
        params = {}
        if trade_ids:
            params['trade_ids'] = ','.join(trade_ids)
        if date:
            params['date'] = date
            
        return self.fetch_data(self.endpoints['new_pricing'], params)
    
    def fetch_trade_metadata(self, trade_ids: List[str] = None) -> Optional[pd.DataFrame]:
        """
        Fetch trade metadata from API
        
        Args:
            trade_ids: List of trade IDs to fetch (optional)
            
        Returns:
            DataFrame with trade metadata
        """
        params = {}
        if trade_ids:
            params['trade_ids'] = ','.join(trade_ids)
            
        return self.fetch_data(self.endpoints['trade_metadata'], params)
    
    def fetch_funding_reference(self, trade_ids: List[str] = None) -> Optional[pd.DataFrame]:
        """
        Fetch funding reference data from API
        
        Args:
            trade_ids: List of trade IDs to fetch (optional)
            
        Returns:
            DataFrame with funding reference data
        """
        params = {}
        if trade_ids:
            params['trade_ids'] = ','.join(trade_ids)
            
        return self.fetch_data(self.endpoints['funding_reference'], params)
    
    def load_all_data_from_api(self, trade_ids: List[str] = None, date: str = None) -> Optional[pd.DataFrame]:
        """
        Load all reconciliation data from APIs and merge into single DataFrame
        
        Args:
            trade_ids: List of trade IDs to fetch (optional)
            date: Specific date for pricing data (optional)
            
        Returns:
            Merged DataFrame with all reconciliation data
        """
        try:
            # Fetch all data sources
            old_pricing = self.fetch_old_pricing(trade_ids, date)
            new_pricing = self.fetch_new_pricing(trade_ids, date)
            metadata = self.fetch_trade_metadata(trade_ids)
            funding = self.fetch_funding_reference(trade_ids)
            
            # Check if all data sources were fetched successfully
            if old_pricing is None or new_pricing is None or metadata is None or funding is None:
                logging.error("Failed to fetch one or more data sources from API")
                return None
            
            # Merge data sources (same logic as file-based loader)
            df = old_pricing.merge(new_pricing, on="TradeID", how="outer", suffixes=('_old', '_new'))
            df = df.merge(metadata, on="TradeID", how="left")
            df = df.merge(funding, on="TradeID", how="left")
            
            logging.info(f"Successfully loaded {len(df)} trades from API")
            return df
            
        except Exception as e:
            logging.error(f"Error loading data from API: {e}")
            return None
    
    def get_api_status(self) -> Dict[str, bool]:
        """
        Check status of all API endpoints
        
        Returns:
            Dictionary with endpoint status
        """
        status = {}
        
        for name, endpoint in self.endpoints.items():
            try:
                response = self.session.get(f"{self.base_url}{endpoint}?limit=1", timeout=5)
                status[name] = response.status_code == 200
            except:
                status[name] = False
        
        return status
    
    def validate_api_connection(self) -> bool:
        """
        Validate API connection and authentication
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try to fetch a small amount of data to test connection
            test_df = self.fetch_old_pricing()
            return test_df is not None and not test_df.empty
        except:
            return False 