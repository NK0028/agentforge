#!/usr/bin/env bash

# ==============================================================================
# AgentForge - Autonomous Multi-Agent AI Platform Startup Script
# ==============================================================================

set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

echo "=================================================="
echo "🚀 Starting AgentForge Platform..."
echo "=================================================="

# Function to clean up child processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down AgentForge services..."
    if [ -n "${BACKEND_PID}" ] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
        kill "${BACKEND_PID}" 2>/dev/null || true
    fi
    if [ -n "${FRONTEND_PID}" ] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
        kill "${FRONTEND_PID}" 2>/dev/null || true
    fi
    echo "👋 AgentForge shut down cleanly."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 1. Check if ports 8000 and 5173 are already occupied and clean them
echo "🔍 Checking port availability..."
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "⚠️  Port 8000 is in use. Terminating stale process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

if lsof -ti:5173 >/dev/null 2>&1; then
    echo "⚠️  Port 5173 is in use. Terminating stale process..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
fi

# 2. Check Ollama daemon
echo "🤖 Checking Ollama local LLM status..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is running."
else
    echo "⚠️  Ollama daemon not detected on http://localhost:11434"
    echo "   Please make sure Ollama is installed and running ('ollama serve')."
fi

# 3. Setup and start Backend
echo "⚙️  Starting FastAPI Backend on http://localhost:8000..."
cd "${BACKEND_DIR}"

# Activate or create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: ${BACKEND_PID})"

# 4. Setup and start Frontend
echo "💻 Starting React Frontend on http://localhost:5173..."
cd "${FRONTEND_DIR}"

if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

npm run dev -- --host &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: ${FRONTEND_PID})"

echo "=================================================="
echo "🎉 AgentForge is running!"
echo "👉 Dashboard: http://localhost:5173"
echo "👉 Backend API: http://localhost:8000"
echo "👉 Press Ctrl+C to stop all services."
echo "=================================================="

# Wait for both processes
wait
