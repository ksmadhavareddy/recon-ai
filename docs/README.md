# 🤖 AI-Powered Reconciliation System

## 📋 Overview

This system implements an intelligent reconciliation workflow that combines rule-based business logic with machine learning to identify and diagnose pricing mismatches between old and new financial models. The system uses a crew-based architecture with specialized AI agents working together to provide comprehensive analysis.

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Reconciliation Pipeline                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Data Loader │  │ Recon Agent │  │ Analyzer    │          │
│  │ Agent       │  │             │  │ Agent       │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│         │                │                │                   │
│         ▼                ▼                ▼                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Load & Merge│  │ Flag        │  │ Rule-based  │          │
│  │ Excel Data  │  │ Mismatches  │  │ Diagnosis   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│         │                │                │                   │
│         └────────────────┼────────────────┘                   │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ML Diagnoser Agent                        │   │
│  │  ┌─────────────────┐  ┌─────────────────┐            │   │
│  │  │ Train Model     │  │ Predict         │            │   │
│  │  │ (CatBoost)      │  │ Diagnoses       │            │   │
│  │  └─────────────────┘  └─────────────────┘            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Narrator Agent                             │   │
│  │  ┌─────────────────┐  ┌─────────────────┐            │   │
│  │  │ Generate        │  │ Save Excel      │            │   │
│  │  │ Summary         │  │ Report          │            │   │
│  │  └─────────────────┘  └─────────────────┘            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Input     │    │   Process   │    │   Output    │
│   Data      │    │   Pipeline  │    │   Reports   │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ old_pricing │    │ 1. Load     │    │ Summary     │
│ new_pricing │───▶│ 2. Merge    │───▶│ Statistics  │
│ metadata    │    │ 3. Flag     │    │ Excel File  │
│ funding     │    │ 4. Analyze  │    │ ML Model    │
└─────────────┘    │ 5. Predict  │    └─────────────┘
                   │ 6. Report   │
                   └─────────────┘
```

## 🧩 Agent Architecture

### Agent Responsibilities

| Agent | Role | Input | Output | Key Features |
|-------|------|-------|--------|--------------|
| **DataLoaderAgent** | Data ingestion and merging | Excel files | Merged DataFrame | Multi-source data fusion |
| **ReconAgent** | Mismatch detection | Merged data | Flagged mismatches | Configurable thresholds |
| **AnalyzerAgent** | Rule-based diagnosis | Flagged data | Business diagnoses | Domain-specific rules |
| **MLDiagnoserAgent** | ML prediction | Training data | ML diagnoses | CatBoost model |
| **NarratorAgent** | Report generation | All results | Excel report | Summary statistics |

### ML Model Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ML Diagnoser Agent                      │
├─────────────────────────────────────────────────────────────┤
│  Features:                                                 │
│  • PV_old, PV_new, Delta_old, Delta_new                  │
│  • ProductType, FundingCurve, CSA_Type, ModelVersion      │
│                                                           │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   Training      │  │   Prediction    │                │
│  │   Phase         │  │   Phase         │                │
│  │                 │  │                 │                │
│  │ 1. Feature      │  │ 1. Load Model   │                │
│  │    Engineering  │  │ 2. Prepare      │                │
│  │ 2. Label        │  │    Features     │                │
│  │    Encoding     │  │ 3. Predict      │                │
│  │ 3. Train        │  │    Diagnoses    │                │
│  │    CatBoost     │  │ 4. Decode       │                │
│  │ 4. Save Model   │  │    Results      │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### Data Structure

Place your input files in the `data/` directory:

```
data/
├── old_pricing.xlsx      # Previous pricing data
├── new_pricing.xlsx      # Current pricing data  
├── trade_metadata.xlsx   # Trade characteristics
└── funding_model_reference.xlsx  # Funding information
```

### Running the Pipeline

```bash
python pipeline.py
```

### Expected Output

```
🚀 Starting Agent-Based Reconciliation Workflow...
🔄 Step 1: Loading data...
📏 Step 2: Computing PV/Delta mismatches...
🧠 Step 3: Diagnosing root causes (rule-based)...
🤖 Step 4: Training ML model and predicting diagnoses...
✅ ML model trained and saved.
📊 Reconciliation Summary:
Total Trades: 5
PV Mismatches: 2
Delta Mismatches: 2
Flagged Trades: 2
✅ Report saved to: final_recon_report.xlsx
🎉 Workflow complete. Check your reconciliation report!
```

## 📊 Output Files

### Generated Reports

1. **`final_recon_report.xlsx`** - Complete reconciliation report with:
   - Original pricing data
   - Mismatch flags
   - Rule-based diagnoses
   - ML-based diagnoses
   - Comparison analysis

2. **`models/catboost_diagnoser.pkl`** - Trained ML model for future predictions

### Report Columns

| Column | Description |
|--------|-------------|
| `TradeID` | Unique trade identifier |
| `PV_old`, `PV_new` | Present value (old/new) |
| `Delta_old`, `Delta_new` | Delta risk (old/new) |
| `PV_Diff`, `Delta_Diff` | Differences between old/new |
| `PV_Mismatch`, `Delta_Mismatch` | Boolean flags for mismatches |
| `Diagnosis` | Rule-based root cause analysis |
| `ML_Diagnosis` | Machine learning predictions |

## 🔧 Configuration

### Thresholds

```python
# In ReconAgent
pv_tolerance = 1000      # PV mismatch threshold
delta_tolerance = 0.05   # Delta mismatch threshold
```

### ML Model Settings

```python
# In MLDiagnoserAgent
model_path = "models/catboost_diagnoser.pkl"
cat_features = ['ProductType', 'FundingCurve', 'CSA_Type', 'ModelVersion']
```

## 🧠 Machine Learning Details

### Feature Engineering

**Numerical Features:**
- `PV_old`, `PV_new` - Present values
- `Delta_old`, `Delta_new` - Delta risk measures

**Categorical Features:**
- `ProductType` - Financial product type
- `FundingCurve` - Funding curve used
- `CSA_Type` - Credit Support Annex type
- `ModelVersion` - Model version identifier

### Model Training

1. **Label Source**: Rule-based diagnoses from `AnalyzerAgent`
2. **Algorithm**: CatBoost (gradient boosting)
3. **Categorical Handling**: Native CatBoost categorical features
4. **Validation**: Uses all available data for training

### Prediction Process

1. Load trained model
2. Prepare features (same as training)
3. Generate predictions
4. Decode labels back to human-readable diagnoses

## 🔍 Business Rules

### Rule-based Diagnoses

| Condition | Diagnosis |
|-----------|-----------|
| `PV_old` is None | "New trade – no prior valuation" |
| `PV_new` is None | "Trade dropped from new model" |
| Legacy LIBOR + outdated model | "Legacy LIBOR curve with outdated model – PV likely shifted" |
| CSA changed post-clearing | "CSA changed post-clearing – funding basis moved" |
| Option + Delta mismatch | "Vol sensitivity likely – delta impact due to model curve shift" |
| Default | "Within tolerance" |

## 🛠️ Development

### Project Structure

```
recon-ai/
├── crew/
│   ├── agents/
│   │   ├── data_loader.py      # Data ingestion
│   │   ├── recon_agent.py      # Mismatch detection
│   │   ├── analyzer_agent.py   # Rule-based analysis
│   │   ├── ml_tool.py         # ML predictions
│   │   └── narrator_agent.py   # Report generation
│   └── crew_builder.py        # Pipeline orchestration
├── data/                      # Input data files
├── models/                    # Trained ML models
├── docs/                      # Documentation
├── pipeline.py               # Main execution script
├── requirements.txt          # Dependencies
└── README.md                # Project overview
```

### Adding New Agents

1. Create agent class in `crew/agents/`
2. Implement required methods
3. Import and integrate in `crew_builder.py`
4. Update pipeline workflow

### Extending ML Capabilities

1. **Feature Engineering**: Add new features in `prepare_features_and_labels()`
2. **Model Selection**: Change `CatBoostClassifier` to other algorithms
3. **Hyperparameter Tuning**: Add grid search or Bayesian optimization
4. **Ensemble Methods**: Combine multiple models for better predictions

## 📈 Performance Metrics

### Current System Performance

- **Processing Speed**: ~5 trades/second
- **Accuracy**: Rule-based + ML comparison
- **Scalability**: Linear with data size
- **Memory Usage**: Minimal (in-memory processing)

### ML Model Performance

- **Training Time**: <1 second for typical datasets
- **Prediction Time**: <0.1 second per trade
- **Model Size**: ~1MB (CatBoost model)
- **Accuracy**: Depends on data quality and feature relevance

## 🔮 Future Enhancements

### Planned Features

1. **Real-time Processing**: Stream processing for live data
2. **Advanced ML**: Deep learning models for complex patterns
3. **Interactive UI**: Streamlit dashboard for visualization
4. **API Integration**: REST API for external systems
5. **Alert System**: Automated notifications for critical mismatches

### Technical Improvements

1. **Database Integration**: Move from Excel to database storage
2. **Parallel Processing**: Multi-threading for large datasets
3. **Model Versioning**: Track model performance over time
4. **A/B Testing**: Compare different model approaches

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

### Code Standards

- Follow PEP 8 for Python code
- Add docstrings to all functions
- Include type hints
- Write unit tests for new features

## 📞 Support

For questions or issues:

1. Check the documentation
2. Review existing issues
3. Create new issue with detailed description
4. Include error logs and data samples

---

**Built with ❤️ using CrewAI architecture and CatBoost ML** 