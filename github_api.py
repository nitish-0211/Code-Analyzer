import requests
from typing import List, Dict, Any
import re


# extracting repo info
def extract_repo_info(github_url: str) -> tuple:
    pattern = r'github\.com/([^/]+)/([^/]+)'
    match = re.search(pattern, github_url)
    
    if not match:
        raise ValueError("Invalid GitHub URL format")
    
    owner, repo = match.groups()
    repo = repo.replace('.git', '')
    
    return owner, repo


# fetching public repos
def get_public_repository_info(github_url: str) -> Dict[str, Any]:
    owner, repo = extract_repo_info(github_url)
    
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        response = requests.get(repo_url)
        
        if response.status_code == 404:
            raise Exception(f"Repository {owner}/{repo} not found or is private")
        elif response.status_code != 200:
            raise Exception(f"Failed to access repository: {response.status_code}")
        
        repo_data = response.json()
        
        # check programming languages
        languages_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
        languages_response = requests.get(languages_url)
        languages = list(languages_response.json().keys()) if languages_response.status_code == 200 else []
        
        # commit counts
        commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100"
        commits_response = requests.get(commits_url)
        if commits_response.status_code == 200:
            commits_data = commits_response.json()
            total_commits = len(commits_data)
            if total_commits == 100:
                total_commits = repo_data.get("size", 0) // 10 
        else:
            total_commits = 0
        
        # contributors
        contributors_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
        contributors_response = requests.get(contributors_url)
        if contributors_response.status_code == 200:
            contributors_data = contributors_response.json()
            contributors = len(contributors_data) if isinstance(contributors_data, list) else 1
        else:
            contributors = 1
        
        return {
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "description": repo_data.get("description", "No description"),
            "languages": languages,
            "size": repo_data["size"],
            "stars": repo_data["stargazers_count"],
            "forks": repo_data["forks_count"],
            "total_commits": total_commits,
            "contributors": contributors,
            "created_at": repo_data["created_at"],
            "updated_at": repo_data["updated_at"]
        }
        
    except requests.RequestException as e:
        raise Exception(f"Network error: {str(e)}")


# fetch codes
def get_public_code_files(github_url: str, max_files: int = 10) -> List[Dict[str, str]]:
    owner, repo = extract_repo_info(github_url)
    
    # Get repository contents
    contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    
    try:
        response = requests.get(contents_url)
        
        if response.status_code != 200:
            return []
        
        files_data = response.json()
        code_files = []
        
        important_extensions = ['.py', '.js', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.md', '.txt']
        
        for file_info in files_data[:max_files]:
            if file_info["type"] == "file":
                file_name = file_info["name"]
                
                if any(file_name.endswith(ext) for ext in important_extensions):
                    file_content = download_public_file_content(file_info["download_url"])
                    
                    if file_content:
                        code_files.append({
                            "name": file_name,
                            "content": file_content[:3000] 
                        })
        
        return code_files
        
    except requests.RequestException as e:
        print(f"Error fetching code files: {str(e)}")
        return []


# fetching file content
def download_public_file_content(download_url: str) -> str:
    try:
        response = requests.get(download_url, timeout=10)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        pass
    return ""


# url validation
def validate_github_url(url: str) -> bool:
    pattern = r'^https?://github\.com/[^/]+/[^/]+/?$'
    return bool(re.match(pattern, url.strip()))
