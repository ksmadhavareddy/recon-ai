# 🧠 CrewAI Reconciliation App

This project implements a modular, agent-based reconciliation engine powered by Crew-style coordination. It compares old and new pricing models across PV and Delta risk, enriched with funding metadata and rule-based diagnostics.

---

## 🚀 Key Features

- ✅ PV and Delta comparison with configurable thresholds
- 📉 Rule-based funding-aware diagnostics
- 🧩 Modular agents: Loader, Reconciler, Analyzer, Narrator
- 📤 Final Excel report with root cause annotations
- 🔌 **API Integration** for real-time data access
- 🌐 **REST API Server** for data access and integration
- 🤖 **ML-powered diagnosis** with CatBoost models
- 📊 **Interactive Dashboard** with Streamlit
- 🔄 **Hybrid data loading** (Files + APIs)

---

## 📁 Folder Structure

```
recon-ai/
├── crew/
│   ├── agents/                      # Modular agents
│   │   ├── data_loader.py          # File-based data loading
│   │   ├── api_data_loader.py      # API-based data loading
│   │   ├── hybrid_data_loader.py   # Hybrid file+API loader
│   │   ├── recon_agent.py          # Mismatch detection
│   │   ├── analyzer_agent.py       # Rule-based analysis
│   │   ├── ml_tool.py             # ML diagnosis
│   │   └── narrator_agent.py       # Report generation
│   └── crew_builder.py             # CrewAI team definition
├── data/                           # Input data files
├── models/                         # Trained ML models
├── docs/                          # Documentation
├── app.py                         # Streamlit dashboard
├── pipeline.py                    # Command-line pipeline
├── api_server.py                  # REST API server
├── api_client.py                  # API client utility
├── test_api_connection.py         # API testing utility
├── api_config_example.json        # API configuration template
├── API_DOCUMENTATION.md           # REST API documentation
├── requirements.txt
└── README.md
```

---

## 🛠️ How to Use

### 1. 🧱 Install requirements:

```bash
pip install -r requirements.txt
```

### 2. 📂 Data Sources

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

### 3. 🚀 Run the workflow:

#### **Command Line:**
```bash
# File-based
python pipeline.py

# API-based
python pipeline.py --api-config api_config.json
```

#### **Web Dashboard:**
```bash
# Launch interactive dashboard
python run_dashboard.py
# or
streamlit run app.py
```

#### **REST API Server:**
```bash
# Start REST API server
python api_server.py

# Test API client
python api_client.py
```

### 4. 📊 Output:

- `final_recon_report.xlsx` containing mismatches and diagnostics
- Interactive dashboard with real-time analysis
- ML model predictions alongside rule-based diagnoses

---

## 🔌 API Integration

### **REST API Server:**
- **FastAPI-based** REST API for data access
- **Excel file access** via HTTP endpoints
- **Database integration** with SQLite
- **Search capabilities** across tables and columns
- **Pagination support** for large datasets
- **Health monitoring** and status endpoints
- **CORS support** for web applications
- **Auto-generated documentation** at `/docs`

### **External API Integration:**
- **Real-time data fetching** from external APIs
- **Authentication** with API keys
- **Custom endpoints** configuration
- **Data validation** and quality checks
- **Fallback mechanisms** to file-based loading
- **Connection monitoring** and status reporting

### **REST API Endpoints:**
```bash
# Health check
GET http://localhost:8000/api/health

# Excel files
GET http://localhost:8000/api/excel
GET http://localhost:8000/api/excel/{filename}

# Database
GET http://localhost:8000/api/database
GET http://localhost:8000/api/database/{table}

# Merged data
GET http://localhost:8000/api/merged

# Search
GET http://localhost:8000/api/search?table={table}&search_term={term}
```

### **External API Configuration:**
```python
api_config = {
    'base_url': 'https://api.example.com',
    'api_key': 'your_api_key',
    'timeout': 30,
    'endpoints': {
        'old_pricing': '/api/v1/pricing/old',
        'new_pricing': '/api/v1/pricing/new',
        'trade_metadata': '/api/v1/trades/metadata',
        'funding_reference': '/api/v1/funding/reference'
    }
}
```

### **Testing APIs:**
```bash
# Test REST API
python api_client.py

# Test external API connection
python test_api_connection.py --config api_config.json
```

---

## 📊 Dashboard Features

### **Data Source Selection:**
- **Files**: Upload Excel files directly
- **API**: Connect to external APIs
- **Auto-detect**: Automatically choose best source

### **Interactive Visualizations:**
- Mismatch distribution charts
- Diagnosis comparison (Rule-based vs ML)
- PV vs Delta scatter plots
- Trend analysis
- Statistical summaries

### **Real-time Monitoring:**
- API connection status
- Data quality validation
- Processing progress indicators
- Export capabilities

---

## 👨‍💼 Agents in Action

| Agent | Role | Data Source |
|-------|------|-------------|
| **DataLoaderAgent** | Loads and merges pricing, trade, and funding data | Files |
| **APIDataLoaderAgent** | Fetches data from external APIs | APIs |
| **HybridDataLoaderAgent** | Combines file and API loading with fallback | Files + APIs |
| **ReconAgent** | Flags mismatches in PV and Delta values | All |
| **AnalyzerAgent** | Provides funding-aware diagnostic tags | All |
| **MLDiagnoserAgent** | ML-powered diagnosis predictions | All |
| **NarratorAgent** | Summarizes results and generates reports | All |

---

## 🧠 ML Integration

### **Features:**
- **CatBoost model** for diagnosis prediction
- **Automatic training** using rule-based diagnoses as labels
- **Model persistence** for reuse
- **Confidence scoring** and validation
- **Comparison analysis** between ML and rule-based results

### **Model Architecture:**
- **Features**: PV/Delta values, product types, funding curves
- **Target**: Rule-based diagnosis labels
- **Algorithm**: CatBoost with categorical feature support
- **Validation**: Cross-validation with business rules

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

### **Technical Improvements:**
- **Database integration** for persistent storage
- **Microservices architecture** for scalability
- **Containerization** with Docker
- **CI/CD pipeline** for automated deployment
- **Performance optimization** for large datasets

---

## 📞 Support & Documentation

### **Documentation:**
- 📖 [Usage Guide](docs/USAGE_GUIDE.md) - Detailed usage instructions
- 🏗️ [Architecture](docs/ARCHITECTURE.md) - System design and components
- 🔧 [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- 📊 [Diagrams](docs/DIAGRAMS.md) - System diagrams and flowcharts

### **Testing:**
```bash
# Test API connection
python test_api_connection.py --config api_config.json

# Run dashboard
python run_dashboard.py

# Run pipeline
python pipeline.py
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