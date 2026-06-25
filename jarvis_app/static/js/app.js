// Main Application Logic

document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI
    initializeUI();
    
    // Check system status
    checkSystemStatus();
});

// Initialize UI components
function initializeUI() {
    const voiceButton = document.getElementById('voiceButton');
    const sendButton = document.getElementById('sendButton');
    const textInput = document.getElementById('textInput');
    const clearButton = document.getElementById('clearButton');
    const settingsButton = document.getElementById('settingsButton');
    const modal = document.getElementById('settingsModal');
    const closeModal = document.getElementById('closeModal');  
    
    // Voice button
    voiceButton.addEventListener('click', toggleVoiceRecording);
    
    // Text input - send on Enter
    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && textInput.value.trim()) {
            sendTextCommand();
        }
    });
    
    // Send button
    sendButton.addEventListener('click', sendTextCommand);
    
    // Clear chat
    clearButton.addEventListener('click', clearChat);
    
    // Settings
    settingsButton.addEventListener('click', () => {
        modal.classList.add('show');
    });
    
    closeModal.addEventListener('click', () => {
        modal.classList.remove('show');
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    });
    
    // Request microphone permission
    requestMicrophonePermission();
}

// Request microphone permission
async function requestMicrophonePermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop());
        console.log('Microphone permission granted');
    } catch (error) {
        console.warn('Microphone permission denied:', error);
        showMessage('माइक्रोफ़ोन एक्सेस दें | Please enable microphone access for voice commands', 'system');
    }
}

// Send text command
async function sendTextCommand(commandArg) {
    const textInput = document.getElementById('textInput');
    const command = commandArg || textInput.value.trim();
    
    if (!command) return;
    
    // Show user message
    showMessage(`📝 ${command}`, 'user');
    textInput.value = '';
    
    // Send to backend
    const sendButton = document.getElementById('sendButton');
    sendButton.disabled = true;
    
    try {
        const response = await fetch('/api/command/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ command: command })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showMessage(data.response, 'assistant');
            
            // Show actions
            if (data.actions && data.actions.length > 0) {
                showActionsBadges(data.actions);
            }
            
            // Auto-play if enabled
            if (document.getElementById('autoPlayResponse').checked) {
                speakResponse(data.response);
            }
        } else {
            showMessage('त्रुटि: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('कनेक्शन त्रुटि | Error: ' + error.message, 'error');
    } finally {
        sendButton.disabled = false;
    }
}

// Clear chat
async function clearChat() {
    if (confirm('क्या आप निश्चित हैं? | Are you sure?')) {
        try {
            const response = await fetch('/api/clear/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                const chatHistory = document.getElementById('chatHistory');
                chatHistory.innerHTML = `
                    <div class="message system">
                        <p>नमस्ते! | Hello! Chat cleared. Ready to help.</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
}

// Check system status
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/status/');
        const data = await response.json();
        console.log('System Status:', data);
    } catch (error) {
        console.error('Status check error:', error);
    }
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Request test
console.log('🤖 JARVIS AI Assistant loaded');
console.log('Wake word: "Hey Jarvis"');
console.log('Commands available: Gmail, Calendar management');
