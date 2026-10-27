#!/bin/bash
# Start both servers
cd "$(dirname "$0")"
python3 backend.py &
BACKEND_PID=$!
sleep 2
python3 server.py &
WEB_PID=$!
echo "Backend PID: $BACKEND_PID, Web PID: $WEB_PID"
wait
