"""
Rotas de Compras
Define os endpoints para compras e títulos
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import compra_controller
from utils.decorators import admin_required
from app.utils.validate_body import validate_body
from app.schemas import CheckoutSchema

compra_bp = Blueprint('compras', __name__, url_prefix='/api')


@compra_bp.route('/compras', methods=['POST'])
@jwt_required()
@validate_body(CheckoutSchema)
def criar_compra():
    """Endpoint para criar nova compra"""
    usuario_id = get_jwt_identity()
    data = g.validated_data
    response, status = compra_controller.criar_compra(usuario_id, data)
    return jsonify(response), status


@compra_bp.route('/meus-titulos', methods=['GET'])
@jwt_required()
def meus_titulos():
    """Endpoint para listar títulos do usuário"""
    usuario_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    response, status = compra_controller.listar_compras_usuario(usuario_id, page, per_page)
    return jsonify(response), status


@compra_bp.route('/compras/<string:compra_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def deletar_compra(compra_id):
    """Endpoint para deletar compra (admin only)"""
    usuario_id = get_jwt_identity()
    response, status = compra_controller.deletar_compra(usuario_id, compra_id)
    return jsonify(response), status
