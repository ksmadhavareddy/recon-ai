# 🧠 CrewAI Reconciliation App

This project implements a modular, agent-based reconciliation engine powered by Crew-style coordination. It compares old and new pricing models across PV and Delta risk, enriched with funding metadata and **dynamic rule-based diagnostics**.

---

## 🚀 Key Features

- ✅ PV and Delta comparison with configurable thresholds
- 📉 **Dynamic rule-based funding-aware diagnostics**
- 🧩 Modular agents: Loader, Reconciler, Analyzer, Narrator
- 📤 Final Excel report with root cause annotations
- 🔌 **API Integration** for real-time data access
- 🌐 **REST API Server** for data access and integration
- 🤖 **ML-powered diagnosis** with LightGBM models
- 📊 **Interactive Dashboard** with Streamlit
- 🔄 **Unified data loading** (Files + APIs + Auto-detect + Hybrid)
- 🎯 **Dynamic Label Generation** for real-time diagnosis scenarios

---

## 📁 Folder Structure

```
recon-ai/
├── crew/
│   ├── agents/                      # Modular agents
│   │   ├── unified_data_loader.py  # Unified data loading (files + APIs)
│   │   ├── recon_agent.py          # Mismatch detection
│   │   ├── analyzer_agent.py       # Dynamic rule-based analysis
│   │   ├── ml_tool.py             # ML diagnosis with dynamic labels
│   │   ├── dynamic_label_generator.py # Dynamic label generation system
│   │   └── narrator_agent.py       # Report generation
│   └── crew_builder.py             # CrewAI team definition
├── data/                           # Input data files
├── models/                         # Trained ML models
├── config/                         # Configuration files
│   └── diagnosis_labels.json      # Dynamic label patterns
├── docs/                          # Documentation
├── app.py                         # Streamlit dashboard
├── pipeline.py                    # Command-line pipeline
├── api_server.py                  # REST API server
├── api_client.py                  # API client utility
├── test_api_connection.py         # API testing utility
├── api_config_example.json        # API configuration template
├── API_DOCUMENTATION.md           # REST API documentation
├── UNIFIED_LOADER.md              # Comprehensive unified data loader guide
├── DYNAMIC_LABELS_GUIDE.md        # Dynamic label generation guide
├── ML_DIAGNOSER_DOCUMENTATION.md  # ML Diagnoser Agent documentation
├── CLEANUP_SUMMARY.md             # Summary of deprecated files removed
├── requirements.txt
└── README.md
```

---

## 🎯 Dynamic Label Generation System

### **Overview:**
The system now features a **Dynamic Label Generator** that creates diagnosis labels in real-time based on:

1. **Business Rules**: Configurable rules from analyzer agents
2. **Data Patterns**: Discovered patterns and anomalies
3. **Domain Knowledge**: Industry standards and best practices
4. **Historical Analysis**: Root cause patterns from previous analyses

### **Key Components:**

#### **DynamicLabelGenerator Class:**
- **Business Rules Engine**: Loads and applies configurable business rules
- **Pattern Discovery**: Analyzes data to identify new diagnosis patterns
- **Domain Knowledge**: Industry-specific diagnosis categories
- **Historical Tracking**: Maintains patterns and label frequency
- **Real-time Updates**: Updates based on analysis results

#### **Enhanced AnalyzerAgent:**
- **Dynamic Rule Application**: Applies business rules dynamically
- **Safe Condition Evaluation**: Safely evaluates string-based conditions
- **Rule Management**: Add, modify, and manage business rules
- **Integration**: Updates the label generator with analysis results

#### **ML Integration:**
- **Dynamic Labels**: ML model uses dynamically generated labels
- **Adaptive Training**: Model adapts to new patterns and rules
- **Real-time Learning**: Incorporates new diagnoses automatically

### **Business Rules Categories:**
- **Trade Lifecycle**: New trades, dropped trades, amendments
- **Curve/Model**: LIBOR transition, model updates, curve changes
- **Funding/CSA**: Clearing changes, collateral updates, margin requirements
- **Volatility**: Option sensitivity, delta impacts, model shifts
- **Data Quality**: Missing data, validation issues, format problems
- **Market Events**: Market disruptions, regulatory changes

---

## 🛠️ How to Use

### 1. 🧱 Install requirements:

```bash
pip install -r requirements.txt
```

### 2. 📂 Data Sources

The system now uses a **unified data loader** that supports multiple sources:

#### **Option A: File-based (Traditional)**
Place input files into `data/`:

```
data/
├── old_pricing.xlsx
├── new_pricing.xlsx
├── trade_metadata.xlsx
└── funding_model_reference.xlsx
```

#### **Option B: API-based (Real-time)**
Configure API endpoints in `api_config_example.json`:

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

#### **Option C: Auto-detect (Smart)**
Automatically chooses the best available source with fallback.

#### **Option D: Hybrid (Best of Both)**
Configure both file and API sources for automatic fallback and data merging.

### 3. 🚀 Run the workflow:

#### **Command Line:**
```bash
# File-based only
python pipeline.py --source files

# API-based only
python pipeline.py --source api --api-config api_config.json

# Auto-detect (default)
python pipeline.py --source auto

# Hybrid loading
python pipeline.py --source hybrid --api-config api_config.json
```

#### **Dashboard:**
```bash
# Launch interactive dashboard
python run_dashboard.py

# Or directly with streamlit
python -m streamlit run app.py --server.port 8501
```

#### **API Server:**
```bash
# Start REST API server
python api_server.py

# Or with uvicorn
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### 4. 📊 View Results:

- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## 🎯 Agent Architecture

| Agent | Role | Data Source | New Features |
|-------|------|-------------|--------------|
| **UnifiedDataLoaderAgent** | Loads and merges pricing, trade, and funding data | Files, APIs, Auto-detect, Hybrid | - |
| **ReconAgent** | Flags mismatches in PV and Delta values | All | Configurable thresholds |
| **AnalyzerAgent** | Provides **dynamic funding-aware diagnostic tags** | All | **Dynamic business rules, safe condition evaluation** |
| **MLDiagnoserAgent** | ML-powered diagnosis predictions | All | **Dynamic label integration, adaptive training** |
| **DynamicLabelGenerator** | **Generates diagnosis labels in real-time** | All | **Pattern discovery, business rules, domain knowledge** |
| **NarratorAgent** | Summarizes results and generates reports | All | - |

---

## 🧠 ML Integration

### **Features:**
- **LightGBM model** for diagnosis prediction
- **Automatic training** using **dynamically generated** diagnoses as labels
- **Model persistence** for reuse
- **Confidence scoring** and validation
- **Comparison analysis** between ML and rule-based results
- **Dynamic label adaptation** based on new patterns

### **Model Architecture:**
- **Features**: PV/Delta values, product types, funding curves
- **Target**: **Dynamically generated** diagnosis labels
- **Algorithm**: LightGBM with categorical feature support
- **Validation**: Cross-validation with business rules
- **Adaptive Learning**: Incorporates new patterns and rules

### **Dynamic Label Integration:**
- **Real-time Generation**: Labels created based on current data and business rules
- **Pattern Discovery**: Automatically identifies new diagnosis patterns
- **Historical Learning**: Incorporates patterns from previous analyses
- **Business Rule Application**: Applies configurable rules dynamically
- **Domain Knowledge**: Uses industry-specific diagnosis categories

### **Why LightGBM?**

We chose **LightGBM** as our primary ML model for the following reasons:

- **Speed**: Faster training and prediction than XGBoost and CatBoost
- **Memory Efficiency**: Histogram-based algorithm for large datasets
- **Categorical Support**: Native handling of product types and funding curves
- **Scalability**: Handles 100+ million records efficiently
- **Feature Interactions**: Captures complex relationships in financial data
- **Dynamic Patterns**: Adapts to changing business rules and market conditions

---

## 🔧 Configuration

### **Threshold Settings:**
```python
# Adjust mismatch detection sensitivity
recon_agent = ReconAgent(
    pv_tolerance=1000,      # PV mismatch threshold
    delta_tolerance=0.05     # Delta mismatch threshold
)
```

### **Dynamic Label Configuration:**
```python
# Configure business rules for diagnosis generation
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
            "label": "Legacy LIBOR curve with outdated model",
            "priority": 2,
            "category": "curve_model"
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
```

### **API Settings:**
```python
# Configure API endpoints and authentication
api_config = {
    'base_url': 'https://api.example.com',
    'api_key': 'your_key',
    'timeout': 30,
    'endpoints': {...}
}
```

---

## 🚀 Future Enhancements

### **Planned Features:**
- 🔄 **Real-time streaming** with WebSocket support
- 🤖 **Advanced ML models** (Deep Learning, Ensemble)
- 📊 **Advanced analytics** and statistical modeling
- 🔔 **Smart alerting** and notification system
- 🌐 **Cloud deployment** (AWS, Azure, GCP)
- 🔐 **Enhanced security** and authentication
- 📱 **Mobile app** for on-the-go monitoring
- 🎯 **Advanced pattern recognition** for complex market scenarios

### **Technical Improvements:**
- **Database integration** for persistent storage
- **Microservices architecture** for scalability
- **Containerization** with Docker
- **CI/CD pipeline** for automated deployment
- **Performance optimization** for large datasets
- **Enhanced dynamic label generation** with machine learning

---

## 📞 Support & Documentation

### **Documentation:**
- 📖 [Usage Guide](docs/USAGE_GUIDE.md) - Detailed usage instructions
- 🏗️ [Architecture](docs/ARCHITECTURE.md) - System design and components
- 🔧 [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- 📊 [Diagrams](docs/DIAGRAMS.md) - System diagrams and flowcharts
- 🔄 [Migration Guide](UNIFIED_LOADER.md) - Guide for unified data loader
- 🎯 [Dynamic Labels Guide](DYNAMIC_LABELS_GUIDE.md) - Dynamic label generation system
- 🤖 [ML Diagnoser Documentation](ML_DIAGNOSER_DOCUMENTATION.md) - ML agent documentation
- 🧹 [Cleanup Summary](CLEANUP_SUMMARY.md) - Summary of removed files
- 🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions
- 🚀 [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Production deployment instructions

### **Testing:**
```bash
# Test API connection
python test_api_connection.py --config api_config.json

# Run dashboard
python run_dashboard.py

# Run pipeline
python pipeline.py
```

### **Quick Troubleshooting:**
```bash
# Check if all packages are installed
python -c "import streamlit, uvicorn, pandas, lightgbm; print('✅ All packages installed')"

# Run with file watching disabled (fixes Streamlit errors)
python -m streamlit run app.py --server.fileWatcherType none

# Check data files
ls -la data/

# Test individual components
python -c "from crew.agents.unified_data_loader import UnifiedDataLoaderAgent; print('✅ Data loader works')"
```

---

## 🤝 Contributing

### **Development Setup:**
1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

### **Code Standards:**
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