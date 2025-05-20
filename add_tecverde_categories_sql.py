#!/usr/bin/env python3
from app import create_app, db
import logging
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_tecverde_categories_sql():
    """
    Adiciona categorias de tecnologias verdes ao banco de dados usando SQL direto.
    """
    # Classes de tecnologias verdes com descrições
    tecverde_classes = {
        "Transporte": "Tecnologias verdes no setor de transporte compreendem soluções que visam reduzir as emissões de gases de efeito estufa e minimizar impactos ambientais associados à mobilidade de pessoas e cargas.",
        "Energia": "As tecnologias verdes de energia englobam a produção, armazenamento, transporte e uso de energia de forma sustentável, com baixa ou nenhuma emissão de carbono.",
        "Poluição e Resíduos": "Tecnologias verdes nesta classe tratam da prevenção, controle e remediação da poluição do ar, da água e do solo, bem como da gestão sustentável de resíduos.",
        "Água": "As tecnologias verdes voltadas à água abrangem soluções para o uso sustentável dos recursos hídricos, assegurando qualidade e disponibilidade.",
        "Agricultura e Silvicultura": "Englobam tecnologias verdes que tornam a produção agrícola e florestal mais sustentável, eficiente e resiliente.",
        "Produtos, Materiais e Processos": "Tecnologias verdes nesta categoria envolvem a concepção e fabricação de produtos e materiais que demandem menos recursos naturais, gerem menos poluição e possam ser reutilizados, reciclados ou compostados.",
        "Construção e Edificações": "Soluções tecnológicas que tornam o setor da construção mais sustentável, incluindo materiais de baixo impacto ambiental, sistemas de aquecimento e refrigeração eficientes, isolamento térmico, iluminação eficiente."
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
        # Obter conexão direta com o banco de dados
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        
        # Limpar categorias existentes
        logger.info("Removendo categorias existentes...")
        cursor.execute("DELETE FROM gepes.categoria_listas WHERE tipo = 'tecverde_classe'")
        cursor.execute("DELETE FROM gepes.categoria_listas WHERE tipo = 'tecverde_subclasse'")
        
        # Adicionar classes
        logger.info("Adicionando classes de tecnologias verdes...")
        for classe in tecverde_classes:
            cursor.execute(
                "INSERT INTO gepes.categoria_listas (tipo, valor, ativo) VALUES (%s, %s, %s)",
                ('tecverde_classe', classe, True)
            )
            logger.info(f"Adicionada classe: {classe}")
        
        # Adicionar subclasses
        logger.info("Adicionando subclasses de tecnologias verdes...")
        for classe, subclasses in tecverde_subclasses.items():
            # Formar o valor completo (classe + subclasses)
            valor = f"{classe}|{subclasses}"
            
            cursor.execute(
                "INSERT INTO gepes.categoria_listas (tipo, valor, ativo) VALUES (%s, %s, %s)",
                ('tecverde_subclasse', valor, True)
            )
            logger.info(f"Adicionadas subclasses para: {classe}")
        
        # Commit das alterações
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("Categorias de tecnologias verdes adicionadas com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao adicionar categorias de tecnologias verdes: {str(e)}")
        if 'connection' in locals() and connection:
            connection.rollback()
            cursor.close()
            connection.close()
        return False

def main():
    """
    Script para adicionar categorias de tecnologias verdes ao banco de dados.
    """
    app = create_app()
    with app.app_context():
        logger.info("Iniciando adição de categorias de tecnologias verdes...")
        result = add_tecverde_categories_sql()
        if result:
            logger.info("Categorias de tecnologias verdes adicionadas com sucesso!")
        else:
            logger.error("Falha ao adicionar categorias de tecnologias verdes.")

if __name__ == "__main__":
    main()
