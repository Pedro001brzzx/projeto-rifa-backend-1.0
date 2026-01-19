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

pagamento_bp = Blueprint('pagamentos', __name__, url_prefix='/api')


@pagamento_bp.route('/checkout', methods=['POST'])
@jwt_required()
def criar_checkout():
    """Endpoint para criar checkout e iniciar pagamento"""
    usuario_id = get_jwt_identity()
    data = request.get_json()
    response, status = pagamento_controller.criar_checkout(usuario_id, data)
    return jsonify(response), status


@pagamento_bp.route('/pagamentos/<int:compra_id>', methods=['GET'])
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
    data =request.get_json()
    gateway = request.args.get('gateway', 'generic')
    
    # ABACATEPAY: Validar assinatura HMAC
    if gateway == 'abacatepay':
        signature = request.headers.get('X-Webhook-Signature')
        webhook_secret = os.getenv('ABACATEPAY_WEBHOOK_SECRET')
        
        if webhook_secret and signature:
            # Recalcular HMAC com o body recebido (RAW bytes)
            body_bytes = request.get_data()
            expected_signature = hmac.new(
                webhook_secret.encode(),
                body_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # Comparação segura (previne timing attacks)
            if not hmac.compare_digest(signature, expected_signature):
                return jsonify({'erro': 'Assinatura inválida'}), 401
        
        # Processar evento do AbacatePay
        if data.get('kind') == 'billing.paid':
            # Pagamento aprovado!
            metadata = data.get('data', {}).get('metadata', {})
            compra_id = int(metadata.get('compra_id'))
            
            response, status = pagamento_controller.processar_webhook({
                'compra_id': compra_id,
                'status': 'aprovado'
            }, 'abacatepay')
            
            return jsonify(response), status
    
    # Fallback para outros gateways ou testes
    response, status = pagamento_controller.processar_webhook(data, gateway)
    return jsonify(response), status


@pagamento_bp.route('/pagamentos/<int:compra_id>/aprovar', methods=['POST'])
@jwt_required()
@admin_required()
def aprovar_pagamento_manual(compra_id):
    """Endpoint para aprovar pagamento manualmente (admin only)"""
    admin_id = get_jwt_identity()
    response, status = pagamento_controller.aprovar_pagamento_manual(compra_id, admin_id)
    return jsonify(response), status
