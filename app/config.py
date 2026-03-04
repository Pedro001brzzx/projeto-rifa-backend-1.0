"""
Configurações da Aplicação Flask - Gêmeos Brasil
"""

import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


def _get_database_url():
    """
    Retorna a DATABASE_URL corrigida para uso com SQLAlchemy.
    O Railway fornece URLs com prefixo 'postgres://' mas o SQLAlchemy
    requer 'postgresql://'. Esta função corrige automaticamente.
    """
    url = os.getenv('DATABASE_URL', '')
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url or None


class Config:
    """Configurações base da aplicação"""

    # Banco de dados
    basedir = os.path.abspath(os.path.dirname(__file__))
    _db_url = _get_database_url()
    SQLALCHEMY_DATABASE_URI = _db_url or (
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'rifas.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,       # Verifica conexão antes de usar
        'pool_recycle': 300,          # Recicla conexões a cada 5 min
        'connect_args': {}
    }

    # Segurança
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # CORS — origens permitidas (separar por vírgula na variável de ambiente)
    CORS_HEADERS = 'Content-Type'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173')


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True


class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False


# Configuração padrão
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
