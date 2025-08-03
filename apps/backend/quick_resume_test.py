#!/usr/bin/env python3
"""Quick test for resume builder functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

def quick_test():
    print("=== QUICK RESUME BUILDER TEST ===")
    client = TestClient(app)
    
    # Test authentication
    signup_data = {"email": "quicktest@example.com", "password": "password123"}
    response = client.post("/api/auth/signup", json=signup_data)
    if response.status_code != 200:
        response = client.post("/api/auth/login", json=signup_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
        # Test resume health endpoint
        response = client.get("/api/v1/resume/health")
        if response.status_code == 200:
            print("✅ Resume service health check passed")
            print(f"   Modes: {response.json()['modes_supported']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        # Test resume generation (fast mode - no roadmap needed for basic test)
        # First create a roadmap
        roadmap_data = {"user_input": "Learn Python basics", "mode": "full"}
        response = client.post("/api/v1/roadmap/generate", json=roadmap_data, headers=headers)
        
        if response.status_code == 200:
            roadmap_id = response.json()["roadmaps"][0]["id"]
            print(f"✅ Created test roadmap: {roadmap_id}")
            
            # Test fast mode resume generation
            resume_data = {"mode": "fast", "roadmap_id": roadmap_id}
            response = client.post("/api/v1/resume/generate", json=resume_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Resume generation successful")
                print(f"   Resume ID: {result['resume']['id']}")
                print(f"   Mode: {result['resume']['mode']}")
                print(f"   Status: {result['status']}")
                return True
            else:
                print(f"❌ Resume generation failed: {response.status_code}")
                print(f"   Error: {response.json()}")
                return False
        else:
            print(f"❌ Roadmap creation failed: {response.status_code}")
            return False
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 RESUME BUILDER IS WORKING!")
    else:
        print("\n❌ Resume builder has issues")
    sys.exit(0 if success else 1)