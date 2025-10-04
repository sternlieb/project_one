// DOM Elements
const usernameInput = document.getElementById('usernameInput');
const questionInput = document.getElementById('questionInput');
const chatMessages = document.getElementById('chatMessages');
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

    // Allow Enter key to send question
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

    usernameInput.addEventListener('input', function() {
        clearStatus();
    });
});

// Add message to chat
function addMessage(message, isUser = false, username = '') {
    const messageDiv = document.createElement('div');
    messageDiv.className = isUser ? 'user-message' : 'bot-message';

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = isUser ? (username.charAt(0).toUpperCase() || '👤') : '🤖';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = `message-bubble ${isUser ? 'user-bubble' : 'bot-bubble'}`;
    bubbleDiv.textContent = message;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(bubbleDiv);

    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send question to server
async function sendQuestion() {
    const username = usernameInput.value.trim();
    const question = questionInput.value.trim();

    // Validate inputs
    if (!username) {
        showStatus('Please enter a username before sending.', 'error');
        usernameInput.focus();
        return;
    }

    if (!question) {
        showStatus('Please enter a question before sending.', 'error');
        questionInput.focus();
        return;
    }

    // Add user message to chat
    addMessage(question, true, username);

    // Clear input and disable form
    questionInput.value = '';
    setLoadingState(true);
    showStatus('Getting response<span class="loading-dots"></span>', 'loading');

    try {
        // Send request to server
        const response = await fetch(`${SERVER_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                question: question
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        // Add bot response to chat
        addMessage(data.answer, false);
        clearStatus();

    } catch (error) {
        console.error('Error sending question:', error);

        // Add error message to chat
        let errorMessage;
        if (error.name === 'TypeError') {
            errorMessage = 'Unable to connect to server. Please make sure the server is running on port 5000.';
        } else {
            errorMessage = `Error: ${error.message}`;
        }

        addMessage(errorMessage, false);
        showStatus('Connection error occurred.', 'error');
    } finally {
        setLoadingState(false);
        questionInput.focus();
    }
}

// Reset form (Clear chat)
function resetForm() {
    // Clear chat messages except welcome message
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    chatMessages.innerHTML = '';
    if (welcomeMessage) {
        chatMessages.appendChild(welcomeMessage);
    }

    questionInput.value = '';
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
        sendBtn.innerHTML = '<span>Sending...</span>';
    } else {
        sendBtn.innerHTML = '<span>Send</span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>';
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
