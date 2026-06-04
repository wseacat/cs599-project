@echo off
REM Enterprise Agentic-RAG Knowledge Base - Setup Script for Windows

echo ==========================================
echo  Enterprise Agentic-RAG Knowledge Base
echo  Setup Script
echo ==========================================

REM Check if .env exists
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo ⚠️  Please edit .env and configure your API keys
    echo.
)

REM Start infrastructure services
echo Starting infrastructure services...
docker compose up -d mysql redis milvus

echo Waiting for services to be ready...
timeout /t 10 /nobreak > nul

REM Setup backend
echo.
echo Setting up backend...
cd backend

REM Create virtual environment if not exists
if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -e ".[dev]"

REM Run database migrations
echo Running database migrations...
alembic upgrade head

cd ..

REM Setup frontend
echo.
echo Setting up frontend...
cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
npm install

cd ..

echo.
echo ==========================================
echo  Setup Complete!
echo ==========================================
echo.
echo To start the application:
echo.
echo 1. Start backend:
echo    cd backend
echo    .venv\Scripts\activate
echo    uvicorn src.main:app --reload --port 8000
echo.
echo 2. Start frontend (in another terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Access the application:
echo    Frontend: http://localhost:5173
echo    API Docs: http://localhost:8000/docs
echo.
echo ==========================================
