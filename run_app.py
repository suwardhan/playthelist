#!/usr/bin/env python3
"""
Simple launcher script for the PlayTheList web app
"""
import subprocess
import sys
import os

def main():
    """Launch the Streamlit app"""
    print("🎵 Starting PlayTheList Web Interface...")
    print("📱 The app will open in your default browser")
    print("🔗 If it doesn't open automatically, go to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run streamlit app
        port = os.getenv("PORT", "8501")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", port,
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down PlayTheList...")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        print("💡 Make sure you have installed all requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
