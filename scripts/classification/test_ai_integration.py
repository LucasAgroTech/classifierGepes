import os
import json
from app.ai_integration import OpenAIClient
from dotenv import load_dotenv
from app import create_app, db

# Carregar variáveis de ambiente (incluindo a chave da API OpenAI)
load_dotenv()

def test_ai_integration():
    """
    Testa a integração com a API OpenAI para sugerir categorias para um projeto.
    """
    # Obter a chave da API OpenAI do ambiente
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("Erro: Chave da API OpenAI não encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
        return
    
    # Criar a aplicação Flask
    app = create_app()
    
    # Criar um contexto de aplicação
    with app.app_context():
        # Criar um cliente OpenAI
        client = OpenAIClient(api_key)
        
        # Criar um projeto de exemplo
        project = {
            'id': 1,
            'titulo': 'Sistema de Monitoramento de Energia Renovável',
            'titulo_publico': 'EcoEnergy Monitor',
            'objetivo': 'Desenvolver um sistema inteligente para monitoramento e otimização de consumo de energia renovável em edifícios comerciais.',
            'descricao_publica': 'O projeto visa criar uma plataforma que integra sensores IoT com algoritmos de inteligência artificial para monitorar, analisar e otimizar o consumo de energia renovável em edifícios comerciais. O sistema permitirá a detecção de padrões de consumo, identificação de anomalias e sugestão de ajustes para maximizar a eficiência energética.',
            'tags': 'energia renovável, eficiência energética, IoT, inteligência artificial, sustentabilidade'
        }
        
        print("Testando a integração com a API OpenAI...")
        print(f"Projeto: {project['titulo']}")
        
        # Chamar o método suggest_categories
        print("\nObtendo sugestões da IA...")
        suggestions = client.suggest_categories(project)
        
        # Verificar se houve erro
        if 'error' in suggestions:
            print(f"Erro: {suggestions['error']}")
            return
        
        # Imprimir o resultado formatado
        print("\nResultado:")
        print(json.dumps(suggestions, indent=2, ensure_ascii=False))
        
        # Imprimir as categorias sugeridas
        print("\nCategorias sugeridas:")
        print(f"Macroárea: {suggestions.get('_aia_n1_macroarea', '')}")
        print(f"Segmento: {suggestions.get('_aia_n2_segmento', '')}")
        print(f"Domínios Afeitos: {suggestions.get('_aia_n3_dominio_afeito', '')}")
        print(f"Domínios Afeitos Outros: {suggestions.get('_aia_n3_dominio_outro', '')}")
        print(f"Confiança: {suggestions.get('confianca', '')}")
        print(f"Justificativa: {suggestions.get('justificativa', '')}")
        
        # Imprimir as tecnologias verdes sugeridas
        print("\nTecnologias Verdes:")
        print(f"Se Aplica: {'Sim' if suggestions.get('tecverde_se_aplica', False) else 'Não'}")
        if suggestions.get('tecverde_se_aplica', False):
            print(f"Classe: {suggestions.get('tecverde_classe', '')}")
            print(f"Subclasse: {suggestions.get('tecverde_subclasse', '')}")
        print(f"Confiança: {suggestions.get('tecverde_confianca', '')}")
        print(f"Justificativa: {suggestions.get('tecverde_justificativa', '')}")

if __name__ == "__main__":
    test_ai_integration()
