#!/bin/bash

# Production startup script for PlayTheList
set -e

echo "🚀 Starting PlayTheList in Production Mode"
echo "=========================================="

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please create it from env.example and configure your production values"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker: sudo systemctl start docker"
    exit 1
fi

# Use production environment file
echo "📝 Using production environment configuration..."
cp .env.production .env

# Build and start services
echo "🔨 Building and starting production services..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 15

# Check if services are running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Production services are running!"
    echo ""
    echo "🌐 Application is available at:"
    echo "   - https://yourdomain.com (via Nginx)"
    echo "   - http://localhost:8501 (direct access)"
    echo ""
    echo "📊 To view logs:"
    echo "   docker-compose -f docker-compose.prod.yml logs -f app"
    echo ""
    echo "🛑 To stop services:"
    echo "   docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo "🔄 To update:"
    echo "   docker-compose -f docker-compose.prod.yml up -d --build"
    echo ""
    echo "🔍 To check health:"
    echo "   curl https://yourdomain.com/health"
else
    echo "❌ Error: Services failed to start!"
    echo "Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi

echo "🎉 Production deployment completed successfully!"
