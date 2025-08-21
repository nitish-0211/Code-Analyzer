"""
Super Simple Test Script
Easy to understand and run
"""

import requests

# Where our API is running
API_URL = "http://localhost:8080"

def test_home():
    """Test if our API is working"""
    print("Testing home page...")
    
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Message: {response.json()}")
    print()

def test_analyze():
    """Test analyzing a GitHub repository"""
    print("Testing repository analysis...")
    
    # Example data to test with
    test_data = {
        "github_url": "https://github.com/octocat/Hello-World",
        "assignment": "Create a simple Hello World program"
    }
    
    print(f"Repository: {test_data['github_url']}")
    print(f"Assignment: {test_data['assignment']}")
    print()
    
    try:
        response = requests.post(f"{API_URL}/analyze", params=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Analysis completed:")
            print(f"Repository: {result['repository']}")
            print(f"Languages: {', '.join(result['languages'])}")
            print(f"Score: {result['score']}/100")
            print(f"Explanation: {result['explanation']}")
            print("Suggestions:")
            for i, suggestion in enumerate(result['suggestions'], 1):
                print(f"  {i}. {suggestion}")
        else:
            print(f"ERROR: {response.status_code}")
            print(f"Details: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        print("Make sure the server is running: python simple_main.py")

if __name__ == "__main__":
    print("Simple GitHub Analyzer - Test")
    print("=" * 40)
    
    test_home()
    test_analyze()
    
    print("=" * 40)
    print("Done! Try your own repositories at: http://localhost:8080/docs")
