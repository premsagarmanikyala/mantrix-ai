#!/usr/bin/env python3
"""
Direct React Frontend Server
Uses Vite from root node_modules to start the frontend development server
"""
import subprocess
import os
import sys
import time
import threading

def start_vite_server():
    """Start Vite development server using root node_modules"""
    print("Starting React Frontend Development Server...")
    
    # Use vite from root node_modules
    vite_path = "./node_modules/.bin/vite"
    frontend_dir = "apps/frontend"
    
    if not os.path.exists(vite_path):
        print(f"Error: Vite not found at {vite_path}")
        return False
    
    if not os.path.exists(frontend_dir):
        print(f"Error: Frontend directory {frontend_dir} not found")
        return False
    
    # Vite command with proper configuration
    cmd = [
        vite_path,
        "--host", "0.0.0.0",
        "--port", "3000",
        "--config", f"{frontend_dir}/vite.config.ts"
    ]
    
    try:
        print(f"Running: {' '.join(cmd)} in {frontend_dir}")
        
        # Start process
        process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("Vite server starting...")
        
        # Stream output for a few seconds to see if it starts
        timeout = 15
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            line = process.stdout.readline()
            if line:
                print(f"[VITE] {line.strip()}")
                if "Local:" in line or "ready in" in line:
                    print("Frontend server is ready!")
                    break
            elif process.poll() is not None:
                break
        
        if process.poll() is None:
            print("Frontend server is running in background")
            return True
        else:
            print(f"Process exited with code {process.returncode}")
            return False
            
    except Exception as e:
        print(f"Error starting Vite server: {e}")
        return False

def check_backend():
    """Check if backend is running"""
    import urllib.request
    try:
        response = urllib.request.urlopen("http://localhost:8000/health")
        print("Backend API is running on port 8000")
        return True
    except:
        print("Backend API not accessible on port 8000")
        return False

if __name__ == "__main__":
    print("=== Mantrix Frontend Development Server ===")
    
    # Check backend
    check_backend()
    
    # Start frontend
    success = start_vite_server()
    
    if success:
        print("\n✅ Frontend server started successfully!")
        print("🌐 Frontend: http://localhost:3000")
        print("📡 Backend API: http://localhost:8000")
        print("📖 API Docs: http://localhost:8000/docs")
    else:
        print("\n❌ Failed to start frontend server")
        sys.exit(1)