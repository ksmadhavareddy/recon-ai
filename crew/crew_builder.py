from crew.agents.data_loader import DataLoaderAgent
from crew.agents.recon_agent import ReconAgent
from crew.agents.analyzer_agent import AnalyzerAgent
from crew.agents.narrator_agent import NarratorAgent
from crew.agents.ml_tool import MLDiagnoserAgent
from crew.agents.hybrid_data_loader import HybridDataLoaderAgent

class ReconciliationCrew:
    def __init__(self, data_dir="data/", api_config=None):
        # Use hybrid data loader if API config provided, otherwise use file loader
        if api_config:
            self.data_loader = HybridDataLoaderAgent(data_dir, api_config)
        else:
            # Only use file loader if data_dir is provided
            if data_dir:
                self.data_loader = DataLoaderAgent(data_dir)
            else:
                raise ValueError("Either data_dir or api_config must be provided")
        
        self.recon_agent = ReconAgent()
        self.analyzer_agent = AnalyzerAgent()
        self.narrator_agent = NarratorAgent()
        self.ml_agent = MLDiagnoserAgent()

    def run(self, source="auto", trade_ids=None, date=None):
        """
        Run the reconciliation pipeline
        
        Args:
            source: "files", "api", or "auto"
            trade_ids: List of trade IDs (for API)
            date: Specific date (for API)
        """
        print("🔄 Step 1: Loading data...")
        
        # Load data using appropriate method
        if hasattr(self.data_loader, 'load_data'):
            # Hybrid data loader
            df = self.data_loader.load_data(source, trade_ids, date)
        else:
            # Legacy file loader
            df = self.data_loader.load_all_data()
        
        if df is None or df.empty:
            print("❌ No data loaded. Please check your data source configuration.")
            return None

        print("📏 Step 2: Computing PV/Delta mismatches...")
        df = self.recon_agent.add_diff_flags(df)

        print("🧠 Step 3: Diagnosing root causes (rule-based)...")
        df = self.analyzer_agent.apply(df)

        # ML Training and Prediction
        print("🤖 Step 4: Training ML model and predicting diagnoses...")
        if self.ml_agent.model is None:
            self.ml_agent.train(df)
        df["ML_Diagnosis"] = self.ml_agent.predict(df)

        print("📝 Step 5: Generating report...")
        self.narrator_agent.summarize_report(df)
        self.narrator_agent.save_report(df)

        return df
    
    def get_data_source_status(self):
        """Get status of available data sources"""
        if hasattr(self.data_loader, 'get_available_sources'):
            return self.data_loader.get_available_sources()
        return {'files': True, 'api': False}
    
    def get_api_status(self):
        """Get detailed API endpoint status"""
        if hasattr(self.data_loader, 'get_api_status'):
            return self.data_loader.get_api_status()
        return {}
    
    def validate_data_quality(self, df):
        """Validate data quality"""
        if hasattr(self.data_loader, 'validate_data_quality'):
            return self.data_loader.validate_data_quality(df)
        return {'has_data': df is not None and not df.empty}
    
    def get_data_summary(self, df):
        """Get data summary statistics"""
        if hasattr(self.data_loader, 'get_data_summary'):
            return self.data_loader.get_data_summary(df)
        return {'total_trades': len(df) if df is not None else 0}
