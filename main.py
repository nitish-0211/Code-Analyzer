
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = FastAPI(
    title="Simple GitHub Repository Analyzer",
    description="Analyze GitHub repositories for assignment alignment",
    version="1.0.0"
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Data-models

class AnalyzeRequest(BaseModel):
    github_url: str
    assignment_description: str 

class AnalyzeResponse(BaseModel):
    repository_name: str
    languages_found: List[str]
    assignment_match_score: float 
    explanation: str
    suggestions: List[str]
    total_commits: int
    contributors: int

# ENDPOINTS

@app.get("/")
def home():
    return {
        "message": "GitHub Repository Analyzer is running!",
        "status": "OK",
        "endpoints": {
            "analyze": "/analyze - Analyze a GitHub repository",
            "docs": "/docs - API documentation"
        }
    }

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_repository(request: AnalyzeRequest):
    try:
        owner, repo_name = extract_repo_info(request.github_url)

        repo_info = get_repository_info(owner, repo_name)

        code_files = get_code_files(owner, repo_name)
        
        # AI Analysis
        ai_analysis = analyze_with_ai(
            assignment_description=request.assignment_description,
            repo_info=repo_info,
            code_files=code_files
        )
        
        # Results
        return AnalyzeResponse(
            repository_name=f"{owner}/{repo_name}",
            languages_found=repo_info["languages"],
            assignment_match_score=ai_analysis["score"],
            explanation=ai_analysis["explanation"],
            suggestions=ai_analysis["suggestions"],
            total_commits=repo_info["total_commits"],
            contributors=repo_info["contributors"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

def extract_repo_info(github_url: str) -> tuple:
    if "github.com" not in github_url:
        raise Exception("Please provide a valid GitHub URL")
    
    path = github_url.replace("https://github.com/", "").replace("http://github.com/", "")
    parts = path.split("/")
    
    if len(parts) < 2:
        raise Exception("Invalid GitHub URL format")
    
    return parts[0], parts[1]

# Repo Information

def get_repository_info(owner: str, repo_name: str) -> Dict[str, Any]:
    repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    response = requests.get(repo_url)
    
    if response.status_code == 404:
        raise Exception(f"Repository {owner}/{repo_name} not found")
    elif response.status_code != 200:
        raise Exception(f"Failed to access repository: {response.status_code}")
    
    repo_data = response.json()
    
    # check programming languages
    languages_url = f"https://api.github.com/repos/{owner}/{repo_name}/languages"
    languages_response = requests.get(languages_url)
    languages = list(languages_response.json().keys()) if languages_response.status_code == 200 else []
    
    # commits
    commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
    commits_response = requests.get(commits_url)
    total_commits = len(commits_response.json()) if commits_response.status_code == 200 else 0
    
    # contributors
    contributors_url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
    contributors_response = requests.get(contributors_url)
    contributors = len(contributors_response.json()) if contributors_response.status_code == 200 else 0
    
    return {
        "name": repo_data["name"],
        "description": repo_data.get("description", "No description"),
        "languages": languages,
        "size": repo_data["size"],
        "stars": repo_data["stargazers_count"],
        "total_commits": total_commits,
        "contributors": contributors
    }

# Repo Contents

def get_code_files(owner: str, repo_name: str, max_files: int = 5) -> List[Dict[str, str]]:
    contents_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
    response = requests.get(contents_url)
    
    if response.status_code != 200:
        return []
    
    files_data = response.json()
    code_files = []
    
    important_extensions = ['.py', '.js', '.java', '.cpp', '.c', '.md', '.txt']
    
    for file_info in files_data[:max_files]:
        if file_info["type"] == "file":
            file_name = file_info["name"]

            if any(file_name.endswith(ext) for ext in important_extensions):
                file_content = download_file_content(file_info["download_url"])
                
                if file_content:
                    code_files.append({
                        "name": file_name,
                        "content": file_content[:2000] 
                    })
    
    return code_files

def download_file_content(download_url: str) -> str:
    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return ""

# AI Analysis

def analyze_with_ai(assignment_description: str, repo_info: Dict, code_files: List[Dict]) -> Dict[str, Any]:

    prompt = f"""
    Analyze this GitHub repository to see if it matches the given assignment.
    
    ASSIGNMENT:
    {assignment_description}
    
    REPOSITORY INFO:
    - Name: {repo_info['name']}
    - Description: {repo_info['description']}
    - Languages: {', '.join(repo_info['languages'])}
    - Size: {repo_info['size']} KB
    
    CODE FILES:
    """

    for file in code_files:
        prompt += f"\n--- {file['name']} ---\n{file['content']}\n"
    
    prompt += """
    
    Please analyze and provide:
    1. Score from 0.0 to 1.0 (how well does it match?)
    2. Clear explanation
    3. 3 specific suggestions for improvement
    
    Format your response as:
    SCORE: [number]
    EXPLANATION: [your analysis]
    SUGGESTIONS: [suggestion 1] | [suggestion 2] | [suggestion 3]
    """
    
    try:
        response = model.generate_content(prompt)
        return parse_ai_response(response.text)
        
    except Exception as e:
        return {
            "score": 0.5,
            "explanation": f"AI analysis unavailable: {str(e)}",
            "suggestions": ["Review code structure", "Add documentation", "Test functionality"]
        }

# AI Response

def parse_ai_response(ai_text: str) -> Dict[str, Any]:
    try:
        lines = ai_text.split('\n')
        score = 0.5
        explanation = "Analysis completed"
        suggestions = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('SCORE:'):
                score_text = line.replace('SCORE:', '').strip()
                score = float(score_text)
            elif line.startswith('EXPLANATION:'):
                explanation = line.replace('EXPLANATION:', '').strip()
            elif line.startswith('SUGGESTIONS:'):
                suggestions_text = line.replace('SUGGESTIONS:', '').strip()
                suggestions = [s.strip() for s in suggestions_text.split('|')]
        
        return {
            "score": max(0.0, min(1.0, score)),  # 0 to 1
            "explanation": explanation,
            "suggestions": suggestions[:3]
        }
        
    except:
        return {
            "score": 0.5,
            "explanation": "Could not parse AI response",
            "suggestions": ["Review requirements", "Improve code quality", "Add tests"]
        }


if __name__ == "__main__":
    import uvicorn
    print("Starting GitHub Repository Analyzer...")
    print("API Documentation: http://localhost:8080/docs")
    print("Home: http://localhost:8080")
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
