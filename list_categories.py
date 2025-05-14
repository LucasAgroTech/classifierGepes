from app import create_app, db
from app.models import CategoriaLista

app = create_app()

with app.app_context():
    # Query all categories
    categories = CategoriaLista.query.all()
    
    # Group by tipo
    categories_by_type = {}
    for cat in categories:
        if cat.tipo not in categories_by_type:
            categories_by_type[cat.tipo] = []
        categories_by_type[cat.tipo].append(cat.valor)
    
    # Print results
    print("\n=== CATEGORIAS DISPONÍVEIS ===\n")
    for tipo, valores in categories_by_type.items():
        print(f"Tipo: {tipo}")
        for valor in valores:
            print(f"  - {valor}")
        print()
    
    if not categories:
        print("Nenhuma categoria encontrada na base de dados.")
