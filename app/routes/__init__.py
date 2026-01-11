"""
Inicialização das rotas
"""

from app.routes.auth_routes import auth_bp
from app.routes.campanha_routes import campanha_bp
from app.routes.compra_routes import compra_bp
from app.routes.ganhador_routes import ganhador_bp
from app.routes.conteudo_routes import conteudo_bp

from app.routes.admin_routes import admin_bp

__all__ = [
    'auth_bp',
    'campanha_bp',
    'compra_bp',
    'ganhador_bp',
    'conteudo_bp',
    'admin_bp'
]
