from openai import OpenAI
import json
import logging
from datetime import datetime
from app.models import AISuggestion, CategoriaLista, db

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
    
    def _get_categories_lists(self):
        """Obtém as listas de categorias do banco de dados."""
        organized_lists = {}
        
        # Obter todas as categorias ativas
        all_categories = CategoriaLista.query.filter_by(ativo=True).all()
        
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
        
        # Adicionar a estrutura hierárquica ao resultado
        organized_lists['dominios_por_microarea_segmento'] = dominios_por_microarea_segmento
        
        return organized_lists
    
    def _get_tecverde_classes(self):
        """Obtém as classes de tecnologias verdes do banco de dados."""
        # Buscar classes de tecnologias verdes no banco de dados
        # Por enquanto, usamos dados predefinidos para exemplo
        tecverde_classes = {
            "Energias alternativas": "Tecnologias relacionadas a fontes de energia alternativas",
            "Gestão Ambiental": "Tecnologias de gerenciamento e controle do impacto ambiental",
            "Transporte": "Tecnologias de transporte com menor impacto ambiental",
            "Conservação": "Tecnologias para conservação de recursos naturais",
            "Agricultura Sustentável": "Métodos agrícolas que minimizam impacto ambiental"
        }
        
        return tecverde_classes
    
    def _get_tecverde_subclasses(self):
        """Obtém as subclasses de tecnologias verdes do banco de dados."""
        # Buscar subclasses de tecnologias verdes no banco de dados
        # Por enquanto, usamos dados predefinidos para exemplo
        tecverde_subclasses = {
            "Energias alternativas": "Solar; Eólica; Biomassa; Geotérmica; Hidrogênio",
            "Gestão Ambiental": "Tratamento de resíduos; Controle de poluição; Monitoramento ambiental; Remediação",
            "Transporte": "Veículos elétricos; Biocombustíveis; Mobilidade urbana sustentável",
            "Conservação": "Conservação de água; Conservação de biodiversidade; Reflorestamento",
            "Agricultura Sustentável": "Agricultura orgânica; Agricultura de precisão; Agroecologia; Sistemas agroflorestais"
        }
        
        return tecverde_subclasses
    
    def _get_aia_data_from_db(self):
        """
        Obtém os dados de AIA (Áreas de Interesse Aplicado) do banco de dados.
        
        Returns:
            Lista de dicionários com as categorias do AIA
        """
        categories_lists = self._get_categories_lists()
        dominios_por_microarea_segmento = categories_lists.get('dominios_por_microarea_segmento', {})
        
        aia_data = []
        
        # Converter a estrutura hierárquica para o formato esperado pelo método _build_prompt_etapa1
        for macroarea, segmentos in dominios_por_microarea_segmento.items():
            for segmento, dominios in segmentos.items():
                dominios_str = "; ".join(dominios) if dominios else ""
                aia_data.append({
                    "Macroárea": macroarea,
                    "Segmento": segmento,
                    "Domínios Afeitos": dominios_str
                })
        
        return aia_data
    
    def suggest_categories(self, project, categories_lists=None, aia_data=None):
        """
        Sugere categorias para um projeto usando a API do OpenAI em um processo de três etapas.
        
        Etapa 1: A IA identifica a Micro Área, Segmento e Domínio
        Etapa 2: Com base nessas informações, fornecemos a lista correta de Domínios Afeitos Outros
                 (todos os domínios de outros segmentos da mesma microárea) para a IA selecionar
        Etapa 3: A IA classifica o projeto em termos de Tecnologias Verdes (classe e subclasse)
        
        Args:
            project: Dicionário com informações do projeto
            categories_lists: Dicionário com as listas de categorias disponíveis (opcional)
            aia_data: Lista de categorias do arquivo aia.json (opcional)
            
        Returns:
            Dicionário com as categorias sugeridas e informações adicionais
        """
        logger.info(f"Iniciando classificação do projeto ID: {project.get('id')}, Título: {project.get('titulo', '')}")
        if not self.api_key:
            return {
                "error": "Chave da API OpenAI não configurada"
            }
        
        try:
            # Se não foi fornecido aia_data, obter do banco de dados
            if not aia_data:
                aia_data = self._get_aia_data_from_db()
                
            # ETAPA 1: Identificar Micro Área, Segmento e Domínio
            prompt_etapa1 = self._build_prompt_etapa1(project, aia_data)
            logger.info(f"Etapa 1 - Enviando prompt para OpenAI (projeto ID: {project.get('id')})")
            logger.debug(f"Prompt Etapa 1: {prompt_etapa1[:200]}...")
            
            # Chamar a API do ChatGPT para a primeira etapa
            response_etapa1 = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em categorizar projetos de pesquisa e desenvolvimento industrial."},
                    {"role": "user", "content": prompt_etapa1}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            # Extrair a resposta da primeira etapa
            ai_response_etapa1 = response_etapa1.choices[0].message.content.strip()
            logger.info(f"Etapa 1 - Resposta recebida da OpenAI (projeto ID: {project.get('id')})")
            logger.info(f"Resposta bruta da API (Etapa 1): {ai_response_etapa1}")
            logger.debug(f"Resposta completa da API (Etapa 1): {response_etapa1}")
            
            # Processar a resposta da primeira etapa
            try:
                # Tentar analisar como JSON
                result_etapa1 = self._parse_ai_response(ai_response_etapa1)
                
                # Se não conseguiu obter um resultado válido, retornar erro
                if not result_etapa1 or "error" in result_etapa1:
                    return result_etapa1
                
                # ETAPA 2: Fornecer a lista de Domínios Afeitos Outros para seleção
                # Extrair a microárea e segmento identificados na primeira etapa
                macroarea = result_etapa1.get("_aia_n1_macroarea", "")
                segmento = result_etapa1.get("_aia_n2_segmento", "")
                
                # Se não temos microárea ou segmento, não podemos continuar
                if not macroarea or not segmento:
                    result_etapa1["_aia_n3_dominio_outro"] = "N/A"
                    result_etapa1["timestamp"] = datetime.now().isoformat()
                    return result_etapa1
                
                # Gerar a lista de Domínios Afeitos Outros (todos os domínios de outros segmentos da mesma microárea)
                dominios_afeitos_outros = self._get_dominios_afeitos_outros(macroarea, segmento, aia_data)
                
                # Verificar se a lista de domínios afeitos outros está vazia
                if not dominios_afeitos_outros:
                    # Se não há domínios afeitos outros, definir como N/A e pular etapa 2
                    result_etapa1["_aia_n3_dominio_outro"] = "N/A"
                    result_etapa1["timestamp"] = datetime.now().isoformat()
                    return result_etapa1
                
                # Construir o prompt para a segunda etapa (só será executado se houver domínios afeitos outros)
                prompt_etapa2 = self._build_prompt_etapa2(project, result_etapa1, dominios_afeitos_outros)
                logger.info(f"Etapa 2 - Enviando prompt para OpenAI (projeto ID: {project.get('id')})")
                logger.debug(f"Prompt Etapa 2: {prompt_etapa2[:200]}...")
                
                # Chamar a API do ChatGPT para a segunda etapa
                response_etapa2 = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Você é um assistente especializado em categorizar projetos de pesquisa e desenvolvimento industrial."},
                        {"role": "user", "content": prompt_etapa2}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )
                
                # Extrair a resposta da segunda etapa
                ai_response_etapa2 = response_etapa2.choices[0].message.content.strip()
                logger.info(f"Etapa 2 - Resposta recebida da OpenAI (projeto ID: {project.get('id')})")
                logger.info(f"Resposta bruta da API (Etapa 2): {ai_response_etapa2}")
                logger.debug(f"Resposta completa da API (Etapa 2): {response_etapa2}")
                
                # Processar a resposta da segunda etapa
                result_etapa2 = self._parse_ai_response(ai_response_etapa2)
                
                # Combinar os resultados das duas etapas
                final_result = result_etapa1.copy()
                if result_etapa2 and "_aia_n3_dominio_outro" in result_etapa2:
                    final_result["_aia_n3_dominio_outro"] = result_etapa2["_aia_n3_dominio_outro"]
                
                # ETAPA 3: Classificar Tecnologias Verdes
                try:
                    # Carregar dados de tecnologias verdes do banco de dados
                    tecverde_classes = self._get_tecverde_classes()
                    tecverde_subclasses = self._get_tecverde_subclasses()
                    
                    # Construir o prompt para a terceira etapa
                    prompt_etapa3 = self._build_prompt_etapa3(project, tecverde_classes, tecverde_subclasses)
                    logger.info(f"Etapa 3 - Enviando prompt para OpenAI (projeto ID: {project.get('id')})")
                    logger.debug(f"Prompt Etapa 3: {prompt_etapa3[:200]}...")
                    
                    # Chamar a API do ChatGPT para a terceira etapa
                    response_etapa3 = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Você é um assistente especializado em categorizar projetos de pesquisa com foco em tecnologias verdes."},
                            {"role": "user", "content": prompt_etapa3}
                        ],
                        temperature=0.3,
                        max_tokens=800
                    )
                    
                    # Extrair a resposta da terceira etapa
                    ai_response_etapa3 = response_etapa3.choices[0].message.content.strip()
                    logger.info(f"Etapa 3 - Resposta recebida da OpenAI (projeto ID: {project.get('id')})")
                    logger.info(f"Resposta bruta da API (Etapa 3): {ai_response_etapa3}")
                    logger.debug(f"Resposta completa da API (Etapa 3): {response_etapa3}")
                    
                    # Processar a resposta da terceira etapa
                    result_etapa3 = self._parse_ai_response(ai_response_etapa3)
                    
                    # Combinar os resultados das três etapas
                    if result_etapa3 and not "error" in result_etapa3:
                        # Normalizar o valor de se_aplica para Boolean
                        tecverde_se_aplica = self._normalize_se_aplica(result_etapa3.get("tecverde_se_aplica", ""))
                        
                        final_result["tecverde_se_aplica"] = tecverde_se_aplica
                        final_result["tecverde_classe"] = result_etapa3.get("tecverde_classe", "") if tecverde_se_aplica else ""
                        final_result["tecverde_subclasse"] = result_etapa3.get("tecverde_subclasse", "") if tecverde_se_aplica else ""
                        final_result["tecverde_confianca"] = result_etapa3.get("confianca", "MÉDIA")
                        final_result["tecverde_justificativa"] = result_etapa3.get("justificativa", "")
                except Exception as e:
                    print(f"Erro na etapa 3 (Tecnologias Verdes): {str(e)}")
                    # Se houver erro na etapa 3, continuar com os resultados das etapas 1 e 2
                    final_result["tecverde_se_aplica"] = False
                    final_result["tecverde_classe"] = ""
                    final_result["tecverde_subclasse"] = ""
                    final_result["tecverde_confianca"] = "BAIXA"
                    final_result["tecverde_justificativa"] = f"Erro ao processar tecnologias verdes: {str(e)}"
                
                # Adicionar timestamp
                final_result["timestamp"] = datetime.now().isoformat()
                
                # Salvar a sugestão no banco de dados
                self._save_suggestion_to_db(project['id'], final_result)
                
                return final_result
                
            except Exception as e:
                return {
                    "_aia_n1_macroarea": "",
                    "_aia_n2_segmento": "",
                    "_aia_n3_dominio_afeito": "",
                    "_aia_n3_dominio_outro": "",
                    "confianca": "BAIXA",
                    "justificativa": f"Erro ao processar resposta da IA: {str(e)}",
                    "error": f"Erro ao processar resposta da IA: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "_aia_n1_macroarea": "",
                "_aia_n2_segmento": "",
                "_aia_n3_dominio_afeito": "",
                "_aia_n3_dominio_outro": "",
                "confianca": "BAIXA",
                "justificativa": "",
                "error": f"Erro ao chamar OpenAI: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _save_suggestion_to_db(self, project_id, suggestion_data):
        """
        Salva a sugestão da IA no banco de dados.
        
        Args:
            project_id: ID do projeto
            suggestion_data: Dados da sugestão
        """
        logger.info(f"Salvando sugestão no banco de dados para o projeto ID: {project_id}")
        logger.info(f"Estrutura dos dados da sugestão: {json.dumps(suggestion_data, indent=2, ensure_ascii=False)}")
        try:
            # Verificar se já existe uma sugestão para este projeto
            suggestion = AISuggestion.query.filter_by(id_projeto=project_id).first()
            
            if suggestion:
                # Atualizar sugestão existente
                logger.info(f"Atualizando sugestão existente para o projeto ID: {project_id}")
                suggestion.microarea = suggestion_data.get('_aia_n1_macroarea', '')
                suggestion.segmento = suggestion_data.get('_aia_n2_segmento', '')
                suggestion.dominio = suggestion_data.get('_aia_n3_dominio_afeito', '')
                suggestion.dominio_outro = suggestion_data.get('_aia_n3_dominio_outro', '')
                suggestion.confianca = suggestion_data.get('confianca', '')
                suggestion.justificativa = suggestion_data.get('justificativa', '')
                suggestion.tecverde_se_aplica = suggestion_data.get('tecverde_se_aplica', False)
                suggestion.tecverde_classe = suggestion_data.get('tecverde_classe', '')
                suggestion.tecverde_subclasse = suggestion_data.get('tecverde_subclasse', '')
                suggestion.tecverde_confianca = suggestion_data.get('tecverde_confianca', '')
                suggestion.tecverde_justificativa = suggestion_data.get('tecverde_justificativa', '')
                suggestion.timestamp = datetime.now()
                suggestion._aia_n1_macroarea = suggestion_data.get('_aia_n1_macroarea', '')
                suggestion._aia_n2_segmento = suggestion_data.get('_aia_n2_segmento', '')
                suggestion._aia_n3_dominio_afeito = suggestion_data.get('_aia_n3_dominio_afeito', '')
                suggestion._aia_n3_dominio_outro = suggestion_data.get('_aia_n3_dominio_outro', '')
            else:
                # Criar nova sugestão
                suggestion = AISuggestion(
                    id_projeto=project_id,
                    microarea=suggestion_data.get('_aia_n1_macroarea', ''),
                    segmento=suggestion_data.get('_aia_n2_segmento', ''),
                    dominio=suggestion_data.get('_aia_n3_dominio_afeito', ''),
                    dominio_outro=suggestion_data.get('_aia_n3_dominio_outro', ''),
                    confianca=suggestion_data.get('confianca', ''),
                    justificativa=suggestion_data.get('justificativa', ''),
                    tecverde_se_aplica=suggestion_data.get('tecverde_se_aplica', False),
                    tecverde_classe=suggestion_data.get('tecverde_classe', ''),
                    tecverde_subclasse=suggestion_data.get('tecverde_subclasse', ''),
                    tecverde_confianca=suggestion_data.get('tecverde_confianca', ''),
                    tecverde_justificativa=suggestion_data.get('tecverde_justificativa', ''),
                    timestamp=datetime.now(),
                    _aia_n1_macroarea=suggestion_data.get('_aia_n1_macroarea', ''),
                    _aia_n2_segmento=suggestion_data.get('_aia_n2_segmento', ''),
                    _aia_n3_dominio_afeito=suggestion_data.get('_aia_n3_dominio_afeito', ''),
                    _aia_n3_dominio_outro=suggestion_data.get('_aia_n3_dominio_outro', '')
                )
                db.session.add(suggestion)
                
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar sugestão no banco de dados: {str(e)}")
            return False
    
    def _build_prompt_etapa3(self, project, tecverde_classes, tecverde_subclasses):
        """
        Constrói o prompt para a terceira etapa: classificação de Tecnologias Verdes.
        
        Args:
            project: Dicionário com informações do projeto
            tecverde_classes: Dicionário com as classes de tecnologias verdes
            tecverde_subclasses: Dicionário com as subclasses de tecnologias verdes
            
        Returns:
            String com o prompt formatado
        """
        tecverde_list = []
        
        for classe, descricao in tecverde_classes.items():
            subclasses_text = ""
            if classe in tecverde_subclasses:
                subclasses = tecverde_subclasses[classe]
                if isinstance(subclasses, str):
                    if ';' in subclasses:
                        subclasses_list = subclasses.split(';')
                    elif ',' in subclasses:
                        subclasses_list = subclasses.split(',')
                    else:
                        subclasses_list = [subclasses]
                    subclasses_list = [s.strip() for s in subclasses_list if s.strip()]
                    subclasses_text = "; ".join(subclasses_list)
            
            tecverde_list.append(f"Classe: {classe} | Descrição: {descricao} | Subclasses: {subclasses_text}")
        
        tecverde_text = "\n".join(tecverde_list)

        prompt = f"""
Você é um assistente especializado em classificar projetos de pesquisa em Tecnologias Verdes.

A partir da definição de tecnologia verde como "tecnologias ambientalmente corretas que protegem o meio ambiente, são menos poluentes, usam os recursos de forma mais sustentável, reciclam mais seus resíduos e produtos, e lidam com os resíduos de forma mais aceitável do que as tecnologias que substituem" (Agenda 21, Capítulo 34), avalie o seguinte projeto em três etapas:

Informações do Projeto:
Título: {project.get('titulo', '')}
Título Público: {project.get('titulo_publico', '')}
Objetivo: {project.get('objetivo', '')}
Descrição Pública: {project.get('descricao_publica', '')}
Tags: {project.get('tags', '')}

Etapa 1 – Avaliação de elegibilidade como tecnologia verde:
O projeto descrito é uma tecnologia verde segundo a definição acima?
Decida com base nos critérios: proteção ambiental, menor poluição, uso sustentável de recursos, reciclagem, etc.

Etapa 2 – Classificação por classe:
Caso o projeto seja uma tecnologia verde, indique a classe do projeto, selecionando entre as classes fornecidas.

Etapa 3 – Classificação por subclasse:
Indique qual subclasse o projeto se encaixa dentro da classe escolhida.

Lista de Classes e Subclasses:
{tecverde_text}

Regras:
- Para a Etapa 1, responda APENAS "Sim" ou "Não".
- Para a Etapa 2, a Classe escolhida deve existir na lista fornecida.
- Para a Etapa 3, a Subclasse escolhida deve pertencer à Classe escolhida.
- Classifique o grau de confiança: ALTA, MÉDIA ou BAIXA.
- A justificativa deve ser clara e concisa (no máximo 2-3 frases).
- Se a resposta for "Não", a justificativa DEVE explicar especificamente por que o projeto não atende aos critérios de tecnologia verde.
- Se a resposta for "Sim", a justificativa deve explicar como o projeto contribui para os objetivos de tecnologia verde.

IMPORTANTE:
Sua resposta deve ser APENAS um JSON válido no seguinte formato:

{{
    "tecverde_se_aplica": "Sim ou Não",
    "tecverde_classe": "Nome da Classe escolhida (apenas se 'se_aplica' for 'Sim')",
    "tecverde_subclasse": "Nome da Subclasse escolhida (apenas se 'se_aplica' for 'Sim')",
    "confianca": "ALTA, MÉDIA ou BAIXA",
    "justificativa": "Breve explicação da escolha, incluindo motivo específico quando não se aplica"
}}

Não adicione explicações fora do JSON.
"""
        
        return prompt.strip()
    
    def _parse_ai_response(self, ai_response):
        """
        Analisa a resposta da IA e tenta extrair o JSON.
        
        Args:
            ai_response: Resposta da IA em texto
            
        Returns:
            Dicionário com os dados extraídos ou objeto de erro
        """
        logger.info("Analisando resposta da IA para extrair JSON")
        try:
            # Tentar analisar como JSON diretamente
            result = json.loads(ai_response)
            logger.info("Resposta da IA analisada com sucesso como JSON")
            return result
        except json.JSONDecodeError:
            logger.warning("Falha ao analisar resposta como JSON diretamente, tentando extrair parte JSON")
            # Tentar extrair apenas a parte JSON da resposta
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > 0:
                json_str = ai_response[start_idx:end_idx]
                try:
                    result = json.loads(json_str)
                    logger.info("JSON extraído com sucesso da resposta da IA")
                    return result
                except Exception as e:
                    logger.error(f"Falha ao analisar JSON extraído: {str(e)}")
            else:
                logger.error("Não foi possível encontrar estrutura JSON na resposta da IA")
            
            # Retornar um objeto de erro se não conseguir extrair como JSON
            error_result = {
                "_aia_n1_macroarea": "",
                "_aia_n2_segmento": "",
                "_aia_n3_dominio_afeito": "",
                "_aia_n3_dominio_outro": "",
                "confianca": "BAIXA",
                "justificativa": "Não foi possível processar a resposta da IA como JSON",
                "error": "Não foi possível processar a resposta da IA como JSON"
            }
            logger.error(f"Retornando objeto de erro: {error_result}")
            return error_result
    
    def _get_dominios_afeitos_outros(self, macroarea, segmento, aia_data):
        """
        Gera a lista de Domínios Afeitos Outros (todos os domínios de outros segmentos da mesma microárea).
        
        Args:
            macroarea: Microárea identificada
            segmento: Segmento identificado
            aia_data: Lista de categorias do arquivo aia.json
            
        Returns:
            Lista de domínios afeitos outros
        """
        if not aia_data:
            return []
        
        dominios_outros = []
        
        # Percorrer todos os itens do aia_data
        for item in aia_data:
            # Verificar se o item pertence à mesma microárea, mas a um segmento diferente
            if item.get('Macroárea') == macroarea and item.get('Segmento') != segmento:
                # Obter os domínios afeitos deste segmento
                dominios = item.get('Domínios Afeitos', '').split(';')
                # Adicionar à lista de domínios afeitos outros
                for dominio in dominios:
                    dominio = dominio.strip()
                    if dominio and dominio not in dominios_outros:
                        dominios_outros.append(dominio)
        
        return dominios_outros
    
    def _build_prompt_etapa1(self, project, aia_data=None):
        """
        Constrói o prompt para a primeira etapa: identificação de Micro Área, Segmento e Domínio.
        
        Args:
            project: Dicionário com informações do projeto
            aia_data: Lista de categorias do arquivo aia.json (opcional)
            
        Returns:
            String com o prompt formatado
        """
        # Construir a parte do prompt com as categorias do aia.json
        aia_categories_text = ""
        
        if aia_data:
            aia_categories_text = "Categorias do AIA (Áreas de Interesse Aplicado):\n\n"
            
            # Agrupar por Macroárea
            macroareas = {}
            for item in aia_data:
                macroarea = item.get('Macroárea')
                if macroarea not in macroareas:
                    macroareas[macroarea] = {}
                
                segmento = item.get('Segmento')
                if segmento not in macroareas[macroarea]:
                    macroareas[macroarea][segmento] = []
                
                dominios = item.get('Domínios Afeitos', '').split(';')
                dominios = [d.strip() for d in dominios if d.strip()]
                macroareas[macroarea][segmento].extend(dominios)
            
            # Formatar o texto das categorias
            for macroarea, segmentos in macroareas.items():
                aia_categories_text += f"Macroárea: {macroarea}\n"
                
                for segmento, dominios in segmentos.items():
                    aia_categories_text += f"  Segmento: {segmento}\n"
                    
                    if dominios:
                        aia_categories_text += "    Domínios Afeitos:\n"
                        for dominio in dominios:
                            aia_categories_text += f"      - {dominio}\n"
                
                aia_categories_text += "\n"
        
        prompt = f"""
        Com base nas informações do projeto abaixo, sugira as categorias mais apropriadas do AIA (Áreas de Interesse Aplicado):
        
        Título do Projeto: {project.get('titulo', '')}
        Título Público: {project.get('titulo_publico', '')}
        Objetivo: {project.get('objetivo', '')}
        Descrição Pública: {project.get('descricao_publica', '')}
        Tags: {project.get('tags', '')}
        
        {aia_categories_text}
        
        Você deve classificar o projeto escolhendo EXATAMENTE UMA Macroárea e UM Segmento das opções acima.
        Para Domínios Afeitos, você pode selecionar MÚLTIPLOS domínios que sejam relevantes para o projeto, mas apenas do segmento escolhido.
        
        IMPORTANTE: Nesta primeira etapa, NÃO selecione Domínios Afeitos Outros. Isso será feito em uma etapa posterior.
        
        Forneça sua resposta APENAS em formato JSON válido com a seguinte estrutura:
        {{
            "_aia_n1_macroarea": "Nome da Macroárea escolhida",
            "_aia_n2_segmento": "Nome do Segmento escolhido",
            "_aia_n3_dominio_afeito": "Domínio1;Domínio2;Domínio3",
            "confianca": "ALTA, MÉDIA ou BAIXA",
            "justificativa": "Breve explicação da sua classificação (máximo 2 frases)"
        }}
        
        A confiança deve ser:
        - ALTA: quando você tem certeza da classificação
        - MÉDIA: quando a classificação é provável, mas há outras possibilidades
        - BAIXA: quando há pouca informação ou o projeto poderia se encaixar em várias categorias
        
        É MUITO IMPORTANTE que sua resposta seja um JSON válido, pois será processada automaticamente.
        """
        
        return prompt
    
    def _build_prompt_etapa2(self, project, result_etapa1, dominios_afeitos_outros):
        """
        Constrói o prompt para a segunda etapa: seleção de Domínios Afeitos Outros.
        
        Args:
            project: Dicionário com informações do projeto
            result_etapa1: Resultado da primeira etapa (Micro Área, Segmento e Domínio)
            dominios_afeitos_outros: Lista de domínios afeitos outros disponíveis
            
        Returns:
            String com o prompt formatado
        """
        # Formatar a lista de domínios afeitos outros disponíveis
        dominios_outros_text = ""
        if dominios_afeitos_outros:
            dominios_outros_text = "Domínios Afeitos Outros disponíveis (de outros segmentos da mesma microárea):\n"
            for dominio in dominios_afeitos_outros:
                dominios_outros_text += f"  - {dominio}\n"
        else:
            dominios_outros_text = "Não há Domínios Afeitos Outros disponíveis para esta microárea e segmento."
        
        # Extrair informações da primeira etapa
        macroarea = result_etapa1.get("_aia_n1_macroarea", "")
        segmento = result_etapa1.get("_aia_n2_segmento", "")
        dominio_afeito = result_etapa1.get("_aia_n3_dominio_afeito", "")
        
        prompt = f"""
        Com base nas informações do projeto e na classificação já realizada, selecione os Domínios Afeitos Outros mais apropriados.
        
        Título do Projeto: {project.get('titulo', '')}
        Título Público: {project.get('titulo_publico', '')}
        Objetivo: {project.get('objetivo', '')}
        Descrição Pública: {project.get('descricao_publica', '')}
        Tags: {project.get('tags', '')}
        
        Classificação já realizada:
        - Macroárea: {macroarea}
        - Segmento: {segmento}
        - Domínios Afeitos: {dominio_afeito}
        
        {dominios_outros_text}
        
        IMPORTANTE: Os Domínios Afeitos Outros são domínios de outros segmentos da mesma microárea que também são relevantes para o projeto, mas não são do segmento principal escolhido.
        
        Você deve selecionar APENAS domínios da lista fornecida acima. Se não houver domínios relevantes, use o valor "N/A".
        
        Forneça sua resposta APENAS em formato JSON válido com a seguinte estrutura:
        {{
            "_aia_n3_dominio_outro": "DomínioOutro1;DomínioOutro2"
        }}
        
        Use o formato exato dos nomes dos domínios como listados acima, separados por ponto e vírgula (;).
        
        É MUITO IMPORTANTE que sua resposta seja um JSON válido, pois será processada automaticamente.
        """
        
        return prompt
    
    def process_validation(self, suggestion, validation):
        """
        Processa a validação do usuário para uma sugestão da IA.
        
        Args:
            suggestion: Dicionário com as sugestões da IA
            validation: Dicionário com as validações do usuário (aceito/rejeitado)
            
        Returns:
            Dicionário com as categorias finais após validação
        """
        result = {}
        
        # Mapear nomes de campos
        field_mapping = {
            'microarea': '_aia_n1_macroarea',
            'segmento': '_aia_n2_segmento',
            'dominio': '_aia_n3_dominio_afeito',
            'dominio_outro': '_aia_n3_dominio_outro'
        }
        
        # Processar cada categoria
        for ui_field, db_field in field_mapping.items():
            if ui_field in validation and validation[ui_field] == 'accepted':
                # Se a categoria foi aceita, usar a sugestão da IA
                value = suggestion.get(db_field, '')
                
                # Verificar se estamos lidando com dominio_outro e se o valor é vazio ou N/A
                if db_field == '_aia_n3_dominio_outro' and (not value or value.lower() == 'n/a'):
                    value = 'N/A'
                
                result[db_field] = value  # Usar a chave do banco de dados no resultado
            else:
                # Se a categoria foi rejeitada ou não foi validada, usar o valor manual
                # Mapear o campo manual para o campo do banco de dados
                # Verificar se estamos lidando com dominio_outro (que no formulário é dominio_outros)
                manual_field = f'manual_{ui_field}'
                if ui_field == 'dominio_outro':
                    # Tentar com ambos os nomes (singular e plural)
                    if manual_field not in validation:
                        manual_field = 'manual_dominio_outros'  # Tentar com o nome plural
                    
                    manual_value = validation.get(manual_field, '')
                    # Se o valor manual for vazio, usar N/A
                    if not manual_value:
                        manual_value = 'N/A'
                else:
                    manual_value = validation.get(manual_field, '')
                
                result[db_field] = manual_value  # Usar a chave do banco de dados no resultado
        
        return result

    def _normalize_se_aplica(self, value):
        """
        Normaliza o valor de 'se_aplica' para um formato consistente.
        
        Args:
            value: Valor original (pode ser string, int, bool)
            
        Returns:
            bool: True para Sim, False para Não
        """
        if isinstance(value, bool):
            return value
        
        if isinstance(value, int):
            return value == 1
        
        if isinstance(value, str):
            value = value.lower().strip()
            return value in ['sim', 'yes', '1', 'true', 'verdadeiro']
        
        return False  # valor padrão para casos não previstos
