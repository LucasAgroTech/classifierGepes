import os
import sys
from app import create_app, db
from app.models import CategoriaLista

def import_production_categories():
    """
    Import categories from the production database to the development database.
    This ensures that the development environment has the same categories as production.
    """
    print("Starting import of production categories...")
    
    # Create the Flask app with the production configuration
    app = create_app()
    
    # Use the app context
    with app.app_context():
        try:
            # Check if we already have categories
            existing_categories = CategoriaLista.query.count()
            print(f"Found {existing_categories} existing categories in the database.")
            
            # If we have less than 100 categories, we need to import from the list_categories.py output
            if existing_categories < 100:
                print("Less than 100 categories found. Importing from the list of categories...")
                
                # Categories from list_categories.py output
                categories = [
                    # Macroáreas
                    {"tipo": "macroárea", "valor": "Construção", "ativo": True},
                    {"tipo": "macroárea", "valor": "Relações B2B/B2C", "ativo": True},
                    {"tipo": "macroárea", "valor": "Telecomunicações", "ativo": True},
                    {"tipo": "macroárea", "valor": "Agro e Alimentos", "ativo": True},
                    {"tipo": "macroárea", "valor": "Serviços Industriais de Utilidade Pública", "ativo": True},
                    {"tipo": "macroárea", "valor": "Indústria de base e transformação", "ativo": True},
                    {"tipo": "macroárea", "valor": "Saúde", "ativo": True},
                    {"tipo": "macroárea", "valor": "Energia renovável", "ativo": True},
                    {"tipo": "macroárea", "valor": "Engenharia de Produção", "ativo": True},
                    {"tipo": "macroárea", "valor": "Defesa e aeroespacial", "ativo": True},
                    {"tipo": "macroárea", "valor": "Petróleo e gás", "ativo": True},
                    
                    # Segmentos (apenas alguns exemplos)
                    {"tipo": "segmento", "valor": "Agro e Alimentos|Agricultura", "ativo": True},
                    {"tipo": "segmento", "valor": "Agro e Alimentos|Alimentos e Bebidas", "ativo": True},
                    {"tipo": "segmento", "valor": "Agro e Alimentos|Pecuária", "ativo": True},
                    {"tipo": "segmento", "valor": "Construção|Construção de Edifícios", "ativo": True},
                    {"tipo": "segmento", "valor": "Construção|Obras de Infraestrutura", "ativo": True},
                    {"tipo": "segmento", "valor": "Construção|Serviços Especializados para Construção", "ativo": True},
                    {"tipo": "segmento", "valor": "Defesa e aeroespacial|Aeronáutica", "ativo": True},
                    {"tipo": "segmento", "valor": "Defesa e aeroespacial|Propulsão e Lançadores Espaciais", "ativo": True},
                    {"tipo": "segmento", "valor": "Defesa e aeroespacial|Tecnologias de Defesa e Armamentos", "ativo": True},
                    {"tipo": "segmento", "valor": "Energia renovável|Biomossa (biodiesel) e biogás", "ativo": True},
                    {"tipo": "segmento", "valor": "Energia renovável|Energia eólica", "ativo": True},
                    {"tipo": "segmento", "valor": "Energia renovável|Energia hidrelétrica", "ativo": True},
                    {"tipo": "segmento", "valor": "Energia renovável|Energia solar fotovoltaica", "ativo": True},
                    {"tipo": "segmento", "valor": "Energia renovável|Hidrogênio verde", "ativo": True},
                    
                    # Domínios (apenas alguns exemplos)
                    {"tipo": "dominio", "valor": "Agro e Alimentos|Agricultura|Fertilizantes e nutrição vegetal", "ativo": True},
                    {"tipo": "dominio", "valor": "Agro e Alimentos|Agricultura|Controle biológico de pragas", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia solar fotovoltaica|Painéis bifaciais e de alta eficiência", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia solar fotovoltaica|Integração com edificações e infraestrutura urbana", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia solar fotovoltaica|Inversores e sistemas de controle", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia solar fotovoltaica|Armazenamento em baterias", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia solar fotovoltaica|Rastreamento solar automático", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia solar fotovoltaica|Sistemas off-grid e híbridos", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia eólica|Turbinas onshore e offshore", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia eólica|Sistemas de controle e conversão de energia", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia eólica|Integração com redes elétricas", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia eólica|Armazenamento complementar", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia eólica|Otimização de aerodinâmica e materiais", "ativo": True},
                    {"tipo": "dominio", "valor": "Energia renovável|Energia eólica|Previsão e monitoramento de vento", "ativo": True},
                ]
                
                # Add categories to the database
                for category in categories:
                    # Check if the category already exists
                    existing = CategoriaLista.query.filter_by(
                        tipo=category["tipo"], 
                        valor=category["valor"]
                    ).first()
                    
                    if not existing:
                        new_category = CategoriaLista(
                            tipo=category["tipo"],
                            valor=category["valor"],
                            ativo=category["ativo"]
                        )
                        db.session.add(new_category)
                        print(f"Added category: {category['tipo']} - {category['valor']}")
                
                # Commit the changes
                db.session.commit()
                print("Categories imported successfully!")
                
                # Count the categories after import
                final_count = CategoriaLista.query.count()
                print(f"Now there are {final_count} categories in the database.")
            else:
                print("Database already has sufficient categories. No import needed.")
        
        except Exception as e:
            print(f"Error importing categories: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    import_production_categories()
