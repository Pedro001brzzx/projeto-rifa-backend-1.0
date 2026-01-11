"""
Decoradores customizados para rotas
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import Usuario


def admin_required():
    """
    Decorador para verificar se o usuário autenticado é administrador
    
    Uso:
        @jwt_required()
        @admin_required()
        def rota_admin():
            ...
    
    Returns:
        função decoradora que verifica is_admin do usuário
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            usuario_id = get_jwt_identity()
            usuario = Usuario.query.get(int(usuario_id))
            
            if not usuario:
                return jsonify({'erro': 'Usuário não encontrado'}), 404
            
            if not usuario.is_admin:
                return jsonify({'erro': 'Acesso negado. Apenas administradores.'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
