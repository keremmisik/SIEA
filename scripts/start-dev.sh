#!/bin/bash

# SIEA Development Environment Start Script

echo "🚀 SIEA Development Environment Starting..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start development services
echo "📦 Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "✅ Services status:"
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📋 Service URLs:"
echo "   PostgreSQL: localhost:5433"
echo "   Redis: localhost:6380"
echo "   pgAdmin: http://localhost:5050 (admin@siea.local / admin)"
echo ""
echo "📝 Next steps:"
echo "1. Start backend: cd backend && python main.py"
echo "2. Start frontend: cd frontend && npm start"
echo ""
echo "To stop services: docker-compose -f docker-compose.dev.yml down"
