"""
Rotas Administrativas
Define endpoints exclusivos para administradores
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.controllers import admin_controller
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

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
