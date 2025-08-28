# GitHub Repository Analyzer API Integration Guide

## Overview
This API service analyzes public GitHub repositories against assignment requirements and detects AI-generated vs human-written code patterns.

## API Endpoints

### 1. Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "GitHub Repository Analyzer API"
}
```

### 2. Repository Validation
```
POST /validate
Content-Type: application/json

{
  "repo_url": "https://github.com/owner/repo"
}
```
**Response:**
```json
{
  "valid": true,
  "repository": "owner/repo",
  "languages": ["Python", "JavaScript"]
}
```

### 3. Repository Analysis (Main Endpoint)
```
POST /analyze
Content-Type: application/json

{
  "repo_url": "https://github.com/owner/repo",
  "assignment_description": "Create a calculator that can add and subtract numbers"
}
```

**Response:**
```json
{
  "success": true,
  "repository_info": {
    "name": "repo",
    "full_name": "owner/repo",
    "description": "A simple calculator",
    "languages": ["Python"],
    "stars": 15,
    "forks": 3,
    "total_commits": 12,
    "contributors": 2
  },
  "assignment_match_score": 0.85,
  "explanation": "Well-structured calculator implementation...",
  "suggestions": [
    "Add error handling for division by zero",
    "Include unit tests",
    "Add documentation"
  ],
  "ai_detection_score": 0.3,
  "ai_detection_details": {
    "assessment": "Likely Human-written",
    "confidence": 0.4,
    "comments": "Comment density: 12/100 lines",
    "structure": "Structure analysis completed",
    "naming": "Variable naming patterns analyzed",
    "error_handling": "Error handling patterns analyzed",
    "metadata": "Commits: 12, Description analyzed"
  }
}
```

## Integration Methods

### 1. Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 2. Platform Integration Examples

#### Python/Django Platform
```python
import requests

def analyze_repository(repo_url, assignment_desc):
    response = requests.post(
        "http://your-api-service:8080/analyze",
        json={
            "repo_url": repo_url,
            "assignment_description": assignment_desc
        }
    )
    return response.json()
```

#### Node.js/Express Platform
```javascript
const axios = require('axios');

async function analyzeRepository(repoUrl, assignmentDesc) {
    const response = await axios.post('http://your-api-service:8080/analyze', {
        repo_url: repoUrl,
        assignment_description: assignmentDesc
    });
    return response.data;
}
```

#### cURL Example
```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/owner/repo",
    "assignment_description": "Create a web scraper"
  }'
```

### 3. Microservice Architecture

#### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: repo-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: repo-analyzer
  template:
    metadata:
      labels:
        app: repo-analyzer
    spec:
      containers:
      - name: api
        image: repo-analyzer:latest
        ports:
        - containerPort: 8080
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: gemini-key
---
apiVersion: v1
kind: Service
metadata:
  name: repo-analyzer-service
spec:
  selector:
    app: repo-analyzer
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### 4. Environment Configuration

Required environment variables:
```env
OPENAI_API_KEY=your_openai_api_key
```

Optional configuration:
```env
API_HOST=0.0.0.0
API_PORT=8080
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-platform.com
```

## Error Handling

### Common Error Responses
```json
{
  "detail": "Invalid GitHub URL format. Use: https://github.com/owner/repo"
}
```

### Error Codes
- `400`: Bad Request (invalid URL, no code files)
- `404`: Repository not found or private
- `500`: Internal server error (API failures)

## Rate Limiting & Performance

- **GitHub API**: 60 requests/hour for unauthenticated requests
- **OpenAI API**: Depends on your API key tier and model usage
- **Processing Time**: 5-15 seconds per repository
- **Concurrent Requests**: Supports multiple simultaneous analyses

## Security Considerations

1. **API Key Protection**: Store Gemini API key securely
2. **CORS Configuration**: Restrict origins in production
3. **Input Validation**: All URLs are validated before processing
4. **Rate Limiting**: Implement rate limiting on your platform side

## Monitoring & Logging

### Health Monitoring
```python
# Check API health
response = requests.get("http://your-api:8080/health")
if response.json()["status"] != "healthy":
    # Handle service down
```

### Logging
The API logs all requests and errors. Monitor for:
- Failed repository access
- Gemini API failures
- Processing timeouts

## Scaling Recommendations

1. **Horizontal Scaling**: Deploy multiple API instances
2. **Caching**: Cache repository data for repeated analyses
3. **Queue System**: Use Redis/Celery for async processing
4. **Load Balancer**: Distribute requests across instances
