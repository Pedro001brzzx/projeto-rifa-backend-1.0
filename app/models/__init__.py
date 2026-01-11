"""
Inicialização dos modelos e extensões do banco de dados
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Inicialização das extensões
db = SQLAlchemy()
bcrypt = Bcrypt()

# Importação de todos os modelos
from app.models.usuario import Usuario
from app.models.campanha import Campanha
from app.models.compra import Compra
from app.models.titulo import Titulo
from app.models.artigo import Artigo
from app.models.comunicado import Comunicado
from app.models.contato import Contato

__all__ = [
    'db',
    'bcrypt',
    'Usuario',
    'Campanha',
    'Compra',
    'Titulo',
    'Artigo',
    'Comunicado',
    'Contato'
]
