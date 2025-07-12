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

Place your input files in the `data/` directory:

```
data/
├── old_pricing.xlsx      # Previous pricing data
├── new_pricing.xlsx      # Current pricing data
├── trade_metadata.xlsx   # Trade characteristics
└── funding_model_reference.xlsx  # Funding information
```

### 3. Run the Pipeline

```bash
python pipeline.py
```

### 4. Check Results

- **Report**: `final_recon_report.xlsx`
- **Model**: `models/catboost_diagnoser.pkl`
- **Console Output**: Summary statistics

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
T001     105200   0.43
T002     -97500   -0.97
T003     50800    0.01
```

#### trade_metadata.xlsx
Required columns:
- `TradeID` (String): Unique trade identifier
- `ProductType` (String): Financial product type
- `FundingCurve` (String): Funding curve identifier
- `CSA_Type` (String): Credit Support Annex type
- `ModelVersion` (String): Model version identifier

Example:
```
TradeID  ProductType  FundingCurve  CSA_Type      ModelVersion
T001     Swap         USD-LIBOR     Cleared_CSA   v2024.3
T002     Option       SOFR          Bilateral     v2024.2
T003     Swap         EUR-EURIBOR   Cleared_CSA   v2024.3
```

#### funding_model_reference.xlsx
Required columns:
- `TradeID` (String): Unique trade identifier
- Additional funding-related fields (various types)

Example:
```
TradeID  FundingRate  CollateralType  MarginType
T001     0.025        Cash            Initial
T002     0.030        Securities      Variation
T003     0.020        Cash            Initial
```

### Configuration

#### Threshold Configuration

Edit `crew/agents/recon_agent.py` to adjust mismatch thresholds:

```python
class ReconAgent:
    def __init__(self, pv_tolerance=1000, delta_tolerance=0.05):
        self.pv_tolerance = pv_tolerance  # Adjust PV threshold
        self.delta_tolerance = delta_tolerance  # Adjust Delta threshold
```

#### ML Model Configuration

Edit `crew/agents/ml_tool.py` to adjust ML settings:

```python
class MLDiagnoserAgent:
    def __init__(self, model_path="models/catboost_diagnoser.pkl"):
        self.model_path = model_path  # Change model location
```

### Advanced Usage

#### Custom Business Rules

Edit `crew/agents/analyzer_agent.py` to add custom business rules:

```python
def rule_based_diagnosis(self, row):
    # Add your custom rules here
    if row.get("YourCondition"):
        return "Your custom diagnosis"
    # ... existing rules
    return "Within tolerance"
```

#### Custom ML Features

Edit `crew/agents/ml_tool.py` to add custom features:

```python
def prepare_features_and_labels(self, df):
    feature_cols = [
        'PV_old', 'PV_new', 'Delta_old', 'Delta_new',
        'ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion',
        'YourCustomFeature'  # Add your custom features
    ]
    # ... rest of the method
```

#### Custom Report Format

Edit `crew/agents/narrator_agent.py` to customize report output:

```python
def save_report(self, df, output_path="final_recon_report.xlsx"):
    cols = [
        "TradeID", "PV_old", "PV_new", "PV_Diff",
        "Delta_old", "Delta_new", "Delta_Diff",
        "ProductType", "FundingCurve", "CSA_Type", "ModelVersion",
        "PV_Mismatch", "Delta_Mismatch", "Diagnosis", "ML_Diagnosis",
        "YourCustomColumn"  # Add your custom columns
    ]
    df.to_excel(output_path, index=False, columns=cols)
```

## Output Interpretation

### Excel Report Analysis

The `final_recon_report.xlsx` contains:

#### Mismatch Analysis
- **PV_Mismatch**: True if |PV_new - PV_old| > threshold
- **Delta_Mismatch**: True if |Delta_new - Delta_old| > threshold
- **Any_Mismatch**: True if either PV or Delta mismatch

#### Diagnosis Comparison
- **Diagnosis**: Rule-based business logic diagnosis
- **ML_Diagnosis**: Machine learning prediction

#### Key Metrics to Monitor
- **Total Trades**: Number of trades processed
- **PV Mismatches**: Number of PV mismatches
- **Delta Mismatches**: Number of Delta mismatches
- **Flagged Trades**: Total trades with any mismatch

### Understanding Diagnoses

#### Rule-based Diagnoses
- **"New trade – no prior valuation"**: Trade exists only in new data
- **"Trade dropped from new model"**: Trade exists only in old data
- **"Legacy LIBOR curve with outdated model"**: LIBOR curve with old model version
- **"CSA changed post-clearing"**: CSA type changed affecting funding
- **"Vol sensitivity likely"**: Option with Delta mismatch
- **"Within tolerance"**: No significant issues detected

#### ML Diagnoses
The ML model learns patterns from rule-based diagnoses and may identify:
- Complex interactions between features
- Non-obvious patterns in the data
- Edge cases not covered by business rules

### Performance Metrics

#### Model Performance
- **Training Time**: Time to train the ML model
- **Prediction Time**: Time to generate ML predictions
- **Model Accuracy**: How well ML predictions match rule-based diagnoses

#### System Performance
- **Processing Speed**: Trades processed per second
- **Memory Usage**: Peak memory consumption
- **Output Quality**: Completeness and accuracy of results

## Troubleshooting

### Common Issues

#### 1. Missing Dependencies
```
ModuleNotFoundError: No module named 'catboost'
```
**Solution**: Install missing packages
```bash
pip install -r requirements.txt
```

#### 2. File Not Found
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/old_pricing.xlsx'
```
**Solution**: Ensure all required files are in the `data/` directory

#### 3. Data Type Errors
```
TypeError: Cannot convert 'Swap' to float
```
**Solution**: Ensure categorical features are properly handled (already fixed in current version)

#### 4. Memory Issues
```
MemoryError: Unable to allocate array
```
**Solution**: Process data in smaller chunks or increase system memory

#### 5. Model Loading Errors
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/catboost_diagnoser.pkl'
```
**Solution**: The model will be created automatically on first run

### Debug Mode

Enable debug output by modifying `pipeline.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# ... rest of the code
```

### Data Validation

Add data validation to check input files:

```python
import os

def validate_input_files(data_dir):
    required_files = [
        'old_pricing.xlsx',
        'new_pricing.xlsx', 
        'trade_metadata.xlsx',
        'funding_model_reference.xlsx'
    ]
    
    for file in required_files:
        if not os.path.exists(f"{data_dir}/{file}"):
            raise FileNotFoundError(f"Missing required file: {file}")
```

## Best Practices

### Data Preparation
1. **Clean Data**: Remove duplicates and handle missing values
2. **Consistent Format**: Ensure all files use the same TradeID format
3. **Data Validation**: Verify data types and ranges
4. **Backup**: Keep backups of original data files

### Model Management
1. **Version Control**: Track model versions and performance
2. **Regular Retraining**: Retrain models with new data
3. **Model Validation**: Validate model predictions against known cases
4. **Performance Monitoring**: Track model accuracy over time

### System Maintenance
1. **Regular Updates**: Keep dependencies updated
2. **Log Monitoring**: Monitor system logs for issues
3. **Performance Tuning**: Optimize for your specific use case
4. **Backup Strategy**: Regular backups of models and data

### Quality Assurance
1. **Data Quality**: Ensure high-quality input data
2. **Result Validation**: Verify output accuracy
3. **Cross-validation**: Compare rule-based and ML results
4. **Documentation**: Document any customizations or changes

## Examples

### Basic Example
```bash
# 1. Prepare data files
cp your_old_pricing.xlsx data/old_pricing.xlsx
cp your_new_pricing.xlsx data/new_pricing.xlsx
cp your_metadata.xlsx data/trade_metadata.xlsx
cp your_funding.xlsx data/funding_model_reference.xlsx

# 2. Run pipeline
python pipeline.py

# 3. Check results
ls -la final_recon_report.xlsx
```

### Custom Threshold Example
```python
# Modify thresholds in recon_agent.py
class ReconAgent:
    def __init__(self, pv_tolerance=500, delta_tolerance=0.01):  # Stricter thresholds
        self.pv_tolerance = pv_tolerance
        self.delta_tolerance = delta_tolerance
```

### Custom Business Rule Example
```python
# Add custom rule in analyzer_agent.py
def rule_based_diagnosis(self, row):
    if row.get("ProductType") == "Exotic" and row.get("PV_Mismatch"):
        return "Exotic product - complex valuation model change"
    # ... existing rules
```

## Support

### Getting Help
1. **Check Documentation**: Review this guide and architecture docs
2. **Review Logs**: Check console output for error messages
3. **Validate Data**: Ensure input files meet requirements
4. **Test with Sample Data**: Use provided sample data to verify setup

### Reporting Issues
When reporting issues, include:
- **Error Message**: Complete error text
- **Input Data**: Sample of problematic data (anonymized)
- **System Info**: Python version, OS, package versions
- **Steps to Reproduce**: Detailed steps to recreate the issue

### Feature Requests
For new features or enhancements:
- **Use Case**: Describe the specific use case
- **Expected Behavior**: What should the system do
- **Current Behavior**: What it currently does
- **Impact**: Why this feature is important 