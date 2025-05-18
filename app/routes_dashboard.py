from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import Projeto, Categoria, TecnologiaVerde, Log, AIRating, Usuario, CategoriaLista, AISuggestion, ClassificacaoAdicional, db
from sqlalchemy import func, desc, distinct, and_, or_
import json
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """
    Rota principal do dashboard que exibe estatísticas e visualizações dos dados.
    """
    try:
        # Estatísticas gerais
        stats = get_general_stats()
        
        # Dados para gráficos
        charts_data = get_charts_data()
        
        # Atividades recentes
        recent_activities = get_recent_activities()
        
        # Avaliações da IA
        ai_ratings = get_ai_ratings_stats()
        
        # Top unidades Embrapii
        top_ues = get_top_ues()
        
        # Distribuição por status de projeto
        status_distribution = get_status_distribution()
        
        # Distribuição por tecnologia verde
        tecverde_distribution = get_tecverde_distribution()
        
        return render_template(
            'dashboard.html',
            stats=stats,
            charts_data=json.dumps(charts_data),
            recent_activities=recent_activities,
            ai_ratings=ai_ratings,
            top_ues=top_ues,
            status_distribution=status_distribution,
            tecverde_distribution=tecverde_distribution
        )
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard: {str(e)}")
        return render_template('dashboard.html', error=str(e))

def get_general_stats():
    """
    Obtém estatísticas gerais sobre os projetos.
    """
    try:
        # Total de projetos
        total_projects = Projeto.query.count()
        
        # Projetos categorizados (com registro na tabela Categoria)
        categorized_projects = db.session.query(Categoria.id_projeto).distinct().count()
        
        # Projetos não categorizados
        uncategorized_projects = total_projects - categorized_projects
        
        # Projetos com tecnologia verde
        tecverde_projects = Projeto.query.filter(Projeto.tecverde_se_aplica == True).count()
        
        # Projetos sem tecnologia verde
        non_tecverde_projects = Projeto.query.filter(or_(
            Projeto.tecverde_se_aplica == False,
            Projeto.tecverde_se_aplica == None
        )).count()
        
        # Projetos com sugestão da IA (apenas os que não foram validados por humanos)
        ai_suggested_projects = db.session.query(AISuggestion.id_projeto).filter(
            ~AISuggestion.id_projeto.in_(db.session.query(Categoria.id_projeto))
        ).distinct().count()
        
        # Projetos com classificações adicionais
        additional_classifications = db.session.query(ClassificacaoAdicional.id_projeto).distinct().count()
        
        # Total de usuários
        total_users = Usuario.query.count()
        
        # Total de logs
        total_logs = Log.query.count()
        
        # Projetos por período (últimos 30 dias)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_projects = Projeto.query.filter(Projeto.data_criacao >= thirty_days_ago).count()
        
        return {
            'total_projects': total_projects,
            'categorized_projects': categorized_projects,
            'uncategorized_projects': uncategorized_projects,
            'categorized_percentage': round((categorized_projects / total_projects * 100) if total_projects > 0 else 0, 1),
            'tecverde_projects': tecverde_projects,
            'non_tecverde_projects': non_tecverde_projects,
            'tecverde_percentage': round((tecverde_projects / total_projects * 100) if total_projects > 0 else 0, 1),
            'ai_suggested_projects': ai_suggested_projects,
            'ai_suggested_percentage': round((ai_suggested_projects / total_projects * 100) if total_projects > 0 else 0, 1),
            'additional_classifications': additional_classifications,
            'total_users': total_users,
            'total_logs': total_logs,
            'recent_projects': recent_projects
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas gerais: {str(e)}")
        return {
            'total_projects': 0,
            'categorized_projects': 0,
            'uncategorized_projects': 0,
            'categorized_percentage': 0,
            'tecverde_projects': 0,
            'non_tecverde_projects': 0,
            'tecverde_percentage': 0,
            'ai_suggested_projects': 0,
            'ai_suggested_percentage': 0,
            'additional_classifications': 0,
            'total_users': 0,
            'total_logs': 0,
            'recent_projects': 0
        }

def get_charts_data():
    """
    Obtém dados para os gráficos do dashboard.
    """
    try:
        # Distribuição por macroárea
        macroareas_data = db.session.query(
            Projeto._aia_n1_macroarea,
            func.count(Projeto.id).label('count')
        ).filter(Projeto._aia_n1_macroarea != None, Projeto._aia_n1_macroarea != '').group_by(Projeto._aia_n1_macroarea).all()
        
        macroareas = {
            'labels': [m[0] for m in macroareas_data],
            'values': [m[1] for m in macroareas_data]
        }
        
        # Distribuição por segmento (top 10)
        segmentos_data = db.session.query(
            Projeto._aia_n2_segmento,
            func.count(Projeto.id).label('count')
        ).filter(Projeto._aia_n2_segmento != None, Projeto._aia_n2_segmento != '').group_by(Projeto._aia_n2_segmento).order_by(desc('count')).limit(10).all()
        
        segmentos = {
            'labels': [s[0] for s in segmentos_data],
            'values': [s[1] for s in segmentos_data]
        }
        
        # Distribuição por tecnologia verde (classes)
        tecverde_data = db.session.query(
            Projeto.tecverde_se_aplica,
            func.count(Projeto.id).label('count')
        ).filter(Projeto.tecverde_se_aplica.in_([True, False])).group_by(Projeto.tecverde_se_aplica).all()
        
        # Mapear True/False para "Sim"/"Não" para melhor visualização
        tecverde_labels = ["Sim" if t[0] else "Não" for t in tecverde_data]
        
        tecverde = {
            'labels': tecverde_labels,
            'values': [t[1] for t in tecverde_data]
        }
        
        # Top 10 classes de tecnologia verde
        tecverde_classes_data = db.session.query(
            Projeto.tecverde_classe,
            func.count(Projeto.id).label('count')
        ).filter(
            Projeto.tecverde_se_aplica == True,
            Projeto.tecverde_classe != None,
            Projeto.tecverde_classe != ''
        ).group_by(Projeto.tecverde_classe).order_by(desc('count')).limit(10).all()
        
        tecverde_classes = {
            'labels': [t[0] for t in tecverde_classes_data],
            'values': [t[1] for t in tecverde_classes_data]
        }
        
        # Timeline de projetos por data de contrato (agrupados por mês)
        timeline_data = db.session.query(
            func.date_trunc('month', func.to_timestamp(Projeto.data_contrato / 1000)).label('month'),
            func.count(Projeto.id).label('count')
        ).filter(Projeto.data_contrato != None).group_by('month').order_by('month').all()
        
        timeline = {
            'labels': [t[0].strftime('%b %Y') if t[0] else 'Desconhecido' for t in timeline_data],
            'values': [t[1] for t in timeline_data]
        }
        
        # Distribuição por status de projeto
        status_data = db.session.query(
            Projeto.status,
            func.count(Projeto.id).label('count')
        ).filter(Projeto.status != None, Projeto.status != '').group_by(Projeto.status).all()
        
        status = {
            'labels': [s[0] for s in status_data],
            'values': [s[1] for s in status_data]
        }
        
        return {
            'macroareas': macroareas,
            'segmentos': segmentos,
            'tecverde': tecverde,
            'tecverde_classes': tecverde_classes,
            'timeline': timeline,
            'status': status
        }
    except Exception as e:
        logger.error(f"Erro ao obter dados para gráficos: {str(e)}")
        return {
            'macroareas': {'labels': [], 'values': []},
            'segmentos': {'labels': [], 'values': []},
            'tecverde': {'labels': [], 'values': []},
            'tecverde_classes': {'labels': [], 'values': []},
            'timeline': {'labels': [], 'values': []},
            'status': {'labels': [], 'values': []}
        }

def get_recent_activities():
    """
    Obtém as atividades recentes de categorização.
    """
    try:
        # Obter os últimos 10 logs de categorização
        recent_logs = Log.query.order_by(Log.data_acao.desc()).limit(10).all()
        
        # Formatar os logs para exibição
        formatted_logs = []
        for log in recent_logs:
            # Obter o nome do projeto
            projeto = Projeto.query.get(log.id_projeto)
            projeto_nome = projeto.titulo if projeto else f"Projeto {log.id_projeto}"
            
            # Formatar a data
            data_formatada = log.data_acao.strftime('%d/%m/%Y %H:%M') if log.data_acao else 'Data desconhecida'
            
            # Adicionar ao resultado
            formatted_logs.append({
                'id': log.id,
                'projeto_id': log.id_projeto,
                'projeto_nome': projeto_nome,
                'usuario': log.nome_usuario or log.email_usuario,
                'acao': log.acao,
                'descricao': log.descricao,
                'data': data_formatada,
                'utilizou_ia': log.utilizou_ia,
                'usuario_modificou': log.usuario_modificou
            })
        
        return formatted_logs
    except Exception as e:
        logger.error(f"Erro ao obter atividades recentes: {str(e)}")
        return []

def get_ai_ratings_stats():
    """
    Obtém estatísticas sobre as avaliações da IA.
    """
    try:
        # Total de avaliações
        total_ratings = AIRating.query.count()
        
        # Distribuição de notas para AIA
        aia_ratings = db.session.query(
            AIRating.rating,
            func.count(AIRating.id).label('count')
        ).filter(AIRating.tipo == 'aia').group_by(AIRating.rating).all()
        
        aia_distribution = {rating: 0 for rating in range(1, 6)}
        for rating, count in aia_ratings:
            aia_distribution[rating] = count
        
        # Distribuição de notas para Tec Verde
        tecverde_ratings = db.session.query(
            AIRating.rating,
            func.count(AIRating.id).label('count')
        ).filter(AIRating.tipo == 'tecverde').group_by(AIRating.rating).all()
        
        tecverde_distribution = {rating: 0 for rating in range(1, 6)}
        for rating, count in tecverde_ratings:
            tecverde_distribution[rating] = count
        
        # Média das avaliações
        avg_aia_rating = db.session.query(func.avg(AIRating.rating)).filter(AIRating.tipo == 'aia').scalar() or 0
        avg_tecverde_rating = db.session.query(func.avg(AIRating.rating)).filter(AIRating.tipo == 'tecverde').scalar() or 0
        
        return {
            'total_ratings': total_ratings,
            'aia_distribution': aia_distribution,
            'tecverde_distribution': tecverde_distribution,
            'avg_aia_rating': round(float(avg_aia_rating), 1),
            'avg_tecverde_rating': round(float(avg_tecverde_rating), 1)
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de avaliações da IA: {str(e)}")
        return {
            'total_ratings': 0,
            'aia_distribution': {rating: 0 for rating in range(1, 6)},
            'tecverde_distribution': {rating: 0 for rating in range(1, 6)},
            'avg_aia_rating': 0,
            'avg_tecverde_rating': 0
        }

def get_top_ues():
    """
    Obtém as unidades Embrapii com mais projetos.
    """
    try:
        # Top 5 unidades Embrapii por número de projetos
        top_ues_data = db.session.query(
            Projeto.unidade_embrapii,
            func.count(Projeto.id).label('count')
        ).filter(Projeto.unidade_embrapii != None, Projeto.unidade_embrapii != '').group_by(Projeto.unidade_embrapii).order_by(desc('count')).limit(5).all()
        
        return [{'nome': ue[0], 'count': ue[1]} for ue in top_ues_data]
    except Exception as e:
        logger.error(f"Erro ao obter top unidades Embrapii: {str(e)}")
        return []

def get_status_distribution():
    """
    Obtém a distribuição de projetos por status de categorização.
    """
    try:
        total_projects = Projeto.query.count()
        
        # Projetos categorizados por humanos (com registro na tabela Categoria)
        human_validated = db.session.query(Categoria.id_projeto).distinct().count()
        
        # Projetos com sugestão da IA mas sem categorização por humanos
        ai_classified = db.session.query(AISuggestion.id_projeto).filter(
            ~AISuggestion.id_projeto.in_(db.session.query(Categoria.id_projeto))
        ).distinct().count()
        
        # Projetos não categorizados
        uncategorized = total_projects - human_validated - ai_classified
        
        return {
            'human_validated': human_validated,
            'ai_classified': ai_classified,
            'uncategorized': uncategorized,
            'human_validated_percentage': round((human_validated / total_projects * 100) if total_projects > 0 else 0, 1),
            'ai_classified_percentage': round((ai_classified / total_projects * 100) if total_projects > 0 else 0, 1),
            'uncategorized_percentage': round((uncategorized / total_projects * 100) if total_projects > 0 else 0, 1)
        }
    except Exception as e:
        logger.error(f"Erro ao obter distribuição por status: {str(e)}")
        return {
            'human_validated': 0,
            'ai_classified': 0,
            'uncategorized': 0,
            'human_validated_percentage': 0,
            'ai_classified_percentage': 0,
            'uncategorized_percentage': 0
        }

def get_tecverde_distribution():
    """
    Obtém a distribuição de projetos por tecnologia verde.
    """
    try:
        total_projects = Projeto.query.count()
        
        # Projetos com tecnologia verde
        tecverde_projects = Projeto.query.filter(Projeto.tecverde_se_aplica == True).count()
        
        # Projetos sem tecnologia verde
        non_tecverde_projects = Projeto.query.filter(Projeto.tecverde_se_aplica == False).count()
        
        # Projetos sem classificação de tecnologia verde
        unclassified_tecverde = total_projects - tecverde_projects - non_tecverde_projects
        
        return {
            'tecverde': tecverde_projects,
            'non_tecverde': non_tecverde_projects,
            'unclassified': unclassified_tecverde,
            'tecverde_percentage': round((tecverde_projects / total_projects * 100) if total_projects > 0 else 0, 1),
            'non_tecverde_percentage': round((non_tecverde_projects / total_projects * 100) if total_projects > 0 else 0, 1),
            'unclassified_percentage': round((unclassified_tecverde / total_projects * 100) if total_projects > 0 else 0, 1)
        }
    except Exception as e:
        logger.error(f"Erro ao obter distribuição por tecnologia verde: {str(e)}")
        return {
            'tecverde': 0,
            'non_tecverde': 0,
            'unclassified': 0,
            'tecverde_percentage': 0,
            'non_tecverde_percentage': 0,
            'unclassified_percentage': 0
        }

@dashboard_bp.route('/api/charts-data')
@login_required
def api_charts_data():
    """
    API para obter dados dos gráficos em formato JSON.
    """
    try:
        charts_data = get_charts_data()
        return jsonify(charts_data)
    except Exception as e:
        logger.error(f"Erro na API de dados de gráficos: {str(e)}")
        return jsonify({'error': str(e)}), 500
