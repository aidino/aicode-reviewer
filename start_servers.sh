#!/bin/bash

echo "🚀 Starting AI Code Reviewer Servers"
echo "===================================="

# Kiểm tra virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Run: source venv/bin/activate"
fi

# Function để kill processes khi script dừng
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap để cleanup khi Ctrl+C
trap cleanup INT

# Khởi chạy backend
echo "🐍 Starting Backend (FastAPI)..."
python -m uvicorn src.webapp.backend.api.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --reload &
BACKEND_PID=$!

# Đợi backend khởi động
echo "   Waiting for backend to start..."
sleep 3

# Test backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ Backend running at http://localhost:8000"
else
    echo "   ❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Khởi chạy frontend
echo ""
echo "⚛️  Starting Frontend (Vite + React)..."
cd src/webapp/frontend
npm run dev &
FRONTEND_PID=$!
cd - > /dev/null

# Đợi frontend khởi động
echo "   Waiting for frontend to start..."
sleep 5

# Test frontend
if curl -s http://localhost:5173/ > /dev/null; then
    echo "   ✅ Frontend running at http://localhost:5173"
else
    echo "   ❌ Frontend failed to start"
    cleanup
    exit 1
fi

echo ""
echo "🎉 All servers running successfully!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Giữ script chạy
wait 