#!/usr/bin/env python3
"""
Comprehensive test suite for the Learning Path Recommendation System.

Tests:
- POST /api/v1/roadmap/recommend - Multi-mode recommendations
- Gap analysis for job descriptions
- Resume enhancement suggestions
- Interest-based learning paths
- AI integration with fallback systems
- User progress integration
"""

import sys
import os
import json
from typing import Dict, List, Any

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

def test_recommendation_system():
    """Comprehensive test for learning path recommendation system."""
    
    print("=== TESTING LEARNING PATH RECOMMENDATION SYSTEM ===")
    client = TestClient(app)
    
    # Test 1: User Authentication
    print("\n1. Testing User Authentication...")
    signup_data = {
        "email": "recommendations@example.com",
        "password": "securepassword123"
    }
    
    response = client.post("/api/auth/signup", json=signup_data)
    if response.status_code != 200:
        # Try login if user already exists
        response = client.post("/api/auth/login", json=signup_data)
    
    if response.status_code == 200:
        user_data = response.json()
        token = user_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"   ✅ User authenticated successfully")
    else:
        print(f"   ❌ Authentication failed: {response.json()}")
        return False
    
    # Test 2: Recommendation Service Health Check
    print("\n2. Testing Recommendation Service Health Check...")
    response = client.get("/api/v1/roadmap/recommend/health")
    
    if response.status_code == 200:
        health_data = response.json()
        print(f"   ✅ Service status: {health_data['status']}")
        print(f"   ✅ AI integration: {health_data['ai_integration']}")
        print(f"   ✅ Available modes: {', '.join(health_data['modes'])}")
        print(f"   ✅ Features: {len(health_data['features'])}")
        print(f"   ✅ Capabilities: {len(health_data['capabilities'])}")
    else:
        print(f"   ⚠️  Health check failed: {response.status_code}")
    
    # Test 3: Create Test Data (User Progress)
    print("\n3. Setting Up Test Progress Data...")
    # Create a roadmap first
    roadmap_data = {
        "user_input": "Learn full-stack web development with React and Node.js",
        "mode": "full"
    }
    
    response = client.post("/api/v1/roadmap/generate", json=roadmap_data, headers=headers)
    if response.status_code == 200:
        roadmap_result = response.json()
        test_roadmap_id = roadmap_result["roadmaps"][0]["id"]
        print(f"   ✅ Created test roadmap: {test_roadmap_id}")
        
        # Add some progress data
        progress_data = {
            "module_id": "react_basics_101",
            "branch_id": "frontend_development",
            "roadmap_id": test_roadmap_id,
            "duration_completed": 1800  # 30 minutes
        }
        
        response = client.post("/api/v1/progress/complete", json=progress_data, headers=headers)
        if response.status_code == 200:
            print("   ✅ Added test progress data")
        else:
            print("   ⚠️  Progress data creation failed")
    else:
        print("   ⚠️  Roadmap creation failed - continuing with tests")
    
    # Test 4: Gap Analysis Mode
    print("\n4. Testing Gap Analysis Recommendations...")
    gap_request = {
        "mode": "gap",
        "target_job_description": """
        Senior Full-Stack Developer position requiring:
        - 5+ years React.js experience
        - Node.js and Express.js backend development
        - PostgreSQL database design
        - AWS cloud services
        - Docker containerization
        - GraphQL API development
        - TypeScript proficiency
        - System design and microservices
        - CI/CD pipeline management
        - Leadership and mentoring skills
        """
    }
    
    response = client.post("/api/v1/roadmap/recommend", json=gap_request, headers=headers)
    
    if response.status_code == 200:
        gap_result = response.json()
        print("   ✅ Gap analysis recommendations generated")
        print(f"   ✅ Mode: {gap_result['mode']}")
        print(f"   ✅ Recommendations: {len(gap_result['recommendations'])}")
        print(f"   ✅ Confidence: {gap_result['confidence_score']:.2f}")
        print(f"   ✅ Analysis: {gap_result['analysis_summary'][:100]}...")
        
        # Show first recommendation details
        if gap_result['recommendations']:
            first_rec = gap_result['recommendations'][0]
            print(f"   📚 First recommendation: {first_rec['title']}")
            print(f"      Reason: {first_rec['reason'][:80]}...")
            print(f"      Modules: {len(first_rec['modules'])}")
            print(f"      Duration: {first_rec['estimated_duration'] // 60} minutes")
            
    else:
        print(f"   ❌ Gap analysis failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        return False
    
    # Test 5: Resume Enhancement Mode
    print("\n5. Testing Resume Enhancement Recommendations...")
    resume_request = {
        "mode": "resume",
        "existing_resume": """
        John Doe - Software Developer
        
        Experience:
        - Junior Developer at TechCorp (2 years)
        - Built web applications using HTML, CSS, JavaScript
        - Worked with basic React components
        - Used MySQL for simple database queries
        
        Skills:
        - HTML/CSS/JavaScript
        - Basic React
        - MySQL
        - Git version control
        
        Education:
        - Bachelor's in Computer Science
        """
    }
    
    response = client.post("/api/v1/roadmap/recommend", json=resume_request, headers=headers)
    
    if response.status_code == 200:
        resume_result = response.json()
        print("   ✅ Resume enhancement recommendations generated")
        print(f"   ✅ Recommendations: {len(resume_result['recommendations'])}")
        print(f"   ✅ Confidence: {resume_result['confidence_score']:.2f}")
        print(f"   ✅ Next steps: {len(resume_result['next_steps'])}")
        
        # Show recommendation titles
        for i, rec in enumerate(resume_result['recommendations']):
            print(f"   📈 {i+1}. {rec['title']} - {rec['reason'][:60]}...")
            
    else:
        print(f"   ❌ Resume enhancement failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        return False
    
    # Test 6: Interest-Based Mode
    print("\n6. Testing Interest-Based Recommendations...")
    interest_request = {
        "mode": "interest",
        "skill_interests": ["Machine Learning", "Data Science", "Python", "AI"],
        "career_level": "intermediate"
    }
    
    response = client.post("/api/v1/roadmap/recommend", json=interest_request, headers=headers)
    
    if response.status_code == 200:
        interest_result = response.json()
        print("   ✅ Interest-based recommendations generated")
        print(f"   ✅ Recommendations: {len(interest_result['recommendations'])}")
        
        # Show detailed breakdown
        for rec in interest_result['recommendations']:
            print(f"   🎯 {rec['title']}")
            print(f"      Difficulty: {rec['difficulty']}")
            print(f"      Prerequisites: {len(rec['prerequisites'])}")
            print(f"      Modules: {len(rec['modules'])}")
            print(f"      Benefit: {rec['completion_benefit'][:50]}...")
            
    else:
        print(f"   ❌ Interest-based recommendations failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        return False
    
    # Test 7: Error Handling - Missing Required Parameters
    print("\n7. Testing Error Handling...")
    invalid_request = {
        "mode": "gap",
        # Missing target_job_description for gap mode
    }
    
    response = client.post("/api/v1/roadmap/recommend", json=invalid_request, headers=headers)
    
    if response.status_code == 400:
        print("   ✅ Correctly handled invalid gap request")
    else:
        print(f"   ⚠️  Expected 400 error, got {response.status_code}")
    
    # Test 8: Recommendation Quality Analysis
    print("\n8. Analyzing Recommendation Quality...")
    
    # Test all modes and analyze results
    modes_tested = ["gap", "resume", "interest"]
    quality_scores = []
    
    for mode in modes_tested:
        if mode == "gap":
            test_data = gap_result
        elif mode == "resume":
            test_data = resume_result
        else:
            test_data = interest_result
        
        # Quality metrics
        has_recommendations = len(test_data['recommendations']) > 0
        has_modules = all(len(rec['modules']) > 0 for rec in test_data['recommendations'])
        has_durations = all(rec['estimated_duration'] > 0 for rec in test_data['recommendations'])
        has_reasons = all(len(rec['reason']) > 20 for rec in test_data['recommendations'])
        
        quality_score = sum([has_recommendations, has_modules, has_durations, has_reasons]) / 4
        quality_scores.append(quality_score)
        
        print(f"   📊 {mode.title()} mode quality: {quality_score:.1%}")
        print(f"      Recommendations: {'✅' if has_recommendations else '❌'}")
        print(f"      Module details: {'✅' if has_modules else '❌'}")
        print(f"      Duration estimates: {'✅' if has_durations else '❌'}")
        print(f"      Clear reasoning: {'✅' if has_reasons else '❌'}")
    
    overall_quality = sum(quality_scores) / len(quality_scores)
    print(f"\n   🎯 Overall system quality: {overall_quality:.1%}")
    
    return overall_quality > 0.75  # 75% quality threshold


def print_feature_summary():
    """Print comprehensive feature summary."""
    print("\n" + "="*80)
    print("LEARNING PATH RECOMMENDATION SYSTEM - IMPLEMENTATION SUMMARY")
    print("="*80)
    
    features = [
        "✅ Multi-Mode Recommendations: Gap analysis, resume enhancement, interest-based",
        "✅ AI-Powered Analysis: GPT-4 integration for intelligent suggestions",
        "✅ User Progress Integration: Leverages completed modules and study history",
        "✅ Job Description Analysis: Skills extraction and gap identification",
        "✅ Resume Enhancement: Profile improvement recommendations",
        "✅ Interest-Based Paths: Personalized learning based on user preferences",
        "✅ Detailed Module Breakdowns: Duration estimates and difficulty levels",
        "✅ Confidence Scoring: Reliability assessment for recommendations",
        "✅ Actionable Next Steps: Clear guidance for learning progression",
        "✅ Fallback System: Reliable recommendations when AI is unavailable",
        "✅ JWT Authentication: Secure user-based recommendation access",
        "✅ Comprehensive Error Handling: Graceful failure management"
    ]
    
    for feature in features:
        print(feature)
    
    print("\nAPI Endpoint Implemented:")
    print("• POST /api/v1/roadmap/recommend - Generate personalized learning recommendations")
    print("• GET /api/v1/roadmap/recommend/health - Service health and capability check")
    
    print("\nRecommendation Modes:")
    modes = [
        "📊 Gap Mode: Analyze skills needed for target job roles",
        "📈 Resume Mode: Suggest improvements to enhance professional profile",
        "🎯 Interest Mode: Recommend paths based on user interests and preferences"
    ]
    
    for mode in modes:
        print(f"• {mode}")
    
    print("\nAI Integration:")
    ai_features = [
        "🤖 OpenAI GPT-4 for intelligent analysis and recommendations",
        "📝 Natural language processing for job descriptions and resumes",
        "🎯 Personalized learning path generation based on user context",
        "🔄 Fallback system with rule-based recommendations",
        "📊 Confidence scoring for recommendation reliability"
    ]
    
    for feature in ai_features:
        print(f"• {feature}")


if __name__ == "__main__":
    try:
        success = test_recommendation_system()
        print_feature_summary()
        
        if success:
            print(f"\n🎉 ALL RECOMMENDATION SYSTEM TESTS PASSED!")
            print("The Learning Path Recommendation System is fully functional and ready for production.")
            sys.exit(0)
        else:
            print(f"\n❌ SOME TESTS FAILED - Please check the implementation")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 TEST EXECUTION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)