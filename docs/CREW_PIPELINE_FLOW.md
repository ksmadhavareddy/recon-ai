# 🚀 Crew Pipeline Flow Documentation

## Overview

When you run `python pipeline.py`, you're executing a sophisticated **agent-based reconciliation workflow** that processes financial trade data through multiple specialized AI agents. This document explains the complete flow for new developers.

## 🎯 Quick Start

```bash
# Basic usage (auto-detects data source)
python pipeline.py

# File-based processing
python pipeline.py --source files

# API-based processing
python pipeline.py --source api --api-config api_config.json

# Hybrid processing (both files and API)
python pipeline.py --source hybrid --api-config api_config.json
```

---

## 📊 High-Level Flow Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   pipeline.py   │───▶│ ReconciliationCrew │───▶│  UnifiedDataLoader │
│   (Entry Point) │    │   (Orchestrator) │    │   (Data Agent)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ReconAgent    │◀───│   AnalyzerAgent │───▶│ MLDiagnoserAgent │
│ (Mismatch Det.) │    │ (Rule Analysis) │    │  (ML Predictor) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  NarratorAgent  │
                       │ (Report Gen.)   │
                       └─────────────────┘
```

---

## 🔄 Detailed Pipeline Flow

### **Step 1: Entry Point (`pipeline.py`)**

```python
# Command line arguments
--source: "files", "api", "auto", "hybrid"
--data-dir: Directory containing Excel files
--api-config: Path to API configuration
--trade-ids: Specific trade IDs to process
--date: Specific date for pricing data
```

**What happens:**
1. Parse command line arguments
2. Load API configuration (if provided)
3. Initialize `ReconciliationCrew`
4. Call `crew.run()` with parameters

### **Step 2: Data Loading (`UnifiedDataLoaderAgent`)**

**Supported Data Sources:**

#### **Files Mode (`--source files`)**
```bash
python pipeline.py --source files --data-dir data/
```
- Loads from Excel files in `data/` directory:
  - `old_pricing.xlsx`
  - `new_pricing.xlsx`
  - `trade_metadata.xlsx`
  - `funding_model_reference.xlsx`

#### **API Mode (`--source api`)**
```bash
python pipeline.py --source api --api-config api_config.json
```
- Connects to REST API endpoints
- Fetches data via HTTP requests
- Supports filtering by trade IDs and dates

#### **Auto Mode (`--source auto`) - DEFAULT**
```bash
python pipeline.py  # Uses auto mode by default
```
- Tries API first, falls back to files
- Automatic source detection
- Graceful error handling

#### **Hybrid Mode (`--source hybrid`)**
```bash
python pipeline.py --source hybrid --api-config api_config.json
```
- Loads from both API and files
- Merges and deduplicates data
- Provides comprehensive coverage

**Data Loading Process:**
```python
# 1. Validate data source availability
# 2. Load required datasets
# 3. Merge dataframes on TradeID
# 4. Validate data quality
# 5. Return unified DataFrame
```

### **Step 3: Mismatch Detection (`ReconAgent`)**

**Purpose:** Identify trades with significant differences between old and new pricing.

**Process:**
```python
# Calculate differences
df["PV_Diff"] = df["PV_new"] - df["PV_old"]
df["Delta_Diff"] = df["Delta_new"] - df["Delta_old"]

# Apply tolerance thresholds
df["PV_Mismatch"] = df["PV_Diff"].abs() > pv_tolerance  # Default: 1000
df["Delta_Mismatch"] = df["Delta_Diff"].abs() > delta_tolerance  # Default: 0.05

# Flag any mismatches
df["Any_Mismatch"] = df["PV_Mismatch"] | df["Delta_Mismatch"]
```

**Configurable Parameters:**
- `pv_tolerance`: PV difference threshold (default: 1000)
- `delta_tolerance`: Delta difference threshold (default: 0.05)

### **Step 4: Rule-Based Analysis (`AnalyzerAgent`)**

**Purpose:** Apply business rules to diagnose root causes of mismatches.

**Components:**

#### **PVAnalysisAgent**
- Analyzes Present Value (PV) related issues
- Applies dynamic business rules
- Generates PV diagnosis labels

#### **DeltaAnalysisAgent**
- Analyzes Delta risk related issues
- Applies delta-specific business rules
- Generates Delta diagnosis labels

#### **DynamicLabelGenerator**
- Manages business rules dynamically
- Discovers patterns in data
- Learns from analysis results

**Business Rules Examples:**
```python
# PV Rules
{
    "condition": "PV_old is None",
    "label": "New trade – no prior valuation",
    "priority": 1,
    "category": "new_trade"
}

# Delta Rules
{
    "condition": "Delta_Mismatch == True and ProductType == 'Option'",
    "label": "Vol sensitivity likely",
    "priority": 2,
    "category": "volatility"
}
```

### **Step 5: Machine Learning Analysis (`MLDiagnoserAgent`)**

**Purpose:** Use trained ML model to predict diagnoses and provide confidence scores.

**Process:**
```python
# 1. Check if model exists
if self.ml_agent.model is None:
    # Train model with current data
    self.ml_agent.train(df, label_col='PV_Diagnosis')

# 2. Make predictions
df["ML_Diagnosis"] = self.ml_agent.predict(df, label_col='PV_Diagnosis')
```

**ML Features:**
- Trade characteristics (ProductType, FundingCurve, CSA_Type)
- Mismatch indicators (PV_Mismatch, Delta_Mismatch)
- Difference values (PV_Diff, Delta_Diff)
- Metadata (ModelVersion, etc.)

### **Step 6: Report Generation (`NarratorAgent`)**

**Purpose:** Generate comprehensive reconciliation reports and summaries.

**Outputs:**
1. **Console Summary:** Key statistics and findings
2. **Excel Report:** Detailed reconciliation data (`final_recon_report.xlsx`)
3. **Analysis Logs:** Processing details and diagnostics

---

## 🏗️ Agent Architecture

### **Agent Responsibilities**

| Agent | Purpose | Key Methods | Output |
|-------|---------|-------------|---------|
| **UnifiedDataLoaderAgent** | Data ingestion | `load_data()`, `_load_from_files()`, `_load_from_api()` | Merged DataFrame |
| **ReconAgent** | Mismatch detection | `add_diff_flags()` | DataFrame with mismatch flags |
| **AnalyzerAgent** | Rule-based analysis | `apply()`, `analyze()` | DataFrame with diagnosis labels |
| **MLDiagnoserAgent** | ML predictions | `train()`, `predict()` | DataFrame with ML predictions |
| **NarratorAgent** | Report generation | `summarize_report()`, `save_report()` | Excel report + console output |

### **Data Flow Between Agents**

```
Raw Data (Files/API)
        ↓
UnifiedDataLoaderAgent
        ↓
Merged DataFrame
        ↓
ReconAgent (add mismatch flags)
        ↓
DataFrame with PV_Diff, Delta_Diff, PV_Mismatch, Delta_Mismatch
        ↓
AnalyzerAgent (apply business rules)
        ↓
DataFrame with PV_Diagnosis, Delta_Diagnosis
        ↓
MLDiagnoserAgent (ML predictions)
        ↓
DataFrame with ML_Diagnosis
        ↓
NarratorAgent (generate reports)
        ↓
final_recon_report.xlsx + Console Summary
```

---

## 🔧 Configuration Options

### **Data Source Configuration**

#### **File-based Configuration**
```bash
# Use specific data directory
python pipeline.py --source files --data-dir /path/to/data/

# Required files:
# - old_pricing.xlsx
# - new_pricing.xlsx  
# - trade_metadata.xlsx
# - funding_model_reference.xlsx
```

#### **API Configuration**
```json
{
  "base_url": "http://localhost:8000",
  "api_key": "your_api_key_here",
  "timeout": 30,
  "endpoints": {
    "old_pricing": "/api/database/old_pricing",
    "new_pricing": "/api/database/new_pricing",
    "trade_metadata": "/api/database/trade_metadata",
    "funding_reference": "/api/database/funding_model_reference"
  }
}
```

```bash
python pipeline.py --source api --api-config api_config.json
```

### **Processing Options**

#### **Filter by Trade IDs**
```bash
python pipeline.py --trade-ids T001 T002 T003
```

#### **Filter by Date**
```bash
python pipeline.py --date 2024-01-15
```

#### **Custom Tolerances**
```python
# In code
crew = ReconciliationCrew(pv_tolerance=500, delta_tolerance=0.01)
```

---

## 📊 Output Structure

### **Final DataFrame Columns**

| Column | Type | Description |
|--------|------|-------------|
| `TradeID` | String | Unique trade identifier |
| `PV_old`, `PV_new` | Float | Present values (old/new) |
| `Delta_old`, `Delta_new` | Float | Delta risk (old/new) |
| `ProductType`, `FundingCurve`, `CSA_Type`, `ModelVersion` | String | Trade metadata |
| `PV_Diff`, `Delta_Diff` | Float | Calculated differences |
| `PV_Mismatch`, `Delta_Mismatch`, `Any_Mismatch` | Boolean | Mismatch flags |
| `PV_Diagnosis`, `Delta_Diagnosis` | String | Rule-based diagnoses |
| `ML_Diagnosis` | String | ML predictions |

### **Console Output Example**
```
🚀 Starting Agent-Based Reconciliation Workflow...

🔄 Step 1: Loading data...
INFO: Loaded 25 rows from old_pricing
INFO: Loaded 25 rows from new_pricing
INFO: Loaded 25 rows from trade_metadata
INFO: Loaded 25 rows from funding_reference
INFO: Merged data contains 25 trades

📏 Step 2: Computing PV/Delta mismatches...

🧠 Step 3: Diagnosing root causes (rule-based)...
INFO: Applying rule-based analysis to 25 trades
INFO: Analysis completed. PV diagnoses: 3 unique, Delta diagnoses: 2 unique

🤖 Step 4: Training ML model and predicting diagnoses...
INFO: Making predictions for 25 samples
INFO: Predictions completed in 0.02s

📝 Step 5: Generating report...
📊 Reconciliation Summary:
Total Trades: 25
PV Mismatches: 3
Delta Mismatches: 2
Flagged Trades: 4
✅ Report saved to: final_recon_report.xlsx

✅ Workflow complete! Processed 25 trades.
📊 Check your reconciliation report: final_recon_report.xlsx
```

---

## 🐛 Troubleshooting

### **Common Issues**

#### **Data Loading Issues**
```bash
# Check if files exist
ls -la data/

# Test API connection
curl http://localhost:8000/api/health

# Verify API configuration
python -c "import json; print(json.dumps(json.load(open('api_config.json')), indent=2))"
```

#### **Memory Issues**
```bash
# Process smaller batches
python pipeline.py --trade-ids T001 T002 T003

# Use specific date to reduce data volume
python pipeline.py --date 2024-01-15
```

#### **ML Model Issues**
```bash
# Check if model files exist
ls -la models/

# Retrain model (will happen automatically if missing)
python pipeline.py --source files
```

### **Debug Mode**
```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run pipeline
python pipeline.py --source files
```

---

## 🚀 Advanced Usage

### **Custom Business Rules**
```python
from crew.crew_builder import ReconciliationCrew

crew = ReconciliationCrew()
analyzer = crew.analyzer_agent

# Add custom rule
analyzer.add_business_rule(
    rule_type="pv_rules",
    condition="ProductType == 'CDS' and PV_Diff > 50000",
    label="Large CDS PV difference - credit event impact",
    priority=3,
    category="credit_event"
)

# Run pipeline
df = crew.run(source="files")
```

### **Programmatic Usage**
```python
from crew.crew_builder import ReconciliationCrew

# Initialize crew
crew = ReconciliationCrew(
    data_dir="data/",
    pv_tolerance=1000,
    delta_tolerance=0.05
)

# Run reconciliation
df = crew.run(source="auto")

# Access individual agents
data_loader = crew.data_loader
recon_agent = crew.recon_agent
analyzer_agent = crew.analyzer_agent
ml_agent = crew.ml_agent
narrator_agent = crew.narrator_agent

# Get data source status
status = crew.get_data_source_status()
print(f"API available: {status['api_available']}")
print(f"Files available: {status['files_available']}")
```

---

## 📈 Performance Considerations

### **Large Dataset Processing**
- **Memory Usage:** ~50MB per 10,000 trades
- **Processing Time:** ~2-5 seconds per 1,000 trades
- **ML Training:** ~10-30 seconds for initial model training

### **Optimization Tips**
1. **Use specific trade IDs** for targeted analysis
2. **Filter by date** to reduce data volume
3. **Use file mode** for faster processing (no API calls)
4. **Batch processing** for very large datasets

### **Scaling Considerations**
- **API Rate Limits:** Respect API endpoint limits
- **Memory Management:** Process in chunks for large datasets
- **Concurrent Processing:** Consider parallel processing for multiple date ranges

---

## 🔗 Integration Points

### **External Systems**
- **REST APIs:** Standard HTTP endpoints for data retrieval
- **Excel Files:** Standard Excel format for data input
- **Database:** Can be extended to support direct database connections

### **Custom Extensions**
- **New Agents:** Extend the agent architecture
- **Custom Rules:** Add domain-specific business rules
- **ML Models:** Integrate custom ML models
- **Report Formats:** Customize output formats

---

**🎯 This crew pipeline provides a robust, scalable solution for financial reconciliation with AI-powered analysis and dynamic rule generation.** 