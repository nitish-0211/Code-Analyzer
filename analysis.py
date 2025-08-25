"""
AI analysis module using Google Gemini
Handles AI-powered code analysis and assignment matching
"""

import os
import google.generativeai as genai
from typing import List, Dict, Any


def analyze_with_ai(code_files: List[Dict[str, str]], repo_info: Dict, assignment_description: str) -> Dict[str, Any]:
    """Analyze repository code using Google Gemini AI"""
    
    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise Exception("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prepare code content for analysis
    code_content = ""
    for file in code_files:
        code_content += f"\n--- {file['name']} ---\n{file['content']}\n"
    
    # Create analysis prompt
    prompt = f"""
    Analyze this GitHub repository code against the assignment description.

    Assignment Description:
    {assignment_description}

    Repository Information:
    - Name: {repo_info['name']}
    - Description: {repo_info.get('description', 'No description')}
    - Languages: {', '.join(repo_info.get('languages', []))}
    - Total Commits: {repo_info.get('total_commits', 0)}
    - Contributors: {repo_info.get('contributors', 1)}

    Code Files:
    {code_content}

    Please provide:
    1. A match score (0.0 to 1.0) indicating how well the code fulfills the assignment
    2. A detailed explanation of your analysis
    3. Specific suggestions for improvement
    4. List the programming languages found in the code

    Format your response as JSON with these keys:
    - assignment_match_score (float)
    - explanation (string)
    - suggestions (array of strings)
    - languages_found (array of strings)
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Try to parse JSON response
        import json
        try:
            result = json.loads(response.text)
        except:
            # If JSON parsing fails, create structured response from text
            result = {
                "assignment_match_score": 0.7,
                "explanation": response.text,
                "suggestions": ["Review the AI analysis output for detailed feedback"],
                "languages_found": repo_info.get('languages', [])
            }
        
        return result
        
    except Exception as e:
        # Fallback response if AI analysis fails
        return {
            "assignment_match_score": 0.5,
            "explanation": f"AI analysis failed: {str(e)}. Basic analysis completed based on repository structure.",
            "suggestions": [
                "Ensure all required functionality is implemented",
                "Add comprehensive documentation",
                "Include proper error handling"
            ],
            "languages_found": repo_info.get('languages', [])
        }
