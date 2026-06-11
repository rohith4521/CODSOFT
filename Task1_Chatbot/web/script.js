// ==========================================================================
// CHATBOT CLIENT INITIAL STATE
// ==========================================================================
let activePersonality = 'nova';
let chatState = {
    name: null,
    topic: null,
    messages_count: 0
};

// Descriptions & defaults for personalities to update welcome card and placeholder
const personalityMetadata = {
    nova: {
        displayName: 'Nova',
        status: 'Online • Ready to assist',
        placeholder: 'Message Nova...',
        welcome: 'Hello! I am Nova, your structured virtual assistant. You can chat with me, ask me to perform calculations, tell you a joke, give the time, or tell you the weather forecast!'
    },
    byte: {
        displayName: 'Byte',
        status: 'Online • Console active',
        placeholder: 'Execute command on Byte...',
        welcome: 'System initialized. I am Byte, your friendly geeky companion. Ask me technical commands, calculations, jokes, or check the database timestamp!'
    },
    spike: {
        displayName: 'Spike',
        status: 'Online • Yawning',
        placeholder: 'Say something to Spike...',
        welcome: 'Yeah, hi. I\'m Spike. I answer questions because I\'m programmed to, not because I want to. Ask for jokes, math, or time if you really must.'
    },
    zen: {
        displayName: 'Zen',
        status: 'Online • Meditating',
        placeholder: 'Share a thought with Zen...',
        welcome: 'Peace. I am Zen, a reflection of the present moment. Let us share a peaceful conversation, seek calm answers, or contemplate numbers and time.'
    }
};

// ==========================================================================
// DOM ELEMENTS
// ==========================================================================
const bodyEl = document.body;
const chatMessagesContainer = document.getElementById('chat-messages-container');
const chatInputForm = document.getElementById('chat-input-form');
const userMessageInput = document.getElementById('user-message-input');
const typingIndicator = document.getElementById('typing-indicator');
const typingTextSpan = document.getElementById('typing-text-span');
const botDisplayName = document.getElementById('bot-display-name');
const botDisplayStatus = document.getElementById('bot-display-status');
const headerAvatar = document.getElementById('header-avatar');
const personalityWelcomeDesc = document.getElementById('personality-welcome-desc');
const clearChatBtn = document.getElementById('clear-chat');
const exportChatBtn = document.getElementById('export-chat');
const quickRepliesContainer = document.getElementById('quick-replies-container');
const toastEl = document.getElementById('toast');

// ==========================================================================
// APPLICATION INITIALIZATION
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    scrollChatToBottom();
});

function setupEventListeners() {
    // Personality Switcher
    const cards = document.querySelectorAll('.personality-card');
    cards.forEach(card => {
        card.addEventListener('click', () => {
            const selected = card.getAttribute('data-personality');
            if (selected !== activePersonality) {
                switchPersonality(selected, cards);
            }
        });
    });

    // Form Submission
    chatInputForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = userMessageInput.value.trim();
        if (!text) return;
        
        sendMessage(text);
        userMessageInput.value = '';
    });

    // Suggestion Chips (inside welcome box)
    document.addEventListener('click', (e) => {
        if (e.target && e.target.classList.contains('suggestion-chip')) {
            const text = e.target.innerText;
            sendMessage(text);
        }
    });

    // Quick Replies
    const quickChips = document.querySelectorAll('.quick-reply-chip');
    quickChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const text = chip.getAttribute('data-text');
            sendMessage(text);
        });
    });

    // Clear Conversation
    clearChatBtn.addEventListener('click', clearConversation);

    // Export Conversation
    exportChatBtn.addEventListener('click', exportConversation);
}

// ==========================================================================
// BUSINESS LOGIC & API CONNECTIVITY
// ==========================================================================

function switchPersonality(personality, cardsList) {
    activePersonality = personality;
    const meta = personalityMetadata[personality];

    // 1. Update UI cards active state
    cardsList.forEach(card => {
        if (card.getAttribute('data-personality') === personality) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });

    // 2. Update Body Theme Class
    bodyEl.className = `personality-${personality}`;

    // 3. Update Chat Header
    botDisplayName.innerText = meta.displayName;
    botDisplayStatus.innerText = meta.status;
    headerAvatar.innerText = meta.displayName.charAt(0);
    headerAvatar.className = `bot-header-avatar ${personality}-avatar`;

    // 4. Update Input Placeholder
    userMessageInput.placeholder = meta.placeholder;

    // 5. Update Welcome Card description if it exists
    if (personalityWelcomeDesc) {
        personalityWelcomeDesc.innerText = meta.welcome;
    }

    // 6. Reset name but preserve message counter
    // Let's print a system notice bubble in the chat log
    appendSystemNotice(`Switched chat partner to ${meta.displayName}`);
    
    showToast(`Connected with ${meta.displayName}`);
}

function sendMessage(text) {
    // 1. Remove welcome box if it's there
    const welcomeBox = document.querySelector('.welcome-box');
    if (welcomeBox) {
        welcomeBox.remove();
    }

    // 2. Append User bubble
    appendMessageBubble(text, 'user');
    scrollChatToBottom();

    // 3. Trigger typing status
    showTypingIndicator();

    // 4. API Request
    const requestData = {
        message: text,
        personality: activePersonality,
        state: chatState
    };

    // Minor organic delay so response doesn't feel instantaneous (feels like bot typing)
    const start = Date.now();
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Server returned error status');
        }
        return response.json();
    })
    .then(data => {
        const elapsed = Date.now() - start;
        const delay = Math.max(500 - elapsed, 200); // minimum 500ms delay for natural pacing

        setTimeout(() => {
            hideTypingIndicator();
            appendMessageBubble(data.response, 'bot');
            chatState = data.state; // Save updated state
            scrollChatToBottom();
        }, delay);
    })
    .catch(error => {
        console.error('API Error:', error);
        setTimeout(() => {
            hideTypingIndicator();
            appendMessageBubble('Connection offline. Running local client fallback: I could not reach the server logic.', 'bot');
            scrollChatToBottom();
        }, 600);
    });
}

function clearConversation() {
    chatMessagesContainer.innerHTML = '';
    chatState = { name: null, topic: null, messages_count: 0 };
    
    // Recreate welcome box
    const meta = personalityMetadata[activePersonality];
    const welcomeHTML = `
        <div class="welcome-box">
            <div class="welcome-icon">
                <i data-lucide="sparkles"></i>
            </div>
            <h2>Welcome to CodSoft Rule-Based Chatbot!</h2>
            <p id="personality-welcome-desc">${meta.welcome}</p>
            
            <div class="tips-box">
                <h4>Try asking:</h4>
                <ul>
                    <li><code class="suggestion-chip">My name is Alex</code></li>
                    <li><code class="suggestion-chip">Calculate 144 / 12</code></li>
                    <li><code class="suggestion-chip">Tell me a joke</code></li>
                    <li><code class="suggestion-chip">What time is it?</code></li>
                </ul>
            </div>
        </div>
    `;
    chatMessagesContainer.innerHTML = welcomeHTML;
    lucide.createIcons();
    
    showToast('Conversation cleared');
}

function exportConversation() {
    const rows = document.querySelectorAll('.message-row');
    if (rows.length === 0) {
        showToast('No messages to export');
        return;
    }

    let textLog = `==================================================\n`;
    textLog += `CODSOFT RULE-BASED CHATBOT EXPORT LOG\n`;
    textLog += `Date: ${new Date().toLocaleString()}\n`;
    textLog += `==================================================\n\n`;

    rows.forEach(row => {
        const isUser = row.classList.contains('user-row');
        const sender = isUser ? 'User' : personalityMetadata[activePersonality].displayName;
        const bubble = row.querySelector('.message-bubble');
        const text = bubble.innerText;
        const time = row.nextElementSibling && row.nextElementSibling.classList.contains('message-time') 
                     ? row.nextElementSibling.innerText 
                     : '';
        
        textLog += `[${time}] ${sender}: ${text}\n\n`;
    });

    const blob = new Blob([textLog], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chatbot_history_${activePersonality}_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Chat history exported successfully!');
}

// ==========================================================================
// RENDER UTILITIES
// ==========================================================================

function appendMessageBubble(text, sender) {
    const messageRow = document.createElement('div');
    messageRow.className = `message-row ${sender}-row`;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    if (sender === 'bot') {
        bubble.innerHTML = parseMarkdown(text);
    } else {
        // User messages are escaped to prevent HTML injection
        bubble.innerText = text;
    }

    messageRow.appendChild(bubble);
    chatMessagesContainer.appendChild(messageRow);

    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    const now = new Date();
    timeSpan.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    chatMessagesContainer.appendChild(timeSpan);
}

function appendSystemNotice(text) {
    const notice = document.createElement('div');
    notice.style.textAlign = 'center';
    notice.style.fontSize = '0.75rem';
    notice.style.color = 'var(--text-secondary)';
    notice.style.margin = '14px 0';
    notice.style.opacity = '0.7';
    notice.innerText = `— ${text} —`;
    chatMessagesContainer.appendChild(notice);
    scrollChatToBottom();
}

function showTypingIndicator() {
    typingTextSpan.innerText = `${personalityMetadata[activePersonality].displayName} is thinking`;
    typingIndicator.style.display = 'flex';
    scrollChatToBottom();
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

function scrollChatToBottom() {
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

function showToast(message) {
    toastEl.innerText = message;
    toastEl.classList.add('show');
    setTimeout(() => {
        toastEl.classList.remove('show');
    }, 2500);
}

/**
 * Super lightweight markdown parser for formatting bold text, code, pre, lists.
 */
function parseMarkdown(text) {
    // 1. Escape HTML first
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // 2. Parse pre code blocks: ```python ... ```
    html = html.replace(/```([a-zA-Z0-9]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code class="language-${lang}">${code.trim()}</code></pre>`;
    });

    // 3. Parse inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // 4. Parse bold: **bold** or *bold*
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // 5. Parse simple bullet points: \n- item
    html = html.replace(/\n\s*-\s+([^\n]+)/g, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>'); // wrap adjacent in ul
    // Clean double ul tags if any
    html = html.replace(/<\/ul>\s*<ul>/g, '');

    // 6. Convert double newlines to paragraph breaks, single newlines to br
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    
    // Wrap in initial paragraph
    return `<p>${html}</p>`;
}
