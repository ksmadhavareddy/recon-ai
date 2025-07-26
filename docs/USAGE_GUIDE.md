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

#### **Option A: File-based Data**
Place your input files in the `data/` directory:

```
data/
├── old_pricing.xlsx      # Previous pricing data
├── new_pricing.xlsx      # Current pricing data
├── trade_metadata.xlsx   # Trade characteristics
└── funding_model_reference.xlsx  # Funding information
```

#### **Option B: API-based Data**
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

### Data Source Options

The unified data loader supports four different source modes:

#### **1. Files (`--source files`)**
- Loads data from Excel files in the data directory
- Fastest option for local development
- Requires all files to be present

#### **2. API (`--source api`)**
- Fetches data from external API endpoints
- Requires valid API configuration
- Supports filtering by trade IDs and dates

#### **3. Auto-detect (`--source auto` or default)**
- Automatically chooses the best available source
- Tries API first, falls back to files if API fails
- Most user-friendly option

#### **4. Hybrid (`--source hybrid`)**
- Loads from both file and API sources
- Merges data from multiple sources
- Provides redundancy and data validation

### Command Line Options

```bash
python pipeline.py [OPTIONS]

Options:
  --source TEXT           Data source: files, api, auto, hybrid [default: auto]
  --data-dir TEXT         Directory containing Excel files [default: data/]
  --api-config TEXT       Path to API configuration file
  --trade-ids TEXT        Specific trade IDs to filter (space-separated)
  --date TEXT            Specific date for API filtering (YYYY-MM-DD)
  --help                 Show this help message
```

### API Configuration

Create an API configuration file (e.g., `api_config.json`):

```json
{
  "base_url": "https://api.example.com",
  "api_key": "your_api_key_here",
  "timeout": 30,
  "endpoints": {
    "old_pricing": "/api/v1/pricing/old",
    "new_pricing": "/api/v1/pricing/new",
    "trade_metadata": "/api/v1/trades/metadata",
    "funding_reference": "/api/v1/funding/reference"
  }
}
```

### Web Dashboard

Launch the interactive Streamlit dashboard:

```bash
# Using the wrapper script
python run_dashboard.py

# Or directly with streamlit
streamlit run app.py
```

The dashboard provides:
- Real-time data loading and processing
- Interactive visualizations
- API connection status monitoring
- Export capabilities

### REST API Server

Start the REST API server for external integrations:

```bash
# Start the server
python api_server.py

# Test the API
python api_client.py
```

## Output Analysis

### Excel Report Structure

The `final_recon_report.xlsx` contains:

#### **Original Data**
- `TradeID`: Unique trade identifier
- `PV_old`, `PV_new`: Present values from old/new models
- `Delta_old`, `Delta_new`: Delta risk from old/new models

#### **Mismatch Analysis**
- `PV_Diff`, `Delta_Diff`: Absolute differences
- `PV_Mismatch`, `Delta_Mismatch`: Boolean flags for mismatches
- `Any_Mismatch`: Overall mismatch indicator

#### **Diagnoses**
- `PV_Diagnosis`, `Delta_Diagnosis`: Rule-based root cause analysis
- `ML_Diagnosis`: Machine learning predictions

### Business Rules

The system applies the following diagnostic rules:

| Condition | Diagnosis |
|-----------|-----------|
| `PV_old` is None | "New trade – no prior valuation" |
| `PV_new` is None | "Trade dropped from new model" |
| Legacy LIBOR + outdated model | "Legacy LIBOR curve with outdated model – PV likely shifted" |
| CSA changed post-clearing | "CSA changed post-clearing – funding basis moved" |
| Option + Delta mismatch | "Vol sensitivity likely – delta impact due to model curve shift" |
| Default | "Within tolerance" |

#### **ML Diagnoses**
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

#### 3. API Connection Issues
```
ConnectionError: Failed to connect to API endpoint
```
**Solution**: 
- Verify API configuration in `api_config.json`
- Check network connectivity
- Use `--source files` as fallback

#### 4. Data Type Errors
```
TypeError: Cannot convert 'Swap' to float
```
**Solution**: Ensure categorical features are properly handled (already fixed in current version)

#### 5. Memory Issues
```
MemoryError: Unable to allocate array
```
**Solution**: Process data in smaller chunks or increase system memory

#### 6. Model Loading Errors
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

### API Configuration
1. **Secure Keys**: Store API keys securely, not in version control
2. **Error Handling**: Implement proper fallback mechanisms
3. **Rate Limiting**: Respect API rate limits
4. **Monitoring**: Monitor API connection status

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

# 2. Run pipeline with auto-detect
python pipeline.py

# 3. Check results
ls -la final_recon_report.xlsx
```

### API Example
```bash
# 1. Create API configuration
cat > api_config.json << EOF
{
  "base_url": "https://api.example.com",
  "api_key": "your_key_here",
  "endpoints": {
    "old_pricing": "/api/v1/pricing/old",
    "new_pricing": "/api/v1/pricing/new",
    "trade_metadata": "/api/v1/trades/metadata",
    "funding_reference": "/api/v1/funding/reference"
  }
}
EOF

# 2. Run with API source
python pipeline.py --source api --api-config api_config.json

# 3. Run with specific trade IDs
python pipeline.py --source api --api-config api_config.json --trade-ids TRADE001 TRADE002
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