"""
Inicialização dos controllers
"""

from app.controllers import auth_controller
from app.controllers import campanha_controller
from app.controllers import compra_controller
from app.controllers import ganhador_controller
from app.controllers import conteudo_controller

__all__ = [
    'auth_controller',
    'campanha_controller',
    'compra_controller',
    'ganhador_controller',
    'conteudo_controller'
]
