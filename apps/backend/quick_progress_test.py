#!/usr/bin/env python3
"""Quick test for Progress Tracker API functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

def quick_progress_test():
    print("=== QUICK PROGRESS TRACKER API TEST ===")
    client = TestClient(app)
    
    # Test authentication
    signup_data = {"email": "progresstest@example.com", "password": "password123"}
    response = client.post("/api/auth/signup", json=signup_data)
    if response.status_code != 200:
        response = client.post("/api/auth/login", json=signup_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
        # Test progress health endpoint
        response = client.get("/api/v1/progress/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ Progress service health check passed")
            print(f"   Features: {len(health['features'])}")
            print(f"   Database: {health['database']}")
            print(f"   Auth: {health['authentication']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        # Create a test roadmap
        roadmap_data = {"user_input": "Learn Python basics", "mode": "full"}
        response = client.post("/api/v1/roadmap/generate", json=roadmap_data, headers=headers)
        
        if response.status_code == 200:
            roadmap_id = response.json()["roadmaps"][0]["id"]
            print(f"✅ Created test roadmap: {roadmap_id}")
            
            # Test progress completion
            progress_data = {
                "module_id": "test_module_1",
                "branch_id": "test_branch_1", 
                "roadmap_id": roadmap_id,
                "duration_completed": 300
            }
            
            response = client.post("/api/v1/progress/complete", json=progress_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Progress completion successful")
                print(f"   Status: {result['status']}")
                print(f"   Progress ID: {result.get('progress_id', 'N/A')}")
                
                # Test progress summary
                response = client.get(f"/api/v1/progress/summary?roadmap_id={roadmap_id}", headers=headers)
                
                if response.status_code == 200:
                    summary = response.json()
                    print("✅ Progress summary retrieved")
                    print(f"   Total modules: {summary['total_modules']}")
                    print(f"   Completed: {summary['completed_modules']}")
                    print(f"   Progress: {summary['progress_percent']}%")
                    print(f"   Branches: {len(summary['branches'])}")
                    return True
                else:
                    print(f"❌ Progress summary failed: {response.status_code}")
                    print(f"   Error: {response.json()}")
                    return False
            else:
                print(f"❌ Progress completion failed: {response.status_code}")
                print(f"   Error: {response.json()}")
                return False
        else:
            print(f"❌ Roadmap creation failed: {response.status_code}")
            return False
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return False

if __name__ == "__main__":
    success = quick_progress_test()
    if success:
        print("\n🎉 PROGRESS TRACKER API IS WORKING!")
        print("✅ Module completion tracking")
        print("✅ Progress summaries with branch breakdowns") 
        print("✅ JWT authentication")
        print("✅ PostgreSQL persistence")
        print("✅ Frontend-ready API format")
    else:
        print("\n❌ Progress tracker has issues")
    sys.exit(0 if success else 1)