"""
Controller de Pagamentos
Contém a lógica de negócio para checkout e processamento de pagamentos
"""

from datetime import datetime
from app.models import db, Compra


def criar_checkout(usuario_id, data):
    """
    Cria um checkout e inicia o processo de pagamento
    
    Args:
        usuario_id: ID do usuário autenticado
        data: Dicionário com dados do checkout
    
    Returns:
        tuple: (response dict, status code)
    """
    from app.controllers.compra_controller import criar_compra
    
    # Validar dados obrigatórios
    if 'campanha_id' not in data or 'quantidade_titulos' not in data:
        return {'erro': 'campanha_id e quantidade_titulos são obrigatórios'}, 400
    
    # Criar compra (que já gera os títulos)
    response, status = criar_compra(usuario_id, data)
    
    if status != 201:
        return response, status
    
    compra = response['compra']
    metodo_pagamento = data.get('metodo_pagamento', 'pix')
    
    # Preparar dados de pagamento baseado no método
    pagamento_data = _gerar_dados_pagamento(compra, metodo_pagamento)
    
    return {
        'mensagem': 'Checkout criado com sucesso',
        'compra_id': compra['id'],
        'status_pagamento': compra['status_pagamento'],
        'valor_total': compra['valor_total'],
        'metodo_pagamento': metodo_pagamento,
        'pagamento': pagamento_data,
        'compra': compra
    }, 201


def _gerar_dados_pagamento(compra, metodo_pagamento):
    """
    Gera dados de pagamento PIX usando AbacatePay
    
    Args:
        compra: Dicionário com dados da compra
        metodo_pagamento: Deve ser sempre 'pix'
    
    Returns:
        dict: Dados do pagamento PIX para o cliente
    """
    import os
    
    # Sistema aceita apenas PIX
    if metodo_pagamento != 'pix':
        raise ValueError('Sistema aceita apenas pagamento via PIX')
    
    # Verificar se está configurado o AbacatePay
    api_key = os.getenv('ABACATEPAY_API_KEY')
    
    if not api_key or api_key.startswith('sua-api'):
        # MODO DESENVOLVIMENTO: Retornar mock se não configurado
        print("⚠️ AVISO: AbacatePay não configurado. Usando dados MOCK.")
        return {
            'tipo': 'pix',
            'qr_code': f'00020126580014br.gov.bcb.pix0136{compra["id"]:032d}520400005303986540{compra["valor_total"]:.2f}5802BR5925Sistema Rifas6014SAO PAULO62070503***6304XXXX',
            'qr_code_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            'copia_cola': f'00020126580014br.gov.bcb.pix{compra["id"]}',
            'expira_em': '2026-01-20T12:00:00',
            'instrucoes': '⚠️ MODO DESENVOLVIMENTO - Configure ABACATEPAY_API_KEY no .env'
        }
    
    # PRODUÇÃO: Usar AbacatePay real
    try:
        from abacatepay import AbacatePay
        
        # Inicializar client
        client = AbacatePay(api_key=api_key)
        
        # URLs base (ajuste BASE_URL no .env para produção)
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        
        # Criar cobrança PIX
        billing = client.billing.create(
            frequency='ONE_TIME',  # Corrigido: deve ser ONE_TIME
            methods=['PIX'],
            customerId=str(compra.get('usuario_id', 'default')),  # OBRIGATÓRIO!
            products=[{
                'externalId': str(compra['id']),
                'name': f"Rifas - {compra.get('campanha', {}).get('titulo', 'Campanha')}",
                'description': f"{compra['quantidade_titulos']} títulos",
                'quantity': compra['quantidade_titulos'],
                'price': int((float(compra['valor_total']) / compra['quantidade_titulos']) * 100)  # Centavos!
            }],
            return_url=f"{base_url}/checkout/sucesso",
            completion_url=f"{base_url}/checkout/completo",
            metadata={
                'compra_id': str(compra['id']),
                'campanha_id': str(compra.get('campanha', {}).get('id', '')),
                'quantidade_titulos': compra['quantidade_titulos']
            }
        )
        
        return {
            'tipo': 'pix',
            'qr_code': billing.pix_url,
            'qr_code_base64': billing.pix_qrcode_base64,
            'copia_cola': billing.pix_emv,
            'payment_id': billing.id,
            'expira_em': billing.expires_at,
            'instrucoes': 'Pague com PIX - Processamento instantâneo via AbacatePay'
        }
    
    except ImportError:
        raise Exception('AbacatePay não instalado. Execute: pip install abacatepay')
    except Exception as e:
        # Capturar mensagem de erro da API se disponível
        error_msg = str(e)
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            error_msg = f"API Error: {e.response.text}"
        print(f"❌ Erro ao criar cobrança AbacatePay: {error_msg}")
        raise Exception(f'Erro ao processar pagamento: {error_msg}')


def consultar_pagamento(compra_id):
    """
    Consulta o status de um pagamento
    
    Args:
        compra_id: ID da compra
    
    Returns:
        tuple: (response dict, status code)
    """
    compra = Compra.query.get(compra_id)
    
    if not compra:
        return {'erro': 'Compra não encontrada'}, 404
    
    return {
        'compra_id': compra.id,
        'status_pagamento': compra.status_pagamento,
        'metodo_pagamento': compra.metodo_pagamento,
        'valor_total': float(compra.valor_total),
        'data_pagamento': compra.data_pagamento.isoformat() if compra.data_pagamento else None,
        'criado_em': compra.criado_em.isoformat()
    }, 200


def processar_webhook(data, gateway='generic'):
    """
    Processa webhook de confirmação de pagamento
    
    IMPORTANTE: Em produção, sempre valide a assinatura/token do gateway
    para garantir que a requisição é legítima
    
    Args:
        data: Dados recebidos do webhook
        gateway: Nome do gateway (mercadopago, asaas, pagseguro, etc.)
    
    Returns:
        tuple: (response dict, status code)
    """
    
    # Validar dados obrigatórios
    if 'compra_id' not in data:
        return {'erro': 'compra_id é obrigatório'}, 400
    
    compra_id = data['compra_id']
    compra = Compra.query.get(compra_id)
    
    if not compra:
        return {'erro': 'Compra não encontrada'}, 404
    
    # Determinar novo status baseado no webhook
    novo_status = data.get('status', 'aprovado')
    
    # Validar status
    if novo_status not in ['aprovado', 'pendente', 'cancelado', 'recusado']:
        return {'erro': f'Status inválido: {novo_status}'}, 400
    
    # Se já está aprovado, não fazer nada
    if compra.status_pagamento == 'aprovado':
        return {
            'mensagem': 'Pagamento já estava aprovado',
            'compra_id': compra.id,
            'status': compra.status_pagamento
        }, 200
    
    # Atualizar status da compra
    status_anterior = compra.status_pagamento
    compra.status_pagamento = novo_status
    
    # Se foi aprovado, registrar data de pagamento
    if novo_status == 'aprovado' and not compra.data_pagamento:
        compra.data_pagamento = datetime.utcnow()
        
        # Atualizar contador da campanha (incrementar titulos_vendidos)
        compra.campanha.titulos_vendidos += compra.quantidade_titulos
    
    # Se foi cancelado/recusado após estar pendente, liberar títulos
    elif novo_status in ['cancelado', 'recusado'] and status_anterior == 'pendente':
        # Opcionalmente, podemos deletar os títulos ou marcá-los como disponíveis
        # Por ora, apenas mantemos o registro histórico
        pass
    
    db.session.commit()
    
    return {
        'mensagem': 'Webhook processado com sucesso',
        'compra_id': compra.id,
        'status_anterior': status_anterior,
        'status_atual': compra.status_pagamento,
        'gateway': gateway
    }, 200


def aprovar_pagamento_manual(compra_id, admin_user_id):
    """
    Aprova um pagamento manualmente (apenas admin)
    Útil para pagamentos offline ou testes
    
    Args:
        compra_id: ID da compra
        admin_user_id: ID do usuário admin
    
    Returns:
        tuple: (response dict, status code)
    """
    from app.models import Usuario
    
    # Verificar se é admin
    admin = Usuario.query.get(int(admin_user_id))
    if not admin or not admin.is_admin:
        return {'erro': 'Acesso negado'}, 403
    
    compra = Compra.query.get(compra_id)
    
    if not compra:
        return {'erro': 'Compra não encontrada'}, 404
    
    # Se já aprovado, retornar
    if compra.status_pagamento == 'aprovado':
        return {
            'mensagem': 'Pagamento já estava aprovado',
            'compra_id': compra.id
        }, 200
    
    # Aprovar
    status_anterior = compra.status_pagamento
    compra.status_pagamento = 'aprovado'
    compra.data_pagamento = datetime.utcnow()
    
    # Atualizar contador da campanha
    compra.campanha.titulos_vendidos += compra.quantidade_titulos
    
    db.session.commit()
    
    return {
        'mensagem': 'Pagamento aprovado manualmente',
        'compra_id': compra.id,
        'status_anterior': status_anterior,
        'status_atual': 'aprovado',
        'aprovado_por': admin.nome
    }, 200
