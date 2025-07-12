import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import tempfile
from pathlib import Path
import time
import json

# Import our reconciliation system
from crew.crew_builder import ReconciliationCrew

# Page configuration
st.set_page_config(
    page_title="AI Reconciliation Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
    .api-status {
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
    .api-status.success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .api-status.error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def create_temp_data_directory():
    """Create a temporary directory for uploaded files"""
    temp_dir = tempfile.mkdtemp()
    return temp_dir

def save_uploaded_files(uploaded_files, temp_dir):
    """Save uploaded files to temporary directory"""
    saved_files = {}
    
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files[uploaded_file.name] = file_path
    
    return saved_files

def run_reconciliation(data_dir=None, api_config=None, source="auto", trade_ids=None, date=None):
    """Run the reconciliation pipeline"""
    try:
        crew = ReconciliationCrew(data_dir=data_dir, api_config=api_config)
        df = crew.run(source=source, trade_ids=trade_ids, date=date)
        return df, None, crew
    except Exception as e:
        return None, str(e), None

def create_mismatch_chart(df):
    """Create a chart showing mismatch distribution"""
    if df is None or df.empty:
        return go.Figure()
    
    # Count mismatches by type
    mismatch_data = {
        'PV Mismatches': df['PV_Mismatch'].sum(),
        'Delta Mismatches': df['Delta_Mismatch'].sum(),
        'Any Mismatch': df['Any_Mismatch'].sum(),
        'Total Trades': len(df)
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(mismatch_data.keys()),
            y=list(mismatch_data.values()),
            marker_color=['#ff7f0e', '#2ca02c', '#d62728', '#1f77b4']
        )
    ])
    
    fig.update_layout(
        title="Mismatch Distribution",
        xaxis_title="Mismatch Type",
        yaxis_title="Count",
        height=400
    )
    
    return fig

def create_diagnosis_chart(df):
    """Create a chart showing diagnosis distribution"""
    if df is None or df.empty:
        return go.Figure()
    
    # Count diagnoses
    rule_diagnosis_counts = df['Diagnosis'].value_counts()
    ml_diagnosis_counts = df['ML_Diagnosis'].value_counts()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Rule-based Diagnoses', 'ML Diagnoses'),
        specs=[[{"type": "pie"}, {"type": "pie"}]]
    )
    
    fig.add_trace(
        go.Pie(labels=rule_diagnosis_counts.index, values=rule_diagnosis_counts.values, name="Rule-based"),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Pie(labels=ml_diagnosis_counts.index, values=ml_diagnosis_counts.values, name="ML"),
        row=1, col=2
    )
    
    fig.update_layout(height=400, title_text="Diagnosis Distribution")
    
    return fig

def create_pv_delta_scatter(df):
    """Create a scatter plot of PV vs Delta changes"""
    if df is None or df.empty:
        return go.Figure()
    
    # Filter for trades with both old and new values
    valid_df = df.dropna(subset=['PV_old', 'PV_new', 'Delta_old', 'Delta_new'])
    
    if valid_df.empty:
        return go.Figure()
    
    fig = px.scatter(
        valid_df,
        x='PV_Diff',
        y='Delta_Diff',
        color='Any_Mismatch',
        hover_data=['TradeID', 'ProductType', 'Diagnosis'],
        title="PV vs Delta Changes",
        labels={'PV_Diff': 'PV Difference', 'Delta_Diff': 'Delta Difference'}
    )
    
    fig.update_layout(height=400)
    
    return fig

def create_trend_chart(df):
    """Create a trend chart showing PV and Delta changes"""
    if df is None or df.empty:
        return go.Figure()
    
    # Sample data for trend (in real scenario, you'd have time series data)
    fig = go.Figure()
    
    # Add PV changes
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['PV_Diff'],
        mode='lines+markers',
        name='PV Changes',
        line=dict(color='blue')
    ))
    
    # Add Delta changes
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Delta_Diff'],
        mode='lines+markers',
        name='Delta Changes',
        line=dict(color='red')
    ))
    
    fig.update_layout(
        title="PV and Delta Changes Over Trades",
        xaxis_title="Trade Index",
        yaxis_title="Change Value",
        height=400
    )
    
    return fig

def display_metrics(df):
    """Display key metrics"""
    if df is None or df.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Trades",
            value=len(df),
            delta=None
        )
    
    with col2:
        pv_mismatches = df['PV_Mismatch'].sum()
        st.metric(
            label="PV Mismatches",
            value=pv_mismatches,
            delta=f"{pv_mismatches/len(df)*100:.1f}%"
        )
    
    with col3:
        delta_mismatches = df['Delta_Mismatch'].sum()
        st.metric(
            label="Delta Mismatches",
            value=delta_mismatches,
            delta=f"{delta_mismatches/len(df)*100:.1f}%"
        )
    
    with col4:
        any_mismatches = df['Any_Mismatch'].sum()
        st.metric(
            label="Flagged Trades",
            value=any_mismatches,
            delta=f"{any_mismatches/len(df)*100:.1f}%"
        )

def display_comparison_table(df):
    """Display comparison between rule-based and ML diagnoses"""
    if df is None or df.empty:
        return
    
    st.subheader("Rule-based vs ML Diagnosis Comparison")
    
    # Create comparison table
    comparison_df = df[['TradeID', 'Diagnosis', 'ML_Diagnosis']].copy()
    comparison_df['Agreement'] = comparison_df['Diagnosis'] == comparison_df['ML_Diagnosis']
    
    # Calculate agreement statistics
    agreement_rate = comparison_df['Agreement'].mean() * 100
    disagreements = comparison_df[~comparison_df['Agreement']]
    
    st.write(f"**Agreement Rate: {agreement_rate:.1f}%**")
    st.write(f"**Disagreements: {len(disagreements)} trades**")
    
    # Show disagreements
    if not disagreements.empty:
        st.write("**Trades with Different Diagnoses:**")
        st.dataframe(disagreements)

def display_api_status(crew):
    """Display API connection status"""
    if crew is None:
        return
    
    st.subheader("🔌 API Connection Status")
    
    # Get data source status
    sources = crew.get_data_source_status()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Data Sources:**")
        for source, available in sources.items():
            status_class = "success" if available else "error"
            status_text = "✅ Available" if available else "❌ Not Available"
            st.markdown(f'<div class="api-status {status_class}">{source.title()}: {status_text}</div>', unsafe_allow_html=True)
    
    with col2:
        st.write("**API Endpoints:**")
        api_status = crew.get_api_status()
        if api_status:
            for endpoint, status in api_status.items():
                status_class = "success" if status else "error"
                status_text = "✅ Online" if status else "❌ Offline"
                st.markdown(f'<div class="api-status {status_class}">{endpoint}: {status_text}</div>', unsafe_allow_html=True)
        else:
            st.info("No API endpoints configured")

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Reconciliation Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Configuration")
    
    # Data Source Selection
    st.sidebar.header("📊 Data Source")
    data_source = st.sidebar.selectbox(
        "Select Data Source",
        ["Files", "API", "Auto-detect"],
        help="Choose how to load your reconciliation data"
    )
    
    # Initialize variables
    uploaded_files = {}
    
    # File upload section (only show if files selected or auto-detect)
    if data_source in ["Files", "Auto-detect"]:
        st.sidebar.header("📁 File Upload")
        st.sidebar.write("Upload your reconciliation data files:")
        
        uploaded_files = {
            'old_pricing.xlsx': st.sidebar.file_uploader("Old Pricing Data", type=['xlsx']),
            'new_pricing.xlsx': st.sidebar.file_uploader("New Pricing Data", type=['xlsx']),
            'trade_metadata.xlsx': st.sidebar.file_uploader("Trade Metadata", type=['xlsx']),
            'funding_model_reference.xlsx': st.sidebar.file_uploader("Funding Model Reference", type=['xlsx'])
        }
        
        # Check if all required files are uploaded
        all_files_uploaded = all(file is not None for file in uploaded_files.values())
        
        if not all_files_uploaded and data_source == "Files":
            st.sidebar.warning("Please upload all required files to proceed.")
            st.info("""
            ### Required Files:
            - **old_pricing.xlsx**: Previous pricing data
            - **new_pricing.xlsx**: Current pricing data  
            - **trade_metadata.xlsx**: Trade characteristics
            - **funding_model_reference.xlsx**: Funding information
            """)
            return
    
    # API Configuration (only show if API selected or auto-detect)
    api_config = None
    if data_source in ["API", "Auto-detect"]:
        st.sidebar.header("🔌 API Configuration")
        
        # Show helpful info for local API
        if data_source == "API":
            st.sidebar.info("""
            **💡 Quick Start:**
            - Use `http://localhost:8000` for local REST API
            - Leave API Key empty for local server
            - Make sure to start the API server first: `python api_server.py`
            """)
        
        # API Settings
        api_base_url = st.sidebar.text_input(
            "API Base URL",
            value="http://localhost:8000",
            help="Base URL for your reconciliation API (use http://localhost:8000 for local server)"
        )
        
        api_key = st.sidebar.text_input(
            "API Key (Optional for local server)",
            type="password",
            help="API key for authentication (leave empty for local server)"
        )
        
        api_timeout = st.sidebar.slider(
            "API Timeout (seconds)",
            min_value=5,
            max_value=60,
            value=30,
            help="Request timeout for API calls"
        )
        
        # Custom endpoints
        st.sidebar.subheader("Custom Endpoints (Optional)")
        use_custom_endpoints = st.sidebar.checkbox("Use custom endpoints")
        
        if use_custom_endpoints:
            old_pricing_endpoint = st.sidebar.text_input("Old Pricing Endpoint", value="/api/v1/pricing/old")
            new_pricing_endpoint = st.sidebar.text_input("New Pricing Endpoint", value="/api/v1/pricing/new")
            metadata_endpoint = st.sidebar.text_input("Metadata Endpoint", value="/api/v1/trades/metadata")
            funding_endpoint = st.sidebar.text_input("Funding Endpoint", value="/api/v1/funding/reference")
            
            endpoints = {
                'old_pricing': old_pricing_endpoint,
                'new_pricing': new_pricing_endpoint,
                'trade_metadata': metadata_endpoint,
                'funding_reference': funding_endpoint
            }
        else:
            endpoints = {}
        
        # API Parameters
        st.sidebar.subheader("API Parameters")
        trade_ids_input = st.sidebar.text_area(
            "Trade IDs (one per line)",
            help="Leave empty for all trades"
        )
        
        date_input = st.sidebar.date_input(
            "Date",
            help="Specific date for pricing data"
        )
        
        # Parse trade IDs
        trade_ids = None
        if trade_ids_input.strip():
            trade_ids = [tid.strip() for tid in trade_ids_input.split('\n') if tid.strip()]
        
        # Create API config
        api_config = None
        if api_base_url:
            api_config = {
                'base_url': api_base_url,
                'api_key': api_key if api_key else None,
                'timeout': api_timeout,
                'endpoints': endpoints
            }
        elif data_source == "API":
            st.sidebar.error("⚠️ API Base URL is required for API data source.")
            return
    else:
        # Initialize variables for non-API data sources
        trade_ids = None
        date_input = None
        api_config = None
    
    # Configuration options
    st.sidebar.header("⚙️ Settings")
    
    pv_tolerance = st.sidebar.slider(
        "PV Tolerance",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100,
        help="Threshold for PV mismatch detection"
    )
    
    delta_tolerance = st.sidebar.slider(
        "Delta Tolerance",
        min_value=0.01,
        max_value=0.50,
        value=0.05,
        step=0.01,
        help="Threshold for Delta mismatch detection"
    )
    
    # Run analysis button
    st.sidebar.header("🚀 Analysis")
    run_analysis = st.sidebar.button("Run Reconciliation Analysis", type="primary")
    
    # Initialize session state for filters (outside the analysis block to persist)
    if 'show_mismatches_only' not in st.session_state:
        st.session_state.show_mismatches_only = False
    if 'selected_product_type' not in st.session_state:
        st.session_state.selected_product_type = "All"
    if 'selected_diagnosis' not in st.session_state:
        st.session_state.selected_diagnosis = "All"
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analysis_crew' not in st.session_state:
        st.session_state.analysis_crew = None

    # Main content area
    if run_analysis:
        with st.spinner("🔄 Processing data and running reconciliation..."):
            # Determine data source
            source_map = {
                "Files": "files",
                "API": "api", 
                "Auto-detect": "auto"
            }
            source = source_map.get(data_source, "auto")
            
            # Prepare parameters
            temp_dir = None
            if data_source == "Files":
                temp_dir = create_temp_data_directory()
                saved_files = save_uploaded_files(uploaded_files.values(), temp_dir)
            
            # Run reconciliation
            # For API source, don't pass data_dir to avoid file loading
            data_dir_to_use = temp_dir if data_source == "Files" else None
            
            df, error, crew = run_reconciliation(
                data_dir=data_dir_to_use,
                api_config=api_config,
                source=source,
                trade_ids=trade_ids,
                date=date_input.strftime("%Y-%m-%d") if date_input else None
            )
            
            if error:
                st.error(f"❌ Error during reconciliation: {error}")
                return
            
            if df is None or df.empty:
                st.warning("⚠️ No data returned from reconciliation process.")
                return
            
            # Store results in session state
            st.session_state.analysis_results = df
            st.session_state.analysis_crew = crew
            
            # Success message
            st.success("✅ Reconciliation completed successfully!")
            
            # Display API status if available
            if crew and source in ["api", "auto"]:
                display_api_status(crew)
            
            # Display metrics
            st.header("📊 Key Metrics")
            display_metrics(df)
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📈 Overview", 
                "🔍 Analysis", 
                "📋 Details", 
                "📊 Comparison",
                "🔌 API Status",
                "💾 Export"
            ])
            
            with tab1:
                st.header("📈 Overview")
                
                # Mismatch distribution chart
                st.plotly_chart(create_mismatch_chart(df), use_container_width=True)
                
                # Diagnosis distribution
                st.plotly_chart(create_diagnosis_chart(df), use_container_width=True)
            
            with tab2:
                st.header("🔍 Detailed Analysis")
                
                # PV vs Delta scatter plot
                st.plotly_chart(create_pv_delta_scatter(df), use_container_width=True)
                
                # Trend chart
                st.plotly_chart(create_trend_chart(df), use_container_width=True)
                
                # Statistical summary
                st.subheader("Statistical Summary")
                if 'PV_Diff' in df.columns and 'Delta_Diff' in df.columns:
                    stats_df = df[['PV_Diff', 'Delta_Diff']].describe()
                    st.dataframe(stats_df)
            
            with tab3:
                st.header("📋 Detailed Results")
                
                # Filter options with session state
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    show_mismatches_only = st.checkbox(
                        "Show mismatches only",
                        value=st.session_state.show_mismatches_only,
                        key="mismatches_filter"
                    )
                    # Update session state
                    st.session_state.show_mismatches_only = show_mismatches_only
                
                with col2:
                    product_types = ["All"] + list(df['ProductType'].unique())
                    selected_product_type = st.selectbox(
                        "Filter by Product Type",
                        options=product_types,
                        index=product_types.index(st.session_state.selected_product_type) if st.session_state.selected_product_type in product_types else 0,
                        key="product_type_filter"
                    )
                    # Update session state
                    st.session_state.selected_product_type = selected_product_type
                
                with col3:
                    diagnoses = ["All"] + list(df['Diagnosis'].unique())
                    selected_diagnosis = st.selectbox(
                        "Filter by Diagnosis",
                        options=diagnoses,
                        index=diagnoses.index(st.session_state.selected_diagnosis) if st.session_state.selected_diagnosis in diagnoses else 0,
                        key="diagnosis_filter"
                    )
                    # Update session state
                    st.session_state.selected_diagnosis = selected_diagnosis
                
                # Apply filters
                filtered_df = df.copy()
                if show_mismatches_only:
                    filtered_df = filtered_df[filtered_df['Any_Mismatch']]
                if selected_product_type != "All":
                    filtered_df = filtered_df[filtered_df['ProductType'] == selected_product_type]
                if selected_diagnosis != "All":
                    filtered_df = filtered_df[filtered_df['Diagnosis'] == selected_diagnosis]
                
                # Display filter summary and reset button
                if show_mismatches_only or selected_product_type != "All" or selected_diagnosis != "All":
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.info(f"📊 Showing {len(filtered_df)} of {len(df)} trades")
                    with col2:
                        if st.button("🔄 Reset Filters", key="reset_filters"):
                            st.session_state.show_mismatches_only = False
                            st.session_state.selected_product_type = "All"
                            st.session_state.selected_diagnosis = "All"
                            st.rerun()
                
                # Display filtered results
                st.dataframe(filtered_df, use_container_width=True)
            
            with tab4:
                st.header("📊 Rule-based vs ML Comparison")
                display_comparison_table(df)
            
            with tab5:
                st.header("🔌 API Status & Data Quality")
                
                if crew:
                    # API Status
                    display_api_status(crew)
                    
                    # Data Quality
                    st.subheader("📊 Data Quality Report")
                    quality = crew.validate_data_quality(df)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        for check, status in quality.items():
                            icon = "✅" if status else "❌"
                            st.write(f"{icon} {check.replace('_', ' ').title()}")
                    
                    with col2:
                        summary = crew.get_data_summary(df)
                        st.write(f"**Total Trades:** {summary.get('total_trades', 0)}")
                        st.write(f"**Columns:** {len(summary.get('columns', []))}")
                        
                        if 'pv_stats' in summary:
                            st.write("**PV Statistics:**")
                            st.write(f"Old Mean: {summary['pv_stats']['old_mean']:.2f}")
                            st.write(f"New Mean: {summary['pv_stats']['new_mean']:.2f}")
            
            with tab6:
                st.header("💾 Export Results")
                
                # Export options
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📥 Download Excel Report"):
                        # Create Excel file
                        output = df.to_excel(index=False)
                        st.download_button(
                            label="📥 Download Excel",
                            data=output,
                            file_name="reconciliation_report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                with col2:
                    if st.button("📊 Download Charts"):
                        # Export charts as images
                        st.info("Chart export functionality coming soon!")
                
                # Summary statistics
                st.subheader("Summary Statistics")
                summary_stats = {
                    "Total Trades": len(df),
                    "PV Mismatches": df['PV_Mismatch'].sum(),
                    "Delta Mismatches": df['Delta_Mismatch'].sum(),
                    "Flagged Trades": df['Any_Mismatch'].sum(),
                    "Agreement Rate": f"{(df['Diagnosis'] == df['ML_Diagnosis']).mean()*100:.1f}%"
                }
                
                for key, value in summary_stats.items():
                    st.write(f"**{key}:** {value}")
    
    # Display results from session state if available (even when not running new analysis)
    elif st.session_state.analysis_results is not None:
        df = st.session_state.analysis_results
        crew = st.session_state.analysis_crew
        
        st.success("✅ Using previous analysis results. Run new analysis to refresh data.")
        
        # Display metrics
        st.header("📊 Key Metrics")
        display_metrics(df)
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Overview", 
            "🔍 Analysis", 
            "📋 Details", 
            "📊 Comparison",
            "🔌 API Status",
            "💾 Export"
        ])
        
        with tab1:
            st.header("📈 Overview")
            
            # Mismatch distribution chart
            st.plotly_chart(create_mismatch_chart(df), use_container_width=True)
            
            # Diagnosis distribution
            st.plotly_chart(create_diagnosis_chart(df), use_container_width=True)
        
        with tab2:
            st.header("🔍 Detailed Analysis")
            
            # PV vs Delta scatter plot
            st.plotly_chart(create_pv_delta_scatter(df), use_container_width=True)
            
            # Trend chart
            st.plotly_chart(create_trend_chart(df), use_container_width=True)
            
            # Statistical summary
            st.subheader("Statistical Summary")
            if 'PV_Diff' in df.columns and 'Delta_Diff' in df.columns:
                stats_df = df[['PV_Diff', 'Delta_Diff']].describe()
                st.dataframe(stats_df)
        
        with tab3:
            st.header("📋 Detailed Results")
            
            # Filter options with session state
            col1, col2, col3 = st.columns(3)
            
            with col1:
                show_mismatches_only = st.checkbox(
                    "Show mismatches only",
                    value=st.session_state.show_mismatches_only,
                    key="mismatches_filter_persistent"
                )
                # Update session state
                st.session_state.show_mismatches_only = show_mismatches_only
            
            with col2:
                product_types = ["All"] + list(df['ProductType'].unique())
                selected_product_type = st.selectbox(
                    "Filter by Product Type",
                    options=product_types,
                    index=product_types.index(st.session_state.selected_product_type) if st.session_state.selected_product_type in product_types else 0,
                    key="product_type_filter_persistent"
                )
                # Update session state
                st.session_state.selected_product_type = selected_product_type
            
            with col3:
                diagnoses = ["All"] + list(df['Diagnosis'].unique())
                selected_diagnosis = st.selectbox(
                    "Filter by Diagnosis",
                    options=diagnoses,
                    index=diagnoses.index(st.session_state.selected_diagnosis) if st.session_state.selected_diagnosis in diagnoses else 0,
                    key="diagnosis_filter_persistent"
                )
                # Update session state
                st.session_state.selected_diagnosis = selected_diagnosis
            
            # Apply filters
            filtered_df = df.copy()
            if show_mismatches_only:
                filtered_df = filtered_df[filtered_df['Any_Mismatch']]
            if selected_product_type != "All":
                filtered_df = filtered_df[filtered_df['ProductType'] == selected_product_type]
            if selected_diagnosis != "All":
                filtered_df = filtered_df[filtered_df['Diagnosis'] == selected_diagnosis]
            
            # Display filter summary and reset button
            if show_mismatches_only or selected_product_type != "All" or selected_diagnosis != "All":
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"📊 Showing {len(filtered_df)} of {len(df)} trades")
                with col2:
                    if st.button("🔄 Reset Filters", key="reset_filters_persistent"):
                        st.session_state.show_mismatches_only = False
                        st.session_state.selected_product_type = "All"
                        st.session_state.selected_diagnosis = "All"
                        st.rerun()
            
            # Display filtered results
            st.dataframe(filtered_df, use_container_width=True)
        
        with tab4:
            st.header("📊 Rule-based vs ML Comparison")
            display_comparison_table(df)
        
        with tab5:
            st.header("🔌 API Status & Data Quality")
            
            if crew:
                # API Status
                display_api_status(crew)
                
                # Data Quality
                st.subheader("📊 Data Quality Report")
                quality = crew.validate_data_quality(df)
                
                col1, col2 = st.columns(2)
                with col1:
                    for check, status in quality.items():
                        icon = "✅" if status else "❌"
                        st.write(f"{icon} {check.replace('_', ' ').title()}")
                
                with col2:
                    summary = crew.get_data_summary(df)
                    st.write(f"**Total Trades:** {summary.get('total_trades', 0)}")
                    st.write(f"**Columns:** {len(summary.get('columns', []))}")
                    
                    if 'pv_stats' in summary:
                        st.write("**PV Statistics:**")
                        st.write(f"Old Mean: {summary['pv_stats']['old_mean']:.2f}")
                        st.write(f"New Mean: {summary['pv_stats']['new_mean']:.2f}")
        
        with tab6:
            st.header("💾 Export Results")
            
            # Export options
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Download Excel Report"):
                    # Create Excel file
                    output = df.to_excel(index=False)
                    st.download_button(
                        label="📥 Download Excel",
                        data=output,
                        file_name="reconciliation_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                if st.button("📊 Download Charts"):
                    # Export charts as images
                    st.info("Chart export functionality coming soon!")
            
            # Summary statistics
            st.subheader("Summary Statistics")
            summary_stats = {
                "Total Trades": len(df),
                "PV Mismatches": df['PV_Mismatch'].sum(),
                "Delta Mismatches": df['Delta_Mismatch'].sum(),
                "Flagged Trades": df['Any_Mismatch'].sum(),
                "Agreement Rate": f"{(df['Diagnosis'] == df['ML_Diagnosis']).mean()*100:.1f}%"
            }
            
            for key, value in summary_stats.items():
                st.write(f"**{key}:** {value}")
    
    else:
        # Welcome message and instructions
        st.info("""
        ### Welcome to the AI Reconciliation Dashboard! 🎉
        
        This dashboard provides a user-friendly interface for running AI-powered reconciliation analysis.
        
        **Data Sources:**
        - **Files**: Upload Excel files directly
        - **API**: Connect to external APIs for real-time data
        - **Auto-detect**: Automatically choose the best available source
        
        **To get started:**
        1. Select your data source (Files/API/Auto-detect)
        2. Configure your data source settings
        3. Adjust tolerance settings
        4. Click "Run Reconciliation Analysis"
        5. Explore the results in the interactive dashboard
        
        **Features:**
        - 📊 Real-time analysis and visualization
        - 🤖 ML-powered diagnosis comparison
        - 📈 Interactive charts and metrics
        - 📋 Detailed results and filtering
        - 🔌 API integration and monitoring
        - 💾 Export capabilities
        """)
        
        # Sample data preview
        st.subheader("📋 Expected Data Format")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**old_pricing.xlsx**")
            sample_old = pd.DataFrame({
                'TradeID': ['T001', 'T002', 'T003'],
                'PV_old': [104500, -98000, 50500],
                'Delta_old': [0.42, -0.98, 0.00]
            })
            st.dataframe(sample_old)
        
        with col2:
            st.write("**new_pricing.xlsx**")
            sample_new = pd.DataFrame({
                'TradeID': ['T001', 'T002', 'T003'],
                'PV_new': [105200, -97500, 50800],
                'Delta_new': [0.43, -0.97, 0.01]
            })
            st.dataframe(sample_new)

if __name__ == "__main__":
    main()
