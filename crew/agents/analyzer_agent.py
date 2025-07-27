import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from .dynamic_label_generator import DynamicLabelGenerator

logger = logging.getLogger(__name__)

class PVAnalysisAgent:
    def __init__(self, label_generator: Optional[DynamicLabelGenerator] = None):
        self.label_generator = label_generator or DynamicLabelGenerator()
        self.business_rules = self.label_generator.business_rules.get('pv_rules', [])
        
    def analyze(self, row: pd.Series) -> str:
        """
        Analyze PV-related issues using dynamic business rules.
        
        Args:
            row: DataFrame row containing trade data
            
        Returns:
            Diagnosis label based on business rules
        """
        # Apply business rules in priority order
        for rule in sorted(self.business_rules, key=lambda x: x.get('priority', 0), reverse=True):
            if self._evaluate_condition(row, rule['condition']):
                return rule['label']
        
        # Default fallback
        return "Within tolerance"
    
    def _evaluate_condition(self, row: pd.Series, condition: str) -> bool:
        """
        Evaluate a business rule condition against a data row.
        
        Args:
            row: DataFrame row
            condition: String condition to evaluate
            
        Returns:
            True if condition is met, False otherwise
        """
        try:
            # Handle common conditions
            if condition == "PV_old is None":
                return row.get("PV_old") is None
            elif condition == "PV_new is None":
                return row.get("PV_new") is None
            elif condition == "PV_Mismatch == False":
                return row.get("PV_Mismatch") == False
            elif condition == "PV_Mismatch == True":
                return row.get("PV_Mismatch") == True
            elif "FundingCurve == 'USD-LIBOR' and ModelVersion != 'v2024.3'" in condition:
                return (row.get("FundingCurve") == "USD-LIBOR" and 
                       row.get("ModelVersion") != "v2024.3")
            elif "CSA_Type == 'Cleared' and PV_Mismatch == True" in condition:
                return (row.get("CSA_Type") == "Cleared" and 
                       row.get("PV_Mismatch") == True)
            elif "CSA_Type == 'Cleared_CSA' and PV_Mismatch" in condition:
                return (row.get("CSA_Type") == "Cleared_CSA" and 
                       row.get("PV_Mismatch") == True)
            else:
                # Try to evaluate as a Python expression (with safety checks)
                return self._safe_eval_condition(row, condition)
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def _safe_eval_condition(self, row: pd.Series, condition: str) -> bool:
        """
        Safely evaluate a condition string against row data.
        
        Args:
            row: DataFrame row
            condition: Condition string to evaluate
            
        Returns:
            Evaluation result
        """
        try:
            # Create a safe namespace with row data
            safe_dict = {}
            for col in row.index:
                safe_dict[col] = row[col]
            
            # Add common operators and functions
            safe_dict.update({
                'None': None,
                'True': True,
                'False': False,
                'is': lambda x, y: x is y,
                'and': lambda x, y: x and y,
                'or': lambda x, y: x or y,
                'not': lambda x: not x
            })
            
            # Evaluate the condition
            result = eval(condition, {"__builtins__": {}}, safe_dict)
            return bool(result)
        except Exception as e:
            logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False

class DeltaAnalysisAgent:
    def __init__(self, label_generator: Optional[DynamicLabelGenerator] = None):
        self.label_generator = label_generator or DynamicLabelGenerator()
        self.business_rules = self.label_generator.business_rules.get('delta_rules', [])
        
    def analyze(self, row: pd.Series) -> str:
        """
        Analyze Delta-related issues using dynamic business rules.
        
        Args:
            row: DataFrame row containing trade data
            
        Returns:
            Diagnosis label based on business rules
        """
        # Apply business rules in priority order
        for rule in sorted(self.business_rules, key=lambda x: x.get('priority', 0), reverse=True):
            if self._evaluate_condition(row, rule['condition']):
                return rule['label']
        
        # Default fallback
        return "Within tolerance"
    
    def _evaluate_condition(self, row: pd.Series, condition: str) -> bool:
        """
        Evaluate a business rule condition against a data row.
        
        Args:
            row: DataFrame row
            condition: String condition to evaluate
            
        Returns:
            True if condition is met, False otherwise
        """
        try:
            # Handle common conditions
            if condition == "Delta_Mismatch == False":
                return row.get("Delta_Mismatch") == False
            elif condition == "Delta_Mismatch == True":
                return row.get("Delta_Mismatch") == True
            elif "ProductType == 'Option' and Delta_Mismatch == True" in condition:
                return (row.get("ProductType") == "Option" and 
                       row.get("Delta_Mismatch") == True)
            else:
                # Try to evaluate as a Python expression (with safety checks)
                return self._safe_eval_condition(row, condition)
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def _safe_eval_condition(self, row: pd.Series, condition: str) -> bool:
        """
        Safely evaluate a condition string against row data.
        
        Args:
            row: DataFrame row
            condition: Condition string to evaluate
            
        Returns:
            Evaluation result
        """
        try:
            # Create a safe namespace with row data
            safe_dict = {}
            for col in row.index:
                safe_dict[col] = row[col]
            
            # Add common operators and functions
            safe_dict.update({
                'None': None,
                'True': True,
                'False': False,
                'is': lambda x, y: x is y,
                'and': lambda x, y: x and y,
                'or': lambda x, y: x or y,
                'not': lambda x: not x
            })
            
            # Evaluate the condition
            result = eval(condition, {"__builtins__": {}}, safe_dict)
            return bool(result)
        except Exception as e:
            logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False

class AnalyzerAgent:
    def __init__(self, label_generator: Optional[DynamicLabelGenerator] = None):
        """
        Initialize the Analyzer Agent with dynamic label generation.
        
        Args:
            label_generator: Optional DynamicLabelGenerator instance
        """
        self.label_generator = label_generator or DynamicLabelGenerator()
        self.pv_agent = PVAnalysisAgent(self.label_generator)
        self.delta_agent = DeltaAnalysisAgent(self.label_generator)
        
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply rule-based analysis to the DataFrame.
        
        Args:
            df: Input DataFrame with trade data
            
        Returns:
            DataFrame with PV_Diagnosis and Delta_Diagnosis columns added
        """
        logger.info(f"Applying rule-based analysis to {len(df)} trades")
        
        # Apply PV analysis
        df["PV_Diagnosis"] = df.apply(self.pv_agent.analyze, axis=1)
        
        # Apply Delta analysis
        df["Delta_Diagnosis"] = df.apply(self.delta_agent.analyze, axis=1)
        
        # Update label generator with analysis results
        self._update_label_generator(df)
        
        logger.info(f"Analysis completed. PV diagnoses: {df['PV_Diagnosis'].nunique()} unique, "
                   f"Delta diagnoses: {df['Delta_Diagnosis'].nunique()} unique")
        
        return df
    
    def _update_label_generator(self, df: pd.DataFrame) -> None:
        """
        Update the label generator with current analysis results.
        
        Args:
            df: DataFrame with analysis results
        """
        try:
            analyzer_output = {
                'pv_diagnoses': df['PV_Diagnosis'].unique().tolist(),
                'delta_diagnoses': df['Delta_Diagnosis'].unique().tolist()
            }
            self.label_generator.update_from_analysis(df, analyzer_output)
            logger.info("Label generator updated with analysis results")
        except Exception as e:
            logger.warning(f"Failed to update label generator: {e}")
    
    def get_business_rules(self) -> Dict[str, List[Dict]]:
        """
        Get current business rules from the label generator.
        
        Returns:
            Dictionary of business rules by category
        """
        return self.label_generator.business_rules
    
    def add_business_rule(self, rule_type: str, condition: str, label: str, 
                         priority: int = 1, category: str = "custom") -> None:
        """
        Add a new business rule to the analyzer.
        
        Args:
            rule_type: Type of rule ('pv_rules' or 'delta_rules')
            condition: Condition string to evaluate
            label: Diagnosis label to return
            priority: Rule priority (higher = more important)
            category: Rule category
        """
        new_rule = {
            "condition": condition,
            "label": label,
            "priority": priority,
            "category": category
        }
        
        if rule_type not in self.label_generator.business_rules:
            self.label_generator.business_rules[rule_type] = []
        
        self.label_generator.business_rules[rule_type].append(new_rule)
        
        # Update the agents with new rules
        if rule_type == 'pv_rules':
            self.pv_agent.business_rules = self.label_generator.business_rules.get('pv_rules', [])
        elif rule_type == 'delta_rules':
            self.delta_agent.business_rules = self.label_generator.business_rules.get('delta_rules', [])
        
        logger.info(f"Added new {rule_type} rule: {condition} -> {label}")
    
    def get_analysis_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get statistics about the analysis results.
        
        Args:
            df: DataFrame with analysis results
            
        Returns:
            Dictionary with analysis statistics
        """
        if 'PV_Diagnosis' not in df.columns or 'Delta_Diagnosis' not in df.columns:
            return {"error": "Analysis not yet applied"}
        
        return {
            'total_trades': len(df),
            'pv_diagnoses': {
                'unique_count': df['PV_Diagnosis'].nunique(),
                'distribution': df['PV_Diagnosis'].value_counts().to_dict()
            },
            'delta_diagnoses': {
                'unique_count': df['Delta_Diagnosis'].nunique(),
                'distribution': df['Delta_Diagnosis'].value_counts().to_dict()
            },
            'business_rules': {
                'pv_rules_count': len(self.label_generator.business_rules.get('pv_rules', [])),
                'delta_rules_count': len(self.label_generator.business_rules.get('delta_rules', []))
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Create sample data
    sample_data = pd.DataFrame({
        'TradeID': ['T001', 'T002', 'T003', 'T004', 'T005'],
        'PV_old': [100000, 200000, None, 150000, 250000],
        'PV_new': [101000, 198000, 50000, None, 252000],
        'Delta_old': [0.5, -0.8, 0.0, 0.3, -0.6],
        'Delta_new': [0.52, -0.82, 0.01, 0.28, -0.58],
        'ProductType': ['Swap', 'Swap', 'Option', 'Swap', 'Option'],
        'FundingCurve': ['USD-LIBOR', 'EUR-LIBOR', 'USD-LIBOR', 'USD-LIBOR', 'EUR-LIBOR'],
        'CSA_Type': ['Cleared', 'Bilateral', 'Cleared', 'Cleared', 'Bilateral'],
        'ModelVersion': ['v2024.1', 'v2024.2', 'v2024.3', 'v2024.1', 'v2024.2'],
        'PV_Mismatch': [False, True, False, True, False],
        'Delta_Mismatch': [False, True, False, False, True]
    })
    
    # Initialize analyzer with dynamic label generator
    analyzer = AnalyzerAgent()
    
    # Apply analysis
    result_df = analyzer.apply(sample_data)
    
    # Get statistics
    stats = analyzer.get_analysis_statistics(result_df)
    
    print("Analysis Results:")
    print(f"Total trades: {stats['total_trades']}")
    print(f"PV diagnoses: {stats['pv_diagnoses']['unique_count']} unique")
    print(f"Delta diagnoses: {stats['delta_diagnoses']['unique_count']} unique")
    print(f"Business rules: {stats['business_rules']['pv_rules_count']} PV rules, "
          f"{stats['business_rules']['delta_rules_count']} Delta rules")
    
    print("\nPV Diagnosis Distribution:")
    for diagnosis, count in stats['pv_diagnoses']['distribution'].items():
        print(f"  {diagnosis}: {count}")
    
    print("\nDelta Diagnosis Distribution:")
    for diagnosis, count in stats['delta_diagnoses']['distribution'].items():
        print(f"  {diagnosis}: {count}")
