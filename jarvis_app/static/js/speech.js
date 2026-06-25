// Speech Recognition Setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

// Configuration
recognition.continuous = false;
recognition.interimResults = true;
recognition.language = 'en-IN'; // Can switch between en-US, hi-IN, etc.

let isListening = false;
let finalTranscript = '';

// Detect wake word
const WAKE_WORDS = ['hey jarvis', 'jarvis', 'hey', 'jaarvis'];

// Speech event handlers
recognition.onstart = () => {
    console.log('Speech recognition started');
    isListening = true;
    document.getElementById('voiceStatus').innerHTML = '<div class="voice-indicator"></div><span>Listening...</span>';
    updateVoiceButtonState(true);
};

recognition.onresult = (event) => {
    let interimTranscript = '';
    
    for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i].transcript;
        
        if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
        } else {
            interimTranscript += transcript;
        }
    }
    
    // Display interim results
    const displayText = finalTranscript || interimTranscript;
    if (displayText) {
        console.log('Transcript:', displayText);
        document.getElementById('voiceStatus').innerHTML = `<span style="font-size: 0.9em; color: #666;">"${displayText.slice(0, 50)}${displayText.length > 50 ? '...' : ''}"</span>`;
    }
};

recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    const errorMessages = {
        'no-speech': 'कोई आवाज़ नहीं सुनी गई | No speech detected',
        'network': 'नेटवर्क त्रुटि | Network error',
        'audio-capture': 'माइक्रोफ़ोन एक्सेस समस्या | Microphone access denied',
    };
    
    const message = errorMessages[event.error] || `Error: ${event.error}`;
    document.getElementById('voiceStatus').innerHTML = `<span style="color: #ef4444;">${message}</span>`;
    updateVoiceButtonState(false);
};

recognition.onend = () => {
    console.log('Speech recognition ended');
    isListening = false;
    updateVoiceButtonState(false);
    
    if (finalTranscript) {
        processVoiceCommand(finalTranscript);
        finalTranscript = '';
    }
};

// Start/Stop voice recording
function toggleVoiceRecording() {
    const button = document.getElementById('voiceButton');
    
    if (isListening) {
        recognition.stop();
        button.classList.remove('listening');
        updateVoiceButtonState(false);
    } else {
        finalTranscript = '';
        recognition.start();
        button.classList.add('listening');
    }
}

// Update voice button state
function updateVoiceButtonState(listening) {
    const button = document.getElementById('voiceButton');
    
    if (listening) {
        button.classList.add('listening');
        button.style.backgroundColor = '#2563eb';
        button.querySelector('.btn-text').style.color = 'white';
    } else {
        button.classList.remove('listening');
        button.style.backgroundColor = 'white';
        button.querySelector('.btn-text').style.color = '#2563eb';
    }
}

// Process voice command
async function processVoiceCommand(transcript) {
    const normalized = transcript.toLowerCase().trim();
    console.log('Processing transcript:', normalized);
    
    // Check for wake word
    let hasWakeWord = false;
    let commandText = normalized;
    
    for (let wakeWord of WAKE_WORDS) {
        if (normalized.includes(wakeWord)) {
            hasWakeWord = true;
            commandText = normalized.replace(wakeWord, '').trim();
            break;
        }
    }
    
    if (!hasWakeWord) {
        // Treat entire transcript as command if no wake word
        commandText = normalized;
    }
    
    if (commandText.length < 3) {
        showMessage('कृपया एक वैलिड कमांड बोलें | Please say a valid command', 'system');
        return;
    }
    
    // Show user transcript
    if (document.getElementById('showTranscript').checked) {
        showMessage(`🎤 "${commandText}"`, 'user');
    }
    
    // Send command to backend
    await sendCommandToBackend(commandText);
}

// Send command to backend
async function sendCommandToBackend(command) {
    const voiceButton = document.getElementById('voiceButton');
    voiceButton.classList.add('processing');
    voiceButton.disabled = true;
    
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
            
            // Show actions taken
            if (data.actions && data.actions.length > 0) {
                showActionsBadges(data.actions);
            }
            
            // Auto-play response if enabled
            if (document.getElementById('autoPlayResponse').checked) {
                speakResponse(data.response);
            }
        } else {
            showMessage('त्रुटि: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('कनेक्शन त्रुटि | Connection error: ' + error.message, 'error');
    } finally {
        voiceButton.classList.remove('processing');
        voiceButton.disabled = false;
    }
}

// Text-to-speech for response
function speakResponse(text) {
    // Remove markdown-like formatting for speech
    const cleanText = text.replace(/[*#`]/g, '');
    
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.language = 'en-IN';
        utterance.rate = 0.95;
        utterance.pitch = 1;
        
        speechSynthesis.speak(utterance);
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

// Show action badges
function showActionsBadges(actions) {
    actions.forEach(action => {
        const badge = document.createElement('div');
        badge.className = 'message action';
        badge.innerHTML = `<span class="action-badge">⚡ ${action.tool.toUpperCase()}</span>`;
        document.getElementById('chatHistory').appendChild(badge);
    });
    scrollChatToBottom();
}

// Show message in chat
function showMessage(message, type) {
    const chatHistory = document.getElementById('chatHistory');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const messageContent = document.createElement('p');
    messageContent.textContent = message;
    messageDiv.appendChild(messageContent);
    
    chatHistory.appendChild(messageDiv);
    scrollChatToBottom();
}

// Scroll chat to bottom
function scrollChatToBottom() {
    const chatHistory = document.getElementById('chatHistory');
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Export for app.js
window.toggleVoiceRecording = toggleVoiceRecording;
window.showMessage = showMessage;
window.scrollChatToBottom = scrollChatToBottom;
