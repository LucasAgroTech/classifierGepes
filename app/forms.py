from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError

class LoginForm(FlaskForm):
    """Formulário de Login de Usuário."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')

class CategorizacaoForm(FlaskForm):
    """Formulário de Categorização de Projeto."""
    microarea = SelectField('Macroárea', validators=[DataRequired()])
    segmento = SelectField('Segmento', validators=[DataRequired()])
    dominio = HiddenField('Domínio')  # Será processado manualmente do form
    dominio_outros = HiddenField('Domínios Afeitos Outros')  # Será processado manualmente
    observacoes = TextAreaField('Observações', validators=[Optional()])
    
    # Tecnologias Verdes
    tecverde_se_aplica = SelectField('Tecnologia Verde se aplica?', 
                                     choices=[('', 'Selecione...'), ('1', 'Sim'), ('0', 'Não')])
    tecverde_classe = SelectField('Classe', validators=[Optional()])
    tecverde_subclasse = SelectField('Subclasse', validators=[Optional()])
    tecverde_observacoes = TextAreaField('Observações', validators=[Optional()])
    
    # Campos hidden para controle
    used_ai = HiddenField('Utilizou IA')
    user_modified = HiddenField('Usuário Modificou')
    additional_classifications = HiddenField('Classificações Adicionais')

class ListasForm(FlaskForm):
    """Formulário para gerenciar listas de categorias."""
    # Este formulário será processado manualmente pois tem campos dinâmicos

class AIRatingForm(FlaskForm):
    """Formulário de avaliação de sugestões da IA."""
    project_id = HiddenField('ID do Projeto', validators=[DataRequired()])
    rating = SelectField('Avaliação', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], 
                         coerce=int, validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[('aia', 'Área de Interesse de Aplicação'), 
                                         ('tecverde', 'Tecnologias Verdes')], 
                        validators=[DataRequired()])
    observacoes = TextAreaField('Observações', validators=[Optional()])

class SettingsForm(FlaskForm):
    """Formulário de configurações."""
    openai_api_key = StringField('Chave da API OpenAI', validators=[Optional()])