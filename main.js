async function analyzeGeneration() {
    const joinDateInput = document.getElementById('joinDate');
    const joinDate = joinDateInput.value;

    if (!joinDate) {
        showError('가입일을 입력해주세요.');
        joinDateInput.focus();
        return;
    }

    // UI Update
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('result').classList.add('hidden');
    document.querySelector('.input-section').classList.add('hidden');

    try {
        // Backend API Call
        const response = await fetch('/api/analyze-insurance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ join_date: joinDate })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || '분석 중 오류가 발생했습니다.');
        }

        displayResult(result);

    } catch (error) {
        showError(error.message);
        document.querySelector('.input-section').classList.remove('hidden');
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}

function displayResult(result) {
    // Badge Update
    const badge = document.getElementById('generationBadge');
    badge.innerHTML = `
        <h2>${result.generation}세대 실손</h2>
        <p>${result.generation_name}</p>
    `;

    // Content Update
    const content = document.getElementById('explanationContent');
    // Use marked library if available, otherwise fallback to simple text
    if (typeof marked !== 'undefined') {
        content.innerHTML = marked.parse(result.explanation);
    } else {
        content.textContent = result.explanation;
        console.warn('Marked.js not loaded');
    }

    // Show Result
    document.getElementById('result').classList.remove('hidden');

    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');

    // Auto hide after 3 seconds
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 3000);
}

function resetForm() {
    document.getElementById('result').classList.add('hidden');
    document.querySelector('.input-section').classList.remove('hidden');
    document.getElementById('joinDate').value = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Allow Enter key to submit
document.getElementById('joinDate').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        analyzeGeneration();
    }
});
