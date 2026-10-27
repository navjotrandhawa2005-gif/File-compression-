#!/bin/bash
cd "$(dirname "$0")"

# Ensure backend API server is running on port 8001
if ! curl -s http://localhost:8001/ >/dev/null 2>&1; then
    echo "Starting backend API server on http://localhost:8001..."
    nohup python3 backend.py > backend.log 2>&1 &
    sleep 1
fi

python3 server.py

