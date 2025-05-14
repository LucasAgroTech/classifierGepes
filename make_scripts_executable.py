#!/usr/bin/env python3
import os
import stat
import sys

def make_executable(file_path):
    """
    Adiciona permissão de execução a um arquivo.
    """
    try:
        # Obter as permissões atuais
        current_permissions = os.stat(file_path).st_mode
        
        # Adicionar permissão de execução para o proprietário, grupo e outros
        new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        
        # Aplicar as novas permissões
        os.chmod(file_path, new_permissions)
        
        print(f"Permissões de execução adicionadas a: {file_path}")
        return True
    except Exception as e:
        print(f"Erro ao adicionar permissões a {file_path}: {str(e)}")
        return False

def main():
    """
    Função principal para tornar os scripts executáveis.
    """
    # Lista de scripts para tornar executáveis
    scripts = [
        'import_projects.py',
        'import_categories.py',
        'import_json_data.py',
        'test_import_categories.py',
        'create_tables.py',
        'create_admin_user.py',
        'setup_database.py',
        'run.py'
    ]
    
    success_count = 0
    error_count = 0
    
    print("Tornando scripts executáveis...")
    
    for script in scripts:
        if os.path.isfile(script):
            if make_executable(script):
                success_count += 1
            else:
                error_count += 1
        else:
            print(f"Arquivo não encontrado: {script}")
            error_count += 1
    
    print(f"\nProcesso concluído: {success_count} scripts tornados executáveis, {error_count} erros.")

if __name__ == "__main__":
    main()
