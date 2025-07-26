import pandas as pd
import os
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
import joblib

class MLDiagnoserAgent:
    ALL_POSSIBLE_LABELS = [
        "New trade – no prior valuation",
        "Trade dropped from new model",
        "Legacy LIBOR curve with outdated model – PV likely shifted",
        "CSA changed post-clearing – funding basis moved",
        "Vol sensitivity likely – delta impact due to model curve shift",
        "Within tolerance"
    ]

    def __init__(self, model_path="models/lightgbm_diagnoser.txt"):
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        if os.path.exists(self.model_path):
            self.load_model()

    def prepare_features_and_labels(self, df, label_col='PV_Diagnosis'):
        feature_cols = [
            'PV_old', 'PV_new', 'Delta_old', 'Delta_new',
            'ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion'
        ]
        X = df[feature_cols].copy()
        for col in ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']:
            if not pd.api.types.is_categorical_dtype(X[col]):
                X[col] = X[col].astype('category')
        y = df[label_col].astype(str)
        if self.label_encoder is None:
            self.label_encoder = LabelEncoder()
            # Fit on the union of all possible labels and those present in y
            all_labels = pd.Series(list(set(self.ALL_POSSIBLE_LABELS) | set(y.unique())))
            self.label_encoder.fit(all_labels)
            y_enc = self.label_encoder.transform(y)
        else:
            y_enc = self.label_encoder.transform(y)
        return X, y_enc

    def train(self, df, label_col='PV_Diagnosis'):
        print(f"[MLDiagnoserAgent] train: Available columns: {list(df.columns)}")
        if label_col not in df.columns:
            print(f"[MLDiagnoserAgent] ERROR: Label column '{label_col}' not found in DataFrame. Available columns: {list(df.columns)}")
            raise KeyError(f"Label column '{label_col}' not found in DataFrame. Available columns: {list(df.columns)}")
        X, y = self.prepare_features_and_labels(df, label_col=label_col)
        cat_features = ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']
        lgb_data = lgb.Dataset(X, label=y, categorical_feature=cat_features, free_raw_data=False)
        params = {
            'objective': 'multiclass' if len(self.label_encoder.classes_) > 2 else 'binary',
            'num_class': len(self.label_encoder.classes_) if len(self.label_encoder.classes_) > 2 else 1,
            'metric': 'multi_logloss' if len(self.label_encoder.classes_) > 2 else 'binary_logloss',
            'verbose': -1
        }
        self.model = lgb.train(params, lgb_data, num_boost_round=100)
        self.save_model()
        print("✅ ML model trained and saved.")

    def predict(self, df, label_col='PV_Diagnosis'):
        print(f"[MLDiagnoserAgent] predict: Available columns: {list(df.columns)}")
        if self.model is None:
            raise ValueError("Model is not loaded.")
        X, _ = self.prepare_features_and_labels(df, label_col=label_col)
        preds = self.model.predict(X)
        if preds.ndim == 1:
            # Binary classification: preds are probabilities for class 1
            pred_labels = (preds > 0.5).astype(int)
        else:
            # Multiclass: preds are probabilities for each class
            pred_labels = preds.argmax(axis=1)
        return self.label_encoder.inverse_transform(pred_labels)

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.model.save_model(self.model_path)
        joblib.dump({'label_encoder': self.label_encoder}, self.model_path + '.le')

    def load_model(self):
        self.model = lgb.Booster(model_file=self.model_path)
        le_path = self.model_path + '.le'
        if os.path.exists(le_path):
            obj = joblib.load(le_path)
            self.label_encoder = obj['label_encoder'] 

if __name__ == "__main__":
    print("[DEBUG] __main__ block is running.")
    # Sample data for demonstration
    import numpy as np
    data = {
        'PV_old': [100, 200, 150, 120],
        'PV_new': [110, 210, 160, 130],
        'Delta_old': [10, 20, 15, 12],
        'Delta_new': [12, 22, 18, 14],
        'ProductType': ['Swap', 'Option', 'Swap', 'Option'],
        'FundingCurve': ['CurveA', 'CurveB', 'CurveA', 'CurveB'],
        'CSA_Type': ['Type1', 'Type2', 'Type1', 'Type2'],
        'ModelVersion': ['v1', 'v2', 'v1', 'v2'],
        'PV_Diagnosis': ['OK', 'Review', 'OK', 'Review']
    }
    df = pd.DataFrame(data)
    for col in ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']:
        df[col] = df[col].astype('category')
    print("[DEBUG] Training DataFrame:")
    print(df)
    print("[DEBUG] Training DataFrame dtypes:")
    print(df.dtypes)
    for col in ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']:
        print(f"[DEBUG] Training DataFrame '{col}' categories: {df[col].cat.categories}")

    print("\n--- Training MLDiagnoserAgent ---")
    agent = MLDiagnoserAgent()
    agent.train(df, label_col='PV_Diagnosis')

    print("\n--- Predicting with MLDiagnoserAgent ---")
    test_data = {
        'PV_old': [105, 205],
        'PV_new': [115, 215],
        'Delta_old': [11, 21],
        'Delta_new': [13, 23],
        'ProductType': ['Swap', 'Option'],
        'FundingCurve': ['CurveA', 'CurveB'],
        'CSA_Type': ['Type1', 'Type2'],
        'ModelVersion': ['v1', 'v2'],
        'PV_Diagnosis': ['OK', 'Review']  # Dummy values for label_col
    }
    test_df = pd.DataFrame(test_data)
    for col in ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']:
        test_df[col] = test_df[col].astype('category')
        # Ensure categories match training data
        test_df[col] = test_df[col].cat.set_categories(df[col].cat.categories)
    print("[DEBUG] Test DataFrame:")
    print(test_df)
    print("[DEBUG] Test DataFrame dtypes:")
    print(test_df.dtypes)
    for col in ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']:
        print(f"[DEBUG] Test DataFrame '{col}' categories: {test_df[col].cat.categories}")
    preds = agent.predict(test_df, label_col='PV_Diagnosis')
    print("Predictions:", preds)
    print("[DEBUG] __main__ block completed.") 