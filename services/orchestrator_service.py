#!/usr/bin/env python3
"""
Orchestrator Service - Coordinates between all other services
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Dict, Any, List, Optional
import logging
import httpx
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Orchestrator Service",
    description="Service that coordinates between all other services",
    version="1.0.0"
)

class OrchestratorService:
    def __init__(self):
        self.service_urls = {
            "data": "http://localhost:8001",
            "reconciliation": "http://localhost:8002", 
            "ml": "http://localhost:8003",
            "report": "http://localhost:8004"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def check_service_health(self) -> Dict[str, Any]:
        """Check health of all services"""
        health_status = {}
        
        for service_name, url in self.service_urls.items():
            try:
                response = await self.client.get(f"{url}/health")
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": url,
                    "response_time": response.elapsed.total_seconds()
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unhealthy",
                    "url": url,
                    "error": str(e)
                }
        
        return health_status
    
    async def run_full_reconciliation(self, 
                                   data_source: str = "files",
                                   data_dir: str = None,
                                   api_config: Dict[str, Any] = None,
                                   trade_ids: List[str] = None,
                                   date: str = None,
                                   pv_tolerance: float = 1000,
                                   delta_tolerance: float = 0.05,
                                   train_ml: bool = True,
                                   generate_reports: bool = True) -> Dict[str, Any]:
        """Run the complete reconciliation workflow"""
        try:
            workflow_result = {
                "workflow_id": f"recon_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "start_time": datetime.now().isoformat(),
                "steps": [],
                "results": {}
            }
            
            # Step 1: Load Data
            logger.info("Step 1: Loading data...")
            if data_source == "files":
                response = await self.client.post(
                    f"{self.service_urls['data']}/load/files",
                    params={"data_dir": data_dir}
                )
            elif data_source == "api":
                response = await self.client.post(
                    f"{self.service_urls['data']}/load/api",
                    json={"api_config": api_config, "trade_ids": trade_ids, "date": date}
                )
            else:  # hybrid
                response = await self.client.post(
                    f"{self.service_urls['data']}/load/hybrid",
                    params={"data_dir": data_dir, "source": data_source},
                    json={"api_config": api_config, "trade_ids": trade_ids, "date": date}
                )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Data loading failed: {response.text}")
            
            data_result = response.json()
            workflow_result["steps"].append({
                "step": "data_loading",
                "status": "completed",
                "result": data_result
            })
            
            # Step 2: Reconciliation Analysis
            logger.info("Step 2: Running reconciliation analysis...")
            response = await self.client.post(
                f"{self.service_urls['reconciliation']}/full-reconciliation",
                json={"data": data_result.get("data", [])},
                params={"pv_tolerance": pv_tolerance, "delta_tolerance": delta_tolerance}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Reconciliation failed: {response.text}")
            
            recon_result = response.json()
            workflow_result["steps"].append({
                "step": "reconciliation",
                "status": "completed", 
                "result": recon_result
            })
            
            # Step 3: ML Training (if requested)
            if train_ml:
                logger.info("Step 3: Training ML model...")
                response = await self.client.post(
                    f"{self.service_urls['ml']}/train",
                    json={"data": recon_result.get("data", [])}
                )
                
                if response.status_code == 200:
                    ml_result = response.json()
                    workflow_result["steps"].append({
                        "step": "ml_training",
                        "status": "completed",
                        "result": ml_result
                    })
                else:
                    workflow_result["steps"].append({
                        "step": "ml_training",
                        "status": "failed",
                        "error": response.text
                    })
            
            # Step 4: Generate Reports (if requested)
            if generate_reports:
                logger.info("Step 4: Generating reports...")
                
                # Generate summary report
                response = await self.client.post(
                    f"{self.service_urls['report']}/summary",
                    json={"data": recon_result.get("data", [])}
                )
                
                if response.status_code == 200:
                    summary_result = response.json()
                    workflow_result["steps"].append({
                        "step": "summary_report",
                        "status": "completed",
                        "result": summary_result
                    })
                
                # Generate detailed report
                response = await self.client.post(
                    f"{self.service_urls['report']}/detailed",
                    json={"data": recon_result.get("data", [])},
                    params={"format": "excel"}
                )
                
                if response.status_code == 200:
                    detailed_result = response.json()
                    workflow_result["steps"].append({
                        "step": "detailed_report",
                        "status": "completed",
                        "result": detailed_result
                    })
            
            workflow_result["end_time"] = datetime.now().isoformat()
            workflow_result["status"] = "completed"
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            workflow_result["end_time"] = datetime.now().isoformat()
            workflow_result["status"] = "failed"
            workflow_result["error"] = str(e)
            return workflow_result
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all services"""
        try:
            health_status = await self.check_service_health()
            
            # Get additional info from each service
            service_info = {}
            
            for service_name, url in self.service_urls.items():
                if health_status[service_name]["status"] == "healthy":
                    try:
                        # Get service-specific info
                        if service_name == "ml":
                            response = await self.client.get(f"{url}/model/info")
                            if response.status_code == 200:
                                service_info[service_name] = response.json()
                        
                        elif service_name == "report":
                            response = await self.client.get(f"{url}/list")
                            if response.status_code == 200:
                                service_info[service_name] = response.json()
                        
                        elif service_name == "reconciliation":
                            response = await self.client.get(f"{url}/config/tolerances")
                            if response.status_code == 200:
                                service_info[service_name] = response.json()
                        
                        elif service_name == "data":
                            response = await self.client.get(f"{url}/sources/available")
                            if response.status_code == 200:
                                service_info[service_name] = response.json()
                    
                    except Exception as e:
                        service_info[service_name] = {"error": str(e)}
            
            return {
                "health_status": health_status,
                "service_info": service_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            raise
    
    async def cleanup_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Cleanup resources for a specific workflow"""
        try:
            # This could include cleaning up temporary files, resetting models, etc.
            cleanup_result = {
                "workflow_id": workflow_id,
                "cleanup_time": datetime.now().isoformat(),
                "actions": []
            }
            
            # Example cleanup actions
            cleanup_result["actions"].append("Workflow cleanup completed")
            
            return cleanup_result
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise

# Initialize service
orchestrator_service = OrchestratorService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "orchestrator_service"}

@app.get("/services/health")
async def check_services_health():
    """Check health of all services"""
    try:
        health_status = await orchestrator_service.check_service_health()
        
        return {
            "status": "success",
            "health_status": health_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/services/status")
async def get_services_status():
    """Get comprehensive status of all services"""
    try:
        status = await orchestrator_service.get_service_status()
        
        return {
            "status": "success",
            "services_status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow/run")
async def run_workflow(
    data_source: str = "files",
    data_dir: str = None,
    api_config: Dict[str, Any] = None,
    trade_ids: List[str] = None,
    date: str = None,
    pv_tolerance: float = 1000,
    delta_tolerance: float = 0.05,
    train_ml: bool = True,
    generate_reports: bool = True
):
    """Run the complete reconciliation workflow"""
    try:
        workflow_result = await orchestrator_service.run_full_reconciliation(
            data_source=data_source,
            data_dir=data_dir,
            api_config=api_config,
            trade_ids=trade_ids,
            date=date,
            pv_tolerance=pv_tolerance,
            delta_tolerance=delta_tolerance,
            train_ml=train_ml,
            generate_reports=generate_reports
        )
        
        return {
            "status": "success",
            "workflow": workflow_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow/cleanup/{workflow_id}")
async def cleanup_workflow(workflow_id: str):
    """Cleanup resources for a specific workflow"""
    try:
        cleanup_result = await orchestrator_service.cleanup_workflow(workflow_id)
        
        return {
            "status": "success",
            "cleanup": cleanup_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/config")
async def get_workflow_config():
    """Get default workflow configuration"""
    return {
        "default_config": {
            "data_source": "files",
            "pv_tolerance": 1000,
            "delta_tolerance": 0.05,
            "train_ml": True,
            "generate_reports": True
        },
        "supported_data_sources": ["files", "api", "hybrid"],
        "service_urls": orchestrator_service.service_urls
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005) 