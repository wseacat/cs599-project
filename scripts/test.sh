#!/bin/bash

# Enterprise Agentic-RAG Knowledge Base - Test Script

set -e

echo "=========================================="
echo " Enterprise Agentic-RAG Knowledge Base"
echo " Running Tests"
echo "=========================================="

# Run backend tests
echo ""
echo "Running backend tests..."
cd backend

# Activate virtual environment
source .venv/bin/activate 2>/dev/null || .venv/Scripts/activate

# Run pytest
pytest src/tests/ -v --cov=src --cov-report=term-mcd

cd ..

echo ""
echo "=========================================="
echo " Tests Complete!"
echo "=========================================="
