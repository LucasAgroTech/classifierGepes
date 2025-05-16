from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Usuario, Projeto, Categoria, TecnologiaVerde, CategoriaLista, ClassificacaoAdicional, Log, AISuggestion, AIRating, db
from app.forms import LoginForm, CategorizacaoForm, SettingsForm
from app.ai_integration import OpenAIClient
from config import Config
import json
import os
from datetime import datetime
import logging

main = Blueprint('main', __name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para extrair nome do email
def extract_name_from_email(email):
    """
    Extrai o nome do usuário a partir do email.
    Exemplo: lucas.pinheiro@embrapii.org.br -> Lucas Pinheiro
    """
    try:
        # Remove o domínio
        username = email.split('@')[0]
        # Substitui pontos por espaços
        name_parts = username.replace('.', ' ').split()
        # Capitaliza cada parte
        capitalized_parts = [part.capitalize() for part in name_parts]
        # Junta as partes
        return ' '.join(capitalized_parts)
    except:
        return email  # Retorna o email original em caso de erro

# Métodos auxiliares para obter dados
def _get_categories_lists():
    """Obtém as listas de categorias do banco de dados."""
    organized_lists = {}
    
    # Obter todas as categorias ativas usando a query segura
    all_categories = _get_categoria_lista_query().filter_by(ativo=True).all()
    
    # Inicializar listas vazias para cada tipo
    for tipo in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
        organized_lists[tipo] = []
    
    # Mapeamento de tipos para consulta no banco de dados
    tipo_mapping = {
        'microarea': 'macroárea',
        'segmento': 'segmento',
        'dominio': 'dominio'
    }
    
    # Estrutura para armazenar domínios por microárea e segmento
    dominios_por_microarea_segmento = {}
    
    # Processar cada categoria
    for categoria in all_categories:
        tipo = categoria.tipo
        valor = categoria.valor
        
        # Mapear o tipo do banco de dados para o tipo usado na interface
        if tipo in tipo_mapping.values():
            # Encontrar a chave correspondente ao valor
            for ui_tipo, db_tipo in tipo_mapping.items():
                if db_tipo == tipo:
                    # Adicionar à lista correspondente
                    if valor not in organized_lists[ui_tipo]:
                        organized_lists[ui_tipo].append(valor)
                    break
        elif tipo in organized_lists:
            # Para outros tipos que não estão no mapeamento
            if valor not in organized_lists[tipo]:
                organized_lists[tipo].append(valor)
        
        # Processar categorias para a estrutura hierárquica
        if tipo == 'macroárea':
            # Macroárea é adicionada diretamente
            if valor not in organized_lists['microarea']:
                organized_lists['microarea'].append(valor)
            
            # Inicializar a estrutura para esta macroárea
            if valor not in dominios_por_microarea_segmento:
                dominios_por_microarea_segmento[valor] = {}
        
        elif tipo == 'segmento':
            # Segmento está no formato "Macroárea|Segmento"
            if '|' in valor:
                parts = valor.split('|')
                if len(parts) >= 2:
                    macroárea = parts[0]
                    segmento = parts[1]
                    
                    # Adicionar à lista de segmentos
                    if segmento not in organized_lists['segmento']:
                        organized_lists['segmento'].append(segmento)
                    
                    # Adicionar à estrutura hierárquica
                    if macroárea not in dominios_por_microarea_segmento:
                        dominios_por_microarea_segmento[macroárea] = {}
                    
                    if segmento not in dominios_por_microarea_segmento[macroárea]:
                        dominios_por_microarea_segmento[macroárea][segmento] = []
        
        elif tipo == 'dominio':
            # Domínio está no formato "Macroárea|Segmento|Domínio"
            if '|' in valor:
                parts = valor.split('|')
                if len(parts) >= 3:
                    macroárea = parts[0]
                    segmento = parts[1]
                    dominio = parts[2]
                    
                    # Adicionar à lista de domínios
                    if dominio not in organized_lists['dominio']:
                        organized_lists['dominio'].append(dominio)
                    
                    # Adicionar à estrutura hierárquica
                    if macroárea not in dominios_por_microarea_segmento:
                        dominios_por_microarea_segmento[macroárea] = {}
                    
                    if segmento not in dominios_por_microarea_segmento[macroárea]:
                        dominios_por_microarea_segmento[macroárea][segmento] = []
                    
                    if dominio not in dominios_por_microarea_segmento[macroárea][segmento]:
                        dominios_por_microarea_segmento[macroárea][segmento].append(dominio)
    
    # Converter a estrutura hierárquica para JSON
    organized_lists['dominios_por_microarea_segmento_json'] = json.dumps(dominios_por_microarea_segmento)
    
    return organized_lists

def _get_aia_data():
    """Simula a obtenção dos dados de AIA (que seria carregado de um arquivo)."""
    return [
        {
            "Macroárea": "Tecnologia da Informação",
            "Segmento": "Inteligência Artificial",
            "Domínios Afeitos": "Machine Learning; Visão Computacional; NLP"
        },
        {
            "Macroárea": "Tecnologia da Informação",
            "Segmento": "Infraestrutura",
            "Domínios Afeitos": "Cloud Computing; Edge Computing; IoT"
        },
        {
            "Macroárea": "Energia",
            "Segmento": "Renovável",
            "Domínios Afeitos": "Solar; Eólica; Biomassa"
        },
        {
            "Macroárea": "Energia",
            "Segmento": "Eficiência Energética",
            "Domínios Afeitos": "Smart Grid; Armazenamento; Gestão de Energia"
        }
    ]

def _get_tecverde_classes():
    """Obtém as classes de tecnologias verdes do banco de dados usando o método do OpenAIClient."""
    openai_client = OpenAIClient(Config.get_openai_api_key())
    return openai_client._get_tecverde_classes()

def _get_tecverde_subclasses():
    """Obtém as subclasses de tecnologias verdes do banco de dados usando o método do OpenAIClient."""
    openai_client = OpenAIClient(Config.get_openai_api_key())
    return openai_client._get_tecverde_subclasses()

def _get_ai_ratings(project_id):
    """Obtém as avaliações mais recentes da IA para um projeto, independente do usuário."""
    from app.models import AIRating
    
    # Verificar se project_id é um objeto Projeto ou um ID
    if isinstance(project_id, int) or (isinstance(project_id, str) and project_id.isdigit()):
        # É um ID numérico, usar diretamente
        project_id_num = int(project_id)
    else:
        # Pode ser um objeto Projeto ou um código de projeto
        if hasattr(project_id, 'id'):
            # É um objeto Projeto
            project_id_num = project_id.id
        elif hasattr(project_id, 'codigo_projeto'):
            # É um objeto Projeto, mas precisamos buscar o ID pelo código
            from app.models import Projeto
            projeto = Projeto.query.filter_by(codigo_projeto=project_id.codigo_projeto).first()
            project_id_num = projeto.id if projeto else None
        else:
            # Assumir que é um código de projeto
            from app.models import Projeto
            projeto = Projeto.query.filter_by(codigo_projeto=project_id).first()
            project_id_num = projeto.id if projeto else None
    
    if not project_id_num:
        return None
    
    # Buscar as avaliações mais recentes para cada tipo
    aia_rating = AIRating.query.filter_by(
        id_projeto=project_id_num,
        tipo='aia'
    ).order_by(AIRating.timestamp.desc()).first()
    
    tecverde_rating = AIRating.query.filter_by(
        id_projeto=project_id_num,
        tipo='tecverde'
    ).order_by(AIRating.timestamp.desc()).first()
    
    return {
        'aia': aia_rating.to_dict() if aia_rating else {'rating': 0, 'observacoes': ''},
        'tecverde': tecverde_rating.to_dict() if tecverde_rating else {'rating': 0, 'observacoes': ''}
    }

# Rota para a página inicial
@main.route('/')
def index():
    return redirect(url_for('main.projects'))

# Rota para login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.projects'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Verificar se o usuário existe
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.remember_me.data)
            flash('Login realizado com sucesso!', 'success')
            
            # Redirecionar para a página requisitada antes do login (se houver)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.projects')
            return redirect(next_page)
        else:
            flash('Credenciais inválidas. Por favor, tente novamente.', 'error')
    
    return render_template('login.html', form=form)

# Rota para logout
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('main.login'))

# Rota para listagem de projetos
@main.route('/projects')
@login_required
def projects():
    try:
        # Obter parâmetros da requisição
        page = request.args.get('page', 1, type=int)
        per_page = 20  # Reduzido para melhor desempenho com infinite scroll
        search = request.args.get('search', '')
        filter_type = request.args.get('filter', 'all')
        tecverde_filter = request.args.get('tecverde', 'all')
        is_ajax = request.args.get('ajax', '0') == '1'
        
        # Obter classes e subclasses de tecnologias verdes do banco de dados
        from app.ai_integration import OpenAIClient
        openai_client = OpenAIClient(Config.get_openai_api_key())
        tecverde_classes = openai_client._get_tecverde_classes()
        tecverde_subclasses = openai_client._get_tecverde_subclasses()
        
        # Carregar projetos com eager loading para evitar consultas N+1
        from sqlalchemy.orm import joinedload
        from sqlalchemy import or_
        
        # Iniciar a consulta base
        query = Projeto.query.options(
            joinedload(Projeto.categoria)
            # Removido joinedload(Projeto.ai_ratings) porque ai_ratings é lazy='dynamic'
            # e não suporta eager loading
        )
        
        # Aplicar filtro de busca se fornecido
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Projeto.titulo.ilike(search_term),
                    Projeto.codigo_projeto.ilike(search_term),
                    Projeto.unidade_embrapii.ilike(search_term),
                    Projeto._aia_n1_macroarea.ilike(search_term),
                    Projeto._aia_n2_segmento.ilike(search_term)
                )
            )
        
        # Aplicar filtro de categoria se fornecido
        if filter_type != 'all' and filter_type in ['uncategorized', 'ai_classified', 'human_validated']:
            if filter_type == 'uncategorized':
                # Projetos sem categoria e sem sugestão da IA
                query = query.outerjoin(Categoria).outerjoin(AISuggestion).filter(
                    Categoria.id_projeto == None,
                    AISuggestion.id_projeto == None
                )
            elif filter_type == 'ai_classified':
                # Projetos classificados por IA (tem sugestão da IA mas não tem categoria)
                query = query.outerjoin(Categoria).outerjoin(AISuggestion).filter(
                    Categoria.id_projeto == None,
                    AISuggestion.id_projeto == Projeto.id
                )
            elif filter_type == 'human_validated':
                # Projetos validados por humano (tem categoria)
                query = query.join(Categoria)
        
        # Aplicar filtro de Tec Verde se fornecido
        if tecverde_filter != 'all':
            if tecverde_filter == 'sim':
                # Projetos com Tec Verde = True
                query = query.filter(Projeto.tecverde_se_aplica == True)
            elif tecverde_filter == 'nao':
                # Projetos com Tec Verde = False
                query = query.filter(Projeto.tecverde_se_aplica == False)
            elif tecverde_filter.startswith('classe:'):
                # Filtrar por classe específica
                classe = tecverde_filter[7:]  # Remove 'classe:'
                query = query.filter(
                    Projeto.tecverde_se_aplica == True,
                    Projeto.tecverde_classe == classe
                )
            elif tecverde_filter.startswith('subclasse:'):
                # Filtrar por subclasse específica
                subclasse = tecverde_filter[10:]  # Remove 'subclasse:'
                query = query.filter(
                    Projeto.tecverde_se_aplica == True,
                    Projeto.tecverde_subclasse == subclasse
                )
        
        # Executar a consulta com paginação
        projects_query = query.paginate(page=page, per_page=per_page, error_out=False)
        
        projects_data = projects_query.items
        
        # Obter IDs dos projetos na página atual para filtrar sugestões da IA
        project_ids = [p.id for p in projects_data]
        
        # Obter apenas as sugestões da IA para os projetos na página atual
        ai_suggestions = AISuggestion.query.filter(
            AISuggestion.id_projeto.in_(project_ids)
        ).all()
        
        # Criar um dicionário de sugestões para acesso mais rápido
        ai_suggestions_by_project = {s.id_projeto: s for s in ai_suggestions}
        ai_suggestions_dict = [suggestion.to_dict() for suggestion in ai_suggestions]
        
        # Definir atributos para cada projeto
        for project in projects_data:
            # Verificar se o projeto tem categoria (já foi classificado)
            project.categorizado = project.categoria is not None
            
            # Verificar se o projeto tem sugestão da IA usando o dicionário
            project.ai_classified = project.id in ai_suggestions_by_project
            
            # Marcar o projeto como validado por humano apenas se tiver categoria
            project.human_validated = project.categorizado
            
            # Log para depuração
            if project.human_validated:
                logger.info(f"Projeto {project.codigo_projeto} (ID: {project.id}) marcado como validado por humano")
        
        # Se for uma requisição AJAX, retornar apenas os dados dos projetos em formato JSON
        if is_ajax:
            # Preparar dados para JSON
            projects_json = []
            for project in projects_data:
                project_dict = {
                    'id': project.id,
                    'codigo_projeto': project.codigo_projeto,
                    'titulo': project.titulo,
                    'unidade_embrapii': project.unidade_embrapii,
                    'data_contrato': project.data_contrato,
                    '_aia_n1_macroarea': project._aia_n1_macroarea,
                    '_aia_n2_segmento': project._aia_n2_segmento,
                    'tecverde_se_aplica': project.tecverde_se_aplica,
                    'tecverde_classe': project.tecverde_classe,
                    'tecverde_subclasse': project.tecverde_subclasse,
                    'human_validated': project.human_validated,
                    'ai_classified': project.ai_classified
                }
                projects_json.append(project_dict)
            
            return jsonify({
                'projects': projects_json,
                'has_next': projects_query.has_next,
                'next_page': projects_query.next_num if projects_query.has_next else None,
                'total': projects_query.total
            })
        
        # Para requisições normais, renderizar o template
        return render_template(
            'projects.html', 
            projects=projects_data, 
            ai_suggestions=ai_suggestions_dict,
            pagination=projects_query,
            total_projects=projects_query.total,
            has_next=projects_query.has_next,
            next_page=projects_query.next_num if projects_query.has_next else None,
            tecverde_classes=tecverde_classes,
            tecverde_subclasses=tecverde_subclasses
        )
        
    except Exception as e:
        # Melhorar o log de erros para facilitar a depuração
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Erro ao carregar projetos: {str(e)}\n{error_details}")
        
        # Informar o usuário sobre o erro
        flash(f'Erro ao carregar projetos: {str(e)}', 'error')
        return redirect(url_for('main.login'))

# Função para registrar log de categorização
def log_categorization(project_id, used_ai=False, validation_info=None, user_modified=False):
    try:
        # Buscar o projeto
        projeto = Projeto.query.get(project_id)
        if not projeto:
            logger.error(f"Projeto não encontrado: {project_id}")
            return False
        
        # Criar registro de log
        log = Log(
            id_projeto=project_id,
            id_usuario=current_user.id if current_user.is_authenticated else None,
            email_usuario=current_user.email if current_user.is_authenticated else 'sistema',
            nome_usuario=current_user.nome if current_user.is_authenticated else 'Sistema',
            acao='categorização',
            descricao=json.dumps(validation_info) if validation_info else None,
            utilizou_ia=used_ai,
            usuario_modificou=user_modified
        )
        
        # Se há avaliações da IA para este projeto, registrar a mais recente
        from app.routes_ai_ratings import get_latest_ai_rating
        
        # Verificar se project_id é um objeto Projeto ou um ID
        project_code = project_id
        if hasattr(projeto, 'codigo_projeto'):
            project_code = projeto.codigo_projeto
        
        # Carregar avaliação mais recente para Área de Interesse de Aplicação
        aia_rating = get_latest_ai_rating(project_code, 'aia')
        if aia_rating:
            log.ai_rating_aia = aia_rating.rating
        
        # Carregar avaliação mais recente para Tecnologias Verdes
        tecverde_rating = get_latest_ai_rating(project_code, 'tecverde')
        if tecverde_rating:
            log.ai_rating_tecverde = tecverde_rating.rating
        
        db.session.add(log)
        db.session.commit()
        
        logger.info(f"Log de categorização registrado para projeto {project_id}")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao registrar log de categorização: {str(e)}")
        return False

# Função para obter logs de um projeto específico
def get_project_logs(project_id):
    """
    Obtém os logs de categorização para um projeto específico.
    """
    try:
        project_logs = Log.query.filter_by(id_projeto=project_id).order_by(Log.data_acao.desc()).all()
        
        for log in project_logs:
            if not log.nome_usuario and log.email_usuario:
                log.nome_usuario = extract_name_from_email(log.email_usuario)
        
        return project_logs
    except Exception as e:
        logger.error(f"Erro ao obter logs do projeto: {str(e)}")
        return []

# Função para obter categorias do banco de dados de forma segura
def _get_categoria_lista_query():
    """
    Retorna uma query para CategoriaLista que é segura mesmo se a coluna 'descricao' não existir.
    """
    try:
        # Verificar se a coluna 'descricao' existe na tabela
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('categoria_listas', schema='gepes')]
        
        if 'descricao' in columns:
            # Se a coluna existe, incluí-la na query
            return CategoriaLista.query
        else:
            # Se a coluna não existe, criar uma query que não inclui a coluna
            from sqlalchemy import select
            from sqlalchemy.orm import aliased
            
            # Criar um alias para a tabela CategoriaLista
            CategoriaListaAlias = aliased(CategoriaLista)
            
            # Criar uma query que seleciona apenas as colunas que existem
            query = select(
                CategoriaListaAlias.id,
                CategoriaListaAlias.tipo,
                CategoriaListaAlias.valor,
                CategoriaListaAlias.ativo
            ).select_from(CategoriaListaAlias)
            
            # Converter para uma query SQLAlchemy
            return db.session.query(CategoriaListaAlias.id, CategoriaListaAlias.tipo, CategoriaListaAlias.valor, CategoriaListaAlias.ativo)
    except Exception as e:
        logger.error(f"Erro ao criar query para CategoriaLista: {str(e)}")
        # Em caso de erro, retornar uma query simples que não inclui a coluna 'descricao'
        return db.session.query(CategoriaLista.id, CategoriaLista.tipo, CategoriaLista.valor, CategoriaLista.ativo)

# Rota para categorização de um projeto
@main.route('/categorize/<project_id>', methods=['GET', 'POST'])
@login_required
def categorize(project_id):
    try:
        # Buscar o projeto pelo código do projeto (string) em vez do ID (inteiro)
        project = Projeto.query.filter_by(codigo_projeto=project_id).first_or_404()
        
        if request.method == 'POST':
            # Processar o formulário de categorização
            form_data = request.form
            
            # Processar dados de categorização
            microarea = form_data.get('microarea')
            segmento = form_data.get('segmento')
            dominio_values = request.form.getlist('dominio')
            dominio_str = ';'.join(dominio_values) if dominio_values else None
            dominio_outros_values = request.form.getlist('dominio_outros')
            dominio_outros_str = ';'.join(dominio_outros_values) if dominio_outros_values else None
            observacoes = form_data.get('observacoes')
            
            # Processar dados de tecnologia verde (apenas para leitura, não serão salvos)
            tecverde_se_aplica_str = form_data.get('tecverde_se_aplica')
            tecverde_se_aplica = bool(tecverde_se_aplica_str == '1' or (tecverde_se_aplica_str and tecverde_se_aplica_str.lower() == 'sim'))
            tecverde_classe = form_data.get('tecverde_classe')
            tecverde_subclasse = form_data.get('tecverde_subclasse')
            tecverde_observacoes = form_data.get('tecverde_observacoes')
            
            # Verificar se utilizou IA e se o usuário modificou os campos
            used_ai = form_data.get('used_ai') == 'true'
            user_modified = form_data.get('user_modified') == 'true'
            
            # Processar classificações adicionais
            additional_classifications_json = form_data.get('additional_classifications')
            additional_classifications = []
            if additional_classifications_json:
                try:
                    additional_classifications = json.loads(additional_classifications_json)
                except json.JSONDecodeError:
                    logger.error("Erro ao decodificar classificações adicionais")
            
            # Atualizar dados do projeto (exceto tecnologias verdes)
            project._aia_n1_macroarea = microarea
            project._aia_n2_segmento = segmento
            project._aia_n3_dominio_afeito = dominio_str
            project._aia_n3_dominio_outro = dominio_outros_str
            
            # Verificar/criar registro de Categoria
            categoria = Categoria.query.filter_by(id_projeto=project.id).first()
            if not categoria:
                categoria = Categoria(id_projeto=project.id)
                db.session.add(categoria)
            
            # Atualizar categoria
            categoria.microarea = microarea
            categoria.segmento = segmento
            categoria.dominio = dominio_str
            categoria.dominio_outros = dominio_outros_str
            categoria.observacoes = observacoes
            
            # Limpar classificações adicionais existentes
            ClassificacaoAdicional.query.filter_by(id_projeto=project.id).delete()
            
            # Adicionar novas classificações adicionais
            for i, classification in enumerate(additional_classifications):
                if classification.get('microarea') and classification.get('segmento'):
                    ordem = i + 1
                    adicional = ClassificacaoAdicional(
                        id_projeto=project.id,
                        microarea=classification['microarea'],
                        segmento=classification['segmento'],
                        ordem=ordem
                    )
                    db.session.add(adicional)
            
            # Salvar mudanças
            db.session.commit()
            
            # Registrar log
            log_categorization(project.id, used_ai, None, user_modified)
            
            flash('Categorização salva com sucesso!', 'success')
            return redirect(url_for('main.projects'))
        
        # Para requisição GET, mostrar formulário de categorização
        form = CategorizacaoForm()
        
        # Obter listas de categorias
        categories_lists = _get_categories_lists()
        
        # Verificar se o projeto tem dados salvos pelo usuário
        user_has_saved_data = has_user_saved_data(project.id)
        
        # Obter categorização existente
        existing = {
            'microarea': project._aia_n1_macroarea,
            'segmento': project._aia_n2_segmento,
            'dominio': project._aia_n3_dominio_afeito,
            'dominio_outros': project._aia_n3_dominio_outro,
            'tecverde_se_aplica': '1' if project.tecverde_se_aplica else '0',
            'tecverde_classe': project.tecverde_classe,
            'tecverde_subclasse': project.tecverde_subclasse,
            'tecverde_observacoes': project.tecverde_observacoes,
            'user_has_saved_data': user_has_saved_data
        }
        
        # Buscar categoria para obter observações
        categoria = Categoria.query.filter_by(id_projeto=project.id).first()
        if categoria:
            existing['observacoes'] = categoria.observacoes
        
        # Buscar classificações adicionais
        classificacoes_adicionais = ClassificacaoAdicional.query.filter_by(id_projeto=project.id).order_by(ClassificacaoAdicional.ordem).all()
        if classificacoes_adicionais:
            existing['additional_classifications'] = [
                {'microarea': ca.microarea, 'segmento': ca.segmento}
                for ca in classificacoes_adicionais
            ]
        
        # Verificar se já existe uma sugestão da IA para este projeto
        ai_suggestion = AISuggestion.query.filter_by(id_projeto=project.id).first()
        if ai_suggestion:
            ai_suggestion = ai_suggestion.to_dict()
        
        # Se não existe sugestão e o openai_api_key está configurado, gerar sugestão
        if not ai_suggestion:
            openai_api_key = Config.get_openai_api_key()
            if openai_api_key:
                try:
                    # Criar cliente OpenAI
                    openai_client = OpenAIClient(openai_api_key)
                    
                    # Obter dados de categorias do banco de dados
                    # O método suggest_categories irá chamar _get_aia_data_from_db internamente
                    ai_suggestion = openai_client.suggest_categories(project.__dict__)
                    
                    # Adicionar ID do projeto
                    ai_suggestion['project_id'] = project.id
                    
                    # A função suggest_categories já deve ter salvo a sugestão no banco
                    # Mas verificamos aqui como garantia
                    if not AISuggestion.query.filter_by(id_projeto=project.id).first():
                        suggestion = AISuggestion(
                            id_projeto=project.id,
                            _aia_n1_macroarea=ai_suggestion.get('_aia_n1_macroarea', ''),
                            _aia_n2_segmento=ai_suggestion.get('_aia_n2_segmento', ''),
                            _aia_n3_dominio_afeito=ai_suggestion.get('_aia_n3_dominio_afeito', ''),
                            _aia_n3_dominio_outro=ai_suggestion.get('_aia_n3_dominio_outro', ''),
                            confianca=ai_suggestion.get('confianca', ''),
                            justificativa=ai_suggestion.get('justificativa', ''),
                            tecverde_se_aplica=ai_suggestion.get('tecverde_se_aplica', False),
                            tecverde_classe=ai_suggestion.get('tecverde_classe', ''),
                            tecverde_subclasse=ai_suggestion.get('tecverde_subclasse', ''),
                            tecverde_confianca=ai_suggestion.get('tecverde_confianca', ''),
                            tecverde_justificativa=ai_suggestion.get('tecverde_justificativa', ''),
                            timestamp=datetime.now()
                        )
                        
                        # Log para depuração do valor de tecverde_se_aplica
                        logger.info(f"Valor de tecverde_se_aplica recebido da IA: {ai_suggestion.get('tecverde_se_aplica')}, tipo: {type(ai_suggestion.get('tecverde_se_aplica'))}")
                        logger.info(f"Valor de tecverde_se_aplica armazenado: {suggestion.tecverde_se_aplica}, tipo: {type(suggestion.tecverde_se_aplica)}")
                        db.session.add(suggestion)
                        db.session.commit()
                except Exception as e:
                    logger.error(f"Erro ao obter sugestão da IA: {str(e)}")
        
        # Obter dados para tecnologias verdes
        tecverde_classes = _get_tecverde_classes()
        tecverde_subclasses = _get_tecverde_subclasses()
        
        # Obter avaliações da IA
        ai_ratings = _get_ai_ratings(project.id)
        
        # Obter logs do projeto
        project_logs = get_project_logs(project.id)
        
        return render_template(
            'categorize.html',
            project=project,
            form=form,
            categories_lists=categories_lists,
            existing=existing,
            ai_suggestion=ai_suggestion,
            openai_enabled=bool(Config.get_openai_api_key()),
            project_logs=project_logs,
            tecverde_classes=tecverde_classes,
            tecverde_subclasses=tecverde_subclasses,
            ai_ratings=ai_ratings,
            user_has_saved_data=user_has_saved_data
        )
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'error')
        logger.error(f"Erro na categorização: {str(e)}")
        return redirect(url_for('main.projects'))

# Rota para salvar tecnologias verdes
@main.route('/save_tecverde/<project_id>', methods=['POST'])
@login_required
def save_tecverde(project_id):
    try:
        # Obter os dados enviados via JSON
        data = request.json
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Buscar o projeto pelo código do projeto (string) em vez do ID (inteiro)
        project = Projeto.query.filter_by(codigo_projeto=project_id).first_or_404()
        
        # Normalizar valor de tecverde_se_aplica para booleano
        tecverde_se_aplica_str = data.get('tecverde_se_aplica', '')
        # Garantir que tecverde_se_aplica seja sempre um booleano (True ou False), nunca None
        tecverde_se_aplica = bool(tecverde_se_aplica_str == '1' or (tecverde_se_aplica_str and tecverde_se_aplica_str.lower() == 'sim'))
        
        # Atualizar dados do projeto
        project.tecverde_se_aplica = tecverde_se_aplica
        project.tecverde_classe = data.get('tecverde_classe', '') if tecverde_se_aplica else ''
        project.tecverde_subclasse = data.get('tecverde_subclasse', '') if tecverde_se_aplica else ''
        project.tecverde_observacoes = data.get('tecverde_observacoes', '')
        
        # Verificar se existe registro de TecnologiaVerde
        tecverde = TecnologiaVerde.query.filter_by(id_projeto=project.id).first()
        if not tecverde:
            tecverde = TecnologiaVerde(id_projeto=project.id)
            db.session.add(tecverde)
        
        # Atualizar dados de TecnologiaVerde
        tecverde.se_aplica = tecverde_se_aplica
        tecverde.classe = data.get('tecverde_classe', '') if tecverde_se_aplica else ''
        tecverde.subclasse = data.get('tecverde_subclasse', '') if tecverde_se_aplica else ''
        tecverde.observacoes = data.get('tecverde_observacoes', '')
        
        # Salvar mudanças
        db.session.commit()
        
        # Registrar log
        log_categorization(project.id, False, None, True)
        
        return jsonify({
            'success': True,
            'message': 'Tecnologias verdes salvas com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar tecnologias verdes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Rota para sugestão automática de categorias
@main.route('/api/suggest-categories', methods=['POST'])
@login_required
def suggest_categories():
    try:
        data = request.json
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({'error': 'ID do projeto não fornecido'}), 400
        
        # Obter chave da API do OpenAI
        openai_api_key = Config.get_openai_api_key()
        
        if not openai_api_key:
            return jsonify({'error': 'Chave da API OpenAI não configurada'}), 400
        
        # Buscar o projeto
        project = Projeto.query.get_or_404(project_id)
        
        # Criar cliente OpenAI
        openai_client = OpenAIClient(openai_api_key)
        
        # Obter sugestões de categorias
        # O método suggest_categories irá obter as categorias do banco de dados
        suggestions = openai_client.suggest_categories(project.__dict__)
        
        # Armazenar a sugestão na sessão para uso posterior
        session['ai_suggestion'] = suggestions
        
        return jsonify(suggestions)
        
    except Exception as e:
        logger.error(f"Erro ao sugerir categorias: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Rota para validação de sugestões da IA
@main.route('/api/validate-suggestion', methods=['POST'])
@login_required
def validate_suggestion():
    try:
        data = request.json
        project_id = data.get('project_id')
        validation = data.get('validation', {})
        
        # Adicionar campos manuais ao objeto de validação
        for field in ['microarea', 'segmento', 'dominio']:
            manual_field = f'manual_{field}'
            if manual_field in data:
                validation[manual_field] = data.get(manual_field)
        
        # Tratar especificamente o campo dominio_outros/dominio_outro
        if 'manual_dominio_outros' in data:
            validation['manual_dominio_outros'] = data.get('manual_dominio_outros')
            validation['manual_dominio_outro'] = data.get('manual_dominio_outros')
        
        if not project_id:
            return jsonify({'error': 'ID do projeto não fornecido'}), 400
        
        # Obter a sugestão da IA da sessão
        suggestion = session.get('ai_suggestion')
        
        if not suggestion:
            return jsonify({'error': 'Nenhuma sugestão da IA encontrada na sessão'}), 400
        
        # Obter chave da API do OpenAI para processar a validação
        openai_api_key = Config.get_openai_api_key()
        
        if not openai_api_key:
            return jsonify({'error': 'Chave da API OpenAI não configurada'}), 400
        
        # Processar a validação
        openai_client = OpenAIClient(openai_api_key)
        result = openai_client.process_validation(suggestion, validation)
        
        # Buscar o projeto
        project = Projeto.query.get_or_404(project_id)
        
        # Atualizar o projeto com os resultados
        project._aia_n1_macroarea = result.get('_aia_n1_macroarea', '')
        project._aia_n2_segmento = result.get('_aia_n2_segmento', '')
        project._aia_n3_dominio_afeito = result.get('_aia_n3_dominio_afeito', '')
        project._aia_n3_dominio_outro = result.get('_aia_n3_dominio_outro', '')
        
        # Verificar/criar registro de Categoria
        categoria = Categoria.query.filter_by(id_projeto=project.id).first()
        if not categoria:
            categoria = Categoria(id_projeto=project.id)
            db.session.add(categoria)
        
        # Atualizar categoria
        categoria.microarea = result.get('_aia_n1_macroarea', '')
        categoria.segmento = result.get('_aia_n2_segmento', '')
        categoria.dominio = result.get('_aia_n3_dominio_afeito', '')
        categoria.dominio_outros = result.get('_aia_n3_dominio_outro', '')
        
        # Salvar mudanças
        db.session.commit()
        
        # Registrar log da categorização
        # Neste caso, consideramos que o usuário modificou os campos se houver campos manuais no objeto de validação
        user_modified = any(key.startswith('manual_') for key in validation.keys())
        log_categorization(project.id, True, validation, user_modified)
        
        return jsonify({'success': True, 'message': 'Validação processada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao validar sugestão: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Rota para adicionar novo domínio
@main.route('/add_dominio', methods=['POST'])
@login_required
def add_dominio():
    try:
        data = request.get_json()
        
        if not data or 'microarea' not in data or 'segmento' not in data or 'dominio' not in data:
            return jsonify({'success': False, 'error': 'Dados incompletos. É necessário fornecer macroárea, segmento e domínio.'}), 400
            
        microarea = data['microarea']
        segmento = data['segmento']
        novo_dominio = data['dominio']
        
        # Criar o valor hierárquico para o domínio
        valor_dominio = f"{microarea}|{segmento}|{novo_dominio}"
        
        # Verificar se o domínio já existe
        existente = _get_categoria_lista_query().filter_by(
            tipo='dominio', 
            valor=valor_dominio
        ).first()
        
        if existente:
            return jsonify({'success': False, 'error': 'Este domínio já existe para esta combinação de Macroárea e Segmento.'}), 400
        
        # Adicionar novo domínio à lista
        dominio = CategoriaLista(
            tipo='dominio',
            valor=valor_dominio,
            ativo=True
        )
        db.session.add(dominio)
        db.session.commit()
        
        # Buscar domínios atualizados para esta combinação de macroárea e segmento
        dominios_por_microarea_segmento = {}
        
        # Obter todas as categorias de domínio ativas
        all_dominios = CategoriaLista.query.filter_by(tipo='dominio', ativo=True).all()
        
        # Processar cada domínio para extrair a estrutura hierárquica
        for cat in all_dominios:
            if '|' in cat.valor:
                parts = cat.valor.split('|')
                if len(parts) >= 3:
                    m = parts[0]  # macroárea
                    s = parts[1]  # segmento
                    d = parts[2]  # domínio
                    
                    if m not in dominios_por_microarea_segmento:
                        dominios_por_microarea_segmento[m] = {}
                    
                    if s not in dominios_por_microarea_segmento[m]:
                        dominios_por_microarea_segmento[m][s] = []
                    
                    if d not in dominios_por_microarea_segmento[m][s]:
                        dominios_por_microarea_segmento[m][s].append(d)
        
        # Obter a lista de domínios para a combinação específica
        dominios_list = []
        if microarea in dominios_por_microarea_segmento and segmento in dominios_por_microarea_segmento[microarea]:
            dominios_list = dominios_por_microarea_segmento[microarea][segmento]
        
        return jsonify({
            'success': True, 
            'message': 'Domínio adicionado com sucesso.',
            'dominios': dominios_list,
            'dominios_por_microarea_segmento': dominios_por_microarea_segmento
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao adicionar domínio: {str(e)}")
        return jsonify({'success': False, 'error': f'Erro ao adicionar domínio: {str(e)}'}), 500

# Rota para salvar uma classificação adicional individualmente
@main.route('/save_additional_classification/<project_id>', methods=['POST'])
@login_required
def save_additional_classification(project_id):
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Verificar se os campos necessários estão presentes
        required_fields = ['microarea', 'segmento']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório ausente: {field}'}), 400
        
        # Verificar se o projeto existe
        project = Projeto.query.filter_by(codigo_projeto=project_id).first_or_404()
        
        # Verificar quantas classificações adicionais já existem
        count = ClassificacaoAdicional.query.filter_by(id_projeto=project_id).count()
        if count >= 3:
            return jsonify({'error': 'Limite máximo de 3 classificações adicionais atingido'}), 400
        
        # Verificar se a classificação já existe
        existente = ClassificacaoAdicional.query.filter_by(
            id_projeto=project_id,
            microarea=data['microarea'],
            segmento=data['segmento']
        ).first()
        
        if existente:
            return jsonify({'error': 'Esta classificação adicional já existe'}), 400
        
        # Criar a nova classificação adicional
        classificacao = ClassificacaoAdicional(
            id_projeto=project_id,
            microarea=data['microarea'],
            segmento=data['segmento'],
            ordem=count + 1
        )
        db.session.add(classificacao)
        db.session.commit()
        
        # Registrar log
        log_categorization(project_id, False, None, True)
        
        return jsonify({
            'success': True, 
            'message': 'Classificação adicional salva com sucesso',
            'classification': {
                'microarea': data['microarea'],
                'segmento': data['segmento']
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar classificação adicional: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Rota para remover uma classificação adicional
@main.route('/remove_additional_classification/<project_id>', methods=['POST'])
@login_required
def remove_additional_classification(project_id):
    try:
        data = request.json
        
        if not data or 'index' not in data:
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Converter index para inteiro
        try:
            index = int(data['index'])
        except ValueError:
            return jsonify({'error': 'Índice inválido'}), 400
        
        # Buscar o projeto pelo código
        project = Projeto.query.filter_by(codigo_projeto=project_id).first_or_404()
        
        # Buscar a classificação pelo índice (ordem)
        classificacao = ClassificacaoAdicional.query.filter_by(
            id_projeto=project.id,
            ordem=index
        ).first()
        
        if not classificacao:
            return jsonify({'error': 'Classificação não encontrada'}), 404
        
        # Guardar dados para retornar ao cliente
        removed = {
            'microarea': classificacao.microarea,
            'segmento': classificacao.segmento
        }
        
        # Remover a classificação
        db.session.delete(classificacao)
        
        # Reordenar as classificações restantes
        classificacoes = ClassificacaoAdicional.query.filter_by(
            id_projeto=project_id
        ).order_by(ClassificacaoAdicional.ordem).all()
        
        for i, c in enumerate(classificacoes, 1):
            c.ordem = i
        
        db.session.commit()
        
        # Registrar log
        log_categorization(project_id, False, None, True)
        
        return jsonify({
            'success': True,
            'message': 'Classificação adicional removida com sucesso',
            'removed_classification': removed
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao remover classificação adicional: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Rota para configurações
@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    
    if form.validate_on_submit():
        openai_api_key = form.openai_api_key.data
        
        # Salvar chave da API
        if Config.save_openai_api_key(openai_api_key):
            flash('Configurações salvas com sucesso!', 'success')
        else:
            flash('Erro ao salvar configurações', 'error')
        
        return redirect(url_for('main.settings'))
    
    # Para GET, preencher o formulário com a chave atual
    form.openai_api_key.data = Config.get_openai_api_key()
    
    return render_template('settings.html', form=form)

# Rota para visualização de logs
@main.route('/logs')
@login_required
def view_logs():
    try:
        # Buscar logs
        logs = Log.query.order_by(Log.data_acao.desc()).all()
        
        # Para cada log, adicionar o nome do projeto
        for log in logs:
            log.projeto_titulo = log.projeto.titulo if log.projeto else f"Projeto {log.id_projeto}"
            
            # Formatar nome do usuário se necessário
            if not log.nome_usuario and log.email_usuario:
                log.nome_usuario = extract_name_from_email(log.email_usuario)
        
        return render_template('logs.html', logs=logs)
        
    except Exception as e:
        flash(f'Erro ao carregar logs: {str(e)}', 'error')
        logger.error(f"Erro ao carregar logs: {str(e)}")
        return redirect(url_for('main.projects'))

# Rota para ir para o próximo projeto
@main.route('/next_project/<current_project_id>')
@login_required
def next_project(current_project_id):
    try:
        # Buscar o projeto atual para obter seu ID
        current_project = Projeto.query.filter_by(codigo_projeto=current_project_id).first_or_404()
        
        # Primeiro, tentar encontrar o próximo projeto classificado por IA mas não validado por humano
        next_project = Projeto.query.join(
            AISuggestion, Projeto.id == AISuggestion.id_projeto
        ).outerjoin(
            Categoria, Projeto.id == Categoria.id_projeto
        ).filter(
            Categoria.id_projeto == None,  # Não tem categoria (não validado por humano)
            Projeto.id > current_project.id  # ID maior que o atual (próximo)
        ).order_by(Projeto.id).first()
        
        # Se não encontrou, buscar qualquer projeto não classificado
        if not next_project:
            next_project = Projeto.query.outerjoin(
                Categoria, Projeto.id == Categoria.id_projeto
            ).filter(
                Categoria.id_projeto == None,  # Não tem categoria (não classificado)
                Projeto.id > current_project.id  # ID maior que o atual (próximo)
            ).order_by(Projeto.id).first()
            
        # Se ainda não encontrou, pegar o primeiro projeto (recomeçar do início)
        if not next_project:
            # Primeiro tentar projetos classificados por IA mas não validados
            next_project = Projeto.query.join(
                AISuggestion, Projeto.id == AISuggestion.id_projeto
            ).outerjoin(
                Categoria, Projeto.id == Categoria.id_projeto
            ).filter(
                Categoria.id_projeto == None  # Não tem categoria (não validado por humano)
            ).order_by(Projeto.id).first()
            
            # Se não encontrou, buscar qualquer projeto não classificado
            if not next_project:
                next_project = Projeto.query.outerjoin(
                    Categoria, Projeto.id == Categoria.id_projeto
                ).filter(
                    Categoria.id_projeto == None  # Não tem categoria (não classificado)
                ).order_by(Projeto.id).first()
        
        # Se encontrou um próximo projeto, redirecionar para ele
        if next_project:
            return redirect(url_for('main.categorize', project_id=next_project.codigo_projeto))
        
        # Se não encontrou nenhum projeto, voltar para a lista de projetos
        flash('Não há mais projetos para classificar.', 'info')
        return redirect(url_for('main.projects'))
        
    except Exception as e:
        flash(f'Erro ao buscar próximo projeto: {str(e)}', 'error')
        logger.error(f"Erro ao buscar próximo projeto: {str(e)}")
        return redirect(url_for('main.projects'))

# Rota para visualização de categorias
@main.route('/categories')
@login_required
def view_categories():
    try:
        # Aqui simularemos os dados do aia.json
        categories_data = [
            {
                "Macroárea": "Tecnologia da Informação",
                "Segmento": "Inteligência Artificial",
                "Domínios Afeitos": "Machine Learning; Visão Computacional; NLP"
            },
            {
                "Macroárea": "Tecnologia da Informação",
                "Segmento": "Infraestrutura",
                "Domínios Afeitos": "Cloud Computing; Edge Computing; IoT"
            },
            {
                "Macroárea": "Energia",
                "Segmento": "Renovável",
                "Domínios Afeitos": "Solar; Eólica; Biomassa"
            },
            {
                "Macroárea": "Energia",
                "Segmento": "Eficiência Energética",
                "Domínios Afeitos": "Smart Grid; Armazenamento; Gestão de Energia"
            }
        ]
        
        # Organizar os dados por macroárea
        organized_categories = {}
        for category in categories_data:
            macroarea = category.get('Macroárea')
            if macroarea not in organized_categories:
                organized_categories[macroarea] = []
            organized_categories[macroarea].append(category)
        
        # Obter dados de tecnologias verdes do banco de dados
        tecverde_classes = _get_tecverde_classes()
        tecverde_subclasses = _get_tecverde_subclasses()
        
        return render_template('categories.html', 
                              categories=organized_categories,
                              tecverde_classes=tecverde_classes,
                              tecverde_subclasses=tecverde_subclasses)
        
    except Exception as e:
        flash(f'Erro ao carregar categorias: {str(e)}', 'error')
        logger.error(f"Erro ao carregar categorias: {str(e)}")
        return redirect(url_for('main.projects'))

# Rota para gerenciar listas de categorias
@main.route('/lists', methods=['GET', 'POST'])
@login_required
def lists():
    try:
        if request.method == 'POST':
            # Processar o formulário de atualização de listas
            lists_data = {}
            
            # Mapeamento de tipos para consulta no banco de dados
            tipo_mapping = {
                'microarea': 'macroárea',
                'segmento': 'segmento',
                'dominio': 'dominio'
            }
            
            for column in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
                values = request.form.getlist(f'{column}[]')
                # Filtrar valores vazios
                values = [v for v in values if v.strip()]
                lists_data[column] = values
                
                # Usar o mapeamento para obter o tipo correto no banco de dados
                db_tipo = tipo_mapping.get(column, column)
                
                # Atualizar no banco de dados
                # Primeiro, marcar todos como inativos
                CategoriaLista.query.filter_by(tipo=db_tipo).update({CategoriaLista.ativo: False})
                
                # Depois, atualizar ou criar cada item
                for value in values:
                    # Para segmentos e domínios, precisamos manter o formato hierárquico
                    if column == 'segmento' or column == 'dominio':
                        # Buscar todos os itens existentes para este tipo
                        existing_items = CategoriaLista.query.filter_by(tipo=db_tipo, ativo=True).all()
                        
                        # Verificar se o valor já existe em algum item
                        found = False
                        for item in existing_items:
                            if '|' in item.valor:
                                parts = item.valor.split('|')
                                if (column == 'segmento' and len(parts) >= 2 and parts[1] == value) or \
                                   (column == 'dominio' and len(parts) >= 3 and parts[2] == value):
                                    item.ativo = True
                                    found = True
                                    break
                        
                        # Se não encontrou, criar um novo item com o formato hierárquico
                        if not found:
                            # Para segmentos, precisamos de uma macroárea
                            if column == 'segmento':
                                # Usar a primeira macroárea disponível
                                macroáreas = CategoriaLista.query.filter_by(tipo='macroárea', ativo=True).all()
                                if macroáreas:
                                    macroárea = macroáreas[0].valor
                                    novo_valor = f"{macroárea}|{value}"
                                    nova_lista = CategoriaLista(tipo=db_tipo, valor=novo_valor, ativo=True)
                                    db.session.add(nova_lista)
                            
                            # Para domínios, precisamos de uma macroárea e um segmento
                            elif column == 'dominio':
                                # Usar a primeira combinação de macroárea e segmento disponível
                                segmentos = CategoriaLista.query.filter_by(tipo='segmento', ativo=True).all()
                                if segmentos:
                                    for segmento in segmentos:
                                        if '|' in segmento.valor:
                                            parts = segmento.valor.split('|')
                                            if len(parts) >= 2:
                                                macroárea = parts[0]
                                                segmento_nome = parts[1]
                                                novo_valor = f"{macroárea}|{segmento_nome}|{value}"
                                                nova_lista = CategoriaLista(tipo=db_tipo, valor=novo_valor, ativo=True)
                                                db.session.add(nova_lista)
                                                break
                    else:
                        # Para outros tipos, atualizar ou criar normalmente
                        lista = CategoriaLista.query.filter_by(tipo=db_tipo, valor=value).first()
                        if lista:
                            lista.ativo = True
                        else:
                            nova_lista = CategoriaLista(tipo=db_tipo, valor=value, ativo=True)
                            db.session.add(nova_lista)
            
            db.session.commit()
            flash('Listas atualizadas com sucesso!', 'success')
            return redirect(url_for('main.lists'))
        
        # Para GET, obter listas de categorias
        organized_lists = {}
        
        # Mapeamento de tipos para consulta no banco de dados
        tipo_mapping = {
            'microarea': 'macroárea',
            'segmento': 'segmento',
            'dominio': 'dominio'
        }
        
        for column in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
            # Usar o mapeamento para obter o tipo correto no banco de dados
            db_tipo = tipo_mapping.get(column, column)
            items = _get_categoria_lista_query().filter_by(tipo=db_tipo, ativo=True).all()
            
            # Para segmentos e domínios, extrair apenas a parte relevante do valor
            if column == 'segmento' or column == 'dominio':
                values = []
                for item in items:
                    if '|' in item.valor:
                        parts = item.valor.split('|')
                        if column == 'segmento' and len(parts) >= 2:
                            # Extrair apenas o nome do segmento
                            segmento = parts[1]
                            if segmento not in values:
                                values.append(segmento)
                        elif column == 'dominio' and len(parts) >= 3:
                            # Extrair apenas o nome do domínio
                            dominio = parts[2]
                            if dominio not in values:
                                values.append(dominio)
                    else:
                        # Se não tiver o formato esperado, usar o valor completo
                        if item.valor not in values:
                            values.append(item.valor)
                organized_lists[column] = values
            else:
                # Para outros tipos, usar o valor completo
                organized_lists[column] = [item.valor for item in items]
        
        return render_template('lists.html', categories_lists=organized_lists)
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'error')
        logger.error(f"Erro nas listas: {str(e)}")
        return redirect(url_for('main.projects'))

# Função para verificar se um projeto tem classificações salvas pelo usuário
def has_user_saved_data(project_id):
    """
    Verifica se um projeto tem classificações salvas por um usuário (não pelo sistema).
    
    Args:
        project_id: ID do projeto a verificar
        
    Returns:
        bool: True se o projeto tem classificações salvas pelo usuário, False caso contrário
    """
    try:
        # Verificar se há logs indicando que o usuário modificou os dados
        user_modified_logs = Log.query.filter_by(
            id_projeto=project_id,
            usuario_modificou=True
        ).count()
        
        if user_modified_logs > 0:
            return True
            
        # Verificar se há avaliações da IA feitas por humanos
        human_ratings = AIRating.query.filter(
            AIRating.id_projeto == project_id,
            AIRating.user_id != 'sistema.automatico@embrapii.org.br'
        ).count()
        
        if human_ratings > 0:
            return True
            
        # Verificar se há categoria definida e não é apenas sugestão da IA
        categoria = Categoria.query.filter_by(id_projeto=project_id).first()
        if categoria:
            # Se há registro em Categoria, considerar como salvo pelo usuário
            # já que a inserção em Categoria só ocorre quando o usuário salva
            return True
            
        return False
    except Exception as e:
        logger.error(f"Erro ao verificar dados salvos pelo usuário: {str(e)}")
        return False
