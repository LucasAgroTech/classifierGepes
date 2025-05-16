#!/usr/bin/env python3
from app import create_app, db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Script para listar as categorias de tecnologias verdes do banco de dados usando SQL direto.
    """
    app = create_app()
    with app.app_context():
        logger.info("Listando categorias de tecnologias verdes...")
        
        try:
            # Obter conexão direta com o banco de dados
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            # Consultar classes
            cursor.execute(
                "SELECT id, tipo, valor, ativo FROM gepes.categoria_listas WHERE tipo = 'tecverde_classe' AND ativo = true"
            )
            classes = cursor.fetchall()
            
            # Consultar subclasses
            cursor.execute(
                "SELECT id, tipo, valor, ativo FROM gepes.categoria_listas WHERE tipo = 'tecverde_subclasse' AND ativo = true"
            )
            subclasses = cursor.fetchall()
            
            # Fechar cursor e conexão
            cursor.close()
            connection.close()
            
            # Processar classes para exibição
            print("\n=== CLASSES DE TECNOLOGIAS VERDES ===")
            if classes:
                for c in classes:
                    id, tipo, valor, ativo = c
                    print(f"- {valor}")
            else:
                print("Nenhuma classe de tecnologia verde encontrada.")
            
            # Processar subclasses para exibição
            print("\n=== SUBCLASSES DE TECNOLOGIAS VERDES ===")
            if subclasses:
                for s in subclasses:
                    id, tipo, valor, ativo = s
                    if '|' in valor:
                        classe, subclasses_str = valor.split('|', 1)
                        print(f"- {classe}:")
                        if ';' in subclasses_str:
                            subclasses_list = [s.strip() for s in subclasses_str.split(';') if s.strip()]
                            for subclasse in subclasses_list:
                                print(f"  * {subclasse}")
                        else:
                            print(f"  * {subclasses_str}")
            else:
                print("Nenhuma subclasse de tecnologia verde encontrada.")
            
            # Exibir todas as categorias no formato original do banco de dados
            print("\n=== CATEGORIAS NO FORMATO DO BANCO DE DADOS ===")
            print("\nClasses:")
            for c in classes:
                id, tipo, valor, ativo = c
                print(f"ID: {id}, Tipo: {tipo}, Valor: {valor}, Ativo: {ativo}")
            
            print("\nSubclasses:")
            for s in subclasses:
                id, tipo, valor, ativo = s
                print(f"ID: {id}, Tipo: {tipo}, Valor: {valor}, Ativo: {ativo}")
            
        except Exception as e:
            logger.error(f"Erro ao listar categorias do banco de dados: {str(e)}")
            print("Erro ao listar categorias do banco de dados. Veja o log para mais detalhes.")

if __name__ == "__main__":
    main()
