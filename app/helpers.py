from app.models import CategoriaLista, db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_tecverde_categories():
    """
    Adiciona categorias de tecnologias verdes ao banco de dados se não existirem.
    Isso inclui classes e subclasses de tecnologias verdes.
    """
    # Classes de tecnologias verdes com descrições
    tecverde_classes_with_desc = {
        "Transporte": "Tecnologias verdes no setor de transporte compreendem soluções que visam reduzir as emissões de gases de efeito estufa e minimizar impactos ambientais associados à mobilidade de pessoas e cargas. Elas promovem a transição para meios de transporte mais eficientes, limpos e sustentáveis, como veículos elétricos e híbridos, transporte ferroviário e aquaviário de baixo carbono, sistemas de compartilhamento baseados em TIC e combustíveis alternativos, priorizando o uso racional de recursos e a mitigação da poluição.",
        "Energia": "As tecnologias verdes de energia englobam a produção, armazenamento, transporte e uso de energia de forma sustentável, com baixa ou nenhuma emissão de carbono. Incluem fontes renováveis (como solar, eólica, hidrelétrica, biomassa e geotérmica), tecnologias de hidrogênio, eficiência energética, redes inteligentes e armazenamento de energia. Essas soluções buscam substituir tecnologias convencionais altamente poluentes, contribuindo para a mitigação das mudanças climáticas e o uso eficiente dos recursos naturais.",
        "Poluição e Resíduos": "Tecnologias verdes nesta classe tratam da prevenção, controle e remediação da poluição do ar, da água e do solo, bem como da gestão sustentável de resíduos. Incluem sistemas de monitoramento, reciclagem, reaproveitamento, coleta eficiente, tratamento e disposição final segura de resíduos. Também compreendem soluções para evitar a geração de resíduos e emissões tóxicas, priorizando a redução na fonte e a economia circular.",
        "Água": "As tecnologias verdes voltadas à água abrangem soluções para o uso sustentável dos recursos hídricos, assegurando qualidade e disponibilidade. Incluem sistemas de captação, tratamento, reutilização, dessalinização, irrigação eficiente, controle de perdas e proteção contra eventos climáticos extremos como enchentes e erosão costeira. Estas tecnologias promovem o uso racional da água e a proteção dos ecossistemas aquáticos.",
        "Agricultura e Silvicultura": "Englobam tecnologias verdes que tornam a produção agrícola e florestal mais sustentável, eficiente e resiliente. Isso inclui agricultura de precisão, sistemas de irrigação inteligentes, cultivares resistentes, manejo sustentável do solo e da água, reflorestamento, restauração ecológica e uso de insumos agrícolas menos poluentes. Também envolvem ferramentas digitais e de sensoriamento remoto para monitoramento ambiental e planejamento do uso da terra.",
        "Produtos, Materiais e Processos": "Tecnologias verdes nesta categoria envolvem a concepção e fabricação de produtos e materiais que demandem menos recursos naturais, gerem menos poluição e possam ser reutilizados, reciclados ou compostados. Incluem materiais biodegradáveis ou de base biológica, processos industriais mais limpos, extração mineral sustentável e produtos que reduzem o consumo de energia ou água ao longo de seu ciclo de vida.",
        "Construção e Edificações": "Soluções tecnológicas que tornam o setor da construção mais sustentável, incluindo materiais de baixo impacto ambiental, sistemas de aquecimento e refrigeração eficientes, isolamento térmico, iluminação eficiente, eletrodomésticos sustentáveis e planejamento urbano ecológico. Essas tecnologias buscam reduzir as emissões e o consumo energético das edificações ao longo de sua vida útil, contribuindo para cidades mais resilientes e habitáveis."
    }
    
    # Subclasses de tecnologias verdes
    tecverde_subclasses = {
        "Transporte": "Soluções de transporte baseadas em TIC (Tecnologias da Informação e Comunicação); Motores de combustão interna aprimorados; Veículos elétricos / híbridos; Transporte marítimo / hidroviário; Aeronáutica / Aviação; Transporte rodoviário; Transporte ferroviário",
        "Energia": "Hidrogênio e células a combustível; Engenharia elétrica; TIC na energia e na gestão energética; Transmissão e distribuição de energia; Eficiência energética; Armazenamento de energia; Geração de energia (Outras fontes renováveis); Recuperação de calor residual; Conversão de resíduos em energia; Biomassa/Bioenergia; Ondas/Maraé/Oceano; Geotérmica; Térmica; Hidrelétrica; Eólica; Solar",
        "Poluição e Resíduos": "TIC na gestão de poluição e resíduos; Detecção, medição, monitoramento e remoção da poluição; Desperdício de alimentos; Tratamento de resíduos sólidos; Reciclagem e reutilização; Coleta e transporte de resíduos; Descarte de resíduos; Evitação de resíduos; Biorremediação; Medição e monitoramento de gases de efeito estufa; Captura e armazenamento de carbono; Carvão limpo; Solo; Tratamento de águas residuais; Ar",
        "Água": "Saneamento; Proteção costeira; Controle de enchentes; Transporte e distribuição de água; Avaliação, monitoramento e controle de reservas de água; Dessalinização; Extração de água; Tratamento de água; Eficiência no uso da água; Armazenamento de água",
        "Agricultura e Silvicultura": "Estufas e ambientes internos; SIG e observação da Terra; Gestão do uso da terra; TIC na agricultura; Cultivo tolerante ao estresse; Variedades de plantas e animais; Piscicultura (aquicultura); Produção florestal (silvicultura); Insumos agrícolas melhorados; Pecuária; Processamento de alimentos; Prevenção de riscos e sistemas de alerta precoce; Restauração e conservação de florestas, biodiversidade e ecossistemas; Tecnologias agrícolas; Colheita e armazenamento; Irrigação; Melhoria do solo",
        "Produtos, Materiais e Processos": "Materiais aprimorados; Mineração e metais; Moda e têxteis sustentáveis; Processos químicos e industriais; Produtos que economizam água/energia; Produtos de base biológica; Produtos biodegradáveis/biocompatíveis; Produtos que evitam emissões tóxicas ou outras; Materiais de embalagem e tecidos",
        "Construção e Edificações": "TIC em edifícios e gestão urbana; Eletrodomésticos; Material de construção; Iluminação; Aquecimento, resfriamento, ventilação, bombas de calor; Isolamento térmico; Planejamento urbano; Edificações"
    }
    
    try:
        # Adicionar classes de tecnologias verdes
        for classe, descricao in tecverde_classes_with_desc.items():
            # Verificar se a classe já existe
            existing_class = CategoriaLista.query.filter_by(
                tipo='tecverde_classe',
                valor=classe
            ).first()
            
            if not existing_class:
                # Criar nova classe - sem usar o campo descricao
                new_class = CategoriaLista(
                    tipo='tecverde_classe',
                    valor=classe,
                    ativo=True
                )
                db.session.add(new_class)
                logger.info(f"Adicionada classe de tecnologia verde: {classe}")
        
        # Adicionar subclasses de tecnologias verdes
        for classe, subclasses in tecverde_subclasses.items():
            # Verificar se a subclasse já existe
            existing_subclass = CategoriaLista.query.filter_by(
                tipo='tecverde_subclasse',
                valor=f"{classe}|{subclasses}"
            ).first()
            
            if not existing_subclass:
                # Criar nova subclasse
                new_subclass = CategoriaLista(
                    tipo='tecverde_subclasse',
                    valor=f"{classe}|{subclasses}",
                    ativo=True
                )
                db.session.add(new_subclass)
                logger.info(f"Adicionadas subclasses para a classe de tecnologia verde: {classe}")
        
        # Commit das alterações
        db.session.commit()
        logger.info("Categorias de tecnologias verdes adicionadas com sucesso")
        
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao adicionar categorias de tecnologias verdes: {str(e)}")
        return False

def get_tecverde_categories():
    """
    Retorna as categorias de tecnologias verdes do banco de dados.
    
    Returns:
        tuple: (classes, subclasses) onde:
            - classes é um dicionário com as classes de tecnologias verdes
            - subclasses é um dicionário com as subclasses de tecnologias verdes
    """
    tecverde_classes = {}
    tecverde_subclasses = {}
    
    # Descrições das classes (hardcoded por enquanto)
    class_descriptions = {
        "Transporte": "Tecnologias verdes no setor de transporte compreendem soluções que visam reduzir as emissões de gases de efeito estufa e minimizar impactos ambientais associados à mobilidade de pessoas e cargas.",
        "Energia": "As tecnologias verdes de energia englobam a produção, armazenamento, transporte e uso de energia de forma sustentável, com baixa ou nenhuma emissão de carbono.",
        "Poluição e Resíduos": "Tecnologias verdes nesta classe tratam da prevenção, controle e remediação da poluição do ar, da água e do solo, bem como da gestão sustentável de resíduos.",
        "Água": "As tecnologias verdes voltadas à água abrangem soluções para o uso sustentável dos recursos hídricos, assegurando qualidade e disponibilidade.",
        "Agricultura e Silvicultura": "Englobam tecnologias verdes que tornam a produção agrícola e florestal mais sustentável, eficiente e resiliente.",
        "Produtos, Materiais e Processos": "Tecnologias verdes nesta categoria envolvem a concepção e fabricação de produtos e materiais que demandem menos recursos naturais, gerem menos poluição e possam ser reutilizados, reciclados ou compostados.",
        "Construção e Edificações": "Soluções tecnológicas que tornam o setor da construção mais sustentável, incluindo materiais de baixo impacto ambiental, sistemas de aquecimento e refrigeração eficientes, isolamento térmico, iluminação eficiente."
    }
    
    try:
        # Buscar classes de tecnologias verdes
        classes = CategoriaLista.query.filter_by(tipo='tecverde_classe', ativo=True).all()
        for classe in classes:
            nome_classe = classe.valor
            # Usar a descrição hardcoded em vez de tentar acessar o campo descricao
            descricao = class_descriptions.get(nome_classe, "Tecnologia verde")
            tecverde_classes[nome_classe] = descricao
        
        # Buscar subclasses de tecnologias verdes
        subclasses = CategoriaLista.query.filter_by(tipo='tecverde_subclasse', ativo=True).all()
        for subclasse in subclasses:
            valor = subclasse.valor
            if '|' in valor:
                partes = valor.split('|')
                if len(partes) >= 2:
                    classe = partes[0].strip()
                    subclasses_str = partes[1].strip()
                    tecverde_subclasses[classe] = subclasses_str
        
        return tecverde_classes, tecverde_subclasses
    except Exception as e:
        logger.error(f"Erro ao obter categorias de tecnologias verdes: {str(e)}")
        return {}, {}
