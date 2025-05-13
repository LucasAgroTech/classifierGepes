from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(int(id))

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {'schema': 'gepes'}
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    nome = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    sharepoint_username = db.Column(db.String(255))
    senha_hash = db.Column(db.String(255))
    ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relações
    logs = db.relationship('Log', backref='usuario', lazy='dynamic')
    ai_ratings = db.relationship('AIRating', backref='usuario', lazy='dynamic')
    
    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Projeto(db.Model):
    __tablename__ = 'projetos'
    __table_args__ = {'schema': 'gepes'}
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_projeto = db.Column(db.String(50), nullable=False, unique=True)
    codigo_interno = db.Column(db.String(50))
    unidade_embrapii = db.Column(db.String(255))
    tipo_projeto = db.Column(db.String(100))
    status = db.Column(db.String(50))
    titulo = db.Column(db.Text, nullable=False)
    titulo_publico = db.Column(db.Text)
    objetivo = db.Column(db.Text)
    descricao_publica = db.Column(db.Text)
    data_contrato = db.Column(db.Date)
    data_avaliacao = db.Column(db.Date)
    observacoes = db.Column(db.Text)
    tags = db.Column(db.Text)
    valor_total = db.Column(db.Numeric(15, 2))
    perc_valor_embrapii = db.Column(db.Numeric(5, 2))
    perc_valor_empresa_sebrae = db.Column(db.Numeric(5, 2))
    perc_valor_unidade_embrapii = db.Column(db.Numeric(5, 2))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campos de categorização (que eram armazenados em all_projetos.json)
    _aia_n1_macroarea = db.Column(db.String(255))
    _aia_n2_segmento = db.Column(db.String(255))
    _aia_n3_dominio_afeito = db.Column(db.Text)
    _aia_n3_dominio_outro = db.Column(db.Text)
    tecverde_se_aplica = db.Column(db.Boolean)
    tecverde_classe = db.Column(db.String(255))
    tecverde_subclasse = db.Column(db.String(255))
    tecverde_observacoes = db.Column(db.Text)
    
    # Campos para avaliações da IA
    ai_rating_aia = db.Column(db.Integer)
    ai_rating_aia_user = db.Column(db.String(255))
    ai_rating_aia_timestamp = db.Column(db.String(50))
    ai_rating_aia_observacoes = db.Column(db.Text)
    
    ai_rating_tecverde = db.Column(db.Integer)
    ai_rating_tecverde_user = db.Column(db.String(255))
    ai_rating_tecverde_timestamp = db.Column(db.String(50))
    ai_rating_tecverde_observacoes = db.Column(db.Text)
    
    # Relações
    categoria = db.relationship('Categoria', backref='projeto', uselist=False, cascade="all, delete-orphan")
    tecverde = db.relationship('TecnologiaVerde', backref='projeto', uselist=False, cascade="all, delete-orphan")
    classificacoes_adicionais = db.relationship('ClassificacaoAdicional', backref='projeto', lazy='dynamic', cascade="all, delete-orphan")
    logs = db.relationship('Log', backref='projeto', lazy='dynamic', cascade="all, delete-orphan")
    ai_suggestions = db.relationship('AISuggestion', backref='projeto', lazy='dynamic', cascade="all, delete-orphan")
    ai_ratings = db.relationship('AIRating', backref='projeto', lazy='dynamic', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Projeto {self.codigo_projeto}>'

class Categoria(db.Model):
    __tablename__ = 'categorias'
    __table_args__ = {'schema': 'gepes'}
    
    id = db.Column(db.Integer, primary_key=True)
    id_projeto = db.Column(db.Integer, db.ForeignKey('gepes.projetos.id'), nullable=False)
    microarea = db.Column(db.String(255))
    segmento = db.Column(db.String(255))
    dominio = db.Column(db.Text)
    dominio_outros = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Categoria {self.id} para projeto {self.id_projeto}>'

class TecnologiaVerde(db.Model):
    __tablename__ = 'tecnologias_verdes'
    __table_args__ = {'schema': 'gepes'}
    
    id = db.Column(db.Integer, primary_key=True)
    id_projeto = db.Column(db.Integer, db.ForeignKey('gepes.projetos.id'), nullable=False)
    se_aplica = db.Column(db.Boolean, nullable=False, default=False)
    classe = db.Column(db.String(255))
    subclasse = db.Column(db.String(255))
    observacoes = db.Column(db.Text)
    confianca = db.Column(db.String(20))
    justificativa = db.Column(db.Text)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TecnologiaVerde {self.id} para projeto {self.id_projeto}>'

class CategoriaLista(db.Model):
    __tablename__ = 'categoria_listas'
    __table_args__ = {'schema': 'gepes'}
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    __table_args__ = (
        db.UniqueConstraint('tipo', 'valor', name='uq_tipo_valor'),
        {'schema': 'gepes'}
    )
    
    def __repr__(self):
        return f'<CategoriaLista {self.tipo}: {self.valor}>'

class ClassificacaoAdicional(db.Model):
    __tablename__ = 'classificacoes_adicionais'
    __table_args__ = {'schema': 'gepes'}
    
    id = db.Column(db.Integer, primary_key=True)
    id_projeto = db.Column(db.Integer, db.ForeignKey('gepes.projetos.id'), nullable=False)
    microarea = db.Column(db.String(255), nullable=False)
    segmento = db.Column(db.String(255), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ClassificacaoAdicional {self.id} para projeto {self.id_projeto}>'

class Log(db.Model):
    __tablename__ = 'logs'
    __table_args__ = {'schema': 'gepes'}
    
    id = db.Column(db.Integer, primary_key=True)
    id_projeto = db.Column(db.Integer, db.ForeignKey('gepes.projetos.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('gepes.usuarios.id'))
    email_usuario = db.Column(db.String(255), nullable=False)
    nome_usuario = db.Column(db.String(255))
    acao = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data_acao = db.Column(db.DateTime, default=datetime.utcnow)
    utilizou_ia = db.Column(db.Boolean, default=False)
    usuario_modificou = db.Column(db.Boolean, default=False)
    ai_rating_aia = db.Column(db.Integer)
    ai_rating_tecverde = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<Log {self.id} para projeto {self.id_projeto}>'

class AISuggestion(db.Model):
    __tablename__ = 'ai_suggestions'
    __table_args__ = {'schema': 'gepes'}
    
    id = db.Column(db.Integer, primary_key=True)
    id_projeto = db.Column(db.Integer, db.ForeignKey('gepes.projetos.id'), nullable=False)
    microarea = db.Column(db.String(255))
    segmento = db.Column(db.String(255))
    dominio = db.Column(db.Text)
    dominio_outro = db.Column(db.Text)
    confianca = db.Column(db.String(20))
    justificativa = db.Column(db.Text)
    tecverde_se_aplica = db.Column(db.Boolean)
    tecverde_classe = db.Column(db.String(255))
    tecverde_subclasse = db.Column(db.String(255))
    tecverde_confianca = db.Column(db.String(20))
    tecverde_justificativa = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Colunas correspondentes ao JSON da API OpenAI
    _aia_n1_macroarea = db.Column(db.String(255))
    _aia_n2_segmento = db.Column(db.String(255))
    _aia_n3_dominio_afeito = db.Column(db.Text)
    _aia_n3_dominio_outro = db.Column(db.Text)
    
    def __repr__(self):
        return f'<AISuggestion {self.id} para projeto {self.id_projeto}>'
    
    def to_dict(self):
        """Converte o objeto para um dicionário para compatibilidade com o código antigo."""
        return {
            'id': self.id,
            'project_id': self.id_projeto,
            'microarea': self.microarea,
            'segmento': self.segmento,
            'dominio': self.dominio,
            'dominio_outro': self.dominio_outro,
            'confianca': self.confianca,
            'justificativa': self.justificativa,
            'tecverde_se_aplica': self.tecverde_se_aplica,
            'tecverde_classe': self.tecverde_classe,
            'tecverde_subclasse': self.tecverde_subclasse,
            'tecverde_confianca': self.tecverde_confianca,
            'tecverde_justificativa': self.tecverde_justificativa,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            '_aia_n1_macroarea': self._aia_n1_macroarea,
            '_aia_n2_segmento': self._aia_n2_segmento,
            '_aia_n3_dominio_afeito': self._aia_n3_dominio_afeito,
            '_aia_n3_dominio_outro': self._aia_n3_dominio_outro,
            'is_ai_suggestion': True
        }

class AIRating(db.Model):
    __tablename__ = 'ai_ratings'
    __table_args__ = {'schema': 'gepes'}
    
    id = db.Column(db.Integer, primary_key=True)
    id_projeto = db.Column(db.Integer, db.ForeignKey('gepes.projetos.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('gepes.usuarios.id'))
    user_id = db.Column(db.String(255), nullable=False)  # Email do usuário (para compatibilidade)
    nome_usuario = db.Column(db.String(255))
    tipo = db.Column(db.String(20), nullable=False)  # 'aia' ou 'tecverde'
    rating = db.Column(db.Integer, nullable=False)
    observacoes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('id_projeto', 'user_id', 'tipo', name='uq_id_projeto_user_id_tipo'),
        {'schema': 'gepes'}
    )
    
    def __repr__(self):
        return f'<AIRating {self.id} para projeto {self.id_projeto}>'
    
    def to_dict(self):
        """Converte o objeto para um dicionário para compatibilidade com o código antigo."""
        return {
            'id': self.id,
            'project_id': self.id_projeto,
            'user_id': self.user_id,
            'nome_usuario': self.nome_usuario,
            'rating': self.rating,
            'observacoes': self.observacoes,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }