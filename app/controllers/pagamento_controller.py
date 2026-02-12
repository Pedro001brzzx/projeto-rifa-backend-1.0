"""
Controller de Pagamentos
Contém a lógica de negócio para checkout e processamento de pagamentos
"""

from datetime import datetime, timedelta
from app.models import db, Compra


def _aprovar_e_gerar_titulos(compra):
    """
    Aprova o pagamento e gera os títulos da compra.
    
    IMPORTANTE: Esta é a ÚNICA função que gera títulos!
    Títulos são gerados APENAS após confirmação do pagamento.
    
    Args:
        compra: Objeto Compra a ser aprovada
        
    Raises:
        Exception: Se não houver títulos disponíveis
    """
    from app.controllers.compra_controller import gerar_titulos, MAX_TITULOS_POSSIVEIS
    from app.models import Titulo
    
    # 1. Verificar se já tem títulos (evitar duplicação)
    titulos_count = Titulo.query.filter_by(compra_id=compra.id).count()
    if titulos_count > 0:
        print(f"⚠️ Compra #{compra.id} já possui {titulos_count} títulos! Pulando geração.")
        return
    
    # 2. Validar disponibilidade de títulos
    titulos_ja_vendidos = Titulo.query.filter(
        Titulo.campanha_id == compra.campanha_id
    ).count()
    
    # Validação 1: Limite físico do sistema
    if titulos_ja_vendidos + compra.quantidade_titulos > MAX_TITULOS_POSSIVEIS:
        disponiveis = MAX_TITULOS_POSSIVEIS - titulos_ja_vendidos
        raise Exception(
            f'Títulos esgotados! Apenas {disponiveis} título(s) disponível(is). '
            f'Limite máximo: {MAX_TITULOS_POSSIVEIS}'
        )
    
    # Validação 2: Limite da campanha
    if compra.campanha.titulos_vendidos + compra.quantidade_titulos > compra.campanha.total_titulos:
        disponiveis = compra.campanha.total_titulos - compra.campanha.titulos_vendidos
        raise Exception(
            f'Títulos esgotados para esta campanha! Apenas {disponiveis} título(s) disponível(is).'
        )
    
    # 3. GERAR TÍTULOS
    print(f"🎫 Gerando {compra.quantidade_titulos} títulos para compra #{compra.id}...")
    gerar_titulos(compra.id, compra.campanha_id, compra.quantidade_titulos)
    
    # 4. Incrementar contador da campanha
    compra.campanha.titulos_vendidos += compra.quantidade_titulos
    
    # 5. Atualizar status da compra
    compra.status_pagamento = 'aprovado'
    compra.data_pagamento = datetime.utcnow()
    
    db.session.commit()
    
    print(f"✅ Compra #{compra.id} aprovada! Títulos gerados e campanha atualizada.")



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
    Gera dados de pagamento PIX usando AbacatePay (API pixQrCode)
    
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
    
    
    if not api_key or api_key == 'sua-api-key-aqui':
        # MODO DESENVOLVIMENTO: Retornar mock se não configurado
        print("⚠️ AVISO: AbacatePay não configurado. Usando dados MOCK.")
        return {
            'tipo': 'pix',
            'qr_code': f'00020126580014br.gov.bcb.pix0136{compra["id"]:032d}520400005303986540{compra["valor_total"]:.2f}5802BR5925Sistema Rifas6014SAO PAULO62070503***6304XXXX',
            'qr_code_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            'copia_cola': f'00020126580014br.gov.bcb.pix{compra["id"]}',
            'expira_em': (datetime.utcnow() + timedelta(minutes=10)).isoformat() + 'Z',
            'instrucoes': '⚠️ MODO DESENVOLVIMENTO - Configure ABACATEPAY_API_KEY no .env'
        }
    
    # PRODUÇÃO: Usar AbacatePay real
    try:
        from abacatepay import AbacatePay
        
        # Inicializar client
        client = AbacatePay(api_key)
        
        # Dados do cliente (usar dados do token/usuário se possível, aqui simplificado)
        customer_data = {
            'name': 'Cliente Rifas', # Idealmente viria de compra['usuario']
            'cellphone': '85999999999',
            'email': 'cliente@exemplo.com',
            'taxId': '00000000000'
        }
        
        # Criar PIX QRCode
        # Valor em centavos (int)
        amount_cents = int(float(compra['valor_total']) * 100)
        
        pix_response = client.pixQrCode.create(
            amount=amount_cents,
            expiresIn=600, # 10 minutos
            description=f"Rifas - Compra #{compra['id']}",
            customer=customer_data,
            metadata={
                'compra_id': str(compra['id']),
                'campanha_id': str(compra.get('campanha', {}).get('id', '')),
                'quantidade_titulos': str(compra['quantidade_titulos'])
            }
        )
        
        return {
            'tipo': 'pix',
            'qr_code': pix_response.data.brcode,
            'qr_code_base64': pix_response.data.brcode_base64,
            'copia_cola': pix_response.data.brcode, # Geralmente o mesmo
            'payment_id': pix_response.data.id,
            'expira_em': pix_response.data.expires_at,
            'instrucoes': 'Pague com PIX - Processamento instantâneo via AbacatePay'
        }
    
    except ImportError:
        raise Exception('AbacatePay não instalado. Execute: pip install abacatepay')
    except Exception as e:
        # Capturar mensagem de erro da API se disponível
        error_msg = str(e)
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            error_msg = f"API Error: {e.response.text}"
        print(f"❌ Erro ao criar PIX AbacatePay: {error_msg}")
        raise Exception(f'Erro ao processar pagamento: {error_msg}')


def _verificar_e_marcar_expiracao(compra):
    """
    Verifica se uma compra está expirada e atualiza o status automaticamente.
    Validação em tempo real - não depende do job de cleanup.
    
    IMPORTANTE: Compras pendentes NÃO TÊM títulos gerados, então não precisa deletá-los.
    
    Args:
        compra: Objeto Compra do banco de dados
    
    Returns:
        bool: True se a compra foi marcada como expirada, False caso contrário
    """
    # Apenas compras pendentes podem expirar
    if compra.status_pagamento != 'pendente':
        return False
    
    # Verificar se tem campo expira_em e se já expirou
    if hasattr(compra, 'expira_em') and compra.expira_em:
        now = datetime.utcnow()
        
        if compra.expira_em < now:
            # Compra expirada! Atualizar status
            print(f"⏱️ Compra #{compra.id} expirada - Marcando como 'expirado'")
            
            # ⚠️ NÃO precisa deletar títulos - compras pendentes não têm títulos!
            # Títulos são gerados APENAS após aprovação do pagamento
            
            # Marcar como expirada
            compra.status_pagamento = 'expirado'
            
            db.session.commit()
            
            print(f"✅ Compra #{compra.id} marcada como expirada (sem títulos para limpar)")
            return True
    
    return False


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
    
    # VALIDAÇÃO EM TEMPO REAL: Verificar se a compra expirou
    _verificar_e_marcar_expiracao(compra)
    
    # Incluir dados da campanha
    campanha_data = {
        'id': compra.campanha.id,
        'titulo': compra.campanha.titulo,
        'slug': compra.campanha.slug,
        'imagem_principal': compra.campanha.imagem_principal,
        'valor_titulo': float(compra.campanha.valor_titulo),
        'total_titulos': compra.campanha.total_titulos
    } if compra.campanha else None
    
    return {
        'compra_id': compra.id,
        'status_pagamento': compra.status_pagamento,
        'metodo_pagamento': compra.metodo_pagamento,
        'valor_total': float(compra.valor_total),
        'quantidade_titulos': compra.quantidade_titulos,
        'data_pagamento': (compra.data_pagamento.isoformat() + 'Z') if compra.data_pagamento else None,
        'criado_em': compra.criado_em.isoformat() + 'Z',
        'expira_em': (getattr(compra, 'expira_em').isoformat() + 'Z') if getattr(compra, 'expira_em', None) else None,
        'campanha': campanha_data
    }, 200


def processar_webhook(data, gateway='abacatepay', raw_body=None, signature=None):
    """
    Processa webhook de confirmação de pagamento
    
    Args:
        data: Dados recebidos do webhook
        gateway: Nome do gateway
        raw_body: Corpo bruto da requisição (bytes) para validação de assinatura
        signature: Assinatura recebida no header X-Webhook-Signature
    
    Returns:
        tuple: (response dict, status code)
    """
    import hmac
    import hashlib
    import os
    
    print(f"📩 Webhook recebido ({gateway}): {data}")
    
    # 1. Validação de Segurança (AbacatePay)
    if gateway == 'abacatepay':
        webhook_secret = os.getenv('ABACATEPAY_WEBHOOK_SECRET')
        
        # Se configurado secret, é OBRIGATÓRIO validar
        if webhook_secret:
            if not raw_body or not signature:
                 print("⛔ Webhook rejeitado: Falta assinatura ou body")
                 return {'erro': 'Assinatura obrigatória'}, 401
            
            # Recalcular HMAC
            expected_signature = hmac.new(
                webhook_secret.encode(),
                raw_body, # Deve ser bytes
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                print(f"⛔ Assinatura inválida! Recebida: {signature}, Esperada: {expected_signature}")
                return {'erro': 'Assinatura inválida'}, 401
            
            print("✅ Assinatura do webhook validada com sucesso!")
        else:
            print("⚠️ AVISO: ABACATEPAY_WEBHOOK_SECRET não configurado. Aceitando webhook inseguro (DEV ONLY).")
            
    # 2. Processar Evento
    event_type = data.get('event')  # AbacatePay usa 'event' no topo
    
    if event_type == 'billing.paid':
        # Extrair dados do pagamento
        webhook_data = data.get('data', {})
        pix_data = webhook_data.get('pixQrCode', {})
        billing_data = webhook_data.get('billing', {})
        
        # Tentar obter compra_id do metadata
        metadata = billing_data.get('customer', {}).get('metadata', {})
        # Fallback: tentar obter do pixQrCode metadata se disponível (depende da versao da API)
        
        # Na versão atual, o ID externo pode estar no metadata global ou produtos
        # Vamos tentar extrair o ID da compra de várias formas
        compra_id = None
        
        # Opção 1: Id enviado no metadata da criação
        # Nota: A API do AbacatePay retorna metadata no nível raiz do objeto data ou billing?
        # Vamos assumir que passamos no customer ou products conforme código de geração
        
        # Tentar achar nos produtos
        products = billing_data.get('products', [])
        if products:
             # externalId foi enviado como compra_id
             compra_id = products[0].get('externalId')
             
        if not compra_id:
             print("⚠️ Compra ID não encontrado no webhook")
             return {'erro': 'Compra ID não identificado'}, 400
             
        # Converter para int
        try:
            compra_id = int(compra_id)
        except:
             print(f"⚠️ Compra ID inválido: {compra_id}")
             return {'erro': 'Compra ID inválido'}, 400
             
        # 3. Aprovar Compra
        print(f"💰 Processando pagamento para Compra #{compra_id}")
        compra = Compra.query.get(compra_id)
        
        if not compra:
            print(f"❌ Compra #{compra_id} não encontrada no banco")
            return {'erro': 'Compra não encontrada'}, 404
            
        if compra.status_pagamento == 'aprovado':
            print(f"ℹ️ Compra #{compra_id} já aprovada anteriormente.")
            return {'mensagem': 'Já processado'}, 200
            
        # APROVAR E GERAR TÍTULOS
        try:
            _aprovar_e_gerar_titulos(compra)
            
            # Log de arrecadação
            print(f"💸 ARRECADAÇÃO REGISTRADA: Campanha {compra.campanha_id} +R$ {compra.valor_total}")
            
            return {'mensagem': 'Pagamento aprovado com sucesso'}, 200
            
        except Exception as e:
            print(f"❌ Erro ao aprovar compra #{compra_id}: {e}")
            return {'erro': f"Erro interno: {str(e)}"}, 500
            
    # Ignorar outros eventos por enquanto
    return {'mensagem': 'Evento ignorado'}, 200

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
    
    # VALIDAÇÃO: Prevenir aprovação de compra expirada
    if _verificar_e_marcar_expiracao(compra):
        return {
            'erro': 'Compra expirada - prazo de pagamento excedido',
            'compra_id': compra.id,
            'expira_em': compra.expira_em.isoformat() if compra.expira_em else None
        }, 400
    
    # Se já aprovado, retornar
    if compra.status_pagamento == 'aprovado':
        return {
            'mensagem': 'Pagamento já estava aprovado',
            'compra_id': compra.id
        }, 200
    
    # Aprovar e gerar títulos
    status_anterior = compra.status_pagamento
    
    try:
        # Esta função já faz TUDO:
        # - Gera títulos
        # - Incrementa contador da campanha
        # - Atualiza status para 'aprovado'
        # - Define data_pagamento
        _aprovar_e_gerar_titulos(compra)
        
        return {
            'mensagem': 'Pagamento aprovado manualmente',
            'compra_id': compra.id,
            'status_anterior': status_anterior,
            'status_atual': 'aprovado',
            'aprovado_por': admin.nome
        }, 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro na aprovação manual: {str(e)}")
        return {'erro': f'Erro ao gerar títulos: {str(e)}'}, 500
