#!/bin/bash
# Direct Frontend Server Starter
set -e

echo "Starting React Frontend Server..."

# Check if required files exist
if [ ! -f "node_modules/.bin/vite" ]; then
    echo "Error: Vite not found in root node_modules"
    exit 1
fi

if [ ! -d "apps/frontend" ]; then
    echo "Error: Frontend directory not found"
    exit 1
fi

# Start Vite development server
cd apps/frontend

echo "Starting Vite server on port 3000..."
echo "Frontend will be available at: http://localhost:3000"
echo "Backend API available at: http://localhost:8000"

# Use Vite from root node_modules with proper configuration
../../node_modules/.bin/vite --host 0.0.0.0 --port 3000 &

VITE_PID=$!
echo "Vite server started with PID: $VITE_PID"

# Wait for server to start
sleep 5

# Test if server is responding
if curl -s http://localhost:3000 > /dev/null; then
    echo "Frontend server is running successfully!"
else
    echo "Frontend server might still be starting..."
fi

echo "Frontend development server is active"