class AnalyzerAgent:
    def __init__(self):
        pass

    def rule_based_diagnosis(self, row):
        if row.get("PV_old") is None:
            return "New trade – no prior valuation"
        if row.get("PV_new") is None:
            return "Trade dropped from new model"
        if row.get("FundingCurve") == "USD-LIBOR" and row.get("ModelVersion") != "v2024.3":
            return "Legacy LIBOR curve with outdated model – PV likely shifted"
        if row.get("CSA_Type") == "Cleared_CSA" and row.get("PV_Mismatch"):
            return "CSA changed post-clearing – funding basis moved"
        if row.get("ProductType") == "Option" and row.get("Delta_Mismatch"):
            return "Vol sensitivity likely – delta impact due to model curve shift"
        return "Within tolerance"

    def apply(self, df):
        df["Diagnosis"] = df.apply(self.rule_based_diagnosis, axis=1)
        return df
