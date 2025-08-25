
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import requests
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from authlib.integrations.starlette_client import OAuth
import secrets

load_dotenv()

app = FastAPI(
    title="GitHub Repository Analyzer with OAuth",
    description="Authenticate with GitHub and analyze your repositories",
    version="2.0.0"
)

app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))

# templates
templates = Jinja2Templates(directory="templates")

# OAuth configuration
oauth = OAuth()
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={
        'scope': 'user:email repo'
    }
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

user_sessions = {}

# Data-models
class Repository(BaseModel):
    name: str
    full_name: str
    description: Optional[str]
    language: Optional[str]
    private: bool
    updated_at: str
    html_url: str

class AnalyzeRequest(BaseModel):
    repo_full_name: str 
    assignment_description: str

class AnalyzeResponse(BaseModel):
    repository_name: str
    languages_found: List[str]
    assignment_match_score: float
    explanation: str
    suggestions: List[str]
    total_commits: int
    contributors: int

# OAUTH ENDPOINTS

@app.get("/")
async def home(request: Request):
    return HTMLResponse("""
    <html>
        <head><title>GitHub Repository Analyzer</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>GitHub Repository Analyzer</h1>
            <p>Authenticate with GitHub to analyze your repositories</p>
            <a href="/login/github" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                Login with GitHub
            </a>
            <br><br>
            <p><a href="/docs">API Documentation</a></p>
        </body>
    </html>
    """)

@app.get("/login/github")
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.github.authorize_redirect(request, redirect_uri)

@app.get("/callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.github.authorize_access_token(request)
        
        # Get user info from GitHub API
        headers = {'Authorization': f'token {token["access_token"]}'}
        user_response = requests.get('https://api.github.com/user', headers=headers)
        user_info = user_response.json() if user_response.status_code == 200 else None
        
        if user_info:
            # sessions
            session_id = secrets.token_urlsafe(32)
            user_sessions[session_id] = {
                'access_token': token['access_token'],
                'user': user_info,
                'username': user_info.get('login')
            }
            
            return RedirectResponse(url=f"/repositories?session={session_id}")
        else:
            raise HTTPException(status_code=400, detail="Failed to get user info")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.get("/repositories")
async def list_repositories(request: Request, session: str):
    if session not in user_sessions:
        return RedirectResponse(url="/")
    
    user_session = user_sessions[session]
    access_token = user_session['access_token']
    username = user_session['username']
    
    repos = get_user_repositories(access_token)
    
    repo_options = ""
    for repo in repos:
        repo_options += f"""
        <div style="border: 1px solid #ddd; margin: 10px; padding: 15px; border-radius: 5px;">
            <h3>{repo['name']}</h3>
            <p>{repo['description'] or 'No description'}</p>
            <p><strong>Language:</strong> {repo['language'] or 'Not specified'}</p>
            <p><strong>Updated:</strong> {repo['updated_at'][:10]}</p>
            <a href="/analyze-form?session={session}&repo={repo['full_name']}" 
               style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px;">
                Analyze This Repository
            </a>
        </div>
        """
    
    return HTMLResponse(f"""
    <html>
        <head><title>Your Repositories</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>Your GitHub Repositories</h1>
            <p>Welcome, {username}! Select a repository to analyze:</p>
            {repo_options}
            <br>
            <a href="/">← Back to Home</a>
        </body>
    </html>
    """)

@app.get("/analyze-form")
async def analyze_form(request: Request, session: str, repo: str):
    if session not in user_sessions:
        return RedirectResponse(url="/")
    
    return HTMLResponse(f"""
    <html>
        <head><title>Analyze Repository</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>Analyze Repository: {repo}</h1>
            <form action="/analyze" method="post">
                <input type="hidden" name="session" value="{session}">
                <input type="hidden" name="repo_full_name" value="{repo}">
                <label for="assignment">Assignment Description:</label><br>
                <textarea name="assignment_description" rows="5" cols="60" required 
                    placeholder="Describe what the assignment should do..."></textarea><br><br>
                <button type="submit" style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 3px;">
                    Analyze Repository
                </button>
            </form>
            <br>
            <a href="/repositories?session={session}">← Back to Repositories</a>
        </body>
    </html>
    """)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repository(request: Request):
    form = await request.form()
    session = form.get("session")
    repo_full_name = form.get("repo_full_name")
    assignment_description = form.get("assignment_description")
    
    if session not in user_sessions:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user_session = user_sessions[session]
    access_token = user_session['access_token']
    
    try:
        repo_info = get_repository_info(repo_full_name, access_token)
        code_files = get_code_files(repo_full_name, access_token)
        
        # AI-Analysis
        ai_analysis = analyze_with_ai(
            assignment_description=assignment_description,
            repo_info=repo_info,
            code_files=code_files
        )
        
        return AnalyzeResponse(
            repository_name=repo_full_name,
            languages_found=repo_info["languages"],
            assignment_match_score=ai_analysis["score"],
            explanation=ai_analysis["explanation"],
            suggestions=ai_analysis["suggestions"],
            total_commits=repo_info["total_commits"],
            contributors=repo_info["contributors"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# FUNCTIONS

def get_user_repositories(access_token: str) -> List[Dict]:
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get('https://api.github.com/user/repos', headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repositories: {response.status_code}")
    
    repos = response.json()
    
    return [{
        'name': repo['name'],
        'full_name': repo['full_name'],
        'description': repo['description'],
        'language': repo['language'],
        'private': repo['private'],
        'updated_at': repo['updated_at'],
        'html_url': repo['html_url']
    } for repo in repos]

# Repo Info

def get_repository_info(repo_full_name: str, access_token: str) -> Dict[str, Any]:
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    repo_url = f"https://api.github.com/repos/{repo_full_name}"
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 404:
        raise Exception(f"Repository {repo_full_name} not found")
    elif response.status_code != 200:
        raise Exception(f"Failed to access repository: {response.status_code}")
    
    repo_data = response.json()
    
    # check programming languages
    languages_url = f"https://api.github.com/repos/{repo_full_name}/languages"
    languages_response = requests.get(languages_url, headers=headers)
    languages = list(languages_response.json().keys()) if languages_response.status_code == 200 else []
    
    # commit counts
    commits_url = f"https://api.github.com/repos/{repo_full_name}/commits?per_page=100"
    commits_response = requests.get(commits_url, headers=headers)
    if commits_response.status_code == 200:
        commits_data = commits_response.json()
        total_commits = len(commits_data)
        if total_commits == 100:
            total_commits = repo_data.get("size", 0) // 10
    else:
        total_commits = 0
    
    # contributors
    contributors_url = f"https://api.github.com/repos/{repo_full_name}/contributors"
    contributors_response = requests.get(contributors_url, headers=headers)
    if contributors_response.status_code == 200:
        contributors_data = contributors_response.json()
        contributors = len(contributors_data) if isinstance(contributors_data, list) else 1
    else:
        contributors = 1  
    
    return {
        "name": repo_data["name"],
        "description": repo_data.get("description", "No description"),
        "languages": languages,
        "size": repo_data["size"],
        "stars": repo_data["stargazers_count"],
        "total_commits": total_commits,
        "contributors": contributors
    }

def get_code_files(repo_full_name: str, access_token: str, max_files: int = 5) -> List[Dict[str, str]]:
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    contents_url = f"https://api.github.com/repos/{repo_full_name}/contents"
    response = requests.get(contents_url, headers=headers)
    
    if response.status_code != 200:
        return []
    
    files_data = response.json()
    code_files = []
    
    important_extensions = ['.py', '.js', '.java', '.cpp', '.c', '.md', '.txt']
    
    for file_info in files_data[:max_files]:
        if file_info["type"] == "file":
            file_name = file_info["name"]
            
            if any(file_name.endswith(ext) for ext in important_extensions):
                file_content = download_file_content(file_info["download_url"], access_token)
                
                if file_content:
                    code_files.append({
                        "name": file_name,
                        "content": file_content[:2000]
                    })
    
    return code_files

def download_file_content(download_url: str, access_token: str) -> str:
    try:
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(download_url, headers=headers)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return ""

# AI ANALYSIS

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
