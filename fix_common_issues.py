#!/usr/bin/env python3
"""
Common Issues Fixer for AI Reconciliation System

This script fixes common issues that users encounter when setting up and running
the AI reconciliation system.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_missing_packages():
    """Install missing packages."""
    required_packages = [
        'streamlit', 'uvicorn', 'fastapi', 'pandas', 'plotly', 
        'openpyxl', 'lightgbm', 'scikit-learn', 'joblib', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.info(f"📦 Installing missing packages: {missing_packages}")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages, check=True)
            logger.info("✅ All packages installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install packages: {e}")
            return False
    else:
        logger.info("✅ All required packages are already installed")
    
    return True

def clean_cache_directories():
    """Clean Python cache directories to fix file watching issues."""
    cache_patterns = ["__pycache__", "*.pyc", "*.pyo", "*.pyd"]
    
    cleaned_count = 0
    for pattern in cache_patterns:
        if pattern == "__pycache__":
            # Remove __pycache__ directories
            for root, dirs, files in os.walk("."):
                if "__pycache__" in dirs:
                    cache_dir = os.path.join(root, "__pycache__")
                    try:
                        shutil.rmtree(cache_dir)
                        cleaned_count += 1
                        logger.info(f"🗑️  Removed: {cache_dir}")
                    except Exception as e:
                        logger.warning(f"⚠️  Could not remove {cache_dir}: {e}")
        else:
            # Remove .pyc, .pyo, .pyd files
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith(pattern[1:]):  # Remove the *
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                            logger.info(f"🗑️  Removed: {file_path}")
                        except Exception as e:
                            logger.warning(f"⚠️  Could not remove {file_path}: {e}")
    
    if cleaned_count > 0:
        logger.info(f"✅ Cleaned {cleaned_count} cache files/directories")
    else:
        logger.info("✅ No cache files to clean")
    
    return True

def setup_streamlit_config():
    """Setup Streamlit configuration to avoid file watching issues."""
    config_dir = Path(".streamlit")
    config_file = config_dir / "config.toml"
    
    if not config_dir.exists():
        config_dir.mkdir(exist_ok=True)
        logger.info("📁 Created .streamlit/ directory")
    
    config_content = """[server]
fileWatcherType = "auto"
fileWatcherExcludePatterns = [
    "**/__pycache__/**",
    "**/*.pyc",
    "**/*.pyo",
    "**/*.pyd",
    "**/.git/**",
    "**/.venv/**",
    "**/venv/**",
    "**/node_modules/**",
    "**/.DS_Store"
]

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
"""
    
    if not config_file.exists() or config_file.read_text() != config_content:
        config_file.write_text(config_content)
        logger.info("📝 Created/updated Streamlit configuration file")
    else:
        logger.info("✅ Streamlit configuration already exists")
    
    return True

def create_sample_data():
    """Create sample data files if they don't exist."""
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir(exist_ok=True)
        logger.info("📁 Created data/ directory")
    
    sample_files = {
        "old_pricing.xlsx": {
            "TradeID": ["TRADE001", "TRADE002", "TRADE003"],
            "PV_old": [1000000, 2000000, 3000000],
            "Delta_old": [0.5, 0.3, 0.7]
        },
        "new_pricing.xlsx": {
            "TradeID": ["TRADE001", "TRADE002", "TRADE003"],
            "PV_new": [1001000, 2002000, 3003000],
            "Delta_new": [0.51, 0.31, 0.71]
        },
        "trade_metadata.xlsx": {
            "TradeID": ["TRADE001", "TRADE002", "TRADE003"],
            "ProductType": ["Swap", "Option", "Swap"],
            "FundingCurve": ["USD-LIBOR", "USD-SOFR", "EUR-EURIBOR"],
            "CSA_Type": ["Cleared", "Bilateral", "Cleared"],
            "ModelVersion": ["v2024.1", "v2024.2", "v2024.1"]
        },
        "funding_model_reference.xlsx": {
            "TradeID": ["TRADE001", "TRADE002", "TRADE003"],
            "FundingCurve": ["USD-LIBOR", "USD-SOFR", "EUR-EURIBOR"],
            "ModelVersion": ["v2024.1", "v2024.2", "v2024.1"]
        }
    }
    
    try:
        import pandas as pd
        
        for filename, data in sample_files.items():
            file_path = data_dir / filename
            if not file_path.exists():
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False)
                logger.info(f"📄 Created sample file: {filename}")
            else:
                logger.info(f"✅ Sample file already exists: {filename}")
        
        return True
    except ImportError:
        logger.warning("⚠️  pandas not available, skipping sample data creation")
        return False

def test_components():
    """Test individual components."""
    tests = [
        ("Data Loader", "from crew.agents.unified_data_loader import UnifiedDataLoaderAgent"),
        ("ML Tool", "from crew.agents.ml_tool import MLDiagnoserAgent"),
        ("Streamlit", "import streamlit"),
        ("FastAPI", "import fastapi"),
        ("Pandas", "import pandas"),
        ("LightGBM", "import lightgbm")
    ]
    
    failed_tests = []
    for test_name, import_statement in tests:
        try:
            exec(import_statement)
            logger.info(f"✅ {test_name} test passed")
        except Exception as e:
            logger.error(f"❌ {test_name} test failed: {e}")
            failed_tests.append(test_name)
    
    if failed_tests:
        logger.error(f"❌ Failed tests: {failed_tests}")
        return False
    else:
        logger.info("✅ All component tests passed")
        return True

def main():
    """Main function to fix common issues."""
    print("🔧 AI Reconciliation System - Common Issues Fixer")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install missing packages
    if not install_missing_packages():
        return False
    
    # Clean cache directories
    clean_cache_directories()
    
    # Setup Streamlit configuration
    setup_streamlit_config()
    
    # Create sample data
    create_sample_data()
    
    # Test components
    if not test_components():
        logger.warning("⚠️  Some components failed tests. Check the errors above.")
    
    print("\n" + "=" * 60)
    print("🎉 Fix completed!")
    print("\n📋 Next steps:")
    print("1. Run the dashboard: python run_dashboard.py")
    print("2. Or run the API server: python api_server.py")
    print("3. Or run the pipeline: python pipeline.py --source files")
    print("\n💡 If you still have issues, check the troubleshooting guide:")
    print("   docs/TROUBLESHOOTING.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 