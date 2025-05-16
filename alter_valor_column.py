#!/usr/bin/env python3
from app import create_app, db
from flask_migrate import Migrate, upgrade
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Script para alterar o tipo da coluna 'valor' na tabela 'categoria_listas' de VARCHAR(255) para TEXT.
    """
    app = create_app()
    
    # Configurar migração
    migrate = Migrate(app, db)
    
    with app.app_context():
        try:
            # Executar migração diretamente usando SQL
            logger.info("Executando SQL para alterar o tipo da coluna 'valor' para TEXT...")
            
            # Obter conexão direta com o banco de dados
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            try:
                # Alterar o tipo da coluna valor para TEXT
                cursor.execute("""
                    ALTER TABLE gepes.categoria_listas 
                    ALTER COLUMN valor TYPE TEXT
                """)
                
                # Commit das alterações
                connection.commit()
                logger.info("SQL executado com sucesso!")
            except Exception as e:
                logger.error(f"Erro ao executar SQL: {str(e)}")
                connection.rollback()
                raise
            finally:
                cursor.close()
                connection.close()
            logger.info("Migração concluída com sucesso!")
            
            logger.info("A coluna 'valor' agora pode armazenar textos de qualquer tamanho.")
        except Exception as e:
            logger.error(f"Erro durante a migração: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    main()
