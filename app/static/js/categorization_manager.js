/**
 * Gerenciador centralizado para decisões de categorização
 * Determina se devem ser usados dados existentes ou sugestões da IA
 */
function verificarDadosCategorizacao() {
    console.log("Verificando dados de categorização...");
    
    // Objeto para armazenar as decisões
    const categorizacaoConfig = {
        // Área de interesse
        areaInteresse: {
            usarDadosExistentes: false,
            dadosExistentes: {},
            usarIa: false,
            dadosIa: {}
        },
        // Tecnologias verdes
        tecVerde: {
            usarDadosExistentes: false,
            dadosExistentes: {},
            usarIa: false,
            dadosIa: {}
        }
    };

    // 1. Verificar dados existentes para área de interesse
    const existingMicroarea = $("#microarea").val() || "";
    const existingSegmento = $("#segmento").val() || "";
    const existingDominio = $("#dominio").val() || "";
    const existingDominioOutros = $("#dominio_outros").val() || "";
    const hasExistingDataTag = $("#microarea").data("has-existing") === true;
    const isUserModified = $("#user_modified").val() === "true";

    // 2. Verificar dados existentes para tecnologias verdes
    const existingTecverdeSePlica = $("#tecverde_se_aplica").val() || "";
    const existingTecverdeClasse = $("#tecverde_classe").val() || "";
    const existingTecverdeSubclasse = $("#tecverde_subclasse").val() || "";
    const hasTecVerdeDataTag = $("#tecverde_se_aplica").data("has-existing") === true;

    // 3. Regra unificada para determinar se há dados existentes para área de interesse
    const hasExistingAreaInteresse = hasExistingDataTag || 
                                   (existingMicroarea && isUserModified) || 
                                   (existingMicroarea && existingSegmento);

    // 4. Regra unificada para determinar se há dados existentes para tecnologias verdes
    const hasExistingTecverde = hasTecVerdeDataTag || 
                              (existingTecverdeSePlica && isUserModified) || 
                              (existingTecverdeSePlica && existingTecverdeClasse);

    // 5. Verificar se há sugestões da IA disponíveis
    const hasAiSuggestions = typeof aiSuggestionData !== 'undefined' && aiSuggestionData;

    // 6. Configurar resultados para área de interesse
    categorizacaoConfig.areaInteresse.usarDadosExistentes = hasExistingAreaInteresse;
    categorizacaoConfig.areaInteresse.dadosExistentes = {
        microarea: existingMicroarea,
        segmento: existingSegmento,
        dominio: existingDominio,
        dominio_outros: existingDominioOutros
    };
    categorizacaoConfig.areaInteresse.usarIa = !hasExistingAreaInteresse && hasAiSuggestions;
    
    // 7. Configurar resultados para tecnologias verdes
    categorizacaoConfig.tecVerde.usarDadosExistentes = hasExistingTecverde;
    categorizacaoConfig.tecVerde.dadosExistentes = {
        se_aplica: existingTecverdeSePlica,
        classe: existingTecverdeClasse,
        subclasse: existingTecverdeSubclasse
    };
    categorizacaoConfig.tecVerde.usarIa = !hasExistingTecverde && hasAiSuggestions;

    // 8. Armazenar dados da IA quando disponíveis
    if (hasAiSuggestions) {
        categorizacaoConfig.areaInteresse.dadosIa = {
            microarea: aiSuggestionData._aia_n1_macroarea || "",
            segmento: aiSuggestionData._aia_n2_segmento || "",
            dominio: aiSuggestionData._aia_n3_dominio_afeito || "",
            dominio_outros: aiSuggestionData._aia_n3_dominio_outro || ""
        };
        
        categorizacaoConfig.tecVerde.dadosIa = {
            se_aplica: aiSuggestionData.tecverde_se_aplica || "",
            classe: aiSuggestionData.tecverde_classe || "",
            subclasse: aiSuggestionData.tecverde_subclasse || ""
        };
    }

    // 9. Registrar decisões no console para depuração
    console.log("Configuração de categorização determinada:", {
        areaInteresse: {
            usarDadosExistentes: categorizacaoConfig.areaInteresse.usarDadosExistentes,
            usarIa: categorizacaoConfig.areaInteresse.usarIa
        },
        tecVerde: {
            usarDadosExistentes: categorizacaoConfig.tecVerde.usarDadosExistentes,
            usarIa: categorizacaoConfig.tecVerde.usarIa
        }
    });

    // 10. Expor globalmente para acesso por outros scripts
    window.categorizacaoConfig = categorizacaoConfig;
    
    return categorizacaoConfig;
}

// Executar assim que o documento estiver pronto
$(document).ready(function() {
    // Verificar com pequeno delay para garantir que todos elementos estão carregados
    setTimeout(verificarDadosCategorizacao, 100);
});
