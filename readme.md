# GitHub Repository Analyzer

## Key Features

1. **Takes input**: GitHub URL + assignment description
2. **Gets repository info**: Uses GitHub API to get basic details
3. **Analyzes with AI**: Uses Google Gemini to check if code matches assignment
4. **Returns results**: Score, explanation, and suggestions

## Execution

1. **Install packages**:
   ```
   pip install -r requirements.txt
   ```

2. **Starting the server**:
   ```
   python simple_main.py
   ```

3. **Testing**:
   ```
   python simple_test.py
   ```

4. **Use the web interface**:
   - Open: http://localhost:8080/docs
   - Try the `/analyze` endpoint

## Code Structure

### Main Functions:

1. **`analyze_repo()`** - Main function that coordinates everything
2. **`get_repo_name()`** - Extracts "user/repo" from GitHub URL
3. **`get_repo_info()`** - Gets repository details from GitHub API
4. **`get_some_code_files()`** - Downloads a few code files to analyze
5. **`ask_ai_to_analyze()`** - Sends everything to AI for analysis
6. **`parse_ai_answer()`** - Converts AI response to structured data

### Data Flow:
```
GitHub URL → Extract repo name → Get repo info → Download code → Ask AI → Parse response → Return results
```

## Example Usage

**Input:**
- URL: `https://github.com/user/calculator`
- Assignment: `Create a calculator that can add and subtract`

**Output:**
```json
{
  "repository": "user/calculator",
  "languages": ["Python"],
  "score": 85,
  "explanation": "Good calculator implementation with basic operations",
  "suggestions": ["Add multiplication", "Improve error handling", "Add tests"]
}
```

## Functionalities

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `analyze_repo()` | Main coordinator | URL + assignment | Analysis results |
| `get_repo_name()` | Extract repo name | GitHub URL | "user/repo" |
| `get_repo_info()` | Get repo details | Repo name | Repo information |
| `ask_ai_to_analyze()` | AI analysis | Repo info + assignment | AI response |
