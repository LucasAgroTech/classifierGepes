import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60 + "\n")

def main():
    """
    Script principal para configuração do banco de dados.
    Permite criar o esquema, tabelas e um usuário administrador.
    """
    print_header("CONFIGURAÇÃO DO BANCO DE DADOS GEPES CLASSIFIER")
    
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
    
    # Menu de opções
    while True:
        print("\nEscolha uma opção:")
        print("1. Criar esquema e tabelas")
        print("2. Criar usuário administrador")
        print("3. Executar ambos (1 e 2)")
        print("0. Sair")
        
        choice = input("\nOpção: ")
        
        if choice == '1':
            # Importar e executar o script de criação de tabelas
            print_header("CRIAÇÃO DE ESQUEMA E TABELAS")
            from scripts_public.create_tables import create_schema_and_tables
            success = create_schema_and_tables()
            
            if not success:
                print("Erro ao criar esquema e tabelas. Verifique as mensagens acima.")
                continue
        
        elif choice == '2':
            # Importar e executar o script de criação de usuário administrador
            print_header("CRIAÇÃO DE USUÁRIO ADMINISTRADOR")
            from create_admin_user import create_admin_user
            success = create_admin_user()
            
            if not success:
                print("Erro ao criar usuário administrador. Verifique as mensagens acima.")
                continue
        
        elif choice == '3':
            # Executar ambos os scripts
            print_header("CRIAÇÃO DE ESQUEMA E TABELAS")
            from scripts_public.create_tables import create_schema_and_tables
            success1 = create_schema_and_tables()
            
            if not success1:
                print("Erro ao criar esquema e tabelas. Verifique as mensagens acima.")
                continue
            
            print_header("CRIAÇÃO DE USUÁRIO ADMINISTRADOR")
            from create_admin_user import create_admin_user
            success2 = create_admin_user()
            
            if not success2:
                print("Erro ao criar usuário administrador. Verifique as mensagens acima.")
                continue
            
            print_header("CONFIGURAÇÃO CONCLUÍDA")
            print("Esquema, tabelas e usuário administrador criados com sucesso!")
            print("Agora você pode executar a aplicação com 'python run.py'")
        
        elif choice == '0':
            print("\nSaindo do programa...")
            break
        
        else:
            print("\nOpção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()
