"""
Rotas de Conteúdo
Define os endpoints para artigos, comunicados e contato
"""

from flask import Blueprint, request, jsonify
from app.controllers import conteudo_controller

conteudo_bp = Blueprint('conteudo', __name__, url_prefix='/api')


@conteudo_bp.route('/artigos', methods=['GET'])
def listar_artigos():
    """Endpoint para listar artigos"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    response, status = conteudo_controller.listar_artigos(page, per_page)
    return jsonify(response), status


@conteudo_bp.route('/artigos/<slug>', methods=['GET'])
def detalhes_artigo(slug):
    """Endpoint para obter detalhes de um artigo"""
    response, status = conteudo_controller.obter_artigo(slug)
    return jsonify(response), status


@conteudo_bp.route('/comunicados', methods=['GET'])
def listar_comunicados():
    """Endpoint para listar comunicados"""
    response, status = conteudo_controller.listar_comunicados()
    return jsonify(response), status


@conteudo_bp.route('/contato', methods=['POST'])
def enviar_contato():
    """Endpoint para enviar mensagem de contato"""
    data = request.get_json()
    response, status = conteudo_controller.enviar_contato(data)
    return jsonify(response), status
