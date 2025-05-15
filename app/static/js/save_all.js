/**
 * Funções para salvar formulários da página de categorização
 * Inclui funções individuais e função para salvar tudo em sequência
 */

// Função para salvar avaliação da IA (AIA)
function saveAiaRating() {
    return new Promise((resolve, reject) => {
        try {
            console.log("Iniciando salvamento da avaliação AIA...");
            
            // Obter o ID do projeto
            const projectId = $('#project_id').val();
            
            // Verificar se existe uma avaliação para salvar
            const ratingValue = $('#aia-rating-value').val();
            if (!ratingValue) {
                console.log("Nenhuma avaliação AIA para salvar, pulando...");
                resolve();
                return;
            }
            
            console.log("Encontrada avaliação AIA para salvar:", {
                rating: ratingValue,
                observacoes: $('#aia-rating-observacoes').val() || ""
            });
            
            // Garantir que o accordion esteja visível
            const justificationBox = $('#justificationBox');
            const wasHidden = justificationBox.is(':hidden');
            if (wasHidden) {
                justificationBox.show();
            }
            
            // Obter os dados da avaliação
            const data = {
                project_id: projectId,
                rating: parseInt(ratingValue),
                observacoes: $('#aia-rating-observacoes').val() || "",
                tipo: "aia"
            };
            
            // Enviar os dados via AJAX
            $.ajax({
                url: '/api/ratings/save',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function(response) {
                    console.log("Avaliação AIA salva com sucesso:", response);
                    // Restaurar o estado do accordion
                    if (wasHidden) {
                        justificationBox.hide();
                    }
                    
                    // Mostrar mensagem de sucesso se não estiver sendo chamado pelo saveAllForms
                    if (!window.savingAllForms) {
                        Swal.fire({
                            title: 'Sucesso!',
                            text: 'Avaliação AIA salva com sucesso!',
                            icon: 'success',
                            timer: 2000,
                            timerProgressBar: true,
                            showConfirmButton: false
                        });
                    }
                    
                    resolve();
                },
                error: function(xhr, status, error) {
                    console.warn("Erro ao salvar avaliação AIA:", error);
                    console.warn("Resposta do servidor:", xhr.responseText);
                    // Restaurar o estado do accordion
                    if (wasHidden) {
                        justificationBox.hide();
                    }
                    
                    // Mostrar mensagem de erro se não estiver sendo chamado pelo saveAllForms
                    if (!window.savingAllForms) {
                        Swal.fire({
                            title: 'Erro!',
                            text: 'Ocorreu um erro ao salvar a avaliação AIA',
                            icon: 'error',
                            confirmButtonColor: '#3085d6',
                            confirmButtonText: 'OK'
                        });
                    }
                    
                    resolve(); // Continuar mesmo com erro
                }
            });
        } catch (e) {
            console.error("Erro ao processar avaliação AIA:", e);
            
            // Mostrar mensagem de erro se não estiver sendo chamado pelo saveAllForms
            if (!window.savingAllForms) {
                Swal.fire({
                    title: 'Erro!',
                    text: 'Ocorreu um erro ao processar a avaliação AIA: ' + e.message,
                    icon: 'error',
                    confirmButtonColor: '#3085d6',
                    confirmButtonText: 'OK'
                });
            }
            
            resolve(); // Continuar mesmo com erro
        }
    });
}

// Função para salvar avaliação de tecnologias verdes
function saveTecverdeRating() {
    return new Promise((resolve, reject) => {
        try {
            console.log("Iniciando salvamento da avaliação Tecverde...");
            
            // Obter o ID do projeto
            const projectId = $('#project_id').val();
            
            // Verificar se existe uma avaliação para salvar
            const ratingValue = $('#tecverde-rating-value').val();
            if (!ratingValue) {
                console.log("Nenhuma avaliação Tecverde para salvar, pulando...");
                resolve();
                return;
            }
            
            console.log("Encontrada avaliação Tecverde para salvar:", {
                rating: ratingValue,
                observacoes: $('#tecverde-rating-observacoes').val() || ""
            });
            
            // Garantir que o accordion esteja visível
            const tecverdeJustificationBox = $('#tecverdeJustificationBox');
            const wasHidden = tecverdeJustificationBox.is(':hidden');
            if (wasHidden) {
                tecverdeJustificationBox.show();
            }
            
            // Obter os dados da avaliação
            const data = {
                project_id: projectId,
                rating: parseInt(ratingValue),
                observacoes: $('#tecverde-rating-observacoes').val() || "",
                tipo: "tecverde"
            };
            
            // Enviar os dados via AJAX
            $.ajax({
                url: '/api/ratings/save',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function(response) {
                    console.log("Avaliação Tecverde salva com sucesso:", response);
                    // Restaurar o estado do accordion
                    if (wasHidden) {
                        tecverdeJustificationBox.hide();
                    }
                    
                    // Mostrar mensagem de sucesso se não estiver sendo chamado pelo saveAllForms
                    if (!window.savingAllForms) {
                        Swal.fire({
                            title: 'Sucesso!',
                            text: 'Avaliação Tecverde salva com sucesso!',
                            icon: 'success',
                            timer: 2000,
                            timerProgressBar: true,
                            showConfirmButton: false
                        });
                    }
                    
                    resolve();
                },
                error: function(xhr, status, error) {
                    console.warn("Erro ao salvar avaliação Tecverde:", error);
                    console.warn("Resposta do servidor:", xhr.responseText);
                    // Restaurar o estado do accordion
                    if (wasHidden) {
                        tecverdeJustificationBox.hide();
                    }
                    
                    // Mostrar mensagem de erro se não estiver sendo chamado pelo saveAllForms
                    if (!window.savingAllForms) {
                        Swal.fire({
                            title: 'Erro!',
                            text: 'Ocorreu um erro ao salvar a avaliação Tecverde',
                            icon: 'error',
                            confirmButtonColor: '#3085d6',
                            confirmButtonText: 'OK'
                        });
                    }
                    
                    resolve(); // Continuar mesmo com erro
                }
            });
        } catch (e) {
            console.error("Erro ao processar avaliação Tecverde:", e);
            
            // Mostrar mensagem de erro se não estiver sendo chamado pelo saveAllForms
            if (!window.savingAllForms) {
                Swal.fire({
                    title: 'Erro!',
                    text: 'Ocorreu um erro ao processar a avaliação Tecverde: ' + e.message,
                    icon: 'error',
                    confirmButtonColor: '#3085d6',
                    confirmButtonText: 'OK'
                });
            }
            
            resolve(); // Continuar mesmo com erro
        }
    });
}

// Função para salvar dados de tecnologias verdes
function saveTecverdeData() {
    return new Promise((resolve, reject) => {
        // Obter o ID do projeto
        const projectId = $('#project_id').val();
        
        // Obter os valores dos campos
        const tecverdeData = {
            tecverde_se_aplica: $('#tecverde_se_aplica').val() || "",
            tecverde_classe: $('#tecverde_classe').val() || "",
            tecverde_subclasse: $('#tecverde_subclasse').val() || "",
            tecverde_observacoes: $('#tecverde_observacoes').val() || ""
        };

        // Enviar dados para o servidor
        $.ajax({
            url: `/save_tecverde/${projectId}`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(tecverdeData),
            success: function(response) {
                if (response.success) {
                    // Mostrar mensagem de sucesso se não estiver sendo chamado pelo saveAllForms
                    if (!window.savingAllForms) {
                        Swal.fire({
                            title: 'Sucesso!',
                            text: 'Dados de tecnologias verdes salvos com sucesso!',
                            icon: 'success',
                            timer: 2000,
                            timerProgressBar: true,
                            showConfirmButton: false
                        });
                    }
                    resolve();
                } else {
                    // Mostrar mensagem de erro se não estiver sendo chamado pelo saveAllForms
                    if (!window.savingAllForms) {
                        Swal.fire({
                            title: 'Erro!',
                            text: response.error || 'Erro ao salvar tecnologias verdes',
                            icon: 'error',
                            confirmButtonColor: '#3085d6',
                            confirmButtonText: 'OK'
                        });
                    }
                    reject(response.error || 'Erro ao salvar tecnologias verdes');
                }
            },
            error: function(xhr) {
                // Mostrar mensagem de erro se não estiver sendo chamado pelo saveAllForms
                if (!window.savingAllForms) {
                    Swal.fire({
                        title: 'Erro!',
                        text: xhr.responseJSON?.error || 'Erro ao salvar tecnologias verdes',
                        icon: 'error',
                        confirmButtonColor: '#3085d6',
                        confirmButtonText: 'OK'
                    });
                }
                reject(xhr.responseJSON?.error || 'Erro ao salvar tecnologias verdes');
            }
        });
    });
}

// Função para salvar dados de categorização
function saveCategoriaData() {
    return new Promise((resolve, reject) => {
        // Obter o ID do projeto
        const projectId = $('#project_id').val();
        
        // Obter os dados do formulário
        const formData = new FormData($('form').get(0));
        
        // Garantir que campos vazios sejam strings vazias e não null
        for (let pair of formData.entries()) {
            if (pair[1] === '') {
                formData.set(pair[0], "");
            }
        }

        // Enviar dados para o servidor
        $.ajax({
            url: window.location.href,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                // Mostrar mensagem de sucesso se não estiver sendo chamado pelo saveAllForms
                if (!window.savingAllForms) {
                    Swal.fire({
                        title: 'Sucesso!',
                        text: 'Dados de categorização salvos com sucesso!',
                        icon: 'success',
                        timer: 2000,
                        timerProgressBar: true,
                        showConfirmButton: false
                    });
                }
                resolve();
            },
            error: function(xhr) {
                // Mostrar mensagem de erro se não estiver sendo chamado pelo saveAllForms
                if (!window.savingAllForms) {
                    Swal.fire({
                        title: 'Erro!',
                        text: xhr.responseJSON?.error || 'Erro ao salvar categorização',
                        icon: 'error',
                        confirmButtonColor: '#3085d6',
                        confirmButtonText: 'OK'
                    });
                }
                reject(xhr.responseJSON?.error || 'Erro ao salvar categorização');
            }
        });
    });
}

/**
 * Função para salvar todos os formulários da página de categorização
 * Coleta dados de ambos os formulários e salva em sequência
 */
function saveAllForms() {
    // Flag para indicar que estamos salvando todos os formulários
    window.savingAllForms = true;
    // Mostrar loading
    Swal.fire({
        title: 'Salvando...',
        text: 'Aguarde enquanto salvamos todos os dados...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Salvar em sequência: primeiro ratings, depois tecnologias verdes, por fim categorização
    saveAiaRating()
        .then(() => {
            return saveTecverdeRating();
        })
        .then(() => {
            return saveTecverdeData();
        })
        .then(() => {
            return saveCategoriaData();
        })
        .then(() => {
            // Resetar a flag
            window.savingAllForms = false;
            
            // Mostrar mensagem de sucesso
            Swal.fire({
                title: 'Sucesso!',
                text: 'Todos os dados foram salvos com sucesso!',
                icon: 'success',
                timer: 2000,
                timerProgressBar: true,
                showConfirmButton: false
            });
        })
        .catch((error) => {
            // Resetar a flag
            window.savingAllForms = false;
            
            // Mostrar mensagem de erro
            Swal.fire({
                title: 'Erro!',
                text: error || 'Ocorreu um erro ao salvar os dados',
                icon: 'error',
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'OK'
            });
        });
}

// Inicializar os botões de salvar quando o documento estiver pronto
$(document).ready(function() {
    // Inicializar o sistema de avaliação por estrelas para AIA
    $('.ai-rating .rating-star:not([data-type="tecverde"])').click(function() {
        const value = $(this).data('value');
        
        // Atualizar a aparência das estrelas
        $('.ai-rating .rating-star:not([data-type="tecverde"])').removeClass('active');
        $('.ai-rating .rating-star:not([data-type="tecverde"])').each(function() {
            if ($(this).data('value') <= value) {
                $(this).addClass('active');
            }
        });
        
        // Atualizar o valor no campo hidden
        $('#aia-rating-value').val(value);
        
        // Atualizar o texto de feedback
        let ratingText = '';
        switch(parseInt(value)) {
            case 1: ratingText = 'Muito ruim'; break;
            case 2: ratingText = 'Ruim'; break;
            case 3: ratingText = 'Regular'; break;
            case 4: ratingText = 'Bom'; break;
            case 5: ratingText = 'Excelente'; break;
            default: ratingText = 'Selecione uma avaliação';
        }
        $('#aia-rating-text').text(ratingText);
    });
    
    // Inicializar o sistema de avaliação por estrelas para Tecverde
    $('.ai-rating .rating-star[data-type="tecverde"]').click(function() {
        const value = $(this).data('value');
        
        // Atualizar a aparência das estrelas
        $('.ai-rating .rating-star[data-type="tecverde"]').removeClass('active');
        $('.ai-rating .rating-star[data-type="tecverde"]').each(function() {
            if ($(this).data('value') <= value) {
                $(this).addClass('active');
            }
        });
        
        // Atualizar o valor no campo hidden
        $('#tecverde-rating-value').val(value);
        
        // Atualizar o texto de feedback
        let ratingText = '';
        switch(parseInt(value)) {
            case 1: ratingText = 'Muito ruim'; break;
            case 2: ratingText = 'Ruim'; break;
            case 3: ratingText = 'Regular'; break;
            case 4: ratingText = 'Bom'; break;
            case 5: ratingText = 'Excelente'; break;
            default: ratingText = 'Selecione uma avaliação';
        }
        $('#tecverde-rating-text').text(ratingText);
    });
    
    // Restaurar estado das estrelas ao carregar a página
    function restoreRatingStars() {
        // Restaurar estrelas AIA
        const aiaRating = $('#aia-rating-value').val();
        if (aiaRating) {
            $('.ai-rating .rating-star:not([data-type="tecverde"])').each(function() {
                if ($(this).data('value') <= aiaRating) {
                    $(this).addClass('active');
                }
            });
            
            // Atualizar o texto de feedback
            let ratingText = '';
            switch(parseInt(aiaRating)) {
                case 1: ratingText = 'Muito ruim'; break;
                case 2: ratingText = 'Ruim'; break;
                case 3: ratingText = 'Regular'; break;
                case 4: ratingText = 'Bom'; break;
                case 5: ratingText = 'Excelente'; break;
                default: ratingText = 'Selecione uma avaliação';
            }
            $('#aia-rating-text').text(ratingText);
        }
        
        // Restaurar estrelas Tecverde
        const tecverdeRating = $('#tecverde-rating-value').val();
        if (tecverdeRating) {
            $('.ai-rating .rating-star[data-type="tecverde"]').each(function() {
                if ($(this).data('value') <= tecverdeRating) {
                    $(this).addClass('active');
                }
            });
            
            // Atualizar o texto de feedback
            let ratingText = '';
            switch(parseInt(tecverdeRating)) {
                case 1: ratingText = 'Muito ruim'; break;
                case 2: ratingText = 'Ruim'; break;
                case 3: ratingText = 'Regular'; break;
                case 4: ratingText = 'Bom'; break;
                case 5: ratingText = 'Excelente'; break;
                default: ratingText = 'Selecione uma avaliação';
            }
            $('#tecverde-rating-text').text(ratingText);
        }
    }
    
    // Restaurar estado das estrelas ao carregar a página
    setTimeout(restoreRatingStars, 500);
    
    // Botão para salvar avaliação AIA
    $('#saveAiaRatingBtn').click(function() {
        saveAiaRating();
    });
    
    // Botão para salvar avaliação Tecverde
    $('#saveTecverdeRatingBtn').click(function() {
        saveTecverdeRating();
    });
    
    // Botão para salvar dados de tecnologias verdes
    $('#saveTecverdeBtn').click(function() {
        saveTecverdeData();
    });
});
