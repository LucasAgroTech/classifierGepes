#!/usr/bin/env python3
from app import create_app, db
from app.models import CategoriaLista
from app.helpers import get_tecverde_categories
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Script para listar as categorias de tecnologias verdes do banco de dados.
    """
    app = create_app()
    with app.app_context():
        logger.info("Listando categorias de tecnologias verdes...")
        
        # Obter todas as categorias de tecnologias verdes
        tecverde_classes, tecverde_subclasses = get_tecverde_categories()
        
        # Exibir classes
        print("\n=== CLASSES DE TECNOLOGIAS VERDES ===")
        if tecverde_classes:
            for classe, descricao in tecverde_classes.items():
                print(f"- {classe}: {descricao}")
        else:
            print("Nenhuma classe de tecnologia verde encontrada.")
        
        # Exibir subclasses
        print("\n=== SUBCLASSES DE TECNOLOGIAS VERDES ===")
        if tecverde_subclasses:
            for classe, subclasses in tecverde_subclasses.items():
                print(f"- {classe}:")
                if ';' in subclasses:
                    subclasses_list = [s.strip() for s in subclasses.split(';') if s.strip()]
                    for subclasse in subclasses_list:
                        print(f"  * {subclasse}")
                else:
                    print(f"  * {subclasses}")
        else:
            print("Nenhuma subclasse de tecnologia verde encontrada.")
        
        # Exibir todas as categorias no formato original do banco de dados
        print("\n=== CATEGORIAS NO FORMATO DO BANCO DE DADOS ===")
        try:
            # Consultar diretamente sem tentar acessar o campo descricao
            classes = db.session.query(
                CategoriaLista.id, 
                CategoriaLista.tipo, 
                CategoriaLista.valor, 
                CategoriaLista.ativo
            ).filter_by(tipo='tecverde_classe', ativo=True).all()
            
            subclasses = db.session.query(
                CategoriaLista.id, 
                CategoriaLista.tipo, 
                CategoriaLista.valor, 
                CategoriaLista.ativo
            ).filter_by(tipo='tecverde_subclasse', ativo=True).all()
            
            print("\nClasses:")
            for c in classes:
                print(f"ID: {c.id}, Tipo: {c.tipo}, Valor: {c.valor}, Ativo: {c.ativo}")
            
            print("\nSubclasses:")
            for s in subclasses:
                print(f"ID: {s.id}, Tipo: {s.tipo}, Valor: {s.valor}, Ativo: {s.ativo}")
        except Exception as e:
            logger.error(f"Erro ao listar categorias do banco de dados: {str(e)}")
            print("Erro ao listar categorias do banco de dados. Veja o log para mais detalhes.")

if __name__ == "__main__":
    main()
