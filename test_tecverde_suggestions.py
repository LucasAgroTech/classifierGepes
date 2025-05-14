#!/usr/bin/env python3
"""
Script para testar as sugestões de tecnologias verdes da IA.
Este script gera uma página HTML simples que simula a página de categorização
e testa a funcionalidade de tecnologias verdes.
"""

import os
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

# Diretório atual
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# HTML para o teste
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teste de Sugestões de Tecnologias Verdes</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        h2 {
            margin-top: 20px;
            color: #444;
        }
        select, input {
            padding: 8px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        label {
            display: block;
            margin-top: 10px;
            font-weight: bold;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
            margin-right: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        #resultados {
            margin-top: 20px;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 4px;
            background-color: #f9f9f9;
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
        }
        .log {
            margin: 5px 0;
            font-family: monospace;
        }
        .timestamp {
            color: #888;
            font-size: 0.8em;
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <h1>Teste de Sugestões de Tecnologias Verdes</h1>
    
    <h2>Tecnologias Verdes</h2>
    <div>
        <label for="tecverde_se_aplica">Se Aplica:</label>
        <select id="tecverde_se_aplica">
            <option value="">Selecione...</option>
            <option value="1">Sim</option>
            <option value="0">Não</option>
        </select>
        
        <label for="tecverde_classe">Classe:</label>
        <select id="tecverde_classe">
            <option value="">Selecione...</option>
            <option value="Eficiência Energética">Eficiência Energética</option>
            <option value="Energias alternativas">Energias alternativas</option>
            <option value="Gestão Ambiental">Gestão Ambiental</option>
            <option value="Transporte">Transporte</option>
            <option value="Conservação">Conservação</option>
        </select>
        
        <label for="tecverde_subclasse">Subclasse:</label>
        <select id="tecverde_subclasse">
            <option value="">Selecione...</option>
        </select>
    </div>
    
    <h2>Dados da IA</h2>
    <div id="ai-data">
        <pre id="ai-data-json">{"tecverde_se_aplica": "1", "tecverde_classe": "Eficiência Energética", "tecverde_subclasse": "Iluminação LED"}</pre>
    </div>
    
    <div>
        <button id="test-sim">Testar com "Sim"</button>
        <button id="test-nao">Testar com "Não"</button>
    </div>
    
    <h2>Resultados do Teste</h2>
    <div id="resultados"></div>
    
    <script>
        // Variável global para armazenar os dados da IA
        var aiSuggestionData = {
            "tecverde_se_aplica": "1",
            "tecverde_classe": "Eficiência Energética",
            "tecverde_subclasse": "Iluminação LED"
        };
        
        // Função para adicionar log
        function addLog(message) {
            const now = new Date();
            const timestamp = `[${now.getHours()}:${now.getMinutes()}:${now.getSeconds()} ${now.getHours() >= 12 ? 'PM' : 'AM'}]`;
            $('#resultados').append(`<div class="log"><span class="timestamp">${timestamp}</span> ${message}</div>`);
            // Scroll para o final
            $('#resultados').scrollTop($('#resultados')[0].scrollHeight);
        }
        
        // Função para verificar se tecnologia verde se aplica
        function verificarTecverdeSePlica() {
            var seAplica = $('#tecverde_se_aplica').val();
            var seAplicaText = $('#tecverde_se_aplica option:selected').text();
            
            addLog("Verificando se tecnologia verde se aplica: " + JSON.stringify({
                valor: seAplica,
                texto: seAplicaText
            }));
            
            // Verificar se é "Não" pelo valor ou pelo texto
            if (seAplica === "0" || seAplicaText === "Não") {
                addLog("APLICANDO NÃO: Desabilitando campos de tecnologias verdes");
                // Desabilitar campos de classe e subclasse
                $('#tecverde_classe, #tecverde_subclasse').prop('disabled', true);
                // Limpar valores dos campos
                $('#tecverde_classe, #tecverde_subclasse').val('');
            } else if (seAplica === "1" || seAplicaText === "Sim") {
                addLog("APLICANDO SIM: Habilitando campos de tecnologias verdes");
                // Habilitar campos de tecnologias verdes
                $('#tecverde_classe, #tecverde_subclasse').prop('disabled', false);
            } else {
                addLog(`INDEFINIDO: Valor="${seAplica}", Texto="${seAplicaText}"`);
            }
        }
        
        // Função para preencher subclasses com base na classe selecionada
        function filtrarSubclasses() {
            var classe = $('#tecverde_classe').val();
            addLog("Filtrando subclasses para classe: " + classe);
            
            // Limpar o select de subclasse
            $('#tecverde_subclasse').empty();
            $('#tecverde_subclasse').append(new Option('Selecione...', ''));
            
            // Adicionar subclasses com base na classe selecionada
            if (classe === "Eficiência Energética") {
                $('#tecverde_subclasse').append(new Option('Iluminação LED', 'Iluminação LED'));
                $('#tecverde_subclasse').append(new Option('Sistemas de automação', 'Sistemas de automação'));
                $('#tecverde_subclasse').append(new Option('Isolamento térmico', 'Isolamento térmico'));
            } else if (classe === "Energias alternativas") {
                $('#tecverde_subclasse').append(new Option('Solar', 'Solar'));
                $('#tecverde_subclasse').append(new Option('Eólica', 'Eólica'));
                $('#tecverde_subclasse').append(new Option('Biomassa', 'Biomassa'));
            } else if (classe === "Gestão Ambiental") {
                $('#tecverde_subclasse').append(new Option('Tratamento de resíduos', 'Tratamento de resíduos'));
                $('#tecverde_subclasse').append(new Option('Controle de poluição', 'Controle de poluição'));
            }
        }
        
        // Função para corrigir os campos de classe e subclasse
        function fixClasseAndSubclasse() {
            addLog("Fixing classe and subclasse fields...");
            
            const classe = aiSuggestionData.tecverde_classe;
            const subclasse = aiSuggestionData.tecverde_subclasse;
            
            addLog("Fixing with AI Values: " + JSON.stringify({ classe, subclasse }));
            
            // Make sure the fields are enabled
            $('#tecverde_classe, #tecverde_subclasse').prop('disabled', false);
            
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
                    addLog(`Classe '${classe}' not found in options. Adding it.`);
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
                
                addLog(`Classe set to '${classe}'`);
                
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
                            addLog(`Subclasse '${subclasse}' not found in options. Adding it.`);
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
                        
                        addLog(`Subclasse set to '${subclasse}'`);
                    }
                }, 500);
            }
        }
        
        // Função para corrigir o campo tecverde_se_aplica
        function fixTecverdeSeAplica() {
            addLog("Attempting to fix tecverde_se_aplica field...");
            
            const aiValue = aiSuggestionData.tecverde_se_aplica;
            const selectElement = document.getElementById('tecverde_se_aplica');
            
            addLog("Fixing with AI Value: " + aiValue);
            
            // Determine the correct index to select
            let targetIndex = -1;
            
            // Handle boolean values directly
            if (aiValue === true) {
                addLog("Boolean TRUE detected, selecting 'Sim'");
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
                addLog("Boolean FALSE detected, selecting 'Não'");
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
                addLog(`Setting select to index ${targetIndex} (${selectElement.options[targetIndex].text})`);
                
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
                
                addLog("Fix applied, new value: " + selectElement.value);
                
                // If "Sim" was selected, also fix classe and subclasse
                if (targetIndex === 1 || selectElement.options[targetIndex].text === "Sim") {
                    setTimeout(fixClasseAndSubclasse, 500);
                } else {
                    // If "Não" was selected, ensure classe and subclasse are disabled and empty
                    setTimeout(function() {
                        $('#tecverde_classe, #tecverde_subclasse').prop('disabled', true).val('');
                        addLog("Disabled and cleared classe and subclasse fields for 'Não' option");
                    }, 500);
                }
                
                // Call verificarTecverdeSePlica to ensure proper state
                setTimeout(function() {
                    verificarTecverdeSePlica();
                }, 600);
            } else {
                addLog("Could not determine the correct option to select");
            }
        }
        
        // Inicializar
        $(document).ready(function() {
            // Limpar resultados
            $('#resultados').empty();
            
            addLog("Página carregada. Pronto para testar.");
            
            // Event listener para o campo tecverde_se_aplica
            $('#tecverde_se_aplica').change(function() {
                verificarTecverdeSePlica();
            });
            
            // Event listener para o campo tecverde_classe
            $('#tecverde_classe').change(function() {
                filtrarSubclasses();
            });
            
            // Botão para testar com "Sim"
            $('#test-sim').click(function() {
                addLog("Iniciando teste com 'Sim'");
                
                // Definir dados da IA
                aiSuggestionData = {
                    "tecverde_se_aplica": "1",
                    "tecverde_classe": "Eficiência Energética",
                    "tecverde_subclasse": "Iluminação LED"
                };
                
                // Atualizar o JSON exibido
                $('#ai-data-json').text(JSON.stringify(aiSuggestionData));
                
                // Limpar campos
                $('#tecverde_se_aplica, #tecverde_classe, #tecverde_subclasse').val('');
                
                // Adicionar log com os dados da IA
                addLog("Dados da IA: Se aplica = Sim, Classe = Eficiência Energética, Subclasse = Iluminação LED");
                
                // Aplicar a correção
                fixTecverdeSeAplica();
            });
            
            // Botão para testar com "Não"
            $('#test-nao').click(function() {
                addLog("Iniciando teste com 'Não'");
                
                // Definir dados da IA
                aiSuggestionData = {
                    "tecverde_se_aplica": "0",
                    "tecverde_classe": "Eficiência Energética",
                    "tecverde_subclasse": "Iluminação LED"
                };
                
                // Atualizar o JSON exibido
                $('#ai-data-json').text(JSON.stringify(aiSuggestionData));
                
                // Limpar campos
                $('#tecverde_se_aplica, #tecverde_classe, #tecverde_subclasse').val('');
                
                // Adicionar log com os dados da IA
                addLog("Dados da IA: Se aplica = Não, Classe = , Subclasse = ");
                
                // Aplicar a correção
                fixTecverdeSeAplica();
            });
        });
    </script>
</body>
</html>
"""

def create_test_html():
    """Cria o arquivo HTML de teste."""
    html_path = os.path.join(CURRENT_DIR, "test_tecverde.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)
    return html_path

class TestHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Handler personalizado para o servidor HTTP."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=CURRENT_DIR, **kwargs)
    
    def log_message(self, format, *args):
        """Sobrescreve o método de log para não poluir o console."""
        return

def start_server(port=8000):
    """Inicia o servidor HTTP."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestHTTPRequestHandler)
    print(f"Servidor iniciado em http://localhost:{port}")
    
    # Iniciar o servidor em uma thread separada
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return httpd

def main():
    """Função principal."""
    # Criar o arquivo HTML de teste
    html_path = create_test_html()
    print(f"Arquivo HTML de teste criado em: {html_path}")
    
    # Iniciar o servidor
    port = 8000
    httpd = start_server(port)
    
    # Abrir o navegador
    url = f"http://localhost:{port}/test_tecverde.html"
    print(f"Abrindo o navegador em: {url}")
    webbrowser.open(url)
    
    try:
        # Manter o servidor rodando até o usuário pressionar Ctrl+C
        print("Pressione Ctrl+C para encerrar o servidor")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando o servidor...")
        httpd.shutdown()
        print("Servidor encerrado")

if __name__ == "__main__":
    main()
