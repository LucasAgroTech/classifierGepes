from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from app.models import CategoriaLista, db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar Blueprint para rotas de categorias
categories = Blueprint('categories', __name__)

@categories.route('/categories/manage', methods=['GET'])
@login_required
def manage_categories():
    """Exibe a página de gerenciamento hierárquico de categorias."""
    # Obter todas as categorias ativas
    categorias = CategoriaLista.query.filter_by(ativo=True).all()
    
    # Organizar categorias por tipo e hierarquia
    macroareas = [c for c in categorias if c.tipo == 'macroárea']
    segmentos = [c for c in categorias if c.tipo == 'segmento']
    dominios = [c for c in categorias if c.tipo == 'dominio']
    
    # Organizar tecnologias verdes
    tecverde_classes = [c for c in categorias if c.tipo == 'tecverde_classe']
    tecverde_subclasses = [c for c in categorias if c.tipo == 'tecverde_subclasse']
    
    # Estrutura hierárquica para UI
    hierarquia = construir_hierarquia(macroareas, segmentos, dominios)
    tecverde_hierarquia = construir_hierarquia_tecverde(tecverde_classes, tecverde_subclasses)
    
    return render_template(
        'manage_categories.html',
        hierarquia=hierarquia,
        tecverde_hierarquia=tecverde_hierarquia
    )

@categories.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    """Adiciona uma nova categoria respeitando a hierarquia."""
    data = request.json
    tipo = data.get('tipo')
    parent_id = data.get('parent_id')  # ID da categoria pai (para segmento/domínio)
    valor = data.get('valor')
    
    if not tipo or not valor:
        return jsonify({'success': False, 'error': 'Dados incompletos'})
    
    try:
        # Construir o valor hierárquico conforme o tipo
        valor_completo = valor
        
        if tipo == 'segmento' and parent_id:
            # Buscar a macroárea pai
            parent = CategoriaLista.query.get(parent_id)
            if parent and parent.tipo == 'macroárea':
                valor_completo = f"{parent.valor}|{valor}"
            else:
                return jsonify({'success': False, 'error': 'Macroárea pai não encontrada'})
                
        elif tipo == 'dominio' and parent_id:
            # Buscar o segmento pai (que já deve incluir a macroárea)
            parent = CategoriaLista.query.get(parent_id)
            if parent and parent.tipo == 'segmento':
                valor_completo = f"{parent.valor}|{valor}"
            else:
                return jsonify({'success': False, 'error': 'Segmento pai não encontrado'})
        
        elif tipo == 'tecverde_subclasse' and parent_id:
            # Buscar a classe pai
            parent = CategoriaLista.query.get(parent_id)
            if parent and parent.tipo == 'tecverde_classe':
                valor_completo = f"{parent.valor}|{valor}"
            else:
                return jsonify({'success': False, 'error': 'Classe pai não encontrada'})
        
        # Verificar se a categoria já existe
        existente = CategoriaLista.query.filter_by(tipo=tipo, valor=valor_completo).first()
        if existente:
            return jsonify({'success': False, 'error': 'Esta categoria já existe'})
        
        # Criar nova categoria
        nova_categoria = CategoriaLista(tipo=tipo, valor=valor_completo, ativo=True)
        db.session.add(nova_categoria)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Categoria adicionada com sucesso',
            'id': nova_categoria.id,
            'valor': valor_completo
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao adicionar categoria: {str(e)}")
        return jsonify({'success': False, 'error': f'Erro ao adicionar categoria: {str(e)}'})

@categories.route('/categories/edit/<int:id>', methods=['PUT'])
@login_required
def edit_category(id):
    """Edita uma categoria existente."""
    categoria = CategoriaLista.query.get_or_404(id)
    data = request.json
    novo_valor = data.get('valor')
    
    if not novo_valor:
        return jsonify({'success': False, 'error': 'Valor não fornecido'})
    
    try:
        # Diferentes abordagens dependendo do tipo
        if categoria.tipo == 'macroárea':
            # Para macroárea, atualizamos seu valor e todos os segmentos/domínios relacionados
            atualizar_hierarquia_macroárea(categoria.valor, novo_valor)
            categoria.valor = novo_valor
        
        elif categoria.tipo == 'segmento':
            # Para segmento, extraímos a macroárea atual e atualizamos o segmento
            partes = categoria.valor.split('|')
            if len(partes) >= 2:
                macroárea = partes[0]
                novo_valor_completo = f"{macroárea}|{novo_valor}"
                # Atualizar domínios relacionados
                atualizar_hierarquia_segmento(categoria.valor, novo_valor_completo)
                categoria.valor = novo_valor_completo
            else:
                return jsonify({'success': False, 'error': 'Formato inválido para segmento'})
        
        elif categoria.tipo == 'dominio':
            # Para domínio, extraímos a macroárea e segmento atuais
            partes = categoria.valor.split('|')
            if len(partes) >= 3:
                macroárea_segmento = '|'.join(partes[:2])
                novo_valor_completo = f"{macroárea_segmento}|{novo_valor}"
                categoria.valor = novo_valor_completo
            else:
                return jsonify({'success': False, 'error': 'Formato inválido para domínio'})
        
        elif categoria.tipo == 'tecverde_classe':
            # Para classe, atualizamos seu valor e todas as subclasses relacionadas
            atualizar_hierarquia_tecverde_classe(categoria.valor, novo_valor)
            categoria.valor = novo_valor
        
        elif categoria.tipo == 'tecverde_subclasse':
            # Para subclasse, extraímos a classe atual
            partes = categoria.valor.split('|')
            if len(partes) >= 2:
                classe = partes[0]
                novo_valor_completo = f"{classe}|{novo_valor}"
                categoria.valor = novo_valor_completo
            else:
                return jsonify({'success': False, 'error': 'Formato inválido para subclasse'})
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Categoria atualizada com sucesso'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao editar categoria: {str(e)}")
        return jsonify({'success': False, 'error': f'Erro ao editar categoria: {str(e)}'})

@categories.route('/categories/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_category(id):
    """Exclui (desativa) uma categoria e suas dependências."""
    categoria = CategoriaLista.query.get_or_404(id)
    
    try:
        # Verificar o tipo para tratamento adequado
        if categoria.tipo == 'macroárea':
            # Desativar todos os segmentos e domínios relacionados
            desativar_hierarquia_macroárea(categoria.valor)
        
        elif categoria.tipo == 'segmento':
            # Desativar todos os domínios relacionados
            desativar_hierarquia_segmento(categoria.valor)
        
        elif categoria.tipo == 'tecverde_classe':
            # Desativar todas as subclasses relacionadas
            desativar_hierarquia_tecverde_classe(categoria.valor)
        
        # Desativar a categoria em si (não excluímos do banco, apenas marcamos como inativa)
        categoria.ativo = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Categoria excluída com sucesso'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao excluir categoria: {str(e)}")
        return jsonify({'success': False, 'error': f'Erro ao excluir categoria: {str(e)}'})

# Funções auxiliares
def construir_hierarquia(macroareas, segmentos, dominios):
    """Constrói a estrutura hierárquica para exibição na UI."""
    hierarquia = []
    
    for macroarea in macroareas:
        macroarea_item = {
            'id': macroarea.id,
            'valor': macroarea.valor,
            'segmentos': []
        }
        
        # Encontrar segmentos relacionados
        for segmento in segmentos:
            partes = segmento.valor.split('|')
            if len(partes) >= 2 and partes[0] == macroarea.valor:
                segmento_item = {
                    'id': segmento.id,
                    'valor': partes[1],
                    'dominios': []
                }
                
                # Encontrar domínios relacionados
                for dominio in dominios:
                    partes_dom = dominio.valor.split('|')
                    if len(partes_dom) >= 3 and partes_dom[0] == macroarea.valor and partes_dom[1] == partes[1]:
                        segmento_item['dominios'].append({
                            'id': dominio.id,
                            'valor': partes_dom[2]
                        })
                
                macroarea_item['segmentos'].append(segmento_item)
        
        hierarquia.append(macroarea_item)
    
    return hierarquia

def construir_hierarquia_tecverde(classes, subclasses):
    """Constrói a estrutura hierárquica para Tecnologias Verdes."""
    hierarquia = []
    
    for classe in classes:
        classe_item = {
            'id': classe.id,
            'valor': classe.valor,
            'subclasses': []
        }
        
        # Encontrar subclasses relacionadas
        for subclasse in subclasses:
            partes = subclasse.valor.split('|')
            if len(partes) >= 2 and partes[0] == classe.valor:
                classe_item['subclasses'].append({
                    'id': subclasse.id,
                    'valor': partes[1]
                })
        
        hierarquia.append(classe_item)
    
    return hierarquia

def atualizar_hierarquia_macroárea(valor_antigo, valor_novo):
    """Atualiza o valor da macroárea em todos os segmentos e domínios relacionados."""
    # Atualizar segmentos
    segmentos = CategoriaLista.query.filter(
        CategoriaLista.tipo == 'segmento',
        CategoriaLista.valor.like(f"{valor_antigo}|%")
    ).all()
    
    for segmento in segmentos:
        partes = segmento.valor.split('|')
        if len(partes) >= 2:
            segmento.valor = f"{valor_novo}|{partes[1]}"
    
    # Atualizar domínios
    dominios = CategoriaLista.query.filter(
        CategoriaLista.tipo == 'dominio',
        CategoriaLista.valor.like(f"{valor_antigo}|%")
    ).all()
    
    for dominio in dominios:
        partes = dominio.valor.split('|')
        if len(partes) >= 3:
            dominio.valor = f"{valor_novo}|{partes[1]}|{partes[2]}"

def atualizar_hierarquia_segmento(valor_antigo, valor_novo):
    """Atualiza o valor do segmento em todos os domínios relacionados."""
    dominios = CategoriaLista.query.filter(
        CategoriaLista.tipo == 'dominio',
        CategoriaLista.valor.like(f"{valor_antigo}|%")
    ).all()
    
    for dominio in dominios:
        partes = dominio.valor.split('|')
        if len(partes) >= 3:
            # Extrair apenas a parte do segmento do valor_novo
            partes_novo = valor_novo.split('|')
            if len(partes_novo) >= 2:
                # Construir o novo valor do domínio
                dominio.valor = f"{partes_novo[0]}|{partes_novo[1]}|{partes[2]}"

def atualizar_hierarquia_tecverde_classe(valor_antigo, valor_novo):
    """Atualiza o valor da classe em todas as subclasses relacionadas."""
    subclasses = CategoriaLista.query.filter(
        CategoriaLista.tipo == 'tecverde_subclasse',
        CategoriaLista.valor.like(f"{valor_antigo}|%")
    ).all()
    
    for subclasse in subclasses:
        partes = subclasse.valor.split('|')
        if len(partes) >= 2:
            subclasse.valor = f"{valor_novo}|{partes[1]}"

def desativar_hierarquia_macroárea(valor_macroárea):
    """Desativa todos os segmentos e domínios relacionados a uma macroárea."""
    # Desativar segmentos
    segmentos = CategoriaLista.query.filter(
        CategoriaLista.tipo == 'segmento',
        CategoriaLista.valor.like(f"{valor_macroárea}|%"),
        CategoriaLista.ativo == True
    ).all()
    
    for segmento in segmentos:
        segmento.ativo = False
    
    # Desativar domínios
    dominios = CategoriaLista.query.filter(
        CategoriaLista.tipo == 'dominio',
        CategoriaLista.valor.like(f"{valor_macroárea}|%"),
        CategoriaLista.ativo == True
    ).all()
    
    for dominio in dominios:
        dominio.ativo = False

def desativar_hierarquia_segmento(valor_segmento):
    """Desativa todos os domínios relacionados a um segmento."""
    dominios = CategoriaLista.query.filter(
        CategoriaLista.tipo == 'dominio',
        CategoriaLista.valor.like(f"{valor_segmento}|%"),
        CategoriaLista.ativo == True
    ).all()
    
    for dominio in dominios:
        dominio.ativo = False

def desativar_hierarquia_tecverde_classe(valor_classe):
    """Desativa todas as subclasses relacionadas a uma classe."""
    subclasses = CategoriaLista.query.filter(
        CategoriaLista.tipo == 'tecverde_subclasse',
        CategoriaLista.valor.like(f"{valor_classe}|%"),
        CategoriaLista.ativo == True
    ).all()
    
    for subclasse in subclasses:
        subclasse.ativo = False
