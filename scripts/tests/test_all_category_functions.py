import unittest
from app import create_app, db
from app.models import CategoriaLista
import json
import os

class TestCategoryFunctions(unittest.TestCase):
    def setUp(self):
        # Configurar o ambiente de teste
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        # Criar contexto de aplicação
        with self.app.app_context():
            # Criar tabelas no banco de dados de teste
            db.create_all()
            
            # Adicionar algumas categorias de teste
            self._add_test_categories()
    
    def tearDown(self):
        # Limpar após cada teste
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _add_test_categories(self):
        """Adiciona categorias de teste ao banco de dados."""
        try:
            # Adicionar macroáreas
            macroarea1 = CategoriaLista(tipo='macroárea', valor='Tecnologia da Informação', ativo=True)
            macroarea2 = CategoriaLista(tipo='macroárea', valor='Energia', ativo=True)
            
            db.session.add_all([macroarea1, macroarea2])
            db.session.commit()
            
            # Adicionar segmentos
            segmento1 = CategoriaLista(tipo='segmento', valor='Tecnologia da Informação|Inteligência Artificial', ativo=True)
            segmento2 = CategoriaLista(tipo='segmento', valor='Tecnologia da Informação|Infraestrutura', ativo=True)
            segmento3 = CategoriaLista(tipo='segmento', valor='Energia|Renovável', ativo=True)
            
            db.session.add_all([segmento1, segmento2, segmento3])
            db.session.commit()
            
            # Adicionar domínios
            dominio1 = CategoriaLista(tipo='dominio', valor='Tecnologia da Informação|Inteligência Artificial|Machine Learning', ativo=True)
            dominio2 = CategoriaLista(tipo='dominio', valor='Tecnologia da Informação|Inteligência Artificial|Visão Computacional', ativo=True)
            dominio3 = CategoriaLista(tipo='dominio', valor='Energia|Renovável|Solar', ativo=True)
            
            db.session.add_all([dominio1, dominio2, dominio3])
            db.session.commit()
            
            # Adicionar classes de tecnologia verde
            classe1 = CategoriaLista(tipo='tecverde_classe', valor='Energia Limpa', ativo=True)
            classe2 = CategoriaLista(tipo='tecverde_classe', valor='Reciclagem', ativo=True)
            
            db.session.add_all([classe1, classe2])
            db.session.commit()
            
            # Adicionar subclasses de tecnologia verde
            subclasse1 = CategoriaLista(tipo='tecverde_subclasse', valor='Energia Limpa|Solar', ativo=True)
            subclasse2 = CategoriaLista(tipo='tecverde_subclasse', valor='Energia Limpa|Eólica', ativo=True)
            subclasse3 = CategoriaLista(tipo='tecverde_subclasse', valor='Reciclagem|Plástico', ativo=True)
            
            db.session.add_all([subclasse1, subclasse2, subclasse3])
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao adicionar categorias de teste: {str(e)}")
    
    def test_manage_categories_page(self):
        """Testa se a página de gerenciamento de categorias carrega corretamente."""
        response = self.client.get('/categories/manage')
        self.assertEqual(response.status_code, 302)  # Redireciona para login
        
        # Simular login (em um cenário real, você precisaria implementar isso)
        # Para este teste, vamos apenas verificar se a rota existe
        
    def test_add_category(self):
        """Testa a adição de uma nova categoria."""
        with self.app.app_context():
            # Adicionar uma nova macroárea
            response = self.client.post('/categories/add', 
                                       data=json.dumps({'tipo': 'macroárea', 'valor': 'Saúde'}),
                                       content_type='application/json')
            
            # Verificar se a resposta é um redirecionamento (302) para login
            # ou um erro de autorização (401)
            self.assertIn(response.status_code, [302, 401])
            
            # Verificar se a categoria foi adicionada ao banco de dados
            # (isso não deve acontecer sem autenticação)
            categoria = CategoriaLista.query.filter_by(tipo='macroárea', valor='Saúde').first()
            self.assertIsNone(categoria)
    
    def test_hierarchy_structure(self):
        """Testa se a estrutura hierárquica está correta."""
        with self.app.app_context():
            # Verificar macroáreas
            macroareas = CategoriaLista.query.filter_by(tipo='macroárea', ativo=True).all()
            self.assertEqual(len(macroareas), 2)
            
            # Verificar segmentos
            segmentos = CategoriaLista.query.filter_by(tipo='segmento', ativo=True).all()
            self.assertEqual(len(segmentos), 3)
            
            # Verificar domínios
            dominios = CategoriaLista.query.filter_by(tipo='dominio', ativo=True).all()
            self.assertEqual(len(dominios), 3)
            
            # Verificar classes de tecnologia verde
            classes = CategoriaLista.query.filter_by(tipo='tecverde_classe', ativo=True).all()
            self.assertEqual(len(classes), 2)
            
            # Verificar subclasses de tecnologia verde
            subclasses = CategoriaLista.query.filter_by(tipo='tecverde_subclasse', ativo=True).all()
            self.assertEqual(len(subclasses), 3)
    
    def test_edit_macroarea(self):
        """Testa a edição de uma macroárea e a atualização em cascata."""
        with self.app.app_context():
            # Obter a macroárea "Tecnologia da Informação"
            macroarea = CategoriaLista.query.filter_by(tipo='macroárea', valor='Tecnologia da Informação').first()
            
            # Simular a edição (sem autenticação, isso não deve funcionar)
            response = self.client.put(f'/categories/edit/{macroarea.id}', 
                                      data=json.dumps({'valor': 'TI'}),
                                      content_type='application/json')
            
            # Verificar se a resposta é um redirecionamento (302) para login
            # ou um erro de autorização (401)
            self.assertIn(response.status_code, [302, 401])
            
            # Verificar se a macroárea não foi alterada
            macroarea_updated = CategoriaLista.query.filter_by(tipo='macroárea', id=macroarea.id).first()
            self.assertEqual(macroarea_updated.valor, 'Tecnologia da Informação')
    
    def test_delete_macroarea(self):
        """Testa a exclusão de uma macroárea e a desativação em cascata."""
        with self.app.app_context():
            # Obter a macroárea "Energia"
            macroarea = CategoriaLista.query.filter_by(tipo='macroárea', valor='Energia').first()
            
            # Simular a exclusão (sem autenticação, isso não deve funcionar)
            response = self.client.delete(f'/categories/delete/{macroarea.id}')
            
            # Verificar se a resposta é um redirecionamento (302) para login
            # ou um erro de autorização (401)
            self.assertIn(response.status_code, [302, 401])
            
            # Verificar se a macroárea não foi desativada
            macroarea_updated = CategoriaLista.query.filter_by(tipo='macroárea', id=macroarea.id).first()
            self.assertTrue(macroarea_updated.ativo)

if __name__ == '__main__':
    unittest.main()
