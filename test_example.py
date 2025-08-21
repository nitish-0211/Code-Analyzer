"""
Simple test script to demonstrate the GitHub Repository Analyzer
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:8080"

def test_home():
    """Test the home endpoint"""
    print("🏠 Testing home endpoint...")
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_analyze():
    """Test the analyze endpoint with a sample repository"""
    print("🔍 Testing analyze endpoint...")
    
    # Example request
    test_data = {
        "github_url": "https://github.com/octocat/Hello-World",
        "assignment_description": "Create a simple Hello World program that prints a greeting message"
    }
    
    print(f"Analyzing: {test_data['github_url']}")
    print(f"Assignment: {test_data['assignment_description']}")
    print()
    
    try:
        response = requests.post(f"{API_URL}/analyze", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis successful!")
            print(f"Repository: {result['repository_name']}")
            print(f"Languages: {', '.join(result['languages_found'])}")
            print(f"Match Score: {result['assignment_match_score']:.2f} ({result['assignment_match_score']*100:.1f}%)")
            print(f"Commits: {result['total_commits']}")
            print(f"Contributors: {result['contributors']}")
            print(f"Explanation: {result['explanation']}")
            print("Suggestions:")
            for i, suggestion in enumerate(result['suggestions'], 1):
                print(f"  {i}. {suggestion}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running!")
        print("Run: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("GitHub Repository Analyzer - Test Script")
    print("=" * 50)
    
    # Test both endpoints
    test_home()
    test_analyze()
    
    print("=" * 50)
    print("To run your own tests:")
    print("1. Start the server: python main.py")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Try different GitHub repositories!")
