# 🤖 AI-Powered Reconciliation System

## 📋 Overview

This system implements an intelligent reconciliation workflow that combines **dynamic rule-based business logic** with machine learning to identify and diagnose pricing mismatches between old and new financial models. The system uses a crew-based architecture with specialized AI agents working together to provide comprehensive analysis, featuring **real-time dynamic label generation** for adaptive diagnosis scenarios.

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
│  │ Load & Merge│  │ Flag        │  │ Dynamic     │          │
│  │ Excel Data  │  │ Mismatches  │  │ Rule-based  │          │
│  └─────────────┘  └─────────────┘  │ Diagnosis   │          │
│         │                │          └─────────────┘          │
│         └────────────────┼────────────────┘                   │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Dynamic Label Generator                   │   │
│  │  ┌─────────────────┐  ┌─────────────────┐            │   │
│  │  │ Business Rules  │  │ Pattern         │            │   │
│  │  │ Engine          │  │ Discovery       │            │   │
│  │  └─────────────────┘  └─────────────────┘            │   │
│  │  ┌─────────────────┐  ┌─────────────────┐            │   │
│  │  │ Domain          │  │ Historical      │            │   │
│  │  │ Knowledge       │  │ Analysis        │            │   │
│  │  └─────────────────┘  └─────────────────┘            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ML Diagnoser Agent                        │   │
│  │  ┌─────────────────┐  ┌─────────────────┐            │   │
│  │  │ Train Model     │  │ Predict         │            │   │
│  │  │ (LightGBM)      │  │ Diagnoses       │            │   │
│  │  │ with Dynamic    │  │ with Dynamic    │            │   │
│  │  │ Labels          │  │ Labels          │            │   │
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
└─────────────┘    │ 5. Generate │    │ Dynamic     │
                   │    Labels   │    │ Labels      │
                   │ 6. Predict  │    └─────────────┘
                   │ 7. Report   │
                   └─────────────┘
```

## 🧩 Agent Architecture

### Agent Responsibilities

| Agent | Role | Input | Output | Key Features |
|-------|------|-------|--------|--------------|
| **UnifiedDataLoaderAgent** | Data ingestion and merging | Files, APIs, Auto-detect, Hybrid | Merged DataFrame | Multi-source data fusion with auto-load functionality |
| **ReconAgent** | Mismatch detection | Merged data | Flagged mismatches | Configurable thresholds |
| **AnalyzerAgent** | **Dynamic rule-based diagnosis** | Flagged data | **Dynamic business diagnoses** | **Dynamic business rules, safe condition evaluation** |
| **DynamicLabelGenerator** | **Real-time label generation** | Analysis data | **Dynamic diagnosis labels** | **Pattern discovery, business rules, domain knowledge** |
| **MLDiagnoserAgent** | ML prediction with dynamic labels | Training data | ML diagnoses | **LightGBM model with dynamic label integration** |
| **NarratorAgent** | Report generation | All results | Excel report | Summary statistics |

### Dynamic Label Generation Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Dynamic Label Generator                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │ Business Rules  │  │ Pattern         │                │
│  │ Engine          │  │ Discovery       │                │
│  │                 │  │                 │                │
│  │ • PV Rules      │  │ • PV Patterns   │                │
│  │ • Delta Rules   │  │ • Delta Patterns│                │
│  │ • Priority      │  │ • Temporal      │                │
│  │ • Categories    │  │ • Product       │                │
│  └─────────────────┘  └─────────────────┘                │
│           │                      │                        │
│           └──────────┬───────────┘                        │
│                      ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Label Generation                      │   │
│  │  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ Domain          │  │ Historical      │        │   │
│  │  │ Knowledge       │  │ Analysis        │        │   │
│  │  │                 │  │                 │        │   │
│  │  │ • Trade         │  │ • Pattern       │        │   │
│  │  │   Lifecycle     │  │   Frequency     │        │   │
│  │  │ • Curve/Model   │  │ • Label         │        │   │
│  │  │ • Funding/CSA   │  │   Statistics    │        │   │
│  │  │ • Volatility    │  │ • Trend         │        │   │
│  │  │ • Data Quality  │  │   Analysis      │        │   │
│  │  └─────────────────┘  └─────────────────┘        │   │
│  └─────────────────────────────────────────────────────┘   │
│                      │                                    │
│                      ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Dynamic Labels                        │   │
│  │  • Real-time generation                           │   │
│  │  • Business rule application                      │   │
│  │  • Pattern-based discovery                       │   │
│  │  • Historical learning                           │   │
│  │  • Domain knowledge integration                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### ML Model Architecture with Dynamic Labels

```
┌─────────────────────────────────────────────────────────────┐
│                ML Diagnoser Agent                         │
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
│  │ 2. Dynamic      │  │    Features     │                │
│  │    Label        │  │ 3. Predict      │                │
│  │    Generation   │  │    Diagnoses    │                │
│  │ 3. Label        │  │ 4. Decode       │                │
│  │    Encoding     │  │    Results      │                │
│  │ 4. Train        │  │ 5. Update       │                │
│  │    LightGBM     │  │    Labels       │                │
│  │ 5. Save Model   │  └─────────────────┘                │
│  └─────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
```

### Business Rules Categories

The dynamic label generation system supports comprehensive business rule categories:

#### **Trade Lifecycle**
- New trade – no prior valuation
- Trade dropped from new model
- Trade amended with new terms
- Trade matured or expired

#### **Curve/Model**
- Legacy LIBOR curve with outdated model
- SOFR transition impact – curve basis changed
- Model version update – methodology changed
- Curve interpolation changed – end points affected

#### **Funding/CSA**
- CSA changed post-clearing – funding basis moved
- Collateral threshold changed – funding cost shifted
- New clearing house – margin requirements different
- Bilateral to cleared transition – funding curve changed

#### **Volatility**
- Vol sensitivity likely – delta impact due to model curve shift
- Option pricing model update – volatility surface changed
- Market volatility spike – delta hedging impact
- Volatility smile adjustment – skew changes

#### **Data Quality**
- Missing pricing data – incomplete valuation
- Data format mismatch – parsing errors
- Validation failures – business rule violations
- Timestamp inconsistencies – temporal misalignment

#### **Market Events**
- Market disruption – liquidity impact
- Regulatory change – compliance requirements
- Central bank action – rate environment shift
- Credit event – counterparty risk change

## 🔄 Dynamic Label Generation Process

### 1. **Business Rules Application**
```python
# Example business rule
{
    "condition": "FundingCurve == 'USD-LIBOR' and ModelVersion != 'v2024.3'",
    "label": "Legacy LIBOR curve with outdated model – PV likely shifted",
    "priority": 2,
    "category": "curve_model"
}
```

### 2. **Pattern Discovery**
- **PV Patterns**: Analyzes PV differences and trends
- **Delta Patterns**: Identifies delta sensitivity patterns
- **Temporal Patterns**: Time-based analysis and seasonality
- **Product Patterns**: Product-specific diagnosis patterns

### 3. **Domain Knowledge Integration**
- **Industry Standards**: Best practices and regulatory requirements
- **Market Knowledge**: Current market conditions and trends
- **Historical Context**: Previous analysis patterns and outcomes

### 4. **Historical Learning**
- **Pattern Frequency**: Tracks how often patterns occur
- **Label Statistics**: Maintains label usage statistics
- **Trend Analysis**: Identifies emerging patterns and trends

## 🎯 Key Features

### **Dynamic Label Generation**
- **Real-time Creation**: Labels generated based on current data and business rules
- **Pattern Discovery**: Automatically identifies new diagnosis patterns
- **Business Rule Application**: Applies configurable rules dynamically
- **Historical Learning**: Incorporates patterns from previous analyses
- **Domain Knowledge**: Uses industry-specific diagnosis categories

### **Enhanced Analyzer Agent**
- **Dynamic Rule Application**: Applies business rules dynamically
- **Safe Condition Evaluation**: Safely evaluates string-based conditions
- **Rule Management**: Add, modify, and manage business rules
- **Integration**: Updates the label generator with analysis results

### **ML Integration**
- **Dynamic Labels**: ML model uses dynamically generated labels
- **Adaptive Training**: Model adapts to new patterns and rules
- **Real-time Learning**: Incorporates new diagnoses automatically

### **Configuration Management**
- **Business Rules**: Configurable rules for diagnosis generation
- **Pattern Discovery**: Automatic pattern identification and learning
- **Domain Knowledge**: Industry-specific diagnosis categories
- **Historical Tracking**: Pattern and label frequency management

## 🚀 Performance Benefits

### **Adaptability**
- **Real-time Adaptation**: System adapts to changing business rules
- **Pattern Learning**: Automatically learns new diagnosis patterns
- **Market Responsiveness**: Responds to market condition changes
- **Regulatory Compliance**: Adapts to regulatory requirement changes

### **Scalability**
- **Dynamic Label Generation**: Scales with data volume and complexity
- **Pattern Discovery**: Efficient pattern identification algorithms
- **Business Rule Management**: Flexible rule configuration and application
- **Historical Learning**: Efficient pattern and frequency tracking

### **Accuracy**
- **Business Rule Validation**: Ensures rule-based accuracy
- **Pattern Validation**: Validates discovered patterns
- **ML Model Adaptation**: Model adapts to new patterns and rules
- **Cross-validation**: Validates results across multiple approaches 