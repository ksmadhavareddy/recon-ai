import pandas as pd
import os
from catboost import CatBoostClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

class MLDiagnoserAgent:
    def __init__(self, model_path="models/catboost_diagnoser.pkl"):
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        if os.path.exists(self.model_path):
            self.load_model()

    def prepare_features_and_labels(self, df):
        # Select features (excluding IDs and labels)
        feature_cols = [
            'PV_old', 'PV_new', 'Delta_old', 'Delta_new',
            'ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion'
        ]
        X = df[feature_cols].copy()
        # Encode categorical features
        for col in ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']:
            X[col] = X[col].astype(str)
        # Label encoding for target
        y = df['Diagnosis'].astype(str)
        if self.label_encoder is None:
            self.label_encoder = LabelEncoder()
            y_enc = self.label_encoder.fit_transform(y)
        else:
            y_enc = self.label_encoder.transform(y)
        return X, y_enc

    def train(self, df):
        X, y = self.prepare_features_and_labels(df)
        # Specify categorical features for CatBoost
        cat_features = ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']
        cat_indices = [X.columns.get_loc(col) for col in cat_features]
        
        self.model = CatBoostClassifier(verbose=0)
        self.model.fit(X, y, cat_features=cat_indices)
        self.save_model()
        print("✅ ML model trained and saved.")

    def predict(self, df):
        X, _ = self.prepare_features_and_labels(df)
        preds = self.model.predict(X)
        return self.label_encoder.inverse_transform(preds)

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'label_encoder': self.label_encoder
        }, self.model_path)

    def load_model(self):
        obj = joblib.load(self.model_path)
        self.model = obj['model']
        self.label_encoder = obj['label_encoder'] 