"""
Rotas de Ganhadores
Define os endpoints para listagem de ganhadores
"""

from flask import Blueprint, request, jsonify
from app.controllers import ganhador_controller

ganhador_bp = Blueprint('ganhadores', __name__, url_prefix='/api/ganhadores')


@ganhador_bp.route('', methods=['GET'])
def listar_ganhadores():
    """Endpoint para listar ganhadores"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    response, status = ganhador_controller.listar_ganhadores(page, per_page)
    return jsonify(response), status
