# Migration Guide: Unified Data Loader

## Overview

The reconciliation system has been refactored to use a **unified data loader** that consolidates file-based, API-based, and hybrid loading into a single, more maintainable class.

## What Changed

### Before (Separate Loaders)
- `DataLoaderAgent` - File-based loading only
- `APIDataLoaderAgent` - API-based loading only  
- `HybridDataLoaderAgent` - Combined both approaches
- **3 separate classes** to maintain
- **Inconsistent interfaces** and methods
- **Code duplication** in merging logic

### After (Unified Loader)
- `UnifiedDataLoaderAgent` - Handles all scenarios
- **Single class** with consistent interface
- **Automatic fallback** and source detection
- **Cleaner codebase** with less duplication

## Migration Steps

### 1. Update Imports

**Old:**
```python
from crew.agents.data_loader import DataLoaderAgent
from crew.agents.api_data_loader import APIDataLoaderAgent
from crew.agents.hybrid_data_loader import HybridDataLoaderAgent
```

**New:**
```python
from crew.agents.unified_data_loader import UnifiedDataLoaderAgent
```

### 2. Update Crew Builder Usage

**Old:**
```python
# File-based only
crew = ReconciliationCrew(data_dir="data/")

# API-based only  
crew = ReconciliationCrew(api_config=api_config)

# Hybrid
crew = ReconciliationCrew(data_dir="data/", api_config=api_config)
```

**New:**
```python
# All scenarios use the same constructor
crew = ReconciliationCrew(data_dir="data/", api_config=api_config)
```

### 3. Update Data Loading Calls

**Old:**
```python
# File loader
df = data_loader.load_all_data()

# API loader
df = data_loader.load_all_data_from_api(trade_ids, date)

# Hybrid loader
df = data_loader.load_data(source, trade_ids, date)
```

**New:**
```python
# Unified interface
df = data_loader.load_data(source="files")           # File-based
df = data_loader.load_data(source="api", trade_ids=trade_ids, date=date)  # API-based
df = data_loader.load_data(source="auto")            # Auto-detect
df = data_loader.load_data(source="hybrid", trade_ids=trade_ids, date=date)  # Hybrid
```

### 4. Update Command Line Usage

**Old:**
```bash
# File-based only
python pipeline.py

# API-based (required custom code)
python pipeline.py --api-config api_config.json
```

**New:**
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

### 3. Consistent Interface
- All methods return the same data types
- Unified configuration approach
- Standardized error handling

## Backward Compatibility

The old data loader classes are **deprecated** but still available for backward compatibility. However, they will be removed in a future version.

### Deprecated Classes
- `crew.agents.data_loader.DataLoaderAgent`
- `crew.agents.api_data_loader.APIDataLoaderAgent`  
- `crew.agents.hybrid_data_loader.HybridDataLoaderAgent`

## Benefits of Migration

1. **Reduced Maintenance**: Single class instead of three
2. **Better Performance**: Optimized merging logic
3. **Cleaner Code**: Less duplication and complexity
4. **Enhanced Features**: Better error handling and validation
5. **Future-Proof**: Easier to extend and modify

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
```

## Support

If you encounter issues during migration, please:
1. Check the error messages for specific guidance
2. Verify your API configuration format
3. Ensure all required files are present
4. Review the updated documentation 