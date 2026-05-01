document.addEventListener('DOMContentLoaded', () => {
    // Theme toggling
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    
    // Check local storage or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        htmlElement.setAttribute('data-theme', 'dark');
    }

    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });

    // Chat Logic
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('user-input');
    const chatHistoryContainer = document.getElementById('chat-history');
    
    // Store chat history for context
    let chatHistory = [];

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        // 1. Add User message to UI
        appendMessage('user', message);
        chatInput.value = '';
        
        // 2. Show typing indicator
        const typingEl = showTypingIndicator();
        
        try {
            // 3. Send to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    history: chatHistory
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            typingEl.remove();
            
            if (response.ok && data.status === 'success') {
                // Formatting links and bold text
                let formattedText = formatMarkdown(data.response);
                appendMessage('system', formattedText, true);
                
                // Update history context
                chatHistory.push({ role: 'user', content: message });
                chatHistory.push({ role: 'model', content: data.response });
                
                // Keep history trimmed to avoid huge requests
                if (chatHistory.length > 10) {
                    chatHistory = chatHistory.slice(chatHistory.length - 10);
                }
            } else {
                appendMessage('system', data.error || 'Oops! Something went wrong.');
            }
        } catch (error) {
            console.error('Chat error:', error);
            typingEl.remove();
            appendMessage('system', 'Unable to reach the server. Please check your connection.');
        }
    });

    function appendMessage(sender, content, isHtml = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'system' ? 'C' : 'U';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.setAttribute('tabindex', '0'); // Accessibility: make focusable
        
        if (isHtml) {
            contentDiv.innerHTML = content;
        } else {
            const p = document.createElement('p');
            p.textContent = content;
            contentDiv.appendChild(p);
        }
        
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        
        chatHistoryContainer.appendChild(msgDiv);
        scrollToBottom();
        
        // Focus for screen readers on new system message
        if (sender === 'system') {
            contentDiv.focus();
        }
    }

    function showTypingIndicator() {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message system-message typing-msg';
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = 'C';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'typing-indicator';
        contentDiv.style.display = 'flex';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            contentDiv.appendChild(dot);
        }
        
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        
        chatHistoryContainer.appendChild(msgDiv);
        scrollToBottom();
        return msgDiv;
    }

    function scrollToBottom() {
        chatHistoryContainer.scrollTop = chatHistoryContainer.scrollHeight;
    }

    // Simple markdown to HTML formatter for bold text and lists
    function formatMarkdown(text) {
        let html = text;
        
        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Bullet points (basic substitution, ensuring each point is a paragraph or styled)
        html = html.replace(/^\* (.*?)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // Line breaks to <br> if not in a list
        html = html.replace(/\n(?!<)/g, '<br>');
        
        // Fix double nesting or weird br tags around lists
        html = html.replace(/<br>(<ul>)/g, '$1');
        html = html.replace(/(<\/ul>)<br>/g, '$1');
        
        return html;
    }
});
