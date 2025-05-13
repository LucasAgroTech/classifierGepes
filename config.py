import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-temporaria'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or \
                             'postgresql://localhost/gepes_classify'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

    @staticmethod
    def get_openai_api_key():
        return os.environ.get('OPENAI_API_KEY', '')
    
    @staticmethod
    def save_openai_api_key(api_key):
        try:
            # Em produção, devemos salvar no banco de dados
            # Aqui, por simplicidade, apenas retornamos True
            # Na implementação real, isso seria persistido para o usuário logado
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False