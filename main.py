import os
from typing import List, Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our custom modules
from github_api import get_public_repository_info, get_public_code_files, validate_github_url
from ai_detection import detect_ai_generated_code
from analysis import analyze_with_ai

load_dotenv()

app = FastAPI(
    title="GitHub Repository Analyzer",
    description="Analyze public GitHub repositories against assignment requirements",
    version="3.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Data models
class AnalyzeRequest(BaseModel):
    repo_url: str
    assignment_description: str

class AnalyzeResponse(BaseModel):
    repository_name: str
    languages_found: List[str]
    assignment_match_score: float
    explanation: str
    suggestions: List[str]
    total_commits: int
    contributors: int
    ai_detection_score: float
    ai_detection_details: Dict[str, Any]

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repository(request: AnalyzeRequest):
    try:
        if not validate_github_url(request.repo_url):
            raise HTTPException(status_code=400, detail="Invalid GitHub URL format")
        
        repo_info = get_public_repository_info(request.repo_url)
        
        code_files = get_public_code_files(request.repo_url)
        
        if not code_files:
            raise HTTPException(status_code=400, detail="No code files found in repository")
        
        ai_detection = detect_ai_generated_code(code_files, repo_info)
        
        ai_analysis = analyze_with_ai(code_files, repo_info, request.assignment_description)
        
        return AnalyzeResponse(
            repository_name=repo_info["full_name"],
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
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting GitHub Repository Analyzer...")
    print("Home: http://localhost:8080")
    print("API Documentation: http://localhost:8080/docs")
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
