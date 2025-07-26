#!/usr/bin/env python3
"""
Microservices Dashboard - Streamlit dashboard for the microservices architecture
"""

import streamlit as st
import pandas as pd
import requests
import json
from typing import Dict, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="AI Reconciliation - Microservices Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Service URLs
SERVICE_URLS = {
    "data": "http://localhost:8001",
    "reconciliation": "http://localhost:8002",
    "ml": "http://localhost:8003",
    "report": "http://localhost:8004",
    "orchestrator": "http://localhost:8005"
}

def check_service_health(service_name: str) -> bool:
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{SERVICE_URLS[service_name]}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_service_status() -> Dict[str, Dict]:
    """Get status of all services"""
    status = {}
    for service_name, url in SERVICE_URLS.items():
        status[service_name] = {
            "healthy": check_service_health(service_name),
            "url": url
        }
    return status

def run_orchestrator_workflow(data_source: str, data_dir: str = None, 
                             api_config: Dict = None, pv_tolerance: float = 1000,
                             delta_tolerance: float = 0.05, train_ml: bool = True,
                             generate_reports: bool = True) -> Dict[str, Any]:
    """Run the complete workflow using orchestrator service"""
    try:
        payload = {
            "data_source": data_source,
            "pv_tolerance": pv_tolerance,
            "delta_tolerance": delta_tolerance,
            "train_ml": train_ml,
            "generate_reports": generate_reports
        }
        
        if data_dir:
            payload["data_dir"] = data_dir
        if api_config:
            payload["api_config"] = api_config
        
        response = requests.post(f"{SERVICE_URLS['orchestrator']}/workflow/run", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Workflow failed: {response.text}"}
    except Exception as e:
        return {"error": f"Error running workflow: {str(e)}"}

def main():
    st.title("🤖 AI Reconciliation - Microservices Dashboard")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("🔧 Service Management")
    
    # Service Status
    st.sidebar.subheader("📊 Service Status")
    service_status = get_service_status()
    
    for service_name, status in service_status.items():
        icon = "🟢" if status["healthy"] else "🔴"
        st.sidebar.write(f"{icon} {service_name.title()}")
    
    # Service Health Check
    if st.sidebar.button("🔄 Refresh Status"):
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard", 
        "⚙️ Workflow", 
        "📊 Analysis", 
        "📈 Reports",
        "🔍 Services"
    ])
    
    with tab1:
        st.header("🏠 Dashboard Overview")
        
        # Service Health Overview
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Data Service", "🟢" if service_status["data"]["healthy"] else "🔴")
        with col2:
            st.metric("Reconciliation", "🟢" if service_status["reconciliation"]["healthy"] else "🔴")
        with col3:
            st.metric("ML Service", "🟢" if service_status["ml"]["healthy"] else "🔴")
        with col4:
            st.metric("Report Service", "🟢" if service_status["report"]["healthy"] else "🔴")
        with col5:
            st.metric("Orchestrator", "🟢" if service_status["orchestrator"]["healthy"] else "🔴")
        
        # Quick Actions
        st.subheader("🚀 Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧪 Test Orchestrator"):
                try:
                    response = requests.get(f"{SERVICE_URLS['orchestrator']}/services/health")
                    if response.status_code == 200:
                        st.success("✅ Orchestrator test passed!")
                        st.json(response.json())
                    else:
                        st.error("❌ Orchestrator test failed")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        with col2:
            if st.button("📋 Get Workflow Config"):
                try:
                    response = requests.get(f"{SERVICE_URLS['orchestrator']}/workflow/config")
                    if response.status_code == 200:
                        st.success("✅ Config retrieved!")
                        st.json(response.json())
                    else:
                        st.error("❌ Failed to get config")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with tab2:
        st.header("⚙️ Workflow Configuration")
        
        # Data Source Configuration
        st.subheader("📊 Data Source")
        
        data_source = st.selectbox(
            "Select Data Source",
            ["files", "api", "hybrid"],
            help="Choose how to load your reconciliation data"
        )
        
        data_dir = None
        api_config = None
        
        if data_source == "files":
            data_dir = st.text_input("Data Directory", value="data", help="Directory containing Excel files")
        elif data_source == "api":
            st.subheader("🔌 API Configuration")
            api_base_url = st.text_input("API Base URL", value="http://localhost:8000")
            api_key = st.text_input("API Key (optional)", type="password")
            api_timeout = st.number_input("Timeout (seconds)", value=30, min_value=5, max_value=300)
            
            api_config = {
                "base_url": api_base_url,
                "api_key": api_key if api_key else None,
                "timeout": api_timeout
            }
        else:  # hybrid
            data_dir = st.text_input("Data Directory (fallback)", value="data")
            st.subheader("🔌 API Configuration")
            api_base_url = st.text_input("API Base URL", value="http://localhost:8000")
            api_key = st.text_input("API Key (optional)", type="password")
            api_timeout = st.number_input("Timeout (seconds)", value=30, min_value=5, max_value=300)
            
            api_config = {
                "base_url": api_base_url,
                "api_key": api_key if api_key else None,
                "timeout": api_timeout
            }
        
        # Tolerance Configuration
        st.subheader("⚖️ Tolerance Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pv_tolerance = st.number_input("PV Tolerance", value=1000.0, min_value=0.0, step=100.0)
        
        with col2:
            delta_tolerance = st.number_input("Delta Tolerance", value=0.05, min_value=0.0, max_value=1.0, step=0.01)
        
        # Workflow Options
        st.subheader("🔧 Workflow Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            train_ml = st.checkbox("Train ML Model", value=True)
            generate_reports = st.checkbox("Generate Reports", value=True)
        
        with col2:
            st.write("**Workflow Steps:**")
            st.write("1. 📊 Load Data")
            st.write("2. 🔍 Detect Mismatches")
            st.write("3. 🧠 Apply Rule-based Diagnosis")
            if train_ml:
                st.write("4. 🤖 Train ML Model")
            if generate_reports:
                st.write("5. 📝 Generate Reports")
        
        # Run Workflow
        st.subheader("🚀 Execute Workflow")
        
        if st.button("▶️ Run Complete Workflow", type="primary"):
            with st.spinner("🔄 Running workflow..."):
                result = run_orchestrator_workflow(
                    data_source=data_source,
                    data_dir=data_dir,
                    api_config=api_config,
                    pv_tolerance=pv_tolerance,
                    delta_tolerance=delta_tolerance,
                    train_ml=train_ml,
                    generate_reports=generate_reports
                )
                
                if "error" in result:
                    st.error(f"❌ Workflow failed: {result['error']}")
                else:
                    st.success("✅ Workflow completed successfully!")
                    
                    # Display workflow results
                    workflow = result.get("workflow", {})
                    
                    st.subheader("📋 Workflow Results")
                    st.write(f"**Workflow ID:** {workflow.get('workflow_id', 'N/A')}")
                    st.write(f"**Status:** {workflow.get('status', 'N/A')}")
                    st.write(f"**Start Time:** {workflow.get('start_time', 'N/A')}")
                    st.write(f"**End Time:** {workflow.get('end_time', 'N/A')}")
                    
                    # Display steps
                    st.subheader("📝 Workflow Steps")
                    for step in workflow.get("steps", []):
                        step_name = step.get("step", "Unknown")
                        step_status = step.get("status", "Unknown")
                        step_icon = "✅" if step_status == "completed" else "❌"
                        
                        with st.expander(f"{step_icon} {step_name}"):
                            st.json(step.get("result", {}))
    
    with tab3:
        st.header("📊 Analysis Results")
        
        # Check if we have results in session state
        if "workflow_results" in st.session_state:
            st.subheader("📈 Analysis Summary")
            
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Trades", st.session_state.workflow_results.get("total_trades", 0))
            
            with col2:
                st.metric("PV Mismatches", st.session_state.workflow_results.get("pv_mismatches", 0))
            
            with col3:
                st.metric("Delta Mismatches", st.session_state.workflow_results.get("delta_mismatches", 0))
            
            with col4:
                mismatch_rate = st.session_state.workflow_results.get("mismatch_rate", 0)
                st.metric("Mismatch Rate", f"{mismatch_rate:.1f}%")
            
            # Diagnosis Distribution
            if "diagnosis_distribution" in st.session_state.workflow_results:
                st.subheader("🧠 Diagnosis Distribution")
                
                diagnosis_data = st.session_state.workflow_results["diagnosis_distribution"]
                if diagnosis_data:
                    fig = px.pie(
                        values=list(diagnosis_data.values()),
                        names=list(diagnosis_data.keys()),
                        title="Diagnosis Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Product Type Distribution
            if "product_distribution" in st.session_state.workflow_results:
                st.subheader("📦 Product Type Distribution")
                
                product_data = st.session_state.workflow_results["product_distribution"]
                if product_data:
                    fig = px.bar(
                        x=list(product_data.keys()),
                        y=list(product_data.values()),
                        title="Product Type Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Run a workflow to see analysis results here.")
    
    with tab4:
        st.header("📈 Reports")
        
        # Get available reports
        try:
            response = requests.get(f"{SERVICE_URLS['report']}/list")
            if response.status_code == 200:
                reports_data = response.json()
                reports = reports_data.get("reports", [])
                
                if reports:
                    st.subheader("📋 Available Reports")
                    
                    for report in reports:
                        with st.expander(f"📄 {report['filename']}"):
                            st.write(f"**Type:** {report['type']}")
                            st.write(f"**Size:** {report['size_bytes']} bytes")
                            st.write(f"**Created:** {report['created_at']}")
                            st.write(f"**Modified:** {report['modified_at']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"⬇️ Download {report['filename']}", key=f"download_{report['filename']}"):
                                    st.info("Download functionality would be implemented here")
                            
                            with col2:
                                if st.button(f"🗑️ Delete {report['filename']}", key=f"delete_{report['filename']}"):
                                    st.info("Delete functionality would be implemented here")
                else:
                    st.info("ℹ️ No reports available. Generate reports by running a workflow.")
            else:
                st.error("❌ Failed to retrieve reports")
        except Exception as e:
            st.error(f"❌ Error retrieving reports: {e}")
    
    with tab5:
        st.header("🔍 Service Details")
        
        # Service Information
        for service_name, status in service_status.items():
            with st.expander(f"{'🟢' if status['healthy'] else '🔴'} {service_name.title()}"):
                st.write(f"**URL:** {status['url']}")
                st.write(f"**Status:** {'Healthy' if status['healthy'] else 'Unhealthy'}")
                
                # Get service-specific information
                try:
                    if service_name == "ml":
                        response = requests.get(f"{status['url']}/model/info")
                        if response.status_code == 200:
                            model_info = response.json()
                            st.write("**Model Info:**")
                            st.json(model_info)
                    
                    elif service_name == "report":
                        response = requests.get(f"{status['url']}/formats/available")
                        if response.status_code == 200:
                            formats = response.json()
                            st.write("**Available Formats:**")
                            st.json(formats)
                    
                    elif service_name == "reconciliation":
                        response = requests.get(f"{status['url']}/config/tolerances")
                        if response.status_code == 200:
                            config = response.json()
                            st.write("**Current Configuration:**")
                            st.json(config)
                    
                    elif service_name == "data":
                        response = requests.get(f"{status['url']}/sources/available")
                        if response.status_code == 200:
                            sources = response.json()
                            st.write("**Available Sources:**")
                            st.json(sources)
                
                except Exception as e:
                    st.write(f"**Error getting service info:** {e}")

if __name__ == "__main__":
    main() 