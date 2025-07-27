# 📖 Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd recon-ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare Your Data

#### **Option A: File-based Data (Auto-Load)**
Place your input files in the `data/` directory for automatic loading:

```
data/
├── old_pricing.xlsx      # Previous pricing data
├── new_pricing.xlsx      # Current pricing data
├── trade_metadata.xlsx   # Trade characteristics
└── funding_model_reference.xlsx  # Funding information
```

**🚀 Auto-Load Feature**: The Streamlit dashboard now includes an auto-load functionality that automatically loads all 4 files from the `data/` directory with visual status indicators and ready confirmation.

#### **Option B: Manual File Upload**
Alternatively, you can manually upload files through the Streamlit dashboard interface.

#### **Option C: API-based Data**
Configure API endpoints in `api_config.json`:

```json
{
  "base_url": "https://api.example.com",
  "api_key": "your_api_key_here",
  "endpoints": {
    "old_pricing": "/api/v1/pricing/old",
    "new_pricing": "/api/v1/pricing/new",
    "trade_metadata": "/api/v1/trades/metadata",
    "funding_reference": "/api/v1/funding/reference"
  }
}
```

### 3. Run the Pipeline

#### **Basic Usage:**
```bash
# Auto-detect (default) - tries API first, falls back to files
python pipeline.py

# File-based only
python pipeline.py --source files

# API-based only
python pipeline.py --source api --api-config api_config.json

# Hybrid - loads from both sources and merges
python pipeline.py --source hybrid --api-config api_config.json
```

#### **Advanced Usage:**
```bash
# With specific trade IDs
python pipeline.py --source api --api-config api_config.json --trade-ids TRADE001 TRADE002

# With specific date
python pipeline.py --source api --api-config api_config.json --date 2024-01-15

# With custom data directory
python pipeline.py --source files --data-dir /path/to/data
```

### 4. Check Results

- **Report**: `final_recon_report.xlsx`
- **Model**: `models/lightgbm_diagnoser.txt`
- **Dynamic Labels**: `config/diagnosis_labels.json`
- **Console Output**: Summary statistics

## 🎯 Dynamic Label Generation System

### Overview

The system now features a **Dynamic Label Generator** that creates diagnosis labels in real-time based on:

1. **Business Rules**: Configurable rules from analyzer agents
2. **Data Patterns**: Discovered patterns and anomalies
3. **Domain Knowledge**: Industry standards and best practices
4. **Historical Analysis**: Root cause patterns from previous analyses

### Configuration

#### **Business Rules Configuration**

Create or modify business rules in your code:

```python
from crew.agents.dynamic_label_generator import DynamicLabelGenerator

# Initialize the dynamic label generator
label_generator = DynamicLabelGenerator()

# Business rules are automatically loaded, but you can customize them:
business_rules = {
    "pv_rules": [
        {
            "condition": "PV_old is None",
            "label": "New trade – no prior valuation",
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
```

#### **Pattern Discovery Configuration**

The system automatically discovers patterns, but you can configure the discovery process:

```python
# Pattern discovery is automatic, but you can influence it:
patterns = label_generator.discover_patterns(df)

# View discovered patterns
print("Discovered PV patterns:", patterns.get('pv_patterns', []))
print("Discovered Delta patterns:", patterns.get('delta_patterns', []))
print("Discovered temporal patterns:", patterns.get('temporal_patterns', []))
print("Discovered product patterns:", patterns.get('product_patterns', []))
```

#### **Domain Knowledge Categories**

The system includes comprehensive domain knowledge categories:

- **Trade Lifecycle**: New trades, dropped trades, amendments
- **Curve/Model**: LIBOR transition, model updates, curve changes
- **Funding/CSA**: Clearing changes, collateral updates, margin requirements
- **Volatility**: Option sensitivity, delta impacts, model shifts
- **Data Quality**: Missing data, validation issues, format problems
- **Market Events**: Market disruptions, regulatory changes

### Usage Examples

#### **Basic Dynamic Label Generation**

```python
from crew.agents.dynamic_label_generator import DynamicLabelGenerator
import pandas as pd

# Initialize the generator
label_generator = DynamicLabelGenerator()

# Generate labels for your data
df = pd.read_excel("data/merged_data.xlsx")
labels = label_generator.generate_labels(df, include_discovered=True, include_historical=True)

print("Generated labels:", labels)
```

#### **Custom Business Rules**

```python
from crew.agents.analyzer_agent import AnalyzerAgent
from crew.agents.dynamic_label_generator import DynamicLabelGenerator

# Initialize with custom label generator
label_generator = DynamicLabelGenerator()
analyzer = AnalyzerAgent(label_generator=label_generator)

# Add custom business rule
analyzer.add_business_rule(
    rule_type="pv_rules",
    condition="ProductType == 'Swap' and PV_Diff > 10000",
    label="Large swap PV difference - model methodology change",
    priority=3,
    category="model_change"
)

# Apply analysis
df = analyzer.apply(df)
```

#### **Pattern Discovery and Learning**

```python
# The system automatically discovers patterns
patterns = label_generator.discover_patterns(df)

# View pattern statistics
stats = label_generator.get_label_statistics()
print("Label frequency:", stats['label_frequency'])
print("Pattern frequency:", stats['pattern_frequency'])

# Get label categories
categories = label_generator.get_label_categories()
for category, labels in categories.items():
    print(f"{category}: {labels}")
```

#### **Historical Learning**

```python
# The system learns from analysis results
analyzer_output = {
    'pv_diagnoses': ['New trade – no prior valuation', 'Legacy LIBOR curve'],
    'delta_diagnoses': ['Vol sensitivity likely', 'Within tolerance']
}

# Update the label generator with analysis results
label_generator.update_from_analysis(df, analyzer_output)

# Save patterns for future use
label_generator._save_patterns()
```

### Integration with ML Model

The ML model now uses dynamically generated labels:

```python
from crew.agents.ml_tool import MLDiagnoserAgent

# Initialize ML agent (automatically uses dynamic labels)
ml_agent = MLDiagnoserAgent()

# Train with dynamic labels
training_result = ml_agent.train(df, label_col='PV_Diagnosis')

# Make predictions with dynamic labels
predictions = ml_agent.predict(df, label_col='PV_Diagnosis')

# Get model information including dynamic label integration
model_info = ml_agent.get_model_info()
print("Dynamic labels used:", model_info['dynamic_labels'])
```

## Detailed Usage

### Input Data Requirements

#### old_pricing.xlsx
Required columns:
- `TradeID` (String): Unique trade identifier
- `PV_old` (Float): Present value from old model
- `Delta_old` (Float): Delta risk from old model

Example:
```
TradeID  PV_old   Delta_old
T001     104500   0.42
T002     -98000   -0.98
T003     50500    0.00
```

#### new_pricing.xlsx
Required columns:
- `TradeID` (String): Unique trade identifier
- `PV_new` (Float): Present value from new model
- `Delta_new` (Float): Delta risk from new model

Example:
```
TradeID  PV_new   Delta_new
T001     104200   0.41
T002     -97500   -0.97
T003     51000    0.01
```

#### trade_metadata.xlsx
Required columns:
- `TradeID` (String): Unique trade identifier
- `ProductType` (String): Type of financial product
- `FundingCurve` (String): Funding curve used
- `CSA_Type` (String): Credit Support Annex type
- `ModelVersion` (String): Model version identifier

Example:
```
TradeID  ProductType  FundingCurve  CSA_Type    ModelVersion
T001     Swap         USD-LIBOR     Cleared     v2024.2
T002     Option       USD-SOFR      Bilateral   v2024.3
T003     Bond         EUR-EURIBOR   Cleared     v2024.1
```

#### funding_model_reference.xlsx
Required columns:
- `FundingCurve` (String): Funding curve identifier
- `ModelVersion` (String): Model version
- `CurveDate` (Date): Curve date
- `Rate` (Float): Reference rate

Example:
```
FundingCurve  ModelVersion  CurveDate    Rate
USD-LIBOR     v2024.2      2024-01-15   5.25
USD-SOFR      v2024.3      2024-01-15   5.30
EUR-EURIBOR   v2024.1      2024-01-15   4.50
```

### Output Data Structure

The system generates a comprehensive Excel report with the following columns:

#### **Original Data**
- `TradeID`: Unique trade identifier
- `PV_old`, `PV_new`: Present values (old/new)
- `Delta_old`, `Delta_new`: Delta risk (old/new)
- `ProductType`, `FundingCurve`, `CSA_Type`, `ModelVersion`: Trade metadata

#### **Calculated Fields**
- `PV_Diff`: Difference between old and new PV
- `Delta_Diff`: Difference between old and new Delta
- `PV_Mismatch`: Boolean flag for PV mismatches
- `Delta_Mismatch`: Boolean flag for Delta mismatches
- `Any_Mismatch`: Boolean flag for any mismatch

#### **Dynamic Diagnosis Labels**
- `PV_Diagnosis`: **Dynamically generated** PV diagnosis labels
- `Delta_Diagnosis`: **Dynamically generated** Delta diagnosis labels
- `ML_PV_Diagnosis`: ML predictions for PV diagnoses
- `ML_Delta_Diagnosis`: ML predictions for Delta diagnoses

### Example Output

```
TradeID  PV_old   PV_new   PV_Diff  PV_Mismatch  PV_Diagnosis                    ML_PV_Diagnosis
T001     104500   104200   -300     False        Within tolerance                 Within tolerance
T002     -98000   -97500   500      False        Within tolerance                 Within tolerance
T003     50500    51000    500      False        Within tolerance                 Within tolerance
T004     None     100000   None     True         New trade – no prior valuation  New trade – no prior valuation
T005     200000   180000   -20000   True         Legacy LIBOR curve with         Legacy LIBOR curve with
                                                  outdated model – PV likely      outdated model – PV likely
                                                  shifted                         shifted
```

## 🚀 Advanced Features

### **Dynamic Threshold Configuration**

Configure mismatch detection thresholds:

```python
from crew.agents.recon_agent import ReconAgent

# Create recon agent with custom thresholds
recon_agent = ReconAgent(
    pv_tolerance=1000,      # PV mismatch threshold
    delta_tolerance=0.05     # Delta mismatch threshold
)
```

### **Business Rule Management**

Add, modify, and manage business rules dynamically:

```python
from crew.agents.analyzer_agent import AnalyzerAgent

analyzer = AnalyzerAgent()

# Add new business rule
analyzer.add_business_rule(
    rule_type="pv_rules",
    condition="ProductType == 'CDS' and PV_Diff > 50000",
    label="Large CDS PV difference - credit event impact",
    priority=3,
    category="credit_event"
)

# Get current business rules
rules = analyzer.get_business_rules()
print("Current PV rules:", rules['pv_rules'])

# Get analysis statistics
stats = analyzer.get_analysis_statistics(df)
print("PV diagnosis distribution:", stats['pv_diagnosis_stats'])
```

### **Pattern Discovery and Learning**

Monitor and analyze pattern discovery:

```python
from crew.agents.dynamic_label_generator import DynamicLabelGenerator

label_generator = DynamicLabelGenerator()

# Discover patterns in your data
patterns = label_generator.discover_patterns(df)

# Get pattern statistics
stats = label_generator.get_label_statistics()
print("Pattern discovery results:", stats)

# Get label categories
categories = label_generator.get_label_categories()
for category, labels in categories.items():
    print(f"{category}: {len(labels)} labels")
```

### **ML Model Integration**

Work with the ML model that uses dynamic labels:

```python
from crew.agents.ml_tool import MLDiagnoserAgent

ml_agent = MLDiagnoserAgent()

# Train the model with dynamic labels
training_result = ml_agent.train(df, label_col='PV_Diagnosis')
print("Training accuracy:", training_result['accuracy'])

# Make predictions
predictions = ml_agent.predict(df, label_col='PV_Diagnosis')

# Get model information
model_info = ml_agent.get_model_info()
print("Model features:", model_info['feature_names'])
print("Dynamic labels used:", model_info['dynamic_labels'])

# Get feature importance
importance = ml_agent.get_feature_importance()
print("Feature importance:", importance)
```

### **Configuration Management**

Manage system configuration:

```python
# Business rules configuration
business_rules_config = {
    "pv_rules": [
        {
            "condition": "PV_old is None",
            "label": "New trade – no prior valuation",
            "priority": 1,
            "category": "trade_lifecycle"
        }
    ],
    "delta_rules": [
        {
            "condition": "ProductType == 'Option' and Delta_Mismatch == True",
            "label": "Vol sensitivity likely – delta impact",
            "priority": 2,
            "category": "volatility"
        }
    ]
}

# Pattern discovery configuration
pattern_config = {
    "pv_threshold": 0.1,
    "delta_threshold": 0.05,
    "temporal_window": 30,
    "product_specific": True,
    "historical_weight": 0.3
}
```

## 📊 Performance Optimization

### **Large Dataset Processing**

For large datasets, consider these optimizations:

```python
# Process data in chunks
chunk_size = 10000
for chunk in pd.read_excel("large_file.xlsx", chunksize=chunk_size):
    # Process each chunk
    result = analyzer.apply(chunk)
    # Save results incrementally
```

### **Memory Management**

```python
# Clear memory after processing
import gc

# After processing large datasets
gc.collect()

# Use efficient data types
df = df.astype({
    'PV_old': 'float32',
    'PV_new': 'float32',
    'Delta_old': 'float32',
    'Delta_new': 'float32'
})
```

### **Parallel Processing**

```python
# For multiple files, process in parallel
from concurrent.futures import ThreadPoolExecutor

def process_file(filename):
    # Process individual file
    pass

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_file, file_list))
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Dynamic Label Generation Issues**

```python
# Check if label generator is working
label_generator = DynamicLabelGenerator()
labels = label_generator.generate_labels(df)
print("Generated labels:", labels)

# Check business rules
rules = label_generator.business_rules
print("Business rules:", rules)
```

#### **ML Model Issues**

```python
# Validate data before training
validation_result = ml_agent.validate_data(df)
print("Validation results:", validation_result)

# Check model info
model_info = ml_agent.get_model_info()
print("Model status:", model_info)
```

#### **Business Rule Issues**

```python
# Test business rule evaluation
analyzer = AnalyzerAgent()
test_row = df.iloc[0]
diagnosis = analyzer.pv_analyzer.analyze(test_row)
print("Test diagnosis:", diagnosis)
```

### **Debug Mode**

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
python pipeline.py --debug
```

### **Performance Monitoring**

```python
import time

start_time = time.time()
# Run your analysis
end_time = time.time()
print(f"Processing time: {end_time - start_time:.2f} seconds")
```

## 📈 Best Practices

### **Data Quality**

1. **Validate Input Data**: Ensure all required columns are present
2. **Handle Missing Values**: Use appropriate strategies for missing data
3. **Check Data Types**: Ensure numerical columns are properly typed
4. **Validate Business Rules**: Test business rules with sample data

### **Dynamic Label Generation**

1. **Start with Default Rules**: Use built-in business rules initially
2. **Add Custom Rules Gradually**: Add custom rules based on domain knowledge
3. **Monitor Pattern Discovery**: Review discovered patterns regularly
4. **Validate Labels**: Ensure generated labels make business sense

### **ML Model Management**

1. **Regular Retraining**: Retrain models with new data
2. **Monitor Performance**: Track model accuracy and performance
3. **Feature Engineering**: Add relevant features based on domain knowledge
4. **Model Versioning**: Keep track of model versions and performance

### **System Configuration**

1. **Threshold Tuning**: Adjust thresholds based on business requirements
2. **Rule Priority**: Set appropriate priorities for business rules
3. **Pattern Discovery**: Configure pattern discovery parameters
4. **Historical Learning**: Monitor and adjust historical learning parameters

## 🚀 Future Enhancements

### **Planned Features**

1. **Advanced Pattern Recognition**: ML-based pattern discovery
2. **Real-time Streaming**: Live data processing capabilities
3. **Advanced Analytics**: Statistical analysis and trend detection
4. **Integration APIs**: REST APIs for external system integration

### **Performance Improvements**

1. **Parallel Processing**: Multi-threading for large datasets
2. **Database Integration**: Move from Excel to database storage
3. **Caching**: Implement intelligent caching for repeated operations
4. **Optimization**: Algorithm optimization for better performance 