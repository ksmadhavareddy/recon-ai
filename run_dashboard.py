#!/usr/bin/env python3
"""
Streamlit Dashboard Launcher for AI Reconciliation System
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard"""
    print("🚀 Starting AI Reconciliation Dashboard...")
    print("📊 Dashboard will open in your default browser")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("💡 Make sure you have installed all requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 