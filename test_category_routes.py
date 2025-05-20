#!/usr/bin/env python3
"""
Script para testar as rotas de gerenciamento de categorias.
"""

import requests
import sys
import os

def test_manage_categories_route():
    """Testa se a rota de gerenciamento de categorias está acessível."""
    try:
        # URL base (ajuste conforme necessário)
        base_url = "http://localhost:5000"
        
        # Testar a rota de gerenciamento de categorias
        response = requests.get(f"{base_url}/categories/manage")
        
        # Verificar se a resposta é um redirecionamento para login (302) ou página carregada (200)
        if response.status_code in [200, 302]:
            print(f"✅ Rota /categories/manage está funcionando (status: {response.status_code})")
            return True
        else:
            print(f"❌ Erro ao acessar a rota /categories/manage (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar a rota: {str(e)}")
        return False

def test_add_category_route():
    """Testa se a rota para adicionar categorias está acessível."""
    try:
        # URL base (ajuste conforme necessário)
        base_url = "http://localhost:5000"
        
        # Dados para teste
        test_data = {
            "tipo": "macroárea",
            "valor": "Teste Automatizado"
        }
        
        # Testar a rota para adicionar categorias
        response = requests.post(f"{base_url}/categories/add", json=test_data)
        
        # Verificar se a resposta é um redirecionamento para login (302) ou sucesso (200)
        if response.status_code in [200, 302]:
            print(f"✅ Rota /categories/add está funcionando (status: {response.status_code})")
            return True
        else:
            print(f"❌ Erro ao acessar a rota /categories/add (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar a rota: {str(e)}")
        return False

def main():
    """Função principal para executar os testes."""
    print("Testando rotas de gerenciamento de categorias...")
    
    # Verificar se o servidor está rodando
    try:
        requests.get("http://localhost:5000")
    except requests.exceptions.ConnectionError:
        print("❌ O servidor não está rodando. Inicie o servidor com 'python run.py' antes de executar este teste.")
        sys.exit(1)
    
    # Executar testes
    manage_result = test_manage_categories_route()
    add_result = test_add_category_route()
    
    # Verificar resultados
    if manage_result and add_result:
        print("✅ Todos os testes passaram!")
        sys.exit(0)
    else:
        print("❌ Alguns testes falharam.")
        sys.exit(1)

if __name__ == "__main__":
    main()
