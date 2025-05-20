#!/usr/bin/env python3
"""
Script para executar o gerenciador de categorias do GEPES Classifier.

Este script inicia o servidor Flask com as rotas de gerenciamento de categorias
ativadas, permitindo testar e utilizar as funcionalidades de gerenciamento
hierárquico de categorias.
"""

from app import create_app
import os
import sys

def main():
    """Função principal para iniciar o servidor Flask."""
    try:
        # Verificar se a variável de ambiente FLASK_APP está definida
        if 'FLASK_APP' not in os.environ:
            os.environ['FLASK_APP'] = 'run.py'
        
        # Verificar se a variável de ambiente FLASK_ENV está definida
        if 'FLASK_ENV' not in os.environ:
            os.environ['FLASK_ENV'] = 'development'
        
        # Criar a aplicação Flask
        app = create_app()
        
        # Definir o host e a porta
        host = os.environ.get('FLASK_HOST', '127.0.0.1')
        port = int(os.environ.get('FLASK_PORT', 5000))
        
        # Iniciar o servidor
        print(f"Iniciando o servidor em {host}:{port}...")
        print("Acesse o gerenciador de categorias em: http://127.0.0.1:5000/categories/manage")
        print("Pressione CTRL+C para encerrar o servidor.")
        
        app.run(host=host, port=port, debug=True)
        
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
