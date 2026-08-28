/* ==========================================================================
   Django RAG Application - Real-Time Streaming Chat Client Handler
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const messagesContainer = document.getElementById('chat-messages-container');
    const emptyState = document.getElementById('chat-empty-state');
    const conversationIdInput = document.getElementById('conversation-id-input');
    const documentFilterSelect = document.getElementById('document-filter-select');

    // Configure Marked.js
    if (window.marked) {
        marked.setOptions({
            breaks: true,
            gfm: true,
            highlight: function(code, lang) {
                if (window.hljs && lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (e) {}
                }
                return code;
            }
        });
    }

    // Render markdown on initial page load
    document.querySelectorAll('.ai-msg-bubble .markdown-body').forEach(el => {
        const raw = el.innerText || el.textContent;
        if (window.marked && raw) {
            el.innerHTML = marked.parse(raw);
        }
    });

    // Format all existing timestamps in user's browser local 12-hour timezone
    document.querySelectorAll('[data-utc]').forEach(el => {
        const utcStr = el.getAttribute('data-utc');
        if (utcStr) {
            const date = new Date(utcStr);
            if (!isNaN(date.getTime())) {
                el.textContent = date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', hour12: true });
            }
        }
    });

    // Initialize syntax highlighting
    if (window.hljs) {
        document.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
    }

    // Scroll to bottom
    const scrollToBottom = () => {
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    };
    scrollToBottom();

    // Auto-resize textarea
    if (chatInput) {
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
        });

        // Enter to submit (Shift+Enter for newline)
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (chatForm) {
                    chatForm.dispatchEvent(new Event('submit'));
                }
            }
        });
    }

    // CSRF Token Helper
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
    const csrftoken = getCookie('csrftoken');

    // 12-Hour Time Formatter (e.g. 2:42 PM)
    function format12HourTime() {
        const now = new Date();
        let hours = now.getHours();
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        return `${hours}:${minutes} ${ampm}`;
    }

    // Parse Markdown safely
    function renderMarkdown(text) {
        if (!text) return '';
        if (window.marked) {
            return marked.parse(text);
        }
        return text
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '<br/><br/>')
            .replace(/\n/g, '<br/>');
    }

    // Copy to clipboard helper
    function attachCopyHandlers() {
        document.querySelectorAll('.copy-msg-btn').forEach(btn => {
            btn.onclick = () => {
                const bubble = btn.closest('.ai-msg-container').querySelector('.markdown-body');
                const text = bubble ? bubble.innerText : '';
                if (text) {
                    navigator.clipboard.writeText(text).then(() => {
                        const originalHTML = btn.innerHTML;
                        btn.innerHTML = `<span>✓ Copied!</span>`;
                        btn.style.color = '#34d399';
                        setTimeout(() => {
                            btn.innerHTML = originalHTML;
                            btn.style.color = '';
                        }, 2000);
                    });
                }
            };
        });
    }
    attachCopyHandlers();

    // Append User Message Bubble
    function appendUserMessage(content) {
        if (emptyState) emptyState.style.display = 'none';

        const row = document.createElement('div');
        row.className = 'message-row user';

        const userContainer = document.createElement('div');
        userContainer.className = 'user-bubble-container';

        const bubble = document.createElement('div');
        bubble.className = 'user-msg-bubble';
        bubble.textContent = content;

        const meta = document.createElement('div');
        meta.className = 'user-msg-meta';
        meta.textContent = format12HourTime();

        userContainer.appendChild(bubble);
        userContainer.appendChild(meta);
        row.appendChild(userContainer);

        messagesContainer.appendChild(row);
        scrollToBottom();
        return row;
    }

    // Create Live Streaming Assistant Card
    function createStreamingAssistantMessage() {
        if (emptyState) emptyState.style.display = 'none';

        const row = document.createElement('div');
        row.className = 'message-row assistant';

        const aiContainer = document.createElement('div');
        aiContainer.className = 'ai-msg-container';

        const aiHeader = document.createElement('div');
        aiHeader.className = 'ai-msg-header';
        aiHeader.innerHTML = `
            <div class="ai-badge">
                <span class="ai-badge-dot"></span>
                <span class="ai-status-text">AI Assistant (Streaming...)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="msg-time">${format12HourTime()}</span>
                <button class="action-icon-btn copy-msg-btn" title="Copy answer">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    Copy
                </button>
            </div>
        `;
        aiContainer.appendChild(aiHeader);

        const aiBubble = document.createElement('div');
        aiBubble.className = 'ai-msg-bubble';

        const mdContent = document.createElement('div');
        mdContent.className = 'markdown-body';
        mdContent.innerHTML = `<span class="streaming-cursor" style="display:inline-block; width:6px; height:14px; background:#6366f1; vertical-align:middle; animation:blink 0.8s infinite;"></span>`;
        aiBubble.appendChild(mdContent);

        aiContainer.appendChild(aiBubble);
        row.appendChild(aiContainer);

        messagesContainer.appendChild(row);
        scrollToBottom();

        return {
            row,
            mdContent,
            statusText: aiHeader.querySelector('.ai-status-text'),
            timeSpan: aiHeader.querySelector('.msg-time'),
            copyBtn: aiHeader.querySelector('.copy-msg-btn')
        };
    }

    // Suggestion Buttons handler
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const promptText = btn.getAttribute('data-prompt') || btn.textContent.trim();
            if (chatInput) {
                chatInput.value = promptText;
                chatInput.style.height = 'auto';
                chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });

    // Form Submit Handler with Real-Time Streaming
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const question = chatInput.value.trim();
            if (!question) return;

            // Reset input size & value
            chatInput.value = '';
            chatInput.style.height = '22px';
            sendBtn.disabled = true;

            const conversationId = conversationIdInput ? conversationIdInput.value : null;
            const documentId = documentFilterSelect ? documentFilterSelect.value : null;

            // Append User Message immediately
            appendUserMessage(question);

            // Create streaming assistant message bubble
            const streamCard = createStreamingAssistantMessage();
            let accumulatedText = "";

            try {
                const response = await fetch('/chat/query/stream/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        question: question,
                        conversation_id: conversationId,
                        document_id: documentId
                    })
                });

                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let buffer = '';

                let renderPending = false;

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n\n');
                    buffer = lines.pop(); // Keep incomplete chunk in buffer

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const jsonStr = line.replace(/^data:\s*/, '').trim();
                            if (!jsonStr) continue;

                            try {
                                const payload = JSON.parse(jsonStr);

                                if (payload.token) {
                                    accumulatedText += payload.token;
                                    if (!renderPending) {
                                        renderPending = true;
                                        requestAnimationFrame(() => {
                                            streamCard.mdContent.innerHTML = renderMarkdown(accumulatedText) + '<span class="streaming-cursor" style="display:inline-block; width:5px; height:13px; background:#6366f1; vertical-align:middle; animation:blink 0.8s infinite; margin-left:3px;"></span>';
                                            scrollToBottom();
                                            renderPending = false;
                                        });
                                    }
                                }

                                if (payload.done) {
                                    if (payload.created_at) {
                                        streamCard.timeSpan.textContent = payload.created_at;
                                    }
                                    if (conversationIdInput && payload.conversation_id) {
                                        conversationIdInput.value = payload.conversation_id;
                                        window.history.replaceState({}, '', `/chat/${payload.conversation_id}/`);
                                    }
                                }
                            } catch (parseErr) {
                                console.warn("SSE chunk parse warning:", parseErr);
                            }
                        }
                    }
                }

                // Final render cleanup
                streamCard.statusText.textContent = "AI Assistant";
                streamCard.mdContent.innerHTML = renderMarkdown(accumulatedText || "I could not find any relevant information in your uploaded documents.");

                // Highlight code blocks
                if (window.hljs) {
                    streamCard.mdContent.querySelectorAll('pre code').forEach(block => {
                        hljs.highlightElement(block);
                    });
                }

                attachCopyHandlers();
                scrollToBottom();

            } catch (err) {
                streamCard.statusText.textContent = "AI Assistant (Error)";
                streamCard.mdContent.innerHTML = `<span style="color:#fda4af;">⚠️ ${err.message}</span>`;
            } finally {
                sendBtn.disabled = false;
                chatInput.focus();
            }
        });
    }
});
