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

# Import unified data loader
import sys
sys.path.append('..')
from crew.agents.unified_data_loader import UnifiedDataLoaderAgent

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
        self.unified_loader = None
    
    def load_data(self, source: str = "auto", data_dir: str = None, api_config: Dict[str, Any] = None, 
                  trade_ids: Optional[List[str]] = None, date: Optional[str] = None) -> pd.DataFrame:
        """Load data using unified loader"""
        try:
            self.unified_loader = UnifiedDataLoaderAgent(data_dir=data_dir, api_config=api_config)
            df = self.unified_loader.load_data(source, trade_ids, date)
            if df is None or df.empty:
                raise ValueError(f"No data loaded from {source} source")
            return df
        except Exception as e:
            logger.error(f"Error loading data from {source}: {e}")
            raise
    
    def load_from_files(self, data_dir: str) -> pd.DataFrame:
        """Load data from Excel files"""
        return self.load_data(source="files", data_dir=data_dir)
    
    def load_from_api(self, api_config: Dict[str, Any], trade_ids: Optional[List[str]] = None, date: Optional[str] = None) -> pd.DataFrame:
        """Load data from API"""
        return self.load_data(source="api", api_config=api_config, trade_ids=trade_ids, date=date)
    
    def load_hybrid(self, data_dir: str, api_config: Dict[str, Any], source: str = "auto", trade_ids: Optional[List[str]] = None, date: Optional[str] = None) -> pd.DataFrame:
        """Load data using hybrid approach"""
        return self.load_data(source=source, data_dir=data_dir, api_config=api_config, trade_ids=trade_ids, date=date)
    
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
    
    def get_available_sources(self) -> Dict[str, bool]:
        """Get available data sources"""
        if self.unified_loader:
            return self.unified_loader.get_available_sources()
        return {"files": False, "api": False}
    
    def get_api_status(self) -> Dict[str, bool]:
        """Get API endpoint status"""
        if self.unified_loader:
            return self.unified_loader.get_api_status()
        return {}

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
    source: str = Query("auto", description="Data source: files, api, auto, or hybrid"),
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
            "message": f"Loaded {len(df)} trades using {source} approach"
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
    sources = data_service.get_available_sources()
    api_status = data_service.get_api_status()
    
    return {
        "sources": sources,
        "api_status": api_status,
        "file_formats": ["xlsx", "csv"],
        "api_endpoints": ["pricing", "metadata", "funding"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 