# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Railway will set PORT environment variable)
EXPOSE $PORT

# Health check
HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health

# Run the application with dynamic port
CMD ["sh", "-c", "streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true --browser.gatherUsageStats false"]
