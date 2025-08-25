import os
import secrets
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import requests

# Import our custom modules
from github_api import get_user_repositories, get_repository_info, get_code_files
from ai_detection import detect_ai_generated_code
from analysis import analyze_with_ai

load_dotenv()

app = FastAPI(
    title="GitHub Repository Analyzer with OAuth",
    description="Authenticate with GitHub and analyze your repositories",
    version="2.0.0"
)

app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))

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
    ai_detection_score: float  # 0.0 = likely human, 1.0 = likely AI
    ai_detection_details: Dict[str, Any]

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
        
        # AI vs Human Detection
        ai_detection = detect_ai_generated_code(code_files, repo_info)
        
        # AI-Analysis
        ai_analysis = analyze_with_ai(code_files, repo_info, assignment_description)
        
        return AnalyzeResponse(
            repository_name=repo_full_name,
            languages_found=ai_analysis["languages_found"],
            assignment_match_score=ai_analysis["assignment_match_score"],
            explanation=ai_analysis["explanation"],
            suggestions=ai_analysis["suggestions"],
            total_commits=repo_info["total_commits"],
            contributors=repo_info["contributors"],
            ai_detection_score=ai_detection["score"],
            ai_detection_details=ai_detection["details"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    print("Starting GitHub Repository Analyzer...")
    print("API Documentation: http://localhost:8080/docs")
    print("Home: http://localhost:8080")
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
