class ReconAgent:
    def __init__(self, pv_tolerance=1000, delta_tolerance=0.05):
        self.pv_tolerance = pv_tolerance
        self.delta_tolerance = delta_tolerance

    def add_diff_flags(self, df):
        df["PV_Diff"] = df["PV_new"] - df["PV_old"]
        df["Delta_Diff"] = df["Delta_new"] - df["Delta_old"]

        df["PV_Mismatch"] = df["PV_Diff"].abs() > self.pv_tolerance
        df["Delta_Mismatch"] = df["Delta_Diff"].abs() > self.delta_tolerance

        # Use fillna to handle NaN values before boolean operations
        df["Any_Mismatch"] = df["PV_Mismatch"].fillna(False) | df["Delta_Mismatch"].fillna(False)
        return df
