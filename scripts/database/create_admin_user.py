from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash
import getpass

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def create_admin_user():
    """
    Cria um usuário administrador no banco de dados.
    """
    try:
        # Criar aplicação Flask com contexto
        app = create_app()
        
        # Criar usuário dentro do contexto da aplicação
        with app.app_context():
            # Verificar se já existe algum usuário
            user_count = Usuario.query.count()
            if user_count > 0:
                print(f"Já existem {user_count} usuários no banco de dados.")
                create_anyway = input("Deseja criar um novo usuário mesmo assim? (s/n): ")
                if create_anyway.lower() != 's':
                    print("Operação cancelada pelo usuário.")
                    return False
            
            # Solicitar informações do usuário
            print("\n--- Criação de Usuário Administrador ---")
            email = input("Email: ")
            nome = input("Nome completo: ")
            password = getpass.getpass("Senha: ")
            confirm_password = getpass.getpass("Confirme a senha: ")
            
            # Validar informações
            if not email or '@' not in email:
                print("Erro: Email inválido.")
                return False
            
            if not nome:
                print("Erro: Nome não pode ser vazio.")
                return False
            
            if password != confirm_password:
                print("Erro: As senhas não coincidem.")
                return False
            
            if len(password) < 6:
                print("Erro: A senha deve ter pelo menos 6 caracteres.")
                return False
            
            # Verificar se o usuário já existe
            existing_user = Usuario.query.filter_by(email=email).first()
            if existing_user:
                print(f"Erro: Já existe um usuário com o email {email}.")
                return False
            
            # Criar o usuário
            user = Usuario(
                email=email,
                nome=nome,
                role='admin'  # Definir como administrador
            )
            user.set_password(password)
            
            # Salvar no banco de dados
            db.session.add(user)
            db.session.commit()
            
            print(f"\nUsuário administrador criado com sucesso!")
            print(f"Email: {email}")
            print(f"Nome: {nome}")
            print(f"Função: administrador")
            
            return True
    
    except Exception as e:
        print(f"Erro ao criar usuário administrador: {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando criação de usuário administrador...")
    success = create_admin_user()
    
    if success:
        print("\nProcesso concluído com sucesso!")
    else:
        print("\nProcesso concluído com erros. Verifique as mensagens acima.")
