#!/usr/bin/env python3
import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

def check_file_exists(file_path, description):
    """
    Verifica se um arquivo existe e exibe uma mensagem apropriada.
    """
    if os.path.isfile(file_path):
        print(f"✅ {description} encontrado: {file_path}")
        return True
    else:
        print(f"❌ {description} não encontrado: {file_path}")
        return False

def check_json_valid(file_path):
    """
    Verifica se um arquivo JSON é válido.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        if isinstance(json_data, list):
            print(f"✅ Arquivo JSON válido: {file_path} (contém {len(json_data)} projetos)")
            return True
        else:
            print(f"❌ Arquivo JSON inválido: {file_path} (não é uma lista)")
            return False
    except json.JSONDecodeError as e:
        print(f"❌ Arquivo JSON inválido: {file_path} (erro de decodificação: {str(e)})")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar arquivo JSON: {file_path} ({str(e)})")
        return False

def check_database_connection():
    """
    Verifica a conexão com o banco de dados.
    """
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Obter a URL do banco de dados
    database_url = os.environ.get('DATABASE_URL', '')
    
    # Garantir que a URL começa com 'postgresql://' em vez de 'postgres://'
    database_url = database_url.replace('postgres://', 'postgresql://')
    
    if not database_url:
        print("❌ DATABASE_URL não está definida no arquivo .env")
        return False
    
    try:
        # Criar engine do SQLAlchemy
        engine = create_engine(database_url)
        
        # Verificar a conexão
        connection = engine.connect()
        
        # Verificar se o esquema 'gepes' existe
        result = connection.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'gepes'"))
        schema_exists = result.fetchone() is not None
        
        if schema_exists:
            print("✅ Conexão com o banco de dados estabelecida com sucesso!")
            print("✅ Esquema 'gepes' encontrado no banco de dados")
        else:
            print("✅ Conexão com o banco de dados estabelecida com sucesso!")
            print("❌ Esquema 'gepes' não encontrado no banco de dados")
            print("   Execute 'python create_tables.py' para criar o esquema e as tabelas")
        
        # Verificar se a tabela 'projetos' existe
        result = connection.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'gepes' AND table_name = 'projetos'"
        ))
        table_exists = result.fetchone() is not None
        
        if table_exists:
            print("✅ Tabela 'projetos' encontrada no esquema 'gepes'")
        else:
            print("❌ Tabela 'projetos' não encontrada no esquema 'gepes'")
            print("   Execute 'python create_tables.py' para criar as tabelas")
        
        connection.close()
        return schema_exists and table_exists
    
    except SQLAlchemyError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado ao verificar banco de dados: {str(e)}")
        return False

def main():
    """
    Função principal para verificar a configuração de importação.
    """
    print("Verificando configuração para importação de projetos...\n")
    
    # Verificar arquivos necessários
    files_ok = True
    files_ok &= check_file_exists('import_projects.py', 'Script de importação')
    files_ok &= check_file_exists('.env', 'Arquivo de configuração')
    
    # Verificar arquivo JSON de exemplo
    json_file = 'example_projects.json'
    json_exists = check_file_exists(json_file, 'Arquivo JSON de exemplo')
    
    if json_exists:
        json_valid = check_json_valid(json_file)
    else:
        json_valid = False
    
    # Verificar conexão com o banco de dados
    print("\nVerificando conexão com o banco de dados...")
    db_ok = check_database_connection()
    
    # Resumo
    print("\nResumo da verificação:")
    if files_ok:
        print("✅ Todos os arquivos necessários estão presentes")
    else:
        print("❌ Alguns arquivos necessários estão faltando")
    
    if json_valid:
        print("✅ Arquivo JSON de exemplo é válido")
    else:
        print("❌ Arquivo JSON de exemplo é inválido ou não existe")
    
    if db_ok:
        print("✅ Banco de dados está configurado corretamente")
    else:
        print("❌ Banco de dados não está configurado corretamente")
    
    # Conclusão
    if files_ok and json_valid and db_ok:
        print("\n✅ Tudo pronto para importação de projetos!")
        print("   Execute 'python import_projects.py example_projects.json' para importar os projetos de exemplo")
    else:
        print("\n❌ Alguns problemas foram encontrados. Corrija-os antes de prosseguir com a importação.")

if __name__ == "__main__":
    main()
