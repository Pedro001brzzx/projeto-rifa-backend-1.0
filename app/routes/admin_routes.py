"""
Rotas Administrativas
Define endpoints exclusivos para administradores
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.controllers import admin_controller
from utils.decorators import admin_required

import os

# Security: Obfuscated Admin URL
ADMIN_PREFIX = os.environ.get('ADMIN_ROUTE_SECRET', '/api/painel-secreto-x9')
admin_bp = Blueprint('admin', __name__, url_prefix=ADMIN_PREFIX)

@admin_bp.route('/usuarios', methods=['GET'])
@jwt_required()
@admin_required()
def listar_usuarios():
    """Lista todos os usuários"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    response, status = admin_controller.listar_usuarios(page, per_page)
    return jsonify(response), status

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required()
def dashboard():
    """Dados para o dashboard admin"""
    response, status = admin_controller.obter_dados_dashboard()
    return jsonify(response), status


@admin_bp.route('/campanhas/<campanha_id>/auditoria', methods=['GET'])
@jwt_required()
@admin_required()
def auditoria_campanha(campanha_id):
    """Retorna histórico de auditoria (AdminLog) de uma campanha (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    response, status = admin_controller.obter_auditoria_campanha(campanha_id, page, per_page)
    return jsonify(response), status


@admin_bp.route('/compras/expiradas', methods=['GET'])
@jwt_required()
@admin_required()
def listar_compras_expiradas():
    """Lista compras expiradas para consulta administrativa"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    response, status = admin_controller.listar_compras_expiradas(page, per_page)
    return jsonify(response), status
