# 🧠 AI-Powered Reconciliation System

An intelligent reconciliation engine that combines **dynamic rule-based business logic** with machine learning to identify and diagnose pricing mismatches between old and new financial models.

## 🚀 Key Features

- ✅ **PV and Delta comparison** with configurable thresholds
- 📉 **Dynamic rule-based funding-aware diagnostics**
- 🧩 **Modular agents**: Loader, Reconciler, Analyzer, Narrator
- 📤 **Final Excel report** with root cause annotations
- 🔌 **API Integration** for real-time data access
- 🌐 **REST API Server** for data access and integration
- 🤖 **ML-powered diagnosis** with LightGBM models
- 📊 **Interactive Dashboard** with Streamlit
- 🔄 **Unified data loading** (Files + APIs + Auto-detect + Hybrid)
- 🎯 **Dynamic Label Generation** for real-time diagnosis scenarios

## 📁 Project Structure

```
recon-ai/
├── crew/
│   ├── agents/                      # Modular agents
│   │   ├── unified_data_loader.py  # Unified data loading
│   │   ├── recon_agent.py          # Mismatch detection
│   │   ├── analyzer_agent.py       # Dynamic rule-based analysis
│   │   ├── ml_tool.py             # ML diagnosis with dynamic labels
│   │   ├── dynamic_label_generator.py # Dynamic label generation
│   │   └── narrator_agent.py       # Report generation
│   └── crew_builder.py             # CrewAI team definition
├── data/                           # Input data files
├── models/                         # Trained ML models
├── config/                         # Configuration files
├── docs/                          # Documentation
├── app.py                         # Streamlit dashboard
├── pipeline.py                    # Command-line pipeline
├── api_server.py                  # REST API server
├── run_dashboard.py               # Enhanced dashboard launcher
├── fix_common_issues.py           # Automated fix script
└── requirements.txt
```

## 🎯 Dynamic Label Generation

The system features **Dynamic Label Generation** that creates diagnosis labels in real-time based on:

1. **Business Rules**: Configurable rules from analyzer agents
2. **Data Patterns**: Discovered patterns and anomalies
3. **Domain Knowledge**: Industry standards and best practices
4. **Historical Analysis**: Root cause patterns from previous analyses

### **Key Components**

- **DynamicLabelGenerator**: Business rules engine with pattern discovery
- **Enhanced AnalyzerAgent**: Dynamic rule application and management
- **ML Integration**: Adaptive training with dynamic labels

---

## 🛠️ Quick Start

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

### **For System Administrators**

1. **Deploy**: Follow [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
2. **Monitor**: Use [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
3. **Configure**: See [Usage Guide](docs/USAGE_GUIDE.md)

---

## 🎯 Agent Architecture

| Agent | Role | Key Features |
|-------|------|--------------|
| **UnifiedDataLoaderAgent** | Loads and merges pricing, trade, and funding data | Multi-source support, auto-fallback |
| **ReconAgent** | Flags mismatches in PV and Delta values | Configurable thresholds |
| **AnalyzerAgent** | Provides **dynamic funding-aware diagnostic tags** | Dynamic business rules, safe condition evaluation |
| **MLDiagnoserAgent** | ML-powered diagnosis predictions | Dynamic label integration, adaptive training |
| **DynamicLabelGenerator** | **Generates diagnosis labels in real-time** | Pattern discovery, business rules, domain knowledge |
| **NarratorAgent** | Summarizes results and generates reports | Comprehensive reporting |

---

## 🧠 ML Integration

### **Features**
- **LightGBM model** for diagnosis prediction
- **Automatic training** using dynamically generated diagnoses as labels
- **Model persistence** for reuse
- **Confidence scoring** and validation
- **Comparison analysis** between ML and rule-based results
- **Dynamic label adaptation** based on new patterns

### **Why LightGBM?**
- **Speed**: Faster training and prediction than XGBoost and CatBoost
- **Memory Efficiency**: Histogram-based algorithm for large datasets
- **Categorical Support**: Native handling of product types and funding curves
- **Scalability**: Handles 100+ million records efficiently
- **Feature Interactions**: Captures complex relationships in financial data
- **Dynamic Patterns**: Adapts to changing business rules and market conditions

---

## 📊 Data Sources

The system supports multiple data sources through a **unified data loader**:

### **File-based (Traditional)**
Place Excel files in `data/` directory:
```
data/
├── old_pricing.xlsx
├── new_pricing.xlsx
├── trade_metadata.xlsx
└── funding_model_reference.xlsx
```

### **API-based (Real-time)**
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

### **Auto-detect (Smart)**
Automatically chooses the best available source with fallback.

### **Hybrid (Best of Both)**
Configure both file and API sources for automatic fallback and data merging.

---

## 🚀 Running the System

### **Interactive Dashboard (Recommended)**
```bash
# Enhanced launcher with error handling
python run_dashboard.py

# Or direct Streamlit command
python -m streamlit run app.py --server.port 8501
```

### **Command Line Pipeline**
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

### **API Server**
```bash
# Start REST API server
python api_server.py

# Or with uvicorn
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### **Access Points**
- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## 🔧 Quick Troubleshooting

### **Common Issues**
```bash
# Check if all packages are installed
python -c "import streamlit, uvicorn, pandas, lightgbm; print('✅ All packages installed')"

# Run with file watching disabled (fixes Streamlit errors)
python -m streamlit run app.py --server.fileWatcherType none

# Check data files
ls -la data/

# Test individual components
python -c "from crew.agents.unified_data_loader import UnifiedDataLoaderAgent; print('✅ Data loader works')"

# Run automated fix script
python fix_common_issues.py
```

### **Quick Health Check**
```bash
# Test API connection
python test_api_connection.py --config api_config.json

# Run dashboard
python run_dashboard.py

# Run pipeline
python pipeline.py
```

---

## 📚 Documentation

### **User Documentation**
- 📖 **[Complete User Guide](docs/USAGE_GUIDE.md)** - Everything you need to use the system
- 🔧 **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- 🚀 **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment instructions

### **Developer Documentation**
- 🏗️ **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- 🔧 **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- 📊 **[Documentation Index](docs/INDEX.md)** - Navigation hub

### **Specialized Guides**
- 🔄 **[Migration Guide](UNIFIED_LOADER.md)** - Guide for unified data loader
- 🎯 **[Dynamic Labels Guide](DYNAMIC_LABELS_GUIDE.md)** - Dynamic label generation system
- 🤖 **[ML Diagnoser Documentation](ML_DIAGNOSER_DOCUMENTATION.md)** - ML agent documentation
- 🧹 **[Cleanup Summary](CLEANUP_SUMMARY.md)** - Summary of removed files

---

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

### **Code Standards**
- Follow PEP 8 for Python code
- Add docstrings to all functions
- Include type hints
- Write unit tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**👋 Author**  
Developed with clarity and modularity by Madhava  
GitHub: ksmadhavareddy

**🎉 Happy Reconciling!**