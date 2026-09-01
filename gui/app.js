document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('searchBtn');
    const queryInput = document.getElementById('queryInput');
    const resultsList = document.getElementById('resultsList');
    const summaryDiv = document.getElementById('summary');
    const combinedScoreSpan = document.getElementById('combinedScore');
    const clearDbBtn = document.getElementById('clearDbBtn');

    searchBtn.addEventListener('click', performSearch);
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    clearDbBtn.addEventListener('click', clearDatabase);

    async function performSearch() {
        const query = queryInput.value.trim();
        if (!query) {
            alert('Please enter a query.');
            return;
        }

        const countSelection = document.querySelector('input[name="resultCount"]:checked').value;
        let topK = 10;

        try {
            searchBtn.disabled = true;
            searchBtn.textContent = 'Searching...';

            const searchRes = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    result_count: countSelection
                })
            });

            if (!searchRes.ok) throw new Error('Failed to query search API.');
            const searchData = await searchRes.json();
            
            renderResults(searchData.results, searchData.combined_score);
        } catch (error) {
            console.error(error);
            alert(`An error occurred: ${error.message}`);
        } finally {
            searchBtn.disabled = false;
            searchBtn.textContent = 'Search';
        }
    }

    function renderResults(docs, combinedScore) {
        resultsList.innerHTML = '';
        
        if (!docs || docs.length === 0) {
            resultsList.innerHTML = '<p>No results found.</p>';
            summaryDiv.classList.add('hidden');
            return;
        }

        docs.forEach((doc, index) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            
            // Format score to 3 decimal places
            const displayScore = doc.similarity.toFixed(3);
            
            card.innerHTML = `
                <div class="result-header">
                    <strong>Result #${index + 1} (ID: ${doc.id})</strong>
                    <span class="result-score">Similarity: ${displayScore}</span>
                </div>
                <button class="preview-btn" onclick="togglePreview('preview-${index}')">Show Preview</button>
                <div id="preview-${index}" class="preview-content hidden">
                    ${escapeHtml(doc.text || 'No text content available')}
                </div>
            `;
            resultsList.appendChild(card);
        });

        // Display combined score from backend
        combinedScoreSpan.textContent = combinedScore.toFixed(3);
        summaryDiv.classList.remove('hidden');
    }

    async function clearDatabase() {
        if (!confirm('Are you sure you want to delete all indexed records? This cannot be undone.')) {
            return;
        }

        try {
            clearDbBtn.disabled = true;
            clearDbBtn.textContent = 'Clearing...';

            // Delete all documents via the backend clear endpoint
            const res = await fetch('/api/clear', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!res.ok) throw new Error('Failed to clear database.');
            
            alert('Database cleared successfully.');
            resultsList.innerHTML = '<p>Database is empty.</p>';
            summaryDiv.classList.add('hidden');
        } catch (error) {
            console.error(error);
            alert(`An error occurred: ${error.message}`);
        } finally {
            clearDbBtn.disabled = false;
            clearDbBtn.textContent = 'Clear Database';
        }
    }

    // Expose togglePreview to global scope so inline onclick works
    window.togglePreview = function(id) {
        const el = document.getElementById(id);
        if (el.classList.contains('hidden')) {
            el.classList.remove('hidden');
        } else {
            el.classList.add('hidden');
        }
    };

    function escapeHtml(unsafe) {
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
});
