# 🔧 API Reference

## Overview

This document provides detailed API reference for all agents and components in the AI-Powered Reconciliation System, including the **dynamic label generation system**.

## Core Components

### ReconciliationCrew

The main orchestrator class that coordinates all agents, now including dynamic label generation.

#### Constructor
```python
ReconciliationCrew(data_dir="data/", api_config=None, pv_tolerance=1000, delta_tolerance=0.05)
```

**Parameters:**
- `data_dir` (str): Directory containing input Excel files
- `api_config` (dict): API configuration for external data sources
- `pv_tolerance` (float): PV mismatch threshold (default: 1000)
- `delta_tolerance` (float): Delta mismatch threshold (default: 0.05)

#### Methods

##### run(source="auto", trade_ids=None, date=None)
Executes the complete reconciliation workflow with dynamic label generation.

**Parameters:**
- `source` (str): Data source ("files", "api", "auto", "hybrid")
- `trade_ids` (list): Specific trade IDs to filter (for API)
- `date` (str): Specific date to filter (for API)

**Returns:**
- `pandas.DataFrame`: Complete reconciliation results with dynamic labels

**Example:**
```python
crew = ReconciliationCrew(data_dir="data", pv_tolerance=500, delta_tolerance=0.03)
df = crew.run(source="auto")
```

## Agent Reference

### UnifiedDataLoaderAgent

Handles unified data ingestion and merging from multiple sources (files, APIs, auto-detect, hybrid) with auto-load functionality.

#### Constructor
```python
UnifiedDataLoaderAgent(data_dir="data/", api_config=None, auto_fallback=True)
```

**Parameters:**
- `data_dir` (str): Directory containing input files
- `api_config` (dict): API configuration for external data sources
- `auto_fallback` (bool): Enable automatic fallback from API to files

#### Methods

##### load_data(source="auto", trade_ids=None, date=None)
Loads and merges data from specified source.

**Parameters:**
- `source` (str): Data source ("files", "api", "auto", "hybrid")
- `trade_ids` (list): Specific trade IDs to filter (for API)
- `date` (str): Specific date to filter (for API)

**Returns:**
- `pandas.DataFrame`: Merged dataset with all trade information

**Source Options:**
- `"files"`: Load from Excel files only
- `"api"`: Load from API endpoints only
- `"auto"`: Auto-detect best available source (default)
- `"hybrid"`: Load from both sources and merge

**Process:**
1. Determines data source based on `source` parameter
2. Loads data from files and/or APIs
3. Merges all data on `TradeID` column
4. Applies filtering if trade_ids or date specified

**Auto-Load Features:**
- **One-Click Setup**: Automatically loads all 4 required files from data/ directory
- **Visual Status Indicators**: Real-time loading status with success/error indicators
- **File Validation**: Checks file existence, size, and format
- **Error Handling**: Graceful handling of missing or corrupted files
- **Ready Confirmation**: Clear indication when all files are loaded and ready

**Example:**
```python
# File-based loading
loader = UnifiedDataLoaderAgent("data/")
df = loader.load_data(source="files")

# API-based loading
loader = UnifiedDataLoaderAgent(api_config=api_config)
df = loader.load_data(source="api", trade_ids=["TRADE001", "TRADE002"])

# Auto-detect (default)
loader = UnifiedDataLoaderAgent("data/", api_config=api_config)
df = loader.load_data()  # Uses auto-detect

# Auto-load functionality (Streamlit dashboard)
# The dashboard automatically loads all 4 files from data/ directory
# with visual status indicators and ready confirmation
```

### ReconAgent

Detects PV and Delta mismatches using configurable thresholds.

#### Constructor
```python
ReconAgent(pv_tolerance=1000, delta_tolerance=0.05)
```

**Parameters:**
- `pv_tolerance` (float): PV mismatch threshold
- `delta_tolerance` (float): Delta mismatch threshold

#### Methods

##### apply(df)
Applies mismatch detection to the input DataFrame.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame with PV and Delta columns

**Returns:**
- `pandas.DataFrame`: DataFrame with mismatch flags added

**Added Columns:**
- `PV_Diff`: Difference between PV_old and PV_new
- `Delta_Diff`: Difference between Delta_old and Delta_new
- `PV_Mismatch`: Boolean flag for PV mismatches
- `Delta_Mismatch`: Boolean flag for Delta mismatches
- `Any_Mismatch`: Boolean flag for any mismatch

**Example:**
```python
recon_agent = ReconAgent(pv_tolerance=500, delta_tolerance=0.03)
df_with_flags = recon_agent.apply(df)
```

### AnalyzerAgent (Enhanced)

Provides **dynamic rule-based diagnosis** using configurable business rules.

#### Constructor
```python
AnalyzerAgent(label_generator=None)
```

**Parameters:**
- `label_generator` (DynamicLabelGenerator): Optional custom label generator

#### Methods

##### apply(df)
Applies dynamic rule-based analysis to the input DataFrame.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame with mismatch flags

**Returns:**
- `pandas.DataFrame`: DataFrame with dynamic diagnoses added

**Added Columns:**
- `PV_Diagnosis`: **Dynamically generated** PV diagnosis labels
- `Delta_Diagnosis`: **Dynamically generated** Delta diagnosis labels

**Process:**
1. Applies business rules dynamically
2. Evaluates conditions safely
3. Updates label generator with results
4. Generates dynamic diagnoses

**Example:**
```python
analyzer = AnalyzerAgent()
df_with_diagnoses = analyzer.apply(df)
```

##### get_business_rules()
Returns current business rules configuration.

**Returns:**
- `dict`: Current business rules for PV and Delta analysis

**Example:**
```python
rules = analyzer.get_business_rules()
print("PV rules:", rules['pv_rules'])
```

##### add_business_rule(rule_type, condition, label, priority=1, category="custom")
Adds a new business rule to the analyzer.

**Parameters:**
- `rule_type` (str): Rule type ("pv_rules" or "delta_rules")
- `condition` (str): String condition to evaluate
- `label` (str): Diagnosis label to assign
- `priority` (int): Rule priority (higher = more important)
- `category` (str): Rule category for organization

**Example:**
```python
analyzer.add_business_rule(
    rule_type="pv_rules",
    condition="ProductType == 'CDS' and PV_Diff > 50000",
    label="Large CDS PV difference - credit event impact",
    priority=3,
    category="credit_event"
)
```

##### get_analysis_statistics(df)
Returns analysis statistics and diagnosis distribution.

**Parameters:**
- `df` (pandas.DataFrame): DataFrame with diagnoses

**Returns:**
- `dict`: Analysis statistics including diagnosis distributions

**Example:**
```python
stats = analyzer.get_analysis_statistics(df)
print("PV diagnosis distribution:", stats['pv_diagnosis_stats'])
```

### DynamicLabelGenerator (New)

Generates diagnosis labels in real-time based on business rules, patterns, and domain knowledge.

#### Constructor
```python
DynamicLabelGenerator(config_path=None)
```

**Parameters:**
- `config_path` (str): Path to configuration file (default: "config/diagnosis_labels.json")

#### Methods

##### generate_labels(df, include_discovered=True, include_historical=True)
Generates dynamic diagnosis labels based on current data and patterns.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame
- `include_discovered` (bool): Include discovered patterns (default: True)
- `include_historical` (bool): Include historical patterns (default: True)

**Returns:**
- `list`: List of dynamic diagnosis labels

**Process:**
1. Applies business rules
2. Discovers patterns in data
3. Integrates domain knowledge
4. Incorporates historical learning

**Example:**
```python
label_generator = DynamicLabelGenerator()
labels = label_generator.generate_labels(df)
print("Generated labels:", labels)
```

##### discover_patterns(df)
Discovers patterns in the input DataFrame.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame

**Returns:**
- `dict`: Dictionary containing discovered patterns

**Pattern Types:**
- `pv_patterns`: PV-related patterns
- `delta_patterns`: Delta-related patterns
- `temporal_patterns`: Time-based patterns
- `product_patterns`: Product-specific patterns

**Example:**
```python
patterns = label_generator.discover_patterns(df)
print("PV patterns:", patterns.get('pv_patterns', []))
```

##### update_from_analysis(df, analyzer_output)
Updates the label generator with analysis results.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame
- `analyzer_output` (dict): Analysis results from analyzer agent

**Process:**
1. Extracts unique diagnoses from analysis
2. Updates historical patterns
3. Saves patterns to configuration file

**Example:**
```python
analyzer_output = {
    'pv_diagnoses': ['New trade – no prior valuation', 'Legacy LIBOR curve'],
    'delta_diagnoses': ['Vol sensitivity likely', 'Within tolerance']
}
label_generator.update_from_analysis(df, analyzer_output)
```

##### get_label_categories()
Returns labels organized by their categories.

**Returns:**
- `dict`: Labels organized by category

**Categories:**
- `trade_lifecycle`: Trade lifecycle-related labels
- `curve_model`: Curve and model-related labels
- `funding_csa`: Funding and CSA-related labels
- `volatility`: Volatility-related labels
- `data_quality`: Data quality-related labels
- `market_events`: Market event-related labels

**Example:**
```python
categories = label_generator.get_label_categories()
for category, labels in categories.items():
    print(f"{category}: {labels}")
```

##### get_label_statistics()
Returns statistics about label usage and patterns.

**Returns:**
- `dict`: Label and pattern statistics

**Statistics:**
- `label_frequency`: Frequency of each label
- `pattern_frequency`: Frequency of each pattern
- `historical_patterns`: Historical pattern data
- `last_update`: Last update timestamp

**Example:**
```python
stats = label_generator.get_label_statistics()
print("Label frequency:", stats['label_frequency'])
```

### MLDiagnoserAgent (Enhanced)

ML-powered diagnosis predictions using **dynamically generated labels**.

#### Constructor
```python
MLDiagnoserAgent(model_path="models/lightgbm_diagnoser.txt")
```

**Parameters:**
- `model_path` (str): Path to saved model file

#### Methods

##### prepare_features_and_labels(df, label_col='PV_Diagnosis')
Prepares features and labels for ML training/prediction with dynamic labels.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame
- `label_col` (str): Column name containing diagnosis labels

**Returns:**
- `tuple`: (features, encoded_labels)

**Features:**
- `PV_old`, `PV_new`: Present values
- `Delta_old`, `Delta_new`: Delta risk measures
- `ProductType`, `FundingCurve`, `CSA_Type`, `ModelVersion`: Categorical features

**Process:**
1. Validates required features
2. Handles categorical features
3. Generates dynamic labels
4. Encodes labels for ML

**Example:**
```python
ml_agent = MLDiagnoserAgent()
X, y = ml_agent.prepare_features_and_labels(df, label_col='PV_Diagnosis')
```

##### train(df, label_col='PV_Diagnosis', validation_df=None, **kwargs)
Trains the LightGBM model using dynamically generated labels.

**Parameters:**
- `df` (pandas.DataFrame): Training DataFrame
- `label_col` (str): Column name containing diagnosis labels
- `validation_df` (pandas.DataFrame): Optional validation DataFrame
- `**kwargs`: Additional LightGBM parameters

**Returns:**
- `dict`: Training metrics and history

**Process:**
1. Prepares features and dynamic labels
2. Trains LightGBM model
3. Updates label generator with analysis results
4. Saves model and metadata

**Example:**
```python
training_result = ml_agent.train(df, label_col='PV_Diagnosis')
print("Training accuracy:", training_result['accuracy'])
```

##### predict(df, label_col='PV_Diagnosis')
Makes predictions using the trained model with dynamic labels.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame
- `label_col` (str): Column name for predictions

**Returns:**
- `numpy.ndarray`: Predicted diagnosis labels

**Process:**
1. Loads trained model
2. Prepares features
3. Makes predictions
4. Decodes labels

**Example:**
```python
predictions = ml_agent.predict(df, label_col='PV_Diagnosis')
```

##### evaluate_model(test_df, true_labels)
Evaluates model performance.

**Parameters:**
- `test_df` (pandas.DataFrame): Test DataFrame
- `true_labels` (pandas.Series): True labels

**Returns:**
- `dict`: Evaluation metrics

**Metrics:**
- `accuracy`: Overall accuracy
- `classification_report`: Detailed classification report
- `confusion_matrix`: Confusion matrix
- `feature_importance`: Feature importance scores

**Example:**
```python
metrics = ml_agent.evaluate_model(test_df, true_labels)
print("Accuracy:", metrics['accuracy'])
```

##### get_feature_importance(importance_type='gain')
Returns feature importance scores.

**Parameters:**
- `importance_type` (str): Importance type ('gain', 'split', 'cover')

**Returns:**
- `pandas.DataFrame`: Feature importance scores

**Example:**
```python
importance = ml_agent.get_feature_importance()
print("Top features:", importance.head())
```

##### get_model_info()
Returns comprehensive model information.

**Returns:**
- `dict`: Model information including dynamic label integration

**Information:**
- `model_path`: Path to saved model
- `feature_names`: List of feature names
- `categorical_features`: List of categorical features
- `dynamic_labels`: Dynamic labels used in training
- `training_history`: Training history
- `last_training`: Last training timestamp

**Example:**
```python
model_info = ml_agent.get_model_info()
print("Dynamic labels used:", model_info['dynamic_labels'])
```

##### validate_data(df)
Validates input data quality.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame

**Returns:**
- `dict`: Validation results

**Checks:**
- Required features present
- Data types correct
- Missing values
- Value ranges

**Example:**
```python
validation = ml_agent.validate_data(df)
print("Validation results:", validation)
```

### NarratorAgent

Generates comprehensive reports and summaries.

#### Constructor
```python
NarratorAgent()
```

#### Methods

##### generate_report(df, output_path="final_recon_report.xlsx")
Generates comprehensive Excel report with dynamic labels.

**Parameters:**
- `df` (pandas.DataFrame): Complete reconciliation results
- `output_path` (str): Output file path

**Returns:**
- `str`: Path to generated report

**Report Contents:**
- Original data with all columns
- Mismatch flags and differences
- **Dynamic diagnosis labels**
- ML predictions
- Summary statistics

**Example:**
```python
narrator = NarratorAgent()
report_path = narrator.generate_report(df)
print(f"Report saved to: {report_path}")
```

## Business Rules Configuration

### PV Rules

```python
pv_rules = [
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
]
```

### Delta Rules

```python
delta_rules = [
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
```

## Domain Knowledge Categories

### Trade Lifecycle
- New trade – no prior valuation
- Trade dropped from new model
- Trade amended with new terms
- Trade matured or expired

### Curve/Model
- Legacy LIBOR curve with outdated model
- SOFR transition impact – curve basis changed
- Model version update – methodology changed
- Curve interpolation changed – end points affected

### Funding/CSA
- CSA changed post-clearing – funding basis moved
- Collateral threshold changed – funding cost shifted
- New clearing house – margin requirements different
- Bilateral to cleared transition – funding curve changed

### Volatility
- Vol sensitivity likely – delta impact due to model curve shift
- Option pricing model update – volatility surface changed
- Market volatility spike – delta hedging impact
- Volatility smile adjustment – skew changes

### Data Quality
- Missing pricing data – incomplete valuation
- Data format mismatch – parsing errors
- Validation failures – business rule violations
- Timestamp inconsistencies – temporal misalignment

### Market Events
- Market disruption – liquidity impact
- Regulatory change – compliance requirements
- Central bank action – rate environment shift
- Credit event – counterparty risk change

## Configuration Management

### Dynamic Label Configuration

```python
# Initialize with custom configuration
label_generator = DynamicLabelGenerator("config/custom_labels.json")

# Business rules are automatically loaded
business_rules = label_generator.business_rules

# Domain knowledge is automatically loaded
domain_knowledge = label_generator.domain_knowledge
```

### Pattern Discovery Configuration

```python
# Pattern discovery is automatic, but you can influence it
patterns = label_generator.discover_patterns(df)

# Configure pattern discovery parameters
pattern_config = {
    "pv_threshold": 0.1,
    "delta_threshold": 0.05,
    "temporal_window": 30,
    "product_specific": True,
    "historical_weight": 0.3
}
```

## Error Handling

### Common Errors

#### Dynamic Label Generation Errors

```python
# Check if label generator is working
try:
    labels = label_generator.generate_labels(df)
    print("Generated labels:", labels)
except Exception as e:
    print(f"Label generation error: {e}")
```

#### Business Rule Evaluation Errors

```python
# Test business rule evaluation
try:
    test_row = df.iloc[0]
    diagnosis = analyzer.pv_analyzer.analyze(test_row)
    print("Test diagnosis:", diagnosis)
except Exception as e:
    print(f"Business rule evaluation error: {e}")
```

#### ML Model Errors

```python
# Validate data before training
try:
    validation = ml_agent.validate_data(df)
    if validation['is_valid']:
        training_result = ml_agent.train(df)
    else:
        print("Data validation failed:", validation['errors'])
except Exception as e:
    print(f"ML model error: {e}")
```

## Performance Optimization

### Large Dataset Processing

```python
# Process data in chunks
chunk_size = 10000
for chunk in pd.read_excel("large_file.xlsx", chunksize=chunk_size):
    # Process each chunk
    result = analyzer.apply(chunk)
    # Save results incrementally
```

### Memory Management

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

### Parallel Processing

```python
# For multiple files, process in parallel
from concurrent.futures import ThreadPoolExecutor

def process_file(filename):
    # Process individual file
    pass

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_file, file_list))
```

## Integration Examples

### Complete Workflow

```python
from crew.crew_builder import ReconciliationCrew

# Initialize crew with dynamic label generation
crew = ReconciliationCrew(
    data_dir="data/",
    pv_tolerance=1000,
    delta_tolerance=0.05
)

# Run complete workflow
df = crew.run(source="auto")

# Access individual agents
loader = crew.data_loader
recon = crew.recon_agent
analyzer = crew.analyzer_agent
ml_agent = crew.ml_agent
narrator = crew.narrator_agent

# Generate report
report_path = narrator.generate_report(df)
```

### Custom Business Rules

```python
from crew.agents.analyzer_agent import AnalyzerAgent
from crew.agents.dynamic_label_generator import DynamicLabelGenerator

# Initialize with custom label generator
label_generator = DynamicLabelGenerator()
analyzer = AnalyzerAgent(label_generator=label_generator)

# Add custom business rule
analyzer.add_business_rule(
    rule_type="pv_rules",
    condition="ProductType == 'CDS' and PV_Diff > 50000",
    label="Large CDS PV difference - credit event impact",
    priority=3,
    category="credit_event"
)

# Apply analysis
df = analyzer.apply(df)
```

### ML Model with Dynamic Labels

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