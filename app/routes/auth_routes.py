"""
Rotas de Autenticação
Define os endpoints para registro, login e perfil
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import auth_controller
from app.extensions import limiter
from app.utils.validate_body import validate_body
from app.schemas import (
    RegistroSchema,
    LoginSchema,
    ForgotSenhaSchema,
    ResetSenhaSchema,
    AtualizarPerfilSchema,
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/registro', methods=['POST'])
@limiter.limit("5 per minute")
@validate_body(RegistroSchema)
def registro():
    """Endpoint para registro de novo usuário"""
    data = g.validated_data
    response, status = auth_controller.registro_usuario(data)
    return jsonify(response), status


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
@validate_body(LoginSchema)
def login():
    """Endpoint para login de usuário"""
    data = g.validated_data
    response, status = auth_controller.login_usuario(data)
    return jsonify(response), status


@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("3 per minute")
@validate_body(ForgotSenhaSchema)
def forgot_password():
    """Endpoint para solicitar recuperação de senha"""
    data = g.validated_data
    response, status = auth_controller.forgot_password(data)
    return jsonify(response), status


@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("5 per minute")
@validate_body(ResetSenhaSchema)
def reset_password():
    """Endpoint para redefinir senha com token"""
    data = g.validated_data
    response, status = auth_controller.reset_password(data)
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
@validate_body(AtualizarPerfilSchema)
def atualizar_perfil():
    """Endpoint para atualizar dados do perfil"""
    usuario_id = get_jwt_identity()
    data = g.validated_data
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
