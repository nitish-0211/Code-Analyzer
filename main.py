import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from github_api import get_public_repository_info, get_public_code_files, validate_github_url
from ai_detection import detect_ai_generated_code
from analysis import analyze_with_ai

load_dotenv()

app = FastAPI(
    title="GitHub Repository Analyzer API",
    description="API service to analyze public GitHub repositories against assignment requirements with AI detection",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configuration based on platform's domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalyzeRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL (public repos only)")
    assignment_description: str = Field(..., description="Description of the assignment requirements")

class RepositoryInfo(BaseModel):
    name: str
    full_name: str
    description: Optional[str]
    languages: List[str]
    stars: int
    forks: int
    total_commits: int
    contributors: int

class AIDetectionDetails(BaseModel):
    assessment: str
    confidence: float
    comments: str
    structure: str
    naming: str
    error_handling: str
    metadata: str

class AnalyzeResponse(BaseModel):
    success: bool = True
    repository_info: RepositoryInfo
    assignment_match_score: float = Field(..., description="Score from 0.0 to 1.0")
    explanation: str
    ai_detection_score: float = Field(..., description="0.0 = likely human, 1.0 = likely AI")
    ai_detection_details: AIDetectionDetails

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: str


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "GitHub Repository Analyzer API"}


# Main analysis endpoint
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repository(request: AnalyzeRequest):
    try:
        # Validate GitHub URL
        if not validate_github_url(request.repo_url):
            raise HTTPException(
                status_code=400, 
                detail="Invalid GitHub URL format. Use: https://github.com/owner/repo"
            )
        
        repo_info = get_public_repository_info(request.repo_url)
        
        code_files = get_public_code_files(request.repo_url)
        
        if not code_files:
            raise HTTPException(
                status_code=400, 
                detail="No analyzable code files found in repository"
            )
        
        ai_detection = detect_ai_generated_code(code_files, repo_info)
        
        ai_analysis = analyze_with_ai(code_files, repo_info, request.assignment_description)
        
        return AnalyzeResponse(
            repository_info=RepositoryInfo(
                name=repo_info["name"],
                full_name=repo_info["full_name"],
                description=repo_info["description"],
                languages=repo_info["languages"],
                stars=repo_info["stars"],
                forks=repo_info["forks"],
                total_commits=repo_info["total_commits"],
                contributors=repo_info["contributors"]
            ),
            assignment_match_score=ai_analysis["assignment_match_score"],
            explanation=ai_analysis["explanation"],
            ai_detection_score=ai_detection["score"],
            ai_detection_details=AIDetectionDetails(**ai_detection["details"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Repository (accessible and public) validation endpoint
@app.post("/validate")
async def validate_repository(repo_url: str):
    try:
        if not validate_github_url(repo_url):
            return {"valid": False, "reason": "Invalid URL format"}
        
        repo_info = get_public_repository_info(repo_url)
        return {
            "valid": True, 
            "repository": repo_info["full_name"],
            "languages": repo_info["languages"]
        }
        
    except Exception as e:
        return {"valid": False, "reason": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Starting GitHub Repository Analyzer API...")
    print("API Documentation: http://localhost:8080/docs")
    print("Health Check: http://localhost:8080/health")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
