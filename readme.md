# GitHub Repository Analyzer with AI Detection

A comprehensive tool that analyzes GitHub repositories against assignment requirements and detects AI-generated vs human-written code patterns.

## 🚀 Features

### **Core Analysis**
- **OAuth Authentication**: Secure GitHub login with repository access
- **Assignment Matching**: AI-powered analysis using Google Gemini
- **Code Pattern Detection**: Identifies AI vs human-written code
- **Multi-language Support**: Python, JavaScript, Java, C++, and more

### **AI Detection Capabilities**
- **Comment Analysis**: Formal vs informal comment patterns
- **Code Structure**: Consistency and template-like patterns  
- **Variable Naming**: Descriptive vs contextual naming conventions
- **Error Handling**: Comprehensive vs basic error patterns
- **Repository Metadata**: Commit patterns and descriptions

## 📁 Project Structure

```
├── main.py              # FastAPI application with OAuth
├── github_api.py        # GitHub API interactions
├── ai_detection.py      # AI vs human code detection
├── analysis.py          # Google Gemini integration
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```

## ⚙️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file:
```env
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GEMINI_API_KEY=your_gemini_api_key
```

### 3. GitHub OAuth Setup
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create new OAuth App with callback URL: `http://localhost:8080/callback`
3. Copy Client ID and Secret to `.env`

### 4. Google Gemini API
1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to `.env` file

## 🏃 Running the Application

```bash
python main.py
```

Access the application:
- **Home**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

## 📊 Analysis Output

```json
{
  "repository_name": "user/project",
  "languages_found": ["Python", "JavaScript"],
  "assignment_match_score": 0.85,
  "explanation": "Well-structured implementation matching requirements",
  "suggestions": ["Add error handling", "Improve documentation"],
  "total_commits": 15,
  "contributors": 2,
  "ai_detection_score": 0.3,
  "ai_detection_details": {
    "assessment": "Likely Human-written",
    "confidence": 0.4,
    "comments": "Comment density: 12/100 lines",
    "structure": "Structure analysis completed",
    "naming": "Variable naming patterns analyzed",
    "error_handling": "Error handling patterns analyzed",
    "metadata": "Commits: 15, Description analyzed"
  }
}
```

## 🔍 AI Detection Scoring

- **0.0 - 0.3**: Likely Human-written
- **0.3 - 0.7**: Mixed/Uncertain  
- **0.7 - 1.0**: Likely AI-generated

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with GitHub login |
| `/login/github` | GET | Initiate OAuth flow |
| `/callback` | GET | OAuth callback handler |
| `/repositories` | GET | List user repositories |
| `/analyze` | POST | Analyze repository |

## 🧪 Testing

Test individual components:
```bash
python test_example.py
```

## 📋 Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Authlib**: OAuth implementation
- **Google Generative AI**: Gemini integration
- **Requests**: HTTP client
- **Python-dotenv**: Environment variables
