#!/bin/bash
cd /Users/navjot/Desktop/file_compression_tool

# Kill any existing processes
pkill -f "backend.py" 2>/dev/null
pkill -f "server.py" 2>/dev/null
sleep 2

# Start backend
python3 backend.py &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID) on http://localhost:8001"

# Start web server
python3 server.py &
WEB_PID=$!
echo "Web server started (PID: $WEB_PID) on http://localhost:8000"

echo ""
echo "Open http://localhost:8000 in your browser"
echo "Press Ctrl+C to stop both servers"

# Wait for either to exit
wait
