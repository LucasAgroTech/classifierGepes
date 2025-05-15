/**
 * AI Loading Overlay Handler
 * Este script gerencia o overlay de carregamento durante operações da IA
 */

// Criar o objeto aiLoading como um singleton
const aiLoading = (function() {
    // Variáveis privadas
    let overlayElement = null;
    let progressBarElement = null;
    let messageElement = null;
    let submessageElement = null;
    let progressValue = 0;
    let progressInterval = null;
    
    // Função para criar o overlay se não existir
    function createOverlay() {
        if (overlayElement) return;
        
        // Criar o elemento do overlay
        overlayElement = document.createElement('div');
        overlayElement.id = 'aiLoadingOverlay';
        overlayElement.className = 'ai-loading-overlay';
        
        // Adicionar estilos inline para garantir que funcionem mesmo sem o CSS externo
        overlayElement.style.position = 'fixed';
        overlayElement.style.top = '0';
        overlayElement.style.left = '0';
        overlayElement.style.width = '100%';
        overlayElement.style.height = '100%';
        overlayElement.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        overlayElement.style.display = 'flex';
        overlayElement.style.flexDirection = 'column';
        overlayElement.style.justifyContent = 'center';
        overlayElement.style.alignItems = 'center';
        overlayElement.style.zIndex = '9999';
        overlayElement.style.opacity = '0';
        overlayElement.style.transition = 'opacity 0.3s ease';
        
        // Criar o conteúdo do overlay
        const content = document.createElement('div');
        content.className = 'ai-loading-content';
        content.style.backgroundColor = 'white';
        content.style.borderRadius = '8px';
        content.style.padding = '20px';
        content.style.width = '80%';
        content.style.maxWidth = '500px';
        content.style.textAlign = 'center';
        content.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        
        // Adicionar ícone de IA
        const icon = document.createElement('div');
        icon.className = 'ai-loading-icon';
        icon.innerHTML = '<i class="fas fa-robot" style="font-size: 2.5rem; color: #0d6efd; margin-bottom: 15px;"></i>';
        
        // Adicionar mensagem principal
        messageElement = document.createElement('h4');
        messageElement.className = 'ai-loading-message';
        messageElement.textContent = 'Processando...';
        messageElement.style.margin = '10px 0';
        messageElement.style.color = '#333';
        
        // Adicionar submensagem
        submessageElement = document.createElement('p');
        submessageElement.className = 'ai-loading-submessage';
        submessageElement.textContent = 'Aguarde enquanto processamos sua solicitação';
        submessageElement.style.margin = '5px 0 15px 0';
        submessageElement.style.color = '#666';
        
        // Adicionar barra de progresso
        const progressContainer = document.createElement('div');
        progressContainer.className = 'ai-loading-progress-container';
        progressContainer.style.width = '100%';
        progressContainer.style.height = '8px';
        progressContainer.style.backgroundColor = '#e9ecef';
        progressContainer.style.borderRadius = '4px';
        progressContainer.style.overflow = 'hidden';
        progressContainer.style.marginTop = '15px';
        
        progressBarElement = document.createElement('div');
        progressBarElement.className = 'ai-loading-progress-bar';
        progressBarElement.style.width = '0%';
        progressBarElement.style.height = '100%';
        progressBarElement.style.backgroundColor = '#0d6efd';
        progressBarElement.style.transition = 'width 0.3s ease';
        
        // Montar a estrutura do overlay
        progressContainer.appendChild(progressBarElement);
        content.appendChild(icon);
        content.appendChild(messageElement);
        content.appendChild(submessageElement);
        content.appendChild(progressContainer);
        overlayElement.appendChild(content);
        
        // Adicionar ao corpo do documento
        document.body.appendChild(overlayElement);
        
        // Forçar reflow para garantir que a transição funcione
        overlayElement.offsetHeight;
        
        // Armazenar no localStorage que o overlay está ativo
        localStorage.setItem('aiLoadingActive', 'true');
    }
    
    // Função para simular progresso automático
    function startProgressSimulation() {
        // Limpar qualquer intervalo existente
        if (progressInterval) {
            clearInterval(progressInterval);
        }
        
        // Resetar o progresso
        progressValue = 0;
        updateProgressBar();
        
        // Iniciar simulação de progresso
        progressInterval = setInterval(() => {
            // Aumentar o progresso de forma não linear (mais rápido no início, mais lento no final)
            if (progressValue < 90) {
                // Calcular o incremento com base no progresso atual
                // Quanto maior o progresso, menor o incremento
                const increment = (100 - progressValue) / 50;
                progressValue += increment;
                updateProgressBar();
            }
        }, 300);
    }
    
    // Função para atualizar a barra de progresso
    function updateProgressBar() {
        if (progressBarElement) {
            progressBarElement.style.width = `${progressValue}%`;
        }
    }
    
    // Objeto público com métodos expostos
    return {
        // Mostrar o overlay com mensagens personalizadas
        show: function(message, submessage) {
            createOverlay();
            
            // Atualizar mensagens
            if (message) {
                messageElement.textContent = message;
                localStorage.setItem('aiLoadingMessage', message);
            }
            
            if (submessage) {
                submessageElement.textContent = submessage;
                localStorage.setItem('aiLoadingSubmessage', submessage);
            }
            
            // Mostrar o overlay com animação
            overlayElement.style.opacity = '1';
            
            // Iniciar simulação de progresso
            startProgressSimulation();
            
            console.log("Overlay de carregamento da IA exibido");
        },
        
        // Atualizar as mensagens do overlay
        updateMessage: function(message, submessage) {
            if (!overlayElement) {
                this.show(message, submessage);
                return;
            }
            
            // Atualizar mensagens
            if (message) {
                messageElement.textContent = message;
                localStorage.setItem('aiLoadingMessage', message);
            }
            
            if (submessage) {
                submessageElement.textContent = submessage;
                localStorage.setItem('aiLoadingSubmessage', submessage);
            }
            
            console.log("Mensagens do overlay atualizadas");
        },
        
        // Completar o progresso e esconder o overlay
        completeProgress: function() {
            if (!overlayElement) return;
            
            // Limpar o intervalo de simulação
            if (progressInterval) {
                clearInterval(progressInterval);
                progressInterval = null;
            }
            
            // Definir progresso para 100%
            progressValue = 100;
            updateProgressBar();
            
            // Aguardar um momento para mostrar o progresso completo
            setTimeout(() => {
                // Esconder o overlay com animação
                overlayElement.style.opacity = '0';
                
                // Remover o overlay após a animação
                setTimeout(() => {
                    if (overlayElement && overlayElement.parentNode) {
                        overlayElement.parentNode.removeChild(overlayElement);
                        overlayElement = null;
                        progressBarElement = null;
                        messageElement = null;
                        submessageElement = null;
                    }
                    
                    // Limpar o localStorage
                    localStorage.removeItem('aiLoadingActive');
                    localStorage.removeItem('aiLoadingMessage');
                    localStorage.removeItem('aiLoadingSubmessage');
                    
                    console.log("Overlay de carregamento da IA removido");
                }, 300);
            }, 500);
        },
        
        // Verificar se o overlay está ativo
        isActive: function() {
            return overlayElement !== null || localStorage.getItem('aiLoadingActive') === 'true';
        },
        
        // Restaurar o overlay se estiver ativo no localStorage
        restoreFromLocalStorage: function() {
            if (localStorage.getItem('aiLoadingActive') === 'true') {
                const message = localStorage.getItem('aiLoadingMessage') || 'Processando...';
                const submessage = localStorage.getItem('aiLoadingSubmessage') || 'Aguarde enquanto processamos sua solicitação';
                this.show(message, submessage);
                console.log("Overlay de carregamento da IA restaurado do localStorage");
            }
        }
    };
})();

// Restaurar o overlay se estiver ativo no localStorage quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    aiLoading.restoreFromLocalStorage();
});
