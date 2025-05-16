from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import AIRating, Projeto, db
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ai_ratings_bp = Blueprint('ai_ratings', __name__, url_prefix='/api/ratings')

# Função para obter uma avaliação específica
def get_ai_rating(project_id, user_id, tipo):
    """
    Obtém a avaliação da IA para um projeto e usuário específicos.
    
    Args:
        project_id: ID ou código do projeto
        user_id: ID do usuário (email)
        tipo: Tipo da avaliação ('aia' ou 'tecverde')
        
    Returns:
        Objeto AIRating ou None se não encontrado
    """
    try:
        # Verificar se project_id é um inteiro (ID interno) ou uma string (código do projeto)
        if isinstance(project_id, str) and not project_id.isdigit():
            # É um código de projeto, precisamos obter o ID interno
            projeto = Projeto.query.filter_by(codigo_projeto=project_id).first()
            if not projeto:
                return None
            project_id = projeto.id
        
        rating = AIRating.query.filter_by(
            id_projeto=project_id,
            user_id=user_id,
            tipo=tipo
        ).first()
        
        return rating
    except Exception as e:
        logger.error(f"Erro ao obter avaliação da IA: {str(e)}")
        return None

# Função para obter a avaliação mais recente, independente do usuário
def get_latest_ai_rating(project_id, tipo):
    """
    Obtém a avaliação mais recente da IA para um projeto, independente do usuário.
    
    Args:
        project_id: ID ou código do projeto
        tipo: Tipo da avaliação ('aia' ou 'tecverde')
        
    Returns:
        Objeto AIRating ou None se não encontrado
    """
    try:
        # Verificar se project_id é um inteiro (ID interno) ou uma string (código do projeto)
        if isinstance(project_id, str) and not project_id.isdigit():
            # É um código de projeto, precisamos obter o ID interno
            projeto = Projeto.query.filter_by(codigo_projeto=project_id).first()
            if not projeto:
                return None
            project_id = projeto.id
        
        # Buscar a avaliação mais recente para este projeto e tipo
        rating = AIRating.query.filter_by(
            id_projeto=project_id,
            tipo=tipo
        ).order_by(AIRating.timestamp.desc()).first()
        
        return rating
    except Exception as e:
        logger.error(f"Erro ao obter avaliação mais recente da IA: {str(e)}")
        return None

# Rota para avaliação da IA
@ai_ratings_bp.route('/save', methods=['POST'])
@login_required
def save_rating():
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Verificar campos obrigatórios
        required_fields = ['project_id', 'rating', 'tipo']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório ausente: {field}'}), 400
        
        project_id = data['project_id']
        rating_value = data['rating']
        tipo = data['tipo']
        observacoes = data.get('observacoes', '')
        
        # Validar tipo
        if tipo not in ['aia', 'tecverde']:
            return jsonify({'error': 'Tipo de avaliação inválido. Deve ser "aia" ou "tecverde"'}), 400
        
        # Validar rating
        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                return jsonify({'error': 'Avaliação deve ser um número entre 1 e 5'}), 400
        except ValueError:
            return jsonify({'error': 'Avaliação deve ser um número entre 1 e 5'}), 400
        
        # Verificar se o projeto existe
        # Buscar o projeto pelo código do projeto (string) em vez do ID (inteiro)
        projeto = Projeto.query.filter_by(codigo_projeto=project_id).first()
        if not projeto:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        # Verificar se já existe uma avaliação para este projeto, usuário e tipo
        user_id = current_user.email
        rating = AIRating.query.filter_by(
            id_projeto=projeto.id,
            user_id=user_id,
            tipo=tipo
        ).first()
        
        if rating:
            # Atualizar avaliação existente
            rating.rating = rating_value
            rating.observacoes = observacoes
            rating.timestamp = datetime.now()
            
            # Atualizar também o registro do projeto
            if tipo == 'aia':
                projeto.ai_rating_aia = rating_value
                projeto.ai_rating_aia_user = current_user.nome
                projeto.ai_rating_aia_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                projeto.ai_rating_aia_observacoes = observacoes
            else:  # tecverde
                projeto.ai_rating_tecverde = rating_value
                projeto.ai_rating_tecverde_user = current_user.nome
                projeto.ai_rating_tecverde_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                projeto.ai_rating_tecverde_observacoes = observacoes
        else:
            # Criar nova avaliação
            rating = AIRating(
                id_projeto=projeto.id,
                id_usuario=current_user.id if current_user.is_authenticated else None,
                user_id=user_id,
                nome_usuario=current_user.nome if current_user.is_authenticated else 'Usuário',
                tipo=tipo,
                rating=rating_value,
                observacoes=observacoes,
                timestamp=datetime.now()
            )
            db.session.add(rating)
            
            # Atualizar também o registro do projeto
            if tipo == 'aia':
                projeto.ai_rating_aia = rating_value
                projeto.ai_rating_aia_user = current_user.nome
                projeto.ai_rating_aia_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                projeto.ai_rating_aia_observacoes = observacoes
            else:  # tecverde
                projeto.ai_rating_tecverde = rating_value
                projeto.ai_rating_tecverde_user = current_user.nome
                projeto.ai_rating_tecverde_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                projeto.ai_rating_tecverde_observacoes = observacoes
        
        # Salvar mudanças
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Avaliação salva com sucesso',
            'rating': rating.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar avaliação: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Rota para obter avaliação
@ai_ratings_bp.route('/get/<project_id>/<string:tipo>', methods=['GET'])
@login_required
def get_rating(project_id, tipo):
    try:
        # Validar tipo
        if tipo not in ['aia', 'tecverde']:
            return jsonify({'error': 'Tipo de avaliação inválido. Deve ser "aia" ou "tecverde"'}), 400
        
        # Obter avaliação
        user_id = current_user.email
        rating = get_ai_rating(project_id, user_id, tipo)
        
        if rating:
            return jsonify({
                'success': True,
                'rating': rating.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nenhuma avaliação encontrada'
            }), 404
            
    except Exception as e:
        logger.error(f"Erro ao obter avaliação: {str(e)}")
        return jsonify({'error': str(e)}), 500
