// GitHub Repository Analyzer JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyzeForm');
    const resultsSection = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');
    const analyzeBtn = form.querySelector('.analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const loading = analyzeBtn.querySelector('.loading');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {
            repo_url: formData.get('repo_url'),
            assignment_description: formData.get('assignment_description')
        };

        // Show loading state
        analyzeBtn.disabled = true;
        btnText.style.display = 'none';
        loading.style.display = 'inline';
        resultsSection.style.display = 'none';

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                displayResults(result);
            } else {
                displayError(result.detail || 'Analysis failed');
            }
        } catch (error) {
            displayError('Network error: ' + error.message);
        } finally {
            // Reset button state
            analyzeBtn.disabled = false;
            btnText.style.display = 'inline';
            loading.style.display = 'none';
        }
    });

    function displayResults(data) {
        const scoreClass = getScoreClass(data.assignment_match_score);
        const aiScoreClass = getScoreClass(1 - data.ai_detection_score); // Invert for display
        
        resultsContent.innerHTML = `
            <div class="result-card">
                <h3>📊 Assignment Match Analysis</h3>
                <div class="score-display">
                    <div class="score-circle ${scoreClass}">
                        ${Math.round(data.assignment_match_score * 100)}%
                    </div>
                    <div>
                        <strong>Repository:</strong> ${data.repository_name}<br>
                        <strong>Languages:</strong> ${data.languages_found.join(', ')}
                    </div>
                </div>
                <p><strong>Analysis:</strong> ${data.explanation}</p>
                
                <h4>💡 Suggestions for Improvement:</h4>
                <ul class="suggestions-list">
                    ${data.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                </ul>
            </div>

            <div class="result-card">
                <h3>📈 Repository Statistics</h3>
                <p><strong>Total Commits:</strong> ${data.total_commits}</p>
                <p><strong>Contributors:</strong> ${data.contributors}</p>
            </div>

            <div class="ai-detection">
                <h4>🤖 AI Detection Analysis</h4>
                <div class="score-display">
                    <div class="score-circle ${aiScoreClass}">
                        ${Math.round((1 - data.ai_detection_score) * 100)}%
                    </div>
                    <div>
                        <strong>Assessment:</strong> ${data.ai_detection_details.assessment}<br>
                        <strong>Confidence:</strong> ${Math.round(data.ai_detection_details.confidence * 100)}%
                    </div>
                </div>
                <div style="margin-top: 15px; font-size: 0.9em;">
                    <p><strong>Comments:</strong> ${data.ai_detection_details.comments}</p>
                    <p><strong>Structure:</strong> ${data.ai_detection_details.structure}</p>
                    <p><strong>Variables:</strong> ${data.ai_detection_details.naming}</p>
                    <p><strong>Error Handling:</strong> ${data.ai_detection_details.error_handling}</p>
                    <p><strong>Metadata:</strong> ${data.ai_detection_details.metadata}</p>
                </div>
            </div>
        `;
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function displayError(message) {
        resultsContent.innerHTML = `
            <div class="error-message">
                <strong>Error:</strong> ${message}
            </div>
        `;
        resultsSection.style.display = 'block';
    }

    function getScoreClass(score) {
        if (score >= 0.7) return 'score-high';
        if (score >= 0.4) return 'score-medium';
        return 'score-low';
    }
});
