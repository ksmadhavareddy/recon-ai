from crew.agents.data_loader import DataLoaderAgent
from crew.agents.recon_agent import ReconAgent
from crew.agents.analyzer_agent import AnalyzerAgent
from crew.agents.narrator_agent import NarratorAgent

class ReconciliationCrew:
    def __init__(self, data_dir="data/"):
        self.data_loader = DataLoaderAgent(data_dir)
        self.recon_agent = ReconAgent()
        self.analyzer_agent = AnalyzerAgent()
        self.narrator_agent = NarratorAgent()

    def run(self):
        print("🔄 Step 1: Loading data...")
        df = self.data_loader.load_all_data()

        print("📏 Step 2: Computing PV/Delta mismatches...")
        df = self.recon_agent.add_diff_flags(df)

        print("🧠 Step 3: Diagnosing root causes...")
        df = self.analyzer_agent.apply(df)

        print("📝 Step 4: Generating report...")
        self.narrator_agent.summarize_report(df)
        self.narrator_agent.save_report(df)

        return df
