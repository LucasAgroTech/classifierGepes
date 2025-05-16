from flask import Flask
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
    
    # Criar tabelas se não existirem (apenas para desenvolvimento)
    with app.app_context():
        db.create_all()
    
    return app

from app import models
