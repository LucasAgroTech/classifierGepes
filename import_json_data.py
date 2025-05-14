import json
import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import Projeto
from sqlalchemy.exc import SQLAlchemyError

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def import_json_data(json_file_path):
    """
    Importa dados de um arquivo JSON para a tabela 'projetos'.
    
    Args:
        json_file_path: Caminho para o arquivo JSON contendo os dados dos projetos
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(json_file_path):
            print(f"Erro: Arquivo {json_file_path} não encontrado.")
            return False
        
        # Carregar dados do arquivo JSON
        print(f"Carregando dados do arquivo {json_file_path}...")
        with open(json_file_path, 'r', encoding='utf-8') as file:
            projects_data = json.load(file)
        
        print(f"Carregados {len(projects_data)} projetos do arquivo JSON.")
        
        # Criar aplicação Flask com contexto
        app = create_app()
        
        # Importar dados dentro do contexto da aplicação
        with app.app_context():
            # Limpar dados existentes na tabela (opcional)
            print("Limpando dados existentes na tabela 'projetos'...")
            db.session.query(Projeto).delete()
            db.session.commit()
            
            # Importar novos dados
            print("Importando novos dados para a tabela 'projetos'...")
            projects_added = 0
            
            for project_data in projects_data:
                try:
                    # Função para converter valores não numéricos para None
                    def convert_to_int_or_none(value):
                        if value is None:
                            return None
                        try:
                            return int(value)
                        except (ValueError, TypeError):
                            return None
                    
                    # Criar novo objeto Projeto com os dados do JSON
                    new_project = Projeto(
                        codigo_projeto=project_data.get('codigo_projeto'),
                        unidade_embrapii=project_data.get('unidade_embrapii'),
                        data_contrato=project_data.get('data_contrato'),
                        data_inicio=project_data.get('data_inicio'),
                        data_termino=project_data.get('data_termino'),
                        status=project_data.get('status'),
                        tipo_projeto=project_data.get('tipo_projeto'),
                        parceria_programa=project_data.get('parceria_programa'),
                        call=project_data.get('call'),
                        cooperacao_internacional=project_data.get('cooperacao_internacional'),
                        modalidade_financiamento=project_data.get('modalidade_financiamento'),
                        uso_recurso_obrigatorio=project_data.get('uso_recurso_obrigatorio'),
                        # Converter valores não numéricos para None
                        tecnologia_habilitadora=None if project_data.get('tecnologia_habilitadora') in ['Não definido', 'Não se aplica'] else project_data.get('tecnologia_habilitadora'),
                        missoes_cndi=None if project_data.get('missoes_cndi') in ['Não definido', 'Não se aplica'] else project_data.get('missoes_cndi'),
                        area_aplicacao=None if project_data.get('area_aplicacao') in ['Não definido', 'Não se aplica'] else project_data.get('area_aplicacao'),
                        projeto=project_data.get('projeto'),
                        trl_inicial=project_data.get('trl_inicial'),
                        trl_final=project_data.get('trl_final'),
                        valor_embrapii=project_data.get('valor_embrapii'),
                        valor_empresa=project_data.get('valor_empresa'),
                        valor_unidade_embrapii=project_data.get('valor_unidade_embrapii'),
                        titulo=project_data.get('titulo'),
                        titulo_publico=project_data.get('titulo_publico'),
                        objetivo=project_data.get('objetivo'),
                        descricao_publica=project_data.get('descricao_publica'),
                        data_avaliacao=project_data.get('data_avaliacao'),
                        nota_avaliacao=project_data.get('nota_avaliacao'),
                        observacoes=project_data.get('observacoes'),
                        tags=project_data.get('tags'),
                        data_extracao_dados=project_data.get('data_extracao_dados'),
                        brasil_mais_produtivo=project_data.get('brasil_mais_produtivo'),
                        valor_sebrae=project_data.get('valor_sebrae'),
                        codigo_negociacao=project_data.get('codigo_negociacao'),
                        macroentregas=convert_to_int_or_none(project_data.get('macroentregas')),
                        pct_aceites=project_data.get('pct_aceites'),
                        _fonte_recurso=project_data.get('_fonte_recurso'),
                        _sebrae=project_data.get('_sebrae'),
                        _valor_total=project_data.get('_valor_total'),
                        _perc_valor_embrapii=project_data.get('_perc_valor_embrapii'),
                        _perc_valor_empresa=project_data.get('_perc_valor_empresa'),
                        _perc_valor_sebrae=project_data.get('_perc_valor_sebrae'),
                        _perc_valor_unidade_embrapii=project_data.get('_perc_valor_unidade_embrapii'),
                        _perc_valor_empresa_sebrae=project_data.get('_perc_valor_empresa_sebrae'),
                        _aia_n1_macroarea=project_data.get('_aia_n1_macroarea'),
                        _aia_n2_segmento=project_data.get('_aia_n2_segmento'),
                        _aia_n3_dominio_afeito=project_data.get('_aia_n3_dominio_afeito'),
                        _aia_n3_dominio_outro=project_data.get('_aia_n3_dominio_outro'),
                        ai_rating_aia=convert_to_int_or_none(project_data.get('ai_rating_aia')),
                        ai_rating_tecverde=convert_to_int_or_none(project_data.get('ai_rating_tecverde'))
                    )
                    
                    # Adicionar à sessão
                    db.session.add(new_project)
                    projects_added += 1
                    
                    # Commit a cada 100 projetos para evitar sobrecarga de memória
                    if projects_added % 100 == 0:
                        db.session.commit()
                        print(f"Importados {projects_added} projetos...")
                
                except SQLAlchemyError as e:
                    # Rollback the session to recover from database errors
                    db.session.rollback()
                    print(f"Erro de banco de dados ao importar projeto {project_data.get('codigo_projeto')}: {str(e)}")
                    continue
                except Exception as e:
                    print(f"Erro ao importar projeto {project_data.get('codigo_projeto')}: {str(e)}")
                    continue
            
            # Commit final
            db.session.commit()
            print(f"Importação concluída. Total de {projects_added} projetos importados com sucesso.")
            
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
    json_file = input("Digite o caminho para o arquivo JSON com os dados dos projetos: ")
    
    print(f"Iniciando importação de dados do arquivo {json_file}...")
    success = import_json_data(json_file)
    
    if success:
        print("\nProcesso concluído com sucesso!")
    else:
        print("\nProcesso concluído com erros. Verifique as mensagens acima.")
