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
            if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                aiLoading.completeProgress();
            }
        }
    } catch (error) {
        console.error("Erro ao processar dados da IA:", error);
        
        // Esconder o overlay de carregamento em caso de erro
        if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
            aiLoading.completeProgress();
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
            // Garantir que tecverde_se_aplica seja tratado corretamente
            // Converter para um formato consistente (string "1" ou "0")
            if (data.tecverde_se_aplica === true || 
                data.tecverde_se_aplica === "true" || 
                data.tecverde_se_aplica === 1 || 
                data.tecverde_se_aplica === "1" ||
                data.tecverde_se_aplica === "Sim" || 
                data.tecverde_se_aplica === "sim") {
                data.tecverde_se_aplica = "1";
            } else {
                data.tecverde_se_aplica = "0";
            }
            
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
        // Atualizar se aplica - converter valor para texto de forma consistente
        let seAplica = 0;
        console.log("Verificando valor de tecverde_se_aplica:", data.tecverde_se_aplica, "tipo:", typeof data.tecverde_se_aplica);
        
        if (data.tecverde_se_aplica === "1" || data.tecverde_se_aplica === 1 || 
            data.tecverde_se_aplica === true || data.tecverde_se_aplica === "true" || 
            data.tecverde_se_aplica === "Sim" || data.tecverde_se_aplica === "sim") {
            seAplica = 1;
            console.log("Valor convertido para seAplica = 1 (Sim/true)");
        } else {
            console.log("Valor mantido como seAplica = 0 (Não/false)");
        }
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
            
            // Garantir que o campo de observações esteja habilitado
            $('#tecverde_observacoes').prop('disabled', false);
            
            // Verificar se o campo de observações está vazio ou se estamos forçando a aplicação
            const observacoesAtuais = $('#tecverde_observacoes').val();
            
            if (force || !observacoesAtuais || observacoesAtuais.trim() === '') {
                console.log("Inserindo justificativa da IA no campo de observações...");
                
                // Formatar a justificativa de acordo com o valor de "se aplica"
                let textoJustificativa = justificativa;
                if (seAplica === "Não" || seAplica === "Nao" || seAplica === 0 || seAplica === "0" || 
                    seAplica === false || seAplica === "false") {
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
            if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                aiLoading.completeProgress();
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
        
        // Verificar se o usuário já salvou categorias manualmente
        // Isso é indicado pela variável 'existing' que é passada para o template
        const hasExistingAreaInteresse = $('#microarea').data('has-existing') === true || 
                                        (currentMicroarea && $('#user_modified').val() === 'true');
        
        const hasExistingTecverde = $('#tecverde_se_aplica').data('has-existing') === true || 
                                   (currentTecverdeSePlica && $('#user_modified').val() === 'true');
        
        console.log("Verificação de dados existentes:", {
            hasExistingAreaInteresse: hasExistingAreaInteresse,
            hasExistingTecverde: hasExistingTecverde,
            userModified: $('#user_modified').val()
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
                if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                    aiLoading.completeProgress();
                }
            }
        }
        
        // Aplicar sugestões para classificação por área de interesse
        // Nova lógica: Aplicar apenas se o usuário NÃO tiver salvo categorias manualmente
        if (!hasExistingAreaInteresse) {
            console.log("Usuário não salvou categorias manualmente, aplicando sugestões da IA para área de interesse");
            applyAiaClassification(data, checkCompletion);
        } else {
            console.log("Usuário já salvou categorias manualmente, mantendo os valores existentes para área de interesse");
            checkCompletion(); // Marcar como concluído mesmo se não aplicar
        }
        
        // Aplicar sugestões para tecnologias verdes
        // Nova lógica: Aplicar apenas se o usuário NÃO tiver salvo tecnologias verdes manualmente
        if (!hasExistingTecverde && (data.tecverde_classe || data.tecverde_subclasse || data.tecverde_se_aplica)) {
            console.log("Usuário não salvou tecnologias verdes manualmente, aplicando sugestões da IA");
            
            // Garantir que tecverde_se_aplica seja tratado corretamente
            // Converter para um formato consistente (string "1" ou "0")
            if (data.tecverde_se_aplica === true || 
                data.tecverde_se_aplica === "true" || 
                data.tecverde_se_aplica === 1 || 
                data.tecverde_se_aplica === "1" ||
                data.tecverde_se_aplica === "Sim" || 
                data.tecverde_se_aplica === "sim") {
                data.tecverde_se_aplica = "1";
            } else {
                data.tecverde_se_aplica = "0";
            }
            
            applyTecverdeClassification(data, checkCompletion);
        } else {
            console.log("Usuário já salvou tecnologias verdes manualmente ou não há sugestões, mantendo os valores existentes");
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
                    
                    // Agora tentar definir via jQuery com o valor false
                    $('#tecverde_se_aplica').val("false");
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
        console.log("Aplicando sugestões de tecnologias verdes via fixTecverdeSeAplica");
        
        // Usar a função fixTecverdeSeAplica para aplicar as sugestões
        // Esta função já contém toda a lógica necessária para corrigir os campos
        fixTecverdeSeAplica();
        
        // Aplicar justificativa se disponível
        if (data.tecverde_justificativa) {
            setTimeout(() => {
                applyTecverdeJustification(data);
            }, 800);
        }
        
        // Completar a operação após um delay para garantir que tudo foi aplicado
        setTimeout(() => {
            if (typeof callback === 'function') callback();
        }, 1500);
    }
    
    /**
     * Função para corrigir os campos de classe e subclasse
     * Adaptada do debug_tecverde.js
     */
function fixClasseAndSubclasse() {
    console.log("Fixing classe and subclasse fields...");
    
    // Check if we're on the categorize page
    if (!document.getElementById('tecverde_classe') || !document.getElementById('tecverde_subclasse')) {
        console.log("Not on categorize page or classe/subclasse fields not found");
        return;
    }
    
    // Check if AI suggestion data is available
    if (typeof aiSuggestionData === 'undefined') {
        console.log("AI Suggestion Data not available, cannot fix");
        return;
    }
    
    const classe = aiSuggestionData.tecverde_classe;
    const subclasse = aiSuggestionData.tecverde_subclasse;
    
    console.log("Fixing with AI Values:", { classe, subclasse });
    
    // Make sure the fields are enabled
    $('#tecverde_classe, #tecverde_subclasse').prop('disabled', false);
    $('#tecverde_classe, #tecverde_subclasse').removeClass('bg-light');
    
    // Fix classe field
    if (classe) {
        const classeElement = document.getElementById('tecverde_classe');
        
        // Check if the classe exists in the options
        let classeExists = false;
        let classeIndex = -1;
        
        for (let i = 0; i < classeElement.options.length; i++) {
            if (classeElement.options[i].value === classe) {
                classeExists = true;
                classeIndex = i;
                break;
            }
        }
        
        if (!classeExists) {
            console.log(`Classe '${classe}' not found in options. Adding it.`);
            const newOption = new Option(classe, classe);
            classeElement.add(newOption);
            classeIndex = classeElement.options.length - 1;
        }
        
        // Set the value
        classeElement.selectedIndex = classeIndex;
        classeElement.value = classe;
        
        // Trigger change event to update subclasse options
        const event = new Event('change', { bubbles: true });
        classeElement.dispatchEvent(event);
        
        // Also trigger jQuery change event for compatibility
        $(classeElement).trigger('change');
        
        console.log(`Classe set to '${classe}'`);
        
        // Wait for subclasse options to update
        setTimeout(() => {
            // Fix subclasse field
            if (subclasse) {
                const subclasseElement = document.getElementById('tecverde_subclasse');
                
                // Check if the subclasse exists in the options
                let subclasseExists = false;
                let subclasseIndex = -1;
                
                for (let i = 0; i < subclasseElement.options.length; i++) {
                    if (subclasseElement.options[i].value === subclasse) {
                        subclasseExists = true;
                        subclasseIndex = i;
                        break;
                    }
                }
                
                if (!subclasseExists) {
                    console.log(`Subclasse '${subclasse}' not found in options. Adding it.`);
                    const newOption = new Option(subclasse, subclasse);
                    subclasseElement.add(newOption);
                    subclasseIndex = subclasseElement.options.length - 1;
                }
                
                // Set the value
                subclasseElement.selectedIndex = subclasseIndex;
                subclasseElement.value = subclasse;
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                subclasseElement.dispatchEvent(event);
                
                // Also trigger jQuery change event for compatibility
                $(subclasseElement).trigger('change');
                
                console.log(`Subclasse set to '${subclasse}'`);
            }
        }, 500);
    }
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
        
        // Aplicar as sugestões com um delay mínimo
        setTimeout(() => {
            console.log("Iniciando aplicação das sugestões");
            
            // Garantir que a flag applyingAiSuggestions esteja definida
            window.applyingAiSuggestions = true;
            console.log("Flag applyingAiSuggestions definida como TRUE");
            
            // Aplicar microárea com highlight visual temporário
            if (microarea) {
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
                    setTimeout(() => {
                        // Aplicar segmento e atualizar domínios
                        if (segmento) {
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
                                setTimeout(() => {
                                    // Aplicar domínios
                                    if (dominio) {
                                        let dominioValues = [];
                                        if (typeof dominio === 'string' && dominio.includes(';')) {
                                            dominioValues = dominio.split(';').map(d => d.trim());
                                        } else if (Array.isArray(dominio)) {
                                            dominioValues = dominio;
                                        } else {
                                            dominioValues = [dominio];
                                        }
                                        
                                        console.log("Definindo domínios:", dominioValues);
                                        
                                        // Verificar se há opções disponíveis no select
                                        const hasOptions = $('#dominio option').length > 0;
                                        
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
                                                // Usar a API do Choices.js para definir os valores
                                                window.dominioChoices.setChoiceByValue(dominioValues);
                                                console.log("Domínios definidos via Choices.js");
                                            } catch (e) {
                                                console.error("Erro ao definir domínios via Choices.js:", e);
                                                // Fallback para o método tradicional
                                                $('#dominio').val(dominioValues);
                                                $('#dominio').trigger('change');
                                            }
                                        } else {
                                            // Fallback para o método tradicional
                                            $('#dominio').val(dominioValues);
                                            // Forçar o evento change para garantir que os listeners sejam acionados
                                            $('#dominio').trigger('change');
                                            console.log("Domínios definidos via jQuery");
                                        }
                                    }
                                    
                                    // Aplicar domínios outros
                                    if (dominio_outros) {
                                        // Tratar valores N/A ou vazios
                                        if (dominio_outros === 'N/A' || dominio_outros === '') {
                                            console.log("Domínios afeitos outros está vazio ou marcado como N/A. Definindo como vazio no formulário.");
                                            // Limpar o campo de domínios outros
                                            $('#dominio_outros').val([]);
                                            
                                            // Atualizar o select2 para refletir as mudanças
                                            if ($('#dominio_outros').hasClass('searchable-select')) {
                                                $('#dominio_outros').trigger('change');
                                            } else {
                                                // Forçar o evento change para garantir que os listeners sejam acionados
                                                $('#dominio_outros').trigger('change');
                                            }
                                            
                                            // Adicionar um atributo de dados para indicar que foi definido como N/A
                                            $('#dominio_outros').attr('data-na', 'true');
                                        } else {
                                            let dominioOutrosValues = [];
                                            if (typeof dominio_outros === 'string' && dominio_outros.includes(';')) {
                                                dominioOutrosValues = dominio_outros.split(';').map(d => d.trim());
                                            } else if (Array.isArray(dominio_outros)) {
                                                dominioOutrosValues = dominio_outros;
                                            } else {
                                                dominioOutrosValues = [dominio_outros];
                                            }
                                        
                                            console.log("Preparando para definir domínios afeitos outros:", dominioOutrosValues);
                                            
                                            // Verificar se há opções disponíveis no select
                                            const hasOptions = $('#dominio_outros option').length > 0;
                                            
                                            // Forçar a adição dos valores como options se não existirem
                                            if (!hasOptions && dominioOutrosValues.length > 0) {
                                                console.log("Não há opções no select de domínios outros, adicionando os valores manualmente");
                                                dominioOutrosValues.forEach(value => {
                                                    $('#dominio_outros').append(new Option(value, value));
                                                });
                                                console.log(`Adicionadas ${dominioOutrosValues.length} opções ao select de domínios outros`);
                                            }
                                            
                                            // Aplicar diretamente os valores no select
                                            if (window.dominioOutrosChoices) {
                                                try {
                                                    // Usar a API do Choices.js para definir os valores
                                                    window.dominioOutrosChoices.setChoiceByValue(dominioOutrosValues);
                                                    console.log("Domínios outros definidos via Choices.js");
                                                } catch (e) {
                                                    console.error("Erro ao definir domínios outros via Choices.js:", e);
                                                    // Fallback para o método tradicional
                                                    $('#dominio_outros').val(dominioOutrosValues);
                                                    $('#dominio_outros').trigger('change');
                                                }
                                            } else {
                                                // Fallback para o método tradicional
                                                $('#dominio_outros').val(dominioOutrosValues);
                                                
                                                // Atualizar o select2 para refletir as mudanças
                                                if ($('#dominio_outros').hasClass('searchable-select')) {
                                                    $('#dominio_outros').trigger('change');
                                                } else {
                                                    // Forçar o evento change para garantir que os listeners sejam acionados
                                                    $('#dominio_outros').trigger('change');
                                                }
                                                console.log("Domínios outros definidos via jQuery");
                                            }
                                        }
                                    }
                                    
                                    // Completar a operação
                                    if (typeof callback === 'function') callback();
                                    
                                }, 1200); // Aumentado de 800ms para 1200ms
                            } else {
                                console.error("Função atualizarDominios não encontrada");
                                // Completar a operação mesmo se houver erro
                                if (typeof callback === 'function') callback();
                            }
                        }
                    }, 1000); // Aumentado de 800ms para 1000ms
                } else {
                    console.error("Função filtrarSegmentos não encontrada");
                    // Completar a operação mesmo se houver erro
                    if (typeof callback === 'function') callback();
                }
            } else {
                console.log("Nenhuma microárea para aplicar");
                // Completar a operação se não houver microárea
                if (typeof callback === 'function') callback();
            }
        }, 300); // Reduzido de 1000ms para 300ms
    }
    
    /**
     * Função para inicializar o sistema de avaliação com estrelas
     * @param {string} type - O tipo de avaliação (aia ou tecverde)
     */
    function initRatingSystem(type) {
        const selector = type === 'tecverde' ? '[data-type="tecverde"]' : ':not([data-type])';
        const ratingInput = type === 'tecverde' ? '#tecverde-rating-value' : '#aia-rating-value';
        const ratingText = type === 'tecverde' ? '#tecverde-rating-text' : '#aia-rating-text';
        // Removemos a referência ao botão de salvar, pois o evento será gerenciado pelo save_all.js
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
        
        // Removido o evento de clique no botão salvar para evitar duplicação
        // O evento agora é gerenciado exclusivamente pelo arquivo save_all.js
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
                    aiLoading.completeProgress();
                }, 3000);
            }
            
            // Verificar e corrigir os campos de tecnologias verdes
            setTimeout(function() {
                verificarECorrigirCamposTecverdes();
            }, 2000);
        });
        
        // Função para verificar e corrigir os campos de tecnologias verdes
        function verificarECorrigirCamposTecverdes() {
            console.log("Verificando e corrigindo campos de tecnologias verdes...");
            
            // Verificar se temos dados de sugestão da IA
            if (typeof aiSuggestionData !== 'undefined' && aiSuggestionData) {
                // Garantir que tecverde_se_aplica seja tratado corretamente
                if (aiSuggestionData.tecverde_se_aplica === "1" || aiSuggestionData.tecverde_se_aplica === 1) {
                    aiSuggestionData.tecverde_se_aplica = true;
                } else if (aiSuggestionData.tecverde_se_aplica === "0" || aiSuggestionData.tecverde_se_aplica === 0) {
                    aiSuggestionData.tecverde_se_aplica = false;
                }
                
                const seAplica = aiSuggestionData.tecverde_se_aplica;
                const classe = aiSuggestionData.tecverde_classe;
                const subclasse = aiSuggestionData.tecverde_subclasse;
                
                console.log("Dados de tecnologias verdes da IA:", {
                    seAplica, classe, subclasse
                });
                
                // Verificar se os campos estão preenchidos corretamente
                const currentSeAplica = $('#tecverde_se_aplica').val();
                const currentClasse = $('#tecverde_classe').val();
                const currentSubclasse = $('#tecverde_subclasse').val();
                
                console.log("Valores atuais nos campos:", {
                    seAplica: currentSeAplica,
                    classe: currentClasse,
                    subclasse: currentSubclasse
                });
                
                // Se os campos não estiverem preenchidos corretamente, tentar corrigir
                if (seAplica && !currentSeAplica) {
                    console.log("Campo 'Se aplica' não está preenchido corretamente. Tentando corrigir...");
                    
                    // Garantir que o campo esteja habilitado
                    $('#tecverde_se_aplica').prop('disabled', false);
                    
                    // Definir o valor
                    if (seAplica === "1" || seAplica === 1 || seAplica === true || seAplica === "true" || 
                        seAplica === "Sim" || seAplica === "sim") {
                        $('#tecverde_se_aplica').val("true");
                    } else {
                        $('#tecverde_se_aplica').val("false");
                    }
                    
                    // Disparar evento de mudança
                    $('#tecverde_se_aplica').trigger('change');
                }
                
                // Se o campo "Se aplica" for "Sim" e os campos de classe e subclasse não estiverem preenchidos
                if ((seAplica === "1" || seAplica === 1 || seAplica === true || seAplica === "true" || seAplica === "Sim") && 
                    (classe && !currentClasse || subclasse && !currentSubclasse)) {
                    
                    console.log("Campos de classe ou subclasse não estão preenchidos corretamente. Tentando corrigir...");
                    
                    // Garantir que os campos estejam habilitados
                    $('#tecverde_classe, #tecverde_subclasse').prop('disabled', false);
                    
                    // Definir os valores
                    if (classe && !currentClasse) {
                        $('#tecverde_classe').val(classe);
                        $('#tecverde_classe').trigger('change');
                    }
                    
                    // Aguardar um pouco para definir a subclasse
                    setTimeout(function() {
                        if (subclasse && !currentSubclasse) {
                            $('#tecverde_subclasse').val(subclasse);
                            $('#tecverde_subclasse').trigger('change');
                        }
                    }, 500);
                }
                
                // Garantir que o campo de observações esteja preenchido
                if (aiSuggestionData.tecverde_justificativa) {
                    applyTecverdeJustification(aiSuggestionData, true);
                }
            }
        }
    } else {
        // Se não estamos na página de categorização, garantir que o overlay seja escondido
        if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
            console.log('Não estamos na página de categorização, escondendo o overlay de carregamento');
            aiLoading.completeProgress();
        }
    }
    
    // Adicionar funcionalidade de toggle para os cabeçalhos colapsáveis
    $('.collapse-icon').parent().on('click', function() {
        $(this).find('i').toggleClass('fa-chevron-up fa-chevron-down');
    });
});

/**
 * Function to fix the tecverde_se_aplica field
 * Adapted from debug_tecverde.js
 */
function fixTecverdeSeAplica() {
    console.log("Attempting to fix tecverde_se_aplica field...");
    
    // Check if we're on the categorize page
    if (!document.getElementById('tecverde_se_aplica')) {
        console.log("Not on categorize page or tecverde_se_aplica field not found");
        return;
    }
    
    // Check if AI suggestion data is available
    if (typeof aiSuggestionData === 'undefined') {
        console.log("AI Suggestion Data not available, cannot fix");
        return;
    }
    
    const aiValue = aiSuggestionData.tecverde_se_aplica;
    const selectElement = document.getElementById('tecverde_se_aplica');
    
    console.log("Fixing with AI Value:", aiValue, "Type:", typeof aiValue);
    
    // Determine the correct index to select
    let targetIndex = -1;
    
    // Handle boolean values directly
    if (aiValue === true) {
        console.log("Boolean TRUE detected, selecting 'Sim'");
        // Find the "Sim" option (usually index 1)
        for (let i = 0; i < selectElement.options.length; i++) {
            if (selectElement.options[i].text === "Sim") {
                targetIndex = i;
                break;
            }
        }
        
        // If not found by text, try index 1
        if (targetIndex === -1 && selectElement.options.length > 1) {
            targetIndex = 1;
        }
    } else if (aiValue === false) {
        console.log("Boolean FALSE detected, selecting 'Não'");
        // Find the "Não" option (usually index 2)
        for (let i = 0; i < selectElement.options.length; i++) {
            if (selectElement.options[i].text === "Não") {
                targetIndex = i;
                break;
            }
        }
        
        // If not found by text, try index 2
        if (targetIndex === -1 && selectElement.options.length > 2) {
            targetIndex = 2;
        }
    } 
    // Handle string and number values as before
    else if (aiValue === "true" || aiValue === 1 || aiValue === "1" || aiValue === "Sim" || aiValue === "sim") {
        // Find the "Sim" option (usually index 1)
        for (let i = 0; i < selectElement.options.length; i++) {
            if (selectElement.options[i].text === "Sim") {
                targetIndex = i;
                break;
            }
        }
        
        // If not found by text, try index 1
        if (targetIndex === -1 && selectElement.options.length > 1) {
            targetIndex = 1;
        }
    } else if (aiValue === "false" || aiValue === 0 || aiValue === "0" || aiValue === "Não" || aiValue === "Nao" || aiValue === "não" || aiValue === "nao") {
        // Find the "Não" option (usually index 2)
        for (let i = 0; i < selectElement.options.length; i++) {
            if (selectElement.options[i].text === "Não") {
                targetIndex = i;
                break;
            }
        }
        
        // If not found by text, try index 2
        if (targetIndex === -1 && selectElement.options.length > 2) {
            targetIndex = 2;
        }
    }
    
    if (targetIndex !== -1) {
        console.log(`Setting select to index ${targetIndex} (${selectElement.options[targetIndex].text})`);
        
        // Set the selected index
        selectElement.selectedIndex = targetIndex;
        
        // Also set the value directly
        const newValue = selectElement.options[targetIndex].value;
        selectElement.value = newValue;
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        selectElement.dispatchEvent(event);
        
        // Also trigger jQuery change event for compatibility
        $(selectElement).trigger('change');
        
        console.log("Fix applied, new value:", selectElement.value);
        
        // If "Sim" was selected, also fix classe and subclasse
        if (targetIndex === 1 || selectElement.options[targetIndex].text === "Sim") {
            setTimeout(fixClasseAndSubclasse, 500);
        } else {
            // If "Não" was selected, ensure classe and subclasse are disabled and empty
            setTimeout(function() {
                $('#tecverde_classe, #tecverde_subclasse').prop('disabled', true).val('').addClass('bg-light');
                console.log("Disabled and cleared classe and subclasse fields for 'Não' option");
            }, 500);
        }
        
        // Call verificarTecverdeSePlica to ensure proper state
        setTimeout(function() {
            if (typeof window.verificarTecverdeSePlica === 'function') {
                window.verificarTecverdeSePlica();
                console.log("Called verificarTecverdeSePlica to ensure proper state");
            }
        }, 600);
    } else {
        console.log("Could not determine the correct option to select");
    }
}

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
