// DOM Elements
const questionInput = document.getElementById('questionInput');
const answerOutput = document.getElementById('answerOutput');
const sendBtn = document.getElementById('sendBtn');
const resetBtn = document.getElementById('resetBtn');
const status = document.getElementById('status');

// Server Configuration
const SERVER_URL = 'http://localhost:5000';

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('Question & Answer App loaded successfully');

    // Add event listeners
    sendBtn.addEventListener('click', sendQuestion);
    resetBtn.addEventListener('click', resetForm);

    // Allow Enter key to send question (Ctrl+Enter for new line)
    questionInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuestion();
        }
    });

    // Clear status when user starts typing
    questionInput.addEventListener('input', function() {
        clearStatus();
    });
});

// Send question to server
async function sendQuestion() {
    const question = questionInput.value.trim();

    // Validate input
    if (!question) {
        showStatus('Please enter a question before sending.', 'error');
        questionInput.focus();
        return;
    }

    // Disable button and show loading
    setLoadingState(true);
    showStatus('Sending question to server<span class="loading-dots"></span>', 'loading');

    try {
        // Send request to server
        const response = await fetch(`${SERVER_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        // Display the answer
        answerOutput.value = data.answer;
        showStatus('Answer received successfully!', 'success');

        // Clear success message after 3 seconds
        setTimeout(() => {
            clearStatus();
        }, 3000);

    } catch (error) {
        console.error('Error sending question:', error);

        // Handle different error types
        if (error.name === 'TypeError') {
            showStatus('Unable to connect to server. Please make sure the server is running on port 5000.', 'error');
        } else {
            showStatus(`Error: ${error.message}`, 'error');
        }

        answerOutput.value = '';
    } finally {
        setLoadingState(false);
    }
}

// Reset form
function resetForm() {
    questionInput.value = '';
    answerOutput.value = '';
    clearStatus();
    questionInput.focus();
}

// Show status message
function showStatus(message, type) {
    status.innerHTML = message;
    status.className = `status ${type}`;
}

// Clear status message
function clearStatus() {
    status.innerHTML = '';
    status.className = 'status';
}

// Set loading state
function setLoadingState(loading) {
    sendBtn.disabled = loading;
    resetBtn.disabled = loading;
    questionInput.disabled = loading;

    if (loading) {
        sendBtn.innerHTML = 'Sending...';
    } else {
        sendBtn.innerHTML = 'Send Question';
    }
}

// Test server connection on page load
async function testServerConnection() {
    try {
        const response = await fetch(`${SERVER_URL}/health`, {
            method: 'GET',
        });

        if (response.ok) {
            console.log('Server connection successful');
        } else {
            console.warn('Server responded with error:', response.status);
        }
    } catch (error) {
        console.warn('Server connection test failed:', error.message);
        showStatus('Server is not running. Please start the server to use this app.', 'error');
    }
}

// Test connection when page loads
setTimeout(testServerConnection, 1000);
