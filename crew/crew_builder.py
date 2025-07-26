from crew.agents.unified_data_loader import UnifiedDataLoaderAgent
from crew.agents.recon_agent import ReconAgent
from crew.agents.analyzer_agent import AnalyzerAgent
from crew.agents.narrator_agent import NarratorAgent
from crew.agents.ml_tool import MLDiagnoserAgent

class ReconciliationCrew:
    def __init__(self, data_dir="data/", api_config=None):
        # Use unified data loader for all scenarios
        self.data_loader = UnifiedDataLoaderAgent(
            data_dir=data_dir,
            api_config=api_config
        )
        
        self.recon_agent = ReconAgent()
        self.analyzer_agent = AnalyzerAgent()
        self.narrator_agent = NarratorAgent()
        self.ml_agent = MLDiagnoserAgent()

    def run(self, source="auto", trade_ids=None, date=None):
        """
        Run the reconciliation pipeline
        
        Args:
            source: "files", "api", "auto", or "hybrid"
            trade_ids: List of trade IDs (for API)
            date: Specific date (for API)
        """
        print("🔄 Step 1: Loading data...")
        
        # Load data using unified loader
        df = self.data_loader.load_data(source, trade_ids, date)
        
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
            self.ml_agent.train(df, label_col='PV_Diagnosis')
        df["ML_Diagnosis"] = self.ml_agent.predict(df, label_col='PV_Diagnosis')

        print("📝 Step 5: Generating report...")
        self.narrator_agent.summarize_report(df)
        self.narrator_agent.save_report(df)

        return df
    
    def get_data_source_status(self):
        """Get status of available data sources"""
        return self.data_loader.get_available_sources()
    
    def get_api_status(self):
        """Get detailed API endpoint status"""
        return self.data_loader.get_api_status()
    
    def validate_data_quality(self, df):
        """Validate data quality"""
        return self.data_loader.validate_data_quality(df)
    
    def get_data_summary(self, df):
        """Get data summary statistics"""
        return self.data_loader.get_data_summary(df)
