# 🛠️ Tools and Requirements Documentation

This document provides detailed descriptions of all tools, libraries, and dependencies used in the AI Reconciliation System.

## 📦 Core Requirements

### 🎯 Main Application (`requirements.txt`)

#### **Web Framework & UI**
- **`streamlit>=1.28.0`** - Modern web framework for creating interactive data applications
  - **Purpose**: Powers the main dashboard interface with real-time data visualization
  - **Features**: Drag-and-drop file upload, interactive charts, responsive design
  - **Usage**: Main dashboard (`app.py`, `run_dashboard.py`)

#### **Data Processing & Analysis**
- **`pandas>=1.5.0`** - Powerful data manipulation and analysis library
  - **Purpose**: Core data processing for reconciliation analysis
  - **Features**: Excel file reading, data filtering, statistical calculations
  - **Usage**: Data loading, cleaning, and transformation across all modules

- **`numpy>=1.24.0`** - Fundamental package for scientific computing
  - **Purpose**: Numerical operations and array manipulations
  - **Features**: Fast array operations, mathematical functions
  - **Usage**: ML model preprocessing, statistical calculations

#### **Visualization & Charts**
- **`plotly>=5.15.0`** - Interactive plotting library for web-based visualizations
  - **Purpose**: Creates interactive charts and graphs in the dashboard
  - **Features**: Scatter plots, bar charts, pie charts, hover interactions
  - **Usage**: Dashboard visualizations (`app.py`)

#### **File Handling**
- **`openpyxl>=3.1.0`** - Library for reading/writing Excel files
  - **Purpose**: Handles Excel file operations for data import/export
  - **Features**: Read/write .xlsx files, preserve formatting
  - **Usage**: File upload processing, result export

#### **Machine Learning**
- **`lightgbm>=4.0.0`** - Gradient boosting framework for ML models
  - **Purpose**: Powers the ML-based diagnosis system
  - **Features**: Fast training, high accuracy, feature importance
  - **Usage**: ML diagnoser model (`models/lightgbm_diagnoser.txt`)

- **`scikit-learn>=1.3.0`** - Comprehensive ML library
  - **Purpose**: Data preprocessing, model evaluation, feature engineering
  - **Features**: StandardScaler, train_test_split, metrics
  - **Usage**: ML pipeline preprocessing and evaluation

- **`joblib>=1.3.0`** - Parallel computing and model persistence
  - **Purpose**: Saves and loads trained ML models
  - **Features**: Model serialization, parallel processing
  - **Usage**: Model persistence (`models/` directory)

#### **API Framework**
- **`fastapi>=0.104.0`** - Modern, fast web framework for building APIs
  - **Purpose**: RESTful API endpoints for microservices
  - **Features**: Automatic API documentation, type validation
  - **Usage**: API server (`api_server.py`)

- **`uvicorn>=0.24.0`** - ASGI server for running FastAPI applications
  - **Purpose**: Production-ready server for API deployment
  - **Features**: High performance, WebSocket support
  - **Usage**: API server hosting

#### **File Upload & Processing**
- **`python-multipart>=0.0.6`** - Multipart form data parsing
  - **Purpose**: Handles file uploads in web applications
  - **Features**: File upload processing, form data parsing
  - **Usage**: Dashboard file upload functionality

- **`aiofiles>=23.2.0`** - Async file operations
  - **Purpose**: Non-blocking file I/O operations
  - **Features**: Async file reading/writing
  - **Usage**: Async file processing in microservices

---

## 🏗️ Microservices Requirements (`requirements_microservices.txt`)

### **Core FastAPI and Async Dependencies**
- **`fastapi==0.104.1`** - Web framework for APIs (version-locked)
- **`uvicorn[standard]==0.24.0`** - ASGI server with standard extras
- **`httpx==0.25.2`** - Async HTTP client for API calls
- **`pydantic==2.5.0`** - Data validation using Python type annotations

### **ML and Data Processing**
- **`pandas>=1.5.0`** - Data manipulation (same as main)
- **`numpy>=1.21.0`** - Numerical computing (same as main)
- **`scikit-learn>=1.1.0`** - Machine learning (same as main)
- **`lightgbm>=4.0.0`** - Gradient boosting (same as main)
- **`joblib>=1.2.0`** - Model persistence (same as main)

### **Dashboard Components**
- **`streamlit==1.29.0`** - Web dashboard (version-locked)
- **`plotly==5.17.0`** - Interactive charts (version-locked)

### **HTTP and Networking**
- **`requests==2.31.0`** - HTTP library for API calls
- **`aiohttp==3.9.1`** - Async HTTP client/server framework

### **Utilities**
- **`python-multipart==0.0.6`** - File upload handling
- **`python-dateutil==2.8.2`** - Date parsing and manipulation
- **`pytz==2023.3`** - Timezone handling

### **Logging and Monitoring**
- **`structlog==23.2.0`** - Structured logging for better debugging

### **Development and Testing**
- **`pytest==7.4.3`** - Testing framework
- **`pytest-asyncio==0.21.1`** - Async testing support
- **`black==23.11.0`** - Code formatting
- **`flake8==6.1.0`** - Code linting

### **Production Deployment**
- **`gunicorn==21.2.0`** - WSGI HTTP Server for production
- **`redis==5.0.1`** - In-memory data structure store
- **`celery==5.3.4`** - Distributed task queue

---

## 🔧 Tool Descriptions by Function

### **Web Interface Tools**
| Tool | Purpose | Key Features | Usage Location |
|------|---------|--------------|----------------|
| **Streamlit** | Dashboard UI | Real-time updates, file upload, interactive widgets | `app.py`, `run_dashboard.py` |
| **Plotly** | Interactive charts | Zoom, pan, hover, responsive design | Dashboard visualizations |
| **FastAPI** | REST API | Auto-docs, validation, async support | `api_server.py` |

### **Data Processing Tools**
| Tool | Purpose | Key Features | Usage Location |
|------|---------|--------------|----------------|
| **Pandas** | Data manipulation | Excel I/O, filtering, aggregation | All data processing modules |
| **NumPy** | Numerical operations | Array operations, math functions | ML preprocessing |
| **OpenPyXL** | Excel handling | Read/write .xlsx files | File upload/export |

### **Machine Learning Tools**
| Tool | Purpose | Key Features | Usage Location |
|------|---------|--------------|----------------|
| **LightGBM** | Gradient boosting | Fast training, high accuracy | `models/lightgbm_diagnoser.txt` |
| **Scikit-learn** | ML pipeline | Preprocessing, evaluation | ML pipeline components |
| **Joblib** | Model persistence | Save/load models | Model storage |

### **API & Communication Tools**
| Tool | Purpose | Key Features | Usage Location |
|------|---------|--------------|----------------|
| **Uvicorn** | ASGI server | High performance, WebSocket | API hosting |
| **HTTPX/AioHTTP** | HTTP client | Async requests, streaming | Microservice communication |
| **Pydantic** | Data validation | Type checking, serialization | API request/response models |

### **Development & Testing Tools**
| Tool | Purpose | Key Features | Usage Location |
|------|---------|--------------|----------------|
| **Pytest** | Testing framework | Unit tests, fixtures | Test files |
| **Black** | Code formatting | Consistent style | Development workflow |
| **Flake8** | Code linting | Style checking, error detection | Development workflow |

### **Production Tools**
| Tool | Purpose | Key Features | Usage Location |
|------|---------|--------------|----------------|
| **Gunicorn** | WSGI server | Production deployment | Production hosting |
| **Redis** | Caching/queuing | In-memory storage | Performance optimization |
| **Celery** | Task queue | Background processing | Async task handling |

---

## 📊 System Architecture by Tools

### **Frontend Layer**
```
Streamlit Dashboard
├── File Upload (python-multipart)
├── Interactive Charts (plotly)
└── Real-time Updates
```

### **API Layer**
```
FastAPI + Uvicorn
├── Request Validation (pydantic)
├── File Processing (aiofiles)
└── HTTP Communication (httpx/aiohttp)
```

### **Data Processing Layer**
```
Pandas + NumPy
├── Excel I/O (openpyxl)
├── Data Cleaning
└── Statistical Analysis
```

### **ML Layer**
```
LightGBM + Scikit-learn
├── Model Training
├── Prediction (joblib)
└── Feature Engineering
```

---

## 🚀 Installation Guide

### **Basic Installation**
```bash
# Install main requirements
pip install -r requirements.txt

# Install microservices requirements
pip install -r requirements_microservices.txt
```

### **Development Installation**
```bash
# Install with development tools
pip install -r requirements_microservices.txt
```

### **Production Installation**
```bash
# Install production dependencies
pip install gunicorn redis celery
```

---

## 🔍 Troubleshooting Common Issues

### **Version Conflicts**
- **Issue**: Package version conflicts
- **Solution**: Use virtual environments, pin versions in requirements

### **Missing Dependencies**
- **Issue**: Import errors for missing packages
- **Solution**: Check requirements.txt, install missing packages

### **Performance Issues**
- **Issue**: Slow dashboard loading
- **Solution**: Use Redis for caching, optimize data processing

### **ML Model Issues**
- **Issue**: Model loading errors
- **Solution**: Check joblib version compatibility, retrain models

---

## 📈 Performance Considerations

### **Memory Usage**
- **Pandas**: Large datasets can consume significant memory
- **LightGBM**: Model loading requires adequate RAM
- **Streamlit**: Caching helps with repeated computations

### **Processing Speed**
- **NumPy**: Vectorized operations for faster computation
- **Joblib**: Parallel processing for ML tasks
- **Async**: Non-blocking I/O for better responsiveness

### **Scalability**
- **Redis**: Caching layer for performance
- **Celery**: Background task processing
- **Gunicorn**: Production-grade server

---

This documentation provides a comprehensive overview of all tools and their purposes in the AI reconciliation system. Each tool has been carefully selected to provide optimal performance, maintainability, and user experience. 