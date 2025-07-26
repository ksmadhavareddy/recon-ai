#!/usr/bin/env python3
"""
Data Service - Handles data loading, merging, and validation
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
import pandas as pd
import os
import tempfile
from typing import Optional, List, Dict, Any
import logging

# Import existing data loader logic
import sys
sys.path.append('..')
from crew.agents.data_loader import DataLoaderAgent
from crew.agents.api_data_loader import APIDataLoaderAgent
from crew.agents.hybrid_data_loader import HybridDataLoaderAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Data Service",
    description="Service for data loading, merging, and validation",
    version="1.0.0"
)

class DataService:
    def __init__(self):
        self.data_loader = None
        self.api_loader = None
        self.hybrid_loader = None
    
    def load_from_files(self, data_dir: str) -> pd.DataFrame:
        """Load data from Excel files"""
        try:
            self.data_loader = DataLoaderAgent(data_dir)
            df = self.data_loader.load_all_data()
            if df is None or df.empty:
                raise ValueError("No data loaded from files")
            return df
        except Exception as e:
            logger.error(f"Error loading data from files: {e}")
            raise
    
    def load_from_api(self, api_config: Dict[str, Any], trade_ids: Optional[List[str]] = None, date: Optional[str] = None) -> pd.DataFrame:
        """Load data from API"""
        try:
            self.api_loader = APIDataLoaderAgent(api_config)
            df = self.api_loader.load_all_data_from_api(trade_ids, date)
            if df is None or df.empty:
                raise ValueError("No data loaded from API")
            return df
        except Exception as e:
            logger.error(f"Error loading data from API: {e}")
            raise
    
    def load_hybrid(self, data_dir: str, api_config: Dict[str, Any], source: str = "auto", trade_ids: Optional[List[str]] = None, date: Optional[str] = None) -> pd.DataFrame:
        """Load data using hybrid approach"""
        try:
            self.hybrid_loader = HybridDataLoaderAgent(data_dir, api_config)
            df = self.hybrid_loader.load_data(source, trade_ids, date)
            if df is None or df.empty:
                raise ValueError("No data loaded from hybrid source")
            return df
        except Exception as e:
            logger.error(f"Error loading data from hybrid source: {e}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data quality and return summary"""
        try:
            validation_result = {
                "total_trades": len(df),
                "columns": list(df.columns),
                "missing_values": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.to_dict(),
                "validation_passed": True,
                "issues": []
            }
            
            # Check for required columns
            required_columns = ['TradeID', 'PV_old', 'PV_new', 'Delta_old', 'Delta_new']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                validation_result["validation_passed"] = False
                validation_result["issues"].append(f"Missing required columns: {missing_columns}")
            
            # Check for duplicate TradeIDs
            if 'TradeID' in df.columns:
                duplicates = df['TradeID'].duplicated().sum()
                if duplicates > 0:
                    validation_result["issues"].append(f"Found {duplicates} duplicate TradeIDs")
            
            return validation_result
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            raise

# Initialize service
data_service = DataService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "data_service"}

@app.post("/load/files")
async def load_from_files(data_dir: str = Query(..., description="Directory containing Excel files")):
    """Load data from Excel files"""
    try:
        df = data_service.load_from_files(data_dir)
        validation = data_service.validate_data(df)
        
        return {
            "status": "success",
            "data_shape": df.shape,
            "validation": validation,
            "message": f"Loaded {len(df)} trades from files"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load/api")
async def load_from_api(
    api_config: Dict[str, Any],
    trade_ids: Optional[List[str]] = None,
    date: Optional[str] = None
):
    """Load data from API"""
    try:
        df = data_service.load_from_api(api_config, trade_ids, date)
        validation = data_service.validate_data(df)
        
        return {
            "status": "success",
            "data_shape": df.shape,
            "validation": validation,
            "message": f"Loaded {len(df)} trades from API"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load/hybrid")
async def load_hybrid(
    data_dir: str = Query(..., description="Directory for file fallback"),
    api_config: Dict[str, Any] = None,
    source: str = Query("auto", description="Data source: files, api, or auto"),
    trade_ids: Optional[List[str]] = None,
    date: Optional[str] = None
):
    """Load data using hybrid approach"""
    try:
        df = data_service.load_hybrid(data_dir, api_config, source, trade_ids, date)
        validation = data_service.validate_data(df)
        
        return {
            "status": "success",
            "data_shape": df.shape,
            "validation": validation,
            "source_used": source,
            "message": f"Loaded {len(df)} trades using hybrid approach"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate")
async def validate_data(data: Dict[str, Any]):
    """Validate data quality"""
    try:
        df = pd.DataFrame(data.get("data", []))
        validation = data_service.validate_data(df)
        
        return {
            "status": "success",
            "validation": validation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources/available")
async def get_available_sources():
    """Get available data sources"""
    return {
        "sources": ["files", "api", "hybrid"],
        "file_formats": ["xlsx", "csv"],
        "api_endpoints": ["pricing", "metadata", "funding"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 