#!/bin/bash
# Frontend Dependency Installation Script
set -e

echo "🔧 Installing React Frontend Dependencies..."

# Already in apps/frontend directory

# Remove any existing conflicting files
rm -rf node_modules package-lock.json

# Copy dependencies from root
if [ -d "../../node_modules" ]; then
    echo "📦 Copying node_modules from root..."
    cp -r ../../node_modules .
fi

# Check if key packages exist
if [ -d "node_modules/react" ] && [ -d "node_modules/vite" ]; then
    echo "✅ Dependencies found, starting development server..."
    
    # Start Vite development server
    ./node_modules/.bin/vite --host 0.0.0.0 --port 3000 &
    
    echo "🌐 Frontend server starting on http://localhost:3000"
    echo "📡 Backend API available at http://localhost:8000"
    
    # Wait for server to start
    sleep 5
    
    # Test if server is running
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Frontend server is running successfully!"
    else
        echo "⚠️ Frontend server might still be starting..."
    fi
else
    echo "❌ Required dependencies not found"
    exit 1
fi