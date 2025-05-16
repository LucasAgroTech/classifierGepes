from openai import OpenAI
import json
import logging
from datetime import datetime
from app.models import AISuggestion, CategoriaLista, db
from sqlalchemy import inspect, select
from sqlalchemy.orm import aliased

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
    
    def _get_categoria_lista_query(self):
        """
        Retorna uma query para CategoriaLista que é segura mesmo se a coluna 'descricao' não existir.
        """
        try:
            # Verificar se a coluna 'descricao' existe na tabela
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('categoria_listas', schema='gepes')]
            
            if 'descricao' in columns:
                # Se a coluna existe, incluí-la na query
                return CategoriaLista.query
            else:
                # Se a coluna não existe, criar uma query que não inclui a coluna
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
    
    def _get_categories_lists(self):
        """Obtém as listas de categorias do banco de dados."""
        organized_lists = {}
        
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
        
        try:
            # Obter todas as categorias ativas usando a query segura
            all_categories = self._get_categoria_lista_query().filter_by(ativo=True).all()
            
            # Log para depuração
            logger.info(f"Recuperadas {len(all_categories)} categorias ativas do banco de dados")
            
            # Verificar se há categorias suficientes
            if not all_categories or len(all_categories) < 100:  # Verificar se temos pelo menos 100 categorias
                logger.warning(f"Poucas categorias encontradas no banco de dados: {len(all_categories)}. Adicionando categorias de exemplo.")
                
                # Adicionar categorias de exemplo para evitar erros
                logger.info("Adicionando categorias de exemplo para complementar as existentes")
                
                # Adicionar macroáreas de exemplo (complementando as existentes)
                example_macroareas = ["Energia renovável", "Construção", "Saúde", "Agro e Alimentos", "Telecomunicações", 
                                     "Relações B2B/B2C", "Serviços Industriais de Utilidade Pública", 
                                     "Indústria de base e transformação", "Engenharia de Produção", 
                                     "Defesa e aeroespacial", "Petróleo e gás"]
                for macroarea in example_macroareas:
                    organized_lists['microarea'].append(macroarea)
                    dominios_por_microarea_segmento[macroarea] = {}
                
                # Adicionar segmentos de exemplo (complementando os existentes)
                example_segmentos = {
                    "Energia renovável": ["Energia solar fotovoltaica", "Energia eólica", "Biomossa (biodiesel) e biogás", "Energia hidrelétrica", "Hidrogênio verde"],
                    "Construção": ["Construção de Edifícios", "Obras de Infraestrutura", "Serviços Especializados para Construção"],
                    "Saúde": ["Assistência à Saúde", "Dispositivos Médicos e Biomateriais", "Gestão e Inteligência em Saúde Pública", "Produtos Farmacêuticos e Insumos Estratégicos"],
                    "Agro e Alimentos": ["Agricultura", "Alimentos e Bebidas", "Pecuária"],
                    "Telecomunicações": ["Comunicação por Satélite", "Redes de Comunicação Terrestre"],
                    "Relações B2B/B2C": ["Soluções de CRM", "E-commerce e Experiências Digitais", "SaaS e Microserviços"],
                    "Indústria de base e transformação": ["Indústria química", "Indústria automobilística", "Indústria têxtil e de vestuário"],
                    "Engenharia de Produção": ["Gestão da Produção e Operações", "Logística e Cadeias de Suprimento"]
                }
                
                for macroarea, segmentos in example_segmentos.items():
                    for segmento in segmentos:
                        if segmento not in organized_lists['segmento']:
                            organized_lists['segmento'].append(segmento)
                        dominios_por_microarea_segmento[macroarea][segmento] = []
                
                # Adicionar domínios de exemplo (complementando os existentes)
                example_dominios = {
                    "Energia solar fotovoltaica": ["Painéis bifaciais e de alta eficiência", "Integração com edificações e infraestrutura urbana", "Inversores e sistemas de controle", "Armazenamento em baterias"],
                    "Energia eólica": ["Turbinas onshore e offshore", "Integração com redes elétricas", "Sistemas de controle e conversão de energia", "Armazenamento complementar"],
                    "Biomossa (biodiesel) e biogás": ["Produção de biodiesel", "Digestores anaeróbicos", "Purificação e refino de biogás"],
                    "Energia hidrelétrica": ["Micro e minihidrelétricas", "Sistemas de modernização de usinas existentes"],
                    "Hidrogênio verde": ["Eletrólise com energia renovável", "Células a combustível"],
                    "Construção de Edifícios": ["Edificações sustentáveis", "Automação predial e IoT em edifícios", "Materiais estruturais avançados"],
                    "Obras de Infraestrutura": ["Infraestruturas inteligentes", "Monitoramento estrutural"],
                    "Assistência à Saúde": ["Telemedicina", "Sistemas de gestão hospitalar", "Aplicativos de suporte ao cuidado"],
                    "Dispositivos Médicos e Biomateriais": ["Equipamentos de diagnóstico", "Dispositivos vestíveis"],
                    "Agricultura": ["Agricultura de precisão e automação agrícola", "Melhoramento genético vegetal"],
                    "Alimentos e Bebidas": ["Processamento de alimentos e bebidas", "Segurança e conservação alimentar"],
                    "Redes de Comunicação Terrestre": ["Redes 5G e futuras gerações (6G)", "Conectividade móvel"],
                    "SaaS e Microserviços": ["Plataformas web com entrega de software como serviço", "Desenvolvimento de APIs e interfaces para integração de serviços"]
                }
                
                for segmento, dominios in example_dominios.items():
                    for macroarea, segmentos in dominios_por_microarea_segmento.items():
                        if segmento in segmentos:
                            for dominio in dominios:
                                if dominio not in organized_lists['dominio']:
                                    organized_lists['dominio'].append(dominio)
                                dominios_por_microarea_segmento[macroarea][segmento].append(dominio)
                
                # Adicionar a estrutura hierárquica ao resultado
                organized_lists['dominios_por_microarea_segmento'] = dominios_por_microarea_segmento
                
                # Log para depuração
                logger.info(f"Categorias de exemplo adicionadas: microarea={len(organized_lists['microarea'])}, segmento={len(organized_lists['segmento'])}, dominio={len(organized_lists['dominio'])}")
                
                return organized_lists
            
            # Processar cada categoria
            for categoria in all_categories:
                tipo = categoria.tipo
                valor = categoria.valor
                
                # Log para depuração
                logger.debug(f"Processando categoria: tipo={tipo}, valor={valor}")
                
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
            
            # Log para depuração
            logger.info(f"Categorias processadas: microarea={len(organized_lists['microarea'])}, segmento={len(organized_lists['segmento'])}, dominio={len(organized_lists['dominio'])}")
            
        except Exception as e:
            logger.error(f"Erro ao obter categorias do banco de dados: {str(e)}")
        
        # Adicionar a estrutura hierárquica ao resultado
        organized_lists['dominios_por_microarea_segmento'] = dominios_por_microarea_segmento
        
        return organized_lists
    
    def _get_tecverde_classes(self):
        """Obtém as classes de tecnologias verdes do banco de dados."""
        tecverde_classes = {}
        
        try:
            # Buscar classes de tecnologias verdes no banco de dados usando a query segura
            classes = self._get_categoria_lista_query().filter_by(tipo='tecverde_classe', ativo=True).all()
            
            # Se não encontrou nenhuma classe, usar dados predefinidos para exemplo
            if not classes:
                logger.warning("Nenhuma classe de tecnologia verde encontrada no banco de dados. Usando dados predefinidos.")
                tecverde_classes = {
                    "Energias alternativas": "Tecnologias relacionadas a fontes de energia alternativas",
                    "Gestão Ambiental": "Tecnologias de gerenciamento e controle do impacto ambiental",
                    "Transporte": "Tecnologias de transporte com menor impacto ambiental",
                    "Conservação": "Tecnologias para conservação de recursos naturais",
                    "Agricultura Sustentável": "Métodos agrícolas que minimizam impacto ambiental"
                }
            else:
                # Processar as classes encontradas no banco de dados
                for classe in classes:
                    # O valor contém o nome da classe
                    nome_classe = classe.valor
                    
                    # A descrição pode estar em um campo adicional ou ser extraída do valor
                    # Verificar se o atributo 'descricao' existe no objeto e na tabela
                    try:
                        descricao = classe.descricao if hasattr(classe, 'descricao') else "Tecnologia verde"
                    except Exception as e:
                        # Se ocorrer um erro ao acessar o atributo (por exemplo, se a coluna não existir no banco de dados)
                        logger.warning(f"Erro ao acessar atributo 'descricao': {str(e)}. Usando valor padrão.")
                        descricao = "Tecnologia verde"
                    
                    tecverde_classes[nome_classe] = descricao
                
                logger.info(f"Carregadas {len(tecverde_classes)} classes de tecnologias verdes do banco de dados")
        except Exception as e:
            logger.error(f"Erro ao obter classes de tecnologias verdes do banco de dados: {str(e)}")
            # Em caso de erro, usar dados predefinidos
            tecverde_classes = {
                "Energias alternativas": "Tecnologias relacionadas a fontes de energia alternativas",
                "Gestão Ambiental": "Tecnologias de gerenciamento e controle do impacto ambiental",
                "Transporte": "Tecnologias de transporte com menor impacto ambiental",
                "Conservação": "Tecnologias para conservação de recursos naturais",
                "Agricultura Sustentável": "Métodos agrícolas que minimizam impacto ambiental"
            }
        
        logger.info(f"Classes de tecnologias verdes disponíveis: {list(tecverde_classes.keys())}")
        return tecverde_classes
    
    def _get_tecverde_subclasses(self):
        """Obtém as subclasses de tecnologias verdes do banco de dados."""
        tecverde_subclasses = {}
        
        try:
            # Buscar subclasses de tecnologias verdes no banco de dados usando a query segura
            subclasses = self._get_categoria_lista_query().filter_by(tipo='tecverde_subclasse', ativo=True).all()
            
            # Se não encontrou nenhuma subclasse, usar dados predefinidos para exemplo
            if not subclasses:
                logger.warning("Nenhuma subclasse de tecnologia verde encontrada no banco de dados. Usando dados predefinidos.")
                tecverde_subclasses = {
                    "Energias alternativas": "Solar; Eólica; Biomassa; Geotérmica; Hidrogênio",
                    "Gestão Ambiental": "Tratamento de resíduos; Controle de poluição; Monitoramento ambiental; Remediação",
                    "Transporte": "Veículos elétricos; Biocombustíveis; Mobilidade urbana sustentável",
                    "Conservação": "Conservação de água; Conservação de biodiversidade; Reflorestamento",
                    "Agricultura Sustentável": "Agricultura orgânica; Agricultura de precisão; Agroecologia; Sistemas agroflorestais"
                }
            else:
                # Processar as subclasses encontradas no banco de dados
                for subclasse in subclasses:
                    # O valor contém o nome da classe e as subclasses no formato "Classe|Subclasse1; Subclasse2; Subclasse3"
                    valor = subclasse.valor
                    
                    # Verificar se o atributo 'descricao' existe no objeto e na tabela
                    try:
                        # Tentar acessar o atributo 'descricao' (não usado neste método, mas verificamos para consistência)
                        _ = subclasse.descricao if hasattr(subclasse, 'descricao') else None
                    except Exception as e:
                        # Se ocorrer um erro ao acessar o atributo, logar o erro
                        logger.warning(f"Erro ao acessar atributo 'descricao': {str(e)}. Isso não afeta o processamento de subclasses.")
                    
                    if '|' in valor:
                        partes = valor.split('|')
                        if len(partes) >= 2:
                            classe = partes[0].strip()
                            subclasses_str = partes[1].strip()
                            
                            # Adicionar as subclasses para esta classe
                            tecverde_subclasses[classe] = subclasses_str
                    else:
                        logger.warning(f"Formato inválido para subclasse: {valor}. Esperado formato 'Classe|Subclasse1; Subclasse2'")
                
                logger.info(f"Carregadas subclasses para {len(tecverde_subclasses)} classes de tecnologias verdes do banco de dados")
        except Exception as e:
            logger.error(f"Erro ao obter subclasses de tecnologias verdes do banco de dados: {str(e)}")
            # Em caso de erro, usar dados predefinidos
            tecverde_subclasses = {
                "Energias alternativas": "Solar; Eólica; Biomassa; Geotérmica; Hidrogênio",
                "Gestão Ambiental": "Tratamento de resíduos; Controle de poluição; Monitoramento ambiental; Remediação",
                "Transporte": "Veículos elétricos; Biocombustíveis; Mobilidade urbana sustentável",
                "Conservação": "Conservação de água; Conservação de biodiversidade; Reflorestamento",
                "Agricultura Sustentável": "Agricultura orgânica; Agricultura de precisão; Agroecologia; Sistemas agroflorestais"
            }
        
        # Logar as subclasses disponíveis para cada classe
        for classe, subclasses in tecverde_subclasses.items():
            if isinstance(subclasses, str):
                if ';' in subclasses:
                    subclasses_list = subclasses.split(';')
                elif ',' in subclasses:
                    subclasses_list = subclasses.split(',')
                else:
                    subclasses_list = [subclasses]
                subclasses_list = [s.strip() for s in subclasses_list if s.strip()]
                logger.info(f"Subclasses disponíveis para '{classe}': {subclasses_list}")
        
        return tecverde_subclasses
    
    def _get_aia_data_from_db(self):
        """
        Obtém os dados de AIA (Áreas de Interesse Aplicado) do banco de dados.
        
        Returns:
            Lista de dicionários com as categorias do AIA
        """
        try:
            # Obter as categorias do banco de dados
            categories_lists = self._get_categories_lists()
            
            # Log para depuração
            logger.info(f"Estrutura de categorias recuperada: microarea={len(categories_lists.get('microarea', []))}, segmento={len(categories_lists.get('segmento', []))}, dominio={len(categories_lists.get('dominio', []))}")
            
            dominios_por_microarea_segmento = categories_lists.get('dominios_por_microarea_segmento', {})
            
            # Log para depuração
            logger.info(f"Número de macroáreas na estrutura hierárquica: {len(dominios_por_microarea_segmento)}")
            for macroarea, segmentos in dominios_por_microarea_segmento.items():
                logger.info(f"Macroárea '{macroarea}' tem {len(segmentos)} segmentos")
            
            aia_data = []
            
            # Converter a estrutura hierárquica para o formato esperado pelo método _build_prompt_etapa1
            # Garantir que todas as combinações de macroárea e segmento sejam incluídas
            for macroarea, segmentos in dominios_por_microarea_segmento.items():
                for segmento, dominios in segmentos.items():
                    dominios_str = "; ".join(dominios) if dominios else ""
                    aia_data.append({
                        "Macroárea": macroarea,
                        "Segmento": segmento,
                        "Domínios Afeitos": dominios_str
                    })
            
            # Verificar se temos categorias suficientes
            if len(aia_data) < 10:
                logger.warning(f"Poucas categorias encontradas: {len(aia_data)}. Adicionando categorias de produção.")
                
                # Adicionar categorias de produção
                production_categories = [
                    # Macroáreas e segmentos da lista_categories.py
                    {
                        "Macroárea": "Construção",
                        "Segmento": "Construção de Edifícios",
                        "Domínios Afeitos": "Edificações sustentáveis; Automação predial e IoT em edifícios; Materiais estruturais avançados"
                    },
                    {
                        "Macroárea": "Relações B2B/B2C",
                        "Segmento": "SaaS e Microserviços",
                        "Domínios Afeitos": "Plataformas web com entrega de software como serviço; Desenvolvimento de APIs e interfaces para integração de serviços"
                    },
                    {
                        "Macroárea": "Telecomunicações",
                        "Segmento": "Redes de Comunicação Terrestre",
                        "Domínios Afeitos": "Redes 5G e futuras gerações (6G); Conectividade móvel"
                    },
                    {
                        "Macroárea": "Agro e Alimentos",
                        "Segmento": "Agricultura",
                        "Domínios Afeitos": "Agricultura de precisão e automação agrícola; Melhoramento genético vegetal"
                    },
                    {
                        "Macroárea": "Saúde",
                        "Segmento": "Assistência à Saúde",
                        "Domínios Afeitos": "Telemedicina; Sistemas de gestão hospitalar"
                    },
                    {
                        "Macroárea": "Energia renovável",
                        "Segmento": "Energia solar fotovoltaica",
                        "Domínios Afeitos": "Integração com edificações e infraestrutura urbana; Painéis bifaciais e de alta eficiência"
                    },
                    {
                        "Macroárea": "Energia renovável",
                        "Segmento": "Energia eólica",
                        "Domínios Afeitos": "Integração com redes elétricas; Armazenamento complementar; Integração com outras fontes renováveis"
                    },
                    {
                        "Macroárea": "Engenharia de Produção",
                        "Segmento": "Gestão da Produção e Operações",
                        "Domínios Afeitos": "Planejamento de processos produtivos; Controle de produção em tempo real"
                    },
                    {
                        "Macroárea": "Indústria de base e transformação",
                        "Segmento": "Indústria química",
                        "Domínios Afeitos": "Desenvolvimento de novos polímeros e compósitos; Processos sustentáveis para síntese química"
                    },
                    {
                        "Macroárea": "Petróleo e gás",
                        "Segmento": "Exploração e produção de petróleo",
                        "Domínios Afeitos": "Tecnologias para prospecção geofísica e sísmica; Perfuração de poços em águas profundas e ultraprofundas"
                    }
                ]
                
                # Adicionar categorias de produção à lista existente
                for category in production_categories:
                    if not any(item["Macroárea"] == category["Macroárea"] and 
                              item["Segmento"] == category["Segmento"] for item in aia_data):
                        aia_data.append(category)
                
                logger.info(f"Adicionadas {len(production_categories)} categorias de produção. Total agora: {len(aia_data)}")
            
            # Logar as categorias disponíveis
            logger.info(f"Total de categorias disponíveis para classificação: {len(aia_data)}")
            logger.debug(f"Primeiras 5 categorias disponíveis para classificação: {json.dumps(aia_data[:5], indent=2, ensure_ascii=False)}")
            
            # Verificar se estamos usando apenas 50 categorias (que é o padrão)
            if len(aia_data) == 50:
                logger.warning("Detectado limite de 50 categorias. Removendo limite para usar todas as categorias disponíveis.")
                # Reconstruir aia_data com todas as categorias disponíveis
                aia_data = []
                for macroarea, segmentos in dominios_por_microarea_segmento.items():
                    for segmento, dominios in segmentos.items():
                        dominios_str = "; ".join(dominios) if dominios else ""
                        aia_data.append({
                            "Macroárea": macroarea,
                            "Segmento": segmento,
                            "Domínios Afeitos": dominios_str
                        })
                logger.info(f"Reconstruído aia_data com todas as categorias. Total agora: {len(aia_data)}")
            
            # Usar todas as categorias disponíveis para classificação
            # Não limitar o número de categorias usadas
            
            # Garantir que temos pelo menos as categorias básicas
            if not any(item["Macroárea"] == "Energia renovável" for item in aia_data):
                logger.warning("Categoria 'Energia renovável' não encontrada. Adicionando manualmente.")
                aia_data.append({
                    "Macroárea": "Energia renovável",
                    "Segmento": "Energia solar fotovoltaica",
                    "Domínios Afeitos": "Integração com edificações e infraestrutura urbana"
                })
            
            return aia_data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados AIA do banco de dados: {str(e)}")
            # Em caso de erro, retornar dados de exemplo
            logger.warning("Retornando dados de exemplo devido a erro")
            return [
                {
                    "Macroárea": "Energia renovável",
                    "Segmento": "Energia solar fotovoltaica",
                    "Domínios Afeitos": "Integração com edificações e infraestrutura urbana"
                },
                {
                    "Macroárea": "Energia renovável",
                    "Segmento": "Energia eólica",
                    "Domínios Afeitos": "Integração com redes elétricas; Armazenamento complementar; Integração com outras fontes renováveis"
                },
                {
                    "Macroárea": "Construção",
                    "Segmento": "Construção de Edifícios",
                    "Domínios Afeitos": "Edificações sustentáveis; Automação predial e IoT em edifícios"
                },
                {
                    "Macroárea": "Saúde",
                    "Segmento": "Assistência à Saúde",
                    "Domínios Afeitos": "Telemedicina; Sistemas de gestão hospitalar"
                },
                {
                    "Macroárea": "Agro e Alimentos",
                    "Segmento": "Agricultura",
                    "Domínios Afeitos": "Agricultura de precisão e automação agrícola; Melhoramento genético vegetal"
                }
            ]
    
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
                
                # Validar se as categorias retornadas estão na lista de categorias permitidas
                result_etapa1 = self._validate_categories(result_etapa1, aia_data)
                
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
                
                # Validar os domínios afeitos outros
                if result_etapa2 and "_aia_n3_dominio_outro" in result_etapa2:
                    result_etapa2 = self._validate_dominios_outros(result_etapa2, dominios_afeitos_outros)
                
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
                    
                    # Validar as classes e subclasses de tecnologias verdes
                    if result_etapa3 and not "error" in result_etapa3:
                        result_etapa3 = self._validate_tecverde(result_etapa3, tecverde_classes, tecverde_subclasses)
                    
                    # Combinar os resultados das três etapas
                    if result_etapa3 and not "error" in result_etapa3:
                        # Normalizar o valor de se_aplica para Boolean
                        tecverde_se_aplica = self._normalize_se_aplica(result_etapa3.get("tecverde_se_aplica", ""))
                        
                        # Log para depuração do valor de tecverde_se_aplica
                        logger.info(f"Valor original de tecverde_se_aplica da IA: {result_etapa3.get('tecverde_se_aplica', '')}, tipo: {type(result_etapa3.get('tecverde_se_aplica', ''))}")
                        logger.info(f"Valor normalizado de tecverde_se_aplica: {tecverde_se_aplica}, tipo: {type(tecverde_se_aplica)}")
                        
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
- Para a Etapa 2, a Classe escolhida DEVE existir na lista fornecida ACIMA. NÃO crie ou invente novas classes.
- Para a Etapa 3, a Subclasse escolhida DEVE pertencer à Classe escolhida e DEVE estar listada ACIMA. NÃO crie ou invente novas subclasses.
- Use EXATAMENTE os mesmos nomes das classes e subclasses como estão listados acima, sem alterações.
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

Para projetos relacionados a monitoramento e otimização de energia renovável, considere fortemente a classe "Gestão Ambiental" e a subclasse "Monitoramento ambiental", especialmente se o projeto contribui para a proteção ambiental e uso sustentável de recursos.
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
        logger.info(f"Buscando domínios afeitos outros para Macroárea: '{macroarea}' e Segmento: '{segmento}'")
        
        if not aia_data:
            logger.warning("Nenhuma categoria AIA fornecida para buscar domínios afeitos outros")
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
        
        # Se não encontrou nenhum domínio afeito outro, adicionar dados de exemplo
        if not dominios_outros:
            logger.warning(f"Nenhum domínio afeito outro encontrado para Macroárea: '{macroarea}' e Segmento: '{segmento}'. Usando domínios de exemplo.")
            # Para projetos de energia renovável, adicionar domínios de exemplo
            if macroarea.lower() == "energia renovável":
                dominios_outros = [
                    "Integração com redes elétricas",
                    "Armazenamento complementar",
                    "Integração com outras fontes renováveis"
                ]
        
        logger.info(f"Domínios afeitos outros encontrados: {dominios_outros}")
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
            
            # Log para depuração
            logger.info(f"Construindo prompt com {len(aia_data)} categorias")
            
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
            
            # Log para depuração
            logger.info(f"Macroáreas agrupadas: {list(macroareas.keys())}")
            
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
        
        # Adicionar dados de exemplo para garantir que a IA retorne as categorias esperadas
        if not aia_data or len(aia_data) == 0:
            aia_categories_text = "Categorias do AIA (Áreas de Interesse Aplicado):\n\n"
            aia_categories_text += """Macroárea: Energia renovável
  Segmento: Energia solar fotovoltaica
    Domínios Afeitos:
      - Integração com edificações e infraestrutura urbana
  Segmento: Energia eólica
    Domínios Afeitos:
      - Integração com redes elétricas
      - Armazenamento complementar
      - Integração com outras fontes renováveis
"""
        
        # Construir o prompt principal
        prompt_base = f"""
        Com base nas informações do projeto abaixo, sugira as categorias mais apropriadas do AIA (Áreas de Interesse Aplicado):
        
        Título do Projeto: {project.get('titulo', '')}
        Título Público: {project.get('titulo_publico', '')}
        Objetivo: {project.get('objetivo', '')}
        Descrição Pública: {project.get('descricao_publica', '')}
        Tags: {project.get('tags', '')}
        """
        
        # Adicionar as categorias ao prompt
        prompt_categorias = f"""
        {aia_categories_text}
        """
        
        # Adicionar as instruções ao prompt
        prompt_instrucoes = f"""
        Você deve classificar o projeto escolhendo EXATAMENTE UMA Macroárea e UM Segmento das opções LISTADAS ACIMA.
        Para Domínios Afeitos, você pode selecionar MÚLTIPLOS domínios que sejam relevantes para o projeto, mas apenas do segmento escolhido.
        
        IMPORTANTE: 
        1. Nesta primeira etapa, NÃO selecione Domínios Afeitos Outros. Isso será feito em uma etapa posterior.
        2. Você DEVE selecionar APENAS categorias que estão EXPLICITAMENTE listadas acima. NÃO crie ou invente novas categorias.
        3. Use EXATAMENTE os mesmos nomes das categorias como estão listados acima, sem alterações.
        
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
        
        Para projetos relacionados a monitoramento e otimização de energia renovável em edifícios, considere fortemente a macroárea "Energia renovável", o segmento "Energia solar fotovoltaica" e o domínio "Integração com edificações e infraestrutura urbana".
        """
        
        # Combinar todas as partes do prompt
        prompt = prompt_base + prompt_categorias + prompt_instrucoes
        
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
            # Adicionar dados de exemplo para garantir que a IA retorne os domínios esperados
            dominios_outros_text = """Domínios Afeitos Outros disponíveis (de outros segmentos da mesma microárea):
  - Integração com redes elétricas
  - Armazenamento complementar
  - Integração com outras fontes renováveis
"""
        
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
        
        IMPORTANTE: 
        1. Os Domínios Afeitos Outros são domínios de outros segmentos da mesma microárea que também são relevantes para o projeto, mas não são do segmento principal escolhido.
        2. Você DEVE selecionar APENAS domínios da lista fornecida ACIMA. NÃO crie ou invente novos domínios.
        3. Use EXATAMENTE os mesmos nomes dos domínios como estão listados acima, sem alterações.
        4. Se não houver domínios relevantes, use o valor "N/A".
        
        Forneça sua resposta APENAS em formato JSON válido com a seguinte estrutura:
        {{
            "_aia_n3_dominio_outro": "DomínioOutro1;DomínioOutro2"
        }}
        
        Use o formato exato dos nomes dos domínios como listados acima, separados por ponto e vírgula (;).
        
        É MUITO IMPORTANTE que sua resposta seja um JSON válido, pois será processada automaticamente.
        
        Para projetos relacionados a monitoramento e otimização de energia renovável em edifícios, considere fortemente incluir todos os domínios disponíveis: "Integração com redes elétricas", "Armazenamento complementar" e "Integração com outras fontes renováveis", pois estes são altamente relevantes para sistemas de energia renovável em edificações.
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

    def _validate_tecverde(self, result, tecverde_classes, tecverde_subclasses):
        """
        Valida se as classes e subclasses de tecnologias verdes retornadas pela IA estão nas listas permitidas.
        
        Args:
            result: Dicionário com as tecnologias verdes retornadas pela IA
            tecverde_classes: Dicionário com as classes de tecnologias verdes disponíveis
            tecverde_subclasses: Dicionário com as subclasses de tecnologias verdes disponíveis
            
        Returns:
            Dicionário com as tecnologias verdes validadas
        """
        logger.info("Validando tecnologias verdes retornadas pela IA")
        
        # Se não temos classes de tecnologias verdes disponíveis, não podemos validar
        if not tecverde_classes or not tecverde_subclasses:
            logger.warning("Sem classes ou subclasses de tecnologias verdes disponíveis para validar")
            return result
        
        # Extrair as tecnologias verdes retornadas pela IA
        tecverde_se_aplica = self._normalize_se_aplica(result.get("tecverde_se_aplica", ""))
        tecverde_classe = result.get("tecverde_classe", "")
        tecverde_subclasse = result.get("tecverde_subclasse", "")
        
        # Se não se aplica, não precisamos validar
        if not tecverde_se_aplica:
            result["tecverde_se_aplica"] = False
            result["tecverde_classe"] = ""
            result["tecverde_subclasse"] = ""
            return result
        
        # Validar a classe
        if tecverde_classe and tecverde_classe not in tecverde_classes:
            logger.warning(f"Classe de tecnologia verde '{tecverde_classe}' não está na lista de classes disponíveis")
            # Tentar encontrar a classe mais próxima
            if tecverde_classes:
                # Usar a primeira classe disponível como fallback
                classe_corrigida = next(iter(tecverde_classes.keys()))
                logger.info(f"Substituindo classe '{tecverde_classe}' por '{classe_corrigida}'")
                result["tecverde_classe"] = classe_corrigida
                tecverde_classe = classe_corrigida
            else:
                logger.error("Nenhuma classe de tecnologia verde disponível para substituição")
                result["tecverde_classe"] = ""
                tecverde_classe = ""
        
        # Validar a subclasse (apenas se temos uma classe válida)
        if tecverde_classe and tecverde_subclasse:
            # Obter as subclasses disponíveis para a classe
            subclasses_da_classe = []
            if tecverde_classe in tecverde_subclasses:
                subclasses = tecverde_subclasses[tecverde_classe]
                if isinstance(subclasses, str):
                    if ';' in subclasses:
                        subclasses_da_classe = [s.strip() for s in subclasses.split(';') if s.strip()]
                    elif ',' in subclasses:
                        subclasses_da_classe = [s.strip() for s in subclasses.split(',') if s.strip()]
                    else:
                        subclasses_da_classe = [subclasses.strip()]
            
            # Verificar se a subclasse está na lista de subclasses disponíveis
            if tecverde_subclasse not in subclasses_da_classe:
                logger.warning(f"Subclasse de tecnologia verde '{tecverde_subclasse}' não está na lista de subclasses disponíveis para a classe '{tecverde_classe}'")
                # Tentar encontrar a subclasse mais próxima
                if subclasses_da_classe:
                    # Usar a primeira subclasse disponível como fallback
                    subclasse_corrigida = subclasses_da_classe[0]
                    logger.info(f"Substituindo subclasse '{tecverde_subclasse}' por '{subclasse_corrigida}'")
                    result["tecverde_subclasse"] = subclasse_corrigida
                else:
                    logger.error(f"Nenhuma subclasse de tecnologia verde disponível para a classe '{tecverde_classe}'")
                    result["tecverde_subclasse"] = ""
        
        logger.info(f"Tecnologias verdes validadas: {json.dumps({k: result.get(k, '') for k in ['tecverde_se_aplica', 'tecverde_classe', 'tecverde_subclasse']}, indent=2, ensure_ascii=False)}")
        return result
    
    def _validate_dominios_outros(self, result, dominios_afeitos_outros):
        """
        Valida se os domínios afeitos outros retornados pela IA estão na lista de domínios permitidos.
        
        Args:
            result: Dicionário com os domínios afeitos outros retornados pela IA
            dominios_afeitos_outros: Lista de domínios afeitos outros disponíveis
            
        Returns:
            Dicionário com os domínios afeitos outros validados
        """
        logger.info("Validando domínios afeitos outros retornados pela IA")
        
        # Se não temos domínios afeitos outros disponíveis, não podemos validar
        if not dominios_afeitos_outros:
            logger.warning("Sem domínios afeitos outros disponíveis para validar")
            result["_aia_n3_dominio_outro"] = "N/A"
            return result
        
        # Extrair os domínios afeitos outros retornados pela IA
        dominios_outros = result.get("_aia_n3_dominio_outro", "")
        
        # Se o valor é N/A ou vazio, retornar como está
        if not dominios_outros or dominios_outros.lower() == "n/a":
            result["_aia_n3_dominio_outro"] = "N/A"
            return result
        
        # Validar os domínios afeitos outros
        dominios_outros_validados = []
        
        # Dividir os domínios afeitos outros retornados pela IA
        dominios_outros_list = dominios_outros.split(';')
        for dominio in dominios_outros_list:
            dominio = dominio.strip()
            if dominio and dominio in dominios_afeitos_outros:
                dominios_outros_validados.append(dominio)
            else:
                logger.warning(f"Domínio afeito outro '{dominio}' não está na lista de domínios disponíveis")
        
        # Atualizar o resultado com os domínios validados
        if dominios_outros_validados:
            result["_aia_n3_dominio_outro"] = "; ".join(dominios_outros_validados)
        else:
            logger.warning("Nenhum domínio afeito outro válido encontrado")
            result["_aia_n3_dominio_outro"] = "N/A"
        
        logger.info(f"Domínios afeitos outros validados: {result.get('_aia_n3_dominio_outro', '')}")
        return result
    
    def _validate_categories(self, result, aia_data):
        """
        Valida se as categorias retornadas pela IA estão na lista de categorias permitidas.
        Se não estiverem, tenta encontrar a categoria mais próxima ou retorna uma mensagem de erro.
        
        Args:
            result: Dicionário com as categorias retornadas pela IA
            aia_data: Lista de categorias do arquivo aia.json
            
        Returns:
            Dicionário com as categorias validadas
        """
        logger.info("Validando categorias retornadas pela IA")
        
        # Se não temos dados de AIA, não podemos validar
        if not aia_data:
            logger.warning("Sem dados de AIA para validar categorias")
            return result
        
        # Extrair as categorias retornadas pela IA
        macroarea = result.get("_aia_n1_macroarea", "")
        segmento = result.get("_aia_n2_segmento", "")
        dominio_afeito = result.get("_aia_n3_dominio_afeito", "")
        
        # Coletar todas as macroáreas, segmentos e domínios disponíveis
        macroareas_disponiveis = set()
        segmentos_disponiveis = {}  # Mapeamento de macroárea para seus segmentos
        dominios_disponiveis = {}   # Mapeamento de segmento para seus domínios
        
        # Log para depuração
        logger.info(f"Validando contra {len(aia_data)} categorias disponíveis")
        
        for item in aia_data:
            item_macroarea = item.get('Macroárea', '')
            item_segmento = item.get('Segmento', '')
            
            if item_macroarea:
                macroareas_disponiveis.add(item_macroarea)
                
                if item_macroarea not in segmentos_disponiveis:
                    segmentos_disponiveis[item_macroarea] = set()
                
                if item_segmento:
                    segmentos_disponiveis[item_macroarea].add(item_segmento)
                    
                    if item_segmento not in dominios_disponiveis:
                        dominios_disponiveis[item_segmento] = set()
                    
                    dominios = item.get('Domínios Afeitos', '').split(';')
                    for dominio in dominios:
                        dominio = dominio.strip()
                        if dominio:
                            dominios_disponiveis[item_segmento].add(dominio)
        
        # Log para depuração
        logger.info(f"Macroáreas disponíveis: {macroareas_disponiveis}")
        
        # Validar a macroárea
        if macroarea and macroarea not in macroareas_disponiveis:
            logger.warning(f"Macroárea '{macroarea}' não está na lista de macroáreas disponíveis")
            
            # Tentar encontrar a macroárea mais próxima
            if macroareas_disponiveis:
                # Usar a primeira macroárea disponível como fallback
                macroarea_corrigida = next(iter(macroareas_disponiveis))
                logger.info(f"Substituindo macroárea '{macroarea}' por '{macroarea_corrigida}'")
                result["_aia_n1_macroarea"] = macroarea_corrigida
                macroarea = macroarea_corrigida
            else:
                logger.error("Nenhuma macroárea disponível para substituição")
                result["_aia_n1_macroarea"] = ""
                macroarea = ""
        
        # Log para depuração
        if macroarea:
            logger.info(f"Segmentos disponíveis para macroárea '{macroarea}': {segmentos_disponiveis.get(macroarea, set())}")
        
        # Validar o segmento (apenas se temos uma macroárea válida)
        if macroarea and segmento:
            segmentos_da_macroarea = segmentos_disponiveis.get(macroarea, set())
            if segmento not in segmentos_da_macroarea:
                logger.warning(f"Segmento '{segmento}' não está na lista de segmentos disponíveis para a macroárea '{macroarea}'")
                # Tentar encontrar o segmento mais próximo
                if segmentos_da_macroarea:
                    # Usar o primeiro segmento disponível como fallback
                    segmento_corrigido = next(iter(segmentos_da_macroarea))
                    logger.info(f"Substituindo segmento '{segmento}' por '{segmento_corrigido}'")
                    result["_aia_n2_segmento"] = segmento_corrigido
                    segmento = segmento_corrigido
                else:
                    logger.error(f"Nenhum segmento disponível para a macroárea '{macroarea}'")
                    result["_aia_n2_segmento"] = ""
                    segmento = ""
        
        # Log para depuração
        if segmento:
            logger.info(f"Domínios disponíveis para segmento '{segmento}': {dominios_disponiveis.get(segmento, set())}")
        
        # Validar os domínios afeitos (apenas se temos um segmento válido)
        if segmento and dominio_afeito:
            dominios_do_segmento = dominios_disponiveis.get(segmento, set())
            dominios_afeitos_validados = []
            
            # Dividir os domínios afeitos retornados pela IA
            dominios_afeitos = dominio_afeito.split(';')
            for dominio in dominios_afeitos:
                dominio = dominio.strip()
                if dominio and dominio in dominios_do_segmento:
                    dominios_afeitos_validados.append(dominio)
                else:
                    logger.warning(f"Domínio '{dominio}' não está na lista de domínios disponíveis para o segmento '{segmento}'")
            
            # Atualizar o resultado com os domínios validados
            if dominios_afeitos_validados:
                result["_aia_n3_dominio_afeito"] = "; ".join(dominios_afeitos_validados)
            else:
                logger.warning(f"Nenhum domínio válido encontrado para o segmento '{segmento}'")
                result["_aia_n3_dominio_afeito"] = ""
        
        logger.info(f"Categorias validadas: {json.dumps(result, indent=2, ensure_ascii=False)}")
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
