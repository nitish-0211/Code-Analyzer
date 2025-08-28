import os
from openai import OpenAI
from typing import List, Dict, Any
import json


# repo analysis (OpenAI)
def analyze_with_ai(code_files: List[Dict[str, str]], repo_info: Dict, assignment_description: str) -> Dict[str, Any]:
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise Exception("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=api_key)
    
    code_content = ""
    for file in code_files:
        code_content += f"\n--- {file['name']} ---\n{file['content']}\n"

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
    3. List the programming languages found in the code

    Format your response as JSON with these keys:
    - assignment_match_score (float)
    - explanation (string)
    - languages_found (array of strings)
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a code analysis expert. Analyze code repositories and provide detailed assessments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
        except:
            result = {
                "assignment_match_score": 0.7,
                "explanation": response.choices[0].message.content,
                "languages_found": repo_info.get('languages', [])
            }
        
        return result
        
    except Exception as e:
        return {
            "assignment_match_score": 0.5,
            "explanation": f"AI analysis failed: {str(e)}. Basic analysis completed based on repository structure.",
            "languages_found": repo_info.get('languages', [])
        }
