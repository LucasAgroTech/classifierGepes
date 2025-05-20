import os
import json
from app.ai_integration import OpenAIClient
from dotenv import load_dotenv
from app import create_app, db
from app.models import CategoriaLista

# Carregar variáveis de ambiente
load_dotenv()

def debug_categories():
    """
    Depura a função _get_categories_lists() para verificar se está obtendo corretamente
    as categorias do banco de dados e mantendo a estrutura hierárquica.
    """
    # Criar a aplicação Flask
    app = create_app()
    
    # Criar um contexto de aplicação
    with app.app_context():
        # Obter a chave da API OpenAI do ambiente
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("Aviso: Chave da API OpenAI não encontrada. Usando uma chave fictícia para teste.")
            api_key = "fake_key"
        
        # Criar um cliente OpenAI
        client = OpenAIClient(api_key)
        
        # Obter as categorias do banco de dados
        print("Obtendo categorias do banco de dados...")
        categories_lists = client._get_categories_lists()
        
        # Imprimir as listas de categorias
        print("\nListas de categorias:")
        for tipo, valores in categories_lists.items():
            if tipo != 'dominios_por_microarea_segmento':
                print(f"\n{tipo.capitalize()}:")
                for valor in valores:
                    print(f"  - {valor}")
        
        # Imprimir a estrutura hierárquica
        print("\nEstrutura hierárquica:")
        dominios_por_microarea_segmento = categories_lists.get('dominios_por_microarea_segmento', {})
        
        for macroarea, segmentos in dominios_por_microarea_segmento.items():
            print(f"\nMacroárea: {macroarea}")
            
            for segmento, dominios in segmentos.items():
                print(f"  Segmento: {segmento}")
                
                if dominios:
                    print("    Domínios Afeitos:")
                    for dominio in dominios:
                        print(f"      - {dominio}")
        
        # Obter os dados de AIA
        print("\nDados de AIA:")
        aia_data = client._get_aia_data_from_db() if hasattr(client, '_get_aia_data_from_db') else []
        print(json.dumps(aia_data, indent=2, ensure_ascii=False))
        
        # Obter as classes e subclasses de tecnologias verdes
        print("\nClasses de Tecnologias Verdes:")
        tecverde_classes = client._get_tecverde_classes()
        for classe, descricao in tecverde_classes.items():
            print(f"  - {classe}: {descricao}")
        
        print("\nSubclasses de Tecnologias Verdes:")
        tecverde_subclasses = client._get_tecverde_subclasses()
        for classe, subclasses in tecverde_subclasses.items():
            print(f"  - {classe}: {subclasses}")
        
        # Verificar se há categorias no banco de dados
        categorias_count = CategoriaLista.query.count()
        print(f"\nTotal de categorias no banco de dados: {categorias_count}")
        
        if categorias_count == 0:
            print("\nAVISO: Não há categorias no banco de dados. Isso pode causar problemas na classificação.")
            print("Considere adicionar categorias ao banco de dados antes de usar a integração com a IA.")

if __name__ == "__main__":
    debug_categories()
