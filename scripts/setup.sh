#!/bin/bash

# Enterprise Agentic-RAG Knowledge Base - Setup Script

set -e

echo "=========================================="
echo " Enterprise Agentic-RAG Knowledge Base"
echo " Setup Script"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and configure your API keys"
    echo ""
fi

# Start infrastructure services
echo "Starting infrastructure services..."
docker compose up -d mysql redis milvus

echo "Waiting for services to be ready..."
sleep 10

# Setup backend
echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate 2>/dev/null || .venv/Scripts/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -e ".[dev]"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

cd ..

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "=========================================="
echo " Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Start backend:"
echo "   cd backend"
echo "   source .venv/bin/activate"
echo "   uvicorn src.main:app --reload --port 8000"
echo ""
echo "2. Start frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "=========================================="
