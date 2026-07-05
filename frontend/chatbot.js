document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('chat-input').focus();
});

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function sendSuggestion(text) {
    document.getElementById('chat-input').value = text;
    sendMessage();
}

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    // Show user message
    addMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    showTyping();

    // Send to real backend API
    fetch(API_URL + '/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        removeTyping();
        if (data.success) {
            addMessage(data.response, 'bot');
        } else {
            addMessage('Sorry, I could not process that. Please try again.', 'bot');
        }
    })
    .catch(function(error) {
        removeTyping();
        addMessage('Connection error. Please make sure the server is running.', 'bot');
    });
}

function addMessage(text, sender) {
    const container = document.getElementById('chat-messages');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ' + sender + '-message';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'bot' ? '🤖' : '👤';

    const content = document.createElement('div');
    content.className = 'message-content';

    // Format text (handle newlines and bold)
    const formatted = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    content.innerHTML = formatted;

    if (sender === 'bot') {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
    } else {
        messageDiv.appendChild(content);
        messageDiv.appendChild(avatar);
    }

    container.appendChild(messageDiv);

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function showTyping() {
    const container = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typing-indicator';

    typingDiv.innerHTML =
        '<div class="message-avatar">🤖</div>' +
        '<div class="message-content typing">' +
        '<span></span><span></span><span></span>' +
        '</div>';

    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
}

function removeTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}