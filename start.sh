#!/bin/bash
# Railway startup script for PlayTheList

# Get port from Railway environment variable
PORT=${PORT:-8501}

echo "🚀 Starting PlayTheList on port $PORT"

# Start Streamlit app
streamlit run app.py \
  --server.port $PORT \
  --server.address 0.0.0.0 \
  --browser.gatherUsageStats false \
  --server.headless true
