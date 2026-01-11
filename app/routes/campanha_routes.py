"""
Rotas de Campanhas
Define os endpoints para listagem e criação de campanhas
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import campanha_controller
from utils.decorators import admin_required

campanha_bp = Blueprint('campanhas', __name__, url_prefix='/api/campanhas')


@campanha_bp.route('', methods=['GET'])
def listar_campanhas():
    """Endpoint para listar campanhas"""
    status = request.args.get('status', 'ativo')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    response, status_code = campanha_controller.listar_campanhas(status, page, per_page)
    return jsonify(response), status_code


@campanha_bp.route('/<slug>', methods=['GET'])
def detalhes_campanha(slug):
    """Endpoint para obter detalhes de uma campanha"""
    response, status = campanha_controller.obter_campanha_por_slug(slug)
    return jsonify(response), status


@campanha_bp.route('', methods=['POST'])
@jwt_required()
def criar_campanha():
    """Endpoint para criar nova campanha (admin only)"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    response, status = campanha_controller.criar_campanha(usuario_id, data)
    return jsonify(response), status


@campanha_bp.route('/<int:campanha_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def atualizar_campanha(campanha_id):
    """Endpoint para atualizar campanha (admin only)"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    response, status = campanha_controller.atualizar_campanha(usuario_id, campanha_id, data)
    return jsonify(response), status


@campanha_bp.route('/<int:campanha_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def deletar_campanha(campanha_id):
    """Endpoint para deletar campanha (admin only)"""
    usuario_id = get_jwt_identity()
    response, status = campanha_controller.deletar_campanha(usuario_id, campanha_id)
    return jsonify(response), status

