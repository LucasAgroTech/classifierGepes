#!/usr/bin/env python3
from app import create_app, db
from app.helpers import add_tecverde_categories
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Script para adicionar categorias de tecnologias verdes ao banco de dados.
    """
    app = create_app()
    with app.app_context():
        logger.info("Iniciando adição de categorias de tecnologias verdes...")
        
        # Limpar categorias existentes (opcional)
        try:
            # Remover classes existentes
            db.session.query(db.models.CategoriaLista).filter_by(tipo='tecverde_classe').delete()
            # Remover subclasses existentes
            db.session.query(db.models.CategoriaLista).filter_by(tipo='tecverde_subclasse').delete()
            db.session.commit()
            logger.info("Categorias existentes removidas com sucesso.")
        except Exception as e:
            db.session.rollback()
            logger.warning(f"Não foi possível remover categorias existentes: {str(e)}")
        
        # Adicionar novas categorias
        result = add_tecverde_categories()
        if result:
            logger.info("Categorias de tecnologias verdes adicionadas com sucesso!")
        else:
            logger.error("Falha ao adicionar categorias de tecnologias verdes.")

if __name__ == "__main__":
    main()
