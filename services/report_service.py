#!/usr/bin/env python3
"""
Report Service - Handles report generation and export functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
from typing import Dict, Any, List, Optional
import logging
import os
import tempfile
from datetime import datetime

# Import existing report logic
import sys
sys.path.append('..')
from crew.agents.narrator_agent import NarratorAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Report Service",
    description="Service for report generation and export functionality",
    version="1.0.0"
)

class ReportService:
    def __init__(self):
        self.narrator_agent = NarratorAgent()
        self.report_dir = "reports"
        
        # Create reports directory if it doesn't exist
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
    
    def generate_summary_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a summary report of the reconciliation analysis"""
        try:
            # Calculate summary statistics
            total_trades = len(df)
            pv_mismatches = df['PV_Mismatch'].sum() if 'PV_Mismatch' in df.columns else 0
            delta_mismatches = df['Delta_Mismatch'].sum() if 'Delta_Mismatch' in df.columns else 0
            any_mismatches = df['Any_Mismatch'].sum() if 'Any_Mismatch' in df.columns else 0
            
            # Get diagnosis distribution
            diagnosis_distribution = {}
            if 'Diagnosis' in df.columns:
                diagnosis_distribution = df['Diagnosis'].value_counts().to_dict()
            
            # Get product type distribution
            product_distribution = {}
            if 'ProductType' in df.columns:
                product_distribution = df['ProductType'].value_counts().to_dict()
            
            summary = {
                "total_trades": total_trades,
                "pv_mismatches": pv_mismatches,
                "delta_mismatches": delta_mismatches,
                "any_mismatches": any_mismatches,
                "mismatch_rate": (any_mismatches / total_trades * 100) if total_trades > 0 else 0,
                "diagnosis_distribution": diagnosis_distribution,
                "product_distribution": product_distribution,
                "generated_at": datetime.now().isoformat()
            }
            
            return summary
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            raise
    
    def generate_detailed_report(self, df: pd.DataFrame, format: str = "excel") -> str:
        """Generate a detailed report and save to file"""
        try:
            # Generate summary
            summary = self.generate_summary_report(df)
            
            # Create detailed report with all data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reconciliation_report_{timestamp}"
            
            if format.lower() == "excel":
                filepath = os.path.join(self.report_dir, f"{filename}.xlsx")
                
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    # Summary sheet
                    summary_df = pd.DataFrame([summary])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Detailed data sheet
                    df.to_excel(writer, sheet_name='Detailed_Data', index=False)
                    
                    # Mismatches only sheet
                    if 'Any_Mismatch' in df.columns:
                        mismatches_df = df[df['Any_Mismatch'] == True]
                        if not mismatches_df.empty:
                            mismatches_df.to_excel(writer, sheet_name='Mismatches_Only', index=False)
                
                logger.info(f"Generated Excel report: {filepath}")
                return filepath
            
            elif format.lower() == "csv":
                filepath = os.path.join(self.report_dir, f"{filename}.csv")
                df.to_csv(filepath, index=False)
                logger.info(f"Generated CSV report: {filepath}")
                return filepath
            
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error generating detailed report: {e}")
            raise
    
    def generate_narrative_report(self, df: pd.DataFrame) -> str:
        """Generate a narrative report using the narrator agent"""
        try:
            # Generate narrative using the narrator agent
            narrative = self.narrator_agent.generate_narrative(df)
            
            # Save narrative to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.report_dir, f"narrative_report_{timestamp}.txt")
            
            with open(filepath, 'w') as f:
                f.write(narrative)
            
            logger.info(f"Generated narrative report: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error generating narrative report: {e}")
            raise
    
    def get_report_list(self) -> List[Dict[str, Any]]:
        """Get list of available reports"""
        try:
            reports = []
            for filename in os.listdir(self.report_dir):
                if filename.endswith(('.xlsx', '.csv', '.txt')):
                    filepath = os.path.join(self.report_dir, filename)
                    file_stats = os.stat(filepath)
                    
                    reports.append({
                        "filename": filename,
                        "filepath": filepath,
                        "size_bytes": file_stats.st_size,
                        "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "type": filename.split('.')[-1]
                    })
            
            # Sort by modification time (newest first)
            reports.sort(key=lambda x: x['modified_at'], reverse=True)
            return reports
        except Exception as e:
            logger.error(f"Error getting report list: {e}")
            raise
    
    def delete_report(self, filename: str) -> bool:
        """Delete a specific report file"""
        try:
            filepath = os.path.join(self.report_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted report: {filepath}")
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error deleting report: {e}")
            raise
    
    def get_trade_analysis(self, df: pd.DataFrame, trade_id: str) -> Dict[str, Any]:
        """Get detailed analysis for a specific trade"""
        try:
            trade_data = df[df['TradeID'] == trade_id]
            if trade_data.empty:
                raise ValueError(f"Trade {trade_id} not found")
            
            trade = trade_data.iloc[0]
            
            analysis = {
                "trade_id": trade_id,
                "analysis": {
                    "pv_analysis": {
                        "old_value": trade.get('PV_old'),
                        "new_value": trade.get('PV_new'),
                        "difference": trade.get('PV_Diff'),
                        "is_mismatch": trade.get('PV_Mismatch', False)
                    },
                    "delta_analysis": {
                        "old_value": trade.get('Delta_old'),
                        "new_value": trade.get('Delta_new'),
                        "difference": trade.get('Delta_Diff'),
                        "is_mismatch": trade.get('Delta_Mismatch', False)
                    },
                    "diagnosis": trade.get('Diagnosis'),
                    "product_info": {
                        "product_type": trade.get('ProductType'),
                        "funding_curve": trade.get('FundingCurve'),
                        "csa_type": trade.get('CSA_Type'),
                        "model_version": trade.get('ModelVersion')
                    }
                }
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error getting trade analysis: {e}")
            raise

# Initialize service
report_service = ReportService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "report_service"}

@app.post("/summary")
async def generate_summary(data: Dict[str, Any]):
    """Generate a summary report"""
    try:
        df = pd.DataFrame(data.get("data", []))
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        summary = report_service.generate_summary_report(df)
        
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detailed")
async def generate_detailed_report(
    data: Dict[str, Any],
    format: str = "excel"
):
    """Generate a detailed report"""
    try:
        df = pd.DataFrame(data.get("data", []))
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        filepath = report_service.generate_detailed_report(df, format)
        
        return {
            "status": "success",
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "format": format,
            "message": f"Generated {format} report"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/narrative")
async def generate_narrative_report(data: Dict[str, Any]):
    """Generate a narrative report"""
    try:
        df = pd.DataFrame(data.get("data", []))
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        filepath = report_service.generate_narrative_report(df)
        
        return {
            "status": "success",
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "message": "Generated narrative report"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list")
async def get_reports():
    """Get list of available reports"""
    try:
        reports = report_service.get_report_list()
        
        return {
            "status": "success",
            "reports": reports,
            "count": len(reports)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_report(filename: str):
    """Download a specific report file"""
    try:
        filepath = os.path.join(report_service.report_dir, filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/{filename}")
async def delete_report(filename: str):
    """Delete a specific report file"""
    try:
        success = report_service.delete_report(filename)
        
        if success:
            return {
                "status": "success",
                "message": f"Deleted report: {filename}"
            }
        else:
            raise HTTPException(status_code=404, detail="Report not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trade/{trade_id}")
async def get_trade_analysis(trade_id: str, data: Dict[str, Any]):
    """Get detailed analysis for a specific trade"""
    try:
        df = pd.DataFrame(data.get("data", []))
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        analysis = report_service.get_trade_analysis(df, trade_id)
        
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/formats/available")
async def get_available_formats():
    """Get available report formats"""
    return {
        "formats": [
            {"name": "Excel", "extension": "xlsx", "description": "Multi-sheet Excel file with summary and detailed data"},
            {"name": "CSV", "extension": "csv", "description": "Comma-separated values file"},
            {"name": "Narrative", "extension": "txt", "description": "Text-based narrative report"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 