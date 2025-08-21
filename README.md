# Simple GitHub Repository Analyzer

A beginner-friendly FastAPI application that analyzes GitHub repositories to check if they match assignment requirements using AI.

## 🚀 Features

- **Simple API**: Easy-to-understand endpoints
- **GitHub Integration**: Analyzes any public GitHub repository
- **AI Analysis**: Uses Google Gemini to evaluate code quality and assignment alignment
- **Detailed Reports**: Provides scores, explanations, and improvement suggestions
- **Entry-Level Friendly**: Clean, well-commented code that's easy to learn from

## 📋 Requirements

- Python 3.8+
- Google Gemini API key
- Internet connection (for GitHub API and AI analysis)

## 🛠️ Setup

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file with:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Open your browser**:
   - API Documentation: http://localhost:8000/docs
   - Home page: http://localhost:8000

## 📖 How to Use

### API Endpoint: `/analyze`

Send a POST request with:
```json
{
  "github_url": "https://github.com/username/repository",
  "assignment_description": "Create a calculator that can add, subtract, multiply and divide numbers"
}
```

### Response:
```json
{
  "repository_name": "username/repository",
  "languages_found": ["Python", "JavaScript"],
  "assignment_match_score": 0.85,
  "explanation": "The repository contains a well-structured calculator...",
  "suggestions": [
    "Add unit tests",
    "Improve error handling",
    "Add documentation"
  ],
  "total_commits": 15,
  "contributors": 2
}
```

## 🎯 What It Analyzes

1. **Repository Structure**: Languages used, file organization
2. **Code Quality**: Readability, structure, best practices
3. **Assignment Match**: How well the code fulfills requirements
4. **Development Practices**: Commit history, collaboration

## 🔧 How It Works

1. **Extract Info**: Parses GitHub URL to get owner/repository
2. **Fetch Data**: Uses GitHub API to get repository information
3. **Download Code**: Gets important code files for analysis
4. **AI Analysis**: Uses Google Gemini to evaluate the code
5. **Generate Report**: Returns structured analysis with scores and suggestions

## 📁 Project Structure

```
windsurf-project/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .env                # Environment variables (API keys)
└── README.md           # This file
```

## 🚨 Important Notes

- Only analyzes **public** GitHub repositories
- Limited to first 5 files and 2000 characters per file
- Requires valid Gemini API key
- Rate limited by GitHub API (60 requests/hour without auth)

## 🎓 Learning Points

This project demonstrates:
- **FastAPI**: Modern Python web framework
- **API Integration**: Working with GitHub's REST API
- **AI Integration**: Using Google Gemini for code analysis
- **Error Handling**: Graceful failure management
- **Data Validation**: Using Pydantic models
- **Environment Variables**: Secure API key management

## 🔮 Future Improvements

- Add GitHub authentication for private repos
- Support for more file types
- Batch analysis of multiple repositories
- Web interface for easier use
- Caching for faster repeated analysis

## 📞 Support

If you encounter issues:
1. Check your `.env` file has the correct API key
2. Ensure the GitHub repository is public
3. Verify your internet connection
4. Check the API documentation at `/docs`

---

**Happy Coding!** 🎉
