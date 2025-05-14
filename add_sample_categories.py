from app import create_app, db
from app.models import CategoriaLista

def add_sample_categories():
    """
    Adiciona categorias de exemplo ao banco de dados para testar a integração com a IA.
    """
    # Criar a aplicação Flask
    app = create_app()
    
    # Criar um contexto de aplicação
    with app.app_context():
        # Verificar se já existem categorias no banco de dados
        existing_count = CategoriaLista.query.count()
        
        if existing_count > 0:
            print(f"Já existem {existing_count} categorias no banco de dados.")
            choice = input("Deseja adicionar as categorias de exemplo mesmo assim? (s/n): ")
            if choice.lower() != 's':
                print("Operação cancelada.")
                return
        
        # Definir as categorias de exemplo
        sample_categories = [
            # Macroáreas
            {'tipo': 'macroárea', 'valor': 'Tecnologia da Informação'},
            {'tipo': 'macroárea', 'valor': 'Energia'},
            {'tipo': 'macroárea', 'valor': 'Saúde'},
            {'tipo': 'macroárea', 'valor': 'Manufatura Avançada'},
            
            # Segmentos (formato: "Macroárea|Segmento")
            {'tipo': 'segmento', 'valor': 'Tecnologia da Informação|Inteligência Artificial'},
            {'tipo': 'segmento', 'valor': 'Tecnologia da Informação|Infraestrutura'},
            {'tipo': 'segmento', 'valor': 'Tecnologia da Informação|Segurança Cibernética'},
            {'tipo': 'segmento', 'valor': 'Energia|Renovável'},
            {'tipo': 'segmento', 'valor': 'Energia|Eficiência Energética'},
            {'tipo': 'segmento', 'valor': 'Saúde|Diagnóstico'},
            {'tipo': 'segmento', 'valor': 'Saúde|Tratamento'},
            {'tipo': 'segmento', 'valor': 'Manufatura Avançada|Automação'},
            {'tipo': 'segmento', 'valor': 'Manufatura Avançada|Robótica'},
            
            # Domínios (formato: "Macroárea|Segmento|Domínio")
            {'tipo': 'dominio', 'valor': 'Tecnologia da Informação|Inteligência Artificial|Machine Learning'},
            {'tipo': 'dominio', 'valor': 'Tecnologia da Informação|Inteligência Artificial|Visão Computacional'},
            {'tipo': 'dominio', 'valor': 'Tecnologia da Informação|Inteligência Artificial|NLP'},
            {'tipo': 'dominio', 'valor': 'Tecnologia da Informação|Infraestrutura|Cloud Computing'},
            {'tipo': 'dominio', 'valor': 'Tecnologia da Informação|Infraestrutura|Edge Computing'},
            {'tipo': 'dominio', 'valor': 'Tecnologia da Informação|Infraestrutura|IoT'},
            {'tipo': 'dominio', 'valor': 'Tecnologia da Informação|Segurança Cibernética|Criptografia'},
            {'tipo': 'dominio', 'valor': 'Tecnologia da Informação|Segurança Cibernética|Detecção de Intrusão'},
            {'tipo': 'dominio', 'valor': 'Energia|Renovável|Solar'},
            {'tipo': 'dominio', 'valor': 'Energia|Renovável|Eólica'},
            {'tipo': 'dominio', 'valor': 'Energia|Renovável|Biomassa'},
            {'tipo': 'dominio', 'valor': 'Energia|Eficiência Energética|Smart Grid'},
            {'tipo': 'dominio', 'valor': 'Energia|Eficiência Energética|Armazenamento'},
            {'tipo': 'dominio', 'valor': 'Energia|Eficiência Energética|Gestão de Energia'},
            {'tipo': 'dominio', 'valor': 'Saúde|Diagnóstico|Imagem Médica'},
            {'tipo': 'dominio', 'valor': 'Saúde|Diagnóstico|Análise de Dados Clínicos'},
            {'tipo': 'dominio', 'valor': 'Saúde|Tratamento|Dispositivos Médicos'},
            {'tipo': 'dominio', 'valor': 'Saúde|Tratamento|Telemedicina'},
            {'tipo': 'dominio', 'valor': 'Manufatura Avançada|Automação|Controle de Processos'},
            {'tipo': 'dominio', 'valor': 'Manufatura Avançada|Automação|Sensoriamento'},
            {'tipo': 'dominio', 'valor': 'Manufatura Avançada|Robótica|Robôs Industriais'},
            {'tipo': 'dominio', 'valor': 'Manufatura Avançada|Robótica|Robôs Colaborativos'},
        ]
        
        # Adicionar as categorias ao banco de dados
        added_count = 0
        for category in sample_categories:
            # Verificar se a categoria já existe
            existing = CategoriaLista.query.filter_by(
                tipo=category['tipo'], 
                valor=category['valor']
            ).first()
            
            if not existing:
                # Criar nova categoria
                nova_categoria = CategoriaLista(
                    tipo=category['tipo'],
                    valor=category['valor'],
                    ativo=True
                )
                db.session.add(nova_categoria)
                added_count += 1
        
        # Salvar as alterações
        db.session.commit()
        
        print(f"Foram adicionadas {added_count} categorias de exemplo ao banco de dados.")
        print("Agora você pode executar o script debug_categories.py para verificar as categorias.")

if __name__ == "__main__":
    add_sample_categories()
