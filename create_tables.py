from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import Usuario, Projeto, Categoria, TecnologiaVerde, CategoriaLista, ClassificacaoAdicional, Log, AISuggestion, AIRating

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def create_schema_and_tables():
    """
    Cria o esquema 'gepes' e todas as tabelas definidas nos modelos.
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
        
        # Criar o esquema 'gepes' se não existir
        with engine.connect() as connection:
            print("Criando esquema 'gepes' se não existir...")
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS gepes"))
            connection.commit()
            print("Esquema 'gepes' criado ou já existente.")
        
        # Criar aplicação Flask com contexto
        app = create_app()
        
        # Criar todas as tabelas dentro do contexto da aplicação
        with app.app_context():
            print("Criando todas as tabelas definidas nos modelos...")
            db.create_all()
            print("Tabelas criadas com sucesso!")
            
            # Listar as tabelas criadas
            print("\nTabelas criadas:")
            for table in db.metadata.tables:
                print(f"- {table}")
        
        return True
    
    except Exception as e:
        print(f"Erro ao criar esquema e tabelas: {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando criação de esquema e tabelas...")
    success = create_schema_and_tables()
    
    if success:
        print("\nProcesso concluído com sucesso!")
    else:
        print("\nProcesso concluído com erros. Verifique as mensagens acima.")
