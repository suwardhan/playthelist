#!/bin/bash
# Railway startup script for PlayTheList

# Get port from Railway environment variable
PORT=${PORT:-8501}

echo "🚀 Starting PlayTheList on port $PORT"
echo "🔧 Environment: PORT=$PORT"
echo "🌐 Binding to 0.0.0.0:$PORT"

# Start Streamlit app with explicit configuration
exec streamlit run app.py \
  --server.port $PORT \
  --server.address 0.0.0.0 \
  --server.headless true \
  --global.gatherUsageStats false \
  --server.enableCORS true \
  --server.enableXsrfProtection false
