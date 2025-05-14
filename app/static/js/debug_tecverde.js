/**
 * This file is kept for compatibility purposes only.
 * The actual functionality has been moved to ai_suggestions.js
 * and now runs automatically without requiring a button click.
 */

// Expose the fixClasseAndSubclasse function globally for compatibility
window.fixClasseAndSubclasse = function fixClasseAndSubclasse() {
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
                
                console.log(`Subclasse set to '${subclasse}'`);
            }
        }, 500);
    }
};
