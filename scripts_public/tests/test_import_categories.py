#!/usr/bin/env python3
import os
import sys
from scripts_public.import_jsons.import_categories import import_categories_data

def main():
    """
    Script para testar a importação de categorias a partir do arquivo example_categories.json
    """
    # Verificar se o arquivo example_categories.json existe
    json_file = 'example_categories.json'
    
    if not os.path.exists(json_file):
        print(f"Erro: Arquivo {json_file} não encontrado.")
        sys.exit(1)
    
    print(f"Iniciando importação de dados do arquivo {json_file}...")
    success = import_categories_data(json_file)
    
    if success:
        print("\nProcesso concluído com sucesso!")
    else:
        print("\nProcesso concluído com erros. Verifique as mensagens acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
