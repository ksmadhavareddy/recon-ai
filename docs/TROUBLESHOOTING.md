# 🔧 Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. Streamlit File Watching Errors

#### **Problem:**
```
FileNotFoundError: [WinError 2] The system cannot find the file specified: 
'F:\\recon-ai\\crew\\agents\\__pycache__\\recon_agent.cpython-312.pyc.1927142661840'
```

#### **Cause:**
Streamlit's file watcher is trying to access temporary Python cache files that are being created and deleted rapidly during development.

#### **Solutions:**

**Option A: Disable File Watching (Recommended for Development)**
```bash
# Run Streamlit with file watching disabled
streamlit run app.py --server.fileWatcherType none

# Or using Python module
python -m streamlit run app.py --server.fileWatcherType none
```

**Option B: Exclude Cache Directories**
```bash
# Create .streamlit/config.toml file
mkdir .streamlit
```

```toml
# .streamlit/config.toml
[server]
fileWatcherType = "auto"
fileWatcherExcludePatterns = [
    "**/__pycache__/**",
    "**/*.pyc",
    "**/*.pyo",
    "**/*.pyd",
    "**/.git/**",
    "**/.venv/**",
    "**/venv/**"
]
```

**Option C: Clean Cache Directories**
```bash
# Remove all Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
```

### 2. Command Not Found Errors

#### **Problem:**
```
streamlit : The term 'streamlit' is not recognized
uvicorn : The term 'uvicorn' is not recognized
```

#### **Cause:**
Python packages are not installed or not in PATH.

#### **Solutions:**

**Option A: Install Missing Packages**
```bash
# Install required packages
pip install streamlit uvicorn fastapi

# Or install from requirements
pip install -r requirements.txt
```

**Option B: Use Python Module Syntax**
```bash
# Instead of direct commands, use Python module syntax
python -m streamlit run app.py
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

**Option C: Check Python Environment**
```bash
# Verify Python installation
python --version

# Check installed packages
pip list | grep streamlit
pip list | grep uvicorn

# Activate virtual environment if using one
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Dashboard Loading Issues

#### **Problem:**
Dashboard starts but shows errors or doesn't load data properly.

#### **Solutions:**

**Check Data Files:**
```bash
# Verify data files exist
ls -la data/
# Should show:
# old_pricing.xlsx
# new_pricing.xlsx
# trade_metadata.xlsx
# funding_model_reference.xlsx
```

**Check File Permissions:**
```bash
# Ensure read permissions
chmod 644 data/*.xlsx
```

**Test Data Loading:**
```python
# Test data loading in Python
import pandas as pd
try:
    df = pd.read_excel('data/old_pricing.xlsx')
    print(f"✅ Loaded {len(df)} rows from old_pricing.xlsx")
except Exception as e:
    print(f"❌ Error loading file: {e}")
```

### 4. API Server Issues

#### **Problem:**
API server fails to start or returns errors.

#### **Solutions:**

**Check Port Availability:**
```bash
# Check if port 8000 is in use
netstat -an | grep 8000
# Windows
netstat -an | findstr 8000

# Use different port if needed
python api_server.py --port 8001
```

**Test API Endpoints:**
```bash
# Test API health
curl http://localhost:8000/api/health

# Test data endpoints
curl http://localhost:8000/api/database/old_pricing?limit=5
```

**Check Database:**
```bash
# Verify database exists
ls -la reconciliation.db

# Recreate database if corrupted
rm reconciliation.db
python api_server.py
```

### 5. ML Model Issues

#### **Problem:**
ML model fails to load or predict.

#### **Solutions:**

**Check Model Files:**
```bash
# Verify model files exist
ls -la models/
# Should show:
# lightgbm_diagnoser.txt
# lightgbm_diagnoser.txt.le
```

**Recreate Model:**
```python
# Force model retraining
from crew.agents.ml_tool import MLDiagnoserAgent
import pandas as pd

# Load sample data
df = pd.read_excel('data/old_pricing.xlsx')
# Add required columns for training
df['PV_Diagnosis'] = 'Within tolerance'  # Default diagnosis

# Train new model
ml_agent = MLDiagnoserAgent()
ml_agent.train(df, label_col='PV_Diagnosis')
```

### 6. Performance Issues

#### **Problem:**
Slow processing or memory errors.

#### **Solutions:**

**Optimize Memory Usage:**
```python
# Add to your script
import gc
import psutil

# Monitor memory
print(f"Memory usage: {psutil.virtual_memory().percent}%")

# Force garbage collection
gc.collect()
```

**Process Data in Chunks:**
```python
# For large datasets
chunk_size = 1000
for chunk in pd.read_excel('large_file.xlsx', chunksize=chunk_size):
    # Process chunk
    process_chunk(chunk)
    gc.collect()
```

### 7. Configuration Issues

#### **Problem:**
Configuration files not found or invalid.

#### **Solutions:**

**Check Configuration Files:**
```bash
# Verify config files exist
ls -la config/
ls -la *.json

# Create missing config
cp api_config_example.json api_config.json
```

**Validate JSON Syntax:**
```bash
# Test JSON syntax
python -m json.tool api_config.json
```

### 8. Development Environment Issues

#### **Problem:**
Inconsistent behavior across different environments.

#### **Solutions:**

**Use Virtual Environment:**
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

**Check Python Version:**
```bash
# Ensure compatible Python version
python --version
# Should be Python 3.8+ for all features
```

**Update Dependencies:**
```bash
# Update all packages
pip install --upgrade -r requirements.txt
```

## 🔍 Debug Mode

### Enable Debug Logging
```python
import logging

# Set debug level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Test Individual Components
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

## 📞 Getting Help

### 1. Check Logs
```bash
# Streamlit logs
streamlit run app.py --logger.level debug

# API server logs
python api_server.py --log-level debug
```

### 2. System Information
When reporting issues, include:
- **OS**: Windows/Linux/Mac version
- **Python**: Version and installation method
- **Packages**: `pip freeze` output
- **Error**: Complete error message and stack trace
- **Steps**: Exact steps to reproduce

### 3. Common Commands
```bash
# Quick health check
python -c "import streamlit, uvicorn, pandas, lightgbm; print('✅ All packages installed')"

# Test dashboard
python run_dashboard.py

# Test API
python api_server.py

# Test pipeline
python pipeline.py --source files
```

## 🚀 Performance Optimization

### For Large Datasets
1. **Use chunked processing**
2. **Enable caching**
3. **Monitor memory usage**
4. **Use efficient data types**

### For Production
1. **Use proper logging**
2. **Implement error handling**
3. **Add monitoring**
4. **Use environment variables**

---

**💡 Tip**: Most issues can be resolved by ensuring all dependencies are installed and using the correct Python environment. 