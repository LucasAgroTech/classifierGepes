"""
RAG Integration for gepesClassifier
Handles the retrieval and generation of responses using OpenAI API
"""

import os
import json
from datetime import datetime
from flask import current_app
import openai
from sqlalchemy import text
from app import db
from app.models import (
    Projeto, Categoria, TecnologiaVerde, CategoriaLista,
    ClassificacaoAdicional, Log, AISuggestion, AIRating, Usuario
)

class RAGAssistant:
    def __init__(self):
        """Initialize the RAG Assistant"""
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        self.model = "gpt-4-turbo"  # Can be configured based on needs
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self):
        """Get the system prompt for the assistant"""
        return """
        Você é um assistente especializado do sistema gepesClassifier, projetado para ajudar usuários a entender e navegar pelo sistema.
        
        Você tem acesso a informações sobre:
        1. Projetos e suas categorias
        2. Tecnologias verdes
        3. Classificações e taxonomias
        4. Estatísticas do sistema
        
        Responda de forma clara, concisa e útil. Use linguagem formal mas amigável.
        
        Quando não souber a resposta, admita isso claramente e sugira como o usuário pode obter a informação por outros meios.
        
        Não invente informações. Se precisar de mais detalhes para responder adequadamente, peça ao usuário para fornecer mais contexto.
        """
    
    def get_response(self, user_message, conversation_history=None):
        """
        Get a response from the RAG assistant
        
        Args:
            user_message (str): The user's message
            conversation_history (list): Previous messages in the conversation
            
        Returns:
            str: The assistant's response
        """
        if conversation_history is None:
            conversation_history = []
        
        # Retrieve relevant information from the database based on the user's query
        context = self._retrieve_context(user_message)
        
        # Prepare messages for the API call
        messages = [
            {"role": "system", "content": self.system_prompt + "\n\n" + context}
        ]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append(msg)
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract and return the assistant's message
            return response.choices[0].message.content
        except Exception as e:
            current_app.logger.error(f"Error calling OpenAI API: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde."
    
    def _retrieve_context(self, query):
        """
        Retrieve relevant context from the database based on the user's query
        
        Args:
            query (str): The user's query
            
        Returns:
            str: Context information to include in the prompt
        """
        context_parts = []
        
        # Add system overview
        context_parts.append(self._get_system_overview())
        
        # Check if query is about projects
        if any(keyword in query.lower() for keyword in ['projeto', 'projetos', 'categorizar', 'classificar']):
            context_parts.append(self._get_projects_info())
        
        # Check if query is about green technologies
        if any(keyword in query.lower() for keyword in ['tecnologia verde', 'tecverde', 'verde', 'sustentável']):
            context_parts.append(self._get_tecverde_info())
        
        # Check if query is about categories
        if any(keyword in query.lower() for keyword in ['categoria', 'categorias', 'taxonomia', 'classificação']):
            context_parts.append(self._get_categories_info())
        
        # Check if query is about statistics
        if any(keyword in query.lower() for keyword in ['estatística', 'estatísticas', 'dashboard', 'números']):
            context_parts.append(self._get_statistics_info())
        
        # If no specific context was added, add general information
        if len(context_parts) == 1:  # Only system overview was added
            context_parts.append(self._get_general_info())
        
        return "\n\n".join(context_parts)
    
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
            # Use direct SQL queries with separate connections to avoid transaction issues
            with db.engine.connect() as connection:
                # Get total projects count
                total_projects_result = connection.execute(text("SELECT COUNT(*) FROM gepes.projetos"))
                total_projects = total_projects_result.scalar() or 0
            
            with db.engine.connect() as connection:
                # Get categorized projects count
                categorized_projects_result = connection.execute(
                    text("SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.categorias c ON p.id = c.id_projeto")
                )
                categorized_projects = categorized_projects_result.scalar() or 0
            
            with db.engine.connect() as connection:
                # Get tecverde projects count
                tecverde_projects_result = connection.execute(
                    text("SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.tecnologias_verdes tv ON p.id = tv.id_projeto WHERE tv.se_aplica = true")
                )
                tecverde_projects = tecverde_projects_result.scalar() or 0
            
            # Get recent projects
            with db.engine.connect() as connection:
                recent_projects_result = connection.execute(
                    text("SELECT titulo, codigo_projeto FROM gepes.projetos ORDER BY data_criacao DESC LIMIT 5")
                )
                recent_projects_info = []
                for row in recent_projects_result:
                    recent_projects_info.append(f"- {row[0]} (Código: {row[1]})")
            
            return f"""
            INFORMAÇÕES SOBRE PROJETOS:
            
            Total de projetos no sistema: {total_projects}
            Projetos categorizados: {categorized_projects}
            Projetos com tecnologia verde: {tecverde_projects}
            
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
            # Use direct SQL queries with separate connections to avoid transaction issues
            with db.engine.connect() as connection:
                # Get macroareas
                macroareas_result = connection.execute(
                    text("SELECT valor FROM gepes.categoria_listas WHERE tipo = 'microarea' AND ativo = true")
                )
                macroareas = [row[0] for row in macroareas_result]
                macroareas_list = [f"- {m}" for m in macroareas]
            
            # Use a separate connection for segments query
            with db.engine.connect() as connection:
                # Get some segments as examples
                segments_result = connection.execute(
                    text("SELECT valor FROM gepes.categoria_listas WHERE tipo = 'segmento' AND ativo = true LIMIT 10")
                )
                segments = [row[0] for row in segments_result]
                segments_list = [f"- {s}" for s in segments]
            
            return f"""
            INFORMAÇÕES SOBRE CATEGORIAS:
            
            O sistema utiliza uma taxonomia de três níveis para categorizar projetos:
            1. Macroárea (Nível 1)
            2. Segmento (Nível 2)
            3. Domínio (Nível 3)
            
            Macroáreas disponíveis:
            {chr(10).join(macroareas_list)}
            
            Exemplos de segmentos:
            {chr(10).join(segments_list)}
            
            Cada projeto pode ter uma categoria principal e categorias adicionais.
            """
        except Exception as e:
            current_app.logger.error(f"Error retrieving categories info: {str(e)}")
            return "INFORMAÇÕES SOBRE CATEGORIAS: Dados não disponíveis no momento."
    
    def _get_statistics_info(self):
        """Get statistical information"""
        try:
            # Use direct SQL queries with separate connections to avoid transaction issues
            with db.engine.connect() as connection:
                # Get total projects count
                total_projects_result = connection.execute(text("SELECT COUNT(*) FROM gepes.projetos"))
                total_projects = total_projects_result.scalar() or 0
            
            with db.engine.connect() as connection:
                # Get categorized projects count
                categorized_projects_result = connection.execute(
                    text("SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.categorias c ON p.id = c.id_projeto")
                )
                categorized_projects = categorized_projects_result.scalar() or 0
            
            with db.engine.connect() as connection:
                # Get tecverde projects count
                tecverde_projects_result = connection.execute(
                    text("SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.tecnologias_verdes tv ON p.id = tv.id_projeto WHERE tv.se_aplica = true")
                )
                tecverde_projects = tecverde_projects_result.scalar() or 0
            
            with db.engine.connect() as connection:
                # Get AI suggestion counts
                ai_suggested_result = connection.execute(
                    text("SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.ai_suggestions ais ON p.id = ais.id_projeto")
                )
                ai_suggested = ai_suggested_result.scalar() or 0
            
            with db.engine.connect() as connection:
                # Get human validated count
                human_validated_result = connection.execute(
                    text("SELECT COUNT(*) FROM gepes.projetos p JOIN gepes.categorias c ON p.id = c.id_projeto WHERE p.ai_rating_aia_user IS NOT NULL")
                )
                human_validated = human_validated_result.scalar() or 0
            
            # Calculate derived statistics
            ai_classified = categorized_projects - human_validated
            uncategorized = total_projects - categorized_projects
            
            return f"""
            ESTATÍSTICAS DO SISTEMA:
            
            Total de projetos: {total_projects}
            Projetos categorizados: {categorized_projects} ({round(categorized_projects/total_projects*100 if total_projects > 0 else 0, 2)}%)
            Projetos com tecnologia verde: {tecverde_projects} ({round(tecverde_projects/total_projects*100 if total_projects > 0 else 0, 2)}%)
            Projetos com sugestões da IA: {ai_suggested} ({round(ai_suggested/total_projects*100 if total_projects > 0 else 0, 2)}%)
            
            Distribuição por status:
            - Validado por humano: {human_validated} ({round(human_validated/total_projects*100 if total_projects > 0 else 0, 2)}%)
            - Classificado por IA: {ai_classified} ({round(ai_classified/total_projects*100 if total_projects > 0 else 0, 2)}%)
            - Não classificado: {uncategorized} ({round(uncategorized/total_projects*100 if total_projects > 0 else 0, 2)}%)
            
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
            # Use direct SQL queries with separate connections to avoid transaction issues
            with db.engine.connect() as connection:
                # Search for projects by title or code
                search_sql = """
                SELECT id, codigo_projeto, titulo 
                FROM gepes.projetos 
                WHERE titulo ILIKE :query OR codigo_projeto ILIKE :query 
                LIMIT 5
                """
                projects_result = connection.execute(
                    text(search_sql),
                    {"query": f"%{query}%"}
                )
                
                projects = [
                    {"id": row[0], "codigo_projeto": row[1], "titulo": row[2]} 
                    for row in projects_result
                ]
            
            if not projects:
                return f"Nenhum projeto encontrado com o termo '{query}'."
            
            result = f"Projetos encontrados com o termo '{query}':\n\n"
            
            for p in projects:
                # Get category if available
                with db.engine.connect() as connection:
                    categoria_sql = """
                    SELECT microarea, segmento 
                    FROM gepes.categorias 
                    WHERE id_projeto = :id_projeto
                    """
                    categoria_result = connection.execute(
                        text(categoria_sql),
                        {"id_projeto": p["id"]}
                    ).fetchone()
                
                categoria_info = ""
                if categoria_result:
                    categoria_info = f"Categoria: {categoria_result[0]} > {categoria_result[1]}"
                
                # Get green technology if available
                with db.engine.connect() as connection:
                    tecverde_sql = """
                    SELECT se_aplica, classe 
                    FROM gepes.tecnologias_verdes 
                    WHERE id_projeto = :id_projeto
                    """
                    tecverde_result = connection.execute(
                        text(tecverde_sql),
                        {"id_projeto": p["id"]}
                    ).fetchone()
                
                tecverde_info = ""
                if tecverde_result:
                    tecverde_info = f"Tecnologia Verde: {'Sim' if tecverde_result[0] else 'Não'}"
                    if tecverde_result[0] and tecverde_result[1]:
                        tecverde_info += f" (Classe: {tecverde_result[1]})"
                
                result += f"""
                Título: {p["titulo"]}
                Código: {p["codigo_projeto"]}
                {categoria_info}
                {tecverde_info}
                """
            
            return result
        except Exception as e:
            current_app.logger.error(f"Error searching project: {str(e)}")
            return f"Erro ao buscar projetos com o termo '{query}'."

# Create a singleton instance
rag_assistant = RAGAssistant()
