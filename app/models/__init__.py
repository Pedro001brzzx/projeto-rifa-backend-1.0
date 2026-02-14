"""
Inicialização dos modelos e extensões do banco de dados
"""

from app.extensions import db, bcrypt

# Importação de todos os modelos
from app.models.usuario import Usuario
from app.models.campanha import Campanha
from app.models.compra import Compra
from app.models.titulo import Titulo
from app.models.artigo import Artigo
from app.models.comunicado import Comunicado
from app.models.contato import Contato
from app.models.admin_log import AdminLog

__all__ = [
    'db',
    'bcrypt',
    'Usuario',
    'Campanha',
    'Compra',
    'Titulo',
    'Artigo',
    'Comunicado',
    'Contato',
    'AdminLog'
]
