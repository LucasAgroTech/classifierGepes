#!/usr/bin/env python3
from app import create_app, db
from flask_migrate import Migrate, upgrade
from app.helpers import add_tecverde_categories
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Script para configurar as categorias de tecnologias verdes no banco de dados.
    Este script executa as seguintes etapas:
    1. Executa a migração para adicionar a coluna 'descricao' à tabela 'categoria_listas'
    2. Adiciona as categorias de tecnologias verdes ao banco de dados
    """
    app = create_app()
    
    # Configurar migração
    migrate = Migrate(app, db)
    
    with app.app_context():
        try:
            # Etapa 1: Executar migração
            logger.info("Executando migração para adicionar coluna 'descricao'...")
            upgrade(directory='migrations', revision='add_descricao_to_categoria_listas')
            logger.info("Migração concluída com sucesso!")
            
            # Etapa 2: Adicionar categorias de tecnologias verdes
            logger.info("Adicionando categorias de tecnologias verdes...")
            result = add_tecverde_categories()
            if result:
                logger.info("Categorias de tecnologias verdes adicionadas com sucesso!")
            else:
                logger.error("Falha ao adicionar categorias de tecnologias verdes.")
                
            logger.info("Configuração concluída!")
        except Exception as e:
            logger.error(f"Erro durante a configuração: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    main()
