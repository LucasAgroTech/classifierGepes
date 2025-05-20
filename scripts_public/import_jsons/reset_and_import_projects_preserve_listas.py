#!/usr/bin/env python3
import sys
import os

# Adicionar o diretório raiz ao path do Python para permitir importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts_public.import_jsons.reset_projetos_table_preserve_listas import reset_projetos_table_preserve_listas
from scripts_public.import_jsons.import_projects_fixed import main as import_projects_main

def main():
    """
    Script para resetar as tabelas do banco (preservando a tabela 'categoria_listas')
    e em seguida importar novos projetos de um arquivo JSON.
    
    Uso: python reset_and_import_projects_preserve_listas.py <arquivo_json>
    """
    # Verificar argumentos
    if len(sys.argv) != 2:
        print("Uso: python reset_and_import_projects_preserve_listas.py <arquivo_json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    # Verificar se o arquivo existe
    if not os.path.isfile(json_file):
        print(f"Erro: Arquivo não encontrado: {json_file}")
        sys.exit(1)
    
    print("=" * 80)
    print("ETAPA 1: Resetando as tabelas (preservando 'categoria_listas')...")
    print("=" * 80)
    
    # Resetar as tabelas (preservando 'categoria_listas')
    success = reset_projetos_table_preserve_listas()
    
    if not success:
        print("Erro ao resetar as tabelas. Abortando importação.")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("ETAPA 2: Importando novos projetos do arquivo JSON...")
    print("=" * 80)
    
    # Substituir sys.argv para a função import_projects_main
    # Isso é necessário porque a função main() em import_projects.py usa sys.argv
    original_argv = sys.argv.copy()
    sys.argv = ['import_projects.py', json_file]
    
    try:
        # Importar projetos
        import_projects_main()
    except Exception as e:
        print(f"Erro durante a importação de projetos: {str(e)}")
        sys.exit(1)
    finally:
        # Restaurar sys.argv
        sys.argv = original_argv
    
    print("\n" + "=" * 80)
    print("Processo de reset e importação concluído com sucesso!")
    print("=" * 80)

if __name__ == "__main__":
    main()
