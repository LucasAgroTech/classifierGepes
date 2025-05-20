"""
RAG Integration for gepesClassifier
Handles the retrieval and generation of responses using OpenAI API
"""

import os
import json
import re
import hashlib
import time
from datetime import datetime
from functools import lru_cache
from flask import current_app
import openai
from sqlalchemy import text
from app import db
from app.models import (
    Projeto, Categoria, TecnologiaVerde, CategoriaLista,
    ClassificacaoAdicional, Log, AISuggestion, AIRating, Usuario
)

class SimpleCache:
    """Implementação simples de cache para respostas"""
    def __init__(self, max_size=100, ttl=3600):  # TTL: 1 hora por padrão
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def _generate_key(self, query):
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def get(self, query):
        key = self._generate_key(query)
        if key in self.cache:
            item = self.cache[key]
            if time.time() - item['timestamp'] < self.ttl:
                current_app.logger.info(f"Cache hit for query: {query}")
                return item['data']
            else:
                del self.cache[key]  # Cache expirado
        return None
    
    def set(self, query, data):
        key = self._generate_key(query)
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        
        # Limitar tamanho do cache
        if len(self.cache) > self.max_size:
            oldest_key = min(self.cache, key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        current_app.logger.info(f"Added to cache: {query}")

class QueryAnalyzer:
    """Analisador de consultas para determinar o tipo e complexidade da consulta"""
    def __init__(self):
        # Padrões para identificar tipos de consultas
        self.query_patterns = {
            "estatistica": [
                r'estatística', r'dashboard', r'número', r'quantidade',
                r'total de', r'percentual', r'quanto'
            ],
            "projeto": [
                r'projeto', r'categorizar', r'classificar', r'buscar',
                r'encontrar', r'pesquisar'
            ],
            "tecnologia_verde": [
                r'tecnologia verde', r'tecverde', r'verde', r'sustentável',
                r'ambiental', r'classe'
            ],
            "categoria": [
                r'categoria', r'taxonomia', r'classificação', r'macroárea',
                r'segmento', r'domínio'
            ],
            "sugestao_ia": [
                r'sugere', r'sugestão', r'recomendação', r'ia', r'inteligência artificial',
                r'rating', r'avaliação'
            ],
            "usuario_comparacao": [
                r'usuário', r'usuários', r'colega', r'colegas', r'comparar',
                r'comparação', r'ranking', r'desempenho', r'classificou', r'contribuíram',
                r'contribuição', r'atividade', r'eu versus', r'eu vs', r'meu ranking',
                r'minha classificação', r'minha posição', r'minhas estatísticas',
                r'meu desempenho', r'como estou', r'quem mais', r'mais ativo',
                r'classificações feitas', r'fez mais', r'quantas classificações', r'quantos projetos'
            ]
        }
    
    def analyze_query(self, query):
        """Analisa a consulta para determinar seu tipo e complexidade"""
        query_lower = query.lower()
        
        # Determina o tipo da consulta
        query_types = {}
        for type_name, patterns in self.query_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, query_lower))
            query_types[type_name] = matches / len(patterns) if matches > 0 else 0
        
        # Determina o tipo principal da consulta
        primary_type = max(query_types, key=query_types.get)
        
        # Estima a complexidade da consulta
        complexity = self._estimate_complexity(query_lower)
        
        return {
            "primary_type": primary_type,
            "type_scores": query_types,
            "complexity": complexity
        }
    
    def _estimate_complexity(self, query):
        """Estima a complexidade da consulta de 0.0 a 1.0"""
        # Fatores que indicam complexidade
        length_factor = min(1.0, len(query.split()) / 20)
        
        # Contagem de fatores de complexidade
        comparison_words = ['comparar', 'versus', 'vs', 'diferença', 'entre', 'maior', 'menor']
        comparison_factor = sum(1 for word in comparison_words if word in query) * 0.1
        
        aggregation_words = ['média', 'total', 'percentual', 'máximo', 'mínimo', 'soma']
        aggregation_factor = sum(1 for word in aggregation_words if word in query) * 0.1
        
        temporal_words = ['quando', 'período', 'data', 'entre', 'antes', 'depois', 'durante']
        temporal_factor = sum(1 for word in temporal_words if word in query) * 0.05
        
        # Conjunções que indicam consultas mais complexas
        conjunction_factor = (query.count(' e ') + query.count(' ou ')) * 0.1
        
        # Cálculo da complexidade final
        complexity = length_factor + comparison_factor + aggregation_factor + temporal_factor + conjunction_factor
        return min(1.0, complexity)  # Limita a 1.0

class RAGAssistant:
    def __init__(self):
        """Initialize the RAG Assistant"""
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Modelos disponíveis com base na complexidade
        self.models = {
            "light": "gpt-3.5-turbo",      # Para consultas simples
            "standard": "gpt-4o",          # Equilíbrio custo-desempenho
            "advanced": "gpt-4-turbo"      # Para consultas complexas
        }
        self.default_model = "gpt-4-turbo"  # Compatibilidade com código existente
        
        # Componentes auxiliares
        self.cache = SimpleCache()
        self.query_analyzer = QueryAnalyzer()
        
        # Configurações do sistema
        self.system_prompt = self._get_system_prompt()
        
        # Contador de uso para monitoramento
        self.usage_stats = {
            "total_calls": 0,
            "cache_hits": 0,
            "model_usage": {model: 0 for model in self.models.values()}
        }
    
    def _get_system_prompt(self):
        """Get the system prompt for the assistant"""
        return """
        Você é um assistente especializado do sistema gepesClassifier, projetado para ajudar usuários a entender e navegar pelo sistema.
        
        INSTRUÇÕES IMPORTANTES:
        
        1. Seja OBJETIVO e CONCISO em suas respostas.
        2. Priorize DADOS ESPECÍFICOS quando disponíveis.
        3. Formate números em negrito para destaque (usando ** para markdown).
        4. Use listas quando apropriado para facilitar a leitura.
        5. Se perguntado sobre estatísticas, SEMPRE forneça os números exatos.
        6. Evite introduções longas ou contexto desnecessário.
        
        Você tem acesso a informações sobre:
        1. Projetos e suas categorias
        2. Tecnologias verdes
        3. Classificações e taxonomias
        4. Estatísticas detalhadas do sistema
        
        Quando não souber a resposta, admita isso claramente e sugira como o usuário pode obter a informação.
        """
    
    def get_response(self, user_message, conversation_history=None, user_info=None):
        """
        Get a response from the RAG assistant
        
        Args:
            user_message (str): The user's message
            conversation_history (list): Previous messages in the conversation
            user_info (dict): Information about the current user
            
        Returns:
            str: The assistant's response
        """
        if conversation_history is None:
            conversation_history = []
        
        # Verifica cache para consultas repetidas
        cached_response = self.cache.get(user_message)
        if cached_response:
            self.usage_stats["cache_hits"] += 1
            return cached_response
        
        # Analisa a consulta para determinar tipo e complexidade
        query_analysis = self.query_analyzer.analyze_query(user_message)
        
        # Busca específica por projetos
        if query_analysis["primary_type"] == "projeto" and any(term in user_message.lower() for term in ['buscar', 'encontrar', 'pesquisar']):
            # Extrai os termos de busca
            search_terms = re.sub(r'buscar|encontrar|pesquisar|projeto[s]?', '', user_message.lower(), flags=re.IGNORECASE).strip()
            if search_terms:
                project_info = self.search_project(search_terms)
                self.cache.set(user_message, project_info)
                return project_info
        
        # Seleciona o modelo apropriado com base na complexidade
        selected_model = self._select_model(query_analysis)
        
        # Retrieve relevant information from the database based on the user's query
        context = self._retrieve_enhanced_context(user_message, query_analysis, user_info)
        
        # Add user information to the system prompt if available
        system_content = self.system_prompt
        if user_info:
            user_context = f"""
            INFORMAÇÕES DO USUÁRIO:
            Nome: {user_info.get('nome', 'Usuário')}
            Email: {user_info.get('email', 'Não disponível')}
            
            Por favor, sempre se dirija ao usuário pelo nome quando apropriado.
            """
            system_content = system_content + "\n\n" + user_context
        
        # Prepare messages for the API call
        messages = [
            {"role": "system", "content": system_content + "\n\n" + context}
        ]
        
        # Add relevant conversation history (limitado a 5 mensagens para economia de tokens)
        for msg in conversation_history[-5:]:
            messages.append(msg)
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Ajusta a temperatura e tokens com base na complexidade
            temperature = max(0.3, min(0.7, 0.3 + query_analysis["complexity"] * 0.4))
            max_tokens = 500 if query_analysis["complexity"] < 0.5 else 1000
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Atualiza estatísticas de uso
            self.usage_stats["total_calls"] += 1
            self.usage_stats["model_usage"][selected_model] += 1
            
            # Extract and return the assistant's message
            answer = response.choices[0].message.content
            
            # Armazena no cache
            self.cache.set(user_message, answer)
            
            return answer
        except Exception as e:
            current_app.logger.error(f"Error calling OpenAI API: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde."
    
    def _select_model(self, query_analysis):
        """Seleciona o modelo apropriado com base na análise da consulta"""
        complexity = query_analysis["complexity"]
        primary_type = query_analysis["primary_type"]
        
        # Consultas simples usam o modelo mais leve
        if complexity < 0.4 or primary_type == "projeto":
            return self.models["light"]
        
        # Consultas de complexidade média usam o modelo padrão
        elif complexity < 0.7:
            return self.models["standard"]
        
        # Consultas complexas usam o modelo avançado
        else:
            return self.models["advanced"]
    
    def _retrieve_enhanced_context(self, query, query_analysis, user_info=None):
        """
        Recupera contexto relevante baseado na análise da consulta
        
        Args:
            query (str): The user's query
            query_analysis (dict): Query type and complexity analysis
            user_info (dict): Information about the current user
            
        Returns:
            str: Context information to include in the prompt
        """
        context_parts = []
        primary_type = query_analysis["primary_type"]
        type_scores = query_analysis["type_scores"]
        
        # Sempre inclui visão geral do sistema
        context_parts.append(self._get_system_overview())
        
        # Adiciona contexto específico com base no tipo de consulta
        if primary_type == "estatistica" or type_scores["estatistica"] > 0.3:
            context_parts.append(self._get_enhanced_statistics_info(query))
        
        if primary_type == "projeto" or type_scores["projeto"] > 0.3:
            context_parts.append(self._get_projects_info())
        
        if primary_type == "tecnologia_verde" or type_scores["tecnologia_verde"] > 0.3:
            context_parts.append(self._get_enhanced_tecverde_info(query))
        
        if primary_type == "categoria" or type_scores["categoria"] > 0.3:
            context_parts.append(self._get_categories_info())
        
        if primary_type == "sugestao_ia" or type_scores["sugestao_ia"] > 0.3:
            context_parts.append(self._get_ai_suggestions_info())
            
        if primary_type == "usuario_comparacao" or type_scores["usuario_comparacao"] > 0.3:
            context_parts.append(self._get_user_comparison_info(query, user_info))
        
        # Se nenhum contexto específico foi adicionado além da visão geral,
        # adiciona informações gerais
        if len(context_parts) == 1:
            context_parts.append(self._get_general_info())
        
        return "\n\n".join(context_parts)
    
    def _get_ai_suggestions_info(self):
        """Obtém informações específicas sobre sugestões da IA"""
        try:
            # Consultas otimizadas para estatísticas de IA
            with db.engine.connect() as connection:
                # Total de sugestões e sugestões de tecnologia verde
                ai_stats_result = connection.execute(text("""
                    SELECT 
                        COUNT(*) AS total_suggestions,
                        SUM(CASE WHEN tecverde_se_aplica = true THEN 1 ELSE 0 END) AS tecverde_suggestions
                    FROM gepes.ai_suggestions
                """))
                ai_stats_row = ai_stats_result.fetchone()
                # Convert Row to dict explicitly
                ai_stats = {}
                if ai_stats_row:
                    ai_stats = {"total_suggestions": ai_stats_row[0], "tecverde_suggestions": ai_stats_row[1]}
                
                # Avaliações médias
                ratings_result = connection.execute(text("""
                    SELECT 
                        'aia' as tipo,
                        COUNT(*) as total,
                        AVG(rating) as avg_rating,
                        SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as positive_ratings
                    FROM gepes.ai_ratings
                    WHERE tipo = 'aia'
                    UNION ALL
                    SELECT 
                        'tecverde' as tipo,
                        COUNT(*) as total,
                        AVG(rating) as avg_rating,
                        SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as positive_ratings
                    FROM gepes.ai_ratings
                    WHERE tipo = 'tecverde'
                """))
                
                ratings = {}
                for row in ratings_result:
                    ratings[row[0]] = {
                        'total': row[1],
                        'avg_rating': row[2],
                        'positive_ratings': row[3],
                        'positive_rate': round(row[3] / row[1] * 100, 1) if row[1] > 0 else 0
                    }
                
                # Distribuição de confiança das sugestões
                confidence_result = connection.execute(text("""
                    SELECT 
                        confianca, 
                        COUNT(*) AS total
                    FROM gepes.ai_suggestions
                    WHERE confianca IS NOT NULL
                    GROUP BY confianca
                    ORDER BY COUNT(*) DESC
                """))
                
                confidence_stats = []
                for row in confidence_result:
                    confidence_stats.append(f"- {row[0]}: {row[1]} sugestões")
            
            return f"""
            INFORMAÇÕES SOBRE SUGESTÕES DA IA:
            
            Total de sugestões geradas pela IA: {ai_stats.get('total_suggestions', 0)}
            Projetos sugeridos como tecnologia verde: {ai_stats.get('tecverde_suggestions', 0)}
            
            Avaliações das sugestões:
            - AIA: Média {ratings.get('aia', {}).get('avg_rating', 0):.2f}/5 ({ratings.get('aia', {}).get('positive_rate', 0)}% positivas)
            - TecVerde: Média {ratings.get('tecverde', {}).get('avg_rating', 0):.2f}/5 ({ratings.get('tecverde', {}).get('positive_rate', 0)}% positivas)
            
            Distribuição de confiança das sugestões:
            {chr(10).join(confidence_stats)}
            
            A IA fornece sugestões para:
            - Categorização em Áreas de Interesse de Aplicação (AIA)
            - Identificação de Tecnologias Verdes
            
            Usuários podem avaliar as sugestões da IA e fornecer feedback para melhorar o sistema.
            """
        except Exception as e:
            current_app.logger.error(f"Error retrieving AI suggestions info: {str(e)}")
            return "INFORMAÇÕES SOBRE SUGESTÕES DA IA: Dados não disponíveis no momento."
    
    def _get_enhanced_statistics_info(self, query):
        """Obtém estatísticas detalhadas baseadas na consulta"""
        try:
            # Verifica se a consulta é sobre uma estatística específica
            detailed_stats = {}
            
            if "tecnologia verde" in query.lower() or "tecverde" in query.lower():
                # Estatísticas específicas de tecnologia verde
                with db.engine.connect() as connection:
                    tecverde_stats_result = connection.execute(text("""
                        SELECT
                            COUNT(*) AS total_tecverde,
                            COUNT(DISTINCT p.id) AS unique_projects,
                            COUNT(DISTINCT CASE WHEN tv.classe IS NOT NULL THEN tv.id END) AS with_class,
                            COUNT(DISTINCT CASE WHEN tv.subclasse IS NOT NULL THEN tv.id END) AS with_subclass
                        FROM gepes.tecnologias_verdes tv
                        JOIN gepes.projetos p ON tv.id_projeto = p.id
                        WHERE tv.se_aplica = true
                    """))
                    tv_stats_row = tecverde_stats_result.fetchone()
                    # Convert Row to dict explicitly
                    tv_stats = {}
                    if tv_stats_row:
                        tv_stats = {
                            "total_tecverde": tv_stats_row[0],
                            "unique_projects": tv_stats_row[1],
                            "with_class": tv_stats_row[2],
                            "with_subclass": tv_stats_row[3]
                        }
                    
                    # Distribuição por classe
                    tecverde_classes_result = connection.execute(text("""
                        SELECT classe, COUNT(*) 
                        FROM gepes.tecnologias_verdes 
                        WHERE se_aplica = true AND classe IS NOT NULL 
                        GROUP BY classe 
                        ORDER BY COUNT(*) DESC
                    """))
                    
                    tv_classes = []
                    for row in tecverde_classes_result:
                        tv_classes.append(f"- {row[0]}: {row[1]} projetos")
                    
                    detailed_stats["tecverde"] = {
                        "texto": f"""
                        ESTATÍSTICAS DETALHADAS DE TECNOLOGIA VERDE:
                        
                        Total de projetos com tecnologia verde: {tv_stats.get('unique_projects', 0)}
                        Projetos com classe definida: {tv_stats.get('with_class', 0)} ({round(tv_stats.get('with_class', 0)/tv_stats.get('unique_projects', 1)*100 if tv_stats.get('unique_projects', 0) > 0 else 0, 1)}%)
                        Projetos com subclasse definida: {tv_stats.get('with_subclass', 0)} ({round(tv_stats.get('with_subclass', 0)/tv_stats.get('unique_projects', 1)*100 if tv_stats.get('unique_projects', 0) > 0 else 0, 1)}%)
                        
                        Distribuição por classe:
                        {chr(10).join(tv_classes[:10])}
                        """,
                        "prioridade": 1
                    }
            
            if "sugestão" in query.lower() or "ia" in query.lower():
                # Já temos essa informação na função específica
                detailed_stats["sugestao_ia"] = {
                    "texto": self._get_ai_suggestions_info(),
                    "prioridade": 1
                }
            
            # Obter estatísticas básicas para todos os casos
            with db.engine.connect() as connection:
                # Consulta otimizada para obter todas as estatísticas básicas de uma vez
                stats_result = connection.execute(text("""
                    WITH stats AS (
                        SELECT 
                            (SELECT COUNT(*) FROM gepes.projetos) AS total_projects,
                            (SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.categorias c ON p.id = c.id_projeto) AS categorized_projects,
                            (SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.tecnologias_verdes tv ON p.id = tv.id_projeto WHERE tv.se_aplica = true) AS tecverde_projects,
                            (SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.ai_suggestions ais ON p.id = ais.id_projeto) AS ai_suggested_projects,
                            (SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.categorias c ON p.id = c.id_projeto WHERE p.ai_rating_aia_user IS NOT NULL) AS human_validated_projects
                    )
                    SELECT * FROM stats
                """))
                
                stats_row = stats_result.fetchone()
                # Convert Row to dict explicitly
                stats = {}
                if stats_row:
                    stats = {
                        "total_projects": stats_row[0],
                        "categorized_projects": stats_row[1],
                        "tecverde_projects": stats_row[2],
                        "ai_suggested_projects": stats_row[3],
                        "human_validated_projects": stats_row[4]
                    }
                
                # Calcular estatísticas derivadas
                ai_classified = stats.get('categorized_projects', 0) - stats.get('human_validated_projects', 0)
                uncategorized = stats.get('total_projects', 0) - stats.get('categorized_projects', 0)
            
            # Formatar estatísticas básicas
            basic_stats = f"""
            ESTATÍSTICAS BÁSICAS DO SISTEMA:
            
            Total de projetos: {stats.get('total_projects', 0)}
            Projetos categorizados: {stats.get('categorized_projects', 0)} ({round(stats.get('categorized_projects', 0)/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            Projetos com tecnologia verde: {stats.get('tecverde_projects', 0)} ({round(stats.get('tecverde_projects', 0)/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            Projetos com sugestões da IA: {stats.get('ai_suggested_projects', 0)} ({round(stats.get('ai_suggested_projects', 0)/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            
            Distribuição por status:
            - Validado por humano: {stats.get('human_validated_projects', 0)} ({round(stats.get('human_validated_projects', 0)/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            - Classificado por IA: {ai_classified} ({round(ai_classified/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            - Não classificado: {uncategorized} ({round(uncategorized/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            """
            
            # Montar resultado final priorizando estatísticas detalhadas
            result = []
            
            # Adicionar estatísticas detalhadas em ordem de prioridade
            if detailed_stats:
                sorted_stats = sorted(detailed_stats.values(), key=lambda x: x["prioridade"])
                for stat in sorted_stats:
                    result.append(stat["texto"])
            
            # Adicionar estatísticas básicas
            result.append(basic_stats)
            
            return "\n\n".join(result)
        except Exception as e:
            current_app.logger.error(f"Error retrieving enhanced statistics: {str(e)}")
            return "ESTATÍSTICAS DO SISTEMA: Dados não disponíveis no momento."
    
    def _get_enhanced_tecverde_info(self, query):
        """Obtém informações aprimoradas sobre tecnologias verdes"""
        try:
            # Obter classes de tecnologia verde - CORRIGIDO: não tenta obter a coluna "descricao"
            tecverde_classes = []
            categoria_lista_query = db.session.query(CategoriaLista.valor)\
                .filter(CategoriaLista.tipo == 'tecverde_classe')\
                .filter(CategoriaLista.ativo == True)\
                .all()
            
            for cl in categoria_lista_query:
                tecverde_classes.append(cl.valor)
            
            classes_info = []
            for classe in tecverde_classes:
                classes_info.append(f"- {classe}")
            
            # Se não houver classes no banco, usar valores estáticos para exemplo
            if not classes_info:
                default_classes = ["Energias alternativas", "Gestão Ambiental", "Transporte", 
                                  "Conservação", "Agricultura Sustentável"]
                classes_info = [f"- {c}" for c in default_classes]
            
            # Obter estatísticas específicas sobre tecnologias verdes
            with db.engine.connect() as connection:
                # Total de tecnologias verdes e distribuição por classe
                tecverde_stats_result = connection.execute(text("""
                    SELECT 
                        COUNT(*) AS total_tecverde,
                        COUNT(DISTINCT CASE WHEN classe IS NOT NULL THEN id END) AS with_class,
                        COUNT(DISTINCT CASE WHEN subclasse IS NOT NULL THEN id END) AS with_subclass
                    FROM gepes.tecnologias_verdes
                    WHERE se_aplica = true
                """))
                tv_stats_row = tecverde_stats_result.fetchone()
                # Convert Row to dict explicitly
                tv_stats = {}
                if tv_stats_row:
                    tv_stats = {
                        "total_tecverde": tv_stats_row[0],
                        "with_class": tv_stats_row[1],
                        "with_subclass": tv_stats_row[2]
                    }
                
                # Top projetos com tecnologia verde por avaliação
                top_rated_result = connection.execute(text("""
                    SELECT 
                        p.titulo, 
                        tv.classe, 
                        p.nota_avaliacao
                    FROM gepes.projetos p
                    JOIN gepes.tecnologias_verdes tv ON p.id = tv.id_projeto
                    WHERE tv.se_aplica = true AND p.nota_avaliacao IS NOT NULL
                    ORDER BY p.nota_avaliacao DESC
                    LIMIT 5
                """))
                
                top_rated = []
                for row in top_rated_result:
                    top_rated.append(f"- {row[0]} (Classe: {row[1] or 'Não definida'}, Nota: {row[2]})")
            
            # Detectar solicitações específicas
            detailed_info = ""
            
            if "top" in query.lower() or "melhor" in query.lower():
                detailed_info = f"""
                TOP PROJETOS DE TECNOLOGIA VERDE POR AVALIAÇÃO:
                {chr(10).join(top_rated)}
                """
            
            # Informações gerais
            general_info = f"""
            INFORMAÇÕES SOBRE TECNOLOGIAS VERDES:
            
            Tecnologias verdes são soluções que contribuem para a sustentabilidade ambiental.
            
            Total de projetos com tecnologia verde: {tv_stats.get('total_tecverde', 0)}
            Com classe definida: {tv_stats.get('with_class', 0)} ({round(tv_stats.get('with_class', 0)/tv_stats.get('total_tecverde', 1)*100 if tv_stats.get('total_tecverde', 0) > 0 else 0, 1)}%)
            Com subclasse definida: {tv_stats.get('with_subclass', 0)} ({round(tv_stats.get('with_subclass', 0)/tv_stats.get('total_tecverde', 1)*100 if tv_stats.get('total_tecverde', 0) > 0 else 0, 1)}%)
            
            Classes de tecnologias verdes no sistema:
            {chr(10).join(classes_info)}
            
            Cada tecnologia verde pode ter uma classe e subclasse específica.
            A classificação de tecnologia verde pode ser feita manualmente ou com sugestões da IA.
            """
            
            # Combinar informações
            if detailed_info:
                return detailed_info + "\n\n" + general_info
            else:
                return general_info
        except Exception as e:
            current_app.logger.error(f"Error retrieving enhanced tecverde info: {str(e)}")
            return "INFORMAÇÕES SOBRE TECNOLOGIAS VERDES: Dados não disponíveis no momento."
    
    # Métodos existentes mantidos para compatibilidade
    def _get_system_overview(self):
        """Get general system overview"""
        return """
        VISÃO GERAL DO SISTEMA:
        
        O gepesClassifier é um sistema para classificação e categorização de projetos da Embrapii.
        O sistema permite categorizar projetos em áreas de interesse de aplicação (AIA) e identificar tecnologias verdes.
        
        Principais funcionalidades:
        - Visualização e filtragem de projetos
        - Categorização manual de projetos
        - Sugestões de categorização por IA
        - Identificação de tecnologias verdes
        - Dashboard com estatísticas e visualizações
        """
    
    def _get_projects_info(self):
        """Get information about projects"""
        try:
            # Consulta SQL otimizada para obter todas as contagens de uma vez
            with db.engine.connect() as connection:
                projects_stats_result = connection.execute(text("""
                    SELECT 
                        (SELECT COUNT(*) FROM gepes.projetos) AS total_projects,
                        (SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.categorias c ON p.id = c.id_projeto) AS categorized_projects,
                        (SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.tecnologias_verdes tv ON p.id = tv.id_projeto WHERE tv.se_aplica = true) AS tecverde_projects
                    
                """))
                
                # CORRIGIDO: Usar índices numéricos para obter valores da linha
                stats_row = projects_stats_result.fetchone()
                stats = {}
                if stats_row:  # Check if row exists before processing
                    stats = {
                        "total_projects": stats_row[0],
                        "categorized_projects": stats_row[1],
                        "tecverde_projects": stats_row[2]
                    }
                else:
                    # Default values if query returns no results
                    stats = {
                        "total_projects": 0,
                        "categorized_projects": 0,
                        "tecverde_projects": 0
                    }
                    
                total_projects = stats.get("total_projects", 0)
                categorized_projects = stats.get("categorized_projects", 0)
                tecverde_projects = stats.get("tecverde_projects", 0)
            
            # Get recent projects with improved efficiency
            with db.engine.connect() as connection:
                recent_projects_result = connection.execute(
                    text("""
                    SELECT titulo, codigo_projeto, data_criacao 
                    FROM gepes.projetos 
                    ORDER BY data_criacao DESC 
                    LIMIT 5
                    """)
                )
                
                recent_projects_info = []
                for row in recent_projects_result:
                    data_criacao = row[2].strftime('%d/%m/%Y') if row[2] else 'Data não disponível'
                    recent_projects_info.append(f"- {row[0]} (Código: {row[1]}, Adicionado: {data_criacao})")
            
            return f"""
            INFORMAÇÕES SOBRE PROJETOS:
            
            Total de projetos no sistema: {total_projects}
            Projetos categorizados: {categorized_projects} ({round(categorized_projects/total_projects*100 if total_projects > 0 else 0, 1)}%)
            Projetos com tecnologia verde: {tecverde_projects} ({round(tecverde_projects/total_projects*100 if total_projects > 0 else 0, 1)}%)
            
            Projetos recentes:
            {chr(10).join(recent_projects_info)}
            
            Os projetos podem ser categorizados manualmente ou com sugestões da IA.
            Cada projeto pode ter uma categoria principal e categorias adicionais.
            """
        except Exception as e:
            current_app.logger.error(f"Error retrieving projects info: {str(e)}")
            return "INFORMAÇÕES SOBRE PROJETOS: Dados não disponíveis no momento."
    
    def _get_tecverde_info(self):
        """Get information about green technologies"""
        try:
            # Get green technology classes
            tecverde_classes = db.session.query(CategoriaLista.valor)\
                .filter(CategoriaLista.tipo == 'tecverde_classe')\
                .filter(CategoriaLista.ativo == True)\
                .all()
            
            classes_info = []
            for classe in tecverde_classes:
                classes_info.append(f"- {classe[0]}")
            
            return f"""
            INFORMAÇÕES SOBRE TECNOLOGIAS VERDES:
            
            Tecnologias verdes são soluções que contribuem para a sustentabilidade ambiental.
            
            Classes de tecnologias verdes no sistema:
            {chr(10).join(classes_info)}
            
            Cada tecnologia verde pode ter uma classe e subclasse específica.
            A classificação de tecnologia verde pode ser feita manualmente ou com sugestões da IA.
            """
        except Exception as e:
            current_app.logger.error(f"Error retrieving tecverde info: {str(e)}")
            return "INFORMAÇÕES SOBRE TECNOLOGIAS VERDES: Dados não disponíveis no momento."
    
    def _get_categories_info(self):
        """Get information about categories"""
        try:
            # Consulta otimizada para categorias
            with db.engine.connect() as connection:
                # Obter categorias e contagens em uma única consulta
                categorias_result = connection.execute(text("""
                    WITH categoria_counts AS (
                        SELECT 
                            cl.tipo, 
                            cl.valor, 
                            COUNT(c.id) AS count
                        FROM gepes.categoria_listas cl
                        LEFT JOIN gepes.categorias c ON 
                            (cl.tipo = 'macroárea' AND cl.valor = c.microarea) OR
                            (cl.tipo = 'segmento' AND cl.valor = c.segmento) OR
                            (cl.tipo = 'dominio' AND cl.valor = c.dominio)
                        WHERE cl.ativo = true
                        GROUP BY cl.tipo, cl.valor
                    )
                    SELECT 
                        tipo, 
                        valor, 
                        count,
                        ROW_NUMBER() OVER (PARTITION BY tipo ORDER BY count DESC, valor) as rank
                    FROM categoria_counts
                    ORDER BY tipo, count DESC, valor
                """))
                
                # Organizar resultados por tipo
                categorias = {"microarea": [], "segmento": [], "dominio": []}
                for row in categorias_result:
                    tipo, valor, count, rank = row
                    if tipo in categorias and rank <= 10:  # Limitar a 10 por tipo
                        suffix = f" ({count} projetos)" if count > 0 else ""
                        categorias[tipo].append(f"- {valor}{suffix}")
            
            # Informações sobre a taxonomia
            taxonomia_info = """
            O sistema utiliza uma taxonomia de três níveis para categorizar projetos:
            1. Macroárea (Nível 1)
            2. Segmento (Nível 2) 
            3. Domínio (Nível 3)
            """
            
            # Formatar seções para cada tipo de categoria
            macroreas_section = """
            Macroáreas disponíveis:
            {}
            """.format(chr(10).join(categorias["microarea"]))
            
            segmentos_section = """
            Top segmentos:
            {}
            """.format(chr(10).join(categorias["segmento"]))
            
            # Combinar informações
            return f"""
            INFORMAÇÕES SOBRE CATEGORIAS:
            
            {taxonomia_info}
            
            {macroreas_section}
            
            {segmentos_section}
            
            Cada projeto pode ter uma categoria principal e categorias adicionais.
            """
        except Exception as e:
            current_app.logger.error(f"Error retrieving categories info: {str(e)}")
            return "INFORMAÇÕES SOBRE CATEGORIAS: Dados não disponíveis no momento."
    
    def _get_statistics_info(self):
        """Get statistical information"""
        try:
            # Consulta SQL otimizada para obter todas as estatísticas em uma única chamada
            with db.engine.connect() as connection:
                stats_result = connection.execute(text("""
                    SELECT 
                        (SELECT COUNT(*) FROM gepes.projetos) AS total_projects,
                        (SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.categorias c ON p.id = c.id_projeto) AS categorized_projects,
                        (SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.tecnologias_verdes tv ON p.id = tv.id_projeto WHERE tv.se_aplica = true) AS tecverde_projects,
                        (SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.ai_suggestions ais ON p.id = ais.id_projeto) AS ai_suggested_projects,
                        (SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.categorias c ON p.id = c.id_projeto WHERE p.ai_rating_aia_user IS NOT NULL) AS human_validated_projects
                """))
                
                stats_row = stats_result.fetchone()
                # Convert Row to dict explicitly
                stats = {}
                if stats_row:
                    stats = {
                        "total_projects": stats_row[0],
                        "categorized_projects": stats_row[1],
                        "tecverde_projects": stats_row[2],
                        "ai_suggested_projects": stats_row[3],
                        "human_validated_projects": stats_row[4]
                    }
                
                # Calcular estatísticas derivadas
                ai_classified = stats.get('categorized_projects', 0) - stats.get('human_validated_projects', 0)
                uncategorized = stats.get('total_projects', 0) - stats.get('categorized_projects', 0)
            
            return f"""
            ESTATÍSTICAS DO SISTEMA:
            
            Total de projetos: {stats.get('total_projects', 0)}
            Projetos categorizados: {stats.get('categorized_projects', 0)} ({round(stats.get('categorized_projects', 0)/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            Projetos com tecnologia verde: {stats.get('tecverde_projects', 0)} ({round(stats.get('tecverde_projects', 0)/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            Projetos com sugestões da IA: {stats.get('ai_suggested_projects', 0)} ({round(stats.get('ai_suggested_projects', 0)/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            
            Distribuição por status:
            - Validado por humano: {stats.get('human_validated_projects', 0)} ({round(stats.get('human_validated_projects', 0)/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            - Classificado por IA: {ai_classified} ({round(ai_classified/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            - Não classificado: {uncategorized} ({round(uncategorized/stats.get('total_projects', 1)*100 if stats.get('total_projects', 0) > 0 else 0, 1)}%)
            
            O dashboard do sistema apresenta estas estatísticas de forma visual, incluindo gráficos e tabelas.
            """
        except Exception as e:
            current_app.logger.error(f"Error retrieving statistics info: {str(e)}")
            return "ESTATÍSTICAS DO SISTEMA: Dados não disponíveis no momento."
    
    def _get_general_info(self):
        """Get general information about the system"""
        return """
        INFORMAÇÕES GERAIS:
        
        O gepesClassifier permite:
        
        1. Visualizar e filtrar projetos da Embrapii
        2. Categorizar projetos em áreas de interesse de aplicação (AIA)
        3. Identificar tecnologias verdes nos projetos
        4. Obter sugestões de categorização por IA
        5. Visualizar estatísticas e métricas no dashboard
        
        A categorização segue uma taxonomia de três níveis:
        - Macroárea (Nível 1)
        - Segmento (Nível 2)
        - Domínio (Nível 3)
        
        As tecnologias verdes são classificadas em classes e subclasses.
        
        O sistema mantém um histórico de atividades e permite avaliar as sugestões da IA.
        """
    
    def search_project(self, query):
        """
        Search for a specific project
        
        Args:
            query (str): The search query
            
        Returns:
            str: Information about the found project(s)
        """
        try:
            # Verifica cache
            cache_key = f"search_project:{query}"
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Consulta otimizada para busca de projetos - utilizando múltiplos critérios
            with db.engine.connect() as connection:
                search_sql = """
                WITH project_search AS (
                    SELECT 
                        p.id, p.codigo_projeto, p.titulo,
                        CASE
                            WHEN p.titulo ILIKE :exact_query THEN 10
                            WHEN p.codigo_projeto ILIKE :exact_query THEN 9
                            WHEN p.titulo ILIKE :partial_query THEN 8
                            WHEN p.codigo_projeto ILIKE :partial_query THEN 7
                            WHEN p.titulo ILIKE :broad_query THEN 6
                            WHEN p.objetivo ILIKE :partial_query THEN 5
                            WHEN p.descricao_publica ILIKE :partial_query THEN 4
                            WHEN p.objetivo ILIKE :broad_query THEN 3
                            WHEN p.descricao_publica ILIKE :broad_query THEN 2
                            ELSE 1
                        END as relevance
                    FROM gepes.projetos p
                    WHERE 
                        p.titulo ILIKE :broad_query OR
                        p.codigo_projeto ILIKE :broad_query OR
                        p.objetivo ILIKE :broad_query OR
                        p.descricao_publica ILIKE :broad_query
                )
                SELECT id, codigo_projeto, titulo
                FROM project_search
                ORDER BY relevance DESC, titulo
                LIMIT 5
                """
                
                projects_result = connection.execute(
                    text(search_sql),
                    {
                        "exact_query": query,
                        "partial_query": f"%{query}%",
                        "broad_query": f"%{' '.join(['%' + word + '%' for word in query.split()])}%"
                    }
                )
                
                projects = [
                    {"id": row[0], "codigo_projeto": row[1], "titulo": row[2]} 
                    for row in projects_result
                ]
            
            if not projects:
                result = f"Nenhum projeto encontrado com o termo '{query}'."
                self.cache.set(cache_key, result)
                return result
            
            # Consulta otimizada para obter detalhes em uma única operação
            project_ids = [p["id"] for p in projects]
            with db.engine.connect() as connection:
                details_sql = """
                SELECT 
                    p.id, 
                    c.microarea, 
                    c.segmento,
                    tv.se_aplica,
                    tv.classe,
                    p.data_criacao,
                    p.nota_avaliacao,
                    p.valor_embrapii + p.valor_empresa + COALESCE(p.valor_sebrae, 0) + p.valor_unidade_embrapii AS valor_total
                FROM gepes.projetos p
                LEFT JOIN gepes.categorias c ON p.id = c.id_projeto
                LEFT JOIN gepes.tecnologias_verdes tv ON p.id = tv.id_projeto
                WHERE p.id IN :project_ids
                """
                
                details_result = connection.execute(
                    text(details_sql),
                    {"project_ids": tuple(project_ids)}
                )
                
                project_details = {row[0]: {
                    "microarea": row[1],
                    "segmento": row[2],
                    "tecverde_se_aplica": row[3],
                    "tecverde_classe": row[4],
                    "data_criacao": row[5],
                    "nota_avaliacao": row[6],
                    "valor_total": row[7]
                } for row in details_result}
            
            # Formatar resultado
            result = f"**Projetos encontrados com o termo '{query}':**\n\n"
            
            for i, p in enumerate(projects, 1):
                details = project_details.get(p["id"], {})
                result += f"**{i}. {p['titulo']}**\n"
                result += f"Código: {p['codigo_projeto']}\n"
                
                if details.get("microarea") and details.get("segmento"):
                    result += f"Categoria: {details['microarea']} > {details['segmento']}\n"
                
                if details.get("tecverde_se_aplica") is not None:
                    result += f"Tecnologia Verde: {'Sim' if details['tecverde_se_aplica'] else 'Não'}"
                    if details['tecverde_se_aplica'] and details.get('tecverde_classe'):
                        result += f" (Classe: {details['tecverde_classe']})"
                    result += "\n"
                
                if details.get("data_criacao"):
                    result += f"Data de criação: {details['data_criacao'].strftime('%d/%m/%Y')}\n"
                
                if details.get("nota_avaliacao"):
                    result += f"Nota de avaliação: {details['nota_avaliacao']}\n"
                
                if details.get("valor_total"):
                    result += f"Valor total: R$ {details['valor_total']:,.2f}\n"
                
                result += "\n"
            
            # Armazenar no cache
            self.cache.set(cache_key, result)
            
            return result
        except Exception as e:
            current_app.logger.error(f"Error searching project: {str(e)}")
            return f"Erro ao buscar projetos com o termo '{query}'."
    
    def _get_user_comparison_info(self, query, user_info=None):
        """Obtém informações comparativas entre usuários do sistema"""
        try:
            # Extrair menção a usuário específico na consulta se houver
            import re
            user_mention = None
            user_pattern = r'usuário\s+([a-zA-Z0-9_\.\-@]+)|colega\s+([a-zA-Z0-9_\.\-@]+)'
            user_match = re.search(user_pattern, query, re.IGNORECASE)
            if user_match:
                user_mention = user_match.group(1) or user_match.group(2)
            
            current_user_email = user_info.get('email') if user_info else None
            
            # Verificar se a consulta contém referências ao próprio usuário
            self_reference_patterns = [
                r'\beu\b', r'\bmim\b', r'\bminhas?\b', r'\bmeuss?\b', 
                r'\bme\b', r'\bcomo estou\b', r'\bmeu desempenho\b'
            ]
            is_self_reference_query = any(re.search(pattern, query, re.IGNORECASE) for pattern in self_reference_patterns)
            
            with db.engine.connect() as connection:
                # Estatísticas gerais sobre atividades dos usuários
                user_stats_result = connection.execute(text("""
                    SELECT 
                        u.email,
                        u.nome,
                        COUNT(DISTINCT l.id_projeto) as total_projetos,
                        COUNT(CASE WHEN l.acao = 'classificacao_aia' THEN 1 END) as total_classificacoes_aia,
                        COUNT(CASE WHEN l.acao = 'classificacao_tecverde' THEN 1 END) as total_classificacoes_tecverde,
                        COUNT(CASE WHEN l.acao LIKE '%avaliacao_ia%' THEN 1 END) as total_avaliacoes_ia,
                        MAX(l.data_acao) as ultima_atividade
                    FROM gepes.usuarios u
                    LEFT JOIN gepes.logs l ON u.id = l.id_usuario
                    GROUP BY u.id, u.email, u.nome
                    ORDER BY COUNT(l.id) DESC
                """))
                
                users_stats = []
                user_specific_stats = None
                current_user_stats = None
                mentioned_user_stats = None
                
                for row in user_stats_result:
                    user_data = {
                        'email': row[0],
                        'nome': row[1],
                        'total_projetos': row[2] or 0,
                        'total_classificacoes_aia': row[3] or 0,
                        'total_classificacoes_tecverde': row[4] or 0,
                        'total_avaliacoes_ia': row[5] or 0,
                        'ultima_atividade': row[6].strftime('%d/%m/%Y') if row[6] else 'Nunca'
                    }
                    
                    # Identificar o usuário atual se disponível
                    if current_user_email and user_data['email'] == current_user_email:
                        current_user_stats = user_data
                    
                    users_stats.append(user_data)
                
                # Calcular médias para comparação
                total_users = len(users_stats)
                if total_users > 0:
                    avg_projects = sum(u['total_projetos'] for u in users_stats) / total_users
                    avg_aia = sum(u['total_classificacoes_aia'] for u in users_stats) / total_users
                    avg_tecverde = sum(u['total_classificacoes_tecverde'] for u in users_stats) / total_users
                    avg_ratings = sum(u['total_avaliacoes_ia'] for u in users_stats) / total_users
                else:
                    avg_projects = avg_aia = avg_tecverde = avg_ratings = 0
                
                # Identificar usuários mais ativos
                most_active_users = sorted(
                    users_stats, 
                    key=lambda u: (u['total_classificacoes_aia'] + u['total_classificacoes_tecverde']), 
                    reverse=True
                )[:5]
                
                # Verificar se há usuário mencionado na consulta
                if user_mention:
                    for user in users_stats:
                        if user_mention.lower() in user['email'].lower() or (
                            user['nome'] and user_mention.lower() in user['nome'].lower()
                        ):
                            mentioned_user_stats = user
                            break
                
                # Classificação do usuário atual
                current_user_rank = None
                if current_user_stats:
                    ranked_users = sorted(
                        users_stats,
                        key=lambda u: (u['total_classificacoes_aia'] + u['total_classificacoes_tecverde']),
                        reverse=True
                    )
                    for i, u in enumerate(ranked_users, 1):
                        if u['email'] == current_user_stats['email']:
                            current_user_rank = i
                            break
                
                # Construir resposta
                response_parts = []
                
                # Informações do usuário atual (se disponível e se a consulta for sobre si mesmo)
                if current_user_stats and is_self_reference_query:
                    current_user_total_classificacoes = current_user_stats['total_classificacoes_aia'] + current_user_stats['total_classificacoes_tecverde']
                    rank_text = f" (classificado em {current_user_rank}º lugar de {total_users})" if current_user_rank else ""
                    
                    current_user_info = f"""
                    SUAS ESTATÍSTICAS:
                    
                    Nome: {current_user_stats['nome']}
                    Email: {current_user_stats['email']}
                    Total de projetos: {current_user_stats['total_projetos']}
                    Total de classificações: {current_user_total_classificacoes}{rank_text}
                    - Classificações AIA: {current_user_stats['total_classificacoes_aia']}
                    - Classificações TecVerde: {current_user_stats['total_classificacoes_tecverde']}
                    Avaliações de IA: {current_user_stats['total_avaliacoes_ia']}
                    Última atividade: {current_user_stats['ultima_atividade']}
                    
                    COMPARAÇÃO COM A MÉDIA:
                    - Projetos: {current_user_stats['total_projetos']} vs média de {avg_projects:.1f} ({(current_user_stats['total_projetos'] / avg_projects * 100 if avg_projects > 0 else 0):.1f}% da média)
                    - Classificações AIA: {current_user_stats['total_classificacoes_aia']} vs média de {avg_aia:.1f} ({(current_user_stats['total_classificacoes_aia'] / avg_aia * 100 if avg_aia > 0 else 0):.1f}% da média)
                    - Classificações TecVerde: {current_user_stats['total_classificacoes_tecverde']} vs média de {avg_tecverde:.1f} ({(current_user_stats['total_classificacoes_tecverde'] / avg_tecverde * 100 if avg_tecverde > 0 else 0):.1f}% da média)
                    """
                    response_parts.append(current_user_info)
                
                # Resumo geral
                summary = f"""
                RESUMO DE ATIVIDADES DOS USUÁRIOS:
                
                Total de usuários no sistema: {total_users}
                Média de projetos por usuário: {avg_projects:.1f}
                Média de classificações AIA por usuário: {avg_aia:.1f}
                Média de classificações TecVerde por usuário: {avg_tecverde:.1f}
                Média de avaliações de IA por usuário: {avg_ratings:.1f}
                """
                response_parts.append(summary)
                
                # Informações do usuário atual (se disponível e a consulta não for sobre si mesmo)
                if current_user_stats and not is_self_reference_query:
                    current_user_total_classificacoes = current_user_stats['total_classificacoes_aia'] + current_user_stats['total_classificacoes_tecverde']
                    rank_text = f" (classificado em {current_user_rank}º lugar de {total_users})" if current_user_rank else ""
                    
                    current_user_info = f"""
                    SUAS ESTATÍSTICAS:
                    
                    Nome: {current_user_stats['nome']}
                    Email: {current_user_stats['email']}
                    Total de projetos: {current_user_stats['total_projetos']}
                    Total de classificações: {current_user_total_classificacoes}{rank_text}
                    - Classificações AIA: {current_user_stats['total_classificacoes_aia']}
                    - Classificações TecVerde: {current_user_stats['total_classificacoes_tecverde']}
                    Avaliações de IA: {current_user_stats['total_avaliacoes_ia']}
                    Última atividade: {current_user_stats['ultima_atividade']}
                    
                    COMPARAÇÃO COM A MÉDIA:
                    - Projetos: {current_user_stats['total_projetos']} vs média de {avg_projects:.1f} ({(current_user_stats['total_projetos'] / avg_projects * 100 if avg_projects > 0 else 0):.1f}% da média)
                    - Classificações AIA: {current_user_stats['total_classificacoes_aia']} vs média de {avg_aia:.1f} ({(current_user_stats['total_classificacoes_aia'] / avg_aia * 100 if avg_aia > 0 else 0):.1f}% da média)
                    - Classificações TecVerde: {current_user_stats['total_classificacoes_tecverde']} vs média de {avg_tecverde:.1f} ({(current_user_stats['total_classificacoes_tecverde'] / avg_tecverde * 100 if avg_tecverde > 0 else 0):.1f}% da média)
                    """
                    response_parts.append(current_user_info)
                
                # Usuários mais ativos
                active_users = """
                USUÁRIOS MAIS ATIVOS:
                """
                for i, user in enumerate(most_active_users, 1):
                    active_users += f"\n{i}. {user['nome']} ({user['email']})"
                    active_users += f"\n   Classificações: {user['total_classificacoes_aia'] + user['total_classificacoes_tecverde']}"
                    active_users += f"\n   Projetos: {user['total_projetos']}"
                    active_users += f"\n   Última atividade: {user['ultima_atividade']}"
                
                response_parts.append(active_users)
                
                # Informações específicas do usuário mencionado
                if mentioned_user_stats:
                    user_specific = f"""
                    INFORMAÇÕES DO USUÁRIO MENCIONADO:
                    
                    Usuário: {mentioned_user_stats['nome']} ({mentioned_user_stats['email']})
                    Total de projetos: {mentioned_user_stats['total_projetos']}
                    Classificações AIA: {mentioned_user_stats['total_classificacoes_aia']}
                    Classificações TecVerde: {mentioned_user_stats['total_classificacoes_tecverde']}
                    Avaliações de IA: {mentioned_user_stats['total_avaliacoes_ia']}
                    Última atividade: {mentioned_user_stats['ultima_atividade']}
                    
                    COMPARAÇÃO COM A MÉDIA:
                    - Projetos: {mentioned_user_stats['total_projetos']} vs média de {avg_projects:.1f} ({(mentioned_user_stats['total_projetos'] / avg_projects * 100 if avg_projects > 0 else 0):.1f}% da média)
                    - Classificações AIA: {mentioned_user_stats['total_classificacoes_aia']} vs média de {avg_aia:.1f} ({(mentioned_user_stats['total_classificacoes_aia'] / avg_aia * 100 if avg_aia > 0 else 0):.1f}% da média)
                    - Classificações TecVerde: {mentioned_user_stats['total_classificacoes_tecverde']} vs média de {avg_tecverde:.1f} ({(mentioned_user_stats['total_classificacoes_tecverde'] / avg_tecverde * 100 if avg_tecverde > 0 else 0):.1f}% da média)
                    """
                    
                    # Adicionar comparação com usuário atual se disponível
                    if current_user_stats and current_user_stats['email'] != mentioned_user_stats['email']:
                        user_specific += f"""
                        
                        COMPARAÇÃO COM VOCÊ:
                        - Projetos: {mentioned_user_stats['total_projetos']} vs seus {current_user_stats['total_projetos']} ({(mentioned_user_stats['total_projetos'] / max(1, current_user_stats['total_projetos']) * 100):.1f}%)
                        - Classificações AIA: {mentioned_user_stats['total_classificacoes_aia']} vs suas {current_user_stats['total_classificacoes_aia']} ({(mentioned_user_stats['total_classificacoes_aia'] / max(1, current_user_stats['total_classificacoes_aia']) * 100):.1f}%)
                        - Classificações TecVerde: {mentioned_user_stats['total_classificacoes_tecverde']} vs suas {current_user_stats['total_classificacoes_tecverde']} ({(mentioned_user_stats['total_classificacoes_tecverde'] / max(1, current_user_stats['total_classificacoes_tecverde']) * 100):.1f}%)
                        """
                    
                    response_parts.append(user_specific)
                
                return "\n\n".join(response_parts)
                
        except Exception as e:
            current_app.logger.error(f"Error retrieving user comparison info: {str(e)}")
            return "INFORMAÇÕES COMPARATIVAS DE USUÁRIOS: Dados não disponíveis no momento."

# Create a singleton instance
rag_assistant = RAGAssistant()
