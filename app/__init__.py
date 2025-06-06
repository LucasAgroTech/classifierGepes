from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Por favor, faça login para acessar o sistema'
login_manager.login_message_category = 'warning'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Verificar se a chave da API OpenAI está configurada
    if not os.environ.get('OPENAI_API_KEY'):
        app.logger.warning("OPENAI_API_KEY não está configurada. O chatbot RAG não funcionará corretamente.")
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Garantir que a pasta de configuração existe
    os.makedirs('instance', exist_ok=True)
    
    # Registrar blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Registrar blueprint para avaliação da IA
    from app.routes_ai_ratings import ai_ratings_bp
    app.register_blueprint(ai_ratings_bp)
    
    # Registrar blueprint para dashboard
    from app.routes_dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    # Registrar blueprint para o chatbot
    from app.routes_chat import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/chat')
    
    # Registrar blueprint para gerenciamento de categorias
    from app.routes_categories import categories
    app.register_blueprint(categories)
    
    # Criar tabelas se não existirem (apenas para desenvolvimento)
    with app.app_context():
        db.create_all()
    
    return app

from app import models
