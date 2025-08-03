#!/usr/bin/env python3
"""
Frontend Development Server Runner
Handles React development server startup with proper dependency management
"""
import subprocess
import sys
import os
import time

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"Running: {cmd} (in {cwd or 'current directory'})")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if check and result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        return False
    return True

def setup_frontend():
    """Setup and start React frontend development server"""
    frontend_dir = "apps/frontend"
    
    print("🚀 Setting up React Frontend Development Server...")
    
    # Check if frontend directory exists
    if not os.path.exists(frontend_dir):
        print(f"❌ Frontend directory {frontend_dir} not found")
        return False
    
    # Check Node.js version
    print("📋 Checking Node.js environment...")
    if not run_command("node --version"):
        print("❌ Node.js not found")
        return False
    
    if not run_command("npm --version"):
        print("❌ npm not found")
        return False
    
    # Check if dependencies exist
    node_modules_path = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules_path):
        print("📦 Installing frontend dependencies...")
        if not run_command("npm install", cwd=frontend_dir, check=False):
            print("⚠️ npm install had issues, but continuing...")
    
    # Start development server
    print("🌐 Starting React development server...")
    print("Frontend will be available at: http://localhost:5173")
    print("Backend API available at: http://localhost:8000")
    
    try:
        # Start the dev server (this will block)
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("✅ React development server started!")
        print("📝 Server logs:")
        
        # Stream output
        for line in process.stdout:
            print(f"[VITE] {line.strip()}")
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down development server...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"❌ Error starting development server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = setup_frontend()
    sys.exit(0 if success else 1)