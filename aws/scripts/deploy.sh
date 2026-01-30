#!/bin/bash

###############################################
# Smart Home IoT - Deploy Script
# Deploys application using Docker Compose
###############################################

set -e

PROJECT_DIR="/opt/smart-home-iot"
COMPOSE_FILE="docker-compose.prod.yml"

echo "================================================"
echo "  Smart Home IoT - Deployment"
echo "================================================"

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env.prod" ]; then
    echo "❌ Error: .env.prod file not found!"
    echo "Please create .env.prod file with all required variables"
    exit 1
fi

# Navigate to project directory
cd "$PROJECT_DIR"

echo "📥 Pulling latest code..."
git pull origin main || echo "⚠️  Git pull failed, using local code"

echo "🛑 Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down || true

echo "🔨 Building images..."
docker-compose -f $COMPOSE_FILE build --no-cache

echo "🚀 Starting containers..."
docker-compose -f $COMPOSE_FILE up -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Checking container status..."
docker-compose -f $COMPOSE_FILE ps

echo "📋 Backend logs (last 20 lines):"
docker-compose -f $COMPOSE_FILE logs --tail=20 backend

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "🌐 Application should be available at:"
echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "📊 Monitor logs:"
echo "   docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "🔄 Restart services:"
echo "   docker-compose -f $COMPOSE_FILE restart"