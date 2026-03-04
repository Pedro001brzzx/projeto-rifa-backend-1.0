"""
Rotas de Pagamentos
Define os endpoints para checkout, webhook e consulta de pagamentos
"""

import hmac
import hashlib
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import pagamento_controller
from utils.decorators import admin_required

from app.utils.admin_logger import with_admin_log

pagamento_bp = Blueprint('pagamentos', __name__, url_prefix='/api')


@pagamento_bp.route('/checkout', methods=['POST'])
@jwt_required()
def criar_checkout():
    """Endpoint para criar checkout e iniciar pagamento"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    response, status = pagamento_controller.criar_checkout(usuario_id, data)
    return jsonify(response), status


@pagamento_bp.route('/pagamentos/<string:compra_id>', methods=['GET'])
@jwt_required()
def consultar_pagamento(compra_id):
    """Endpoint para consultar status de pagamento"""
    response, status = pagamento_controller.consultar_pagamento(compra_id)
    return jsonify(response), status


@pagamento_bp.route('/pagamentos/webhook', methods=['POST'])
def processar_webhook():
    """
    Endpoint para receber webhooks de gateways de pagamento
    
    Suporta AbacatePay com validação HMAC
    """
    data = request.get_json(silent=True) or {}
    gateway = request.args.get('gateway', 'abacatepay')  # Default to AbacatePay
    
    # Capturar signature e body para validação
    signature = request.headers.get('X-Webhook-Signature')
    raw_body = request.get_data()
    
    response, status = pagamento_controller.processar_webhook(
        data=data, 
        gateway=gateway,
        raw_body=raw_body,
        signature=signature
    )
    return jsonify(response), status


@pagamento_bp.route('/pagamentos/<string:compra_id>/aprovar', methods=['POST'])
@jwt_required()
@admin_required()
@with_admin_log("Aprovação Manual de Pagamento")
def aprovar_pagamento_manual(compra_id):
    """Endpoint para aprovar pagamento manualmente (admin only)"""
    admin_id = get_jwt_identity()
    response, status = pagamento_controller.aprovar_pagamento_manual(compra_id, admin_id)
    return jsonify(response), status
