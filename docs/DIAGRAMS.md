# 📊 System Diagrams

## Overview

This document contains comprehensive diagrams for the AI-Powered Reconciliation System, including architecture, data flow, and component interactions, featuring the **dynamic label generation system**.

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Input Layer"
        A[old_pricing.xlsx]
        B[new_pricing.xlsx]
        C[trade_metadata.xlsx]
        D[funding_model_reference.xlsx]
        E[API Endpoints]
    end
    
    subgraph "Agent Layer"
        F[UnifiedDataLoaderAgent]
        G[ReconAgent]
        H[AnalyzerAgent]
        I[DynamicLabelGenerator]
        J[MLDiagnoserAgent]
        K[NarratorAgent]
    end
    
    subgraph "Data Processing"
        L[Merged DataFrame]
        M[Flagged Mismatches]
        N[Dynamic Rule-based Diagnoses]
        O[Dynamic Labels]
        P[ML Predictions with Dynamic Labels]
    end
    
    subgraph "Output Layer"
        Q[Excel Report]
        R[Trained ML Model]
        S[Summary Statistics]
        T[Dynamic Label Patterns]
    end
    
    A --> F
    B --> F
    C --> F
    D --> F
    E --> F
    F --> L
    L --> G
    G --> M
    M --> H
    H --> N
    N --> I
    I --> O
    O --> J
    J --> P
    P --> K
    K --> Q
    K --> S
    J --> R
    I --> T
```

## Dynamic Label Generation Architecture

### Core Components
```mermaid
graph TB
    subgraph "Dynamic Label Generator"
        A[Business Rules Engine]
        B[Pattern Discovery]
        C[Domain Knowledge]
        D[Historical Analysis]
    end
    
    subgraph "Label Generation Process"
        E[Rule Application]
        F[Pattern Analysis]
        G[Knowledge Integration]
        H[Historical Learning]
    end
    
    subgraph "Output"
        I[Dynamic Labels]
        J[Pattern Statistics]
        K[Historical Patterns]
    end
    
    A --> E
    B --> F
    C --> G
    D --> H
    E --> I
    F --> I
    G --> I
    H --> I
    F --> J
    H --> K
```

### Business Rules Engine
```mermaid
graph LR
    subgraph "Business Rules"
        A[PV Rules]
        B[Delta Rules]
        C[Priority System]
        D[Category Classification]
    end
    
    subgraph "Rule Application"
        E[Condition Evaluation]
        F[Safe Expression Parsing]
        G[Priority Sorting]
        H[Label Assignment]
    end
    
    A --> E
    B --> E
    C --> G
    D --> H
    E --> F
    F --> G
    G --> H
```

### Pattern Discovery Process
```mermaid
graph TB
    subgraph "Data Analysis"
        A[PV Patterns]
        B[Delta Patterns]
        C[Temporal Patterns]
        D[Product Patterns]
    end
    
    subgraph "Pattern Processing"
        E[Threshold Analysis]
        F[Trend Detection]
        G[Anomaly Detection]
        H[Category Assignment]
    end
    
    subgraph "Output"
        I[Discovered Patterns]
        J[Pattern Statistics]
        K[New Labels]
    end
    
    A --> E
    B --> F
    C --> G
    D --> H
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J
    I --> K
```

## Data Flow Architecture

### Phase 1: Data Ingestion
```mermaid
sequenceDiagram
    participant U as User
    participant UDLA as UnifiedDataLoaderAgent
    participant FS as File System
    participant API as API Endpoints
    
    U->>UDLA: Initialize(data_dir, api_config)
    alt File-based loading
        UDLA->>FS: Load old_pricing.xlsx
        FS-->>UDLA: old_pricing DataFrame
        UDLA->>FS: Load new_pricing.xlsx
        FS-->>UDLA: new_pricing DataFrame
        UDLA->>FS: Load trade_metadata.xlsx
        FS-->>UDLA: metadata DataFrame
        UDLA->>FS: Load funding_model_reference.xlsx
        FS-->>UDLA: funding DataFrame
    else API-based loading
        UDLA->>API: Fetch old_pricing data
        API-->>UDLA: old_pricing DataFrame
        UDLA->>API: Fetch new_pricing data
        API-->>UDLA: new_pricing DataFrame
        UDLA->>API: Fetch trade_metadata data
        API-->>UDLA: metadata DataFrame
        UDLA->>API: Fetch funding_reference data
        API-->>UDLA: funding DataFrame
    end
    UDLA->>UDLA: Merge all DataFrames on TradeID
    UDLA-->>U: Merged DataFrame
```

### Phase 2: Mismatch Detection
```mermaid
sequenceDiagram
    participant U as User
    participant RA as ReconAgent
    participant DF as DataFrame
    
    U->>RA: Initialize(pv_tolerance, delta_tolerance)
    U->>RA: apply(df)
    RA->>DF: Calculate PV_Diff = PV_new - PV_old
    RA->>DF: Calculate Delta_Diff = Delta_new - Delta_old
    RA->>DF: Flag PV_Mismatch if |PV_Diff| > pv_tolerance
    RA->>DF: Flag Delta_Mismatch if |Delta_Diff| > delta_tolerance
    RA->>DF: Set Any_Mismatch = PV_Mismatch OR Delta_Mismatch
    RA-->>U: DataFrame with mismatch flags
```

### Phase 3: Dynamic Analysis & Prediction
```mermaid
sequenceDiagram
    participant U as User
    participant AA as AnalyzerAgent
    participant DLG as DynamicLabelGenerator
    participant MLA as MLDiagnoserAgent
    participant DF as DataFrame
    
    U->>AA: Initialize(label_generator)
    U->>AA: apply(df)
    AA->>DF: Apply dynamic business rules
    AA->>DF: Generate PV_Diagnosis and Delta_Diagnosis
    AA->>DLG: update_from_analysis(df, analyzer_output)
    DLG->>DLG: Update historical patterns
    DLG->>DLG: Save patterns to config file
    AA-->>U: DataFrame with dynamic diagnoses
    
    U->>MLA: Initialize(model_path)
    U->>MLA: train(df, label_col='PV_Diagnosis')
    MLA->>DLG: generate_labels(df, include_discovered=True)
    DLG-->>MLA: Dynamic labels for training
    MLA->>MLA: Train LightGBM model with dynamic labels
    MLA->>MLA: Save model and metadata
    MLA-->>U: Training results
    
    U->>MLA: predict(df, label_col='PV_Diagnosis')
    MLA->>DLG: generate_labels(df, include_discovered=True)
    DLG-->>MLA: Dynamic labels for prediction
    MLA->>MLA: Make predictions with dynamic labels
    MLA-->>U: Predicted diagnoses
```

### Phase 4: Report Generation
```mermaid
sequenceDiagram
    participant U as User
    participant NA as NarratorAgent
    participant DF as DataFrame
    participant FS as File System
    
    U->>NA: generate_report(df, output_path)
    NA->>DF: Extract all columns including dynamic labels
    NA->>NA: Calculate summary statistics
    NA->>NA: Generate Excel report with dynamic labels
    NA->>FS: Save final_recon_report.xlsx
    NA-->>U: Report path and summary statistics
```

## Business Rules Flow

### PV Rule Application
```mermaid
graph TD
    A[Start PV Analysis] --> B{PV_old is None?}
    B -->|Yes| C[Label: New trade – no prior valuation]
    B -->|No| D{PV_new is None?}
    D -->|Yes| E[Label: Trade dropped from new model]
    D -->|No| F{FundingCurve == 'USD-LIBOR' and ModelVersion != 'v2024.3'?}
    F -->|Yes| G[Label: Legacy LIBOR curve with outdated model]
    F -->|No| H{CSA_Type == 'Cleared' and PV_Mismatch == True?}
    H -->|Yes| I[Label: CSA changed post-clearing]
    H -->|No| J{PV_Mismatch == False?}
    J -->|Yes| K[Label: Within tolerance]
    J -->|No| L[Label: Default diagnosis]
    
    C --> M[End]
    E --> M
    G --> M
    I --> M
    K --> M
    L --> M
```

### Delta Rule Application
```mermaid
graph TD
    A[Start Delta Analysis] --> B{ProductType == 'Option' and Delta_Mismatch == True?}
    B -->|Yes| C[Label: Vol sensitivity likely – delta impact]
    B -->|No| D{Delta_Mismatch == False?}
    D -->|Yes| E[Label: Within tolerance]
    D -->|No| F[Label: Default diagnosis]
    
    C --> G[End]
    E --> G
    F --> G
```

## Pattern Discovery Flow

### PV Pattern Discovery
```mermaid
graph TD
    A[Analyze PV Data] --> B{PV_Diff > threshold?}
    B -->|Yes| C[Identify large PV differences]
    B -->|No| D{PV_Diff < -threshold?}
    D -->|Yes| E[Identify negative PV shifts]
    D -->|No| F[No significant pattern]
    
    C --> G[Create PV pattern label]
    E --> H[Create PV pattern label]
    F --> I[No pattern created]
    
    G --> J[Add to discovered patterns]
    H --> J
    I --> K[End]
    J --> K
```

### Delta Pattern Discovery
```mermaid
graph TD
    A[Analyze Delta Data] --> B{Delta_Diff > threshold?}
    B -->|Yes| C[Identify large Delta differences]
    B -->|No| D{Delta_Diff < -threshold?}
    D -->|Yes| E[Identify negative Delta shifts]
    D -->|No| F[No significant pattern]
    
    C --> G[Create Delta pattern label]
    E --> H[Create Delta pattern label]
    F --> I[No pattern created]
    
    G --> J[Add to discovered patterns]
    H --> J
    I --> K[End]
    J --> K
```

## ML Model Integration

### Training with Dynamic Labels
```mermaid
graph TD
    A[Start Training] --> B[Load training data]
    B --> C[Generate dynamic labels]
    C --> D[Prepare features]
    D --> E[Encode labels]
    E --> F[Train LightGBM model]
    F --> G[Update label generator]
    G --> H[Save model and metadata]
    H --> I[End Training]
```

### Prediction with Dynamic Labels
```mermaid
graph TD
    A[Start Prediction] --> B[Load trained model]
    B --> C[Generate dynamic labels]
    C --> D[Prepare features]
    D --> E[Make predictions]
    E --> F[Decode labels]
    F --> G[Return predictions]
    G --> H[End Prediction]
```

## Domain Knowledge Categories

### Trade Lifecycle Patterns
```mermaid
graph LR
    A[Trade Lifecycle] --> B[New trade – no prior valuation]
    A --> C[Trade dropped from new model]
    A --> D[Trade amended with new terms]
    A --> E[Trade matured or expired]
```

### Curve/Model Patterns
```mermaid
graph LR
    A[Curve/Model] --> B[Legacy LIBOR curve with outdated model]
    A --> C[SOFR transition impact]
    A --> D[Model version update]
    A --> E[Curve interpolation changed]
```

### Funding/CSA Patterns
```mermaid
graph LR
    A[Funding/CSA] --> B[CSA changed post-clearing]
    A --> C[Collateral threshold changed]
    A --> D[New clearing house]
    A --> E[Bilateral to cleared transition]
```

### Volatility Patterns
```mermaid
graph LR
    A[Volatility] --> B[Vol sensitivity likely]
    A --> C[Option pricing model update]
    A --> D[Market volatility spike]
    A --> E[Volatility smile adjustment]
```

## Configuration Management

### Business Rules Configuration
```mermaid
graph TD
    A[Load Configuration] --> B{Config file exists?}
    B -->|Yes| C[Load from file]
    B -->|No| D[Use default rules]
    C --> E[Parse business rules]
    D --> F[Initialize default rules]
    E --> G[Validate rules]
    F --> G
    G --> H[Apply rules to analyzer]
    H --> I[Configuration complete]
```

### Pattern Discovery Configuration
```mermaid
graph TD
    A[Start Pattern Discovery] --> B[Set discovery parameters]
    B --> C[Analyze PV patterns]
    C --> D[Analyze Delta patterns]
    D --> E[Analyze temporal patterns]
    E --> F[Analyze product patterns]
    F --> G[Combine discovered patterns]
    G --> H[Update historical patterns]
    H --> I[Save patterns to config]
    I --> J[Pattern discovery complete]
```

## Error Handling Flow

### Dynamic Label Generation Errors
```mermaid
graph TD
    A[Generate Labels] --> B{Business rules valid?}
    B -->|No| C[Log error: Invalid business rules]
    B -->|Yes| D{Pattern discovery successful?}
    D -->|No| E[Log error: Pattern discovery failed]
    D -->|Yes| F{Label generation successful?}
    F -->|No| G[Log error: Label generation failed]
    F -->|Yes| H[Return generated labels]
    
    C --> I[Use fallback labels]
    E --> I
    G --> I
    I --> J[End with fallback]
    H --> K[End successfully]
```

### Business Rule Evaluation Errors
```mermaid
graph TD
    A[Evaluate Condition] --> B{Parse condition safely?}
    B -->|No| C[Log error: Invalid condition syntax]
    B -->|Yes| D{Evaluate condition successfully?}
    D -->|No| E[Log error: Condition evaluation failed]
    D -->|Yes| F[Return evaluation result]
    
    C --> G[Use default evaluation]
    E --> G
    G --> H[End with default]
    F --> I[End successfully]
```

## Performance Monitoring

### System Performance Metrics
```mermaid
graph TD
    A[Monitor Performance] --> B[Track processing time]
    B --> C[Monitor memory usage]
    C --> D[Track pattern discovery rate]
    D --> E[Monitor label generation speed]
    E --> F[Track ML model performance]
    F --> G[Generate performance report]
    G --> H[End monitoring]
```

### Dynamic Label Performance
```mermaid
graph TD
    A[Monitor Dynamic Labels] --> B[Track label generation time]
    B --> C[Monitor pattern discovery rate]
    C --> D[Track business rule application]
    D --> E[Monitor historical learning]
    E --> F[Track label diversity]
    F --> G[Generate label statistics]
    G --> H[End monitoring]
```

## Integration Examples

### Complete Workflow Integration
```mermaid
graph TD
    A[Start Workflow] --> B[Load Data]
    B --> C[Detect Mismatches]
    C --> D[Apply Dynamic Analysis]
    D --> E[Generate Dynamic Labels]
    E --> F[Train ML Model]
    F --> G[Make Predictions]
    G --> H[Generate Report]
    H --> I[End Workflow]
```

### Custom Business Rules Integration
```mermaid
graph TD
    A[Add Custom Rule] --> B[Validate rule syntax]
    B --> C[Add to business rules]
    C --> D[Update analyzer agent]
    D --> E[Test rule application]
    E --> F[Deploy rule]
    F --> G[Monitor rule performance]
    G --> H[End integration]
```

### ML Model Integration
```mermaid
graph TD
    A[Initialize ML Agent] --> B[Load dynamic labels]
    B --> C[Prepare features]
    C --> D[Train model]
    D --> E[Make predictions]
    E --> F[Update label generator]
    F --> G[Save model]
    G --> H[End integration]
```

## Future Enhancements

### Advanced Pattern Recognition
```mermaid
graph TD
    A[Advanced Patterns] --> B[ML-based pattern discovery]
    B --> C[Deep learning integration]
    C --> D[Ensemble methods]
    D --> E[Real-time pattern recognition]
    E --> F[End enhancement]
```

### Real-time Streaming
```mermaid
graph TD
    A[Real-time Processing] --> B[Stream data ingestion]
    B --> C[Real-time analysis]
    C --> D[Live pattern discovery]
    D --> E[Instant label generation]
    E --> F[End enhancement]
```

### Advanced Analytics
```mermaid
graph TD
    A[Advanced Analytics] --> B[Statistical analysis]
    B --> C[Trend detection]
    C --> D[Anomaly detection]
    D --> E[Predictive analytics]
    E --> F[End enhancement]
``` 