"""
Configurações da Aplicação Flask - Gêmeos Brasil
"""

import os
import secrets
from datetime import timedelta


class Config:
    """Configurações base da aplicação"""
    
    # Banco de dados
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///gemeos_brasil.db'  # SQLite por padrão para desenvolvimento
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
    # SQLite para desenvolvimento local
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///gemeos_brasil.db'
    )


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
