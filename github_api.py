import requests
from typing import List, Dict, Any


# fetch github repo's.
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
    
    # checking programming languages
    languages_url = f"https://api.github.com/repos/{repo_full_name}/languages"
    languages_response = requests.get(languages_url, headers=headers)
    languages = list(languages_response.json().keys()) if languages_response.status_code == 200 else []
    
    # fetch commits
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
