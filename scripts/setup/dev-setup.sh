#!/bin/bash

# Development Environment Setup Script
# This script helps set up the development environment for the Extremism Monitor Bot

set -e

echo "=================================================="
echo "Extremism Monitor Bot - Development Setup"
echo "=================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker Compose is installed"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python 3 is not installed. Some features may not work."
else
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    echo "✅ Python $PYTHON_VERSION is installed"
fi

echo ""
echo "Setting up environment files..."
echo ""

# Create .env files from examples if they don't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example"
    echo "⚠️  Please edit .env with your actual credentials"
else
    echo "ℹ️  .env already exists"
fi

if [ ! -f discord-bot/.env ]; then
    cp discord-bot/.env.example discord-bot/.env
    echo "✅ Created discord-bot/.env from example"
    echo "⚠️  Please edit discord-bot/.env with your Discord bot token"
else
    echo "ℹ️  discord-bot/.env already exists"
fi

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from example"
    echo "⚠️  Please edit backend/.env with your API keys"
else
    echo "ℹ️  backend/.env already exists"
fi

echo ""
echo "Creating required directories..."
echo ""

mkdir -p logs
mkdir -p data/vectordb
mkdir -p data/models
mkdir -p discord-bot/logs
mkdir -p backend/logs

echo "✅ Directories created"

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit environment files with your credentials:"
echo "   - discord-bot/.env (add Discord bot token)"
echo "   - backend/.env (add Anthropic API key)"
echo ""
echo "2. Start the services:"
echo "   docker-compose up -d"
echo ""
echo "3. Check service status:"
echo "   docker-compose ps"
echo ""
echo "4. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "5. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "For more information, see GETTING_STARTED.md"
echo ""
