#!/usr/bin/env python3
"""
AI Reconciliation Dashboard Launcher

This script launches the Streamlit dashboard with optimized settings for development
and production environments.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = ['streamlit', 'pandas', 'plotly', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {missing_packages}")
        logger.info("Install missing packages with: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All dependencies are installed")
    return True

def check_data_files():
    """Check if data directory and files exist."""
    data_dir = Path("data")
    required_files = [
        "old_pricing.xlsx",
        "new_pricing.xlsx", 
        "trade_metadata.xlsx",
        "funding_model_reference.xlsx"
    ]
    
    if not data_dir.exists():
        logger.warning("⚠️  Data directory not found. Creating 'data/' directory.")
        data_dir.mkdir(exist_ok=True)
        logger.info("📁 Created data/ directory. Please add your Excel files.")
        return False
    
    missing_files = []
    for file in required_files:
        if not (data_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.warning(f"⚠️  Missing data files: {missing_files}")
        logger.info("📁 Please add the missing files to the data/ directory")
        return False
    
    logger.info("✅ All data files found")
    return True

def setup_streamlit_config():
    """Setup Streamlit configuration to avoid file watching issues."""
    config_dir = Path(".streamlit")
    config_file = config_dir / "config.toml"
    
    if not config_dir.exists():
        config_dir.mkdir(exist_ok=True)
        logger.info("📁 Created .streamlit/ directory")
    
    if not config_file.exists():
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
        config_file.write_text(config_content)
        logger.info("📝 Created Streamlit configuration file")

def get_dashboard_port():
    """Get available dashboard port."""
    import socket
    
    # Try default port first
    port = 8501
    
    for i in range(10):  # Try ports 8501-8510
        test_port = 8501 + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', test_port))
                port = test_port
                break
        except OSError:
            continue
    
    return port

def launch_dashboard():
    """Launch the Streamlit dashboard with optimized settings."""
    try:
        # Setup configuration
        setup_streamlit_config()
        
        # Get available port
        port = get_dashboard_port()
        
        # Set environment variables for better performance
        os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'auto'
        os.environ['STREAMLIT_SERVER_MAX_UPLOAD_SIZE'] = '200'
        os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
        
        # Build command
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.address", "localhost",
            "--server.fileWatcherType", "auto",
            "--server.maxUploadSize", "200",
            "--browser.gatherUsageStats", "false"
        ]
        
        logger.info("🚀 Starting AI Reconciliation Dashboard...")
        logger.info(f"📊 Dashboard will open in your default browser")
        logger.info(f"🔗 URL: http://localhost:{port}")
        logger.info("⏹️  Press Ctrl+C to stop the dashboard")
        logger.info("-" * 50)
        
        # Launch dashboard
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to start dashboard: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
    
    return True

def main():
    """Main function to launch the dashboard."""
    print("🤖 AI Reconciliation Dashboard Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check data files (warning only)
    check_data_files()
    
    # Launch dashboard
    success = launch_dashboard()
    
    if not success:
        logger.error("❌ Failed to launch dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main() 