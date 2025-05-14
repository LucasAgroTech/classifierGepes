import os
import sys
import json
from dotenv import load_dotenv
from reset_projetos_table import reset_projetos_table
from import_json_data import import_json_data

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60 + "\n")

def migrate_production():
    """
    Executa a migração em produção:
    1. Reseta a tabela 'projetos' com o novo esquema
    2. Importa os dados do JSON para a tabela
    """
    print_header("MIGRAÇÃO DA TABELA PROJETOS EM PRODUÇÃO")
    
    # Verificar se o arquivo .env existe e contém as configurações necessárias
    if not os.path.exists('.env'):
        print("Erro: Arquivo .env não encontrado.")
        print("Crie um arquivo .env com as configurações necessárias.")
        return False
    
    database_url = os.environ.get('DATABASE_URL', '')
    if not database_url:
        print("Erro: DATABASE_URL não está definida no arquivo .env")
        print("Adicione a URL do banco de dados ao arquivo .env.")
        return False
    
    # Solicitar confirmação do usuário
    print("\nATENÇÃO: Esta operação irá resetar a tabela 'projetos' e importar novos dados.")
    print("Todos os dados existentes na tabela serão perdidos.")
    confirmation = input("\nDeseja continuar? (s/n): ")
    
    if confirmation.lower() != 's':
        print("Operação cancelada pelo usuário.")
        return False
    
    # Solicitar o caminho do arquivo JSON
    json_file = input("\nDigite o caminho para o arquivo JSON com os dados dos projetos: ")
    
    # Verificar se o arquivo existe
    if not os.path.exists(json_file):
        print(f"Erro: Arquivo {json_file} não encontrado.")
        return False
    
    # Verificar se o arquivo é um JSON válido
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            json.load(file)
    except json.JSONDecodeError:
        print(f"Erro: O arquivo {json_file} não é um JSON válido.")
        return False
    except Exception as e:
        print(f"Erro ao ler o arquivo {json_file}: {str(e)}")
        return False
    
    # Passo 1: Resetar a tabela 'projetos'
    print_header("RESETANDO A TABELA 'PROJETOS'")
    reset_success = reset_projetos_table()
    
    if not reset_success:
        print("Erro ao resetar a tabela 'projetos'. Operação abortada.")
        return False
    
    # Passo 2: Importar os dados do JSON
    print_header("IMPORTANDO DADOS DO JSON")
    import_success = import_json_data(json_file)
    
    if not import_success:
        print("Erro ao importar dados do JSON. Verifique as mensagens acima.")
        return False
    
    print_header("MIGRAÇÃO CONCLUÍDA COM SUCESSO")
    print("A tabela 'projetos' foi resetada e os novos dados foram importados com sucesso.")
    
    return True

if __name__ == "__main__":
    success = migrate_production()
    
    if success:
        print("\nProcesso de migração concluído com sucesso!")
        sys.exit(0)
    else:
        print("\nProcesso de migração concluído com erros. Verifique as mensagens acima.")
        sys.exit(1)
