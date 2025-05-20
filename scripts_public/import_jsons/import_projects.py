#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app import create_app, db
from app.models import Projeto

def convert_timestamp_to_date(timestamp):
    """
    Converte um timestamp em milissegundos para um objeto datetime.date
    """
    if not timestamp:
        return None
    
    # Converter de milissegundos para segundos
    seconds = timestamp / 1000.0
    
    # Criar objeto datetime e retornar apenas a data
    return datetime.fromtimestamp(seconds).date()

def import_projects(json_data):
    """
    Importa projetos do JSON para o banco de dados.
    Apenas insere novos projetos, ignorando os existentes.
    """
    # Contador de estatísticas
    stats = {
        'total': 0,
        'inserted': 0,
        'skipped': 0,
        'errors': 0
    }
    
    # Lista para armazenar erros
    errors = []
    
    # Processar cada projeto no JSON
    for project_data in json_data:
        stats['total'] += 1
        
        try:
            # Verificar se o projeto já existe
            codigo_projeto = project_data.get('codigo_projeto')
            if not codigo_projeto:
                raise ValueError(f"Projeto sem código: {project_data}")
            
            existing_project = Projeto.query.filter_by(codigo_projeto=codigo_projeto).first()
            
            if existing_project:
                print(f"Projeto já existe: {codigo_projeto} - Ignorando")
                stats['skipped'] += 1
                continue
            
            # Converter campos de data
            data_contrato = convert_timestamp_to_date(project_data.get('data_contrato'))
            data_avaliacao = convert_timestamp_to_date(project_data.get('data_avaliacao'))
            
            # Calcular valor total
            valor_embrapii = float(project_data.get('valor_embrapii', 0) or 0)
            valor_empresa = float(project_data.get('valor_empresa', 0) or 0)
            valor_unidade_embrapii = float(project_data.get('valor_unidade_embrapii', 0) or 0)
            valor_total = valor_embrapii + valor_empresa + valor_unidade_embrapii
            
            # Calcular percentuais
            perc_valor_embrapii = round((valor_embrapii / valor_total) * 100, 2) if valor_total > 0 else 0
            perc_valor_empresa_sebrae = round((valor_empresa / valor_total) * 100, 2) if valor_total > 0 else 0
            perc_valor_unidade_embrapii = round((valor_unidade_embrapii / valor_total) * 100, 2) if valor_total > 0 else 0
            
            # Criar novo projeto
            new_project = Projeto(
                codigo_projeto=codigo_projeto,
                codigo_interno=project_data.get('codigo_negociacao'),
                unidade_embrapii=project_data.get('unidade_embrapii'),
                tipo_projeto=project_data.get('tipo_projeto'),
                status=project_data.get('status'),
                titulo=project_data.get('titulo', ''),
                titulo_publico=project_data.get('titulo_publico'),
                objetivo=project_data.get('objetivo'),
                descricao_publica=project_data.get('descricao_publica'),
                data_contrato=data_contrato,
                data_avaliacao=data_avaliacao,
                observacoes=project_data.get('observacoes'),
                tags=project_data.get('tags'),
                valor_total=valor_total,
                perc_valor_embrapii=perc_valor_embrapii,
                perc_valor_empresa_sebrae=perc_valor_empresa_sebrae,
                perc_valor_unidade_embrapii=perc_valor_unidade_embrapii,
                _aia_n1_macroarea=project_data.get('_aia_n1_macroarea'),
                _aia_n2_segmento=project_data.get('_aia_n2_segmento'),
                _aia_n3_dominio_afeito=project_data.get('_aia_n3_dominio_afeito'),
                _aia_n3_dominio_outro=project_data.get('_aia_n3_dominio_outro')
            )
            
            # Adicionar ao banco de dados
            db.session.add(new_project)
            db.session.commit()
            
            print(f"Projeto inserido: {codigo_projeto}")
            stats['inserted'] += 1
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"Erro ao processar projeto {project_data.get('codigo_projeto', 'desconhecido')}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)
            stats['errors'] += 1
    
    # Retornar estatísticas e erros
    return stats, errors

def main():
    """
    Função principal para importar projetos de um arquivo JSON.
    """
    # Verificar argumentos
    if len(sys.argv) != 2:
        print("Uso: python import_projects.py <arquivo_json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    # Verificar se o arquivo existe
    if not os.path.isfile(json_file):
        print(f"Erro: Arquivo não encontrado: {json_file}")
        sys.exit(1)
    
    try:
        # Ler o arquivo JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Verificar se o JSON é uma lista
        if not isinstance(json_data, list):
            print("Erro: O arquivo JSON deve conter uma lista de projetos")
            sys.exit(1)
        
        # Criar aplicação Flask com contexto
        app = create_app()
        
        # Importar projetos dentro do contexto da aplicação
        with app.app_context():
            print(f"Iniciando importação de {len(json_data)} projetos...")
            stats, errors = import_projects(json_data)
            
            # Exibir estatísticas
            print("\nEstatísticas de importação:")
            print(f"Total de projetos processados: {stats['total']}")
            print(f"Projetos inseridos: {stats['inserted']}")
            print(f"Projetos ignorados (já existentes): {stats['skipped']}")
            print(f"Erros: {stats['errors']}")
            
            # Exibir erros
            if errors:
                print("\nErros encontrados:")
                for error in errors:
                    print(f"- {error}")
            
            print("\nImportação concluída!")
    
    except json.JSONDecodeError:
        print(f"Erro: O arquivo {json_file} não contém JSON válido")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
