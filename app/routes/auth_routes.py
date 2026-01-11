"""
Rotas de Autenticação
Define os endpoints para registro, login e perfil
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import auth_controller

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/registro', methods=['POST'])
def registro():
    """Endpoint para registro de novo usuário"""
    data = request.get_json()
    response, status = auth_controller.registro_usuario(data)
    return jsonify(response), status


@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuário"""
    data = request.get_json()
    response, status = auth_controller.login_usuario(data)
    return jsonify(response), status


@auth_bp.route('/recuperar-senha', methods=['POST'])
def recuperar_senha():
    """Endpoint para recuperação de senha"""
    data = request.get_json()
    response, status = auth_controller.recuperar_senha(data)
    return jsonify(response), status


@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    """Endpoint para obter dados do perfil"""
    usuario_id = get_jwt_identity()
    response, status = auth_controller.obter_perfil(usuario_id)
    return jsonify(response), status


@auth_bp.route('/perfil', methods=['PUT'])
@jwt_required()
def atualizar_perfil():
    """Endpoint para atualizar dados do perfil"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    response, status = auth_controller.atualizar_perfil(usuario_id, data)
    return jsonify(response), status


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Endpoint para logout
    
    Como JWT é stateless, o logout é principalmente do lado do cliente.
    Este endpoint pode ser usado para:
    - Confirmar o logout no servidor (log de auditoria)
    - Adicionar token a uma blocklist (se implementado)
    """
    return jsonify({'mensagem': 'Logout realizado com sucesso'}), 200

