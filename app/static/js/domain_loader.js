/**
 * Domain Loader Script
 * This script handles loading domain options for the categorize.html page
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Domain Loader script initialized");
    
    // Function to load domains based on microarea and segmento
    function loadDomains() {
        var microarea = $('#microarea').val();
        var segmento = $('#segmento').val();
        
        console.log("Loading domains for microarea:", microarea, "and segmento:", segmento);
        
        if (!microarea || !segmento) {
            console.log("Microarea or segmento not selected, skipping domain loading");
            return;
        }
        
        // Get the domain data from the global variable
        var dominiosPorMicroareaSegmento = window.dominiosPorMicroareaSegmento;
        
        if (!dominiosPorMicroareaSegmento) {
            console.error("Domain data not available!");
            return;
        }
        
        // Check if we have data for the selected microarea
        if (!dominiosPorMicroareaSegmento[microarea]) {
            console.error("No data found for microarea:", microarea);
            return;
        }
        
        // Check if we have data for the selected segmento
        if (!dominiosPorMicroareaSegmento[microarea][segmento]) {
            console.error("No data found for segmento:", segmento, "in microarea:", microarea);
            return;
        }
        
        // Get the domains for the selected microarea and segmento
        var dominiosDoSegmentoAtual = dominiosPorMicroareaSegmento[microarea][segmento];
        console.log("Domains for selected segmento:", dominiosDoSegmentoAtual);
        
        // Get domains from other segmentos in the same microarea
        var dominiosDeOutrosSegmentos = [];
        for (var outroSegmento in dominiosPorMicroareaSegmento[microarea]) {
            if (outroSegmento !== segmento) {
                var dominiosOutroSegmento = dominiosPorMicroareaSegmento[microarea][outroSegmento];
                if (Array.isArray(dominiosOutroSegmento)) {
                    dominiosDeOutrosSegmentos = dominiosDeOutrosSegmentos.concat(dominiosOutroSegmento);
                }
            }
        }
        console.log("Domains from other segmentos:", dominiosDeOutrosSegmentos);
        
        // Clear existing options
        $('#dominio').empty();
        $('#dominio_outros').empty();
        
        // Add domains to the selects
        if (Array.isArray(dominiosDoSegmentoAtual)) {
            dominiosDoSegmentoAtual.forEach(function(dominio) {
                $('#dominio').append(new Option(dominio, dominio));
            });
        }
        
        if (Array.isArray(dominiosDeOutrosSegmentos)) {
            dominiosDeOutrosSegmentos.forEach(function(dominio) {
                $('#dominio_outros').append(new Option(dominio, dominio));
            });
        }
        
        // Initialize Choices.js
        initializeChoices();
    }
    
    // Function to initialize Choices.js
    function initializeChoices() {
        // Destroy existing instances if they exist
        if (window.dominioChoices) {
            window.dominioChoices.destroy();
        }
        if (window.dominioOutrosChoices) {
            window.dominioOutrosChoices.destroy();
        }
        
        // Initialize Choices.js for dominio select
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
        
        // Initialize Choices.js for dominio_outros select
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
        
        console.log("Choices.js initialized for domain selects");
    }
    
    // Add event listeners to microarea and segmento selects
    $('#microarea').change(function() {
        // Clear segmento select
        $('#segmento').empty();
        $('#segmento').append(new Option('Selecione...', ''));
        
        var microarea = $(this).val();
        if (!microarea) return;
        
        var dominiosPorMicroareaSegmento = window.dominiosPorMicroareaSegmento;
        if (!dominiosPorMicroareaSegmento || !dominiosPorMicroareaSegmento[microarea]) return;
        
        // Add segmentos for the selected microarea
        for (var segmento in dominiosPorMicroareaSegmento[microarea]) {
            $('#segmento').append(new Option(segmento, segmento));
        }
    });
    
    $('#segmento').change(loadDomains);
    
    // Initial load if microarea and segmento are already selected
    if ($('#microarea').val() && $('#segmento').val()) {
        loadDomains();
    }
});
