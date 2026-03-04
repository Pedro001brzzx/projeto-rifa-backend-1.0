"""
Rotas de Campanhas
Define os endpoints para listagem e criação de campanhas
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import campanha_controller
from utils.decorators import admin_required

from app.utils.admin_logger import with_admin_log

campanha_bp = Blueprint('campanhas', __name__, url_prefix='/api/campanhas')


@campanha_bp.route('', methods=['GET'])
def listar_campanhas():
    """Endpoint para listar campanhas"""
    status = request.args.get('status', None)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    response, status_code = campanha_controller.listar_campanhas(status, page, per_page)
    return jsonify(response), status_code


@campanha_bp.route('/<slug>', methods=['GET'])
def detalhes_campanha(slug):
    """Endpoint para obter detalhes de uma campanha"""
    response, status = campanha_controller.obter_campanha_por_slug(slug)
    return jsonify(response), status


@campanha_bp.route('/<slug>/titulos-premiados', methods=['GET'])
def listar_titulos_premiados(slug):
    """Endpoint para listar títulos premiados da campanha"""
    response, status = campanha_controller.listar_titulos_premiados(slug)
    return jsonify(response), status


@campanha_bp.route('/<campanha_id>/titulos-premiados', methods=['POST'])
@jwt_required()
@admin_required()
def adicionar_titulo_premiado(campanha_id):
    """Endpoint para adicionar título premiado (admin only)"""
    data = request.get_json()
    response, status = campanha_controller.adicionar_titulo_premiado(campanha_id, data)
    return jsonify(response), status


@campanha_bp.route('/titulos-premiados/<int:titulo_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def deletar_titulo_premiado(titulo_id):
    """Endpoint para deletar título premiado (admin only)"""
    response, status = campanha_controller.deletar_titulo_premiado(titulo_id)
    return jsonify(response), status


@campanha_bp.route('', methods=['POST'])
@jwt_required()
@admin_required()
@with_admin_log("Criação de Campanha")
def criar_campanha():
    """Endpoint para criar nova campanha (admin only)"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    response, status = campanha_controller.criar_campanha(usuario_id, data)
    return jsonify(response), status


@campanha_bp.route('/<campanha_id>', methods=['PUT'])
@jwt_required()
@admin_required()
@with_admin_log("Atualização de Campanha")
def atualizar_campanha(campanha_id):
    """Endpoint para atualizar campanha (admin only) - aceita UUID"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    response, status = campanha_controller.atualizar_campanha(usuario_id, campanha_id, data)
    return jsonify(response), status


@campanha_bp.route('/<campanha_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
@with_admin_log("Exclusão de Campanha")
def deletar_campanha(campanha_id):
    """Endpoint para deletar campanha (admin only) - aceita UUID"""
    usuario_id = get_jwt_identity()
    response, status = campanha_controller.deletar_campanha(usuario_id, campanha_id)
    return jsonify(response), status


@campanha_bp.route('/<campanha_id>/compradores', methods=['GET'])
@jwt_required()
@admin_required()
def buscar_compradores(campanha_id):
    """Endpoint para buscar compradores de uma campanha (admin only)"""
    termo = request.args.get('q', '')
    response, status = campanha_controller.buscar_compradores(campanha_id, termo)
    return jsonify(response), status


@campanha_bp.route('/<campanha_id>/ganhador', methods=['POST'])
@jwt_required()
@admin_required()
@with_admin_log("Definição de Ganhador")
def definir_ganhador(campanha_id):
    """Endpoint para definir ganhador de uma campanha (admin only)"""
    data = request.get_json()
    response, status = campanha_controller.definir_ganhador(campanha_id, data)
    return jsonify(response), status
