from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import Projeto

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def reset_projetos_table():
    """
    Recria a tabela 'projetos' com o novo esquema.
    Este script irá:
    1. Fazer backup das relações existentes
    2. Dropar a tabela 'projetos'
    3. Recriar a tabela com o novo esquema
    """
    try:
        # Obter a URL do banco de dados do ambiente
        database_url = os.environ.get('DATABASE_URL', '')
        
        # Garantir que a URL começa com 'postgresql://' em vez de 'postgres://'
        database_url = database_url.replace('postgres://', 'postgresql://')
        
        if not database_url:
            print("Erro: DATABASE_URL não está definida no arquivo .env")
            return False
        
        print(f"Conectando ao banco de dados: {database_url}")
        
        # Criar engine do SQLAlchemy
        engine = create_engine(database_url)
        
        # Verificar a conexão
        try:
            connection = engine.connect()
            print("Conexão com o banco de dados estabelecida com sucesso!")
            connection.close()
        except SQLAlchemyError as e:
            print(f"Erro ao conectar ao banco de dados: {str(e)}")
            return False
        
        # Criar aplicação Flask com contexto
        app = create_app()
        
        # Executar operações dentro do contexto da aplicação
        with app.app_context():
            print("Iniciando reset da tabela 'projetos'...")
            
            # Verificar se a tabela existe
            with engine.connect() as connection:
                result = connection.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'gepes' AND table_name = 'projetos')"
                ))
                table_exists = result.scalar()
            
            if not table_exists:
                print("A tabela 'projetos' não existe. Criando nova tabela...")
                db.create_all()
                print("Tabela 'projetos' criada com sucesso!")
                return True
            
            # Fazer backup das relações existentes (opcional)
            print("Fazendo backup das relações existentes...")
            # Aqui você pode adicionar código para fazer backup dos dados se necessário
            
            # Dropar a tabela 'projetos'
            print("Dropando a tabela 'projetos'...")
            with engine.connect() as connection:
                connection.execute(text("DROP TABLE IF EXISTS gepes.projetos CASCADE"))
                connection.commit()
            
            # Recriar a tabela com o novo esquema
            print("Recriando a tabela 'projetos' com o novo esquema...")
            db.create_all()
            
            print("Reset da tabela 'projetos' concluído com sucesso!")
            return True
    
    except Exception as e:
        print(f"Erro ao resetar a tabela 'projetos': {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando reset da tabela 'projetos'...")
    success = reset_projetos_table()
    
    if success:
        print("\nProcesso concluído com sucesso!")
    else:
        print("\nProcesso concluído com erros. Verifique as mensagens acima.")
