import pandas as pd

class NarratorAgent:
    def __init__(self):
        pass

    def summarize_report(self, df):
        summary = {
            "Total Trades": len(df),
            "PV Mismatches": df["PV_Mismatch"].sum(),
            "Delta Mismatches": df["Delta_Mismatch"].sum(),
            "Flagged Trades": df["Any_Mismatch"].sum(),
        }

        print("\n📊 Reconciliation Summary:")
        for k, v in summary.items():
            print(f"{k}: {v}")
        return summary

    def save_report(self, df, output_path="final_recon_report.xlsx"):
        cols = [
            "TradeID", "PV_old", "PV_new", "PV_Diff",
            "Delta_old", "Delta_new", "Delta_Diff",
            "ProductType", "FundingCurve", "CSA_Type", "ModelVersion",
            "PV_Mismatch", "Delta_Mismatch", "PV_Diagnosis", "Delta_Diagnosis", "ML_Diagnosis"
        ]
        df.to_excel(output_path, index=False, columns=cols)
        print(f"\n✅ Report saved to: {output_path}")
