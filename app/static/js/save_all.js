/**
 * Função para salvar todos os formulários da página de categorização
 * Coleta dados de ambos os formulários e salva em sequência
 */
function saveAllForms() {
    // Mostrar loading
    Swal.fire({
        title: 'Salvando...',
        text: 'Aguarde enquanto salvamos todos os dados...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    // Obter o ID do projeto
    const projectId = $('#project_id').val();
    
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
            // Mostrar mensagem de erro
            Swal.fire({
                title: 'Erro!',
                text: error || 'Ocorreu um erro ao salvar os dados',
                icon: 'error',
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'OK'
            });
        });

    // Função para salvar avaliação da IA (AIA)
    function saveAiaRating() {
        return new Promise((resolve, reject) => {
            try {
                console.log("Iniciando salvamento da avaliação AIA...");
                
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
                    url: '/save_ai_rating/' + projectId,
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(data),
                    success: function(response) {
                        console.log("Avaliação AIA salva com sucesso:", response);
                        // Restaurar o estado do accordion
                        if (wasHidden) {
                            justificationBox.hide();
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
                        resolve(); // Continuar mesmo com erro
                    }
                });
            } catch (e) {
                console.error("Erro ao processar avaliação AIA:", e);
                resolve(); // Continuar mesmo com erro
            }
        });
    }

    // Função para salvar avaliação de tecnologias verdes
    function saveTecverdeRating() {
        return new Promise((resolve, reject) => {
            try {
                console.log("Iniciando salvamento da avaliação Tecverde...");
                
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
                    url: '/save_ai_rating/' + projectId,
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(data),
                    success: function(response) {
                        console.log("Avaliação Tecverde salva com sucesso:", response);
                        // Restaurar o estado do accordion
                        if (wasHidden) {
                            tecverdeJustificationBox.hide();
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
                        resolve(); // Continuar mesmo com erro
                    }
                });
            } catch (e) {
                console.error("Erro ao processar avaliação Tecverde:", e);
                resolve(); // Continuar mesmo com erro
            }
        });
    }

    // Função para salvar dados de tecnologias verdes
    function saveTecverdeData() {
        return new Promise((resolve, reject) => {
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
                        resolve();
                    } else {
                        reject(response.error || 'Erro ao salvar tecnologias verdes');
                    }
                },
                error: function(xhr) {
                    reject(xhr.responseJSON?.error || 'Erro ao salvar tecnologias verdes');
                }
            });
        });
    }

    // Função para salvar dados de categorização
    function saveCategoriaData() {
        return new Promise((resolve, reject) => {
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
                    resolve();
                },
                error: function(xhr) {
                    reject(xhr.responseJSON?.error || 'Erro ao salvar categorização');
                }
            });
        });
    }
}
