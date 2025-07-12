from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import sqlite3
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reconciliation Data API",
    description="REST API for fetching reconciliation data from Excel files and databases",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DataService:
    def __init__(self, data_dir="data/", db_path="reconciliation.db"):
        self.data_dir = Path(data_dir)
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with sample data if it doesn't exist"""
        if not os.path.exists(self.db_path):
            self._create_sample_database()
    
    def _create_sample_database(self):
        """Create sample database with data from Excel files"""
        try:
            # Load data from Excel files
            old_pricing = pd.read_excel(self.data_dir / "old_pricing.xlsx")
            new_pricing = pd.read_excel(self.data_dir / "new_pricing.xlsx")
            trade_metadata = pd.read_excel(self.data_dir / "trade_metadata.xlsx")
            funding_model = pd.read_excel(self.data_dir / "funding_model_reference.xlsx")
            
            # Create SQLite database
            conn = sqlite3.connect(self.db_path)
            
            # Save dataframes to database
            old_pricing.to_sql('old_pricing', conn, if_exists='replace', index=False)
            new_pricing.to_sql('new_pricing', conn, if_exists='replace', index=False)
            trade_metadata.to_sql('trade_metadata', conn, if_exists='replace', index=False)
            funding_model.to_sql('funding_model_reference', conn, if_exists='replace', index=False)
            
            # Create merged view
            merged_query = """
            CREATE VIEW IF NOT EXISTS merged_data AS
            SELECT 
                o.*,
                n.PV_new, n.Delta_new,
                t.TradeType, t.Counterparty, t.Notional,
                f.FundingModel, f.FundingRate
            FROM old_pricing o
            LEFT JOIN new_pricing n ON o.TradeID = n.TradeID
            LEFT JOIN trade_metadata t ON o.TradeID = t.TradeID
            LEFT JOIN funding_model_reference f ON o.TradeID = f.TradeID
            """
            conn.execute(merged_query)
            conn.commit()
            conn.close()
            logger.info("Sample database created successfully")
        except Exception as e:
            logger.error(f"Error creating sample database: {e}")
    
    def get_excel_files(self) -> List[Dict[str, Any]]:
        """Get list of available Excel files"""
        files = []
        for file_path in self.data_dir.glob("*.xlsx"):
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(file_path)
            })
        return files
    
    def load_excel_data(self, filename: str) -> Dict[str, Any]:
        """Load data from specific Excel file"""
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
        try:
            df = pd.read_excel(file_path)
            return {
                "filename": filename,
                "rows": len(df),
                "columns": list(df.columns),
                "data": df.to_dict(orient='records'),
                "summary": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "column_types": df.dtypes.to_dict()
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    def get_database_tables(self) -> List[str]:
        """Get list of available database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    
    def query_database(self, table: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Query data from database table"""
        conn = sqlite3.connect(self.db_path)
        
        # Get table info
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total_count = cursor.fetchone()[0]
        
        # Get data
        query = f"SELECT * FROM {table} LIMIT {limit} OFFSET {offset}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return {
            "table": table,
            "total_rows": total_count,
            "returned_rows": len(df),
            "columns": columns,
            "data": df.to_dict(orient='records'),
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }
    
    def get_merged_data(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get merged reconciliation data"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Check if merged_data view exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='merged_data'")
            view_exists = cursor.fetchone() is not None
            
            if not view_exists:
                # Create the merged view if it doesn't exist
                merged_query = """
                CREATE VIEW IF NOT EXISTS merged_data AS
                SELECT 
                    o.*,
                    n.PV_new, n.Delta_new,
                    t.TradeType, t.Counterparty, t.Notional,
                    f.FundingModel, f.FundingRate
                FROM old_pricing o
                LEFT JOIN new_pricing n ON o.TradeID = n.TradeID
                LEFT JOIN trade_metadata t ON o.TradeID = t.TradeID
                LEFT JOIN funding_model_reference f ON o.TradeID = f.TradeID
                """
                conn.execute(merged_query)
                conn.commit()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM merged_data")
            total_count = cursor.fetchone()[0]
            
            # Get data
            query = f"SELECT * FROM merged_data LIMIT {limit} OFFSET {offset}"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return {
                "data_type": "merged_reconciliation_data",
                "total_rows": total_count,
                "returned_rows": len(df),
                "columns": list(df.columns),
                "data": df.to_dict(orient='records'),
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                }
            }
        except Exception as e:
            conn.close()
            raise HTTPException(status_code=500, detail=f"Error accessing merged data: {str(e)}")
    
    def search_data(self, table: str, search_term: str, column: Optional[str] = None) -> Dict[str, Any]:
        """Search data in specified table"""
        conn = sqlite3.connect(self.db_path)
        
        # Get table columns
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Build search query
        if column and column in columns:
            query = f"SELECT * FROM {table} WHERE {column} LIKE ?"
            params = [f"%{search_term}%"]
        else:
            # Search in all text columns
            text_columns = [col for col in columns if col.lower() in ['tradeid', 'tradetype', 'counterparty', 'fundingmodel']]
            if not text_columns:
                text_columns = columns[:1]  # Use first column if no text columns found
            
            conditions = " OR ".join([f"{col} LIKE ?" for col in text_columns])
            query = f"SELECT * FROM {table} WHERE {conditions}"
            params = [f"%{search_term}%" for _ in text_columns]
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return {
            "table": table,
            "search_term": search_term,
            "searched_column": column,
            "results_count": len(df),
            "data": df.to_dict(orient='records')
        }

# Initialize data service
data_service = DataService()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Reconciliation Data API",
        "version": "1.0.0",
        "endpoints": {
            "excel": "/api/excel",
            "database": "/api/database",
            "merged": "/api/merged",
            "search": "/api/search"
        }
    }

@app.get("/api/excel")
async def get_excel_files():
    """Get list of available Excel files"""
    return {
        "files": data_service.get_excel_files(),
        "total_files": len(data_service.get_excel_files())
    }

@app.get("/api/excel/{filename}")
async def get_excel_data(filename: str):
    """Get data from specific Excel file"""
    return data_service.load_excel_data(filename)

@app.get("/api/database")
async def get_database_info():
    """Get database information and available tables"""
    tables = data_service.get_database_tables()
    return {
        "database_path": data_service.db_path,
        "tables": tables,
        "total_tables": len(tables)
    }

@app.get("/api/database/{table}")
async def get_table_data(
    table: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get data from specific database table"""
    return data_service.query_database(table, limit, offset)

@app.get("/api/merged")
async def get_merged_data(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get merged reconciliation data"""
    return data_service.get_merged_data(limit, offset)

@app.get("/api/search")
async def search_data(
    table: str,
    search_term: str,
    column: Optional[str] = None
):
    """Search data in specified table"""
    return data_service.search_data(table, search_term, column)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_dir": str(data_service.data_dir),
        "database_exists": os.path.exists(data_service.db_path)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Reconciliation Data API Server...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔗 Health Check: http://localhost:8000/api/health")
    uvicorn.run(app, host="0.0.0.0", port=8000) 