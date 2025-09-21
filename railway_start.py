#!/usr/bin/env python3
"""
Railway startup script for PlayTheList
"""
import os
import subprocess
import sys

def main():
    # Get port from Railway environment variable
    port = os.getenv("PORT", "8501")
    
    print(f"🚀 Starting PlayTheList on port {port}")
    print(f"🔧 Environment: PORT={port}")
    print(f"🌐 Binding to 0.0.0.0:{port}")
    
    # Start Streamlit app
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--server.enableCORS", "true",
        "--server.enableXsrfProtection", "false"
    ]
    
    print(f"🔧 Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down PlayTheList...")
        sys.exit(0)

if __name__ == "__main__":
    main()
