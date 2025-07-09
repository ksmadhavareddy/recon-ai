import pandas as pd

class DataLoaderAgent:
    def __init__(self, data_dir="data/"):
        self.data_dir = data_dir

    def load_all_data(self):
        old = pd.read_excel(f"{self.data_dir}/old_pricing.xlsx")
        new = pd.read_excel(f"{self.data_dir}/new_pricing.xlsx")
        meta = pd.read_excel(f"{self.data_dir}/trade_metadata.xlsx")
        funding = pd.read_excel(f"{self.data_dir}/funding_model_reference.xlsx")

        df = old.merge(new, on="TradeID", how="outer", suffixes=('_old', '_new'))
        df = df.merge(meta, on="TradeID", how="left")
        df = df.merge(funding, on="TradeID", how="left")
        return df
