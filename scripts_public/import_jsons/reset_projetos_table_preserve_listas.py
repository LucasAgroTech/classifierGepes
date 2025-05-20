import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path do Python para permitir importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app, db
from app.models import Projeto, CategoriaLista

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def reset_projetos_table_preserve_listas():
    """
    Recria todas as tabelas do banco, exceto a tabela 'categoria_listas'.
    Este script irá:
    1. Fazer backup das listas de categorias
    2. Dropar todas as tabelas exceto 'categoria_listas'
    3. Recriar as tabelas com o novo esquema
    4. Restaurar as listas de categorias (não necessário pois a tabela é preservada)
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
            print("Iniciando reset das tabelas (preservando 'categoria_listas')...")
            
            # Verificar se as tabelas existem
            with engine.connect() as connection:
                result = connection.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'gepes' AND table_name = 'projetos')"
                ))
                projetos_exists = result.scalar()
                
                result = connection.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'gepes' AND table_name = 'categoria_listas')"
                ))
                categoria_listas_exists = result.scalar()
            
            if not projetos_exists and not categoria_listas_exists:
                print("As tabelas não existem. Criando novas tabelas...")
                db.create_all()
                print("Tabelas criadas com sucesso!")
                return True
            
            # Dropar todas as tabelas exceto 'categoria_listas'
            print("Dropando tabelas (exceto 'categoria_listas')...")
            with engine.connect() as connection:
                # Dropar tabelas com relações primeiro
                connection.execute(text("DROP TABLE IF EXISTS gepes.ai_ratings CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS gepes.ai_suggestions CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS gepes.logs CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS gepes.classificacoes_adicionais CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS gepes.tecnologias_verdes CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS gepes.categorias CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS gepes.projetos CASCADE"))
                connection.execute(text("DROP TABLE IF EXISTS gepes.usuarios CASCADE"))
                connection.commit()
            
            # Recriar as tabelas com o novo esquema
            print("Recriando as tabelas com o novo esquema...")
            db.create_all()
            
            print("Reset das tabelas (preservando 'categoria_listas') concluído com sucesso!")
            return True
    
    except Exception as e:
        print(f"Erro ao resetar as tabelas: {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando reset das tabelas (preservando 'categoria_listas')...")
    success = reset_projetos_table_preserve_listas()
    
    if success:
        print("\nProcesso concluído com sucesso!")
    else:
        print("\nProcesso concluído com erros. Verifique as mensagens acima.")
