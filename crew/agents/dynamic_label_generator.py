import pandas as pd
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class DynamicLabelGenerator:
    """
    Dynamic label generator for real-time diagnosis scenarios.
    
    This class generates diagnosis labels based on:
    1. Business rules from analyzer agents
    2. Data patterns and anomalies
    3. Domain knowledge and industry standards
    4. Historical analysis of root causes
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/diagnosis_labels.json"
        self.business_rules = self._load_business_rules()
        self.domain_knowledge = self._load_domain_knowledge()
        self.historical_patterns = {}
        self.label_frequency = {}
        self.last_update = None
        
    def _load_business_rules(self) -> Dict[str, List[Dict]]:
        """Load business rules for diagnosis generation"""
        return {
            "pv_rules": [
                {
                    "condition": "PV_old is None",
                    "label": "New trade – no prior valuation",
                    "priority": 1,
                    "category": "trade_lifecycle"
                },
                {
                    "condition": "PV_new is None", 
                    "label": "Trade dropped from new model",
                    "priority": 1,
                    "category": "trade_lifecycle"
                },
                {
                    "condition": "FundingCurve == 'USD-LIBOR' and ModelVersion != 'v2024.3'",
                    "label": "Legacy LIBOR curve with outdated model – PV likely shifted",
                    "priority": 2,
                    "category": "curve_model"
                },
                {
                    "condition": "CSA_Type == 'Cleared' and PV_Mismatch == True",
                    "label": "CSA changed post-clearing – funding basis moved",
                    "priority": 2,
                    "category": "funding_csa"
                },
                {
                    "condition": "PV_Mismatch == False",
                    "label": "Within tolerance",
                    "priority": 0,
                    "category": "tolerance"
                }
            ],
            "delta_rules": [
                {
                    "condition": "ProductType == 'Option' and Delta_Mismatch == True",
                    "label": "Vol sensitivity likely – delta impact due to model curve shift",
                    "priority": 2,
                    "category": "volatility"
                },
                {
                    "condition": "Delta_Mismatch == False",
                    "label": "Within tolerance",
                    "priority": 0,
                    "category": "tolerance"
                }
            ]
        }
    
    def _load_domain_knowledge(self) -> Dict[str, List[str]]:
        """Load domain-specific diagnosis categories"""
        return {
            "trade_lifecycle": [
                "New trade – no prior valuation",
                "Trade dropped from new model",
                "Trade amended with new terms",
                "Trade matured or expired"
            ],
            "curve_model": [
                "Legacy LIBOR curve with outdated model – PV likely shifted",
                "SOFR transition impact – curve basis changed",
                "Model version update – methodology changed",
                "Curve interpolation changed – end points affected"
            ],
            "funding_csa": [
                "CSA changed post-clearing – funding basis moved",
                "Collateral threshold changed – funding cost shifted",
                "New clearing house – margin requirements different",
                "Bilateral to cleared transition – funding curve changed"
            ],
            "volatility": [
                "Vol sensitivity likely – delta impact due to model curve shift",
                "Vol surface updated – smile/skew changed",
                "Market stress – vol regime shifted",
                "Option-specific model change – vol dynamics affected"
            ],
            "tolerance": [
                "Within tolerance",
                "Minor deviation – no action required",
                "Acceptable range – monitor for trends"
            ],
            "data_quality": [
                "Missing data – incomplete valuation",
                "Data corruption – invalid inputs",
                "Timing mismatch – stale data",
                "System error – calculation failed"
            ],
            "market_events": [
                "Market volatility – broad repricing",
                "Credit event – counterparty risk changed",
                "Regulatory change – capital requirements updated",
                "Liquidity crisis – funding costs spiked"
            ]
        }
    
    def discover_patterns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Discover new patterns in the data that might indicate new diagnosis categories.
        
        Args:
            df: DataFrame with trade data and diagnoses
            
        Returns:
            Dictionary of discovered patterns by category
        """
        patterns = {}
        
        # Analyze PV patterns
        if 'PV_Diagnosis' in df.columns:
            pv_patterns = self._analyze_pv_patterns(df)
            patterns['pv_patterns'] = pv_patterns
        
        # Analyze Delta patterns  
        if 'Delta_Diagnosis' in df.columns:
            delta_patterns = self._analyze_delta_patterns(df)
            patterns['delta_patterns'] = delta_patterns
        
        # Analyze temporal patterns
        temporal_patterns = self._analyze_temporal_patterns(df)
        patterns['temporal_patterns'] = temporal_patterns
        
        # Analyze product-specific patterns
        product_patterns = self._analyze_product_patterns(df)
        patterns['product_patterns'] = product_patterns
        
        return patterns
    
    def _analyze_pv_patterns(self, df: pd.DataFrame) -> List[str]:
        """Analyze PV-related patterns"""
        patterns = []
        
        # Check for funding curve transitions
        if 'FundingCurve' in df.columns:
            curve_changes = df.groupby('FundingCurve')['PV_Mismatch'].mean()
            if len(curve_changes) > 1:
                patterns.append("Multiple funding curves detected - curve-specific issues")
        
        # Check for model version issues
        if 'ModelVersion' in df.columns:
            version_issues = df.groupby('ModelVersion')['PV_Mismatch'].mean()
            if len(version_issues) > 1:
                patterns.append("Model version differences detected - version-specific issues")
        
        # Check for CSA type patterns
        if 'CSA_Type' in df.columns:
            csa_patterns = df.groupby('CSA_Type')['PV_Mismatch'].mean()
            if len(csa_patterns) > 1:
                patterns.append("CSA type differences detected - clearing vs bilateral issues")
        
        return patterns
    
    def _analyze_delta_patterns(self, df: pd.DataFrame) -> List[str]:
        """Analyze Delta-related patterns"""
        patterns = []
        
        # Check for product type patterns
        if 'ProductType' in df.columns:
            product_delta = df.groupby('ProductType')['Delta_Mismatch'].mean()
            if len(product_delta) > 1:
                patterns.append("Product-specific delta issues detected")
        
        # Check for volatility patterns
        if 'Delta_Diff' in df.columns:
            vol_patterns = df[df['Delta_Mismatch']]['Delta_Diff'].abs().describe()
            if vol_patterns['std'] > 0.1:
                patterns.append("High delta volatility detected - vol surface issues")
        
        return patterns
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> List[str]:
        """Analyze temporal patterns in the data"""
        patterns = []
        
        # Check for time-based patterns if date column exists
        if 'TradeDate' in df.columns:
            df['TradeDate'] = pd.to_datetime(df['TradeDate'])
            daily_mismatches = df.groupby(df['TradeDate'].dt.date)['Any_Mismatch'].sum()
            if daily_mismatches.std() > 2:
                patterns.append("Temporal clustering of mismatches detected")
        
        return patterns
    
    def _analyze_product_patterns(self, df: pd.DataFrame) -> List[str]:
        """Analyze product-specific patterns"""
        patterns = []
        
        if 'ProductType' in df.columns:
            # Check for product-specific issues
            product_mismatches = df.groupby('ProductType')['Any_Mismatch'].mean()
            for product, mismatch_rate in product_mismatches.items():
                if mismatch_rate > 0.5:
                    patterns.append(f"High mismatch rate for {product} products")
        
        return patterns
    
    def generate_labels(self, df: pd.DataFrame, 
                       include_discovered: bool = True,
                       include_historical: bool = True) -> List[str]:
        """
        Generate comprehensive list of possible diagnosis labels.
        
        Args:
            df: DataFrame with trade data
            include_discovered: Whether to include discovered patterns
            include_historical: Whether to include historical patterns
            
        Returns:
            List of all possible diagnosis labels
        """
        labels = set()
        
        # Add labels from business rules
        for rule_type, rules in self.business_rules.items():
            for rule in rules:
                labels.add(rule['label'])
        
        # Add labels from domain knowledge
        for category, category_labels in self.domain_knowledge.items():
            labels.update(category_labels)
        
        # Add discovered patterns if requested
        if include_discovered:
            patterns = self.discover_patterns(df)
            for pattern_list in patterns.values():
                labels.update(pattern_list)
        
        # Add historical patterns if requested
        if include_historical and self.historical_patterns:
            for pattern_list in self.historical_patterns.values():
                labels.update(pattern_list)
        
        # Add frequency-based labels
        if self.label_frequency:
            frequent_labels = [label for label, freq in self.label_frequency.items() 
                             if freq > 5]  # Labels that appeared more than 5 times
            labels.update(frequent_labels)
        
        return sorted(list(labels))
    
    def update_from_analysis(self, df: pd.DataFrame, 
                           analyzer_output: Dict[str, List[str]]) -> None:
        """
        Update label generator based on recent analysis results.
        
        Args:
            df: DataFrame with trade data
            analyzer_output: Output from analyzer agents
        """
        # Update historical patterns
        patterns = self.discover_patterns(df)
        for category, pattern_list in patterns.items():
            if category not in self.historical_patterns:
                self.historical_patterns[category] = []
            self.historical_patterns[category].extend(pattern_list)
        
        # Update label frequency
        if 'PV_Diagnosis' in df.columns:
            pv_counts = df['PV_Diagnosis'].value_counts()
            for label, count in pv_counts.items():
                self.label_frequency[label] = self.label_frequency.get(label, 0) + count
        
        if 'Delta_Diagnosis' in df.columns:
            delta_counts = df['Delta_Diagnosis'].value_counts()
            for label, count in delta_counts.items():
                self.label_frequency[label] = self.label_frequency.get(label, 0) + count
        
        # Update timestamp
        self.last_update = datetime.now()
        
        # Save updated patterns
        self._save_patterns()
    
    def _save_patterns(self) -> None:
        """Save discovered patterns to configuration file"""
        config_data = {
            'historical_patterns': self.historical_patterns,
            'label_frequency': self.label_frequency,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'business_rules': self.business_rules,
            'domain_knowledge': self.domain_knowledge
        }
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logger.info(f"Saved patterns to {self.config_path}")
    
    def get_label_categories(self) -> Dict[str, List[str]]:
        """Get labels organized by category"""
        categories = {}
        
        # Business rule categories
        for rule_type, rules in self.business_rules.items():
            category = rule_type.replace('_rules', '')
            categories[category] = [rule['label'] for rule in rules]
        
        # Domain knowledge categories
        categories.update(self.domain_knowledge)
        
        # Historical patterns
        if self.historical_patterns:
            categories['discovered_patterns'] = []
            for pattern_list in self.historical_patterns.values():
                categories['discovered_patterns'].extend(pattern_list)
        
        return categories
    
    def get_label_statistics(self) -> Dict[str, Any]:
        """Get statistics about label usage"""
        return {
            'total_unique_labels': len(self.label_frequency),
            'most_frequent_labels': sorted(self.label_frequency.items(), 
                                         key=lambda x: x[1], reverse=True)[:10],
            'label_frequency': self.label_frequency,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'pattern_categories': list(self.historical_patterns.keys())
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
        'Delta_Mismatch': [False, True, False, False, True],
        'Any_Mismatch': [False, True, False, True, True],
        'PV_Diagnosis': ['Within tolerance', 'Legacy LIBOR curve with outdated model – PV likely shifted', 
                        'New trade – no prior valuation', 'Trade dropped from new model', 'Within tolerance'],
        'Delta_Diagnosis': ['Within tolerance', 'Vol sensitivity likely – delta impact due to model curve shift',
                           'Within tolerance', 'Within tolerance', 'Vol sensitivity likely – delta impact due to model curve shift']
    })
    
    # Initialize label generator
    generator = DynamicLabelGenerator()
    
    # Generate labels
    labels = generator.generate_labels(sample_data)
    print(f"Generated {len(labels)} labels:")
    for label in labels:
        print(f"  - {label}")
    
    # Update from analysis
    generator.update_from_analysis(sample_data, {})
    
    # Get statistics
    stats = generator.get_label_statistics()
    print(f"\nLabel statistics: {stats}") 