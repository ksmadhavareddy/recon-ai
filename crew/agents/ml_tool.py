import pandas as pd
import os
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import numpy as np
import logging
import time
from typing import Dict, List, Tuple, Optional, Any
from .dynamic_label_generator import DynamicLabelGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLDiagnoserAgent:
    def __init__(self, model_path="models/lightgbm_diagnoser.txt"):
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        self.training_history = {}
        self.feature_names = [
            'PV_old', 'PV_new', 'Delta_old', 'Delta_new',
            'ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion'
        ]
        self.categorical_features = ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']
        
        # Initialize dynamic label generator
        self.label_generator = DynamicLabelGenerator()
        
        if os.path.exists(self.model_path):
            self.load_model()
    
    @property
    def ALL_POSSIBLE_LABELS(self) -> List[str]:
        """Dynamic property that generates labels based on current data and patterns"""
        # This will be updated during training/prediction based on actual data
        return self.label_generator.generate_labels(pd.DataFrame(), include_discovered=False)

    def prepare_features_and_labels(self, df: pd.DataFrame, label_col: str = 'PV_Diagnosis') -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Prepare features and labels for ML training/prediction.
        
        Args:
            df: Input DataFrame
            label_col: Column name containing diagnosis labels
            
        Returns:
            Tuple of (features, encoded_labels)
        """
        # Validate required features
        missing_features = [col for col in self.feature_names if col not in df.columns]
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        
        X = df[self.feature_names].copy()
        
        # Handle categorical features
        for col in self.categorical_features:
            if not pd.api.types.is_categorical_dtype(X[col]):
                X[col] = X[col].astype('category')
        
        # Handle label column
        if label_col not in df.columns:
            raise KeyError(f"Label column '{label_col}' not found. Available columns: {list(df.columns)}")
        
        y = df[label_col].astype(str)
        
        # Initialize or use existing label encoder
        if self.label_encoder is None:
            self.label_encoder = LabelEncoder()
            # Generate dynamic labels based on current data
            dynamic_labels = self.label_generator.generate_labels(df, include_discovered=True, include_historical=True)
            # Fit on the union of dynamic labels and those present in y
            all_labels = pd.Series(list(set(dynamic_labels) | set(y.unique())))
            self.label_encoder.fit(all_labels)
            logger.info(f"Label encoder fitted with {len(self.label_encoder.classes_)} classes")
            logger.info(f"Dynamic labels generated: {len(dynamic_labels)} labels")
        
        y_enc = self.label_encoder.transform(y)
        
        logger.info(f"Prepared features: {X.shape}, labels: {y_enc.shape}")
        return X, y_enc

    def train(self, df: pd.DataFrame, label_col: str = 'PV_Diagnosis', 
              validation_df: Optional[pd.DataFrame] = None,
              **kwargs) -> Dict[str, Any]:
        """
        Train the LightGBM model using rule-based diagnoses as labels.
        
        Args:
            df: Training DataFrame
            label_col: Column name containing diagnosis labels
            validation_df: Optional validation DataFrame
            **kwargs: Additional LightGBM parameters
            
        Returns:
            Dictionary containing training metrics and history
        """
        start_time = time.time()
        logger.info(f"Starting training with {len(df)} samples")
        
        # Validate input
        if label_col not in df.columns:
            raise KeyError(f"Label column '{label_col}' not found. Available columns: {list(df.columns)}")
        
        # Prepare training data
        X_train, y_train = self.prepare_features_and_labels(df, label_col)
        
        # Create LightGBM dataset
        train_data = lgb.Dataset(
            X_train, 
            label=y_train, 
            categorical_feature=self.categorical_features,
            free_raw_data=False
        )
        
        # Prepare validation data if provided
        valid_data = None
        if validation_df is not None:
            X_val, y_val = self.prepare_features_and_labels(validation_df, label_col)
            valid_data = lgb.Dataset(
                X_val, 
                label=y_val, 
                categorical_feature=self.categorical_features,
                free_raw_data=False
            )
        
        # Configure model parameters
        params = {
            'objective': 'multiclass' if len(self.label_encoder.classes_) > 2 else 'binary',
            'num_class': len(self.label_encoder.classes_) if len(self.label_encoder.classes_) > 2 else 1,
            'metric': 'multi_logloss' if len(self.label_encoder.classes_) > 2 else 'binary_logloss',
            'verbose': -1,
            'boosting_type': 'gbdt',
            'num_leaves': kwargs.get('num_leaves', 31),
            'learning_rate': kwargs.get('learning_rate', 0.1),
            'feature_fraction': kwargs.get('feature_fraction', 0.9),
            'bagging_fraction': kwargs.get('bagging_fraction', 0.8),
            'bagging_freq': kwargs.get('bagging_freq', 5),
            'min_data_in_leaf': kwargs.get('min_data_in_leaf', 20),
            'lambda_l1': kwargs.get('lambda_l1', 0),
            'lambda_l2': kwargs.get('lambda_l2', 0),
            'seed': kwargs.get('seed', 42)
        }
        
        # Train model
        callbacks = [lgb.log_evaluation(period=10)] if logger.level <= logging.INFO else []
        
        self.model = lgb.train(
            params, 
            train_data, 
            valid_sets=[valid_data] if valid_data else None,
            num_boost_round=kwargs.get('num_boost_round', 100),
            callbacks=callbacks
        )
        
        # Save model
        self.save_model()
        
        # Calculate training metrics
        train_predictions = self.predict(df, label_col)
        train_accuracy = accuracy_score(df[label_col], train_predictions)
        
        training_time = time.time() - start_time
        
        # Store training history
        self.training_history = {
            'training_samples': len(df),
            'validation_samples': len(validation_df) if validation_df is not None else 0,
            'num_classes': len(self.label_encoder.classes_),
            'training_accuracy': train_accuracy,
            'training_time_seconds': training_time,
            'model_parameters': params
        }
        
        # Update label generator with current analysis results
        analyzer_output = {
            'pv_diagnoses': df['PV_Diagnosis'].unique().tolist() if 'PV_Diagnosis' in df.columns else [],
            'delta_diagnoses': df['Delta_Diagnosis'].unique().tolist() if 'Delta_Diagnosis' in df.columns else []
        }
        self.label_generator.update_from_analysis(df, analyzer_output)
        
        logger.info(f"✅ Training completed in {training_time:.2f}s")
        logger.info(f"Training accuracy: {train_accuracy:.2%}")
        
        return self.training_history

    def predict(self, df: pd.DataFrame, label_col: str = 'PV_Diagnosis') -> np.ndarray:
        """
        Generate ML-based diagnoses for input data.
        
        Args:
            df: Input DataFrame
            label_col: Column name for label reference
            
        Returns:
            Array of predicted diagnosis strings
        """
        if self.model is None:
            raise ValueError("Model is not loaded. Please train or load model first.")
        
        start_time = time.time()
        logger.info(f"Making predictions for {len(df)} samples")
        
        # Prepare features
        X, _ = self.prepare_features_and_labels(df, label_col)
        
        # Generate predictions
        preds = self.model.predict(X)
        
        # Convert probabilities to class labels
        if preds.ndim == 1:
            # Binary classification: preds are probabilities for class 1
            pred_labels = (preds > 0.5).astype(int)
        else:
            # Multiclass: preds are probabilities for each class
            pred_labels = preds.argmax(axis=1)
        
        # Decode labels back to strings
        predictions = self.label_encoder.inverse_transform(pred_labels)
        
        prediction_time = time.time() - start_time
        logger.info(f"Predictions completed in {prediction_time:.2f}s")
        logger.info(f"Average time per prediction: {prediction_time/len(df)*1000:.2f}ms")
        
        return predictions

    def evaluate_model(self, test_df: pd.DataFrame, true_labels: pd.Series) -> Dict[str, Any]:
        """
        Evaluate model performance on test data.
        
        Args:
            test_df: Test DataFrame
            true_labels: True diagnosis labels
            
        Returns:
            Dictionary containing evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model is not loaded. Please train or load model first.")
        
        # Make predictions
        predictions = self.predict(test_df, label_col='PV_Diagnosis')
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, predictions)
        class_report = classification_report(true_labels, predictions, output_dict=True)
        conf_matrix = confusion_matrix(true_labels, predictions)
        
        # Calculate per-class accuracy
        unique_labels = np.unique(np.concatenate([true_labels.unique(), predictions]))
        per_class_accuracy = {}
        for label in unique_labels:
            mask = true_labels == label
            if mask.sum() > 0:
                per_class_accuracy[label] = (predictions[mask] == true_labels[mask]).mean()
        
        evaluation_results = {
            'overall_accuracy': accuracy,
            'classification_report': class_report,
            'confusion_matrix': conf_matrix.tolist(),
            'per_class_accuracy': per_class_accuracy,
            'num_test_samples': len(test_df),
            'unique_predictions': list(set(predictions)),
            'prediction_distribution': pd.Series(predictions).value_counts().to_dict()
        }
        
        logger.info(f"Model evaluation completed:")
        logger.info(f"Overall accuracy: {accuracy:.2%}")
        logger.info(f"Per-class accuracy: {per_class_accuracy}")
        
        return evaluation_results

    def get_feature_importance(self, importance_type: str = 'gain') -> pd.DataFrame:
        """
        Get feature importance from trained model.
        
        Args:
            importance_type: Type of importance ('gain', 'split', 'cover')
            
        Returns:
            DataFrame with feature importance scores
        """
        if self.model is None:
            raise ValueError("Model is not loaded. Please train or load model first.")
        
        importance = self.model.feature_importance(importance_type=importance_type)
        
        importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': importance
        }).sort_values('Importance', ascending=False)
        
        logger.info(f"Feature importance (type: {importance_type}):")
        logger.info(importance_df.to_string(index=False))
        
        return importance_df

    def save_model(self) -> None:
        """Save the trained model and label encoder to disk."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        if self.model is not None:
            self.model.save_model(self.model_path)
            logger.info(f"Model saved to: {self.model_path}")
        
        if self.label_encoder is not None:
            joblib.dump({
                'label_encoder': self.label_encoder,
                'training_history': self.training_history,
                'feature_names': self.feature_names,
                'categorical_features': self.categorical_features
            }, self.model_path + '.le')
            logger.info(f"Label encoder saved to: {self.model_path}.le")

    def load_model(self) -> None:
        """Load a previously trained model and label encoder from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        # Load LightGBM model
        self.model = lgb.Booster(model_file=self.model_path)
        logger.info(f"Model loaded from: {self.model_path}")
        
        # Load label encoder and metadata
        le_path = self.model_path + '.le'
        if os.path.exists(le_path):
            obj = joblib.load(le_path)
            self.label_encoder = obj['label_encoder']
            self.training_history = obj.get('training_history', {})
            self.feature_names = obj.get('feature_names', self.feature_names)
            self.categorical_features = obj.get('categorical_features', self.categorical_features)
            logger.info(f"Label encoder loaded from: {le_path}")
        else:
            logger.warning(f"Label encoder file not found: {le_path}")

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the trained model.
        
        Returns:
            Dictionary containing model information
        """
        info = {
            'model_loaded': self.model is not None,
            'model_path': self.model_path,
            'label_encoder_loaded': self.label_encoder is not None,
            'num_classes': len(self.label_encoder.classes_) if self.label_encoder else 0,
            'classes': list(self.label_encoder.classes_) if self.label_encoder else [],
            'feature_names': self.feature_names,
            'categorical_features': self.categorical_features,
            'training_history': self.training_history
        }
        
        if self.model is not None:
            info.update({
                'num_trees': self.model.num_trees(),
                'num_features': self.model.num_features(),
                'model_size_mb': os.path.getsize(self.model_path) / (1024 * 1024) if os.path.exists(self.model_path) else 0
            })
        
        return info

    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate input data for training or prediction.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            'valid': True,
            'issues': [],
            'warnings': []
        }
        
        # Check required columns
        missing_features = [col for col in self.feature_names if col not in df.columns]
        if missing_features:
            validation_results['valid'] = False
            validation_results['issues'].append(f"Missing required features: {missing_features}")
        
        # Check data types
        for col in self.categorical_features:
            if col in df.columns and not pd.api.types.is_categorical_dtype(df[col]):
                validation_results['warnings'].append(f"Column {col} should be categorical")
        
        # Check for missing values
        for col in self.feature_names:
            if col in df.columns and df[col].isnull().any():
                validation_results['warnings'].append(f"Missing values in {col}")
        
        # Check for infinite values in numerical columns
        numerical_cols = ['PV_old', 'PV_new', 'Delta_old', 'Delta_new']
        for col in numerical_cols:
            if col in df.columns and np.isinf(df[col]).any():
                validation_results['warnings'].append(f"Infinite values in {col}")
        
        # Check data size
        if len(df) == 0:
            validation_results['valid'] = False
            validation_results['issues'].append("DataFrame is empty")
        
        return validation_results

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
        'PV_Diagnosis': ['Within tolerance', 'Review', 'Within tolerance', 'Review']
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
    
    # Validate data first
    validation_results = agent.validate_data(df)
    print(f"Data validation: {validation_results}")
    
    # Train model
    training_history = agent.train(df, label_col='PV_Diagnosis')
    print(f"Training history: {training_history}")
    
    # Get model info
    model_info = agent.get_model_info()
    print(f"Model info: {model_info}")
    
    # Get feature importance
    importance_df = agent.get_feature_importance()
    print(f"Feature importance:\n{importance_df}")

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
        'PV_Diagnosis': ['Within tolerance', 'Review']  # Dummy values for label_col
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
    
    # Evaluate model
    evaluation_results = agent.evaluate_model(test_df, test_df['PV_Diagnosis'])
    print(f"Evaluation results: {evaluation_results}")
    
    print("[DEBUG] __main__ block completed.") 