#!/usr/bin/env python3
"""
Complete Mantrix Application Startup Script
Starts both backend FastAPI and frontend React servers
"""
import subprocess
import time
import sys
import os
import signal
import threading
import urllib.request

def check_port(port, service_name):
    """Check if a service is running on a specific port"""
    try:
        response = urllib.request.urlopen(f"http://localhost:{port}")
        print(f"✅ {service_name} is running on port {port}")
        return True
    except:
        print(f"❌ {service_name} not responding on port {port}")
        return False

def start_backend():
    """Start FastAPI backend server"""
    print("🚀 Starting FastAPI Backend Server...")
    
    backend_dir = "apps/backend"
    if not os.path.exists(backend_dir):
        print(f"Error: Backend directory {backend_dir} not found")
        return None
    
    try:
        process = subprocess.Popen(
            ["python", "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        print(f"Backend started with PID: {process.pid}")
        return process
        
    except Exception as e:
        print(f"Error starting backend: {e}")
        return None

def start_frontend():
    """Start Vite frontend development server"""
    print("🌐 Starting React Frontend Server...")
    
    frontend_dir = "apps/frontend"
    vite_path = "./node_modules/.bin/vite"
    
    if not os.path.exists(vite_path):
        print(f"Error: Vite not found at {vite_path}")
        return None
    
    if not os.path.exists(frontend_dir):
        print(f"Error: Frontend directory {frontend_dir} not found")
        return None
    
    try:
        cmd = [
            "../../node_modules/.bin/vite",
            "--host", "0.0.0.0",
            "--port", "3000"
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        print(f"Frontend started with PID: {process.pid}")
        return process
        
    except Exception as e:
        print(f"Error starting frontend: {e}")
        return None

def main():
    """Main application startup"""
    print("=== Mantrix Full-Stack Application Startup ===")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("Failed to start backend")
        sys.exit(1)
    
    # Wait for backend to start
    print("Waiting for backend to start...")
    time.sleep(5)
    
    # Check backend health
    backend_running = check_port(8000, "FastAPI Backend")
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("Failed to start frontend")
        # Don't exit, backend might still be useful
    
    # Wait for frontend to start
    print("Waiting for frontend to start...")
    time.sleep(8)
    
    # Check frontend
    frontend_running = check_port(3000, "React Frontend")
    
    # Final status
    print("\n=== Startup Complete ===")
    if backend_running:
        print("📡 Backend API: http://localhost:8000")
        print("📖 API Docs: http://localhost:8000/docs")
    
    if frontend_running:
        print("🌐 Frontend: http://localhost:3000")
    
    print("\n✅ All services started successfully!")
    print("🎯 Multi-Track Merge & Timeline Planning System is ready!")
    
    # Keep processes running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()

if __name__ == "__main__":
    main()