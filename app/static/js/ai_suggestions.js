/**
 * AI Suggestions Handler - Versão Modernizada
 * Este script gerencia a funcionalidade de sugestões da IA para a página de categorização.
 */

// Função para inicializar sugestões da IA com animações e efeitos modernos
function initAiSuggestions() {
    console.log("Inicializando módulo de sugestões da IA...");
    
    // Atualizar mensagem do overlay de carregamento se estiver ativo
    if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
        aiLoading.updateMessage(
            "Processando sugestões da IA...",
            "Analisando o projeto e gerando recomendações inteligentes"
        );
    }
    
    // Variável para armazenar as sugestões da IA
    let aiSuggestions = null;
    
    // Utilizar a variável global definida no template
    try {
        // Verificar se a variável global aiSuggestionData existe
        if (typeof aiSuggestionData !== 'undefined') {
            aiSuggestions = aiSuggestionData;
            console.log("Dados da IA carregados:", aiSuggestions);
            
            // Atualizar mensagem do overlay
            if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                aiLoading.updateMessage(
                    "Aplicando sugestões...",
                    "Preparando a interface com as recomendações da IA"
                );
            }
            
            // Exibir informações da sugestão com animação
            displayAiSuggestions(aiSuggestions);
            
            // Aplicar automaticamente as sugestões aos campos do formulário
            applyAllAiSuggestions(aiSuggestions);
        } else {
            console.log("Nenhuma sugestão da IA disponível");
            
            // Esconder o overlay de carregamento se estiver ativo
            if (typeof aiLoading !== 'undefined') {
                // Forçar a limpeza do overlay independentemente do estado do localStorage
                console.log('Forçando limpeza do overlay após processamento das sugestões da IA');
                aiLoading.forceCleanup();
                
                // Garantir que o localStorage também seja limpo
                localStorage.removeItem('aiLoadingActive');
                localStorage.removeItem('aiLoadingMessage');
                localStorage.removeItem('aiLoadingSubmessage');
            }
        }
    } catch (error) {
        console.error("Erro ao processar dados da IA:", error);
        
        // Esconder o overlay de carregamento em caso de erro
        if (typeof aiLoading !== 'undefined') {
            // Forçar a limpeza do overlay independentemente do estado do localStorage
            console.log('Forçando limpeza do overlay após erro no processamento das sugestões da IA');
            aiLoading.forceCleanup();
            
            // Garantir que o localStorage também seja limpo
            localStorage.removeItem('aiLoadingActive');
            localStorage.removeItem('aiLoadingMessage');
            localStorage.removeItem('aiLoadingSubmessage');
        }
    }
    
    /**
     * Função para exibir as informações da sugestão da IA com efeitos visuais
     * @param {Object} data - Dados de sugestão da IA
     */
    function displayAiSuggestions(data) {
        if (!data) {
            console.error("Dados da IA inválidos");
            return;
        }
        
        aiSuggestions = data;
        
        // Mostrar a seção de sugestões com animação
        $('#aiSuggestionSection').fadeIn(300);
        
        // Atualizar badge de confiança com classes modernas
        if (data.confianca) {
            let confidenceClass = 'accent-badge-info';
            let borderColor = '#17a2b8'; // cor padrão info
            
            if (data.confianca === 'ALTA') {
                confidenceClass = 'accent-badge-success';
                borderColor = '#198754'; // cor verde para alta confiança
            } else if (data.confianca === 'BAIXA') {
                confidenceClass = 'accent-badge-warning';
                borderColor = '#ffc107'; // cor amarela para baixa confiança
            }
            
            // Aplicar classes com animação
            $('#aiConfidenceBadge')
                .hide()
                .removeClass('accent-badge-info accent-badge-success accent-badge-warning')
                .addClass(confidenceClass)
                .css('border-color', borderColor)
                .find('span').text(data.confianca)
                .end()
                .fadeIn(400);
        }
        
        // Atualizar justificativa
        if (data.justificativa) {
            $('#aiJustificationText').text(data.justificativa);
        }
        
        // Atualizar categorias sugeridas
        updateAiCategories(data);
        
        // Mostrar a seção de sugestões de tecnologias verdes
        if (data.tecverde_justificativa || data.tecverde_se_aplica || data.tecverde_confianca) {
            console.log("Exibindo sugestões de tecnologias verdes:", {
                seAplica: data.tecverde_se_aplica,
                classe: data.tecverde_classe,
                subclasse: data.tecverde_subclasse,
                confianca: data.tecverde_confianca,
                justificativa: data.tecverde_justificativa
            });
            
            $('#aiTecverdeSuggestionSection').fadeIn(300);
            
            // Atualizar badge de confiança para tecnologias verdes
            if (data.tecverde_confianca) {
                let confidenceClass = 'accent-badge-info';
                let borderColor = '#17a2b8'; // cor padrão info
                
                if (data.tecverde_confianca === 'ALTA') {
                    confidenceClass = 'accent-badge-success';
                    borderColor = '#198754'; // cor verde para alta confiança
                } else if (data.tecverde_confianca === 'BAIXA') {
                    confidenceClass = 'accent-badge-warning';
                    borderColor = '#ffc107'; // cor amarela para baixa confiança
                }
                
                // Aplicar classes com animação
                $('#aiTecverdeConfidenceBadge')
                    .hide()
                    .removeClass('accent-badge-info accent-badge-success accent-badge-warning')
                    .addClass(confidenceClass)
                    .css('border-color', borderColor)
                    .find('span').text(data.tecverde_confianca)
                    .end()
                    .fadeIn(400);
            }
            
            // Atualizar justificativa para tecnologias verdes
            if (data.tecverde_justificativa) {
                $('#aiTecverdeJustificationText').text(data.tecverde_justificativa);
            }
            
            // Atualizar categorias de tecnologias verdes sugeridas
            updateAiTecverdeCategories(data);
        } else {
            console.log("Nenhuma sugestão de tecnologias verdes disponível");
            $('#aiTecverdeSuggestionSection').hide();
        }
    }
    
    /**
     * Função para atualizar as categorias de tecnologias verdes sugeridas pela IA
     * @param {Object} data - Dados de sugestão da IA
     */
    function updateAiTecverdeCategories(data) {
        // Atualizar se aplica - converter valor binário para texto
        const seAplica = parseInt(data.tecverde_se_aplica);
        const seAplicaTexto = seAplica === 1 ? "Sim" : "Não";
        $('#aiTecverdeSeAplica').text(seAplicaTexto || '-');
        
        // Atualizar classe e subclasse, mostrando "Não se aplica" se a tecnologia verde não se aplica
        if (seAplica === 0) {
            // Se tecnologia verde não se aplica, mostrar "Não se aplica" para classe e subclasse
            $('#aiTecverdeClasse').text("Não se aplica");
            $('#aiTecverdeSubclasse').text("Não se aplica");
        } else {
            // Caso contrário, mostrar os valores normais ou '-' se estiverem vazios
            const classe = data.tecverde_classe || '';
            $('#aiTecverdeClasse').text(classe || '-');
            
            const subclasse = data.tecverde_subclasse || '';
            $('#aiTecverdeSubclasse').text(subclasse || '-');
        }
    }
    
    /**
     * Função para atualizar as categorias sugeridas pela IA
     * @param {Object} data - Dados de sugestão da IA
     */
    function updateAiCategories(data) {
        // Atualizar macroarea
        const macroarea = data._aia_n1_macroarea || data.microarea || '';
        $('#aiMacroarea').text(macroarea || '-');
        
        // Atualizar segmento
        const segmento = data._aia_n2_segmento || data.segmento || '';
        $('#aiSegmento').text(segmento || '-');
        
        // Atualizar domínios afeitos como balões
        const dominioAfeito = data._aia_n3_dominio_afeito || data.dominio || '';
        updateCategoryBubbles('aiDominioAfeito', dominioAfeito);
        
        // Atualizar domínios afeitos outros como balões
        const dominioOutro = data._aia_n3_dominio_outro || data.dominio_outro || '';
        
        // Verificar se há domínios outros para exibir ou ocultar a seção
        if (dominioOutro && dominioOutro !== 'N/A' && dominioOutro !== '-') {
            $('#aiDominioOutroContainer').show();
            updateCategoryBubbles('aiDominioOutro', dominioOutro);
        } else {
            $('#aiDominioOutroContainer').hide();
        }
    }
    
    /**
     * Função para criar balões de categorias a partir de uma string separada por ponto-e-vírgula
     * @param {string} containerId - ID do container onde os balões serão adicionados
     * @param {string} categoriesString - String com categorias separadas por ponto-e-vírgula
     */
    function updateCategoryBubbles(containerId, categoriesString) {
        const container = $(`#${containerId}`);
        container.empty();
        
        // Verificar se há categorias para exibir
        if (!categoriesString || categoriesString === 'N/A' || categoriesString === '-') {
            container.append('<span class="no-categories">Nenhuma categoria</span>');
            return;
        }
        
        // Dividir a string em categorias individuais
        let categories = [];
        if (typeof categoriesString === 'string' && categoriesString.includes(';')) {
            categories = categoriesString.split(';').map(cat => cat.trim()).filter(cat => cat);
        } else if (Array.isArray(categoriesString)) {
            categories = categoriesString.filter(cat => cat);
        } else {
            categories = [categoriesString];
        }
        
        // Criar um balão para cada categoria
        categories.forEach(category => {
            const bubble = $('<span>')
                .addClass('category-bubble')
                .text(category);
            container.append(bubble);
        });
    }
    
    /**
     * Função dedicada para garantir que a justificativa da IA seja aplicada ao campo de observações
     * @param {Object} data - Dados de sugestão da IA
     * @param {boolean} force - Se verdadeiro, substitui mesmo se o campo já estiver preenchido
     */
    function applyTecverdeJustification(data, force = false) {
        if (!data) {
            console.error("Dados da IA inválidos para aplicar justificativa");
            return;
        }
        
        const justificativa = data.tecverde_justificativa || '';
        const seAplica = data.tecverde_se_aplica || '';
        
        if (justificativa) {
            console.log("Aplicando justificativa para tecnologias verdes:", justificativa);
            
            // Verificar se o campo de observações está vazio ou se estamos forçando a aplicação
            const observacoesAtuais = $('#tecverde_observacoes').val();
            
            if (force || !observacoesAtuais || observacoesAtuais.trim() === '') {
                console.log("Inserindo justificativa da IA no campo de observações...");
                
                // Formatar a justificativa de acordo com o valor de "se aplica"
                let textoJustificativa = justificativa;
                if (seAplica === "Não" || seAplica === "Nao") {
                    textoJustificativa = "Motivo para não se aplicar: " + justificativa;
                }
                
                // Inserir a justificativa no campo de observações
                $('#tecverde_observacoes').val(textoJustificativa);
                console.log("Justificativa inserida com sucesso:", textoJustificativa);
                
                return true;
            } else {
                console.log("Campo de observações já preenchido, não substituindo:", observacoesAtuais);
                return false;
            }
        } else {
            console.log("Nenhuma justificativa disponível para aplicar");
            return false;
        }
    }
    
    /**
     * Função para aplicar todas as sugestões da IA aos campos do formulário
     * @param {Object} data - Dados de sugestão da IA
     */
    function applyAllAiSuggestions(data) {
        if (!data) {
            console.error("Não há sugestões da IA para aplicar");
            
            // Esconder o overlay de carregamento se estiver ativo
            if (typeof aiLoading !== 'undefined') {
                // Forçar a limpeza do overlay independentemente do estado do localStorage
                console.log('Forçando limpeza do overlay quando não há sugestões da IA para aplicar');
                aiLoading.forceCleanup();
                
                // Garantir que o localStorage também seja limpo
                localStorage.removeItem('aiLoadingActive');
                localStorage.removeItem('aiLoadingMessage');
                localStorage.removeItem('aiLoadingSubmessage');
            }
            
            return;
        }
        
        // Verificar se já existem valores nos campos de classificação por área de interesse
        const currentMicroarea = $('#microarea').val();
        const currentSegmento = $('#segmento').val();
        const currentDominio = $('#dominio').val();
        const currentDominioOutros = $('#dominio_outros').val();
        
        // Verificar se já existem valores nos campos de tecnologias verdes
        const currentTecverdeSePlica = $('#tecverde_se_aplica').val();
        const currentTecverdeClasse = $('#tecverde_classe').val();
        const currentTecverdeSubclasse = $('#tecverde_subclasse').val();
        
        console.log("Valores atuais nos campos:", {
            microarea: currentMicroarea,
            segmento: currentSegmento,
            dominio: currentDominio,
            dominio_outros: currentDominioOutros,
            tecverde_se_aplica: currentTecverdeSePlica,
            tecverde_classe: currentTecverdeClasse,
            tecverde_subclasse: currentTecverdeSubclasse
        });
        
        // Indicar que estamos aplicando sugestões da IA (para não marcar como modificado pelo usuário)
        window.applyingAiSuggestions = true;
        
        // Contador para controlar quando todas as operações foram concluídas
        let operationsCompleted = 0;
        const totalOperations = 2; // AIA classificação e Tecnologias Verdes
        
        // Função para verificar se todas as operações foram concluídas e remover o overlay
        function checkCompletion() {
            operationsCompleted++;
            console.log(`Operação concluída: ${operationsCompleted}/${totalOperations}`);
            
            if (operationsCompleted >= totalOperations) {
                console.log("Todas as operações concluídas, removendo overlay e restaurando flags...");
                window.applyingAiSuggestions = false;
                
                // Verificar se há observações para tecnologias verdes para aplicar
                if (data.tecverde_justificativa) {
                    applyTecverdeJustification(data);
                }
                
                // Esconder o overlay de carregamento se estiver ativo
                if (typeof aiLoading !== 'undefined') {
                    // Forçar a limpeza do overlay independentemente do estado do localStorage
                    console.log('Forçando limpeza do overlay após completar todas as operações');
                    aiLoading.forceCleanup();
                    
                    // Garantir que o localStorage também seja limpo
                    localStorage.removeItem('aiLoadingActive');
                    localStorage.removeItem('aiLoadingMessage');
                    localStorage.removeItem('aiLoadingSubmessage');
                }
            }
        }
        
        // Verificar se há dados salvos pelo usuário para classificação por área de interesse
        const hasUserAiaData = currentMicroarea || currentSegmento || 
            (currentDominio && currentDominio.length > 0) || 
            (currentDominioOutros && currentDominioOutros.length > 0);
        
        // Verificar se há dados salvos pelo usuário para tecnologias verdes
        const hasUserTecverdeData = currentTecverdeSePlica || currentTecverdeClasse || currentTecverdeSubclasse;
        
        // Aplicar sugestões para classificação por área de interesse apenas se não houver dados do usuário
        if (!hasUserAiaData) {
            console.log("Não há dados salvos pelo usuário para classificação por área de interesse, aplicando sugestões da IA");
            applyAiaClassification(data, checkCompletion);
        } else {
            console.log("Dados do usuário encontrados para classificação por área de interesse, mantendo dados do usuário");
            checkCompletion(); // Marcar como concluído mesmo se não aplicar
        }
        
        // Aplicar sugestões para tecnologias verdes apenas se não houver dados do usuário e houver sugestões da IA
        if (!hasUserTecverdeData && (data.tecverde_classe || data.tecverde_subclasse || data.tecverde_se_aplica)) {
            console.log("Não há dados salvos pelo usuário para tecnologias verdes, aplicando sugestões da IA");
            applyTecverdeClassification(data, checkCompletion);
        } else {
            if (hasUserTecverdeData) {
                console.log("Dados do usuário encontrados para tecnologias verdes, mantendo dados do usuário");
            } else {
                console.log("Não há sugestões da IA para tecnologias verdes");
            }
            checkCompletion(); // Marcar como concluído mesmo se não aplicar
        }
    }
    
    /**
     * Função auxiliar para garantir que "Não" seja aplicado corretamente
     * @param {number} tentativa - Número da tentativa atual (para controle de recursão)
     */
    function garantirNaoAplicado(tentativa = 1) {
        const valorAtual = $('#tecverde_se_aplica').val();
        const textoSelecionado = $('#tecverde_se_aplica option:selected').text();
        
        console.log(`Verificação #${tentativa}: Estado atual:`, {
            valor: valorAtual,
            texto: textoSelecionado
        });
        
        // Se nem o valor (com ou sem acento) nem o texto for "Não"
        if (valorAtual !== "Não" && valorAtual !== "Nao" && textoSelecionado !== "Não") {
            console.log(`Tentativa #${tentativa} de aplicar 'Não'...`);
            
            // Diagnóstico do select
            const selectElement = document.getElementById('tecverde_se_aplica');
            if (selectElement) {
                console.log("Diagnóstico do select antes da modificação:");
                for (let i = 0; i < selectElement.options.length; i++) {
                    const option = selectElement.options[i];
                    console.log(`Opção ${i}:`, {
                        valor: option.value,
                        texto: option.text,
                        selected: option.selected
                    });
                }
                
                // Modificar o valor para evitar problemas com acentuação
                if (selectElement.options.length >= 3 && selectElement.options[2].text === "Não") {
                    selectElement.options[2].value = "Nao"; // Sem acento
                    console.log("Valor da opção 'Não' modificado para 'Nao'");
                }
                
                // Selecionar pelo índice
                selectElement.selectedIndex = 2; // Geralmente a terceira opção (índice 2) é "Não"
                console.log(`Tentativa #${tentativa}: Selecionado pelo índice (2)`);
                
                // Verificar o resultado
                if (selectElement.selectedIndex === 2) {
                    const option = selectElement.options[2];
                    console.log(`Tentativa #${tentativa}: Opção selecionada:`, {
                        índice: 2,
                        valor: option.value,
                        texto: option.text
                    });
                    
                    // Agora tentar definir via jQuery com o valor sem acento
                    $('#tecverde_se_aplica').val("Nao");
                }
                
                // Disparar eventos de change
                $('#tecverde_se_aplica').trigger('change');
                
                const event = new Event('change', { bubbles: true });
                selectElement.dispatchEvent(event);
                
                // Verificar resultado após as tentativas
                const valorAposChange = $('#tecverde_se_aplica').val();
                const textoAposChange = $('#tecverde_se_aplica option:selected').text();
                const indiceAposChange = selectElement.selectedIndex;
                
                console.log(`Após alterações: Estado final:`, {
                    valor: valorAposChange,
                    texto: textoAposChange,
                    índice: indiceAposChange
                });
                
                // Se ainda não estiver correto e dentro do limite de tentativas, tentar novamente
                if (indiceAposChange !== 2 && textoAposChange !== "Não" && tentativa < 5) {
                    setTimeout(() => garantirNaoAplicado(tentativa + 1), 300);
                }
            } else {
                console.error("Elemento select não encontrado!");
            }
        } else {
            console.log(`Valor 'Não' já aplicado com sucesso:`, {
                valor: valorAtual,
                texto: textoSelecionado
            });
        }
    }
    
    /**
     * Função para aplicar as sugestões de tecnologias verdes
     * @param {Object} data - Dados de sugestão da IA
     * @param {Function} callback - Função para chamar quando concluído
     */
    function applyTecverdeClassification(data, callback) {
        // Mapear campos da API para campos da UI
        const seAplica = parseInt(data.tecverde_se_aplica) || 0;
        const classe = data.tecverde_classe || '';
        const subclasse = data.tecverde_subclasse || '';
        const justificativa = data.tecverde_justificativa || '';
        
        console.log("Aplicando sugestões de tecnologias verdes:", {
            seAplica, classe, subclasse, justificativa
        });

        // Aplicar as sugestões com um delay mínimo
        setTimeout(() => {
            console.log("Iniciando aplicação das sugestões de tecnologias verdes");
            
            // Definir o campo "Se aplica" com base no valor binário
            const selectElement = document.getElementById('tecverde_se_aplica');
            if (selectElement && selectElement.options.length >= 3) {
                // Selecionar com base no valor binário: 0 = Não (índice 2), 1 = Sim (índice 1)
                const selectedIndex = seAplica === 1 ? 1 : 2;
                selectElement.selectedIndex = selectedIndex;
                console.log(`Opção selecionada pelo índice (${selectedIndex}): ${selectElement.options[selectedIndex].text}`);
                
                // Disparar eventos de mudança
                $('#tecverde_se_aplica').trigger('change');
                selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                
                // Se for "Sim" (1), aplicar classe e subclasse
                if (seAplica === 1) {
                    // Pequeno delay para garantir que os campos estejam habilitados
                    setTimeout(() => {
                        if (classe) {
                            $('#tecverde_classe').val(classe);
                            console.log("Classe de tecnologia verde definida para:", classe);
                            $('#tecverde_classe').trigger('change');
                            
                            // Aguardar atualização das subclasses
                            setTimeout(() => {
                                if (subclasse) {
                                    $('#tecverde_subclasse').val(subclasse);
                                    console.log("Subclasse de tecnologia verde definida para:", subclasse);
                                    $('#tecverde_subclasse').trigger('change');
                                }
                                
                                // Aplicar justificativa
                                if (justificativa) {
                                    applyTecverdeJustification(data);
                                }
                                
                                if (typeof callback === 'function') callback();
                            }, 500);
                        } else {
                            if (justificativa) {
                                applyTecverdeJustification(data);
                            }
                            if (typeof callback === 'function') callback();
                        }
                    }, 300);
                } else {
                    // Para "Não" (0), limpar campos e aplicar justificativa
                    $('#tecverde_classe, #tecverde_subclasse').val('');
                    console.log("Valores de classe e subclasse limpos (se_aplica = 0)");
                    
                    if (justificativa) {
                        applyTecverdeJustification(data);
                    }
                    
                    if (typeof callback === 'function') callback();
                }
            } else {
                console.error("Estrutura do select inválida");
                if (typeof callback === 'function') callback();
            }
        }, 300);
    }
    
    /**
     * Função para aplicar as sugestões de classificação por área de interesse
     * @param {Object} data - Dados de sugestão da IA
     * @param {Function} callback - Função para chamar quando concluído
     */
    function applyAiaClassification(data, callback) {
        // Mapear campos da API para campos da UI
        const microarea = data._aia_n1_macroarea || data.microarea || '';
        const segmento = data._aia_n2_segmento || data.segmento || '';
        const dominio = data._aia_n3_dominio_afeito || data.dominio || '';
        const dominio_outros = data._aia_n3_dominio_outro || data.dominio_outro || '';
        
        console.log("Aplicando sugestões de classificação por área de interesse:", {
            microarea, segmento, dominio, dominio_outros
        });
        
        // Função para aplicar domínios após os selects de microarea e segmento estiverem atualizados
        function aplicarDominios() {
            console.log("Aplicando domínios após atualização dos selects...");
            
            // Aplicar domínios
            if (dominio) {
                let dominioValues = [];
                if (typeof dominio === 'string' && dominio.includes(';')) {
                    dominioValues = dominio.split(';').map(d => d.trim()).filter(d => d);
                } else if (Array.isArray(dominio)) {
                    dominioValues = dominio.filter(d => d);
                } else if (dominio) {
                    dominioValues = [dominio];
                }
                
                if (dominioValues.length > 0) {
                    console.log("Valores de domínio a aplicar:", dominioValues);
                    
                    // Verificar se há opções disponíveis no select
                    const hasOptions = $('#dominio option').length > 0;
                    console.log("Opções disponíveis no select de domínio:", hasOptions, "Total:", $('#dominio option').length);
                    
                    // Forçar a adição dos valores como options se não existirem
                    if (!hasOptions && dominioValues.length > 0) {
                        console.log("Não há opções no select de domínio, adicionando os valores manualmente");
                        dominioValues.forEach(value => {
                            $('#dominio').append(new Option(value, value));
                        });
                        console.log(`Adicionadas ${dominioValues.length} opções ao select de domínio`);
                    }
                    
                    // Verificar se estamos usando Choices.js
                    if (window.dominioChoices) {
                        try {
                            // Destruir e recriar o Choices.js para garantir que está atualizado
                            if (typeof window.dominioChoices.destroy === 'function') {
                                window.dominioChoices.destroy();
                                console.log("Choices.js para domínio destruído para recriação");
                            }
                            
                            // Recriar o Choices.js
                            window.dominioChoices = new Choices('#dominio', {
                                removeItemButton: true,
                                searchEnabled: true,
                                searchPlaceholderValue: 'Pesquisar domínios...',
                                placeholder: true,
                                placeholderValue: 'Selecione os domínios',
                                noResultsText: 'Nenhum resultado encontrado',
                                noChoicesText: 'Nenhuma opção disponível',
                                itemSelectText: 'Clique para selecionar',
                                classNames: {
                                    containerOuter: 'choices shadow-sm'
                                }
                            });
                            
                            // Adicionar os valores
                            window.dominioChoices.setChoiceByValue(dominioValues);
                            console.log("Domínios definidos via Choices.js recriado");
                        } catch (e) {
                            console.error("Erro ao definir domínios via Choices.js:", e);
                            // Fallback para o método tradicional
                            $('#dominio').val(dominioValues);
                            $('#dominio').trigger('change');
                            console.log("Domínios definidos via jQuery (fallback)");
                        }
                    } else {
                        // Fallback para o método tradicional
                        $('#dominio').val(dominioValues);
                        // Forçar o evento change para garantir que os listeners sejam acionados
                        $('#dominio').trigger('change');
                        console.log("Domínios definidos via jQuery");
                    }
                }
            }
            
            // Aplicar domínios outros
            if (dominio_outros) {
                // Tratar valores N/A ou vazios
                if (dominio_outros === 'N/A' || dominio_outros === '') {
                    console.log("Domínios afeitos outros está vazio ou marcado como N/A. Definindo como vazio no formulário.");
                    // Limpar o campo de domínios outros
                    $('#dominio_outros').val([]);
                    
                    // Atualizar o select para refletir as mudanças
                    $('#dominio_outros').trigger('change');
                    
                    // Adicionar um atributo de dados para indicar que foi definido como N/A
                    $('#dominio_outros').attr('data-na', 'true');
                } else {
                    let dominioOutrosValues = [];
                    if (typeof dominio_outros === 'string' && dominio_outros.includes(';')) {
                        dominioOutrosValues = dominio_outros.split(';').map(d => d.trim()).filter(d => d);
                    } else if (Array.isArray(dominio_outros)) {
                        dominioOutrosValues = dominio_outros.filter(d => d);
                    } else if (dominio_outros) {
                        dominioOutrosValues = [dominio_outros];
                    }
                    
                    if (dominioOutrosValues.length > 0) {
                        console.log("Valores de domínio outros a aplicar:", dominioOutrosValues);
                        
                        // Verificar se há opções disponíveis no select
                        const hasOptions = $('#dominio_outros option').length > 0;
                        console.log("Opções disponíveis no select de domínio outros:", hasOptions, "Total:", $('#dominio_outros option').length);
                        
                        // Forçar a adição dos valores como options se não existirem
                        if (!hasOptions && dominioOutrosValues.length > 0) {
                            console.log("Não há opções no select de domínios outros, adicionando os valores manualmente");
                            dominioOutrosValues.forEach(value => {
                                $('#dominio_outros').append(new Option(value, value));
                            });
                            console.log(`Adicionadas ${dominioOutrosValues.length} opções ao select de domínios outros`);
                        }
                        
                        // Verificar se estamos usando Choices.js
                        if (window.dominioOutrosChoices) {
                            try {
                                // Destruir e recriar o Choices.js para garantir que está atualizado
                                if (typeof window.dominioOutrosChoices.destroy === 'function') {
                                    window.dominioOutrosChoices.destroy();
                                    console.log("Choices.js para domínio outros destruído para recriação");
                                }
                                
                                // Recriar o Choices.js
                                window.dominioOutrosChoices = new Choices('#dominio_outros', {
                                    removeItemButton: true,
                                    searchEnabled: true,
                                    searchPlaceholderValue: 'Pesquisar domínios afeitos outros...',
                                    placeholder: true,
                                    placeholderValue: 'Selecione os domínios afeitos outros',
                                    noResultsText: 'Nenhum resultado encontrado',
                                    noChoicesText: 'Nenhuma opção disponível',
                                    itemSelectText: 'Clique para selecionar',
                                    classNames: {
                                        containerOuter: 'choices shadow-sm'
                                    }
                                });
                                
                                // Adicionar os valores
                                window.dominioOutrosChoices.setChoiceByValue(dominioOutrosValues);
                                console.log("Domínios outros definidos via Choices.js recriado");
                            } catch (e) {
                                console.error("Erro ao definir domínios outros via Choices.js:", e);
                                // Fallback para o método tradicional
                                $('#dominio_outros').val(dominioOutrosValues);
                                $('#dominio_outros').trigger('change');
                                console.log("Domínios outros definidos via jQuery (fallback)");
                            }
                        } else {
                            // Fallback para o método tradicional
                            $('#dominio_outros').val(dominioOutrosValues);
                            // Forçar o evento change para garantir que os listeners sejam acionados
                            $('#dominio_outros').trigger('change');
                            console.log("Domínios outros definidos via jQuery");
                        }
                    }
                }
            }
            
            // Completar a operação
            if (typeof callback === 'function') {
                console.log("Aplicação de domínios concluída, chamando callback");
                callback();
            }
        }
        
        // Função para aplicar segmento após a microárea estar atualizada
        function aplicarSegmento() {
            if (segmento) {
                console.log("Aplicando segmento:", segmento);
                
                // Verificar se o segmento existe nas opções
                let segmentoExiste = false;
                $('#segmento option').each(function() {
                    if ($(this).val() === segmento) {
                        segmentoExiste = true;
                        return false; // break
                    }
                });
                
                if (!segmentoExiste) {
                    console.log("Segmento não encontrado nas opções, adicionando manualmente:", segmento);
                    $('#segmento').append(new Option(segmento, segmento));
                }
                
                // Definir o valor do segmento
                $('#segmento').val(segmento);
                console.log("Segmento definido para:", segmento);
                
                // Forçar o evento change para garantir que os listeners sejam acionados
                $('#segmento').trigger('change');
                
                // Chamar a função global atualizarDominios diretamente
                if (typeof window.atualizarDominios === 'function') {
                    console.log("Chamando atualizarDominios diretamente com triggeredByUser=false");
                    window.atualizarDominios(false); // Passar false para indicar que não é uma ação do usuário
                    console.log("Domínios atualizados após definir segmento");
                    
                    // Aumentar o delay para garantir que os domínios foram atualizados
                    setTimeout(aplicarDominios, 1500);
                } else {
                    console.error("Função atualizarDominios não encontrada");
                    // Tentar aplicar domínios mesmo sem a função
                    setTimeout(aplicarDominios, 1000);
                }
            } else {
                console.log("Nenhum segmento para aplicar");
                // Tentar aplicar domínios mesmo sem segmento
                setTimeout(aplicarDominios, 1000);
            }
        }
        
        // Garantir que a flag applyingAiSuggestions esteja definida
        window.applyingAiSuggestions = true;
        console.log("Flag applyingAiSuggestions definida como TRUE");
        
        // Aplicar microárea
        if (microarea) {
            console.log("Aplicando microárea:", microarea);
            
            // Verificar se a microárea existe nas opções
            let microareaExiste = false;
            $('#microarea option').each(function() {
                if ($(this).val() === microarea) {
                    microareaExiste = true;
                    return false; // break
                }
            });
            
            if (!microareaExiste) {
                console.log("Microárea não encontrada nas opções, adicionando manualmente:", microarea);
                $('#microarea').append(new Option(microarea, microarea));
            }
            
            // Definir o valor da microárea
            $('#microarea').val(microarea);
            console.log("Microárea definida para:", microarea);
            
            // Forçar o evento change para garantir que os listeners sejam acionados
            $('#microarea').trigger('change');
            
            // Chamar a função global filtrarSegmentos diretamente
            if (typeof window.filtrarSegmentos === 'function') {
                console.log("Chamando filtrarSegmentos diretamente com triggeredByUser=false");
                window.filtrarSegmentos(false); // Passar false para indicar que não é uma ação do usuário
                console.log("Segmentos filtrados após definir microárea");
                
                // Aumentar o delay para garantir que os segmentos foram atualizados
                setTimeout(aplicarSegmento, 1500);
            } else {
                console.error("Função filtrarSegmentos não encontrada");
                // Tentar aplicar segmento mesmo sem a função
                setTimeout(aplicarSegmento, 1000);
            }
        } else {
            console.log("Nenhuma microárea para aplicar");
            // Tentar aplicar segmento mesmo sem microárea
            setTimeout(aplicarSegmento, 1000);
        }
    }
    
    /**
     * Função para inicializar o sistema de avaliação com estrelas
     * @param {string} type - O tipo de avaliação (aia ou tecverde)
     */
    function initRatingSystem(type) {
        const selector = type === 'tecverde' ? '[data-type="tecverde"]' : ':not([data-type])';
        const ratingInput = type === 'tecverde' ? '#tecverde-rating-value' : '#aia-rating-value';
        const ratingText = type === 'tecverde' ? '#tecverde-rating-text' : '#aia-rating-text';
        const saveButton = type === 'tecverde' ? '#saveTecverdeRatingBtn' : '#saveAiaRatingBtn';
        const observacoesInput = type === 'tecverde' ? '#tecverde-rating-observacoes' : '#aia-rating-observacoes';
        
        // Carregar avaliação existente
        const existingRating = parseInt($(ratingInput).val()) || 0;
        if (existingRating > 0) {
            updateStars(existingRating);
        }
        
        // Evento de clique nas estrelas
        $(`.rating-star${selector}`).on('click', function() {
            const value = parseInt($(this).data('value'));
            $(ratingInput).val(value);
            updateStars(value);
        });
        
        // Função para atualizar estrelas
        function updateStars(value) {
            $(`.rating-star${selector}`).removeClass('fas active').addClass('far');
            $(`.rating-star${selector}`).each(function() {
                if (parseInt($(this).data('value')) <= value) {
                    $(this).removeClass('far').addClass('fas active');
                }
            });
            
            // Atualizar texto com base no valor
            let ratingMessage = '';
            switch(value) {
                case 1: ratingMessage = 'Muito ruim'; break;
                case 2: ratingMessage = 'Ruim'; break;
                case 3: ratingMessage = 'Regular'; break;
                case 4: ratingMessage = 'Bom'; break;
                case 5: ratingMessage = 'Excelente'; break;
                default: ratingMessage = 'Selecione uma avaliação';
            }
            $(ratingText).text(ratingMessage);
        }
        
        // Evento de clique no botão salvar
        $(saveButton).on('click', function() {
            const rating = parseInt($(ratingInput).val());
            if (rating === 0) {
                // Mostrar alerta se nenhuma estrela for selecionada
                Swal.fire({
                    title: 'Avaliação necessária',
                    text: 'Por favor, selecione uma classificação (de 1 a 5 estrelas)',
                    icon: 'warning',
                    confirmButtonColor: '#3085d6',
                    confirmButtonText: 'OK'
                });
                return;
            }
            
            const observacoes = $(observacoesInput).val();
            const projectId = $('#project_id').val();
            
            // Preparar dados para envio
            const data = {
                project_id: projectId,
                rating: rating,
                observacoes: observacoes,
                tipo: type
            };
            
            // Enviar via AJAX
            $.ajax({
                url: `/save_ai_rating/${projectId}`,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(data),
                beforeSend: function() {
                    // Mostrar loading
                    $(saveButton).html('<i class="fas fa-spinner fa-spin me-1"></i>Salvando...');
                    $(saveButton).prop('disabled', true);
                },
                success: function(response) {
                    // Mostrar mensagem de sucesso
                    $(saveButton).html('<i class="fas fa-check-circle me-1"></i>Salvo!');
                    setTimeout(function() {
                        $(saveButton).html('<i class="fas fa-save me-1"></i>Salvar Avaliação');
                        $(saveButton).prop('disabled', false);
                    }, 2000);
                    
                    // Exibir notificação
                    Swal.fire({
                        title: 'Avaliação salva',
                        text: 'Sua avaliação foi registrada com sucesso',
                        icon: 'success',
                        timer: 2000,
                        timerProgressBar: true,
                        showConfirmButton: false
                    });
                    
                    console.log(`Avaliação ${type} salva com sucesso:`, response);
                },
                error: function(xhr, status, error) {
                    // Mostrar mensagem de erro
                    $(saveButton).html('<i class="fas fa-save me-1"></i>Salvar Avaliação');
                    $(saveButton).prop('disabled', false);
                    
                    Swal.fire({
                        title: 'Erro!',
                        text: xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Erro ao salvar avaliação',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                    
                    console.error(`Erro ao salvar avaliação ${type}:`, error);
                    console.error('Resposta do servidor:', xhr.responseText);
                }
            });
        });
    }
    
    // Inicializar sistemas de avaliação se estiverem disponíveis na página
    if ($('#aiSuggestionSection').length > 0) {
        initRatingSystem('aia');
    }

    // Sempre inicializar o sistema de avaliação para tecnologias verdes,
    // independentemente se a IA indicou "se aplica" ou não
    setTimeout(function() {
        if ($('#tecverde-rating-value').length > 0) {
            console.log("Inicializando sistema de avaliação para tecnologias verdes");
            initRatingSystem('tecverde');
            
            // Garantir que a seção de tecnologias verdes esteja visível se houver dados da IA
            if (typeof aiSuggestionData !== 'undefined' && aiSuggestionData) {
                if (aiSuggestionData.tecverde_justificativa || 
                    aiSuggestionData.tecverde_se_aplica || 
                    aiSuggestionData.tecverde_confianca) {
                    console.log("Forçando seção de tecnologias verdes da IA a ficar visível");
                    $('#aiTecverdeSuggestionSection').show();
                }
            }
        }
    }, 2000);
}

// Initialize when document is ready
$(document).ready(function() {
    // Check if we're on the categorize page
    if ($('#aiSuggestionSection').length > 0) {
        initAiSuggestions();
        
        // Inicializar o botão de justificativa de tecnologias verdes
        initJustificationButton();
        
        // Verificar estado do preenchimento após carregar a página
        $(window).on('load', function() {
            // Verificar se todos os campos foram preenchidos e esconder o overlay se necessário
            if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                // Esconder o overlay se estiver ativo por mais de 3 segundos (segurança)
                setTimeout(function() {
                    console.log("Verificação final: escondendo overlay de carregamento se ainda estiver visível");
                    if (typeof aiLoading !== 'undefined') {
                        aiLoading.forceCleanup();
                        
                        // Garantir que o localStorage também seja limpo
                        localStorage.removeItem('aiLoadingActive');
                        localStorage.removeItem('aiLoadingMessage');
                        localStorage.removeItem('aiLoadingSubmessage');
                    }
                }, 3000);
            }
        });
    } else {
        // Se não estamos na página de categorização, garantir que o overlay seja escondido
        if (typeof aiLoading !== 'undefined') {
            console.log('Não estamos na página de categorização, escondendo o overlay de carregamento');
            aiLoading.forceCleanup();
            
            // Garantir que o localStorage também seja limpo
            localStorage.removeItem('aiLoadingActive');
            localStorage.removeItem('aiLoadingMessage');
            localStorage.removeItem('aiLoadingSubmessage');
        }
    }
    
    // Adicionar funcionalidade de toggle para os cabeçalhos colapsáveis
    $('.collapse-icon').parent().on('click', function() {
        $(this).find('i').toggleClass('fa-chevron-up fa-chevron-down');
    });
});

/**
 * Função para inicializar os botões de exibição de justificativa
 */
function initJustificationButton() {
    // Botão de justificativa para área de aplicação
    $('#showJustificationBtn').off('click').on('click', function(e) {
        e.preventDefault(); // Prevenir comportamento padrão
        e.stopPropagation(); // Impedir propagação do evento
        
        console.log("Botão 'Ver Classificação' clicado (Área de Aplicação)");
        $('#justificationBox').slideToggle();
        
        // Alterar o texto do botão entre "Ver Classificação" e "Ocultar Classificação"
        var btnText = $(this).find('span');
        if (btnText.text() === 'Ver Classificação') {
            btnText.text('Ocultar Classificação');
        } else {
            btnText.text('Ver Classificação');
        }
    });
    
    // Garantir que o botão para tecnologias verdes também funcione
    $('#showTecverdeJustificationBtn').off('click').on('click', function(e) {
        e.preventDefault(); // Prevenir comportamento padrão
        e.stopPropagation(); // Impedir propagação do evento
        
        console.log("Botão 'Ver Classificação' clicado (Tecnologias Verdes)");
        $('#tecverdeJustificationBox').slideToggle();
        
        // Alterar o texto do botão entre "Ver Classificação" e "Ocultar Classificação"
        var btnText = $(this).find('span');
        if (btnText.text() === 'Ver Classificação') {
            btnText.text('Ocultar Classificação');
        } else {
            btnText.text('Ver Classificação');
        }
    });
    
    console.log("Botões de justificativa inicializados");
}
