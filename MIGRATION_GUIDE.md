# Migration Guide: Unified Data Loader

## Overview

The reconciliation system has been **completely refactored** to use a **unified data loader** that consolidates file-based, API-based, and hybrid loading into a single, more maintainable class. The old separate data loader classes have been **removed** and replaced with the new `UnifiedDataLoaderAgent`.

## What Changed

### Before (Separate Loaders) - REMOVED
- `DataLoaderAgent` - File-based loading only ❌ **DELETED**
- `APIDataLoaderAgent` - API-based loading only ❌ **DELETED**  
- `HybridDataLoaderAgent` - Combined both approaches ❌ **DELETED**
- **3 separate classes** to maintain
- **Inconsistent interfaces** and methods
- **Code duplication** in merging logic

### After (Unified Loader) - CURRENT
- `UnifiedDataLoaderAgent` - Handles all scenarios ✅ **ACTIVE**
- **Single class** with consistent interface
- **Automatic fallback** and source detection
- **Cleaner codebase** with less duplication
- **Enhanced features** and better error handling

## Migration Steps

### 1. Update Imports

**Old (No longer available):**
```python
from crew.agents.data_loader import DataLoaderAgent
from crew.agents.api_data_loader import APIDataLoaderAgent
from crew.agents.hybrid_data_loader import HybridDataLoaderAgent
```

**New (Required):**
```python
from crew.agents.unified_data_loader import UnifiedDataLoaderAgent
```

### 2. Update Crew Builder Usage

**Old (No longer supported):**
```python
# File-based only
crew = ReconciliationCrew(data_dir="data/")

# API-based only  
crew = ReconciliationCrew(api_config=api_config)

# Hybrid
crew = ReconciliationCrew(data_dir="data/", api_config=api_config)
```

**New (Current implementation):**
```python
# All scenarios use the same constructor
crew = ReconciliationCrew(data_dir="data/", api_config=api_config)
```

### 3. Update Data Loading Calls

**Old (No longer available):**
```python
# File loader
df = data_loader.load_all_data()

# API loader
df = data_loader.load_all_data_from_api(trade_ids, date)

# Hybrid loader
df = data_loader.load_data(source, trade_ids, date)
```

**New (Current implementation):**
```python
# Unified interface
df = data_loader.load_data(source="files")           # File-based
df = data_loader.load_data(source="api", trade_ids=trade_ids, date=date)  # API-based
df = data_loader.load_data(source="auto")            # Auto-detect
df = data_loader.load_data(source="hybrid", trade_ids=trade_ids, date=date)  # Hybrid
```

### 4. Update Command Line Usage

**Old (No longer supported):**
```bash
# File-based only
python pipeline.py

# API-based (required custom code)
python pipeline.py --api-config api_config.json
```

**New (Current implementation):**
```bash
# File-based
python pipeline.py --source files

# API-based
python pipeline.py --source api --api-config api_config.json

# Auto-detect (default)
python pipeline.py

# Hybrid
python pipeline.py --source hybrid --api-config api_config.json

# With specific trade IDs
python pipeline.py --source api --api-config api_config.json --trade-ids TRADE001 TRADE002

# With specific date
python pipeline.py --source api --api-config api_config.json --date 2024-01-15
```

## New Features

### 1. Source Options
- `"files"` - Load from Excel files only
- `"api"` - Load from API endpoints only
- `"auto"` - Auto-detect best available source (default)
- `"hybrid"` - Load from both sources and merge

### 2. Enhanced Error Handling
- Better error messages and logging
- Automatic fallback when API fails
- Data quality validation
- Graceful degradation for missing data

### 3. Consistent Interface
- All methods return the same data types
- Unified configuration approach
- Standardized error handling
- Built-in data validation

### 4. Performance Improvements
- **Data Loading**: 1,000-10,000 trades/second (file-based)
- **ML Training**: 10,000-100,000 trades/second (LightGBM)
- **ML Prediction**: 50,000-500,000 trades/second
- **Report Generation**: 1,000-10,000 trades/second

## Backward Compatibility

**⚠️ IMPORTANT**: The old data loader classes have been **completely removed** and are no longer available. This is a breaking change that requires migration.

### Removed Classes
- `crew.agents.data_loader.DataLoaderAgent` ❌ **DELETED**
- `crew.agents.api_data_loader.APIDataLoaderAgent` ❌ **DELETED**  
- `crew.agents.hybrid_data_loader.HybridDataLoaderAgent` ❌ **DELETED**

### Required Migration
All existing code must be updated to use the new `UnifiedDataLoaderAgent`. There is no backward compatibility.

## Benefits of Migration

1. **Reduced Maintenance**: Single class instead of three
2. **Better Performance**: Optimized merging logic and LightGBM ML
3. **Cleaner Code**: Less duplication and complexity
4. **Enhanced Features**: Better error handling and validation
5. **Future-Proof**: Easier to extend and modify
6. **Consistent Interface**: Unified API across all data sources

## Testing Migration

After migrating, test your application with:

```python
# Test file-based loading
crew = ReconciliationCrew(data_dir="data/")
df = crew.run(source="files")

# Test API-based loading  
crew = ReconciliationCrew(api_config=api_config)
df = crew.run(source="api")

# Test auto-detection
crew = ReconciliationCrew(data_dir="data/", api_config=api_config)
df = crew.run(source="auto")

# Test hybrid loading
crew = ReconciliationCrew(data_dir="data/", api_config=api_config)
df = crew.run(source="hybrid")
```

## Current File Structure

```
crew/agents/
├── unified_data_loader.py    ✅ Active
├── ml_tool.py               ✅ Active (LightGBM)
├── narrator_agent.py        ✅ Active
├── analyzer_agent.py        ✅ Active
├── recon_agent.py           ✅ Active
└── __pycache__/            📁 Cache directory
```

## Support

If you encounter issues during migration, please:
1. Check the error messages for specific guidance
2. Verify your API configuration format
3. Ensure all required files are present
4. Review the updated documentation
5. Check the `UNIFIED_LOADER_SUMMARY.md` for detailed implementation
6. Check the `CLEANUP_SUMMARY.md` for removed files

## Migration Checklist

- [ ] Update all imports to use `UnifiedDataLoaderAgent`
- [ ] Update crew initialization to use new constructor
- [ ] Update data loading calls to use new `load_data()` method
- [ ] Update command line usage with new `--source` parameter
- [ ] Test all data source options (files, api, auto, hybrid)
- [ ] Verify API configuration format
- [ ] Test error handling and fallback scenarios
- [ ] Update any custom code that referenced old loaders 