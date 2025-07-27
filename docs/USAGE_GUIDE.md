# 📖 Complete User Guide

## 🎯 Overview

This is the **single comprehensive guide** for all users of the AI-Powered Reconciliation System. Everything you need to install, configure, and use the system is contained here.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation & Setup](#installation--setup)
3. [Data Preparation](#data-preparation)
4. [Running the System](#running-the-system)
5. [Configuration](#configuration)
6. [Dynamic Label Generation](#dynamic-label-generation)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## 🚀 Quick Start

### **For New Users (5 minutes)**

1. **Install**: `pip install -r requirements.txt`
2. **Prepare Data**: Place Excel files in `data/` directory
3. **Run Dashboard**: `python run_dashboard.py`
4. **View Results**: Open http://localhost:8501

### **For Developers (10 minutes)**

1. **Install**: `pip install -r requirements.txt`
2. **Run Pipeline**: `python pipeline.py --source files`
3. **Check Results**: `final_recon_report.xlsx`
4. **API Server**: `python api_server.py`

---

## 🛠️ Installation & Setup

### **Prerequisites**

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 1GB free space
- **Network**: Internet connection for package installation

### **Installation Steps**

#### **Step 1: Clone Repository**
```bash
git clone <repository-url>
cd recon-ai
```

#### **Step 2: Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import streamlit, uvicorn, pandas, lightgbm; print('✅ All packages installed')"
```

#### **Step 3: Setup Data Directory**
```bash
# Create data directory
mkdir -p data

# Verify setup
ls -la data/
```

#### **Step 4: Run Quick Test**
```bash
# Test basic functionality
python fix_common_issues.py

# Test dashboard
python run_dashboard.py
```

### **Alternative Installation Methods**

#### **Using Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### **Using Conda**
```bash
# Create conda environment
conda create -n recon-ai python=3.11
conda activate recon-ai

# Install dependencies
pip install -r requirements.txt
```

---

## 📊 Data Preparation

### **Required Input Files**

Place these files in the `data/` directory:

#### **1. old_pricing.xlsx**
```csv
TradeID,PV_old,Delta_old
T001,104500,0.42
T002,-98000,-0.98
T003,50500,0.00
```

#### **2. new_pricing.xlsx**
```csv
TradeID,PV_new,Delta_new
T001,104200,0.41
T002,-97500,-0.97
T003,51000,0.01
```

#### **3. trade_metadata.xlsx**
```csv
TradeID,ProductType,FundingCurve,CSA_Type,ModelVersion
T001,Swap,USD-LIBOR,Cleared,v2024.2
T002,Option,USD-SOFR,Bilateral,v2024.3
T003,Bond,EUR-EURIBOR,Cleared,v2024.1
```

#### **4. funding_model_reference.xlsx**
```csv
FundingCurve,ModelVersion,CurveDate,Rate
USD-LIBOR,v2024.2,2024-01-15,5.25
USD-SOFR,v2024.3,2024-01-15,5.30
EUR-EURIBOR,v2024.1,2024-01-15,4.50
```

### **Data Requirements**

#### **Column Specifications**
- **TradeID**: Unique string identifier (required)
- **PV_old/PV_new**: Numeric values (can be null for new trades)
- **Delta_old/Delta_new**: Numeric values (can be null)
- **ProductType**: String (Swap, Option, Bond, etc.)
- **FundingCurve**: String (USD-LIBOR, USD-SOFR, etc.)
- **CSA_Type**: String (Cleared, Bilateral, etc.)
- **ModelVersion**: String (v2024.1, v2024.2, etc.)

#### **Data Quality Checks**
- **No duplicate TradeIDs**
- **Consistent data types**
- **Reasonable value ranges**
- **Complete metadata for all trades**

### **Auto-Load Feature**

The dashboard includes an **auto-load functionality** that automatically loads all 4 files from the `data/` directory:

1. **One-Click Setup**: Choose "Auto-load from data/" option
2. **Visual Status**: Real-time loading indicators
3. **Ready Confirmation**: Clear "Ready for reconciliation analysis!" message
4. **Error Handling**: Graceful handling of missing or corrupted files

---

## 🚀 Running the System

### **Method 1: Interactive Dashboard (Recommended)**

#### **Start Dashboard**
```bash
# Enhanced launcher with error handling
python run_dashboard.py

# Or direct Streamlit command
python -m streamlit run app.py --server.port 8501
```

#### **Dashboard Features**
- **Auto-load**: Automatically loads files from `data/` directory
- **File Upload**: Manual file upload interface
- **Real-time Processing**: Live reconciliation analysis
- **Interactive Visualizations**: Charts and graphs with Plotly
- **Export Capabilities**: Download results as Excel files

#### **Dashboard URL**
- **Local**: http://localhost:8501
- **Network**: http://your-ip:8501

### **Method 2: Command Line Pipeline**

#### **Basic Usage**
```bash
# File-based only
python pipeline.py --source files

# Auto-detect (default)
python pipeline.py --source auto

# API-based only
python pipeline.py --source api --api-config api_config.json

# Hybrid loading
python pipeline.py --source hybrid --api-config api_config.json
```

#### **Advanced Usage**
```bash
# With specific trade IDs
python pipeline.py --source api --api-config api_config.json --trade-ids TRADE001 TRADE002

# With specific date
python pipeline.py --source api --api-config api_config.json --date 2024-01-15

# With custom data directory
python pipeline.py --source files --data-dir /path/to/data
```

### **Method 3: API Server**

#### **Start API Server**
```bash
# Start REST API server
python api_server.py

# Or with uvicorn
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

#### **API Endpoints**
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Data Access**: http://localhost:8000/api/database/

### **Method 4: Python Script**

#### **Programmatic Usage**
```python
from crew.crew_builder import ReconciliationCrew

# Initialize crew
crew = ReconciliationCrew(
    data_dir="data/",
    pv_tolerance=1000,
    delta_tolerance=0.05
)

# Run reconciliation
df = crew.run(source="files")

# Save results
df.to_excel("final_recon_report.xlsx", index=False)
```

---

## ⚙️ Configuration

### **Threshold Configuration**

Adjust mismatch detection sensitivity:

```python
from crew.agents.recon_agent import ReconAgent

# Create recon agent with custom thresholds
recon_agent = ReconAgent(
    pv_tolerance=1000,      # PV mismatch threshold
    delta_tolerance=0.05     # Delta mismatch threshold
)
```

### **API Configuration**

Configure external data sources:

```json
{
  "base_url": "https://api.example.com",
  "api_key": "your_api_key_here",
  "timeout": 30,
  "retries": 3,
  "endpoints": {
    "old_pricing": "/api/v1/pricing/old",
    "new_pricing": "/api/v1/pricing/new",
    "trade_metadata": "/api/v1/trades/metadata",
    "funding_reference": "/api/v1/funding/reference"
  }
}
```

### **Environment Variables**

Set system-wide configuration:

```bash
# Data directory
export DATA_DIR="/path/to/data"

# Database path
export DB_PATH="/path/to/reconciliation.db"

# API settings
export API_HOST="0.0.0.0"
export API_PORT="8000"

# Logging level
export LOG_LEVEL="INFO"
```

---

## 🎯 Dynamic Label Generation

### **Overview**

The system features **Dynamic Label Generation** that creates diagnosis labels in real-time based on:

1. **Business Rules**: Configurable rules from analyzer agents
2. **Data Patterns**: Discovered patterns and anomalies
3. **Domain Knowledge**: Industry standards and best practices
4. **Historical Analysis**: Root cause patterns from previous analyses

### **Business Rules Configuration**

#### **Default Business Rules**
```python
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

#### **Custom Business Rules**
```python
from crew.agents.analyzer_agent import AnalyzerAgent

analyzer = AnalyzerAgent()

# Add custom business rule
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
```

### **Domain Knowledge Categories**

The system includes comprehensive domain knowledge categories:

- **Trade Lifecycle**: New trades, dropped trades, amendments
- **Curve/Model**: LIBOR transition, model updates, curve changes
- **Funding/CSA**: Clearing changes, collateral updates, margin requirements
- **Volatility**: Option sensitivity, delta impacts, model shifts
- **Data Quality**: Missing data, validation issues, format problems
- **Market Events**: Market disruptions, regulatory changes

### **Pattern Discovery**

The system automatically discovers patterns:

```python
from crew.agents.dynamic_label_generator import DynamicLabelGenerator

label_generator = DynamicLabelGenerator()

# Discover patterns in your data
patterns = label_generator.discover_patterns(df)

# View discovered patterns
print("Discovered PV patterns:", patterns.get('pv_patterns', []))
print("Discovered Delta patterns:", patterns.get('delta_patterns', []))
print("Discovered temporal patterns:", patterns.get('temporal_patterns', []))
print("Discovered product patterns:", patterns.get('product_patterns', []))
```

### **Usage Examples**

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

---

## 🔧 Troubleshooting

### **Common Issues**

#### **1. Streamlit File Watching Errors**
```bash
# Problem: FileNotFoundError in file watcher
# Solution: Use file watching disabled
python -m streamlit run app.py --server.fileWatcherType none

# Or use the enhanced launcher
python run_dashboard.py
```

#### **2. Command Not Found Errors**
```bash
# Problem: streamlit/uvicorn not recognized
# Solution: Use Python module syntax
python -m streamlit run app.py
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

#### **3. Missing Dependencies**
```bash
# Problem: ImportError for missing packages
# Solution: Install all dependencies
pip install -r requirements.txt

# Or run the fix script
python fix_common_issues.py
```

#### **4. Dashboard Loading Issues**
```bash
# Problem: Dashboard errors and missing files
# Solution: Check data files
ls -la data/

# Verify all required files exist
python -c "import pandas as pd; pd.read_excel('data/old_pricing.xlsx')"
```

### **Debug Mode**

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
python pipeline.py --debug
```

### **Performance Issues**

#### **Memory Management**
```python
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

#### **Large Dataset Processing**
```python
# Process data in chunks
chunk_size = 10000
for chunk in pd.read_excel("large_file.xlsx", chunksize=chunk_size):
    # Process each chunk
    result = analyzer.apply(chunk)
    # Save results incrementally
```

### **Component Testing**

Test individual components:

```python
# Test data loader
from crew.agents.unified_data_loader import UnifiedDataLoaderAgent
loader = UnifiedDataLoaderAgent()
df = loader.load_data('files')
print(f"Loaded {len(df)} trades")

# Test ML model
from crew.agents.ml_tool import MLDiagnoserAgent
ml_agent = MLDiagnoserAgent()
print(f"Model loaded: {ml_agent.model is not None}")
```

### **Quick Health Check**
```bash
# Verify all packages installed
python -c "import streamlit, uvicorn, pandas, lightgbm; print('✅ All packages installed')"

# Test dashboard
python run_dashboard.py

# Test API
python api_server.py

# Test pipeline
python pipeline.py --source files
```

---

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

### **Performance Optimization**

1. **Use Appropriate Data Types**: Use efficient data types for large datasets
2. **Process in Chunks**: Handle large datasets in manageable chunks
3. **Monitor Memory Usage**: Keep track of memory consumption
4. **Use Caching**: Implement caching for repeated operations

---

## 📊 Output Interpretation

### **Report Structure**

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

### **Example Output**

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

### **Understanding Diagnoses**

#### **Rule-based Diagnoses**
- **Within tolerance**: No significant mismatch detected
- **New trade – no prior valuation**: Trade exists only in new data
- **Legacy LIBOR curve**: Using outdated LIBOR curve with new model
- **Vol sensitivity likely**: Option with significant delta change

#### **ML Predictions**
- **Confidence scores**: ML model confidence in predictions
- **Feature importance**: Which factors influenced the prediction
- **Pattern recognition**: ML-identified patterns in the data

---

## 🚀 Advanced Features

### **Real-time Processing**

The system supports real-time data processing:

```python
# Process streaming data
for chunk in data_stream:
    result = crew.process_chunk(chunk)
    # Handle results in real-time
```

### **Custom Integrations**

Extend the system with custom integrations:

```python
# Custom data loader
class CustomDataLoader:
    def load_data(self):
        # Custom data loading logic
        pass

# Custom analyzer
class CustomAnalyzer:
    def analyze(self, data):
        # Custom analysis logic
        pass
```

### **Performance Monitoring**

Monitor system performance:

```python
import time

start_time = time.time()
# Run your analysis
end_time = time.time()
print(f"Processing time: {end_time - start_time:.2f} seconds")
```

---

## 📞 Getting Help

### **Documentation Resources**
- **This Guide**: Complete user guide (you're reading it)
- **API Reference**: Technical API documentation
- **Architecture**: System design and components
- **Troubleshooting**: Common issues and solutions
- **Deployment**: Production deployment instructions

### **Support Channels**
- **Documentation**: Comprehensive guides and examples
- **Code Examples**: Ready-to-use implementation
- **Troubleshooting**: Common issues and solutions
- **Performance Monitoring**: System performance tracking

### **Community Support**
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides
- **Examples**: Code examples in documentation
- **Troubleshooting**: Step-by-step solutions

---

**🎉 Happy Reconciling!**

This guide contains everything you need to successfully use the AI-Powered Reconciliation System. For technical details, see the API Reference and Architecture documentation. 