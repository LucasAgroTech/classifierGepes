"""
Example script to demonstrate how to use auto_classify_projects.py with a sample project.
This can be used to test the classification functionality without accessing the database.
"""

import os
from dotenv import load_dotenv
from app.ai_integration import OpenAIClient

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("Error: OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        return
    
    # Create OpenAI client
    client = OpenAIClient(api_key)
    
    # Sample project
    sample_project = {
        'id': 999,
        'titulo': 'Sistema de Monitoramento de Energia Renovável',
        'titulo_publico': 'EcoEnergy Monitor',
        'objetivo': 'Desenvolver um sistema inteligente para monitoramento e otimização de consumo de energia renovável em edifícios comerciais.',
        'descricao_publica': 'O projeto visa criar uma plataforma que integra sensores IoT com algoritmos de inteligência artificial para monitorar, analisar e otimizar o consumo de energia renovável em edifícios comerciais. O sistema permitirá a detecção de padrões de consumo, identificação de anomalias e sugestão de ajustes para maximizar a eficiência energética.',
        'tags': 'energia renovável, eficiência energética, IoT, inteligência artificial, sustentabilidade'
    }
    
    print("Classificando projeto de exemplo...")
    print(f"Título: {sample_project['titulo']}")
    print(f"Objetivo: {sample_project['objetivo']}")
    
    # Classify the sample project
    try:
        result = client.suggest_categories(sample_project)
        
        # Check for errors
        if 'error' in result:
            print(f"Erro na classificação: {result['error']}")
            return
        
        # Print the results
        print("\nResultados da classificação:")
        print(f"Macroárea: {result.get('_aia_n1_macroarea', '')}")
        print(f"Segmento: {result.get('_aia_n2_segmento', '')}")
        print(f"Domínios Afeitos: {result.get('_aia_n3_dominio_afeito', '')}")
        print(f"Domínios Afeitos Outros: {result.get('_aia_n3_dominio_outro', '')}")
        print(f"Confiança: {result.get('confianca', '')}")
        print(f"Justificativa: {result.get('justificativa', '')}")
        
        # Print the green technology results
        print("\nTecnologias Verdes:")
        print(f"Se Aplica: {'Sim' if result.get('tecverde_se_aplica', False) else 'Não'}")
        if result.get('tecverde_se_aplica', False):
            print(f"Classe: {result.get('tecverde_classe', '')}")
            print(f"Subclasse: {result.get('tecverde_subclasse', '')}")
        print(f"Confiança: {result.get('tecverde_confianca', '')}")
        print(f"Justificativa: {result.get('tecverde_justificativa', '')}")
        
    except Exception as e:
        print(f"Erro ao classificar projeto: {str(e)}")

if __name__ == "__main__":
    main()
