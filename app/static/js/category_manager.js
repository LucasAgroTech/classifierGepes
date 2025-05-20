/**
 * GEPES Classifier - Gerenciamento de Categorias
 * 
 * Este script gerencia as interações do usuário com a interface de gerenciamento
 * de categorias, incluindo adição, edição e exclusão de categorias hierárquicas.
 */

$(document).ready(function() {
    // ===== MACROÁREAS =====
    // Abrir modal para adicionar macroárea
    $("#addMacroareaBtn").click(function() {
        $("#macroareaModalLabel").text("Nova Macroárea");
        $("#macroarea-id").val("");
        $("#macroarea-value").val("");
        $("#macroareaModal").modal("show");
    });
    
    // Abrir modal para editar macroárea
    $(document).on("click", ".edit-macroarea", function() {
        $("#macroareaModalLabel").text("Editar Macroárea");
        $("#macroarea-id").val($(this).data("id"));
        $("#macroarea-value").val($(this).data("value"));
        $("#macroareaModal").modal("show");
    });
    
    // Salvar macroárea
    $("#saveMacroareaBtn").click(function() {
        var id = $("#macroarea-id").val();
        var value = $("#macroarea-value").val();
        
        if (!value) {
            alert("Por favor, digite o nome da macroárea.");
            return;
        }
        
        if (id) {
            // Editar macroárea existente
            $.ajax({
                url: `/categories/edit/${id}`,
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify({ valor: value }),
                success: function(response) {
                    if (response.success) {
                        location.reload();  // Recarregar a página
                    } else {
                        alert(response.error || "Erro ao editar macroárea.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        } else {
            // Adicionar nova macroárea
            $.ajax({
                url: "/categories/add",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ tipo: "macroárea", valor: value }),
                success: function(response) {
                    if (response.success) {
                        location.reload();  // Recarregar a página
                    } else {
                        alert(response.error || "Erro ao adicionar macroárea.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        }
    });
    
    // Confirmar exclusão de macroárea
    $(document).on("click", ".delete-macroarea", function() {
        var id = $(this).data("id");
        var value = $(this).data("value");
        
        $("#confirmDeleteText").text(`Tem certeza que deseja excluir a macroárea "${value}"?`);
        $("#deleteWarningText").text("Esta ação também excluirá todos os segmentos e domínios relacionados a esta macroárea.");
        
        $("#confirmDeleteBtn").off("click").on("click", function() {
            $.ajax({
                url: `/categories/delete/${id}`,
                type: "DELETE",
                success: function(response) {
                    if (response.success) {
                        location.reload();  // Recarregar a página
                    } else {
                        alert(response.error || "Erro ao excluir macroárea.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        });
        
        $("#confirmDeleteModal").modal("show");
    });
    
    // ===== SEGMENTOS =====
    // Abrir modal para adicionar segmento
    $(document).on("click", ".add-segmento", function() {
        $("#segmentoModalLabel").text("Novo Segmento");
        $("#segmento-id").val("");
        $("#segmento-parent-id").val($(this).data("parent-id"));
        $("#segmento-parent").val($(this).data("parent-value"));
        $("#segmento-value").val("");
        $("#segmentoModal").modal("show");
    });
    
    // Abrir modal para editar segmento
    $(document).on("click", ".edit-segmento", function() {
        $("#segmentoModalLabel").text("Editar Segmento");
        $("#segmento-id").val($(this).data("id"));
        $("#segmento-parent-id").val($(this).data("parent-id"));
        
        // Extrair apenas o nome do segmento (sem a macroárea)
        var valorCompleto = $(this).data("value");
        var partes = valorCompleto.split("|");
        if (partes.length >= 2) {
            $("#segmento-parent").val(partes[0]);
            $("#segmento-value").val(partes[1]);
        } else {
            $("#segmento-value").val(valorCompleto);
        }
        
        $("#segmentoModal").modal("show");
    });
    
    // Salvar segmento
    $("#saveSegmentoBtn").click(function() {
        var id = $("#segmento-id").val();
        var parentId = $("#segmento-parent-id").val();
        var value = $("#segmento-value").val();
        
        if (!value) {
            alert("Por favor, digite o nome do segmento.");
            return;
        }
        
        if (id) {
            // Editar segmento existente
            $.ajax({
                url: `/categories/edit/${id}`,
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify({ valor: value }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao editar segmento.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        } else {
            // Adicionar novo segmento
            $.ajax({
                url: "/categories/add",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ 
                    tipo: "segmento", 
                    parent_id: parentId,
                    valor: value 
                }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao adicionar segmento.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        }
    });
    
    // Confirmar exclusão de segmento
    $(document).on("click", ".delete-segmento", function() {
        var id = $(this).data("id");
        var valorCompleto = $(this).data("value");
        var partes = valorCompleto.split("|");
        var valor = partes.length >= 2 ? partes[1] : valorCompleto;
        
        $("#confirmDeleteText").text(`Tem certeza que deseja excluir o segmento "${valor}"?`);
        $("#deleteWarningText").text("Esta ação também excluirá todos os domínios relacionados a este segmento.");
        
        $("#confirmDeleteBtn").off("click").on("click", function() {
            $.ajax({
                url: `/categories/delete/${id}`,
                type: "DELETE",
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao excluir segmento.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        });
        
        $("#confirmDeleteModal").modal("show");
    });
    
    // ===== DOMÍNIOS =====
    // Abrir modal para adicionar domínio
    $(document).on("click", ".add-dominio", function() {
        $("#dominioModalLabel").text("Novo Domínio");
        $("#dominio-id").val("");
        $("#dominio-parent-id").val($(this).data("parent-id"));
        
        // Extrair apenas o nome do segmento para exibição
        var valorCompleto = $(this).data("parent-value");
        var partes = valorCompleto.split("|");
        $("#dominio-parent").val(partes.length >= 2 ? partes[1] : valorCompleto);
        
        $("#dominio-value").val("");
        $("#dominioModal").modal("show");
    });
    
    // Abrir modal para editar domínio
    $(document).on("click", ".edit-dominio", function() {
        $("#dominioModalLabel").text("Editar Domínio");
        $("#dominio-id").val($(this).data("id"));
        $("#dominio-parent-id").val($(this).data("parent-id"));
        $("#dominio-value").val($(this).data("value"));
        
        // Buscar o valor do segmento pai para exibição
        var parentSegmentoBtn = $(".add-dominio[data-parent-id='" + $(this).data("parent-id") + "']");
        if (parentSegmentoBtn.length > 0) {
            var valorCompleto = parentSegmentoBtn.data("parent-value");
            var partes = valorCompleto.split("|");
            $("#dominio-parent").val(partes.length >= 2 ? partes[1] : valorCompleto);
        }
        
        $("#dominioModal").modal("show");
    });
    
    // Salvar domínio
    $("#saveDominioBtn").click(function() {
        var id = $("#dominio-id").val();
        var parentId = $("#dominio-parent-id").val();
        var value = $("#dominio-value").val();
        
        if (!value) {
            alert("Por favor, digite o nome do domínio.");
            return;
        }
        
        if (id) {
            // Editar domínio existente
            $.ajax({
                url: `/categories/edit/${id}`,
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify({ valor: value }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao editar domínio.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        } else {
            // Adicionar novo domínio
            $.ajax({
                url: "/categories/add",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ 
                    tipo: "dominio", 
                    parent_id: parentId,
                    valor: value 
                }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao adicionar domínio.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        }
    });
    
    // Confirmar exclusão de domínio
    $(document).on("click", ".delete-dominio", function() {
        var id = $(this).data("id");
        var valor = $(this).data("value");
        
        $("#confirmDeleteText").text(`Tem certeza que deseja excluir o domínio "${valor}"?`);
        $("#deleteWarningText").text("Esta ação não pode ser desfeita.");
        
        $("#confirmDeleteBtn").off("click").on("click", function() {
            $.ajax({
                url: `/categories/delete/${id}`,
                type: "DELETE",
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao excluir domínio.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        });
        
        $("#confirmDeleteModal").modal("show");
    });
    
    // ===== CLASSES DE TECNOLOGIA VERDE =====
    // Abrir modal para adicionar classe
    $("#addClasseBtn").click(function() {
        $("#classeModalLabel").text("Nova Classe");
        $("#classe-id").val("");
        $("#classe-value").val("");
        $("#classeModal").modal("show");
    });
    
    // Abrir modal para editar classe
    $(document).on("click", ".edit-classe", function() {
        $("#classeModalLabel").text("Editar Classe");
        $("#classe-id").val($(this).data("id"));
        $("#classe-value").val($(this).data("value"));
        $("#classeModal").modal("show");
    });
    
    // Salvar classe
    $("#saveClasseBtn").click(function() {
        var id = $("#classe-id").val();
        var value = $("#classe-value").val();
        
        if (!value) {
            alert("Por favor, digite o nome da classe.");
            return;
        }
        
        if (id) {
            // Editar classe existente
            $.ajax({
                url: `/categories/edit/${id}`,
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify({ valor: value }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao editar classe.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        } else {
            // Adicionar nova classe
            $.ajax({
                url: "/categories/add",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ tipo: "tecverde_classe", valor: value }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao adicionar classe.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        }
    });
    
    // Confirmar exclusão de classe
    $(document).on("click", ".delete-classe", function() {
        var id = $(this).data("id");
        var value = $(this).data("value");
        
        $("#confirmDeleteText").text(`Tem certeza que deseja excluir a classe "${value}"?`);
        $("#deleteWarningText").text("Esta ação também excluirá todas as subclasses relacionadas a esta classe.");
        
        $("#confirmDeleteBtn").off("click").on("click", function() {
            $.ajax({
                url: `/categories/delete/${id}`,
                type: "DELETE",
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao excluir classe.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        });
        
        $("#confirmDeleteModal").modal("show");
    });
    
    // ===== SUBCLASSES DE TECNOLOGIA VERDE =====
    // Abrir modal para adicionar subclasse
    $(document).on("click", ".add-subclasse", function() {
        $("#subclasseModalLabel").text("Nova Subclasse");
        $("#subclasse-id").val("");
        $("#subclasse-parent-id").val($(this).data("parent-id"));
        $("#subclasse-parent").val($(this).data("parent-value"));
        $("#subclasse-value").val("");
        $("#subclasseModal").modal("show");
    });
    
    // Abrir modal para editar subclasse
    $(document).on("click", ".edit-subclasse", function() {
        $("#subclasseModalLabel").text("Editar Subclasse");
        $("#subclasse-id").val($(this).data("id"));
        $("#subclasse-parent-id").val($(this).data("parent-id"));
        
        // Extrair apenas o nome da subclasse (sem a classe)
        var valorCompleto = $(this).data("value");
        var partes = valorCompleto.split("|");
        if (partes.length >= 2) {
            $("#subclasse-parent").val(partes[0]);
            $("#subclasse-value").val(partes[1]);
        } else {
            $("#subclasse-value").val(valorCompleto);
        }
        
        $("#subclasseModal").modal("show");
    });
    
    // Salvar subclasse
    $("#saveSubclasseBtn").click(function() {
        var id = $("#subclasse-id").val();
        var parentId = $("#subclasse-parent-id").val();
        var value = $("#subclasse-value").val();
        
        if (!value) {
            alert("Por favor, digite o nome da subclasse.");
            return;
        }
        
        if (id) {
            // Editar subclasse existente
            $.ajax({
                url: `/categories/edit/${id}`,
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify({ valor: value }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao editar subclasse.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        } else {
            // Adicionar nova subclasse
            $.ajax({
                url: "/categories/add",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ 
                    tipo: "tecverde_subclasse", 
                    parent_id: parentId,
                    valor: value 
                }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao adicionar subclasse.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        }
    });
    
    // Confirmar exclusão de subclasse
    $(document).on("click", ".delete-subclasse", function() {
        var id = $(this).data("id");
        var valorCompleto = $(this).data("value");
        var partes = valorCompleto.split("|");
        var valor = partes.length >= 2 ? partes[1] : valorCompleto;
        
        $("#confirmDeleteText").text(`Tem certeza que deseja excluir a subclasse "${valor}"?`);
        $("#deleteWarningText").text("Esta ação não pode ser desfeita.");
        
        $("#confirmDeleteBtn").off("click").on("click", function() {
            $.ajax({
                url: `/categories/delete/${id}`,
                type: "DELETE",
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error || "Erro ao excluir subclasse.");
                    }
                },
                error: function() {
                    alert("Erro de comunicação com o servidor.");
                }
            });
        });
        
        $("#confirmDeleteModal").modal("show");
    });
});
