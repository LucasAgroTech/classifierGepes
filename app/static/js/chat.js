/**
 * RAG Chatbot for gepesClassifier
 * Handles the chat interface and communication with the backend
 */

class ChatBot {
    constructor() {
        this.container = null;
        this.messagesContainer = null;
        this.inputField = null;
        this.sendButton = null;
        this.isOpen = false;
        this.isTyping = false;
        this.messages = [];
        this.typingTimeout = null;
        this.userInfo = null;
        
        // Initialize the chat interface
        this.init();
    }
    
    /**
     * Initialize the chat interface
     */
    init() {
        // Create chat container if it doesn't exist
        if (!document.querySelector('.chat-container')) {
            this.createChatInterface();
        } else {
            this.container = document.querySelector('.chat-container');
            this.messagesContainer = document.querySelector('.chat-messages');
            this.inputField = document.querySelector('.chat-input textarea');
            this.sendButton = document.querySelector('.chat-input button');
        }
        
        // Add event listeners
        this.addEventListeners();
        
        // Fetch user info and then add welcome message
        this.fetchUserInfo();
    }
    
    /**
     * Fetch user information from the server
     */
    fetchUserInfo() {
        fetch('/chat/user_info', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            this.userInfo = data;
            this.addWelcomeMessage();
        })
        .catch(error => {
            console.error('Error fetching user info:', error);
            // Fallback to generic welcome message if we can't get user info
            this.addWelcomeMessage();
        });
    }
    
    /**
     * Add welcome message with user information if available
     */
    addWelcomeMessage() {
        let welcomeMessage = "";
        
        if (this.userInfo && this.userInfo.nome) {
            const stats = this.userInfo.estatisticas || {};
            const userName = this.userInfo.nome.split(' ')[0]; // Pega apenas o primeiro nome
            
            // Construir mensagem com estatísticas
            welcomeMessage = `Olá, ${userName}! 👋\n\nBem-vindo de volta ao classificador.`;
            
            // Adicionar estatísticas se disponíveis
            if (Object.keys(stats).length > 0) {
                welcomeMessage += ` Aqui estão alguns dados sobre sua performance:\n\n`;
                
                // Estatísticas básicas
                welcomeMessage += `📊 Classificações: **${stats.total_classificacoes || 0}**  \n`;
                welcomeMessage += `🔍 Projetos: **${stats.projetos_unicos || 0}**  \n`;
                
                // Uso da IA
                if (stats.projetos_com_ia > 0) {
                    welcomeMessage += `🤖 Uso da IA: **${stats.projetos_com_ia}** vezes (**${stats.taxa_uso_ia}%**)  \n`;
                }
                
                // Ratings médios
                if (stats.media_aia > 0 || stats.media_tecverde > 0) {
                    welcomeMessage += `⭐ AIA: **${stats.media_aia}** \n`;
                }

                // Ratings médios
                if (stats.media_aia > 0 || stats.media_tecverde > 0) {
                    welcomeMessage += `⭐ Tec Verde: **${stats.media_tecverde}**  \n`;
                }
                
                // Última classificação
                if (stats.ultima_classificacao && stats.ultima_classificacao !== "Nenhuma") {
                    welcomeMessage += `📅 Última atuação: **${stats.ultima_classificacao}**  \n\n`;
                }
                
                // Segmentos frequentes
                if (stats.segmentos_frequentes && stats.segmentos_frequentes.length > 0) {
                    const segmentos = stats.segmentos_frequentes.join(', ');
                    welcomeMessage += `📌 Segmentos recorrentes: **${segmentos}**  \n\n`;
                }
                
                // Comparação com outros usuários
                if (stats.percentil > 50) {
                    welcomeMessage += `Você está entre os **${stats.percentil}%** mais ativos da plataforma. Continue assim!\n`;
                } else if (stats.total_classificacoes > 0) {
                    welcomeMessage += `Você já contribuiu com **${stats.total_classificacoes}** classificações. `;
                    if (stats.media_usuarios > 0) {
                        welcomeMessage += `A média entre usuários é **${stats.media_usuarios}**.\n`;
                    }
                }
                
                // Projetos pendentes
                if (stats.projetos_pendentes > 0) {
                    welcomeMessage += `Temos **${stats.projetos_pendentes}** projetos aguardando sua análise.`;
                }
            } else {
                // Mensagem simplificada sem estatísticas
                welcomeMessage += ` Como posso ajudar você hoje? Posso fornecer informações sobre projetos, categorias, tecnologias verdes e muito mais.`;
            }
        } else {
            // Mensagem genérica caso não tenha informações do usuário
            welcomeMessage = "Olá! Sou o assistente do gepesClassifier. Como posso ajudar você hoje? Posso fornecer informações sobre projetos, categorias, tecnologias verdes e muito mais.";
        }
        
        this.addBotMessage(welcomeMessage);
    }
    
    /**
     * Create the chat interface elements
     */
    createChatInterface() {
        // Create container
        this.container = document.createElement('div');
        this.container.className = 'chat-container minimized';
        
        // Create header
        const header = document.createElement('div');
        header.className = 'chat-header';
        header.innerHTML = `
            <h3><i class="fas fa-brain"></i> <span>Agente</span></h3>
            <div class="chat-controls">
                <button class="minimize-chat" title="Minimizar"><i class="fas fa-minus"></i></button>
                <button class="clear-chat" title="Limpar conversa"><i class="fas fa-trash"></i></button>
            </div>
        `;
        
        // Create messages container
        this.messagesContainer = document.createElement('div');
        this.messagesContainer.className = 'chat-messages';
        
        // Create input area
        const inputArea = document.createElement('div');
        inputArea.className = 'chat-input';
        
        this.inputField = document.createElement('textarea');
        this.inputField.placeholder = 'Digite sua mensagem...';
        this.inputField.rows = 1;
        
        this.sendButton = document.createElement('button');
        this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        this.sendButton.disabled = true;
        
        inputArea.appendChild(this.inputField);
        inputArea.appendChild(this.sendButton);
        
        // Append all elements to container
        this.container.appendChild(header);
        this.container.appendChild(this.messagesContainer);
        this.container.appendChild(inputArea);
        
        // Append container to body
        document.body.appendChild(this.container);
    }
    
    /**
     * Add event listeners to chat elements
     */
    addEventListeners() {
        // Toggle chat on header click
        const header = this.container.querySelector('.chat-header');
        header.addEventListener('click', (e) => {
            // Ignore clicks on control buttons
            if (e.target.closest('.chat-controls')) return;
            
            // If minimized, open the chat
            if (this.container.classList.contains('minimized')) {
                this.toggleChat(true);
            } else {
                this.toggleChat();
            }
        });
        
        // Minimize chat
        const minimizeBtn = this.container.querySelector('.minimize-chat');
        minimizeBtn.addEventListener('click', () => {
            this.toggleChat(false);
        });
        
        // Clear chat
        const clearBtn = this.container.querySelector('.clear-chat');
        clearBtn.addEventListener('click', () => {
            this.clearChat();
        });
        
        // Send message on button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enable/disable send button based on input
        this.inputField.addEventListener('input', () => {
            this.sendButton.disabled = !this.inputField.value.trim();
            this.adjustTextareaHeight();
        });
        
        // Send message on Enter key (but allow Shift+Enter for new line)
        this.inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!this.sendButton.disabled) {
                    this.sendMessage();
                }
            }
        });
    }
    
    /**
     * Toggle chat open/closed
     */
    toggleChat(forceState = null) {
        this.isOpen = forceState !== null ? forceState : !this.isOpen;
        
        if (this.isOpen) {
            // Opening the chat
            this.container.classList.add('open');
            this.container.classList.remove('minimized');
            this.inputField.focus();
            this.scrollToBottom();
            
            // Update minimize button icon
            const minimizeBtn = this.container.querySelector('.minimize-chat i');
            minimizeBtn.className = 'fas fa-minus';
        } else {
            // Closing/minimizing the chat
            this.container.classList.remove('open');
            this.container.classList.add('minimized');
            
            // Update minimize button icon
            const minimizeBtn = this.container.querySelector('.minimize-chat i');
            minimizeBtn.className = 'fas fa-expand';
        }
    }
    
    /**
     * Clear all messages from the chat
     */
    clearChat() {
        // Clear messages array
        this.messages = [];
        
        // Clear messages container
        this.messagesContainer.innerHTML = '';
        
        // Add welcome message again
        this.addWelcomeMessage();
        
        // Send clear request to server to reset session
        fetch('/chat/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        });
    }
    
    /**
     * Send a message to the server
     */
    sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addUserMessage(message);
        
        // Clear input field
        this.inputField.value = '';
        this.adjustTextareaHeight();
        this.sendButton.disabled = true;
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Prepare message data with user info if available
        const messageData = {
            message: message
        };
        
        // Send message to server
        fetch('/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(messageData)
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response to chat
            this.addBotMessage(data.response);
        })
        .catch(error => {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addBotMessage("Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde.");
        });
    }
    
    /**
     * Add a user message to the chat
     */
    addUserMessage(text) {
        const message = {
            text,
            sender: 'user',
            time: new Date()
        };
        
        this.messages.push(message);
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message user';
        messageElement.innerHTML = `
            ${this.escapeHTML(text)}
            <div class="message-time">${this.formatTime(message.time)}</div>
        `;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    /**
     * Add a bot message to the chat
     */
    addBotMessage(text) {
        const message = {
            text,
            sender: 'bot',
            time: new Date()
        };
        
        this.messages.push(message);
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot';
        messageElement.innerHTML = `
            ${this.formatBotMessage(text)}
            <div class="message-time">${this.formatTime(message.time)}</div>
        `;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        this.isTyping = true;
        
        const typingElement = document.createElement('div');
        typingElement.className = 'typing-indicator';
        typingElement.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        
        this.messagesContainer.appendChild(typingElement);
        this.scrollToBottom();
    }
    
    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        this.isTyping = false;
        
        const typingIndicator = this.messagesContainer.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    /**
     * Format bot message with markdown-like syntax
     */
    formatBotMessage(text) {
        // Convert line breaks to <br>
        let formatted = text.replace(/\n/g, '<br>');
        
        // Format code blocks
        formatted = formatted.replace(/```([^`]+)```/g, '<pre>$1</pre>');
        
        // Format inline code
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Format bold text
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Format italic text
        formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        return formatted;
    }
    
    /**
     * Format time for message timestamp
     */
    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    /**
     * Adjust textarea height based on content
     */
    adjustTextareaHeight() {
        this.inputField.style.height = 'auto';
        this.inputField.style.height = `${Math.min(this.inputField.scrollHeight, 100)}px`;
    }
    
    /**
     * Get CSRF token from cookies
     */
    getCSRFToken() {
        const name = 'csrf_token=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookieArray = decodedCookie.split(';');
        
        for (let i = 0; i < cookieArray.length; i++) {
            let cookie = cookieArray[i].trim();
            if (cookie.indexOf(name) === 0) {
                return cookie.substring(name.length, cookie.length);
            }
        }
        
        return '';
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize on dashboard, projects, and categorize pages
    if (document.querySelector('.dashboard-header') || 
        document.querySelector('.projects-header') || 
        document.querySelector('.page-header')) {
        window.chatBot = new ChatBot();
    }
});
