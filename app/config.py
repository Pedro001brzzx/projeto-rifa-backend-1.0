"""
Configurações da Aplicação Flask - Gêmeos Brasil
"""

import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    """Configurações base da aplicação"""
    
    # Banco de dados
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'rifas.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Segurança
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # CORS
    CORS_HEADERS = 'Content-Type'


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    # Herda SQLALCHEMY_DATABASE_URI da classe Config base


class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    # PostgreSQL para produção
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://usuario:senha@localhost/gemeos_brasil'
    )


# Configuração padrão
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
