class PVAnalysisAgent:
    def __init__(self):
        pass

    def analyze(self, row):
        if row.get("PV_old") is None:
            return "New trade – no prior valuation"
        if row.get("PV_new") is None:
            return "Trade dropped from new model"
        if row.get("FundingCurve") == "USD-LIBOR" and row.get("ModelVersion") != "v2024.3":
            return "Legacy LIBOR curve with outdated model – PV likely shifted"
        if row.get("CSA_Type") == "Cleared_CSA" and row.get("PV_Mismatch"):
            return "CSA changed post-clearing – funding basis moved"
        return "Within tolerance"

class DeltaAnalysisAgent:
    def __init__(self):
        pass

    def analyze(self, row):
        if row.get("ProductType") == "Option" and row.get("Delta_Mismatch"):
            return "Vol sensitivity likely – delta impact due to model curve shift"
        return "Within tolerance"

class AnalyzerAgent:
    def __init__(self):
        self.pv_agent = PVAnalysisAgent()
        self.delta_agent = DeltaAnalysisAgent()

    def apply(self, df):
        df["PV_Diagnosis"] = df.apply(self.pv_agent.analyze, axis=1)
        df["Delta_Diagnosis"] = df.apply(self.delta_agent.analyze, axis=1)
        return df
