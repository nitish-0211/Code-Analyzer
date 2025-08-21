"""
SUPER SIMPLE GitHub Repository Analyzer
Perfect for entry-level developers to understand and explain

This code does 3 things:
1. Takes a GitHub URL and assignment description
2. Gets basic info about the repository 
3. Uses AI to check if it matches the assignment
"""

from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load our secret keys
load_dotenv()

# Create our web app
app = FastAPI(title="Simple GitHub Analyzer")

# Setup AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ai_model = genai.GenerativeModel('gemini-pro')

@app.get("/")
def home():
    """Home page - just says hello"""
    return {"message": "Hello! GitHub Analyzer is working!"}

@app.post("/analyze")
def analyze_repo(github_url: str, assignment: str):
    """
    Main function - analyzes a GitHub repository
    
    Steps:
    1. Get repository name from URL
    2. Get repository information from GitHub
    3. Ask AI to analyze it
    4. Return the results
    """
    
    # Step 1: Get repo name from URL
    repo_name = get_repo_name(github_url)
    
    # Step 2: Get repo info from GitHub
    repo_info = get_repo_info(repo_name)
    
    # Step 3: Ask AI to analyze
    ai_result = ask_ai_to_analyze(repo_info, assignment)
    
    # Step 4: Return results
    return {
        "repository": repo_name,
        "languages": repo_info["languages"],
        "score": ai_result["score"],
        "explanation": ai_result["explanation"],
        "suggestions": ai_result["suggestions"]
    }

def get_repo_name(github_url):
    """
    Extract repository name from GitHub URL
    Example: "https://github.com/user/my-repo" -> "user/my-repo"
    """
    # Remove the GitHub part
    clean_url = github_url.replace("https://github.com/", "")
    clean_url = clean_url.replace("http://github.com/", "")
    
    # Get just the user/repo part
    parts = clean_url.split("/")
    repo_name = f"{parts[0]}/{parts[1]}"
    
    return repo_name

def get_repo_info(repo_name):
    """
    Get basic information about the repository from GitHub
    """
    
    # Ask GitHub for repository information
    url = f"https://api.github.com/repos/{repo_name}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Could not find repository: {repo_name}")
    
    repo_data = response.json()
    
    # Get programming languages used
    languages_url = f"https://api.github.com/repos/{repo_name}/languages"
    languages_response = requests.get(languages_url)
    languages = list(languages_response.json().keys()) if languages_response.status_code == 200 else []
    
    # Get some code files to analyze
    code_content = get_some_code_files(repo_name)
    
    return {
        "name": repo_data["name"],
        "description": repo_data.get("description", "No description"),
        "languages": languages,
        "code_files": code_content
    }

def get_some_code_files(repo_name):
    """
    Download a few code files to analyze
    """
    
    # Get list of files in the repository
    url = f"https://api.github.com/repos/{repo_name}/contents"
    response = requests.get(url)
    
    if response.status_code != 200:
        return "No code files found"
    
    files = response.json()
    code_content = ""
    
    # Look at first few files
    for file in files[:3]:  # Only look at first 3 files
        if file["type"] == "file":
            file_name = file["name"]
            
            # Only look at code files
            if any(file_name.endswith(ext) for ext in ['.py', '.js', '.java', '.cpp', '.md']):
                # Download the file content
                file_content = download_file(file["download_url"])
                if file_content:
                    code_content += f"\n--- {file_name} ---\n{file_content[:500]}\n"  # First 500 characters only
    
    return code_content if code_content else "No code files found"

def download_file(file_url):
    """
    Download content of a single file
    """
    try:
        response = requests.get(file_url)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return ""

def ask_ai_to_analyze(repo_info, assignment):
    """
    Ask AI to analyze if the repository matches the assignment
    """
    
    # Create a simple question for the AI
    question = f"""
    Look at this GitHub repository and tell me if it matches this assignment.
    
    ASSIGNMENT: {assignment}
    
    REPOSITORY INFO:
    - Name: {repo_info['name']}
    - Description: {repo_info['description']}
    - Languages: {', '.join(repo_info['languages'])}
    
    CODE FILES:
    {repo_info['code_files']}
    
    Please answer:
    1. Score from 0 to 100 (how well does it match?)
    2. Simple explanation why
    3. Three suggestions to improve
    
    Format: SCORE: [number] EXPLANATION: [text] SUGGESTIONS: [suggestion1] | [suggestion2] | [suggestion3]
    """
    
    try:
        # Ask the AI
        response = ai_model.generate_content(question)
        return parse_ai_answer(response.text)
    except Exception as e:
        # If AI fails, return a default answer
        return {
            "score": 50,
            "explanation": f"AI analysis failed: {str(e)}",
            "suggestions": ["Check code quality", "Add documentation", "Test functionality"]
        }

def parse_ai_answer(ai_text):
    """
    Convert AI response into organized data
    """
    
    # Default values
    score = 50
    explanation = "Analysis completed"
    suggestions = ["Improve code", "Add tests", "Better documentation"]
    
    try:
        # Look for SCORE:
        if "SCORE:" in ai_text:
            score_part = ai_text.split("SCORE:")[1].split("EXPLANATION:")[0].strip()
            score = int(score_part)
        
        # Look for EXPLANATION:
        if "EXPLANATION:" in ai_text:
            explanation_part = ai_text.split("EXPLANATION:")[1].split("SUGGESTIONS:")[0].strip()
            explanation = explanation_part
        
        # Look for SUGGESTIONS:
        if "SUGGESTIONS:" in ai_text:
            suggestions_part = ai_text.split("SUGGESTIONS:")[1].strip()
            suggestions = [s.strip() for s in suggestions_part.split("|")]
    
    except:
        # If parsing fails, use defaults
        pass
    
    return {
        "score": max(0, min(100, score)),  # Keep score between 0-100
        "explanation": explanation,
        "suggestions": suggestions[:3]  # Maximum 3 suggestions
    }

# Start the server
if __name__ == "__main__":
    import uvicorn
    print("Starting Simple GitHub Analyzer...")
    print("Visit: http://localhost:8080/docs")
    uvicorn.run("simple_main:app", host="localhost", port=8080, reload=True)
