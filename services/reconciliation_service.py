#!/usr/bin/env python3
"""
Reconciliation Service - Handles mismatch detection and rule-based analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Dict, Any, List, Optional
import logging

# Import existing reconciliation logic
import sys
sys.path.append('..')
from crew.agents.recon_agent import ReconAgent
from crew.agents.analyzer_agent import AnalyzerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reconciliation Service",
    description="Service for mismatch detection and rule-based analysis",
    version="1.0.0"
)

class ReconciliationService:
    def __init__(self):
        self.recon_agent = ReconAgent()
        self.analyzer_agent = AnalyzerAgent()
    
    def detect_mismatches(self, df: pd.DataFrame, pv_tolerance: float = 1000, delta_tolerance: float = 0.05) -> pd.DataFrame:
        """Detect PV and Delta mismatches"""
        try:
            # Update tolerances
            self.recon_agent.pv_tolerance = pv_tolerance
            self.recon_agent.delta_tolerance = delta_tolerance
            
            # Add mismatch flags
            df_with_flags = self.recon_agent.add_diff_flags(df)
            
            logger.info(f"Detected mismatches: PV={df_with_flags['PV_Mismatch'].sum()}, Delta={df_with_flags['Delta_Mismatch'].sum()}")
            return df_with_flags
        except Exception as e:
            logger.error(f"Error detecting mismatches: {e}")
            raise
    
    def apply_rule_based_diagnosis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply rule-based diagnosis to flagged trades"""
        try:
            df_with_diagnosis = self.analyzer_agent.apply(df)
            
            # Count diagnoses
            diagnosis_counts = df_with_diagnosis['Diagnosis'].value_counts().to_dict()
            logger.info(f"Applied rule-based diagnosis: {diagnosis_counts}")
            
            return df_with_diagnosis
        except Exception as e:
            logger.error(f"Error applying rule-based diagnosis: {e}")
            raise
    
    def get_mismatch_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary of mismatches and diagnoses"""
        try:
            summary = {
                "total_trades": len(df),
                "pv_mismatches": df['PV_Mismatch'].sum() if 'PV_Mismatch' in df.columns else 0,
                "delta_mismatches": df['Delta_Mismatch'].sum() if 'Delta_Mismatch' in df.columns else 0,
                "any_mismatches": df['Any_Mismatch'].sum() if 'Any_Mismatch' in df.columns else 0,
                "diagnosis_distribution": df['Diagnosis'].value_counts().to_dict() if 'Diagnosis' in df.columns else {},
                "mismatch_rate": (df['Any_Mismatch'].sum() / len(df) * 100) if 'Any_Mismatch' in df.columns else 0
            }
            
            return summary
        except Exception as e:
            logger.error(f"Error generating mismatch summary: {e}")
            raise
    
    def get_trade_details(self, df: pd.DataFrame, trade_id: str) -> Dict[str, Any]:
        """Get detailed analysis for a specific trade"""
        try:
            trade_data = df[df['TradeID'] == trade_id]
            if trade_data.empty:
                raise ValueError(f"Trade {trade_id} not found")
            
            trade = trade_data.iloc[0]
            details = {
                "trade_id": trade_id,
                "pv_old": trade.get('PV_old'),
                "pv_new": trade.get('PV_new'),
                "pv_diff": trade.get('PV_Diff'),
                "pv_mismatch": trade.get('PV_Mismatch', False),
                "delta_old": trade.get('Delta_old'),
                "delta_new": trade.get('Delta_new'),
                "delta_diff": trade.get('Delta_Diff'),
                "delta_mismatch": trade.get('Delta_Mismatch', False),
                "any_mismatch": trade.get('Any_Mismatch', False),
                "diagnosis": trade.get('Diagnosis'),
                "product_type": trade.get('ProductType'),
                "funding_curve": trade.get('FundingCurve'),
                "csa_type": trade.get('CSA_Type'),
                "model_version": trade.get('ModelVersion')
            }
            
            return details
        except Exception as e:
            logger.error(f"Error getting trade details: {e}")
            raise

# Initialize service
reconciliation_service = ReconciliationService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "reconciliation_service"}

@app.post("/detect-mismatches")
async def detect_mismatches(
    data: Dict[str, Any],
    pv_tolerance: float = 1000,
    delta_tolerance: float = 0.05
):
    """Detect PV and Delta mismatches in the data"""
    try:
        df = pd.DataFrame(data.get("data", []))
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        df_with_flags = reconciliation_service.detect_mismatches(df, pv_tolerance, delta_tolerance)
        
        return {
            "status": "success",
            "data": df_with_flags.to_dict(orient='records'),
            "summary": reconciliation_service.get_mismatch_summary(df_with_flags),
            "message": f"Detected mismatches with tolerances: PV={pv_tolerance}, Delta={delta_tolerance}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/apply-diagnosis")
async def apply_diagnosis(data: Dict[str, Any]):
    """Apply rule-based diagnosis to the data"""
    try:
        df = pd.DataFrame(data.get("data", []))
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        df_with_diagnosis = reconciliation_service.apply_rule_based_diagnosis(df)
        
        return {
            "status": "success",
            "data": df_with_diagnosis.to_dict(orient='records'),
            "summary": reconciliation_service.get_mismatch_summary(df_with_diagnosis),
            "message": "Applied rule-based diagnosis"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/full-reconciliation")
async def full_reconciliation(
    data: Dict[str, Any],
    pv_tolerance: float = 1000,
    delta_tolerance: float = 0.05
):
    """Perform full reconciliation (mismatch detection + diagnosis)"""
    try:
        df = pd.DataFrame(data.get("data", []))
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        # Step 1: Detect mismatches
        df_with_flags = reconciliation_service.detect_mismatches(df, pv_tolerance, delta_tolerance)
        
        # Step 2: Apply diagnosis
        df_with_diagnosis = reconciliation_service.apply_rule_based_diagnosis(df_with_flags)
        
        return {
            "status": "success",
            "data": df_with_diagnosis.to_dict(orient='records'),
            "summary": reconciliation_service.get_mismatch_summary(df_with_diagnosis),
            "message": "Completed full reconciliation analysis"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trade/{trade_id}")
async def get_trade_details(trade_id: str, data: Dict[str, Any]):
    """Get detailed analysis for a specific trade"""
    try:
        df = pd.DataFrame(data.get("data", []))
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        trade_details = reconciliation_service.get_trade_details(df, trade_id)
        
        return {
            "status": "success",
            "trade_details": trade_details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary")
async def get_summary(data: Dict[str, Any]):
    """Get reconciliation summary"""
    try:
        df = pd.DataFrame(data.get("data", []))
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        summary = reconciliation_service.get_mismatch_summary(df)
        
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/tolerances")
async def get_tolerance_config():
    """Get current tolerance configuration"""
    return {
        "pv_tolerance": reconciliation_service.recon_agent.pv_tolerance,
        "delta_tolerance": reconciliation_service.recon_agent.delta_tolerance
    }

@app.post("/config/tolerances")
async def update_tolerance_config(pv_tolerance: float, delta_tolerance: float):
    """Update tolerance configuration"""
    try:
        reconciliation_service.recon_agent.pv_tolerance = pv_tolerance
        reconciliation_service.recon_agent.delta_tolerance = delta_tolerance
        
        return {
            "status": "success",
            "message": f"Updated tolerances: PV={pv_tolerance}, Delta={delta_tolerance}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 