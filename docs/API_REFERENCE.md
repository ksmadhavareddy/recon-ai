# 🔧 API Reference

## Overview

This document provides detailed API reference for all agents and components in the AI-Powered Reconciliation System.

## Core Components

### ReconciliationCrew

The main orchestrator class that coordinates all agents.

#### Constructor
```python
ReconciliationCrew(data_dir="data/")
```

**Parameters:**
- `data_dir` (str): Directory containing input Excel files

#### Methods

##### run()
Executes the complete reconciliation workflow.

**Returns:**
- `pandas.DataFrame`: Complete reconciliation results

**Example:**
```python
crew = ReconciliationCrew(data_dir="data")
df = crew.run()
```

## Agent Reference

### DataLoaderAgent

Handles data ingestion and merging from multiple Excel files.

#### Constructor
```python
DataLoaderAgent(data_dir="data/")
```

**Parameters:**
- `data_dir` (str): Directory containing input files

#### Methods

##### load_all_data()
Loads and merges all input Excel files.

**Returns:**
- `pandas.DataFrame`: Merged dataset with all trade information

**Process:**
1. Loads `old_pricing.xlsx`
2. Loads `new_pricing.xlsx`
3. Loads `trade_metadata.xlsx`
4. Loads `funding_model_reference.xlsx`
5. Merges all data on `TradeID` column

**Example:**
```python
loader = DataLoaderAgent("data/")
df = loader.load_all_data()
```

### ReconAgent

Identifies PV and Delta mismatches using configurable thresholds.

#### Constructor
```python
ReconAgent(pv_tolerance=1000, delta_tolerance=0.05)
```

**Parameters:**
- `pv_tolerance` (float): Threshold for PV mismatch detection
- `delta_tolerance` (float): Threshold for Delta mismatch detection

#### Methods

##### add_diff_flags(df)
Adds mismatch flags to the DataFrame.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame with PV and Delta columns

**Returns:**
- `pandas.DataFrame`: DataFrame with added mismatch flags

**Added Columns:**
- `PV_Diff`: Difference between PV_new and PV_old
- `Delta_Diff`: Difference between Delta_new and Delta_old
- `PV_Mismatch`: Boolean flag for PV mismatches
- `Delta_Mismatch`: Boolean flag for Delta mismatches
- `Any_Mismatch`: Boolean flag for any mismatch

**Example:**
```python
recon = ReconAgent(pv_tolerance=500, delta_tolerance=0.01)
df = recon.add_diff_flags(df)
```

### AnalyzerAgent

Provides rule-based root cause analysis for mismatches.

#### Constructor
```python
AnalyzerAgent()
```

#### Methods

##### rule_based_diagnosis(row)
Applies business rules to diagnose root causes.

**Parameters:**
- `row` (pandas.Series): Single row of data

**Returns:**
- `str`: Diagnosis string

**Business Rules:**
1. **New trade**: `PV_old` is None → "New trade – no prior valuation"
2. **Dropped trade**: `PV_new` is None → "Trade dropped from new model"
3. **Legacy LIBOR**: `FundingCurve == "USD-LIBOR"` and `ModelVersion != "v2024.3"` → "Legacy LIBOR curve with outdated model – PV likely shifted"
4. **CSA change**: `CSA_Type == "Cleared_CSA"` and `PV_Mismatch` → "CSA changed post-clearing – funding basis moved"
5. **Vol sensitivity**: `ProductType == "Option"` and `Delta_Mismatch` → "Vol sensitivity likely – delta impact due to model curve shift"
6. **Default**: → "Within tolerance"

**Example:**
```python
analyzer = AnalyzerAgent()
diagnosis = analyzer.rule_based_diagnosis(row)
```

##### apply(df)
Applies rule-based diagnosis to entire DataFrame.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame

**Returns:**
- `pandas.DataFrame`: DataFrame with added `Diagnosis` column

**Example:**
```python
analyzer = AnalyzerAgent()
df = analyzer.apply(df)
```

### MLDiagnoserAgent

Provides machine learning-based diagnosis predictions using CatBoost.

#### Constructor
```python
MLDiagnoserAgent(model_path="models/catboost_diagnoser.pkl")
```

**Parameters:**
- `model_path` (str): Path to save/load the trained model

#### Methods

##### prepare_features_and_labels(df)
Prepares features and labels for ML training/prediction.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame

**Returns:**
- `tuple`: (X, y) where X is feature matrix and y is encoded labels

**Features Used:**
- Numerical: `PV_old`, `PV_new`, `Delta_old`, `Delta_new`
- Categorical: `ProductType`, `FundingCurve`, `CSA_Type`, `ModelVersion`

**Example:**
```python
ml_agent = MLDiagnoserAgent()
X, y = ml_agent.prepare_features_and_labels(df)
```

##### train(df)
Trains the CatBoost model using rule-based diagnoses as labels.

**Parameters:**
- `df` (pandas.DataFrame): Training data with `Diagnosis` column

**Process:**
1. Prepares features and labels
2. Initializes CatBoostClassifier
3. Specifies categorical features
4. Fits the model
5. Saves model and label encoder

**Example:**
```python
ml_agent = MLDiagnoserAgent()
ml_agent.train(df)
```

##### predict(df)
Generates ML-based diagnoses for input data.

**Parameters:**
- `df` (pandas.DataFrame): Input DataFrame

**Returns:**
- `numpy.ndarray`: Array of predicted diagnosis strings

**Process:**
1. Prepares features (same as training)
2. Loads trained model if not already loaded
3. Generates predictions
4. Decodes labels back to strings

**Example:**
```python
ml_agent = MLDiagnoserAgent()
predictions = ml_agent.predict(df)
```

##### save_model()
Saves the trained model and label encoder.

**Saved Components:**
- Trained CatBoost model
- LabelEncoder for target variable

**Example:**
```python
ml_agent = MLDiagnoserAgent()
ml_agent.train(df)
ml_agent.save_model()
```

##### load_model()
Loads a previously trained model and label encoder.

**Example:**
```python
ml_agent = MLDiagnoserAgent()
ml_agent.load_model()  # Loads existing model
```

### NarratorAgent

Generates reports and summaries of reconciliation results.

#### Constructor
```python
NarratorAgent()
```

#### Methods

##### summarize_report(df)
Generates summary statistics for the reconciliation results.

**Parameters:**
- `df` (pandas.DataFrame): Complete reconciliation DataFrame

**Returns:**
- `dict`: Summary statistics

**Summary Metrics:**
- `Total Trades`: Number of trades processed
- `PV Mismatches`: Number of PV mismatches
- `Delta Mismatches`: Number of Delta mismatches
- `Flagged Trades`: Total trades with any mismatch

**Example:**
```python
narrator = NarratorAgent()
summary = narrator.summarize_report(df)
```

##### save_report(df, output_path="final_recon_report.xlsx")
Saves the complete reconciliation results to Excel.

**Parameters:**
- `df` (pandas.DataFrame): Complete reconciliation DataFrame
- `output_path` (str): Path for output Excel file

**Output Columns:**
- `TradeID`: Unique trade identifier
- `PV_old`, `PV_new`, `PV_Diff`: Present value data
- `Delta_old`, `Delta_new`, `Delta_Diff`: Delta risk data
- `ProductType`, `FundingCurve`, `CSA_Type`, `ModelVersion`: Trade characteristics
- `PV_Mismatch`, `Delta_Mismatch`: Mismatch flags
- `Diagnosis`: Rule-based diagnosis
- `ML_Diagnosis`: ML-based diagnosis

**Example:**
```python
narrator = NarratorAgent()
narrator.save_report(df, "my_report.xlsx")
```

## Data Structures

### Input Data Schema

#### old_pricing.xlsx
| Column | Type | Description | Required |
|--------|------|-------------|----------|
| TradeID | String | Unique trade identifier | Yes |
| PV_old | Float | Present value (old model) | Yes |
| Delta_old | Float | Delta risk (old model) | Yes |

#### new_pricing.xlsx
| Column | Type | Description | Required |
|--------|------|-------------|----------|
| TradeID | String | Unique trade identifier | Yes |
| PV_new | Float | Present value (new model) | Yes |
| Delta_new | Float | Delta risk (new model) | Yes |

#### trade_metadata.xlsx
| Column | Type | Description | Required |
|--------|------|-------------|----------|
| TradeID | String | Unique trade identifier | Yes |
| ProductType | String | Financial product type | Yes |
| FundingCurve | String | Funding curve identifier | Yes |
| CSA_Type | String | Credit Support Annex type | Yes |
| ModelVersion | String | Model version identifier | Yes |

#### funding_model_reference.xlsx
| Column | Type | Description | Required |
|--------|------|-------------|----------|
| TradeID | String | Unique trade identifier | Yes |
| Additional fields | Various | Funding-related parameters | No |

### Output Data Schema

#### final_recon_report.xlsx
| Column | Type | Description |
|--------|------|-------------|
| TradeID | String | Unique trade identifier |
| PV_old, PV_new | Float | Present values |
| PV_Diff | Float | PV difference |
| Delta_old, Delta_new | Float | Delta risk measures |
| Delta_Diff | Float | Delta difference |
| ProductType | String | Financial product type |
| FundingCurve | String | Funding curve identifier |
| CSA_Type | String | Credit Support Annex type |
| ModelVersion | String | Model version identifier |
| PV_Mismatch | Boolean | PV mismatch flag |
| Delta_Mismatch | Boolean | Delta mismatch flag |
| Diagnosis | String | Rule-based diagnosis |
| ML_Diagnosis | String | ML-based diagnosis |

## Configuration Options

### ReconAgent Configuration

```python
# Adjust mismatch thresholds
recon_agent = ReconAgent(
    pv_tolerance=1000,      # PV mismatch threshold
    delta_tolerance=0.05     # Delta mismatch threshold
)
```

### MLDiagnoserAgent Configuration

```python
# Change model path
ml_agent = MLDiagnoserAgent(
    model_path="custom/path/model.pkl"
)
```

### NarratorAgent Configuration

```python
# Custom report path
narrator.save_report(df, "custom/report.xlsx")
```

## Error Handling

### Common Exceptions

#### FileNotFoundError
**Cause**: Missing input files
**Solution**: Ensure all required files are in the data directory

```python
# Check if files exist
import os
if not os.path.exists("data/old_pricing.xlsx"):
    raise FileNotFoundError("Missing old_pricing.xlsx")
```

#### ValueError
**Cause**: Invalid data types or missing required columns
**Solution**: Validate input data structure

```python
# Validate required columns
required_cols = ['TradeID', 'PV_old', 'Delta_old']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    raise ValueError(f"Missing columns: {missing_cols}")
```

#### MemoryError
**Cause**: Insufficient memory for large datasets
**Solution**: Process data in chunks or increase system memory

```python
# Process in chunks
chunk_size = 1000
for chunk in pd.read_excel(file, chunksize=chunk_size):
    process_chunk(chunk)
```

## Performance Considerations

### Memory Usage
- **Peak Memory**: ~2x data size for merged DataFrame
- **Model Size**: ~1MB for CatBoost model
- **Optimization**: Process large datasets in chunks

### Processing Speed
- **Data Loading**: ~1000 trades/second
- **Mismatch Detection**: ~5000 trades/second
- **ML Training**: ~1-5 seconds for typical datasets
- **ML Prediction**: ~10000 trades/second

### Scalability
- **Linear Scaling**: Performance scales linearly with data size
- **Parallel Processing**: Can be extended for multi-threading
- **Batch Processing**: Suitable for large datasets

## Best Practices

### Data Validation
```python
def validate_data(df):
    # Check required columns
    required_cols = ['TradeID', 'PV_old', 'PV_new']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    
    # Check data types
    if not df['TradeID'].dtype == 'object':
        raise ValueError("TradeID must be string type")
    
    # Check for missing values
    if df[['PV_old', 'PV_new']].isnull().any().any():
        print("Warning: Missing values detected")
```

### Model Management
```python
def manage_model(ml_agent, df, retrain=False):
    if retrain or ml_agent.model is None:
        print("Training new model...")
        ml_agent.train(df)
    else:
        print("Using existing model...")
        ml_agent.load_model()
    
    return ml_agent.predict(df)
```

### Error Recovery
```python
def safe_pipeline(data_dir):
    try:
        crew = ReconciliationCrew(data_dir)
        df = crew.run()
        return df
    except FileNotFoundError as e:
        print(f"Data file error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Integration Examples

### Custom Pipeline
```python
from crew.crew_builder import ReconciliationCrew
from crew.agents.ml_tool import MLDiagnoserAgent

# Custom pipeline with ML focus
def custom_ml_pipeline(data_dir):
    # Load and process data
    crew = ReconciliationCrew(data_dir)
    df = crew.data_loader.load_all_data()
    df = crew.recon_agent.add_diff_flags(df)
    df = crew.analyzer_agent.apply(df)
    
    # Focus on ML analysis
    ml_agent = MLDiagnoserAgent()
    if ml_agent.model is None:
        ml_agent.train(df)
    
    df["ML_Diagnosis"] = ml_agent.predict(df)
    
    # Compare rule-based vs ML
    comparison = df[df["Diagnosis"] != df["ML_Diagnosis"]]
    print(f"Disagreements: {len(comparison)}")
    
    return df
```

### Batch Processing
```python
import os
from crew.crew_builder import ReconciliationCrew

def batch_process(data_dirs):
    results = {}
    for data_dir in data_dirs:
        if os.path.exists(data_dir):
            try:
                crew = ReconciliationCrew(data_dir)
                df = crew.run()
                results[data_dir] = df
            except Exception as e:
                print(f"Error processing {data_dir}: {e}")
    return results
```

### Custom Reporting
```python
from crew.agents.narrator_agent import NarratorAgent

def custom_report(df, output_path):
    narrator = NarratorAgent()
    
    # Generate summary
    summary = narrator.summarize_report(df)
    
    # Custom analysis
    ml_accuracy = (df["Diagnosis"] == df["ML_Diagnosis"]).mean()
    print(f"ML vs Rule-based agreement: {ml_accuracy:.2%}")
    
    # Save report
    narrator.save_report(df, output_path)
    
    return summary
``` 