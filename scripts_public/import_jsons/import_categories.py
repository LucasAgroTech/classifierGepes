import json
import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório raiz ao Python path para permitir importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import CategoriaLista
from sqlalchemy.exc import SQLAlchemyError

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def import_categories_data(json_file_path):
    """
    Importa dados de categorias de um arquivo JSON para a tabela 'categoria_listas'.
    
    Args:
        json_file_path: Caminho para o arquivo JSON contendo os dados das categorias
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(json_file_path):
            print(f"Erro: Arquivo {json_file_path} não encontrado.")
            return False
        
        # Carregar dados do arquivo JSON
        print(f"Carregando dados do arquivo {json_file_path}...")
        with open(json_file_path, 'r', encoding='utf-8') as file:
            categories_data = json.load(file)
        
        print(f"Carregados {len(categories_data)} itens do arquivo JSON.")
        
        # Criar aplicação Flask com contexto
        app = create_app()
        
        # Importar dados dentro do contexto da aplicação
        with app.app_context():
            # Limpar dados existentes na tabela (opcional)
            print("Limpando dados existentes na tabela 'categoria_listas'...")
            db.session.query(CategoriaLista).delete()
            db.session.commit()
            
            # Importar novos dados
            print("Importando novos dados para a tabela 'categoria_listas'...")
            categories_added = 0
            
            # Conjuntos para rastrear itens únicos
            macroáreas = set()
            segmentos = {}  # {macroárea: [segmentos]}
            dominios = {}   # {segmento: [dominios]}
            
            # Primeiro passo: coletar todas as categorias únicas
            for item in categories_data:
                macroárea = item.get('Macroárea')
                segmento = item.get('Segmento')
                dominios_afeitos = item.get('Domínios Afeitos', '')
                
                # Adicionar macroárea ao conjunto
                if macroárea and macroárea not in macroáreas:
                    macroáreas.add(macroárea)
                
                # Adicionar segmento à lista da macroárea
                if macroárea and segmento:
                    if macroárea not in segmentos:
                        segmentos[macroárea] = []
                    if segmento not in segmentos[macroárea]:
                        segmentos[macroárea].append(segmento)
                
                # Processar domínios afeitos
                if segmento and dominios_afeitos:
                    if segmento not in dominios:
                        dominios[segmento] = []
                    
                    # Dividir os domínios por ponto e vírgula
                    dominio_list = [d.strip() for d in dominios_afeitos.split(';') if d.strip()]
                    
                    # Adicionar cada domínio à lista do segmento
                    for dominio in dominio_list:
                        if dominio not in dominios[segmento]:
                            dominios[segmento].append(dominio)
            
            # Segundo passo: inserir macroáreas
            print("Inserindo macroáreas...")
            for macroárea in macroáreas:
                try:
                    new_category = CategoriaLista(
                        tipo='macroárea',
                        valor=macroárea,
                        ativo=True
                    )
                    db.session.add(new_category)
                    categories_added += 1
                except SQLAlchemyError as e:
                    db.session.rollback()
                    print(f"Erro ao inserir macroárea '{macroárea}': {str(e)}")
                    continue
            
            # Commit após inserir todas as macroáreas
            db.session.commit()
            print(f"Inseridas {len(macroáreas)} macroáreas.")
            
            # Terceiro passo: inserir segmentos
            print("Inserindo segmentos...")
            segmentos_count = 0
            for macroárea, segmento_list in segmentos.items():
                for segmento in segmento_list:
                    try:
                        new_category = CategoriaLista(
                            tipo='segmento',
                            valor=f"{macroárea}|{segmento}",  # Formato: "Macroárea|Segmento"
                            ativo=True
                        )
                        db.session.add(new_category)
                        segmentos_count += 1
                    except SQLAlchemyError as e:
                        db.session.rollback()
                        print(f"Erro ao inserir segmento '{segmento}' da macroárea '{macroárea}': {str(e)}")
                        continue
            
            # Commit após inserir todos os segmentos
            db.session.commit()
            print(f"Inseridos {segmentos_count} segmentos.")
            categories_added += segmentos_count
            
            # Quarto passo: inserir domínios
            print("Inserindo domínios...")
            dominios_count = 0
            for segmento, dominio_list in dominios.items():
                # Encontrar a macroárea correspondente ao segmento
                macroárea_do_segmento = None
                for macroárea, segmento_list in segmentos.items():
                    if segmento in segmento_list:
                        macroárea_do_segmento = macroárea
                        break
                
                if not macroárea_do_segmento:
                    print(f"Aviso: Não foi possível encontrar a macroárea para o segmento '{segmento}'")
                    continue
                
                for dominio in dominio_list:
                    try:
                        new_category = CategoriaLista(
                            tipo='dominio',
                            valor=f"{macroárea_do_segmento}|{segmento}|{dominio}",  # Formato: "Macroárea|Segmento|Domínio"
                            ativo=True
                        )
                        db.session.add(new_category)
                        dominios_count += 1
                    except SQLAlchemyError as e:
                        db.session.rollback()
                        print(f"Erro ao inserir domínio '{dominio}' do segmento '{segmento}': {str(e)}")
                        continue
            
            # Commit após inserir todos os domínios
            db.session.commit()
            print(f"Inseridos {dominios_count} domínios.")
            categories_added += dominios_count
            
            print(f"Importação concluída. Total de {categories_added} categorias importadas com sucesso.")
            
            return True
    
    except SQLAlchemyError as e:
        # Ensure session is rolled back in case of database errors
        if 'db' in locals() and hasattr(db, 'session'):
            db.session.rollback()
        print(f"Erro de banco de dados: {str(e)}")
        return False
    except Exception as e:
        print(f"Erro ao importar dados: {str(e)}")
        return False

if __name__ == "__main__":
    # Solicitar o caminho do arquivo JSON
    json_file = input("Digite o caminho para o arquivo JSON com os dados das categorias: ")
    
    print(f"Iniciando importação de dados do arquivo {json_file}...")
    success = import_categories_data(json_file)
    
    if success:
        print("\nProcesso concluído com sucesso!")
    else:
        print("\nProcesso concluído com erros. Verifique as mensagens acima.")
