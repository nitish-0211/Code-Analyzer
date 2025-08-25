from typing import List, Dict, Any

#code pattern analysis to check if code is AI-generated or human-written
#scoring: 0 human, 1 = AI.

def detect_ai_generated_code(code_files: List[Dict[str, str]], repo_info: Dict) -> Dict[str, Any]:

    if not code_files:
        return {"score": 0.5, "details": {"reason": "No code files to analyze"}}
    
    ai_indicators = 0
    human_indicators = 0
    total_checks = 0
    details = {}
    
    all_code = "\n".join([file["content"] for file in code_files])
    
    # code comments analysis
    comment_analysis = analyze_comments(all_code)
    ai_indicators += comment_analysis["ai_score"]
    human_indicators += comment_analysis["human_score"]
    total_checks += 1
    details["comments"] = comment_analysis["details"]
    
    # code structure analysis
    structure_analysis = analyze_code_structure(all_code)
    ai_indicators += structure_analysis["ai_score"]
    human_indicators += structure_analysis["human_score"]
    total_checks += 1
    details["structure"] = structure_analysis["details"]
    
    # variable naming analysis
    naming_analysis = analyze_variable_naming(all_code)
    ai_indicators += naming_analysis["ai_score"]
    human_indicators += naming_analysis["human_score"]
    total_checks += 1
    details["naming"] = naming_analysis["details"]
    
    # error handling analysis
    error_analysis = analyze_error_handling(all_code)
    ai_indicators += error_analysis["ai_score"]
    human_indicators += error_analysis["human_score"]
    total_checks += 1
    details["error_handling"] = error_analysis["details"]
    
    # repository metadata analysis
    metadata_analysis = analyze_repo_metadata(repo_info)
    ai_indicators += metadata_analysis["ai_score"]
    human_indicators += metadata_analysis["human_score"]
    total_checks += 1
    details["metadata"] = metadata_analysis["details"]
    
    # scoring
    if total_checks > 0:
        ai_ratio = ai_indicators / total_checks
        human_ratio = human_indicators / total_checks
        
        if ai_ratio + human_ratio > 0:
            final_score = ai_ratio / (ai_ratio + human_ratio)
        else:
            final_score = 0.5
    else:
        final_score = 0.5
    
    if final_score < 0.3:
        assessment = "Likely Human-written"
    elif final_score < 0.7:
        assessment = "Mixed/Uncertain"
    else:
        assessment = "Likely AI-generated"
    
    details["assessment"] = assessment
    details["confidence"] = abs(final_score - 0.5) * 2
    
    return {
        "score": final_score,
        "details": details
    }


#analyze comments
def analyze_comments(code: str) -> Dict[str, Any]:
    ai_score = 0
    human_score = 0
    
    ai_comment_patterns = [
        "This function",
        "This method",
        "Initialize the",
        "Create a new",
        "Returns the result",
        "Performs the operation",
        "Handles the request"
    ]
    
    human_comment_patterns = [
        "TODO",
        "FIXME",
        "HACK",
        "NOTE:",
        "BUG:",
        "XXX",
        "wtf",
        "temp",
        "quick fix"
    ]
    
    code_lower = code.lower()
    
    for pattern in ai_comment_patterns:
        if pattern.lower() in code_lower:
            ai_score += 0.2
    
    for pattern in human_comment_patterns:
        if pattern.lower() in code_lower:
            human_score += 0.3
    
    lines = code.split('\n')
    comment_lines = [line for line in lines if line.strip().startswith('#') or line.strip().startswith('//')]
    
    if len(lines) > 0:
        comment_ratio = len(comment_lines) / len(lines)
        if comment_ratio > 0.3: 
            ai_score += 0.3
        elif comment_ratio < 0.05: 
            human_score += 0.2
    
    return {
        "ai_score": min(ai_score, 1.0),
        "human_score": min(human_score, 1.0),
        "details": f"Comment density: {len(comment_lines)}/{len(lines)} lines"
    }


#code structure analysis
def analyze_code_structure(code: str) -> Dict[str, Any]:
    ai_score = 0
    human_score = 0
    
    if "def main():" in code and "if __name__ == '__main__':" in code:
        ai_score += 0.3
    
    lines = code.split('\n')
    consistent_indentation = True
    for line in lines:
        if line.strip() and not (line.startswith('    ') or line.startswith('\t') or not line.startswith(' ')):
            consistent_indentation = False
            break
    
    if consistent_indentation and len(lines) > 20:
        ai_score += 0.2
    
    if 'print(' in code and 'console.log' in code:  
        human_score += 0.3
    
    return {
        "ai_score": min(ai_score, 1.0),
        "human_score": min(human_score, 1.0),
        "details": f"Structure analysis completed"
    }


# variables analysis
def analyze_variable_naming(code: str) -> Dict[str, Any]:
    ai_score = 0
    human_score = 0
    
    ai_patterns = [
        "user_input",
        "result_data",
        "response_object",
        "input_parameter",
        "output_value",
        "temp_variable",
        "current_index"
    ]
    
    human_patterns = [
        " i ",
        " j ",
        " x ",
        " y ",
        " tmp ",
        " temp ",
        " val ",
        " idx "
    ]
    
    code_lower = code.lower()
    
    for pattern in ai_patterns:
        if pattern in code_lower:
            ai_score += 0.1
    
    for pattern in human_patterns:
        if pattern in code_lower:
            human_score += 0.15
    
    return {
        "ai_score": min(ai_score, 1.0),
        "human_score": min(human_score, 1.0),
        "details": "Variable naming patterns analyzed"
    }


# error handling patterns 
def analyze_error_handling(code: str) -> Dict[str, Any]:
    ai_score = 0
    human_score = 0
    
    if "try:" in code and "except Exception as e:" in code:
        ai_score += 0.4
    
    if "try:" in code and "except:" in code and "Exception" not in code:
        human_score += 0.3
    
    if "print(" in code and ("debug" in code.lower() or "test" in code.lower()):
        human_score += 0.2
    
    return {
        "ai_score": min(ai_score, 1.0),
        "human_score": min(human_score, 1.0),
        "details": "Error handling patterns analyzed"
    }


#repo metadata
def analyze_repo_metadata(repo_info: Dict) -> Dict[str, Any]:
    ai_score = 0
    human_score = 0
    
    total_commits = repo_info.get("total_commits", 0)
    
    if total_commits <= 3:
        ai_score += 0.3
    elif total_commits > 20:
        human_score += 0.2
    
    description = repo_info.get("description", "").lower()
    if any(word in description for word in ["generated", "automated", "ai", "chatgpt", "gpt"]):
        ai_score += 0.5
    
    return {
        "ai_score": min(ai_score, 1.0),
        "human_score": min(human_score, 1.0),
        "details": f"Commits: {total_commits}, Description analyzed"
    }
