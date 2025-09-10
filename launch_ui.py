#!/usr/bin/env python3
"""
Launch script for the Adobe Creative Studio Streamlit UI
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit UI."""
    
    print("🎨 Launching Adobe Creative Studio...")
    print("=" * 50)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly", "pandas"])
        print("✅ Streamlit installed successfully")
    
    # Check if required directories exist
    required_dirs = ["examples", "output", "src"]
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            Path(dir_name).mkdir(exist_ok=True)
            print(f"📁 Created directory: {dir_name}")
    
    # Launch Streamlit
    print("\n🚀 Starting Adobe Creative Studio...")
    print("📱 The UI will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("\n" + "=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Adobe Creative Studio closed")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")
        print("💡 Try running: pip install streamlit plotly pandas")

if __name__ == "__main__":
    main()

