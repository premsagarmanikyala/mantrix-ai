#!/usr/bin/env python3
"""
Development Server Starter for React Frontend
Bypasses npm run restrictions in Replit environment
"""
import subprocess
import os
import sys
import signal
import time

def run_vite_server():
    """Start Vite development server directly"""
    frontend_dir = "apps/frontend"
    
    print("🚀 Starting React Development Server...")
    print("📍 Frontend directory:", os.path.abspath(frontend_dir))
    print("🌐 Backend API:", "http://localhost:8000")
    print("🎯 Frontend URL:", "http://localhost:3000")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Start Vite server directly
    vite_cmd = [
        "../../node_modules/.bin/vite",
        "--host", "0.0.0.0",
        "--port", "3000",
        "--open"
    ]
    
    try:
        print("📋 Running command:", " ".join(vite_cmd))
        process = subprocess.Popen(
            vite_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            preexec_fn=os.setsid  # Create new process group
        )
        
        print("✅ Vite server started (PID: {})".format(process.pid))
        
        # Stream output
        for line in process.stdout:
            print(f"[VITE] {line.strip()}")
            
            # Check if server is ready
            if "Local:" in line or "ready in" in line:
                print("🎉 Development server is ready!")
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down development server...")
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process.wait()
        print("✅ Server stopped cleanly")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_vite_server()
    sys.exit(0 if success else 1)