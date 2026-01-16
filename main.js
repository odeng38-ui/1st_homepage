// --- Modal Logic ---
function openSettings() {
    document.getElementById('settingsModal').classList.remove('hidden');
    loadSavedKeys();
}

function closeSettings() {
    document.getElementById('settingsModal').classList.add('hidden');
    document.getElementById('testStatus').classList.add('hidden');
}

async function loadSavedKeys() {
    try {
        const response = await fetch('/api/get-keys');
        const data = await response.json();
        if (data.google) document.getElementById('googleKey').value = data.google;
        if (data.openai) document.getElementById('openaiKey').value = data.openai;
        if (data.anthropic) document.getElementById('anthropicKey').value = data.anthropic;
    } catch (err) {
        console.error('Failed to load keys:', err);
    }
}

async function saveSettings() {
    const keys = {
        google: document.getElementById('googleKey').value,
        openai: document.getElementById('openaiKey').value,
        anthropic: document.getElementById('anthropicKey').value
    };

    try {
        const response = await fetch('/api/save-keys', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(keys)
        });
        const result = await response.json();
        if (response.ok) {
            showStatus('성공적으로 저장되었습니다.', 'success');
            setTimeout(closeSettings, 1000);
        } else {
            showStatus(result.error || '저장 중 오류가 발생했습니다.', 'error');
        }
    } catch (err) {
        showStatus('서버 연결 실패', 'error');
    }
}

async function testConnection(provider) {
    const key = document.getElementById(`${provider}Key`).value;
    if (!key) {
        showStatus('키를 입력해주세요.', 'error');
        return;
    }

    showStatus(`${provider} 연결 테스트 중...`, '');

    try {
        const response = await fetch('/api/test-connection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider, key })
        });
        const result = await response.json();
        if (response.ok) {
            showStatus(`${provider} 연결 성공! ✨`, 'success');
        } else {
            showStatus(`${provider} 연결 실패: ${result.error}`, 'error');
        }
    } catch (err) {
        showStatus('연결 테스트 중 오류 발생', 'error');
    }
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('testStatus');
    statusDiv.textContent = message;
    statusDiv.className = 'test-status'; // Reset classes
    if (type) statusDiv.classList.add(`status-${type}`);
    statusDiv.classList.remove('hidden');
}

// --- Analysis Logic ---
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
