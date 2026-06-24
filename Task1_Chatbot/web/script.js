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
const toastEl = document.getElementById('toast');

// Speech API elements
const btnVoiceInput = document.getElementById('btn-voice-input');
const micIcon = document.getElementById('mic-icon');
const btnVoiceOutput = document.getElementById('btn-voice-output');
const voiceOutputIcon = document.getElementById('voice-output-icon');

let recognition = null;
let isListening = false;
let voiceOutputEnabled = true;

// ==========================================================================
// APPLICATION INITIALIZATION
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupSpeechRecognition();
    setupSpeechSynthesis();
    updateStateGauges();
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
// SPEECH API INTEGRATION
// ==========================================================================
function setupSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            btnVoiceInput.classList.add('listening');
            micIcon.setAttribute('data-lucide', 'mic-off');
            lucide.createIcons();
            userMessageInput.placeholder = "Listening...";
        };

        recognition.onend = () => {
            isListening = false;
            btnVoiceInput.classList.remove('listening');
            micIcon.setAttribute('data-lucide', 'mic');
            lucide.createIcons();
            const meta = personalityMetadata[activePersonality];
            userMessageInput.placeholder = meta.placeholder;
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userMessageInput.value = transcript;
            sendMessage(transcript);
            userMessageInput.value = '';
        };

        recognition.onerror = (e) => {
            console.error("Speech Recognition Error:", e);
        };

        btnVoiceInput.addEventListener('click', () => {
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        btnVoiceInput.style.display = 'none';
    }
}

function setupSpeechSynthesis() {
    if ('speechSynthesis' in window) {
        btnVoiceOutput.addEventListener('click', () => {
            voiceOutputEnabled = !voiceOutputEnabled;
            if (voiceOutputEnabled) {
                btnVoiceOutput.classList.add('active');
                voiceOutputIcon.setAttribute('data-lucide', 'volume-2');
            } else {
                btnVoiceOutput.classList.remove('active');
                voiceOutputIcon.setAttribute('data-lucide', 'volume-x');
                window.speechSynthesis.cancel();
            }
            lucide.createIcons();
            showToast(voiceOutputEnabled ? 'Speech Synthesis Enabled' : 'Speech Synthesis Muted');
        });
    } else {
        btnVoiceOutput.style.display = 'none';
    }
}

function speakResponse(text, personality) {
    if (!voiceOutputEnabled || !('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel(); // cancel any active speech

    // strip tags for voice
    const voiceText = text.replace(/<[^>]*>/g, '').replace(/\*\*([^*]+)\*\*/g, '$1').replace(/\*([^*]+)\*/g, '$1');
    const utterance = new SpeechSynthesisUtterance(voiceText);
    const voices = window.speechSynthesis.getVoices();

    if (personality === 'zen') {
        utterance.rate = 0.75;
        utterance.pitch = 0.85;
        const zenVoice = voices.find(v => v.name.includes('Google US English') || v.lang.startsWith('en'));
        if (zenVoice) utterance.voice = zenVoice;
    } else if (personality === 'byte') {
        utterance.rate = 1.15;
        utterance.pitch = 1.3;
        const byteVoice = voices.find(v => v.name.includes('Robotic') || v.name.includes('David') || v.lang.startsWith('en'));
        if (byteVoice) utterance.voice = byteVoice;
    } else if (personality === 'spike') {
        utterance.rate = 1.1;
        utterance.pitch = 0.9;
        const spikeVoice = voices.find(v => v.name.includes('Google UK English') || v.lang.startsWith('en'));
        if (spikeVoice) utterance.voice = spikeVoice;
    } else {
        utterance.rate = 1.0;
        utterance.pitch = 1.05;
        const stdVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Zira') || v.lang.startsWith('en'));
        if (stdVoice) utterance.voice = stdVoice;
    }

    window.speechSynthesis.speak(utterance);
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

    // 6. Append notice
    appendSystemNotice(`Switched chat partner to ${meta.displayName}`);
    updateStateGauges();
    showToast(`Connected with ${meta.displayName}`);
}

function sendMessage(text) {
    const welcomeBox = document.querySelector('.welcome-box');
    if (welcomeBox) {
        welcomeBox.remove();
    }

    // Append User bubble
    appendMessageBubble(text, 'user');
    scrollChatToBottom();

    // Trigger typing status
    showTypingIndicator();

    chatState.last_input = text;

    const requestData = {
        message: text,
        personality: activePersonality,
        state: chatState
    };

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
        const delay = Math.max(500 - elapsed, 200);

        setTimeout(() => {
            hideTypingIndicator();
            
            chatState = data.state; // Save updated state
            const metadata = data.state.last_match_metadata || {};
            
            appendMessageBubble(data.response, 'bot', metadata);
            speakResponse(data.response, activePersonality);
            updateStateGauges();
            renderRegexTrace(metadata);
            
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
            <h2>VisionChat Intent Parser Dashboard</h2>
            <p id="personality-welcome-desc">${meta.welcome}</p>
            
            <div class="tips-box">
                <h4>Explore matched rules:</h4>
                <ul>
                    <li><code class="suggestion-chip">My name is Alex</code></li>
                    <li><code class="suggestion-chip">Calculate 15 * 6</code></li>
                    <li><code class="suggestion-chip">Tell me a joke</code></li>
                    <li><code class="suggestion-chip">What is the weather in Paris?</code></li>
                </ul>
            </div>
        </div>
    `;
    chatMessagesContainer.innerHTML = welcomeHTML;
    lucide.createIcons();
    updateStateGauges();
    
    // Clear debug panels
    document.getElementById('debug-raw-input').innerText = '—';
    document.getElementById('debug-entities-container').innerHTML = '<div class="empty-debug-text">No variables bound in current scope.</div>';
    document.getElementById('regex-steps-container').innerHTML = `
        <div class="regex-step-card">
            <span class="step-badge text-secondary">Step 1</span>
            <div class="step-meta">
                <h5>Evaluate Rule Matchers</h5>
                <p>Pattern checking sequence initialized.</p>
            </div>
        </div>
    `;
    const statusPill = document.getElementById('debug-status-pill');
    statusPill.innerText = 'Idle';
    statusPill.className = 'debug-status-pill idle';

    showToast('Conversation cleared');
}

function exportConversation() {
    const rows = document.querySelectorAll('.message-row');
    if (rows.length === 0) {
        showToast('No messages to export');
        return;
    }

    let textLog = `==================================================\n`;
    textLog += `VISIONCHAT INTENT PARSER LOG EXPORT\n`;
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
    a.download = `chat_history_${activePersonality}_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Chat history exported successfully!');
}

// ==========================================================================
// RENDER & TEMPLATIZATION UTILITIES
// ==========================================================================

function appendMessageBubble(text, sender, metadata = {}) {
    const messageRow = document.createElement('div');
    messageRow.className = `message-row ${sender}-row`;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    if (sender === 'bot') {
        if (metadata.matched_rule === 'weather' && metadata.template_data) {
            bubble.innerHTML = renderWeatherWidget(metadata.template_data);
        } else if (metadata.matched_rule === 'math' && metadata.template_data) {
            bubble.innerHTML = renderMathWidget(metadata.template_data);
        } else if (metadata.matched_rule === 'joke' && metadata.template_data) {
            bubble.innerHTML = renderJokeWidget(metadata.template_data);
        } else {
            bubble.innerHTML = parseMarkdown(text);
        }
    } else {
        bubble.innerText = text;
    }

    messageRow.appendChild(bubble);
    chatMessagesContainer.appendChild(messageRow);

    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    const now = new Date();
    timeSpan.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    chatMessagesContainer.appendChild(timeSpan);
    lucide.createIcons();
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

// ==========================================================================
// WIDGET RENDERERS
// ==========================================================================
function renderWeatherWidget(data) {
    let icon = 'sun';
    if (data.condition === 'rainy') icon = 'cloud-rain';
    else if (data.condition === 'cloudy') icon = 'cloud';
    else if (data.condition === 'windy') icon = 'wind';

    return `
        <div class="weather-widget">
            <div class="weather-header">
                <span class="weather-loc">${data.location}</span>
                <i data-lucide="${icon}" class="weather-icon-svg ${data.condition}"></i>
            </div>
            <div class="weather-body">
                <span class="temp-deg">${data.condition === 'sunny' ? '27°C' : data.condition === 'rainy' ? '18°C' : data.condition === 'cloudy' ? '21°C' : '16°C'}</span>
                <span class="temp-cond">${data.condition.toUpperCase()}</span>
            </div>
            <p class="weather-desc">${data.details}</p>
        </div>
    `;
}

function renderMathWidget(data) {
    if (data.is_error) {
        return `
            <div class="math-widget error">
                <div class="math-screen">
                    <div class="math-formula">${data.operand1} ${data.operator} ${data.operand2}</div>
                    <div class="math-result">ERR: ${data.error_msg}</div>
                </div>
                <div class="math-footer-tag">ALGEBRA MODULE</div>
            </div>
        `;
    } else {
        return `
            <div class="math-widget">
                <div class="math-screen">
                    <div class="math-formula">${data.operand1} ${data.operator} ${data.operand2}</div>
                    <div class="math-result">= ${data.result}</div>
                </div>
                <div class="math-footer-tag">MATH CALCULATOR</div>
            </div>
        `;
    }
}

function renderJokeWidget(data) {
    const id = 'joke-' + Math.round(Math.random() * 100000);
    return `
        <div class="joke-widget" id="${id}">
            <div class="joke-setup">🎭 ${data.setup}</div>
            <button class="btn-reveal-joke" onclick="document.getElementById('${id}').classList.add('revealed')">
                Reveal Punchline 🤫
            </button>
            <div class="joke-punchline">👉 ${data.punchline}</div>
        </div>
    `;
}

// ==========================================================================
// REGEX DEBUGGER & COGNITIVE STATE UPDATERS
// ==========================================================================
function renderRegexTrace(metadata) {
    const statusPill = document.getElementById('debug-status-pill');
    const rawInputEl = document.getElementById('debug-raw-input');
    const entitiesContainer = document.getElementById('debug-entities-container');
    const stepsContainer = document.getElementById('regex-steps-container');

    if (!metadata || !metadata.regex_checks) return;

    // Set status pill class
    if (metadata.matched_rule === 'unknown') {
        statusPill.innerText = 'Fallback';
        statusPill.className = 'debug-status-pill fallback';
    } else {
        statusPill.innerText = 'Parsed';
        statusPill.className = 'debug-status-pill parsed';
    }

    // Set input text
    rawInputEl.innerText = `"${chatState.last_input || '—'}"`;

    // Render entities
    entitiesContainer.innerHTML = '';
    const keys = Object.keys(metadata.parsed_entities || {});
    if (keys.length === 0) {
        entitiesContainer.innerHTML = '<div class="empty-debug-text">No variables bound in current scope.</div>';
    } else {
        let html = '<table class="debug-entities-table"><thead><tr><th>Entity</th><th>Bound Value</th></tr></thead><tbody>';
        keys.forEach(k => {
            html += `<tr><td><code>${k}</code></td><td><strong>${metadata.parsed_entities[k]}</strong></td></tr>`;
        });
        html += '</tbody></table>';
        entitiesContainer.innerHTML = html;
    }

    // Render evaluated regex rules
    stepsContainer.innerHTML = '';
    metadata.regex_checks.forEach((check, index) => {
        const matchedClass = check.matched ? 'matched' : 'skipped';
        const icon = check.matched ? 'check-circle' : 'circle';
        const stepCard = document.createElement('div');
        stepCard.className = `regex-step-card ${matchedClass}`;
        stepCard.innerHTML = `
            <span class="step-badge">${index + 1}</span>
            <div class="step-meta">
                <h5>${check.rule}</h5>
                <code class="step-pattern">${check.pattern}</code>
            </div>
            <div class="step-status">
                <i data-lucide="${icon}"></i>
            </div>
        `;
        stepsContainer.appendChild(stepCard);
    });
    lucide.createIcons();
}

function updateStateGauges() {
    const lbl1 = document.getElementById('gauge-label-1');
    const val1 = document.getElementById('gauge-val-1');
    const fill1 = document.getElementById('gauge-fill-1');

    const lbl2 = document.getElementById('gauge-label-2');
    const val2 = document.getElementById('gauge-val-2');
    const fill2 = document.getElementById('gauge-fill-2');

    const turns = chatState.messages_count || 0;

    if (activePersonality === 'nova') {
        lbl1.innerText = 'Assistant Efficiency';
        let eff = Math.min(85 + turns * 3, 100);
        val1.innerText = `${eff}%`;
        fill1.style.width = `${eff}%`;

        lbl2.innerText = 'Conversational Focus';
        let foc = chatState.topic !== 'unknown' ? 95 : 40;
        val2.innerText = `${foc}%`;
        fill2.style.width = `${foc}%`;
    } 
    else if (activePersonality === 'byte') {
        lbl1.innerText = 'Neural RAM Allocated';
        let ram = Math.min(256 + turns * 16, 1024);
        val1.innerText = `${ram} MB`;
        fill1.style.width = `${Math.round((ram / 1024) * 100)}%`;

        lbl2.innerText = 'Process CPU Load';
        let cpu = Math.round(12 + Math.random() * 25 + turns * 2);
        cpu = Math.min(cpu, 100);
        val2.innerText = `${cpu}%`;
        fill2.style.width = `${cpu}%`;
    }
    else if (activePersonality === 'spike') {
        lbl1.innerText = 'Patience Quotient';
        let pat = Math.max(80 - turns * 8, 10);
        val1.innerText = `${pat}%`;
        fill1.style.width = `${pat}%`;

        lbl2.innerText = 'Spike Snark Level';
        let snark = Math.min(30 + turns * 12, 100);
        val2.innerText = `${snark}%`;
        fill2.style.width = `${snark}%`;
    }
    else if (activePersonality === 'zen') {
        lbl1.innerText = 'Inner Peace Meter';
        let peace = Math.min(80 + turns * 4, 100);
        if (chatState.topic === 'math' && chatState.last_match_metadata && chatState.last_match_metadata.template_data.is_error) {
            peace = 30;
        }
        val1.innerText = `${peace}%`;
        fill1.style.width = `${peace}%`;

        lbl2.innerText = 'Meditation Depth';
        let depth = Math.min(50 + turns * 6, 100);
        val2.innerText = `${depth}%`;
        fill2.style.width = `${depth}%`;
    }
}

// ==========================================================================
// LIGHTWEIGHT MARKDOWN PARSER
// ==========================================================================
function parseMarkdown(text) {
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Pre code blocks: ```python ... ```
    html = html.replace(/```([a-zA-Z0-9]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code class="language-${lang}">${code.trim()}</code></pre>`;
    });

    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bold: **bold** or *bold*
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Bullet points: \n- item
    html = html.replace(/\n\s*-\s+([^\n]+)/g, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');
    html = html.replace(/<\/ul>\s*<ul>/g, '');

    // Paragraph breaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    
    return `<p>${html}</p>`;
}
